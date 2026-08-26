#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TRANSCRICAO LOCAL (so transcreve) — GPU NVIDIA, cai pra CPU sozinho.
A diarizacao (quem falou) e um passo SEPARADO -> rode 'diarizar.py' depois.

    pip install faster-whisper
    python transcrever_local.py

>>> Passe a data do dia na linha de comando (nao precisa editar o arquivo): <<<
    python transcrever_local.py 2026-08-25
Sem argumento, usa a data de hoje. (procura videos nas subpastas tambem)
Saida: subpasta "_transcricoes" (.txt + .json). Pula os que ja fez.
"""
import os, re, sys, json
from datetime import date
from pathlib import Path

# --- CONFIG ---
RAIZ   = Path(r"C:\Users\Renata\Desktop\projetos\transcricao_video_closers")
MODELO = "medium"             # "small" = + rapido | "large-v3" = + qualidade
IDIOMA = "pt"
EXTS   = (".mp4", ".mkv", ".mov", ".avi", ".m4a", ".mp3", ".wav", ".webm")

# dia = 1o argumento da linha de comando; sem argumento, hoje
DIA = sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat()
PASTA = Path(DIA) if Path(DIA).is_absolute() else RAIZ / DIA
if not PASTA.is_dir():
    sys.exit(f"Pasta nao encontrada: {PASTA}")


# registra os DLLs da NVIDIA (resolve cublas64_12.dll no Windows)
def _add_nvidia_dlls():
    import importlib.util, glob
    achados = []
    spec = importlib.util.find_spec("nvidia")
    if not spec or not spec.submodule_search_locations:
        return achados
    root = list(spec.submodule_search_locations)[0]
    for binpath in glob.glob(os.path.join(root, "*", "bin")):
        if os.path.isdir(binpath):
            try:
                os.add_dll_directory(binpath)
            except Exception:
                pass
            os.environ["PATH"] = binpath + os.pathsep + os.environ.get("PATH", "")
            achados.append(binpath)
    return achados

print(f"Pastas de DLL da NVIDIA registradas: {len(_add_nvidia_dlls())}")

from faster_whisper import WhisperModel

SAIDA = PASTA / "_transcricoes"
SAIDA.mkdir(parents=True, exist_ok=True)
RE_MEET = re.compile(r"([a-z]{3}-[a-z]{4}-[a-z]{3})")


def build(device):
    return WhisperModel(MODELO, device=device,
                        compute_type="float16" if device == "cuda" else "int8")

device = "cuda"
try:
    model = build("cuda"); print(f"Whisper '{MODELO}' — GPU")
except Exception as e:
    print("GPU indisponivel, CPU:", str(e)[:80]); device = "cpu"; model = build("cpu")


def transcrever(v):
    global device, model
    try:
        segs, info = model.transcribe(str(v), language=IDIOMA, vad_filter=True)
        return list(segs), info
    except Exception as e:
        if device == "cuda":
            print("  GPU falhou, indo pra CPU...", str(e)[:60])
            device = "cpu"; model = build("cpu")
            segs, info = model.transcribe(str(v), language=IDIOMA, vad_filter=True)
            return list(segs), info
        raise


# videos na PASTA e subpastas (Frizzo/, Nicolas/, ...), sem a saida _transcricoes
videos = [f for f in sorted(PASTA.rglob("*"))
          if f.suffix.lower() in EXTS and "_transcricoes" not in f.parts]
print(f"Videos em '{PASTA.name}' (com subpastas): {len(videos)}")

for i, v in enumerate(videos, 1):
    base = v.stem
    out_json = SAIDA / (base + ".json")
    if out_json.exists():
        print(f"  [{i}/{len(videos)}] pulando (ja feito): {base}"); continue
    print(f"  [{i}/{len(videos)}] transcrevendo: {v.name} ...", flush=True)
    segs, info = transcrever(v)
    segmentos = [{"ini": round(s.start, 2), "fim": round(s.end, 2),
                  "falante": "", "texto": s.text.strip()} for s in segs]
    texto = " ".join(s["texto"] for s in segmentos).strip()
    m = RE_MEET.search(v.name.lower())
    data = {
        "arquivo": v.name, "video_path": str(v), "codigo_meet": (m.group(1) if m else ""),
        "duracao_seg": round(info.duration, 1), "modelo": MODELO,
        "diarizado": False, "n_palavras": len(texto.split()),
        "segmentos": segmentos, "texto_completo": texto,
    }
    out_json.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    (SAIDA / (base + ".txt")).write_text(texto, encoding="utf-8")
    print(f"      OK ({device}) — {round(info.duration/60)} min, {len(texto.split())} palavras")

print(f"\nFIM (so transcricao). Agora rode: python diarizar.py")
