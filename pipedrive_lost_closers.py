#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
 PERDIDOS (LOST) POR CLOSER  -  Pipedrive  (01/01/2026 -> 10/08/2026)
==============================================================================

Le todos os negocios, pega os PERDIDOS no periodo (lost_time na janela),
atribui ao closer (Vendedor) e cruza:

  lost_ranking_closer.csv   closer x (qtd, valor, dias medios ate o lost, taxa%)
  lost_closer_x_lead.csv    closer x grade do Lead (A..F)
  lost_motivos.csv          motivo da perda (dropdown OU texto real "Descricao da Perda")
  lost_por_produto.csv      produto apresentado x qtd
  lost_por_etapa.csv        etapa onde perdeu x qtd
  lost_por_mes.csv          curva de perdas por mes
  lost_detalhe.csv          1 linha por negocio perdido (auditoria)

"Tempo ate o lost": dias entre a criacao (add_time) e a perda (lost_time).
Tambem calcula dias desde o SAL (lead aceito pelo closer), quando existir.
"Taxa de lost" = perdidos / (perdidos + ganhos) do closer no periodo.

COMO USAR
---------
    python pipedrive_lost_closers.py        (token embutido; revogue depois)
==============================================================================
"""
import os, csv, time
from datetime import date
from collections import defaultdict, Counter

import requests

# =============================================================================
# CONFIG
# =============================================================================
TOKEN = os.environ.get("PIPEDRIVE_TOKEN", "5497d52719432ce49d0ad281cb71108be7212129").strip()
COMPANY_DOMAIN = os.environ.get("PIPEDRIVE_DOMAIN", "").strip()

PERIODO_INI = "2026-01-01"
PERIODO_FIM = "2026-08-10"

K_VENDEDOR = "db2c9632937b836eae914bb3749d19f3b129b31d"   # Vendedor (closer)
K_LEAD     = "1cb9ad4729d5f241f8a329045613582070ee2c95"   # Lead (A..F)
K_PROD_APR = "810aeffbcd6e447f89e9b82d1a977738a10f2f86"   # Produto Apresentado
K_PRODUTO  = "6621eda2196194ded0bd671ae263ccbcb213666c"   # Produto (vendido)
K_SAL      = "62df15f8b5a4071a910ee37b0a4b4654afbc48db"   # Data Lead Aceito Closer (SAL)
K_DESC     = "c1056dfb2bc711a3a2dc66b4dc9c83a436a36a84"   # Descricao DETALHADA da Perda
PAUSA = 0.2


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
    return {u.get("id"): u.get("name") for u in (api_get("users").get("data") or [])}


def carregar_etapas():
    return {s.get("id"): s.get("name") for s in (api_get("stages", {"limit": 500}).get("data") or [])}


def puxar_deals(status):
    out, start = [], 0
    while True:
        d = api_get("deals", {"status": status, "start": start, "limit": 500})
        out.extend(d.get("data") or [])
        info = (d.get("additional_data") or {}).get("pagination") or {}
        if info.get("more_items_in_collection"):
            start = info.get("next_start", start + 500); time.sleep(PAUSA)
        else:
            break
    return out


def opt(valor, key, mapa):
    if valor in (None, ""):
        return ""
    if isinstance(valor, str) and "," in valor:
        return ", ".join(mapa.get(key, {}).get(p.strip(), p.strip()) for p in valor.split(","))
    return mapa.get(key, {}).get(str(valor), valor)


def closer_de(d, users):
    v = d.get(K_VENDEDOR)
    if isinstance(v, dict):
        v = v.get("value") or v.get("id")
    if v not in (None, ""):
        return users.get(v) or users.get(int(v) if str(v).isdigit() else v) or f"user {v}"
    o = d.get("user_id")
    if isinstance(o, dict):
        return o.get("name") or "(sem closer)"
    return users.get(o, "(sem closer)")


def no_periodo(d):
    return bool(d) and PERIODO_INI <= d[:10] <= PERIODO_FIM


def num(v):
    try: return float(v)
    except Exception: return 0.0


def dias(ini, fim):
    try:
        return (date.fromisoformat(fim[:10]) - date.fromisoformat(ini[:10])).days
    except Exception:
        return None


def responsavel_motivo(m):
    m = (m or "").lower()
    if "sdr/closer" in m or ("[closer]" in m and "[sdr]" in m): return "Closer/SDR"
    if "[closer]" in m: return "Closer"
    if "[sdr]" in m: return "SDR"
    return "Outro"


def main():
    if not TOKEN:
        print("!! Defina PIPEDRIVE_TOKEN"); return
    print("Carregando campos/usuarios/etapas...")
    mapa = carregar_mapa_opcoes(); users = carregar_usuarios(); etapas = carregar_etapas()
    print("Puxando perdidos e ganhos...")
    perdidos = puxar_deals("lost")
    ganhos = puxar_deals("won")

    # base da taxa: ganhos no periodo por closer
    base = Counter()
    for d in ganhos:
        if no_periodo(d.get("won_time") or ""):
            base[closer_de(d, users)] += 1

    lost = [d for d in perdidos if no_periodo(d.get("lost_time") or "")]
    print(f"Perdidos no periodo {PERIODO_INI}..{PERIODO_FIM}: {len(lost)}")

    rank = defaultdict(lambda: {"qtd": 0, "valor": 0.0, "dias": []})
    x_lead = Counter(); x_prod = Counter(); x_etapa = Counter()
    motivos = defaultdict(lambda: {"qtd": 0, "valor": 0.0, "resp": ""})
    por_mes = defaultdict(lambda: {"qtd": 0, "valor": 0.0})
    detalhe = []

    for d in lost:
        closer = closer_de(d, users)
        valor = num(d.get("value"))
        lead = opt(d.get(K_LEAD), K_LEAD, mapa) or "(sem)"
        prod = opt(d.get(K_PROD_APR), K_PROD_APR, mapa) or opt(d.get(K_PRODUTO), K_PRODUTO, mapa) or "(sem)"
        motivo_drop = d.get("lost_reason") or ""                       # dropdown (quase sempre vazio)
        desc = (d.get(K_DESC) or "").replace("\n", " ").strip()        # texto livre = motivo real
        motivo = motivo_drop or desc or "(sem motivo)"                 # usa o que tiver
        etapa = etapas.get(d.get("stage_id"), d.get("stage_id"))
        lt = (d.get("lost_time") or "")[:10]
        dcriacao = dias(d.get("add_time") or "", lt) if d.get("add_time") else None
        dsal = dias(d.get(K_SAL) or "", lt) if d.get(K_SAL) else None

        rank[closer]["qtd"] += 1
        rank[closer]["valor"] += valor
        if dcriacao is not None:
            rank[closer]["dias"].append(dcriacao)
        x_lead[(closer, lead)] += 1
        x_prod[prod] += 1
        x_etapa[etapa] += 1
        motivos[motivo]["qtd"] += 1; motivos[motivo]["valor"] += valor
        motivos[motivo]["resp"] = responsavel_motivo(motivo_drop)
        por_mes[lt[:7]]["qtd"] += 1; por_mes[lt[:7]]["valor"] += valor
        detalhe.append({
            "deal_id": d.get("id"), "closer": closer, "titulo": d.get("title", ""),
            "lead": lead, "produto": prod, "motivo_perda": motivo,
            "motivo_dropdown": motivo_drop, "responsavel": responsavel_motivo(motivo_drop),
            "etapa": etapa,
            "criado_em": (d.get("add_time") or "")[:10], "perdido_em": lt,
            "dias_ate_lost": dcriacao if dcriacao is not None else "",
            "dias_desde_SAL": dsal if dsal is not None else "",
            "descricao_perda": (d.get(K_DESC) or "").replace("\n", " ")[:300],
            "valor": valor,
        })

    # ranking closer
    linhas_rank = []
    for c, v in rank.items():
        med = round(sum(v["dias"]) / len(v["dias"]), 1) if v["dias"] else ""
        b = base.get(c, 0)
        taxa = round(100 * v["qtd"] / (v["qtd"] + b), 1) if (v["qtd"] + b) else ""
        linhas_rank.append({"closer": c, "qtd_lost": v["qtd"],
                            "valor_lost": round(v["valor"], 2),
                            "dias_medio_ate_lost": med,
                            "ganhos_periodo": b, "taxa_lost_%": taxa})
    linhas_rank.sort(key=lambda x: (-x["qtd_lost"], -x["valor_lost"]))

    def escrever(nome, cols, linhas):
        with open(nome, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader(); w.writerows(linhas)

    escrever("lost_ranking_closer.csv",
             ["closer", "qtd_lost", "valor_lost", "dias_medio_ate_lost",
              "ganhos_periodo", "taxa_lost_%"], linhas_rank)
    escrever("lost_closer_x_lead.csv", ["closer", "lead", "qtd"],
             [{"closer": c, "lead": l, "qtd": n} for (c, l), n in
              sorted(x_lead.items(), key=lambda x: -x[1])])
    escrever("lost_motivos.csv", ["motivo", "responsavel", "qtd", "valor"],
             [{"motivo": m, "responsavel": v["resp"], "qtd": v["qtd"],
               "valor": round(v["valor"], 2)} for m, v in
              sorted(motivos.items(), key=lambda x: -x[1]["qtd"])])
    escrever("lost_por_produto.csv", ["produto", "qtd"],
             [{"produto": p, "qtd": n} for p, n in sorted(x_prod.items(), key=lambda x: -x[1])])
    escrever("lost_por_etapa.csv", ["etapa", "qtd"],
             [{"etapa": e, "qtd": n} for e, n in sorted(x_etapa.items(), key=lambda x: -x[1])])
    escrever("lost_por_mes.csv", ["mes", "qtd", "valor"],
             [{"mes": m, "qtd": v["qtd"], "valor": round(v["valor"], 2)} for m, v in
              sorted(por_mes.items())])
    escrever("lost_detalhe.csv",
             ["deal_id", "closer", "titulo", "lead", "produto", "motivo_perda",
              "motivo_dropdown", "responsavel", "etapa", "criado_em", "perdido_em",
              "dias_ate_lost", "dias_desde_SAL", "descricao_perda", "valor"], detalhe)

    # resumo na tela
    print("-" * 74)
    print("RANKING DE LOST POR CLOSER (qtd | valor | dias medios | taxa)")
    for l in linhas_rank[:15]:
        print(f"  {l['closer'][:24]:<25} {l['qtd_lost']:>3}  "
              f"R$ {l['valor_lost']:>11,.0f}  {str(l['dias_medio_ate_lost']):>6}d  "
              f"taxa {l['taxa_lost_%']}%")
    print("-" * 74)
    print("TOP MOTIVOS DE PERDA")
    for m, v in sorted(motivos.items(), key=lambda x: -x[1]["qtd"])[:10]:
        print(f"  [{v['resp']:<10}] {m[:42]:<43} {v['qtd']:>3}")
    print("-" * 74)
    resp_tot = Counter()
    for d in detalhe: resp_tot[d["responsavel"]] += 1
    print("Perdas por responsavel:", dict(resp_tot))
    print(f"Total lost: {len(lost)}  |  valor: R$ {sum(num(d.get('value')) for d in lost):,.0f}")
    print("Arquivos: lost_ranking_closer.csv, lost_closer_x_lead.csv, lost_motivos.csv,")
    print("          lost_por_produto.csv, lost_por_etapa.csv, lost_por_mes.csv, lost_detalhe.csv")


if __name__ == "__main__":
    main()
