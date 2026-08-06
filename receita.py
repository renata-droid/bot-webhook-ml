#!/usr/bin/env python3
"""
Base de CNPJ da Receita (Dados Abertos) -> SQLite enxuto para casar com sellers.

Por que local: a BrasilAPI só vai de CNPJ -> dados, e tem rate limit. Aqui
carregamos a base pública da Receita UMA vez e consultamos à vontade, offline.

O que enxuga: NÃO carregamos o Brasil inteiro. Só os estabelecimentos ATIVOS
que estão nas MESMAS cidades (município+UF) dos seus sellers — que é tudo que
o casamento precisa. De ~60 milhões de linhas sobram uns poucos milhões.

Fonte oficial (grátis, sem login):
    https://arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj/AAAA-MM/
    Estabelecimentos0..9.zip  Empresas0..9.zip  Simples.zip  Municipios.zip

Uso:
    python receita.py baixar                 # descobre o mês mais novo e baixa
    python receita.py baixar --mes 2026-07   # força um mês
    python receita.py carregar               # carrega TODAS as UFs dos seus sellers
    python receita.py carregar --ufs SP,RJ,MG,ES,PR,SC,RS   # só Sudeste + Sul
    python receita.py status                 # o que já foi baixado/carregado
"""

# atalhos de região, pra não digitar UF por UF
REGIOES = {
    "sudeste": {"SP", "RJ", "MG", "ES"},
    "sul": {"PR", "SC", "RS"},
    "centro-oeste": {"GO", "MT", "MS", "DF"},
    "nordeste": {"BA", "SE", "AL", "PE", "PB", "RN", "CE", "PI", "MA"},
    "norte": {"AM", "PA", "AC", "RO", "RR", "AP", "TO"},
}

import argparse
import csv
import io
import re
import sqlite3
import sys
import time
import unicodedata
import zipfile
from difflib import SequenceMatcher
from pathlib import Path

import requests

BASE = "https://dadosabertos.rfb.gov.br/CNPJ/dados_abertos_cnpj"
DIR = Path("receita_cnpj")          # onde os ZIPs ficam (você já tem essa pasta)
DB = "receita.db"
SELLERS_DB = "sellers.db"

ARQ_ESTAB = [f"Estabelecimentos{i}.zip" for i in range(10)]
ARQ_EMPRESA = [f"Empresas{i}.zip" for i in range(10)]
ARQ_OUTROS = ["Simples.zip", "Municipios.zip"]

PORTE = {"00": "NÃO INFORMADO", "01": "ME", "03": "EPP", "05": "DEMAIS"}

# csv da Receita: separador ';', sem cabeçalho, latin-1, campos entre aspas
csv.field_size_limit(10 * 1024 * 1024)


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    return " ".join(s.upper().split())


# --------------------------------------------------------------------------- #
# Descoberta do mês e download
# --------------------------------------------------------------------------- #
def mes_mais_novo() -> str | None:
    try:
        r = requests.get(BASE + "/", timeout=30)
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"! não consegui listar {BASE}: {e}", file=sys.stderr)
        return None
    import re
    meses = sorted(set(re.findall(r"(\d{4}-\d{2})/", r.text)))
    return meses[-1] if meses else None


def baixar_arquivo(url: str, destino: Path) -> bool:
    """Baixa com retomada simples: se o arquivo já existe com o mesmo tamanho, pula."""
    for tentativa in range(4):
        try:
            with requests.get(url, stream=True, timeout=120) as r:
                if r.status_code == 404:
                    print(f"  - {destino.name}: não existe nesse mês (404), pulando")
                    return False
                r.raise_for_status()
                tamanho = int(r.headers.get("content-length", 0))
                if destino.exists() and tamanho and destino.stat().st_size == tamanho:
                    print(f"  = {destino.name}: já baixado ({tamanho/1e6:.0f} MB)")
                    return True
                baixado = 0
                with open(destino, "wb") as f:
                    for chunk in r.iter_content(1024 * 1024):
                        f.write(chunk)
                        baixado += len(chunk)
                        if tamanho:
                            pct = 100 * baixado / tamanho
                            print(f"\r  ↓ {destino.name}: {pct:5.1f}%", end="", flush=True)
                print(f"\r  ↓ {destino.name}: OK ({baixado/1e6:.0f} MB)      ")
                return True
        except requests.RequestException as e:
            print(f"\n  ! {destino.name}: {e} (tentativa {tentativa+1})", file=sys.stderr)
            time.sleep(2 ** tentativa)
    return False


def baixar(mes: str | None, parcial: bool = False) -> None:
    DIR.mkdir(exist_ok=True)
    mes = mes or mes_mais_novo()
    if not mes:
        sys.exit("Não descobri o mês — passe --mes AAAA-MM")
    if parcial:
        # amostra pra validar: 1/10 das empresas + complementos pequenos
        arquivos = ["Estabelecimentos0.zip", "Empresas0.zip", "Simples.zip", "Municipios.zip"]
        print(f"Baixando AMOSTRA (parcial) da Receita de {mes} para {DIR}/\n")
    else:
        arquivos = ARQ_ESTAB + ARQ_EMPRESA + ARQ_OUTROS
        print(f"Baixando base COMPLETA da Receita de {mes} para {DIR}/\n")
    (DIR / "MES.txt").write_text(mes)
    ok = 0
    for nome in arquivos:
        if baixar_arquivo(f"{BASE}/{mes}/{nome}", DIR / nome):
            ok += 1
    print(f"\n{ok}/{len(arquivos)} arquivos prontos em {DIR}/")


# --------------------------------------------------------------------------- #
# Carga filtrada
# --------------------------------------------------------------------------- #
def linhas_do_zip(caminho: Path):
    """Itera as linhas do único CSV dentro do ZIP da Receita."""
    with zipfile.ZipFile(caminho) as z:
        nome = z.namelist()[0]
        with z.open(nome) as bruto:
            texto = io.TextIOWrapper(bruto, encoding="latin-1", newline="")
            yield from csv.reader(texto, delimiter=";", quotechar='"')


def ufs_e_cidades_dos_sellers() -> tuple[set, set]:
    """UFs (sem BR-) e nomes de cidade normalizados presentes na sua base."""
    con = sqlite3.connect(SELLERS_DB)
    ufs, cidades = set(), set()
    for estado, cidade in con.execute("SELECT estado, cidade FROM sellers"):
        if estado and estado.startswith("BR-"):
            ufs.add(estado[3:].upper())
        if cidade:
            cidades.add(norm(cidade))
    con.close()
    return ufs, cidades


def carregar(ufs_arg: str | None) -> None:
    if not (DIR / ARQ_ESTAB[0]).exists():
        sys.exit(f"Nada em {DIR}/ — rode 'python receita.py baixar' primeiro.")

    ufs, cidades = ufs_e_cidades_dos_sellers()

    if ufs_arg:
        # aceita "sudeste,sul" ou "SP,RJ,..." (ou os dois misturados)
        pedido = set()
        for parte in ufs_arg.lower().replace(" ", "").split(","):
            pedido |= REGIOES.get(parte, {parte.upper()})
        ufs &= pedido
        print(f"Filtro de UF: {', '.join(sorted(ufs))}")

    print(f"Carregando: {len(ufs)} UFs, {len(cidades)} cidades distintas")

    # 1) Municipios.zip -> código -> nome, e o conjunto de códigos das suas cidades
    cod_nome, cods_alvo = {}, set()
    usar_muni = (DIR / "Municipios.zip").exists()
    if usar_muni:
        for cod, desc in linhas_do_zip(DIR / "Municipios.zip"):
            cod_nome[cod] = desc
            if norm(desc) in cidades:
                cods_alvo.add(cod)
        print(f"{len(cods_alvo)} códigos de município batem com suas cidades")
    else:
        print("Sem Municipios.zip -> guardo todas as empresas ativas das UFs (casa por UF+nome)")

    con = sqlite3.connect(DB)
    con.executescript("""
        DROP TABLE IF EXISTS estab;
        CREATE TABLE estab (
            cnpj_basico TEXT, cnpj TEXT, matriz_filial TEXT, nome_fantasia TEXT,
            situacao TEXT, cnae TEXT, uf TEXT, municipio_cod TEXT, municipio TEXT,
            ddd1 TEXT, tel1 TEXT, ddd2 TEXT, tel2 TEXT, email TEXT,
            municipio_norm TEXT
        );
    """)

    # 2) Estabelecimentos: só ATIVO (situacao=02), na UF e no município dos sellers
    keep = set()
    total = inseridos = 0
    for arq in ARQ_ESTAB:
        p = DIR / arq
        if not p.exists():
            continue
        for r in linhas_do_zip(p):
            total += 1
            if total % 2_000_000 == 0:
                print(f"  ...{total/1e6:.0f}M linhas de estabelecimentos, {inseridos} guardadas")
            if len(r) < 28 or r[5] != "02":
                continue
            uf, cod = r[19], r[20]
            if uf not in ufs:
                continue
            if usar_muni and cod not in cods_alvo:
                continue
            basico = r[0]
            cnpj = basico + r[1] + r[2]
            keep.add(basico)
            con.execute(
                "INSERT INTO estab VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (basico, cnpj, r[3], r[4], r[5], r[11], uf, cod,
                 cod_nome.get(cod, ""), r[21], r[22], r[23], r[24], r[27],
                 norm(cod_nome.get(cod, ""))),
            )
            inseridos += 1
        con.commit()
        print(f"  {arq}: {inseridos} estabelecimentos guardados até aqui")

    # 3) Empresas: razão social + porte, só dos CNPJs que guardamos
    con.executescript("""
        DROP TABLE IF EXISTS empresa;
        CREATE TABLE empresa (cnpj_basico TEXT PRIMARY KEY, razao_social TEXT, porte TEXT);
    """)
    n = 0
    for arq in ARQ_EMPRESA:
        p = DIR / arq
        if not p.exists():
            continue
        for r in linhas_do_zip(p):
            if len(r) < 6 or r[0] not in keep:
                continue
            con.execute("INSERT OR IGNORE INTO empresa VALUES (?,?,?)",
                        (r[0], r[1], PORTE.get(r[5], r[5])))
            n += 1
        con.commit()
    print(f"  empresas: {n} razões sociais + porte")

    # 4) Simples: regime (Simples/MEI)
    con.executescript("""
        DROP TABLE IF EXISTS simples;
        CREATE TABLE simples (cnpj_basico TEXT PRIMARY KEY, opcao_simples TEXT, opcao_mei TEXT);
    """)
    n = 0
    if (DIR / "Simples.zip").exists():
        for r in linhas_do_zip(DIR / "Simples.zip"):
            if len(r) < 5 or r[0] not in keep:
                continue
            con.execute("INSERT OR IGNORE INTO simples VALUES (?,?,?)", (r[0], r[1], r[4]))
            n += 1
        con.commit()
    print(f"  simples: {n} registros de regime")

    con.executescript("""
        CREATE INDEX IF NOT EXISTS idx_estab_uf ON estab(uf);
        CREATE INDEX IF NOT EXISTS idx_estab_mun ON estab(uf, municipio_norm);
        CREATE INDEX IF NOT EXISTS idx_estab_basico ON estab(cnpj_basico);
    """)
    con.commit()
    con.close()
    print(f"\nOK — {inseridos} estabelecimentos ativos nas suas cidades em {DB}")


# --------------------------------------------------------------------------- #
# Casamento seller -> CNPJ + preenchimento
# --------------------------------------------------------------------------- #
_LIXO = {"LTDA", "ME", "EPP", "EIRELI", "MEI", "COMERCIO", "COMERCIAL", "LOJA",
         "LOJAS", "STORE", "SHOP", "BRASIL", "OFICIAL", "SA", "COM", "BR", "WWW",
         "IMPORTS", "IMPORTADOS", "DISTRIBUIDORA", "GRUPO", "EIRELLI",
         "DE", "DA", "DO", "DOS", "DAS", "E"}


def _partes(s: str) -> list:
    # separa por nao-alfanumerico E entre letras/digitos:
    # "PITSTOP2IRMAOS" -> [PITSTOP, 2, IRMAOS];  "CELLTEK_SOLUTIONS" -> [CELLTEK, SOLUTIONS]
    bruto = re.findall(r"[A-Z]+|[0-9]+", norm(s))
    return [p for p in bruto if p not in _LIXO and len(p) > 1]


def _tokens(s: str) -> set:
    return set(_partes(s))


def _compact(s: str) -> str:
    return "".join(_partes(s))


def _pontuar(nick: str, *nomes: str) -> float:
    """0..1 — quao bem o apelido do seller casa com nome fantasia / razao social."""
    nt, nc = _tokens(nick), _compact(nick)
    if not nt and not nc:
        return 0.0
    melhor = 0.0
    for nome in nomes:
        if not nome:
            continue
        ct, cc = _tokens(nome), _compact(nome)
        s = 0.0
        if nt and ct:
            inter = len(nt & ct)
            s = max(s, inter / len(nt), inter / len(nt | ct))   # cobertura + jaccard
        if len(nc) >= 4 and cc:
            if nc in cc or cc in nc:
                s = max(s, 0.95)                                # apelido colado dentro do nome
            else:
                s = max(s, SequenceMatcher(None, nc, cc).ratio())  # tolera erro de grafia
        melhor = max(melhor, s)
    return melhor


def _fmt_cnpj(c: str) -> str:
    return f"{c[:2]}.{c[2:5]}.{c[5:8]}/{c[8:12]}-{c[12:]}" if len(c) == 14 else c


def _regime(sim) -> str:
    if not sim:
        return ""
    op_s, op_mei = sim
    if op_mei == "S":
        return "MEI"
    if op_s == "S":
        return "Simples Nacional"
    return "Outros (Presumido/Real)"


def casar(entrada: str, top: int, saida: str) -> None:
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row

    with open(entrada, encoding="utf-8") as f:
        leads = list(csv.DictReader(f))
    leads.sort(key=lambda r: float(r.get("score") or 0), reverse=True)
    leads = leads[:top]

    resultado = []
    for L in leads:
        uf = (L.get("estado") or "")[3:]
        cidade = norm(L.get("cidade"))
        nick = L.get("nickname") or ""

        # pre-filtra no banco pelos tokens distintivos do apelido -> poucos candidatos
        # (com Municipios: cidade exata; sem ele: municipio_norm vazio cai pra UF)
        chaves = sorted(_tokens(nick), key=len, reverse=True)[:2]
        cand = []
        if chaves:
            like = " OR ".join(["e.nome_fantasia LIKE ? OR em.razao_social LIKE ?"
                                for _ in chaves])
            params = [uf, cidade]
            for k in chaves:
                params += [f"%{k}%", f"%{k}%"]
            cand = con.execute(
                "SELECT e.*, em.razao_social AS razao, em.porte AS porte "
                "FROM estab e LEFT JOIN empresa em ON em.cnpj_basico = e.cnpj_basico "
                "WHERE e.uf=? AND (e.municipio_norm=? OR e.municipio_norm='') "
                f"AND ({like})", params).fetchall()

        melhor, melhor_s, segundo_s = None, 0.0, 0.0
        for e in cand:
            s = _pontuar(nick, e["nome_fantasia"], e["razao"])
            if s > melhor_s:
                melhor_s, segundo_s, melhor = s, melhor_s, e
            elif s > segundo_s:
                segundo_s = s

        # dois candidatos quase empatados = arriscado -> nao preenche, marca p/ revisar
        ambiguo = melhor_s >= 0.5 and segundo_s >= 0.5 and (melhor_s - segundo_s) < 0.15

        row = {
            "nickname": nick, "uf": uf, "cidade": L.get("cidade"),
            "transacoes": L.get("transacoes"), "score": L.get("score"),
            "cnpj": "", "razao_social": "", "nome_fantasia": "", "porte": "",
            "regime": "", "telefone": "", "email": "", "municipio_receita": "",
            "confianca": "", "candidatos": len(cand), "permalink": L.get("permalink"),
        }

        if melhor and melhor_s >= 0.5 and not ambiguo:
            e = melhor
            sim = con.execute(
                "SELECT opcao_simples, opcao_mei FROM simples WHERE cnpj_basico=?",
                (e["cnpj_basico"],)).fetchone()
            tel = f"({e['ddd1']}) {e['tel1']}" if e["ddd1"] and e["tel1"] else ""
            row.update({
                "cnpj": _fmt_cnpj(e["cnpj"]),
                "razao_social": e["razao"] or "",
                "nome_fantasia": e["nome_fantasia"],
                "porte": e["porte"] or "",
                "regime": _regime(sim),
                "telefone": tel,
                "email": e["email"],
                "municipio_receita": e["municipio"],
                "confianca": "ALTA" if melhor_s >= 0.85 else "MEDIA",
            })
        else:
            row["confianca"] = "SEM MATCH" if not cand else ("AMBIGUO" if ambiguo else "REVISAR")
        resultado.append(row)

    campos = ["nickname", "uf", "cidade", "transacoes", "score", "cnpj",
              "razao_social", "nome_fantasia", "porte", "regime", "telefone",
              "email", "municipio_receita", "confianca", "candidatos", "permalink"]
    with open(saida, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        w.writerows(resultado)

    cheios = sum(1 for r in resultado if r["cnpj"])
    print(f"\n{len(resultado)} leads -> {cheios} com CNPJ preenchido em {saida}\n")
    print(f"{'confianca':<9} {'nickname':<22} {'cnpj':<20} telefone")
    for r in resultado:
        print(f"{r['confianca']:<9} {(r['nickname'] or '')[:22]:<22} "
              f"{r['cnpj'] or '—':<20} {r['telefone']}")
    con.close()


def status() -> None:
    mes = (DIR / "MES.txt").read_text().strip() if (DIR / "MES.txt").exists() else "?"
    print(f"Mês baixado: {mes}")
    baixados = sorted(p.name for p in DIR.glob("*.zip")) if DIR.exists() else []
    print(f"ZIPs em {DIR}/: {len(baixados)}")
    for n in baixados:
        print(f"  {n}  ({(DIR/n).stat().st_size/1e6:.0f} MB)")
    if Path(DB).exists():
        con = sqlite3.connect(DB)
        for t in ("estab", "empresa", "simples"):
            try:
                c = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                print(f"  {DB}:{t} = {c}")
            except sqlite3.OperationalError:
                pass
        con.close()


def main() -> None:
    p = argparse.ArgumentParser(description="Base CNPJ da Receita -> SQLite enxuto")
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("baixar")
    b.add_argument("--mes", help="AAAA-MM (padrão: mais novo)")
    b.add_argument("--parcial", action="store_true",
                   help="baixa só amostra (Estab0+Empresas0+Simples+Municipios) p/ validar")
    c = sub.add_parser("carregar")
    c.add_argument("--ufs", help="UFs ou regiões, ex: 'sudeste,sul' ou 'SP,RJ,MG'")
    k = sub.add_parser("casar")
    k.add_argument("--entrada", default="leads_casa.csv")
    k.add_argument("--top", type=int, default=50)
    k.add_argument("--saida", default="leads_preenchido.csv")
    sub.add_parser("status")
    a = p.parse_args()
    if a.cmd == "baixar":
        baixar(a.mes, a.parcial)
    elif a.cmd == "carregar":
        carregar(a.ufs)
    elif a.cmd == "casar":
        casar(a.entrada, a.top, a.saida)
    elif a.cmd == "status":
        status()


if __name__ == "__main__":
    main()
