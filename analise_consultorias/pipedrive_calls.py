#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
 PIPEDRIVE - PUXAR DEALS DE CALLS (closers/SDRs)   [rodar no VSCode]
==============================================================================
Para cada deal_id do deals.csv, puxa do Pipedrive:
  - o negocio (todos os campos personalizados JA TRADUZIDOS)
  - pessoa de contato + organizacao
  - NOTAS (anotacoes do closer/SDR)
  - ATIVIDADES (ligacoes/reunioes/historico)
Salva em _pipedrive/calls_deals.json  (estruturado, eu leio isso)
       e _pipedrive/calls_resumo.txt   (legivel)

USO
---
1) Crie um .env nesta pasta com:
     PIPEDRIVE_DOMAIN=icommescola
     PIPEDRIVE_API_TOKEN=seu_token
2) Crie deals.csv com uma coluna "deal_id" (um por linha).
   (Opcional: coluna "slug" para rotular; e "codigo_call" para casar com a transcricao.)
3) python pipedrive_calls.py

Sem dependencias externas (so biblioteca padrao).
==============================================================================
"""
import os, csv, json, re, time
import urllib.parse, urllib.request
from pathlib import Path

PASTA = Path(__file__).resolve().parent

def carregar_env(p):
    env = {}
    f = p / ".env"
    if f.exists():
        for linha in f.read_text(encoding="utf-8").splitlines():
            linha = linha.strip()
            if linha and not linha.startswith("#") and "=" in linha:
                k, v = linha.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env

_ENV = carregar_env(PASTA)
TOKEN  = _ENV.get("PIPEDRIVE_API_TOKEN") or os.environ.get("PIPEDRIVE_API_TOKEN", "")
DOMAIN = (_ENV.get("PIPEDRIVE_DOMAIN") or os.environ.get("PIPEDRIVE_DOMAIN", "")).replace("https://","").replace(".pipedrive.com","").strip("/ ")

def base_url():
    return f"https://{DOMAIN}.pipedrive.com/api/v1" if DOMAIN else "https://api.pipedrive.com/v1"

def api_get(endpoint, params=None, tentativas=3):
    params = dict(params or {}); params["api_token"] = TOKEN
    url = f"{base_url()}/{endpoint}?" + urllib.parse.urlencode(params)
    for t in range(tentativas):
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            if t == tentativas - 1:
                print(f"    !! erro {endpoint}: {e}"); return {}
            time.sleep(1.5 * (t + 1))
    return {}

def limpar_html(txt):
    if not txt: return ""
    txt = re.sub(r"<br\s*/?>", "\n", str(txt))
    txt = re.sub(r"</p>", "\n", txt)
    txt = re.sub(r"<[^>]+>", "", txt)
    return txt.replace("&nbsp;", " ").replace("&amp;", "&").replace("&gt;", ">").replace("&lt;", "<").strip()

def status_pt(s): return {"won":"Ganho","lost":"Perdido","open":"Aberto"}.get(s, s)

def carregar_mapas():
    """key -> {option_id: label}  e  user_id -> nome."""
    opt = {}
    for f in (api_get("dealFields", {"limit": 500}).get("data") or []):
        if f.get("options"):
            opt[f["key"]] = {str(o["id"]): o["label"] for o in f["options"]}
    users = {str(u.get("id")): u.get("name") for u in (api_get("users").get("data") or [])}
    # nome amigavel de cada campo
    nomes = {f["key"]: f.get("name") for f in (api_get("dealFields", {"limit": 500}).get("data") or []) if f.get("key")}
    return opt, users, nomes

def traduzir(valor, key, opt, users):
    if valor in (None, "", []): return ""
    if key in opt:
        ids = [s.strip() for s in str(valor).split(",") if s.strip()]
        return ", ".join(opt[key].get(i, i) for i in ids)
    if isinstance(valor, dict):
        return valor.get("name") or valor.get("value") or ""
    sv = str(valor)
    return users.get(sv, valor)

def pega_notas(deal_id, users):
    out = []
    for n in (api_get("notes", {"deal_id": deal_id, "limit": 100, "sort": "add_time ASC"}).get("data") or []):
        out.append({"data": n.get("add_time"), "autor": users.get(str(n.get("user_id")), n.get("user_id")),
                    "texto": limpar_html(n.get("content"))})
    return out

def pega_atividades(deal_id, users):
    out = []
    for a in (api_get(f"deals/{deal_id}/activities", {"limit": 100}).get("data") or []):
        out.append({"data": a.get("due_date"), "hora": a.get("due_time"), "tipo": a.get("type"),
                    "assunto": a.get("subject"), "concluida": a.get("done"),
                    "nota": limpar_html(a.get("note")), "responsavel": users.get(str(a.get("user_id")), a.get("user_id"))})
    out.sort(key=lambda x: (str(x.get("data") or ""), str(x.get("hora") or "")))
    return out

def main():
    if not TOKEN:
        print("!! Sem token. Crie o .env com PIPEDRIVE_API_TOKEN e PIPEDRIVE_DOMAIN."); return
    print(f"Dominio: {DOMAIN or 'api.pipedrive.com'}")

    # le deals.csv
    csv_path = PASTA / "deals.csv"
    if not csv_path.exists():
        print("!! Crie um deals.csv com a coluna deal_id."); return
    deals = []
    with open(csv_path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            did = (row.get("deal_id") or "").strip()
            if did:
                deals.append({"deal_id": int(float(did)),
                              "slug": (row.get("slug") or "").strip(),
                              "codigo_call": (row.get("codigo_call") or "").strip()})
    if not deals:
        print("!! deals.csv vazio."); return
    print(f"Deals a puxar: {len(deals)}")

    opt, users, nomes = carregar_mapas()
    print(f"  (mapas: {len(opt)} campos c/ opcoes, {len(users)} usuarios)")

    destino = PASTA / "_pipedrive"; destino.mkdir(exist_ok=True)
    saida = []
    for item in deals:
        did = item["deal_id"]
        print(f"  -> deal {did} {item.get('slug') or ''} ...", flush=True)
        d = api_get(f"deals/{did}").get("data") or {}
        if not d:
            saida.append({**item, "ERRO": "deal nao encontrado"}); continue

        org = d.get("org_id"); person = d.get("person_id")
        reg = {
            "slug": item.get("slug"), "codigo_call": item.get("codigo_call"),
            "deal_id": d.get("id"), "Titulo": d.get("title"), "Status": status_pt(d.get("status")),
            "Valor": d.get("value"),
            "Organizacao": org.get("name") if isinstance(org, dict) else org,
            "Pessoa": person.get("name") if isinstance(person, dict) else person,
            "Dono": users.get(str((d.get("user_id") or {}).get("id") if isinstance(d.get("user_id"), dict) else d.get("user_id"))),
            "Criado em": d.get("add_time"), "Ganho em": d.get("won_time"), "Perdido em": d.get("lost_time"),
            "Motivo perda": d.get("lost_reason"),
        }
        # TODOS os campos personalizados (chave-hash) traduzidos p/ nome legivel
        campos = {}
        for key, val in d.items():
            if re.fullmatch(r"[0-9a-f]{40}", str(key)):  # campos custom tem chave hash de 40 chars
                nome = nomes.get(key, key)
                tv = traduzir(val, key, opt, users)
                if tv not in (None, "", []):
                    campos[nome] = tv
        reg["campos"] = campos
        reg["notas"] = pega_notas(did, users)
        reg["atividades"] = pega_atividades(did, users)
        saida.append(reg)
        time.sleep(0.2)

    json.dump(saida, open(destino / "calls_deals.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    with open(destino / "calls_resumo.txt", "w", encoding="utf-8") as f:
        for reg in saida:
            f.write("=" * 74 + "\n")
            f.write(f"{reg.get('slug') or ''} | deal {reg.get('deal_id')} | {reg.get('Titulo','')}\n")
            f.write("=" * 74 + "\n")
            for k in ["Status","Valor","Organizacao","Pessoa","Dono","Criado em","Ganho em","Perdido em","Motivo perda","codigo_call"]:
                if reg.get(k) not in (None, ""): f.write(f"  {k}: {reg[k]}\n")
            for k, v in (reg.get("campos") or {}).items():
                f.write(f"  {k}: {v}\n")
            nt = reg.get("notas") or []
            if nt:
                f.write(f"\n  NOTAS ({len(nt)}):\n")
                for n in nt[:40]:
                    f.write(f"    [{str(n.get('data'))[:16]}] {n.get('autor')}: {n.get('texto','')[:500]}\n")
            at = reg.get("atividades") or []
            if at:
                f.write(f"\n  ATIVIDADES ({len(at)}):\n")
                for a in at[:50]:
                    f.write(f"    [{str(a.get('data'))} {a.get('hora') or ''}] {a.get('tipo')}: {a.get('assunto','')} {('- '+a['nota'][:200]) if a.get('nota') else ''}\n")
            f.write("\n\n")

    print("-" * 64)
    print(f"OK. {len(saida)} deals salvos em {destino}")
    print("  - calls_deals.json   <<< me manda este")
    print("  - calls_resumo.txt")

if __name__ == "__main__":
    main()
