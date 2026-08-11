#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
 LEAD E do pipe  x  DECK V5   (01/01/2026 -> 10/08/2026)
==============================================================================

Puxa todos os negocios marcados como Lead = E (campo Lead) criados no periodo
e RECLASSIFICA pela regra oficial do deck V5. O objetivo e achar os "falsos E":
leads marcados como E (descartados) que, pela regra, seriam MQL (A, B, C ou D)
-> ou seja, lead bom que foi jogado fora.

Saida:
  leadE_x_deck.csv   1 linha por lead E, com deck_grade e bate_E (SIM/NAO)

COMO USAR
---------
    python pipedrive_leadE_deck.py        (token ja embutido; revogue depois)
==============================================================================
"""
import os, csv, time
from collections import Counter

import requests

# =============================================================================
# CONFIG
# =============================================================================
TOKEN = os.environ.get("PIPEDRIVE_TOKEN", "5497d52719432ce49d0ad281cb71108be7212129").strip()
COMPANY_DOMAIN = os.environ.get("PIPEDRIVE_DOMAIN", "").strip()

PERIODO_INI = "2026-01-01"
PERIODO_FIM = "2026-08-10"          # ate ontem
DATA_FILTRO = "add_time"            # filtra por "Negocio criado em"

K_LEAD      = "1cb9ad4729d5f241f8a329045613582070ee2c95"   # campo Lead
LEAD_E_OPT  = "221"                                          # opcao "E"
K_ESTADO    = "cbef5dcdc3dcb5fd20bb243a6f4291093cea5ed7"
K_CARGO     = "2c0d5e90bfdb3ced22e92a136f329b576d2ab2d9"
K_FAT_MKT   = "e5310680e97128cdd6fd135118b1c277f0538e21"
K_FAT_FIS   = "e4b95213fed643447308e95399bbff05a7d31d87"
K_ONDE      = "d166e9a3c962c7dcbf849b78100083ca42323505"
K_PROD_APR  = "810aeffbcd6e447f89e9b82d1a977738a10f2f86"
K_VENDEDOR  = "db2c9632937b836eae914bb3749d19f3b129b31d"
PAUSA = 0.2

# ---- matrizes do deck V5 (estado valido) ----
_MKT = {"S": {1: "D", 2: "B", 3: "B", 4: "A", 5: "A", 6: "A", 7: "A", 8: "A"},
        "G": {1: "E", 2: "D", 3: "B", 4: "B", 5: "B", 6: "B", 7: "B", 8: "D"}}
_FIS = {"S": {1: "E", 2: "D", 3: "D", 4: "C", 5: "C", 6: "C", 7: "C", 8: "C"},
        "G": {1: "E", 2: "E", 3: "E", 4: "E", 5: "E", 6: "E", 7: "D", 8: "D"}}
_ESTADOS_VAL = {"são paulo", "minas gerais", "paraná", "rio grande do sul",
                "santa catarina", "distrito federal", "rio de janeiro"}
_CARGO_S = {"sócio ou fundador", "diretor"}
_CARGO_G = {"gerente", "coordenador"}


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


def _tier(v):
    if not v:
        return None
    v = v.lower()
    if "ainda não" in v or "não temos" in v or "não vendemos" in v:
        return None
    if "acima de r$ 5" in v: return 8
    if "1 milhão a r$ 5" in v: return 7
    if "500.000 a r$ 1" in v: return 6
    if "300.000 a r$ 500" in v: return 5
    if "100.000 a r$ 300" in v: return 4
    if "60.000 a r$ 100" in v: return 3
    if ("15.000 a r$ 40" in v or "40.000 a r$ 60" in v
            or "15.000 a r$ 60" in v or "0 a r$ 60" in v): return 2
    if "0 a r$ 5.000" in v or "5.000 a r$ 15" in v or "0 a r$ 15" in v: return 1
    return None


def classificar_deck(cargo, estado, fat_mkt, fat_fis):
    c = (cargo or "").lower()
    grupo = "S" if c in _CARGO_S else ("G" if c in _CARGO_G else None)
    if grupo is None:
        return "E", "cargo <= Supervisor"
    if (estado or "").lower() not in _ESTADOS_VAL:
        return "E", "estado nao valido"
    tm, tf = _tier(fat_mkt), _tier(fat_fis)
    if tm is None and tf is None:
        return "F", "nao vende em nenhum canal"
    g_mkt = _MKT[grupo][tm] if tm else None
    g_fis = _FIS[grupo][tf] if tf else None
    grade = g_mkt or g_fis
    det = (f"mkt=tier{tm}->{g_mkt}" if tm else "mkt=nao vende")
    det += (f" | fis=tier{tf}->{g_fis}" if tf else " | fis=nao vende")
    return grade, det


def no_periodo(d):
    return bool(d) and PERIODO_INI <= d[:10] <= PERIODO_FIM


def main():
    if not TOKEN:
        print("!! Defina PIPEDRIVE_TOKEN"); return
    print("Carregando campos/usuarios e puxando negocios...")
    mapa = carregar_mapa_opcoes()
    users = carregar_usuarios()
    deals = puxar_todos_deals()
    print(f"Total de negocios: {len(deals)}")

    E = [d for d in deals
         if str(d.get(K_LEAD)) == LEAD_E_OPT and no_periodo(d.get(DATA_FILTRO) or "")]
    print(f"Lead E no periodo {PERIODO_INI}..{PERIODO_FIM}: {len(E)}")

    linhas = []
    dist = Counter()
    for d in E:
        cargo = opt(d.get(K_CARGO), K_CARGO, mapa)
        estado = opt(d.get(K_ESTADO), K_ESTADO, mapa)
        fmkt = opt(d.get(K_FAT_MKT), K_FAT_MKT, mapa)
        ffis = opt(d.get(K_FAT_FIS), K_FAT_FIS, mapa)
        deck, det = classificar_deck(cargo, estado, fmkt, ffis)
        dist[deck] += 1
        closer = d.get(K_VENDEDOR)
        if isinstance(closer, dict):
            closer = closer.get("value") or closer.get("id")
        closer = users.get(closer, "") if closer else ""
        linhas.append({
            "deal_id": d.get("id"), "titulo": d.get("title", ""),
            "closer": closer, "status": d.get("status", ""),
            "criado_em": (d.get("add_time") or "")[:10],
            "estado": estado, "cargo": cargo,
            "fat_marketplaces": fmkt, "fat_fisico": ffis,
            "onde_vende": opt(d.get(K_ONDE), K_ONDE, mapa),
            "produto_apresentado": opt(d.get(K_PROD_APR), K_PROD_APR, mapa),
            "lead_pipe": "E", "deck_grade": deck,
            "bate_E": "SIM" if deck == "E" else "NAO",
            "deck_detalhe": det, "valor": d.get("value", ""),
        })

    linhas.sort(key=lambda x: ("ABCDEF".index(x["deck_grade"]) if x["deck_grade"] in "ABCDEF" else 9))
    cols = ["deal_id", "titulo", "closer", "status", "criado_em", "estado", "cargo",
            "fat_marketplaces", "fat_fisico", "onde_vende", "produto_apresentado",
            "lead_pipe", "deck_grade", "bate_E", "deck_detalhe", "valor"]
    with open("leadE_x_deck.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader(); w.writerows(linhas)

    mql = sum(dist[g] for g in "ABCD")
    print("-" * 60)
    print("Reclassificacao dos Lead E pelo deck:")
    for g in "ABCDEF":
        if dist[g]:
            print(f"  vira {g}: {dist[g]}")
    print("-" * 60)
    print(f"Bate E (E de verdade): {dist['E']}/{len(E)}")
    print(f"FALSOS E (eram MQL A-D, lead bom descartado): {mql}")
    print("Arquivo: leadE_x_deck.csv")


if __name__ == "__main__":
    main()
