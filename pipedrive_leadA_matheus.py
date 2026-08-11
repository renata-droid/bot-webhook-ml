#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
 LEAD A - closer MATHEUS MEDEIROS  ->  data + perfil do lead + produto apresentado
==============================================================================

O QUE FAZ
---------
1) Busca a lista de campos (dealFields) uma vez e monta o dicionario
   opcao_id -> texto, para decodificar os campos enum/set (senao eles vem
   como numero).
2) Para cada deal da lista TARGETS, pega o negocio em /deals/{id} e extrai:
       - DATA .............. Dia da Reuniao / Dia Oportunidade / Ganho em / Criado em
       - PERFIL DO LEAD .... grade Lead (A/B/C...), Score, Faturamentos,
                             Onde vende, Estado, Cidade, Cargo, Categoria,
                             Tipo de Negocio, Marketplaces, Tempo de ML,
                             Principal Dor, Objetivo, Pessoa, Organizacao
       - PRODUTO APRESENTADO  campo "Produto Apresentado" (id 280)
3) Confere se a etiqueta "Matheus Medeiros" (id 660) esta no negocio.
4) Salva  leadA_matheus.csv  e  leadA_matheus.json  na pasta atual.

COMO USAR
---------
    export PIPEDRIVE_TOKEN="seu_token_aqui"      # (Windows: set PIPEDRIVE_TOKEN=...)
    python pipedrive_leadA_matheus.py

    # ou passando ids diferentes:
    python pipedrive_leadA_matheus.py 114715 114805 ...
==============================================================================
"""

import os
import sys
import csv
import json
import time

import requests

# =============================================================================
# CONFIG
# =============================================================================
TOKEN = os.environ.get("PIPEDRIVE_TOKEN", "").strip()
COMPANY_DOMAIN = os.environ.get("PIPEDRIVE_DOMAIN", "").strip()  # opcional
PAUSA = 0.15  # segundos entre chamadas (educado com a API)

# etiqueta que marca o closer
CLOSER_LABEL_ID = 660          # "Matheus Medeiros"
CLOSER_LABEL_NOME = "Matheus Medeiros"

# os deals a puxar (pode sobrescrever pela linha de comando)
TARGETS_PADRAO = [114715, 114805, 114841, 114880, 115051, 115054, 115453, 115645]

# campos que compoem o "perfil do lead" (nome_amigavel -> key da API)
PERFIL_FIELDS = [
    ("lead_grade",              "1cb9ad4729d5f241f8a329045613582070ee2c95"),  # Lead A/B/C...
    ("score",                   "score"),
    ("faturamento_marketplaces","e5310680e97128cdd6fd135118b1c277f0538e21"),
    ("faturamento_fisico",      "e4b95213fed643447308e95399bbff05a7d31d87"),
    ("onde_vende",              "d166e9a3c962c7dcbf849b78100083ca42323505"),
    ("estado",                  "cbef5dcdc3dcb5fd20bb243a6f4291093cea5ed7"),
    ("cidade",                  "c3b792625224f2a850ee2d68a2ed8fb2243b2dd8"),
    ("cargo",                   "2c0d5e90bfdb3ced22e92a136f329b576d2ab2d9"),
    ("categoria_principal",     "4feca3e670cd5fa48432231cde645bca827551de"),
    ("tipo_negocio",            "d020ce7781ab8bebdd90fcf1c7ed874f0457ae64"),
    ("marketplaces_vende",      "85835ceac34a89350688bb976331fbd42f6bbbd7"),
    ("tempo_mercado_livre",     "18b907895a6e7674970f1901d4b81d00e295f8df"),
    ("principal_dor",           "88dbdbdebd39d50e0c4bad8e6cc7c05e3e1e0731"),
    ("objetivo",                "c99ef8ae335443d128839b8b63e3f35c0580125b"),
]

# datas relevantes (nome_amigavel -> key)
DATA_FIELDS = [
    ("dia_reuniao",     "c8a99e668e9913e2362556c43a03bd821db81006"),
    ("dia_oportunidade","395bf927e670b580aa5d012e9f242defca9f3050"),
    ("ganho_em",        "won_time"),
    ("criado_em",       "add_time"),
]

# produto apresentado (id 280) + produto vendido (id 65) para referencia
PRODUTO_APRESENTADO_KEY = "810aeffbcd6e447f89e9b82d1a977738a10f2f86"
PRODUTO_VENDIDO_KEY = "6621eda2196194ded0bd671ae263ccbcb213666c"


# =============================================================================
# API
# =============================================================================
def base_url():
    if COMPANY_DOMAIN:
        return f"https://{COMPANY_DOMAIN}.pipedrive.com/api/v1"
    return "https://api.pipedrive.com/v1"


def api_get(endpoint, params=None, tentativas=3):
    params = dict(params or {})
    params["api_token"] = TOKEN
    url = f"{base_url()}/{endpoint}"
    for t in range(tentativas):
        try:
            r = requests.get(url, params=params,
                             headers={"Accept": "application/json"}, timeout=60)
            if r.status_code == 200:
                return r.json()
            if r.status_code == 429:  # rate limit
                time.sleep(2 * (t + 1))
                continue
            print(f"    !! HTTP {r.status_code} em {endpoint}: {r.text[:150]}")
            return {}
        except requests.RequestException as e:
            if t == tentativas - 1:
                print(f"    !! erro em {endpoint}: {e}")
                return {}
            time.sleep(1.5 * (t + 1))
    return {}


# =============================================================================
# DECODIFICACAO DE CAMPOS
# =============================================================================
def carregar_mapa_opcoes():
    """Monta { field_key: { str(option_id): label } } a partir de dealFields."""
    data = api_get("dealFields", {"limit": 500})
    mapa = {}
    for f in (data.get("data") or []):
        key = f.get("key")
        opts = f.get("options")
        if key and opts:
            mapa[key] = {str(o.get("id")): o.get("label") for o in opts}
    return mapa


def decodificar(valor, key, mapa):
    """Traduz o valor de um campo enum/set para texto; senao devolve como esta."""
    if valor is None or valor == "":
        return ""
    # pessoa/org vem como dict {name: ...}
    if isinstance(valor, dict):
        return valor.get("name") or valor.get("value") or ""
    opcoes = mapa.get(key)
    if not opcoes:
        return valor
    # set (multiplo) pode vir como "1,2,3" ou lista
    if isinstance(valor, str) and "," in valor:
        partes = [p.strip() for p in valor.split(",")]
        return ", ".join(opcoes.get(p, p) for p in partes)
    if isinstance(valor, list):
        return ", ".join(opcoes.get(str(p), str(p)) for p in valor)
    return opcoes.get(str(valor), valor)


def tem_etiqueta_closer(deal):
    """True se a etiqueta Matheus Medeiros (660) esta no negocio."""
    ids = deal.get("label_ids")
    if isinstance(ids, list):
        return CLOSER_LABEL_ID in [int(x) for x in ids if str(x).isdigit()]
    lab = deal.get("label")
    if lab is None:
        return False
    partes = str(lab).split(",")
    return str(CLOSER_LABEL_ID) in [p.strip() for p in partes]


# =============================================================================
# MAIN
# =============================================================================
def main():
    if not TOKEN:
        print("!! Defina o token:  export PIPEDRIVE_TOKEN=...  (ou set no Windows)")
        return

    targets = [int(a) for a in sys.argv[1:] if a.isdigit()] or TARGETS_PADRAO
    print(f"Puxando {len(targets)} deals...")

    mapa = carregar_mapa_opcoes()
    if not mapa:
        print("!! Nao consegui carregar dealFields (token/conexao?). Abortando.")
        return

    linhas = []
    for did in targets:
        d = api_get(f"deals/{did}").get("data")
        if not d:
            print(f"  deal/{did}: NAO ENCONTRADO")
            linhas.append({"deal_id": did, "erro": "nao encontrado"})
            time.sleep(PAUSA)
            continue

        linha = {
            "deal_id": did,
            "titulo": d.get("title", ""),
            "status": d.get("status", ""),
            "valor": d.get("value", ""),
            "etiqueta_matheus": "SIM" if tem_etiqueta_closer(d) else "NAO",
        }
        # datas
        for nome, key in DATA_FIELDS:
            linha[nome] = d.get(key) or ""
        # produto apresentado / vendido
        linha["produto_apresentado"] = decodificar(d.get(PRODUTO_APRESENTADO_KEY),
                                                    PRODUTO_APRESENTADO_KEY, mapa)
        linha["produto_vendido"] = decodificar(d.get(PRODUTO_VENDIDO_KEY),
                                                PRODUTO_VENDIDO_KEY, mapa)
        # perfil do lead
        for nome, key in PERFIL_FIELDS:
            linha[nome] = decodificar(d.get(key), key, mapa)
        # pessoa / organizacao
        linha["pessoa"] = decodificar(d.get("person_id"), "person_id", mapa)
        linha["organizacao"] = decodificar(d.get("org_id"), "org_id", mapa)

        marca = "OK" if linha["etiqueta_matheus"] == "SIM" else "(sem etiqueta Matheus)"
        print(f"  deal/{did}: {linha['titulo'][:40]:<40} "
              f"[{linha['status']}] {marca}")
        linhas.append(linha)
        time.sleep(PAUSA)

    # ordem das colunas
    cols = ["deal_id", "titulo", "status", "valor", "etiqueta_matheus"]
    cols += [n for n, _ in DATA_FIELDS]
    cols += ["produto_apresentado", "produto_vendido"]
    cols += [n for n, _ in PERFIL_FIELDS]
    cols += ["pessoa", "organizacao"]

    with open("leadA_matheus.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for l in linhas:
            w.writerow(l)
    with open("leadA_matheus.json", "w", encoding="utf-8") as f:
        json.dump(linhas, f, ensure_ascii=False, indent=2)

    achou = sum(1 for l in linhas if "erro" not in l)
    com_etq = sum(1 for l in linhas if l.get("etiqueta_matheus") == "SIM")
    print("-" * 64)
    print(f"Deals encontrados: {achou}/{len(targets)}")
    print(f"Com etiqueta Matheus Medeiros: {com_etq}")
    print("Arquivos: leadA_matheus.csv  |  leadA_matheus.json")


if __name__ == "__main__":
    main()
