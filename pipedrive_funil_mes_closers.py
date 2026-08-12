#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
 FUNIL DO MES POR CLOSER (cohort)  -  Pipedrive
==============================================================================

Corrige o problema do "lost inflado por faxina de pipeline": em vez de contar
tudo que foi MARCADO como perdido no mes (que junta deal velho de meses atras
limpado de uma vez), este script trabalha por COHORT:

  1) Pega as OPORTUNIDADES CRIADAS no mes (add_time dentro da janela).
  2) Classifica cada uma pelo status ATUAL: Ganho / Perdido / Aberto.
  3) Por closer: nro de ops, ganhas, perdidas, abertas, TAXA DE PERDA real,
     e o valor perdido -> so das ops que nasceram no mes.

Assim "ops do mes" e "perdas do mes" batem: mede o que nasceu e morreu no mes.

Saidas:
  funil_mes_closer.csv     closer x (ops, ganhas, perdidas, abertas, taxa%, valor_perdido)
  funil_mes_perdas.csv     1 linha por oportunidade PERDIDA do cohort (auditoria)
  funil_mes_motivos.csv    motivo da perda (dropdown OU texto real) das perdas do cohort
  funil_mes_x_lead.csv     closer x grade do Lead (das perdas)
  funil_mes_x_produto.csv  produto x qtd (das perdas)

ANCORA do cohort = add_time (Negocio criado em). Troque ANCHOR p/ o campo
"Dia Oportunidade" se preferir contar pela data de oportunidade.

COMO USAR
---------
    python pipedrive_funil_mes_closers.py     (token embutido; revogue depois)
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

PERIODO_INI = "2026-08-01"
PERIODO_FIM = "2026-08-11"
ANCHOR = "add_time"                 # data que define o cohort (criacao). Alt: campo Dia Oportunidade
K_DIA_OPORT = "395bf927e670b580aa5d012e9f242defca9f3050"   # se quiser usar: ANCHOR = K_DIA_OPORT

# considerar so perdas que chegaram a etapa de closer? (True = so closer)
SO_CLOSER = True
CLOSER_STAGES = {"Reunião Realizada", "Negociação da Proposta", "Retorno Agendado",
                 "Retorno Realizado", "Follow UP", "Proposta Enviada", "Link Enviado", "Perdido"}

K_VENDEDOR = "db2c9632937b836eae914bb3749d19f3b129b31d"
K_LEAD     = "1cb9ad4729d5f241f8a329045613582070ee2c95"
K_PROD_APR = "810aeffbcd6e447f89e9b82d1a977738a10f2f86"
K_PRODUTO  = "6621eda2196194ded0bd671ae263ccbcb213666c"
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


def puxar_todos_deals():
    out, start = [], 0
    while True:
        d = api_get("deals", {"status": "all_not_deleted", "start": start, "limit": 500})
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


def responsavel_motivo(m):
    m = (m or "").lower()
    if "sdr/closer" in m or ("[closer]" in m and "[sdr]" in m): return "Closer/SDR"
    if "[closer]" in m: return "Closer"
    if "[sdr]" in m: return "SDR"
    return "Outro"


def main():
    if not TOKEN:
        print("!! Defina PIPEDRIVE_TOKEN"); return
    print("Carregando campos/usuarios/etapas e puxando negocios...")
    mapa = carregar_mapa_opcoes(); users = carregar_usuarios(); etapas = carregar_etapas()
    deals = puxar_todos_deals()
    print(f"Total de negocios: {len(deals)}")

    # COHORT = oportunidades criadas no mes
    cohort = [d for d in deals if no_periodo(d.get(ANCHOR) or "")]
    print(f"Oportunidades criadas em {PERIODO_INI}..{PERIODO_FIM}: {len(cohort)}")

    rank = defaultdict(lambda: {"ops": 0, "ganho": 0, "perdido": 0, "aberto": 0, "valor_perd": 0.0})
    perdas, motivos, x_lead, x_prod = [], defaultdict(lambda: {"qtd": 0, "valor": 0.0, "resp": ""}), Counter(), Counter()

    for d in cohort:
        closer = closer_de(d, users)
        st = d.get("status")  # open / won / lost
        etapa = etapas.get(d.get("stage_id"), d.get("stage_id"))
        rank[closer]["ops"] += 1
        if st == "won":
            rank[closer]["ganho"] += 1
        elif st == "lost":
            # so conta como "perda de closer" se chegou a etapa de closer (se SO_CLOSER)
            if SO_CLOSER and etapa not in CLOSER_STAGES:
                rank[closer]["aberto"] += 0  # perda de topo/SDR: nao entra no funil de closer
                continue
            rank[closer]["perdido"] += 1
            valor = num(d.get("value"))
            rank[closer]["valor_perd"] += valor
            lead = opt(d.get(K_LEAD), K_LEAD, mapa) or "(sem)"
            prod = opt(d.get(K_PROD_APR), K_PROD_APR, mapa) or opt(d.get(K_PRODUTO), K_PRODUTO, mapa) or "(sem)"
            motivo_drop = d.get("lost_reason") or ""
            desc = (d.get(K_DESC) or "").replace("\n", " ").strip()
            motivo = motivo_drop or desc or "(sem motivo)"
            x_lead[(closer, lead)] += 1; x_prod[prod] += 1
            motivos[motivo]["qtd"] += 1; motivos[motivo]["valor"] += valor
            motivos[motivo]["resp"] = responsavel_motivo(motivo_drop)
            perdas.append({
                "deal_id": d.get("id"), "closer": closer, "titulo": d.get("title", ""),
                "lead": lead, "produto": prod, "motivo": motivo,
                "responsavel": responsavel_motivo(motivo_drop), "etapa": etapa,
                "criado_em": (d.get("add_time") or "")[:10],
                "perdido_em": (d.get("lost_time") or "")[:10],
                "descricao_perda": desc[:300], "valor": valor,
            })
        else:
            rank[closer]["aberto"] += 1

    # ranking closer (ordena por perdas)
    linhas = []
    for c, v in rank.items():
        base = v["ganho"] + v["perdido"]
        taxa = round(100 * v["perdido"] / base, 1) if base else ""
        linhas.append({"closer": c, "ops_criadas": v["ops"], "ganhas": v["ganho"],
                       "perdidas": v["perdido"], "abertas": v["aberto"],
                       "taxa_perda_%": taxa, "valor_perdido": round(v["valor_perd"], 2)})
    linhas.sort(key=lambda x: (-x["perdidas"], -x["valor_perdido"]))

    def escrever(nome, cols, dados):
        with open(nome, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader(); w.writerows(dados)

    escrever("funil_mes_closer.csv",
             ["closer", "ops_criadas", "ganhas", "perdidas", "abertas", "taxa_perda_%", "valor_perdido"], linhas)
    escrever("funil_mes_perdas.csv",
             ["deal_id", "closer", "titulo", "lead", "produto", "motivo", "responsavel",
              "etapa", "criado_em", "perdido_em", "descricao_perda", "valor"], perdas)
    escrever("funil_mes_motivos.csv", ["motivo", "responsavel", "qtd", "valor"],
             [{"motivo": m, "responsavel": v["resp"], "qtd": v["qtd"], "valor": round(v["valor"], 2)}
              for m, v in sorted(motivos.items(), key=lambda x: -x[1]["qtd"])])
    escrever("funil_mes_x_lead.csv", ["closer", "lead", "qtd"],
             [{"closer": c, "lead": l, "qtd": n} for (c, l), n in sorted(x_lead.items(), key=lambda x: -x[1])])
    escrever("funil_mes_x_produto.csv", ["produto", "qtd"],
             [{"produto": p, "qtd": n} for p, n in sorted(x_prod.items(), key=lambda x: -x[1])])

    tot_ops = len(cohort)
    tot_perd = sum(l["perdidas"] for l in linhas)
    tot_ganho = sum(l["ganhas"] for l in linhas)
    tot_valor = sum(l["valor_perdido"] for l in linhas)
    print("-" * 72)
    print(f"FUNIL DO MES (cohort de {tot_ops} oportunidades criadas no periodo)")
    print(f"  Ganhas: {tot_ganho} | Perdidas (closer): {tot_perd} | Valor perdido: R$ {tot_valor:,.0f}")
    print("-" * 72)
    print("Perdas de closer por closer (das ops criadas no mes):")
    for l in linhas:
        if l["perdidas"]:
            print(f"  {l['closer'][:24]:<25} ops {l['ops_criadas']:>3}  perd {l['perdidas']:>2}  "
                  f"R$ {l['valor_perdido']:>10,.0f}  taxa {l['taxa_perda_%']}%")
    print("Arquivos: funil_mes_closer.csv, funil_mes_perdas.csv, funil_mes_motivos.csv,")
    print("          funil_mes_x_lead.csv, funil_mes_x_produto.csv")


if __name__ == "__main__":
    main()
