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


def nome_dono(deal):
    u = deal.get("user_id")
    if isinstance(u, dict):
        return u.get("name") or f"user {u.get('id')}"
    return f"user {u}"


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
        por_dono_val[nome_dono(d)] += valor(d)
        por_dono_qtd[nome_dono(d)] += 1
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
    # atividades por tipo e por usuário
    ativ_tipo, ativ_user = defaultdict(int), defaultdict(int)
    for a in P["atividades"]:
        ativ_tipo[a.get("type") or "?"] += 1
        ativ_user[a.get("owner_name") or a.get("assigned_to_user_id") or "?"] += 1
    return {
        "ganho_total": total,
        "ganho_qtd": len(g),
        "criados_qtd": len(P["criados"]),
        "perdidos_qtd": len(P["perdidos"]),
        "ticket_medio": (total / len(g)) if g else 0.0,
        "por_dono_val": dict(por_dono_val),
        "por_dono_qtd": dict(por_dono_qtd),
        "por_pipeline": dict(por_pipeline),
        "por_campo": por_campo,
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
print(f"  Relatório completo -> {os.path.join(ARGS.saida, 'relatorio.html')}\n")


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
    da = RA["por_campo"].get(nome); db_ = RB["por_campo"].get(nome)
    if not da and not db_:
        continue
    campos_html += tabela_comparada(f"Ganhos por “{nome}” (valor)",
                                    (da or {}).get("valor", {}), (db_ or {}).get("valor", {}))

prod_a = {k: v["valor"] for k, v in RA["produtos"].items()}
prod_b = {k: v["valor"] for k, v in RB["produtos"].items()}

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

<div class="grid">
  <div>{tabela_comparada("Ganhos por vendedor (valor)", RA['por_dono_val'], RB['por_dono_val'])}</div>
  <div>{tabela_comparada("Nº de ganhos por vendedor", RA['por_dono_qtd'], RB['por_dono_qtd'], is_moeda=False)}</div>
</div>

{tabela_comparada("Ganhos por produto (line items)", prod_a, prod_b)}
{tabela_comparada("Ganhos por pipeline", RA['por_pipeline'], RB['por_pipeline'])}
{campos_html}

<div class="grid">
  <div>{tabela_comparada("Atividades por tipo", RA['ativ_tipo'], RB['ativ_tipo'], is_moeda=False)}</div>
  <div>{tabela_comparada("Atividades por pessoa", RA['ativ_user'], RB['ativ_user'], is_moeda=False)}</div>
</div>

</body></html>"""

with open(os.path.join(ARGS.saida, "relatorio.html"), "w", encoding="utf-8") as f:
    f.write(html)

# JSON bruto agregado (útil se você quiser me mandar de volta para eu analisar)
with open(os.path.join(ARGS.saida, "resumo.json"), "w", encoding="utf-8") as f:
    json.dump({"ano_a": ARGS.ano_a, "ano_b": ARGS.ano_b,
               "resumo_a": RA, "resumo_b": RB}, f, ensure_ascii=False, indent=2, default=str)

print("Concluído. Abra saida/relatorio.html e, se quiser, me mande o saida/resumo.json.\n")
