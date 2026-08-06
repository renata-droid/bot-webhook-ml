#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
comparar_semanas.py
===================

Compara a MESMA semana (01/08 a 06/08) de dois anos no Pipedrive e mostra
"o que fizemos de diferente": ganhos, por vendedor, por produto, funil/conversão
e atividades (esforço).

Roda na SUA máquina (onde a API do Pipedrive é acessível). Usa só a biblioteca
padrão do Python 3 — não precisa instalar nada.

Como usar
---------
1) Pegue um token de API novo no Pipedrive:
   Configurações pessoais -> API -> "Seu token de API".
   (Se você já expôs o token antigo em algum lugar, gere um novo e revogue o antigo.)

2) Rode passando o token por variável de ambiente (recomendado):

   Linux/Mac:
       export PD_TOKEN="seu_token_aqui"
       python3 comparar_semanas.py

   Windows (PowerShell):
       $env:PD_TOKEN="seu_token_aqui"
       python comparar_semanas.py

   Ou por argumento:
       python3 comparar_semanas.py --token seu_token_aqui

3) Saída:
       saida/relatorio.html   -> abra no navegador
       saida/*.csv            -> planilhas para conferência
       saida/deal_fields.json -> mapa dos campos (para auditoria)

Parâmetros opcionais
--------------------
   --dominio icommescola        (subdomínio da sua conta; padrão: icommescola)
   --ano-a 2025 --ano-b 2026    (anos a comparar)
   --inicio 08-01 --fim 08-06   (janela MM-DD, inclusive)
"""

import os
import sys
import json
import time
import argparse
import urllib.parse
import urllib.request
import urllib.error
from collections import defaultdict
from datetime import date

# ---------------------------------------------------------------------------
# Configuração / argumentos
# ---------------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(description="Compara a mesma semana de dois anos no Pipedrive.")
    p.add_argument("--token", default=os.environ.get("PD_TOKEN", ""),
                   help="Token de API do Pipedrive (ou use a variável de ambiente PD_TOKEN).")
    p.add_argument("--dominio", default=os.environ.get("PD_DOMINIO", "icommescola"),
                   help="Subdomínio da conta Pipedrive (padrão: icommescola).")
    p.add_argument("--ano-a", type=int, default=2025, help="Ano do período A (padrão: 2025).")
    p.add_argument("--ano-b", type=int, default=2026, help="Ano do período B (padrão: 2026).")
    p.add_argument("--inicio", default="08-01", help="Início da janela, formato MM-DD (padrão: 08-01).")
    p.add_argument("--fim", default="08-06", help="Fim da janela, inclusive, formato MM-DD (padrão: 08-06).")
    p.add_argument("--saida", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "saida"),
                   help="Pasta de saída.")
    return p.parse_args()


ARGS = parse_args()
TOKEN = ARGS.token.strip()
BASE = f"https://{ARGS.dominio}.pipedrive.com/api/v1"

if not TOKEN:
    print("ERRO: nenhum token informado.\n"
          "  Use:  export PD_TOKEN=seu_token   (ou --token seu_token)\n", file=sys.stderr)
    sys.exit(1)


def janela(ano):
    mi, di = map(int, ARGS.inicio.split("-"))
    mf, df = map(int, ARGS.fim.split("-"))
    return date(ano, mi, di), date(ano, mf, df)


INI_A, FIM_A = janela(ARGS.ano_a)
INI_B, FIM_B = janela(ARGS.ano_b)
DIAS = (FIM_A - INI_A).days + 1  # nº de dias (inclusive)

os.makedirs(ARGS.saida, exist_ok=True)


# ---------------------------------------------------------------------------
# Camada HTTP (só stdlib)
# ---------------------------------------------------------------------------

def _url(path, params):
    q = dict(params or {})
    q["api_token"] = TOKEN
    return f"{BASE}{path}?{urllib.parse.urlencode(q)}"


def http_get(path, params=None, tentativas=5):
    url = _url(path, params)
    for t in range(tentativas):
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429:  # rate limit -> espera e tenta de novo
                espera = 2 ** t
                print(f"  (rate limit 429, aguardando {espera}s...)", file=sys.stderr)
                time.sleep(espera)
                continue
            body = e.read().decode("utf-8", "ignore")[:300]
            raise SystemExit(f"ERRO HTTP {e.code} em {path}\n{body}")
        except urllib.error.URLError as e:
            espera = 2 ** t
            print(f"  (rede falhou: {e.reason}; retry em {espera}s)", file=sys.stderr)
            time.sleep(espera)
    raise SystemExit(f"ERRO: falha de rede persistente em {path}")


def http_get_all(path, params=None):
    """Pagina endpoints v1 (additional_data.pagination)."""
    itens, start = [], 0
    while True:
        p = dict(params or {}); p["start"] = start; p["limit"] = 500
        data = http_get(path, p)
        if not data.get("success", True):
            raise SystemExit(f"ERRO API em {path}: {json.dumps(data)[:300]}")
        itens.extend(data.get("data") or [])
        pg = ((data.get("additional_data") or {}).get("pagination") or {})
        if pg.get("more_items_in_collection"):
            start = pg.get("next_start")
        else:
            return itens


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def brl(v):
    try:
        v = float(v or 0)
    except (TypeError, ValueError):
        v = 0.0
    return "R$ " + f"{v:,.0f}".replace(",", ".")


usuarios = {}  # {id: nome} — preenchido depois de conectar (map ID -> nome)

# Campo customizado "Vendedor" (o CLOSER que fechou). NÃO confundir com "user_id"
# (que é o Proprietário/dono do card). Também existe "SDR".
VENDEDOR_KEY = "db2c9632937b836eae914bb3749d19f3b129b31d"
SDR_KEY = "966e0b1c6e28cbb30fb6d82394746d33da5c07ea"


def _nome_usuario(v):
    """Resolve um valor de campo do tipo usuário (id int, string ou dict) -> nome."""
    if v in (None, "", 0, "0"):
        return None
    if isinstance(v, dict):
        v = v.get("id")
    try:
        v = int(v)
    except (TypeError, ValueError):
        pass
    return usuarios.get(v)


def nome_dono(deal):
    u = deal.get("user_id")
    if isinstance(u, dict):
        return u.get("name") or usuarios.get(u.get("id")) or f"user {u.get('id')}"
    return usuarios.get(u) or f"user {u}"


def nome_vendedor(deal):
    """Vendedor (closer) do negócio: usa o campo 'Vendedor'; se vazio, cai no dono."""
    return _nome_usuario(deal.get(VENDEDOR_KEY)) or nome_dono(deal)


def nome_sdr(deal):
    """SDR (pré-vendas) do negócio; 'Sem SDR' quando não preenchido."""
    return _nome_usuario(deal.get(SDR_KEY)) or "Sem SDR"


def valor(deal):
    try:
        return float(deal.get("value") or 0)
    except (TypeError, ValueError):
        return 0.0


def deals_da_timeline(field_key, inicio):
    """Usa /deals/timeline para pegar os negócios cuja `field_key` (won_time,
    add_time, lost_time) cai na janela [inicio .. inicio+DIAS-1], por dia."""
    params = {
        "start_date": inicio.isoformat(),
        "interval": "day",
        "amount": DIAS,
        "field_key": field_key,
        "exclude_deleted": 1,
    }
    data = http_get("/deals/timeline", params)
    if not data.get("success", True):
        raise SystemExit(f"ERRO timeline ({field_key}): {json.dumps(data)[:300]}")
    deals = []
    for periodo in (data.get("data") or []):
        for d in (periodo.get("deals") or []):
            deals.append(d)
    # de-dup por id (um negócio aparece uma vez)
    vistos, unicos = set(), []
    for d in deals:
        if d.get("id") not in vistos:
            vistos.add(d.get("id")); unicos.append(d)
    return unicos


# ---------------------------------------------------------------------------
# 0) Metadados: conta, campos, estágios, pipelines
# ---------------------------------------------------------------------------

print("Conectando ao Pipedrive...", file=sys.stderr)
me = http_get("/users/me").get("data", {})
print(f"  Conta: {me.get('name')} | Empresa: {me.get('company_name')} | "
      f"Moeda: {me.get('default_currency')} | TZ: {me.get('timezone_name')}", file=sys.stderr)

deal_fields = http_get("/dealFields").get("data") or []
with open(os.path.join(ARGS.saida, "deal_fields.json"), "w", encoding="utf-8") as f:
    json.dump(deal_fields, f, ensure_ascii=False, indent=2)

# Campos categóricos customizados (enum/set) -> mapa opção_id -> rótulo
campos_cat = []  # [(key, nome, {id:rotulo})]
for fld in deal_fields:
    if fld.get("field_type") in ("enum", "set") and fld.get("edit_flag"):  # edit_flag=custom
        opts = {str(o["id"]): o["label"] for o in (fld.get("options") or [])}
        campos_cat.append((fld["key"], fld["name"], opts))

estagios = {s["id"]: s for s in (http_get_all("/stages") or [])}
pipelines = {p["id"]: p["name"] for p in (http_get_all("/pipelines") or [])}
usuarios.update({u["id"]: u.get("name") for u in (http_get_all("/users") or [])})

# Tipos de atividade -> nome legível (Ligação, E-mail, Reunião, Tarefa...)
tipos_ativ = {t.get("key_string"): t.get("name")
              for t in (http_get_all("/activityTypes") or [])}

# Campos que indicam ORIGEM / CANAL do lead ("de onde vem o lead")
PALAVRAS_CANAL = ("origem", "fonte", "canal", "source", "onde", "midia", "mídia",
                  "campanha", "utm", "aquisic", "aquisiç", "lead")
EXCLUIR_CANAL = ("origem contratual",)   # campos de canal a NÃO exibir
canais_cat = [(k, n, o) for (k, n, o) in campos_cat
              if any(w in n.lower() for w in PALAVRAS_CANAL)
              and n.lower().strip() not in EXCLUIR_CANAL]

# Campos que devem aparecer em "Ganhos por categoria" (o resto é descartado)
GANHOS_MANTER = {"produto", "lead", "bu", "utm_source v3", "utm_source_new", "utm_medium_new"}

# Pessoas que NÃO são vendedores (CS, suporte...) — saem das tabelas por vendedor.
# Adicione nomes aqui em minúsculo se precisar remover mais alguém.
EXCLUIR_PESSOAS = {"aline silva"}


def sem_cs(d):
    """Remove das agregações por pessoa quem está em EXCLUIR_PESSOAS (compara pelo
    nome antes de um eventual ' (#id')."""
    return {k: v for k, v in d.items()
            if str(k).split(" (#")[0].strip().lower() not in EXCLUIR_PESSOAS}


# Time de closers (vendas). Todos aparecem nas tabelas por vendedor, mesmo com 0.
# Casa por nome parcial (ex.: "Nickolas" casa com "Nickolas Ferreira") para não duplicar.
CLOSERS = ["Christopher", "Renato Benedetti", "Lucas Gallera", "Matheus Medeiros", "Nickolas"]


def com_closers(d):
    """Garante que todo closer apareça no dicionário (0 se não houver dado),
    sem duplicar quando o nome no CRM for mais completo."""
    out = dict(d)
    for c in CLOSERS:
        cl = c.lower()
        if not any(cl in str(k).lower() or str(k).lower() in cl for k in out):
            out[c] = 0
    return out
# Opções do campo nativo "channel" (canal de marketing configurado na conta)
canal_opts = {}
for fld in deal_fields:
    if fld.get("key") == "channel":
        canal_opts = {str(o["id"]): o["label"] for o in (fld.get("options") or [])}


# ---------------------------------------------------------------------------
# 1) Coleta por período
# ---------------------------------------------------------------------------

def coletar(inicio):
    ganhos = deals_da_timeline("won_time", inicio)
    perdidos = deals_da_timeline("lost_time", inicio)
    criados = deals_da_timeline("add_time", inicio)
    fim = date(inicio.year, int(ARGS.fim.split("-")[0]), int(ARGS.fim.split("-")[1]))
    atividades = http_get_all("/activities", {
        "user_id": 0,            # todos os usuários
        "start_date": inicio.isoformat(),
        "end_date": fim.isoformat(),
        "done": 1,
    })
    return {"ganhos": ganhos, "perdidos": perdidos, "criados": criados, "atividades": atividades}


print(f"Coletando período A ({INI_A} -> {FIM_A})...", file=sys.stderr)
A = coletar(INI_A)
print(f"Coletando período B ({INI_B} -> {FIM_B})...", file=sys.stderr)
B = coletar(INI_B)


# Produtos (line items) por negócio ganho — pode ser 0 se usarem campo custom
def produtos_por_deal(deals):
    total = defaultdict(lambda: {"valor": 0.0, "qtd": 0})
    for d in deals:
        did = d.get("id")
        try:
            itens = http_get(f"/deals/{did}/products").get("data") or []
        except SystemExit:
            itens = []
        for it in itens:
            nome = it.get("name") or f"produto {it.get('product_id')}"
            total[nome]["valor"] += float(it.get("sum") or 0)
            total[nome]["qtd"] += float(it.get("quantity") or 0)
    return total


print("Buscando produtos dos negócios ganhos...", file=sys.stderr)
A["produtos"] = produtos_por_deal(A["ganhos"])
B["produtos"] = produtos_por_deal(B["ganhos"])


# ---------------------------------------------------------------------------
# 2) Agregações
# ---------------------------------------------------------------------------

def resumo(P):
    g = P["ganhos"]
    total = sum(valor(d) for d in g)
    por_dono_val, por_dono_qtd = defaultdict(float), defaultdict(int)
    for d in g:
        por_dono_val[nome_vendedor(d)] += valor(d)
        por_dono_qtd[nome_vendedor(d)] += 1
    por_pipeline = defaultdict(float)
    for d in g:
        por_pipeline[pipelines.get(d.get("pipeline_id"), f"pipeline {d.get('pipeline_id')}")] += valor(d)
    # campos categóricos (ex.: lead A/B/C/D, produto à ofertar)
    por_campo = {}
    for key, nome, opts in campos_cat:
        acc_v, acc_q = defaultdict(float), defaultdict(int)
        houve = False
        for d in g:
            raw = d.get(key)
            if raw in (None, "", "0"):
                continue
            for oid in str(raw).split(","):
                rot = opts.get(oid.strip(), oid.strip())
                acc_v[rot] += valor(d); acc_q[rot] += 1; houve = True
        if houve:
            por_campo[nome] = {"valor": dict(acc_v), "qtd": dict(acc_q)}
    # atividades (toques) por tipo (nome legível) e por pessoa
    ativ_tipo, ativ_user = defaultdict(int), defaultdict(int)
    for a in P["atividades"]:
        tp = a.get("type") or "?"
        ativ_tipo[tipos_ativ.get(tp, tp)] += 1
        pessoa = (a.get("owner_name") or usuarios.get(a.get("owner_id"))
                  or usuarios.get(a.get("user_id"))
                  or usuarios.get(a.get("assigned_to_user_id")) or "?")
        ativ_user[pessoa] += 1

    # LEADS (negócios criados) por canal/origem e por dono
    criados = P["criados"]
    por_dono_criados = defaultdict(int)
    for d in criados:
        por_dono_criados[nome_vendedor(d)] += 1

    # SDR (pré-vendas): leads gerados e vendas que vieram desses leads
    por_sdr_criados = defaultdict(int)
    for d in criados:
        por_sdr_criados[nome_sdr(d)] += 1
    por_sdr_ganho_val, por_sdr_ganho_qtd = defaultdict(float), defaultdict(int)
    for d in g:
        por_sdr_ganho_val[nome_sdr(d)] += valor(d)
        por_sdr_ganho_qtd[nome_sdr(d)] += 1

    por_canal = {}  # {nome_do_campo: {rotulo: contagem_de_leads}}

    def _acc_canal(nome, getter):
        acc, houve = defaultdict(int), False
        for d in criados:
            rot = getter(d)
            if rot:
                acc[rot] += 1; houve = True
        if houve:
            por_canal[nome] = dict(acc)

    _acc_canal("Origem (sistema)", lambda d: d.get("origin"))
    if canal_opts:
        _acc_canal("Canal de marketing",
                   lambda d: canal_opts.get(str(d.get("channel")))
                   if d.get("channel") not in (None, "", 0, "0") else None)
    for key, nome, opts in canais_cat:
        def _get(d, key=key, opts=opts):
            raw = d.get(key)
            if raw in (None, "", "0"):
                return None
            return ", ".join(opts.get(o.strip(), o.strip()) for o in str(raw).split(","))
        _acc_canal(nome, _get)

    return {
        "ganho_total": total,
        "ganho_qtd": len(g),
        "criados_qtd": len(criados),
        "perdidos_qtd": len(P["perdidos"]),
        "ticket_medio": (total / len(g)) if g else 0.0,
        "por_dono_val": dict(por_dono_val),
        "por_dono_qtd": dict(por_dono_qtd),
        "por_dono_criados": dict(por_dono_criados),
        "por_sdr_criados": dict(por_sdr_criados),
        "por_sdr_ganho_val": dict(por_sdr_ganho_val),
        "por_sdr_ganho_qtd": dict(por_sdr_ganho_qtd),
        "por_pipeline": dict(por_pipeline),
        "por_campo": por_campo,
        "por_canal": por_canal,
        "produtos": {k: v for k, v in P["produtos"].items()},
        "ativ_tipo": dict(ativ_tipo),
        "ativ_user": dict(ativ_user),
        "ativ_total": len(P["atividades"]),
    }


RA = resumo(A)
RB = resumo(B)


def pct(novo, velho):
    if not velho:
        return None
    return (novo - velho) / velho * 100.0


# ---------------------------------------------------------------------------
# 3) Console (resumo rápido)
# ---------------------------------------------------------------------------

L = f"{ARGS.ano_a}"; R = f"{ARGS.ano_b}"
print("\n" + "=" * 64)
print(f"  COMPARATIVO {ARGS.inicio.replace('-', '/')} a {ARGS.fim.replace('-', '/')}  |  {L}  x  {R}")
print("=" * 64)


def linha(rotulo, va, vb, fmt=brl):
    p = pct(vb, va)
    ps = "" if p is None else f"  ({p:+.1f}%)"
    print(f"  {rotulo:<22} {fmt(va):>14} {L}   {fmt(vb):>14} {R}{ps}")


linha("Ganhos (R$)", RA["ganho_total"], RB["ganho_total"])
linha("Nº negócios ganhos", RA["ganho_qtd"], RB["ganho_qtd"], fmt=lambda x: str(int(x)))
linha("Ticket médio", RA["ticket_medio"], RB["ticket_medio"])
linha("Negócios criados", RA["criados_qtd"], RB["criados_qtd"], fmt=lambda x: str(int(x)))
linha("Negócios perdidos", RA["perdidos_qtd"], RB["perdidos_qtd"], fmt=lambda x: str(int(x)))
linha("Atividades feitas", RA["ativ_total"], RB["ativ_total"], fmt=lambda x: str(int(x)))
print("=" * 64)


# ---------------------------------------------------------------------------
# 3b) DIAGNÓSTICO: por que caiu? (tabelas no terminal)
# ---------------------------------------------------------------------------

def fmt_delta(a, b):
    p = pct(b, a)
    return "(novo)" if p is None else f"({p:+.0f}%)"


def tab_terminal(titulo, da, db, moeda=True, largura=24):
    chaves = sorted(set(da) | set(db), key=lambda k: -(da.get(k, 0) + db.get(k, 0)))
    print(f"\n  {titulo}")
    print(f"      {'':<{largura}}{L:>12}{R:>12}{'Δ':>10}")
    for k in chaves:
        a, b = da.get(k, 0), db.get(k, 0)
        fa = brl(a) if moeda else str(int(a))
        fb = brl(b) if moeda else str(int(b))
        print(f"      {str(k)[:largura - 1]:<{largura}}{fa:>12}{fb:>12}{fmt_delta(a, b):>10}")


print("\n" + "=" * 64)
print("  POR QUE CAIU?  (diagnóstico automático)")
print("=" * 64)

# 1) Vendedores: ganho, nº de vendas e toques
tab_terminal("[1] Ganho por vendedor", RA["por_dono_val"], RB["por_dono_val"])
tab_terminal("[2] Toques (atividades) por vendedor", RA["ativ_user"], RB["ativ_user"], moeda=False)

# 2) Toques por tipo (ligação, e-mail, reunião...)
tab_terminal("[3] Toques por tipo", RA["ativ_tipo"], RB["ativ_tipo"], moeda=False)

# 3) Produtos vendidos
prod_val_a = {k: v["valor"] for k, v in RA["produtos"].items()}
prod_val_b = {k: v["valor"] for k, v in RB["produtos"].items()}
if prod_val_a or prod_val_b:
    tab_terminal("[4] Ganho por produto", prod_val_a, prod_val_b, largura=30)
else:
    print("\n  [4] Ganho por produto: (sem line items — produto pode estar em campo custom)")

# 4) LEADS por canal / origem
if RA["por_canal"] or RB["por_canal"]:
    campos = sorted(set(RA["por_canal"]) | set(RB["por_canal"]))
    for nome in campos:
        tab_terminal(f"[5] Leads criados por “{nome}”",
                     RA["por_canal"].get(nome, {}), RB["por_canal"].get(nome, {}),
                     moeda=False, largura=30)
else:
    print("\n  [5] Canal/origem do lead: nenhum campo de origem encontrado.")
    print("      (crie um campo 'Origem/Fonte' no Pipedrive p/ rastrear canal)")

# 5) Leitura automática
print("\n  [6] LEITURA AUTOMÁTICA")
ta = RA["ativ_total"] / RA["criados_qtd"] if RA["criados_qtd"] else 0
tb = RB["ativ_total"] / RB["criados_qtd"] if RB["criados_qtd"] else 0
print(f"      - Toques por lead: {ta:.1f} ({L}) -> {tb:.1f} ({R})  {fmt_delta(ta, tb)}")
# quem trabalhava e praticamente parou
sumiram = []
for v in set(RA["ativ_user"]) | set(RB["ativ_user"]):
    aa, ab = RA["ativ_user"].get(v, 0), RB["ativ_user"].get(v, 0)
    if aa >= 20 and ab <= aa * 0.25:
        sumiram.append((v, aa, ab))
if sumiram:
    print("      - Vendedor(es) que quase PARARAM (saída/férias?):")
    for v, aa, ab in sorted(sumiram, key=lambda x: -x[1]):
        print(f"          * {v}: {aa} -> {ab} toques")
else:
    print("      - Queda de toques parece GERAL (não concentrada em 1 pessoa).")
# produto que encalhou
for p in prod_val_a:
    if prod_val_a.get(p, 0) >= 10000 and prod_val_b.get(p, 0) == 0:
        print(f"      - Produto que ENCALHOU: {p} ({brl(prod_val_a[p])} -> R$ 0)")
if RB["criados_qtd"] > RA["criados_qtd"] * 1.3 and RB["ativ_total"] < RA["ativ_total"]:
    print(f"      - MUDANÇA DE FOCO: leads {int(RA['criados_qtd'])} -> {int(RB['criados_qtd'])}, "
          f"mas toques {int(RA['ativ_total'])} -> {int(RB['ativ_total'])}.")
    print("        => a operação passou a GERAR lead em vez de TRABALHAR/FECHAR lead.")
print("=" * 64)
print(f"\n  Relatório completo -> {os.path.join(ARGS.saida, 'relatorio.html')}\n")


# ---------------------------------------------------------------------------
# 4) CSVs
# ---------------------------------------------------------------------------
import csv


def dump_deals_csv(deals, caminho):
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "titulo", "valor", "moeda", "dono", "pipeline", "estagio",
                    "won_time", "add_time", "status"])
        for d in deals:
            w.writerow([
                d.get("id"), d.get("title"), valor(d), d.get("currency"),
                nome_dono(d), pipelines.get(d.get("pipeline_id"), d.get("pipeline_id")),
                (estagios.get(d.get("stage_id"), {}) or {}).get("name", d.get("stage_id")),
                d.get("won_time"), d.get("add_time"), d.get("status"),
            ])


dump_deals_csv(A["ganhos"], os.path.join(ARGS.saida, f"ganhos_{ARGS.ano_a}.csv"))
dump_deals_csv(B["ganhos"], os.path.join(ARGS.saida, f"ganhos_{ARGS.ano_b}.csv"))


def dump_comparativo_csv(caminho):
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["metrica", str(ARGS.ano_a), str(ARGS.ano_b), "variacao_%"])
        def row(m, a, b):
            p = pct(b, a)
            w.writerow([m, round(a, 2), round(b, 2), "" if p is None else round(p, 1)])
        row("ganhos_brl", RA["ganho_total"], RB["ganho_total"])
        row("negocios_ganhos", RA["ganho_qtd"], RB["ganho_qtd"])
        row("ticket_medio", RA["ticket_medio"], RB["ticket_medio"])
        row("negocios_criados", RA["criados_qtd"], RB["criados_qtd"])
        row("negocios_perdidos", RA["perdidos_qtd"], RB["perdidos_qtd"])
        row("atividades", RA["ativ_total"], RB["ativ_total"])


dump_comparativo_csv(os.path.join(ARGS.saida, "comparativo.csv"))


# ---------------------------------------------------------------------------
# 5) Relatório HTML
# ---------------------------------------------------------------------------

def tabela_comparada(titulo, dados_a, dados_b, is_moeda=True):
    chaves = sorted(set(dados_a) | set(dados_b),
                    key=lambda k: -(dados_b.get(k, 0) + dados_a.get(k, 0)))
    linhas = []
    for k in chaves:
        a = dados_a.get(k, 0); b = dados_b.get(k, 0)
        p = pct(b, a)
        cor = "" if p is None else ("pos" if p >= 0 else "neg")
        ps = "—" if p is None else f"{p:+.0f}%"
        fa = brl(a) if is_moeda else (f"{a:g}")
        fb = brl(b) if is_moeda else (f"{b:g}")
        linhas.append(f"<tr><td>{k}</td><td class='num'>{fa}</td>"
                      f"<td class='num'>{fb}</td><td class='num {cor}'>{ps}</td></tr>")
    if not linhas:
        return ""
    return f"""<h3>{titulo}</h3>
    <table><thead><tr><th>Item</th><th>{ARGS.ano_a}</th><th>{ARGS.ano_b}</th><th>Δ</th></tr></thead>
    <tbody>{''.join(linhas)}</tbody></table>"""


def card(rotulo, va, vb, moeda=True):
    p = pct(vb, va)
    cor = "" if p is None else ("pos" if p >= 0 else "neg")
    ps = "—" if p is None else f"{p:+.1f}%"
    fa = brl(va) if moeda else str(int(va))
    fb = brl(vb) if moeda else str(int(vb))
    return f"""<div class="card">
      <div class="rot">{rotulo}</div>
      <div class="big {cor}">{fb}</div>
      <div class="sub">{ARGS.ano_b} &nbsp;·&nbsp; {ARGS.ano_a}: {fa} <span class="{cor}">({ps})</span></div>
    </div>"""


campos_html = ""
for key, nome, _opts in campos_cat:
    if nome.lower().strip() not in GANHOS_MANTER:
        continue
    da = RA["por_campo"].get(nome); db_ = RB["por_campo"].get(nome)
    if not da and not db_:
        continue
    campos_html += tabela_comparada(f"Ganhos por “{nome}” (valor)",
                                    (da or {}).get("valor", {}), (db_ or {}).get("valor", {}))

prod_a = {k: v["valor"] for k, v in RA["produtos"].items()}
prod_b = {k: v["valor"] for k, v in RB["produtos"].items()}

# Tabelas de canal/origem dos leads criados
canal_html = ""
for nome in sorted(set(RA["por_canal"]) | set(RB["por_canal"])):
    canal_html += tabela_comparada(f"Leads criados por “{nome}”",
                                   RA["por_canal"].get(nome, {}),
                                   RB["por_canal"].get(nome, {}), is_moeda=False)
if not canal_html:
    canal_html = ("<h3>Canal / origem do lead</h3><p style='color:#888'>Nenhum campo de "
                  "origem encontrado. Crie um campo <b>Origem/Fonte</b> no Pipedrive para "
                  "rastrear de onde vêm os leads.</p>")

html = f"""<!doctype html><html lang="pt-br"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Comparativo {ARGS.ano_a} x {ARGS.ano_b}</title>
<style>
  :root {{ color-scheme: light dark; }}
  body {{ font-family: -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 0; padding: 24px;
         background:#f6f7f9; color:#1a1a1a; }}
  @media (prefers-color-scheme: dark) {{ body {{ background:#14161a; color:#e8e8e8; }}
    .card,table {{ background:#1e2127 !important; }} th {{ background:#262a31 !important; }} }}
  h1 {{ font-size: 22px; margin: 0 0 4px; }}
  .meta {{ color:#888; font-size: 13px; margin-bottom: 20px; }}
  .cards {{ display:flex; flex-wrap:wrap; gap:14px; margin-bottom:8px; }}
  .card {{ background:#fff; border-radius:12px; padding:16px 18px; min-width:180px; flex:1;
          box-shadow:0 1px 3px rgba(0,0,0,.08); }}
  .rot {{ font-size:12px; text-transform:uppercase; letter-spacing:.04em; color:#888; }}
  .big {{ font-size:26px; font-weight:700; margin:4px 0; }}
  .sub {{ font-size:12px; color:#999; }}
  .pos {{ color:#16a34a; }} .neg {{ color:#dc2626; }}
  table {{ width:100%; border-collapse:collapse; background:#fff; border-radius:10px; overflow:hidden;
          margin:8px 0 22px; box-shadow:0 1px 3px rgba(0,0,0,.06); }}
  th,td {{ padding:9px 12px; text-align:left; font-size:14px; border-bottom:1px solid rgba(128,128,128,.15); }}
  th {{ background:#f0f1f3; font-size:12px; text-transform:uppercase; letter-spacing:.03em; color:#666; }}
  td.num {{ text-align:right; font-variant-numeric:tabular-nums; }}
  h3 {{ margin:22px 0 6px; font-size:16px; }}
  .grid {{ display:grid; grid-template-columns:1fr 1fr; gap:0 28px; }}
  @media (max-width:800px) {{ .grid {{ grid-template-columns:1fr; }} }}
</style></head><body>
<h1>Comparativo — mesma semana {ARGS.inicio.replace('-', '/')} a {ARGS.fim.replace('-', '/')}</h1>
<div class="meta">{me.get('company_name','')} · {ARGS.ano_a} vs {ARGS.ano_b} · gerado por comparar_semanas.py</div>

<div class="cards">
  {card("Ganhos (R$)", RA['ganho_total'], RB['ganho_total'])}
  {card("Negócios ganhos", RA['ganho_qtd'], RB['ganho_qtd'], moeda=False)}
  {card("Ticket médio", RA['ticket_medio'], RB['ticket_medio'])}
</div>
<div class="cards">
  {card("Negócios criados", RA['criados_qtd'], RB['criados_qtd'], moeda=False)}
  {card("Negócios perdidos", RA['perdidos_qtd'], RB['perdidos_qtd'], moeda=False)}
  {card("Atividades feitas", RA['ativ_total'], RB['ativ_total'], moeda=False)}
</div>

<h2 style="margin:26px 0 2px;font-size:18px">👥 Vendedores</h2>
<div class="grid">
  <div>{tabela_comparada("Ganhos por vendedor (valor)", RA['por_dono_val'], RB['por_dono_val'])}</div>
  <div>{tabela_comparada("Nº de ganhos por vendedor", RA['por_dono_qtd'], RB['por_dono_qtd'], is_moeda=False)}</div>
</div>

<h2 style="margin:26px 0 2px;font-size:18px">📞 Toques (atividades)</h2>
<div class="grid">
  <div>{tabela_comparada("Toques por tipo", RA['ativ_tipo'], RB['ativ_tipo'], is_moeda=False)}</div>
  <div>{tabela_comparada("Toques por pessoa", RA['ativ_user'], RB['ativ_user'], is_moeda=False)}</div>
</div>

<h2 style="margin:26px 0 2px;font-size:18px">📥 Leads: volume e canal</h2>
<div class="grid">
  <div>{tabela_comparada("Leads criados por vendedor", RA['por_dono_criados'], RB['por_dono_criados'], is_moeda=False)}</div>
  <div></div>
</div>
{canal_html}

<h2 style="margin:26px 0 2px;font-size:18px">💼 Produtos e funil</h2>
{tabela_comparada("Ganhos por produto (line items)", prod_a, prod_b)}
{tabela_comparada("Ganhos por pipeline", RA['por_pipeline'], RB['por_pipeline'])}
{campos_html}

</body></html>"""

with open(os.path.join(ARGS.saida, "relatorio.html"), "w", encoding="utf-8") as f:
    f.write(html)

# JSON bruto agregado (útil se você quiser me mandar de volta para eu analisar)
with open(os.path.join(ARGS.saida, "resumo.json"), "w", encoding="utf-8") as f:
    json.dump({"ano_a": ARGS.ano_a, "ano_b": ARGS.ano_b,
               "resumo_a": RA, "resumo_b": RB}, f, ensure_ascii=False, indent=2, default=str)

# ---------------------------------------------------------------------------
# 6) Relatório WORD (.docx) — sem dependências (só zipfile + stdlib)
# ---------------------------------------------------------------------------
import zipfile
from xml.sax.saxutils import escape as _esc

VERDE, VERMELHO = "16A34A", "DC2626"


def _run(text, bold=False, color=None, size=None):
    props = ""
    if bold:
        props += "<w:b/>"
    if color:
        props += f'<w:color w:val="{color}"/>'
    if size:
        props += f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>'
    rpr = f"<w:rPr>{props}</w:rPr>" if props else ""
    return f'<w:r>{rpr}<w:t xml:space="preserve">{_esc(str(text))}</w:t></w:r>'


def _p(runs="", before=None):
    if isinstance(runs, str) and not runs.startswith("<w:r"):
        runs = _run(runs)
    ppr = f'<w:pPr><w:spacing w:before="{before}"/></w:pPr>' if before else ""
    return f"<w:p>{ppr}{runs}</w:p>"


def _h(text, level=1):
    return _p(_run(text, bold=True, size=(32 if level == 1 else 26)), before="240")


_BORDERS = "<w:tblBorders>" + "".join(
    f'<w:{s} w:val="single" w:sz="4" w:space="0" w:color="D0D0D0"/>'
    for s in ("top", "left", "bottom", "right", "insideH", "insideV")) + "</w:tblBorders>"


def _tc(runs, fill=None):
    tcpr = "<w:tcPr>" + (f'<w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>' if fill else "") + "</w:tcPr>"
    return f"<w:tc>{tcpr}{_p(runs)}</w:tc>"


def _tabela(headers, rows):
    tbl = f'<w:tbl><w:tblPr><w:tblW w:w="0" w:type="auto"/>{_BORDERS}</w:tblPr>'
    tbl += "<w:tr>" + "".join(_tc(_run(h, bold=True), fill="EEF0F3") for h in headers) + "</w:tr>"
    for row in rows:
        cells = ""
        for c in row:
            cells += _tc(_run(c[0], color=c[1])) if isinstance(c, tuple) else _tc(_run(c))
        tbl += f"<w:tr>{cells}</w:tr>"
    return tbl + "</w:tbl>" + _p("")


def _linhas(da, db, moeda=True):
    chaves = sorted(set(da) | set(db), key=lambda k: -(da.get(k, 0) + db.get(k, 0)))
    out = []
    for k in chaves:
        a, b = da.get(k, 0), db.get(k, 0)
        p = pct(b, a)
        col = None if p is None else (VERDE if p >= 0 else VERMELHO)
        ps = "—" if p is None else f"{p:+.0f}%"
        fa = brl(a) if moeda else str(int(a))
        fb = brl(b) if moeda else str(int(b))
        out.append([str(k), fa, fb, (ps, col)])
    return out


def _row(nome, a, b, moeda=True):
    p = pct(b, a)
    col = None if p is None else (VERDE if p >= 0 else VERMELHO)
    ps = "—" if p is None else f"{p:+.0f}%"
    fa = brl(a) if moeda else str(int(a))
    fb = brl(b) if moeda else str(int(b))
    return [nome, fa, fb, (ps, col)]


HDR = ["Item", L, R, "Δ (2026/2025)"]


def _vendedores(R):
    nomes = set(R["por_dono_val"]) | set(R["ativ_user"]) | set(R["por_dono_criados"])
    return sorted(n for n in nomes if n and n != "?" and not str(n).startswith("user "))


def _leads_por_id(deals):
    acc = defaultdict(int)
    for d in deals:
        acc[nome_vendedor(d)] += 1
    return dict(acc)


va, vb = _vendedores(RA), _vendedores(RB)
corpo = []
corpo.append(_h(f"Comparativo — mesma semana {ARGS.inicio.replace('-', '/')} a {ARGS.fim.replace('-', '/')}", 1))
corpo.append(_p(_run(f"{me.get('company_name', '')}  ·  {L} vs {R}  ·  Δ = variação de {R} sobre {L}", color="777777")))

corpo.append(_h("Resumo", 2))
corpo.append(_tabela(HDR, [
    _row("Ganhos (R$)", RA["ganho_total"], RB["ganho_total"]),
    _row("Negócios ganhos", RA["ganho_qtd"], RB["ganho_qtd"], moeda=False),
    _row("Ticket médio", RA["ticket_medio"], RB["ticket_medio"]),
    _row("Negócios criados", RA["criados_qtd"], RB["criados_qtd"], moeda=False),
    _row("Negócios perdidos", RA["perdidos_qtd"], RB["perdidos_qtd"], moeda=False),
    _row("Atividades (toques)", RA["ativ_total"], RB["ativ_total"], moeda=False),
]))

corpo.append(_h("Vendedores", 2))
corpo.append(_tabela(["Ano", "Qtd vendedores", "Nomes"], [
    [L, str(len(va)), ", ".join(va) or "—"],
    [R, str(len(vb)), ", ".join(vb) or "—"],
]))
corpo.append(_p(_run("Ganho por vendedor", bold=True)))
corpo.append(_tabela(HDR, _linhas(RA["por_dono_val"], RB["por_dono_val"])))
corpo.append(_p(_run("Nº de ganhos por vendedor", bold=True)))
corpo.append(_tabela(HDR, _linhas(RA["por_dono_qtd"], RB["por_dono_qtd"], moeda=False)))

corpo.append(_h("Toques (atividades)", 2))
corpo.append(_p(_run("Por tipo", bold=True)))
corpo.append(_tabela(HDR, _linhas(RA["ativ_tipo"], RB["ativ_tipo"], moeda=False)))
corpo.append(_p(_run("Por pessoa", bold=True)))
corpo.append(_tabela(HDR, _linhas(RA["ativ_user"], RB["ativ_user"], moeda=False)))

corpo.append(_h("Leads: volume e canal", 2))
corpo.append(_p(_run("Leads criados por vendedor (com #ID do usuário)", bold=True)))
corpo.append(_tabela(HDR, _linhas(_leads_por_id(A["criados"]), _leads_por_id(B["criados"]), moeda=False)))
for nome in sorted(set(RA["por_canal"]) | set(RB["por_canal"])):
    corpo.append(_p(_run(f"Leads criados por “{nome}”", bold=True)))
    corpo.append(_tabela(HDR, _linhas(RA["por_canal"].get(nome, {}), RB["por_canal"].get(nome, {}), moeda=False)))

corpo.append(_h("Ganhos por pipeline", 2))
corpo.append(_tabela(HDR, _linhas(RA["por_pipeline"], RB["por_pipeline"])))

corpo.append(_h("Ganhos por categoria", 2))
for key, nome, _o in campos_cat:
    if nome.lower().strip() not in GANHOS_MANTER:
        continue
    da = (RA["por_campo"].get(nome) or {}).get("valor", {})
    db_ = (RB["por_campo"].get(nome) or {}).get("valor", {})
    if not da and not db_:
        continue
    corpo.append(_p(_run(f"Ganhos por “{nome}”", bold=True)))
    corpo.append(_tabela(HDR, _linhas(da, db_)))

_document = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
             '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'
             + "".join(corpo)
             + '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
               '<w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134"/></w:sectPr>'
               '</w:body></w:document>')
_ct = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
       '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
       '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
       '<Default Extension="xml" ContentType="application/xml"/>'
       '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
       '</Types>')
_rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
         '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
         '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
         '</Relationships>')
_docx = os.path.join(ARGS.saida, "relatorio.docx")
with zipfile.ZipFile(_docx, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", _ct)
    z.writestr("_rels/.rels", _rels)
    z.writestr("word/document.xml", _document)

print(f"  Word: {_docx}", file=sys.stderr)


# ---------------------------------------------------------------------------
# 7) Relatório EXCEL (.xlsx) — apresentável, para o "head bater o olho"
# ---------------------------------------------------------------------------

def gerar_xlsx(caminho):
    try:
        import openpyxl
    except ImportError:
        import subprocess
        print("  Instalando openpyxl (só na 1ª vez)...", file=sys.stderr)
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "openpyxl"], check=False)
        import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.chart import BarChart, Reference

    NAVY, ZEBRA, GREEN, RED, GRAY = "1F3864", "F2F5F9", "2E7D32", "C62828", "808080"
    F_NAME = "Calibri"
    hfont = Font(name=F_NAME, color="FFFFFF", bold=True, size=11)
    navy = PatternFill("solid", fgColor=NAVY)
    zebra = PatternFill("solid", fgColor=ZEBRA)
    thin = Side(style="thin", color="D9D9D9")
    bd = Border(left=thin, right=thin, top=thin, bottom=thin)
    AL = Alignment(horizontal="left", vertical="center")
    AC = Alignment(horizontal="center", vertical="center")
    AR = Alignment(horizontal="right", vertical="center")

    wb = openpyxl.Workbook()

    def cabecalho(ws, r, c0, cols):
        for j, h in enumerate(cols):
            cell = ws.cell(r, c0 + j, h)
            cell.font = hfont; cell.fill = navy; cell.border = bd
            cell.alignment = AL if j == 0 else AC

    def escreve(ws, r0, c0, titulo, da, db, moeda=True, largura0=26):
        ws.cell(r0, c0, titulo).font = Font(name=F_NAME, bold=True, size=12, color=NAVY)
        r = r0 + 1
        cabecalho(ws, r, c0, ["Item", L, R, "Δ %"])
        chaves = sorted(set(da) | set(db), key=lambda k: -(da.get(k, 0) + db.get(k, 0)))
        i = 0
        for k in chaves:
            r += 1; i += 1
            a, b = da.get(k, 0), db.get(k, 0)
            p = pct(b, a)
            fill = zebra if i % 2 == 0 else None
            ci = ws.cell(r, c0, str(k)); ci.alignment = AL
            ca = ws.cell(r, c0 + 1, a if moeda else int(a))
            cb = ws.cell(r, c0 + 2, b if moeda else int(b))
            if moeda:
                ca.number_format = cb.number_format = 'R$ #,##0'
            ca.alignment = cb.alignment = AR
            cd = ws.cell(r, c0 + 3, (p / 100.0) if p is not None else None)
            if p is not None:
                cd.number_format = '+0%;-0%'
                cd.font = Font(name=F_NAME, bold=True, color=(GREEN if p >= 0 else RED))
            cd.alignment = AC
            for j in range(4):
                cc = ws.cell(r, c0 + j); cc.border = bd
                if fill:
                    cc.fill = fill
        ws.column_dimensions[chr(64 + c0)].width = largura0
        for j in (1, 2, 3):
            ws.column_dimensions[chr(64 + c0 + j)].width = 14
        return r  # última linha escrita

    # ---- Aba PAINEL ----
    ws = wb.active; ws.title = "Painel"
    ws.sheet_view.showGridLines = False
    ws.merge_cells("A1:D1")
    t = ws.cell(1, 1, f"Comparativo — semana {ARGS.inicio.replace('-', '/')} a {ARGS.fim.replace('-', '/')}")
    t.font = Font(name=F_NAME, bold=True, size=18, color=NAVY)
    ws.merge_cells("A2:D2")
    st = ws.cell(2, 1, f"{me.get('company_name', '')}  ·  {L} vs {R}  ·  Δ = variação de {R} sobre {L}")
    st.font = Font(name=F_NAME, italic=True, size=10, color=GRAY)

    ws.cell(4, 1, "Resumo").font = Font(name=F_NAME, bold=True, size=12, color=NAVY)
    cabecalho(ws, 5, 1, ["Métrica", L, R, "Δ %"])
    kpis = [("Ganhos (R$)", RA["ganho_total"], RB["ganho_total"], True),
            ("Negócios ganhos", RA["ganho_qtd"], RB["ganho_qtd"], False),
            ("Ticket médio", RA["ticket_medio"], RB["ticket_medio"], True),
            ("Negócios criados", RA["criados_qtd"], RB["criados_qtd"], False),
            ("Negócios perdidos", RA["perdidos_qtd"], RB["perdidos_qtd"], False),
            ("Atividades (toques)", RA["ativ_total"], RB["ativ_total"], False)]
    r = 5
    for i, (nome, a, b, moeda) in enumerate(kpis, 1):
        r += 1; p = pct(b, a)
        ci = ws.cell(r, 1, nome); ci.alignment = AL; ci.font = Font(name=F_NAME, size=11)
        ca = ws.cell(r, 2, a if moeda else int(a)); cb = ws.cell(r, 3, b if moeda else int(b))
        if moeda:
            ca.number_format = cb.number_format = 'R$ #,##0'
        ca.alignment = cb.alignment = AR
        cd = ws.cell(r, 4, (p / 100.0) if p is not None else None)
        if p is not None:
            cd.number_format = '+0%;-0%'
            cd.font = Font(name=F_NAME, bold=True, size=11, color=(GREEN if p >= 0 else RED))
        cd.alignment = AC
        fill = zebra if i % 2 == 0 else None
        for j in range(1, 5):
            cc = ws.cell(r, j); cc.border = bd
            if fill:
                cc.fill = fill
    ws.column_dimensions["A"].width = 24
    for col in ("B", "C", "D"):
        ws.column_dimensions[col].width = 15
    ws.freeze_panes = "A6"

    # gráfico: ganhos por vendedor (fonte na aba Vendedores, criado depois)

    # ---- Aba VENDEDORES ----
    wv = wb.create_sheet("Vendedores")
    wv.sheet_view.showGridLines = False
    wv.cell(1, 1, "Vendedores").font = Font(name=F_NAME, bold=True, size=16, color=NAVY)
    fim_g = escreve(wv, 3, 1, "Ganho por vendedor",
                    com_closers(sem_cs(RA["por_dono_val"])), com_closers(sem_cs(RB["por_dono_val"])))
    escreve(wv, 3, 6, "Nº de ganhos por vendedor",
            com_closers(sem_cs(RA["por_dono_qtd"])), com_closers(sem_cs(RB["por_dono_qtd"])), moeda=False)
    # gráfico de barras: ganho por vendedor (2025 x 2026)
    if fim_g > 4:
        ch = BarChart(); ch.type = "bar"; ch.title = f"Ganho por vendedor  {L} x {R}"
        ch.height = 8; ch.width = 16
        dados = Reference(wv, min_col=2, max_col=3, min_row=4, max_row=fim_g)
        cats = Reference(wv, min_col=1, min_row=5, max_row=fim_g)
        ch.add_data(dados, titles_from_data=True); ch.set_categories(cats)
        wv.add_chart(ch, "A" + str(fim_g + 3))

    # ---- Aba SDR ----
    ws = wb.create_sheet("SDR")
    ws.sheet_view.showGridLines = False
    ws.cell(1, 1, "SDR (pré-vendas)").font = Font(name=F_NAME, bold=True, size=16, color=NAVY)
    fim_sdr = escreve(ws, 3, 1, "Leads gerados por SDR",
                      sem_cs(RA["por_sdr_criados"]), sem_cs(RB["por_sdr_criados"]), moeda=False)
    escreve(ws, 3, 6, "Vendas (R$) vindas dos leads do SDR",
            sem_cs(RA["por_sdr_ganho_val"]), sem_cs(RB["por_sdr_ganho_val"]), largura0=26)
    escreve(ws, fim_sdr + 3, 1, "Nº de vendas por SDR (lead dele que fechou)",
            sem_cs(RA["por_sdr_ganho_qtd"]), sem_cs(RB["por_sdr_ganho_qtd"]), moeda=False)

    # ---- Aba TOQUES ----
    wt = wb.create_sheet("Toques")
    wt.sheet_view.showGridLines = False
    wt.cell(1, 1, "Toques (atividades)").font = Font(name=F_NAME, bold=True, size=16, color=NAVY)
    escreve(wt, 3, 1, "Por tipo", RA["ativ_tipo"], RB["ativ_tipo"], moeda=False, largura0=22)
    escreve(wt, 3, 6, "Por pessoa",
            com_closers(sem_cs(RA["ativ_user"])), com_closers(sem_cs(RB["ativ_user"])), moeda=False)

    # ---- Aba LEADS E CANAIS ----
    wl = wb.create_sheet("Leads e Canais")
    wl.sheet_view.showGridLines = False
    wl.cell(1, 1, "Leads: volume e canal").font = Font(name=F_NAME, bold=True, size=16, color=NAVY)
    r = escreve(wl, 3, 1, "Leads criados por vendedor",
                com_closers(sem_cs(RA["por_dono_criados"])),
                com_closers(sem_cs(RB["por_dono_criados"])), moeda=False)
    r += 3
    for nome in sorted(set(RA["por_canal"]) | set(RB["por_canal"])):
        r = escreve(wl, r, 1, f"Leads por “{nome}”",
                    RA["por_canal"].get(nome, {}), RB["por_canal"].get(nome, {}),
                    moeda=False, largura0=30) + 3

    # ---- Aba GANHOS ----
    wg = wb.create_sheet("Ganhos")
    wg.sheet_view.showGridLines = False
    wg.cell(1, 1, "Ganhos por pipeline e categoria").font = Font(name=F_NAME, bold=True, size=16, color=NAVY)
    r = escreve(wg, 3, 1, "Ganhos por pipeline", RA["por_pipeline"], RB["por_pipeline"], largura0=30) + 3
    for key, nome, _o in campos_cat:
        if nome.lower().strip() not in GANHOS_MANTER:
            continue
        da = (RA["por_campo"].get(nome) or {}).get("valor", {})
        db_ = (RB["por_campo"].get(nome) or {}).get("valor", {})
        if not da and not db_:
            continue
        r = escreve(wg, r, 1, f"Ganhos por “{nome}”", da, db_, largura0=30) + 3

    wb.save(caminho)


_xlsx = os.path.join(ARGS.saida, "relatorio.xlsx")
gerar_xlsx(_xlsx)
print(f"\n  >>> EXCEL gerado: {_xlsx}")
print("  Abra no Excel (abas: Painel, Vendedores, Toques, Leads e Canais, Ganhos).")
print("  (também gerou relatorio.docx, relatorio.html e resumo.json)\n")
