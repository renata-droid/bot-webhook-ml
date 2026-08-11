#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DESCOBRE todos os LEAD A do closer MATHEUS MEDEIROS (sem filtro de mes).

Pega TODOS os negocios do Matheus (por Proprietario OU etiqueta) e marca os
que sao Lead A -> pelo CAMPO Lead (=A) OU pela ETIQUETA "LEAD A" (id 256).
Mostra as datas de cada um (criado / reuniao / fechamento esperado) pra voce
enxergar QUAL data o filtro "deste mes" esta derrubando.

Uso:  export PIPEDRIVE_TOKEN=...   (ou usa o embutido)
      python pipedrive_leadA_matheus_descobrir.py
Saida: leadA_matheus_TODOS.csv
"""
import os, sys, csv, time
import requests

TOKEN = os.environ.get("PIPEDRIVE_TOKEN", "5497d52719432ce49d0ad281cb71108be7212129").strip()
COMPANY_DOMAIN = os.environ.get("PIPEDRIVE_DOMAIN", "").strip()

CLOSER_NOME = "Matheus Medeiros"
CLOSER_LABEL_ID = 660       # etiqueta "Matheus Medeiros"
LEAD_A_LABEL_ID = 256       # etiqueta "LEAD A"
LEAD_FIELD_KEY = "1cb9ad4729d5f241f8a329045613582070ee2c95"  # campo Lead
LEAD_A_OPTION_ID = "217"    # opcao "A" do campo Lead
MES_REF = "2026-08"         # mes que voce esta filtrando (YYYY-MM)


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


def achar_user_id(nome):
    for u in (api_get("users").get("data") or []):
        if (u.get("name") or "").strip().lower() == nome.strip().lower():
            return u.get("id")
    return None


def tem_label(deal, alvo):
    ids = deal.get("label_ids")
    if isinstance(ids, list):
        return alvo in [int(x) for x in ids if str(x).isdigit()]
    lab = deal.get("label")
    return lab is not None and str(alvo) in [p.strip() for p in str(lab).split(",")]


def eh_lead_a(deal):
    campo = deal.get(LEAD_FIELD_KEY)
    if str(campo) == LEAD_A_OPTION_ID:
        return True
    return tem_label(deal, LEAD_A_LABEL_ID)


def puxar_todos_do_dono(uid):
    """Pagina TODOS os negocios (qualquer status) do proprietario uid."""
    out, start = [], 0
    while True:
        d = api_get("deals", {"user_id": uid, "status": "all_not_deleted",
                              "start": start, "limit": 500})
        itens = d.get("data") or []
        out.extend(itens)
        info = (d.get("additional_data") or {}).get("pagination") or {}
        if info.get("more_items_in_collection"):
            start = info.get("next_start", start + 500); time.sleep(0.2)
        else:
            break
    return out


def main():
    if not TOKEN:
        print("!! Defina PIPEDRIVE_TOKEN"); return

    uid = achar_user_id(CLOSER_NOME)
    print(f"user_id de {CLOSER_NOME}: {uid}")
    todos = puxar_todos_do_dono(uid) if uid else []
    print(f"Negocios do Matheus (proprietario): {len(todos)}")

    a = [d for d in todos if eh_lead_a(d)]
    print(f"  destes, Lead A: {len(a)}")

    linhas = []
    for d in a:
        criado = (d.get("add_time") or "")[:10]
        reuniao = d.get("c8a99e668e9913e2362556c43a03bd821db81006") or ""
        fecha = d.get("expected_close_date") or ""
        linhas.append({
            "deal_id": d.get("id"),
            "titulo": d.get("title", ""),
            "status": d.get("status", ""),
            "lead_campo": "A" if str(d.get(LEAD_FIELD_KEY)) == LEAD_A_OPTION_ID else "",
            "etiqueta_LEAD_A": "SIM" if tem_label(d, LEAD_A_LABEL_ID) else "",
            "criado_em": criado,
            "dia_reuniao": reuniao,
            "fechamento_esperado": fecha,
            "no_mes_ref": "SIM" if MES_REF in (criado, reuniao[:7], fecha[:7]) else "NAO",
            "valor": d.get("value", ""),
        })

    linhas.sort(key=lambda x: x["deal_id"])
    cols = ["deal_id", "titulo", "status", "lead_campo", "etiqueta_LEAD_A",
            "criado_em", "dia_reuniao", "fechamento_esperado", "no_mes_ref", "valor"]
    with open("leadA_matheus_TODOS.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(linhas)

    print("-" * 64)
    for l in linhas:
        print(f"  deal/{l['deal_id']} [{l['status']:<7}] campo={l['lead_campo'] or '-':<1} "
              f"etq={l['etiqueta_LEAD_A'] or '-':<3} mes={l['no_mes_ref']:<3} {l['titulo'][:32]}")
    no_mes = sum(1 for l in linhas if l["no_mes_ref"] == "SIM")
    print("-" * 64)
    print(f"TOTAL Lead A do Matheus: {len(linhas)}  |  no mes {MES_REF}: {no_mes}")
    print("Arquivo: leadA_matheus_TODOS.csv")


if __name__ == "__main__":
    main()
