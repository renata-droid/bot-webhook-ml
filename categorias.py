#!/usr/bin/env python3
"""
Despeja a árvore de categorias e subcategorias do Mercado Livre em CSV.

Endpoints usados (públicos, NÃO precisam de token):
    /sites/{site}/categories   -> categorias-raiz [{id, name}, ...]
    /categories/{id}           -> detalhe: path_from_root, children_categories
                                  (cada filha já vem com total_items_in_this_category)

Como você quer mapear onde estão os GRANDES sellers, o --min-itens evita
descer em subcategoria de nicho: só abre a filha se ela tiver volume relevante.
A contagem de itens da categoria é um bom proxy de "tem seller grande aqui".

Uso:
    python categorias.py                              # árvore toda, até nível 3
    python categorias.py --nivel-max 2                # só 2 níveis (mais rápido)
    python categorias.py --raiz MLB1051               # só a subárvore de Celulares
    python categorias.py --min-itens 5000 --saida categorias.csv
"""

import argparse
import csv
import sys
import time

import requests

API = "https://api.mercadolibre.com"
PAUSA = 0.3  # segundos entre chamadas — educado com a API


def get(path: str, tentativas: int = 4):
    url = f"{API}{path}"
    for i in range(tentativas):
        try:
            r = requests.get(url, headers={"accept": "application/json"}, timeout=20)
        except requests.RequestException as e:
            print(f"  ! rede: {e}", file=sys.stderr)
            time.sleep(2 ** i)
            continue
        if r.status_code == 200:
            return r.json()
        if r.status_code == 429:
            espera = 5 * (i + 1)
            print(f"  ! rate limit, aguardando {espera}s", file=sys.stderr)
            time.sleep(espera)
            continue
        print(f"  ! HTTP {r.status_code} em {path}: {r.text[:150]}", file=sys.stderr)
        return None
    return None


def raizes(site: str) -> list[dict]:
    data = get(f"/sites/{site}/categories")
    return data or []


def caminhar(cat_id: str, nome: str, nivel: int, nivel_max: int,
             min_itens: int, vistos: set, linhas: list) -> None:
    """
    Visita a categoria, registra a linha e desce nas filhas com volume >= min_itens.
    Uma chamada a /categories/{id} já devolve total desta + filhas com contagem.
    """
    if cat_id in vistos:
        return
    vistos.add(cat_id)

    det = get(f"/categories/{cat_id}")
    time.sleep(PAUSA)
    if not det:
        return

    filhas = det.get("children_categories") or []
    caminho = " > ".join(p["name"] for p in det.get("path_from_root", [])) or nome
    linhas.append({
        "id": cat_id,
        "nome": det.get("name") or nome,
        "nivel": nivel,
        "caminho": caminho,
        "total_itens": det.get("total_items_in_this_category"),
        "qtd_subcategorias": len(filhas),
        "folha": 0 if filhas else 1,
    })
    print(f"{'  ' * nivel}{cat_id:<12} {det.get('name','?'):<40} "
          f"{det.get('total_items_in_this_category') or 0:>10} itens")

    if nivel >= nivel_max:
        return

    # ordena filhas da maior pra menor: onde tem mais item, tende a ter seller grande
    filhas.sort(key=lambda c: c.get("total_items_in_this_category") or 0, reverse=True)
    for f in filhas:
        if (f.get("total_items_in_this_category") or 0) < min_itens:
            continue
        caminhar(f["id"], f.get("name", ""), nivel + 1,
                 nivel_max, min_itens, vistos, linhas)


def main() -> None:
    p = argparse.ArgumentParser(description="Mapa de categorias do Mercado Livre")
    p.add_argument("--site", default="MLB")
    p.add_argument("--raiz", help="começa de uma categoria específica (ex: MLB1051)")
    p.add_argument("--nivel-max", type=int, default=3, help="profundidade máxima")
    p.add_argument("--min-itens", type=int, default=0,
                   help="só desce em subcategoria com pelo menos N itens")
    p.add_argument("--saida", default="categorias.csv")
    a = p.parse_args()

    vistos: set = set()
    linhas: list = []

    if a.raiz:
        caminhar(a.raiz, a.raiz, 0, a.nivel_max, a.min_itens, vistos, linhas)
    else:
        roots = raizes(a.site)
        print(f"{len(roots)} categorias-raiz em {a.site}\n")
        for r in roots:
            caminhar(r["id"], r.get("name", ""), 0,
                     a.nivel_max, a.min_itens, vistos, linhas)

    if not linhas:
        print("nada coletado — confira o site/raiz")
        return

    with open(a.saida, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        w.writeheader()
        w.writerows(linhas)

    folhas = sum(1 for l in linhas if l["folha"])
    print(f"\n{len(linhas)} categorias em {a.saida} ({folhas} folhas)")
    print("\nTop 15 por volume de itens:")
    for l in sorted(linhas, key=lambda x: x["total_itens"] or 0, reverse=True)[:15]:
        print(f"  {l['id']:<12} {(l['total_itens'] or 0):>10}  {l['caminho']}")


if __name__ == "__main__":
    main()
