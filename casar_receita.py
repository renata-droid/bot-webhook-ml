#!/usr/bin/env python3
"""
Casa os leads do ML (leads_casa.csv) com a base da Receita (receita.db) e
PREENCHE cnpj, razao social, porte, regime, telefone e email — casando por
municipio + UF + nome. Nao inventa: marca a confianca de cada casamento.

Precisa antes:
    python receita.py carregar --ufs sudeste,sul   # cria receita.db

Uso:
    python casar_receita.py                          # top 50 do leads_casa.csv
    python casar_receita.py --entrada leads_casa.csv --top 50 --saida leads_preenchido.csv
"""
import argparse
import csv
import sqlite3
import unicodedata


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    return " ".join(s.upper().split())


def tokens(s: str) -> set:
    # ignora palavras genericas que nao ajudam a distinguir
    lixo = {"LTDA", "ME", "EPP", "EIRELI", "COMERCIO", "COMERCIAL", "LOJA",
            "STORE", "SHOP", "BRASIL", "OFICIAL", "SA", "DE", "DA", "DO", "E"}
    return {t for t in norm(s).split() if t not in lixo and len(t) > 1}


def similaridade(nick: str, *nomes: str) -> float:
    """Fracao dos tokens do nickname que aparecem no nome da empresa (0..1)."""
    a = tokens(nick)
    if not a:
        return 0.0
    melhor = 0.0
    for nome in nomes:
        b = tokens(nome)
        if b:
            melhor = max(melhor, len(a & b) / len(a))
    return melhor


def fmt_cnpj(c: str) -> str:
    return f"{c[:2]}.{c[2:5]}.{c[5:8]}/{c[8:12]}-{c[12:]}" if len(c) == 14 else c


def regime(sim) -> str:
    if not sim:
        return ""
    op_s, op_mei = sim
    if op_mei == "S":
        return "MEI"
    if op_s == "S":
        return "Simples Nacional"
    return "Outros (Presumido/Real)"


def casar(entrada: str, top: int, saida: str) -> None:
    con = sqlite3.connect("receita.db")
    con.row_factory = sqlite3.Row

    with open(entrada, encoding="utf-8") as f:
        leads = list(csv.DictReader(f))
    leads.sort(key=lambda r: float(r.get("score") or 0), reverse=True)
    leads = leads[:top]

    resultado = []
    for L in leads:
        uf = (L.get("estado") or "")[3:]           # BR-SP -> SP
        cidade = norm(L.get("cidade"))
        nick = L.get("nickname") or ""

        cand = con.execute(
            "SELECT * FROM estab WHERE uf=? AND municipio_norm=?", (uf, cidade)
        ).fetchall()

        melhor, melhor_s = None, 0.0
        for e in cand:
            emp = con.execute(
                "SELECT razao_social, porte FROM empresa WHERE cnpj_basico=?",
                (e["cnpj_basico"],)).fetchone()
            razao = emp["razao_social"] if emp else ""
            s = similaridade(nick, e["nome_fantasia"], razao)
            if s > melhor_s:
                melhor_s, melhor = s, (e, emp)

        row = {
            "nickname": nick, "uf": uf, "cidade": L.get("cidade"),
            "transacoes": L.get("transacoes"), "score": L.get("score"),
            "cnpj": "", "razao_social": "", "nome_fantasia": "", "porte": "",
            "regime": "", "telefone": "", "email": "", "municipio_receita": "",
            "confianca": "SEM MATCH" if not cand else "AMBIGUO",
            "candidatos": len(cand), "permalink": L.get("permalink"),
        }

        if melhor and melhor_s >= 0.5:
            e, emp = melhor
            sim = con.execute(
                "SELECT opcao_simples, opcao_mei FROM simples WHERE cnpj_basico=?",
                (e["cnpj_basico"],)).fetchone()
            tel = f"({e['ddd1']}) {e['tel1']}" if e["ddd1"] and e["tel1"] else ""
            row.update({
                "cnpj": fmt_cnpj(e["cnpj"]),
                "razao_social": emp["razao_social"] if emp else "",
                "nome_fantasia": e["nome_fantasia"],
                "porte": emp["porte"] if emp else "",
                "regime": regime(sim),
                "telefone": tel,
                "email": e["email"],
                "municipio_receita": e["municipio"],
                "confianca": "ALTA" if melhor_s >= 0.8 else "MEDIA",
            })
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


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Casa leads do ML com a Receita e preenche")
    p.add_argument("--entrada", default="leads_casa.csv")
    p.add_argument("--top", type=int, default=50)
    p.add_argument("--saida", default="leads_preenchido.csv")
    a = p.parse_args()
    casar(a.entrada, a.top, a.saida)
