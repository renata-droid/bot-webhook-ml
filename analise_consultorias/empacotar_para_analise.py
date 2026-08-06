#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
 EMPACOTADOR PARA ANALISE  -  consultorias (Claude)
==============================================================================

PARA QUE SERVE
--------------
Voce ja tem os dois scripts que fazem o trabalho pesado:
  - transcrever_consultorias.py  -> gera .txt/.json de cada encontro,
                                     DENTRO da pasta de cada cliente
  - pipedrive_consultorias.py    -> gera _pipedrive/consultorias_negocios.json
                                     (CRM ja traduzido: jornada, notas, etc.)

O problema: as transcricoes ficam MISTURADAS com os videos (pesados). Se voce
zipar a pasta "transcricoes" inteira, vao junto varios GB de video.

Este script resolve isso. Ele varre tudo e monta um pacote LEVE contendo:
  - so os .txt e .json das transcricoes (nunca os videos), por cliente
  - o consultorias_negocios.json (CRM de todos)
  - o consultorias_resumo.txt (se existir)
  - um indice (_INDICE.txt) com clientes, nº de encontros e palavras
E fecha tudo num unico arquivo:  _para_analise.zip

Esse zip e o que voce sobe aqui no chat pra eu fazer:
  1) um dossie individual de cada aluno (igual ao do Limendes)
  2) uma analise geral cruzando todos

COMO USAR
---------
1) Confira PASTA_BASE abaixo (mesmo caminho dos outros scripts).
2) Rode:  python empacotar_para_analise.py
3) Suba o arquivo  _para_analise.zip  aqui no chat.

Sem dependencias externas: usa so a biblioteca padrao do Python.
==============================================================================
"""

import json
import shutil
import zipfile
from pathlib import Path

# =============================================================================
# CONFIGURACAO  (ajuste so isto, se precisar)
# =============================================================================
# Mesma pasta raiz usada nos outros scripts.
PASTA_BASE = Path(r"C:\Users\marke\Desktop\projetos\transcricao_consultorias")

# Onde estao as subpastas dos clientes (com os videos + transcricoes).
# No transcrever_consultorias.py isto e  PASTA_BASE / "transcricoes".
PASTA_VIDEOS = PASTA_BASE / "transcricoes"

# Onde o pipedrive_consultorias.py salvou o CRM.
PASTA_PIPEDRIVE = PASTA_BASE / "_pipedrive"

# Pasta/zip de saida.
PASTA_SAIDA = PASTA_BASE / "_para_analise"
ZIP_SAIDA = PASTA_BASE / "_para_analise.zip"

# So estas extensoes de transcricao entram no pacote (NUNCA video).
EXT_TRANSCRICAO = {".txt", ".json"}

# Extensoes de video/audio -> sempre ignoradas (seguranca extra).
EXT_MIDIA = {".mp4", ".m4a", ".mkv", ".mov", ".avi", ".webm", ".mp3", ".wav"}

# Subpastas que nao sao encontros (prints de metricas etc.) -> ignoradas.
IGNORAR_SUBPASTAS = {"metricas", "_transcricoes", "txt"}


# =============================================================================
# (nao precisa mexer daqui pra baixo)
# =============================================================================
def contar_palavras_json(caminho_json):
    """Le n_palavras de um .json de transcricao; volta 0 se nao der."""
    try:
        d = json.loads(Path(caminho_json).read_text(encoding="utf-8"))
        if isinstance(d, dict) and "n_palavras" in d:
            return int(d.get("n_palavras") or 0)
        texto = d.get("texto_completo", "") if isinstance(d, dict) else ""
        return len(texto.split())
    except Exception:
        return 0


def coletar_transcricoes():
    """
    Retorna dict:
      { cliente: [lista de Paths de .txt/.json], ... }
    varrendo PASTA_VIDEOS/<cliente>/, ignorando midia e subpastas ignoradas.
    """
    clientes = {}
    if not PASTA_VIDEOS.exists():
        return clientes

    for sub in sorted(PASTA_VIDEOS.iterdir()):
        if not sub.is_dir() or sub.name.startswith("_"):
            continue
        if sub.name.lower() in IGNORAR_SUBPASTAS:
            continue

        arquivos = []
        # rglob para pegar transcricoes mesmo se houver subnivel, mas
        # pulando qualquer coisa dentro de subpastas ignoradas / de midia.
        for arq in sorted(sub.rglob("*")):
            if not arq.is_file():
                continue
            partes_baixo = {p.lower() for p in arq.relative_to(sub).parts[:-1]}
            if partes_baixo & IGNORAR_SUBPASTAS:
                continue
            ext = arq.suffix.lower()
            if ext in EXT_MIDIA:
                continue
            if ext in EXT_TRANSCRICAO:
                arquivos.append(arq)

        if arquivos:
            clientes[sub.name] = arquivos
    return clientes


def main():
    print("=" * 70)
    print(" EMPACOTADOR PARA ANALISE - consultorias")
    print("=" * 70)

    if not PASTA_VIDEOS.exists():
        print(f"!! Nao achei a pasta de clientes: {PASTA_VIDEOS}")
        print("   Confira PASTA_BASE / PASTA_VIDEOS no topo do script.")
        return

    # limpa saida anterior
    if PASTA_SAIDA.exists():
        shutil.rmtree(PASTA_SAIDA)
    PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

    clientes = coletar_transcricoes()
    if not clientes:
        print(f"!! Nenhuma transcricao (.txt/.json) encontrada em {PASTA_VIDEOS}")
        print("   Rode primeiro o transcrever_consultorias.py.")
        return

    # copia transcricoes por cliente
    linhas_indice = []
    total_encontros = total_palavras = 0
    for cliente, arquivos in clientes.items():
        destino = PASTA_SAIDA / "transcricoes" / cliente
        destino.mkdir(parents=True, exist_ok=True)

        n_txt = n_json = palavras = 0
        for arq in arquivos:
            shutil.copy2(arq, destino / arq.name)
            if arq.suffix.lower() == ".txt":
                n_txt += 1
            elif arq.suffix.lower() == ".json":
                n_json += 1
                palavras += contar_palavras_json(arq)

        # nº de encontros = nº de .json (1 por video). Se so houver .txt, usa txt.
        encontros = n_json if n_json else n_txt
        total_encontros += encontros
        total_palavras += palavras
        linhas_indice.append((cliente, encontros, palavras))
        print(f"  + {cliente:40s} {encontros:3d} encontros  ~{palavras:>7d} palavras")

    # copia os arquivos do Pipedrive (CRM)
    crm_ok = False
    for nome in ("consultorias_negocios.json", "consultorias_resumo.txt"):
        origem = PASTA_PIPEDRIVE / nome
        if origem.exists():
            shutil.copy2(origem, PASTA_SAIDA / nome)
            crm_ok = crm_ok or nome.endswith(".json")
            print(f"  + CRM: {nome}")
    if not crm_ok:
        print("  !! AVISO: nao achei consultorias_negocios.json em", PASTA_PIPEDRIVE)
        print("     (rode o pipedrive_consultorias.py; sem ele o dossie fica so")
        print("      com a parte qualitativa das transcricoes, sem faturamento.)")

    # escreve indice
    indice = PASTA_SAIDA / "_INDICE.txt"
    with open(indice, "w", encoding="utf-8") as f:
        f.write("INDICE DO PACOTE PARA ANALISE\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Clientes .......... {len(clientes)}\n")
        f.write(f"Encontros total ... {total_encontros}\n")
        f.write(f"Palavras total .... ~{total_palavras}\n")
        f.write(f"CRM incluido ...... {'sim' if crm_ok else 'NAO'}\n\n")
        f.write(f"{'CLIENTE':40s} {'ENCONTROS':>10s} {'PALAVRAS':>12s}\n")
        f.write("-" * 64 + "\n")
        for cliente, enc, pal in sorted(linhas_indice):
            f.write(f"{cliente:40s} {enc:>10d} {pal:>12d}\n")

    # zipa tudo
    if ZIP_SAIDA.exists():
        ZIP_SAIDA.unlink()
    with zipfile.ZipFile(ZIP_SAIDA, "w", zipfile.ZIP_DEFLATED) as z:
        for arq in sorted(PASTA_SAIDA.rglob("*")):
            if arq.is_file():
                z.write(arq, arq.relative_to(PASTA_SAIDA))

    tam_mb = ZIP_SAIDA.stat().st_size / (1024 * 1024)
    print("-" * 70)
    print(f" OK! Pacote pronto: {ZIP_SAIDA}")
    print(f"     {len(clientes)} clientes | {total_encontros} encontros | ~{total_palavras} palavras")
    print(f"     Tamanho: {tam_mb:.1f} MB   (sem videos)")
    print("-" * 70)
    print(" >> Suba o arquivo _para_analise.zip no chat com o Claude.")
    print("    Ele fara: 1 dossie por aluno + 1 analise geral de todos.")


if __name__ == "__main__":
    main()
