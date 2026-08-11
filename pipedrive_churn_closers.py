#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
 CHURN POR CLOSER  -  Pipedrive  (01/01/2026 -> 10/08/2026)
==============================================================================

O QUE FAZ
---------
Le TODOS os negocios, marca os que CANCELARAM no periodo (campo "Data do
Cancelamento" dentro da janela) e atribui ao closer (campo "Vendedor").
Gera rankings e cruzamentos:

  churn_ranking_closer.csv    closer x (qtd churn, valor, reembolso, taxa%)
  churn_closer_x_lead.csv     closer x grade do Lead (A..F)
  churn_closer_x_produto.csv  closer x produto vendido
  churn_motivos.csv           motivo do churn (qtd, valor)
  churn_por_mes.csv           curva de churn por mes
  churn_detalhe.csv           1 linha por negocio cancelado (auditoria)

A "taxa de churn" usa como base os negocios GANHOS do closer no mesmo periodo
(won_time na janela) -> e uma aproximacao, mas ja da o ranking relativo.

COMO USAR
---------
    export PIPEDRIVE_TOKEN=...        # (Windows: set PIPEDRIVE_TOKEN=...)
    python pipedrive_churn_closers.py
==============================================================================
"""
import os, csv, time
from collections import defaultdict, Counter

import requests

# =============================================================================
# CONFIG
# =============================================================================
TOKEN = os.environ.get("PIPEDRIVE_TOKEN", "5497d52719432ce49d0ad281cb71108be7212129").strip()
COMPANY_DOMAIN = os.environ.get("PIPEDRIVE_DOMAIN", "").strip()

PERIODO_INI = "2026-01-01"
PERIODO_FIM = "2026-08-10"      # ate ontem

# marcador de churn: data dentro do periodo neste campo
K_DATA_CANCEL   = "2c29e719270fbfd6ecd08493148c39a00e0befba"  # Data do Cancelamento
K_DATA_SOLIC    = "cd0cc16e257579e4210871e5cfb26876b87c442b"  # Data Solicitacao Cancelamento
K_MOTIVO_CHURN  = "9755e115e954e1c1328c81979d6d190434a444db"  # Motivo Churn (set)
K_REEMBOLSO     = "77ee68c16f4760b4e17f6aafe4044996afc689f4"  # Valor Reembolsado
K_VENDEDOR      = "db2c9632937b836eae914bb3749d19f3b129b31d"  # Vendedor (closer)
K_LEAD          = "1cb9ad4729d5f241f8a329045613582070ee2c95"  # Lead (A..F)
K_PRODUTO       = "6621eda2196194ded0bd671ae263ccbcb213666c"  # Produto (vendido)

PAUSA = 0.2


# =============================================================================
# API
# =============================================================================
def base_url():
    return (f"https://{COMPANY_DOMAIN}.pipedrive.com/api/v1"
            if COMPANY_DOMAIN else "https://api.pipedrive.com/v1")


def api_get(endpoint, params=None):
    params = dict(params or {}); params["api_token"] = TOKEN
    for t in range(3):
        try:
            r = requests.get(f"{base_url()}/{endpoint}", params=params,
                             headers={"Accept": "application/json"}, timeout=60)
            if r.status_code == 200:
                return r.json()
            if r.status_code == 429:
                time.sleep(2 * (t + 1)); continue
            print(f"  !! HTTP {r.status_code} {endpoint}: {r.text[:120]}"); return {}
        except requests.RequestException as e:
            if t == 2:
                print(f"  !! erro {endpoint}: {e}"); return {}
            time.sleep(1.5 * (t + 1))
    return {}


def carregar_mapa_opcoes():
    data = api_get("dealFields", {"limit": 500})
    mapa = {}
    for f in (data.get("data") or []):
        key, opts = f.get("key"), f.get("options")
        if key and opts:
            mapa[key] = {str(o.get("id")): o.get("label") for o in opts}
    return mapa


def carregar_usuarios():
    return {u.get("id"): u.get("name")
            for u in (api_get("users").get("data") or [])}


def puxar_todos_deals():
    """Pagina TODOS os negocios (qualquer status, exceto deletados)."""
    out, start = [], 0
    while True:
        d = api_get("deals", {"status": "all_not_deleted", "start": start, "limit": 500})
        itens = d.get("data") or []
        out.extend(itens)
        info = (d.get("additional_data") or {}).get("pagination") or {}
        if info.get("more_items_in_collection"):
            start = info.get("next_start", start + 500); time.sleep(PAUSA)
        else:
            break
    return out


# =============================================================================
# HELPERS
# =============================================================================
def opt(valor, key, mapa):
    if valor in (None, ""):
        return ""
    if isinstance(valor, str) and "," in valor:
        return ", ".join(mapa.get(key, {}).get(p.strip(), p.strip()) for p in valor.split(","))
    return mapa.get(key, {}).get(str(valor), valor)


def nome_closer(deal, users, mapa):
    v = deal.get(K_VENDEDOR)
    if isinstance(v, dict):
        v = v.get("value") or v.get("id")
    if v not in (None, ""):
        return users.get(v) or users.get(int(v) if str(v).isdigit() else v) or f"user {v}"
    # fallback: proprietario
    o = deal.get("user_id")
    if isinstance(o, dict):
        return o.get("name") or "(sem closer)"
    return users.get(o, "(sem closer)")


def no_periodo(d):
    return bool(d) and PERIODO_INI <= d[:10] <= PERIODO_FIM


def num(v):
    try: return float(v)
    except Exception: return 0.0


# =============================================================================
# MAIN
# =============================================================================
def main():
    if not TOKEN:
        print("!! Defina PIPEDRIVE_TOKEN"); return

    print("Carregando campos e usuarios...")
    mapa = carregar_mapa_opcoes()
    users = carregar_usuarios()
    print("Puxando todos os negocios (pode levar alguns minutos)...")
    deals = puxar_todos_deals()
    print(f"Total de negocios: {len(deals)}")

    # ganhos por closer no periodo (base da taxa)
    ganhos = Counter()
    for d in deals:
        if d.get("status") == "won" and no_periodo(d.get("won_time") or ""):
            ganhos[nome_closer(d, users, mapa)] += 1

    # churn no periodo
    churn = [d for d in deals if no_periodo(d.get(K_DATA_CANCEL) or "")]
    print(f"Cancelamentos no periodo {PERIODO_INI}..{PERIODO_FIM}: {len(churn)}")

    rank = defaultdict(lambda: {"qtd": 0, "valor": 0.0, "reemb": 0.0})
    x_lead = Counter(); x_prod = Counter()
    motivos = defaultdict(lambda: {"qtd": 0, "valor": 0.0})
    por_mes = defaultdict(lambda: {"qtd": 0, "valor": 0.0})
    detalhe = []

    for d in churn:
        closer = nome_closer(d, users, mapa)
        valor = num(d.get("value"))
        reemb = num(d.get(K_REEMBOLSO))
        lead = opt(d.get(K_LEAD), K_LEAD, mapa) or "(sem)"
        prod = opt(d.get(K_PRODUTO), K_PRODUTO, mapa) or "(sem)"
        motivo = opt(d.get(K_MOTIVO_CHURN), K_MOTIVO_CHURN, mapa) or "(sem motivo)"
        dcancel = (d.get(K_DATA_CANCEL) or "")[:10]
        mes = dcancel[:7]
        won = (d.get("won_time") or "")[:10]
        dias = ""
        if won and dcancel:
            from datetime import date
            try:
                a = date.fromisoformat(won); b = date.fromisoformat(dcancel)
                dias = (b - a).days
            except Exception:
                dias = ""

        rank[closer]["qtd"] += 1
        rank[closer]["valor"] += valor
        rank[closer]["reemb"] += reemb
        x_lead[(closer, lead)] += 1
        x_prod[(closer, prod)] += 1
        motivos[motivo]["qtd"] += 1; motivos[motivo]["valor"] += valor
        por_mes[mes]["qtd"] += 1; por_mes[mes]["valor"] += valor
        detalhe.append({
            "deal_id": d.get("id"), "closer": closer, "titulo": d.get("title", ""),
            "lead": lead, "produto": prod, "motivo_churn": motivo,
            "data_cancelamento": dcancel, "ganho_em": won, "dias_ate_churn": dias,
            "valor": valor, "valor_reembolsado": reemb,
        })

    # ---------- ranking closer ----------
    linhas_rank = []
    for c, v in rank.items():
        base = ganhos.get(c, 0)
        taxa = round(100 * v["qtd"] / base, 1) if base else ""
        linhas_rank.append({"closer": c, "qtd_churn": v["qtd"],
                            "valor_churn": round(v["valor"], 2),
                            "valor_reembolsado": round(v["reemb"], 2),
                            "ganhos_periodo": base, "taxa_churn_%": taxa})
    linhas_rank.sort(key=lambda x: (-x["qtd_churn"], -x["valor_churn"]))

    def escrever(nome, cols, linhas):
        with open(nome, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader(); w.writerows(linhas)

    escrever("churn_ranking_closer.csv",
             ["closer", "qtd_churn", "valor_churn", "valor_reembolsado",
              "ganhos_periodo", "taxa_churn_%"], linhas_rank)
    escrever("churn_closer_x_lead.csv", ["closer", "lead", "qtd"],
             [{"closer": c, "lead": l, "qtd": n} for (c, l), n in
              sorted(x_lead.items(), key=lambda x: -x[1])])
    escrever("churn_closer_x_produto.csv", ["closer", "produto", "qtd"],
             [{"closer": c, "produto": p, "qtd": n} for (c, p), n in
              sorted(x_prod.items(), key=lambda x: -x[1])])
    escrever("churn_motivos.csv", ["motivo", "qtd", "valor"],
             [{"motivo": m, "qtd": v["qtd"], "valor": round(v["valor"], 2)} for m, v in
              sorted(motivos.items(), key=lambda x: -x[1]["qtd"])])
    escrever("churn_por_mes.csv", ["mes", "qtd", "valor"],
             [{"mes": m, "qtd": v["qtd"], "valor": round(v["valor"], 2)} for m, v in
              sorted(por_mes.items())])
    escrever("churn_detalhe.csv",
             ["deal_id", "closer", "titulo", "lead", "produto", "motivo_churn",
              "data_cancelamento", "ganho_em", "dias_ate_churn", "valor",
              "valor_reembolsado"], detalhe)

    # ---------- resumo na tela ----------
    print("-" * 70)
    print("RANKING DE CHURN POR CLOSER (qtd | valor | taxa)")
    for l in linhas_rank[:15]:
        print(f"  {l['closer'][:26]:<27} {l['qtd_churn']:>3}  "
              f"R$ {l['valor_churn']:>12,.0f}  taxa {l['taxa_churn_%']}%")
    print("-" * 70)
    print("TOP MOTIVOS DE CHURN")
    for m, v in sorted(motivos.items(), key=lambda x: -x[1]["qtd"])[:8]:
        print(f"  {m[:40]:<41} {v['qtd']:>3}")
    print("-" * 70)
    print(f"Total churn: {len(churn)}  |  valor: "
          f"R$ {sum(num(d.get('value')) for d in churn):,.0f}")
    print("Arquivos: churn_ranking_closer.csv, churn_closer_x_lead.csv, "
          "churn_closer_x_produto.csv, churn_motivos.csv, churn_por_mes.csv, churn_detalhe.csv")


if __name__ == "__main__":
    main()
