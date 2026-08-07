#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
 GERADOR AUTOMÁTICO DE ANÁLISE DE CALL (.docx)  — modelo "deu certo/deu errado"
==============================================================================
Você NÃO precisa mais me mandar a transcrição. Este script:
  1) lê a transcrição da call (.txt gerada no Colab)
  2) lê o CRM do Pipedrive (calls_deals.json, saída do pipedrive_calls.py)
  3) lê o talk-ratio (opcional, _talkratio/<arquivo>.json)
  4) manda tudo pro Claude (API) no escopo EXATO acordado
  5) gera  Analise_Call_<nome>.docx  no mesmo layout do Andrea

DETECTA sozinho VENDEU / NÃO VENDEU pelo Status do deal no Pipedrive e ajusta
os títulos ("o que deu certo" x "o que deu errado"). O anexo de rubrica é fixo.

------------------------------------------------------------------------------
PRÉ-REQUISITOS
------------------------------------------------------------------------------
  pip install anthropic python-docx
  Definir a chave da API (paga):
      Windows:  setx ANTHROPIC_API_KEY "sk-ant-..."   (reabrir o terminal)
      Linux/Mac: export ANTHROPIC_API_KEY="sk-ant-..."

USO
------------------------------------------------------------------------------
  python gerar_analise_call.py "caminho/da/transcricao.txt"

  Opções:
    --crm         caminho do calls_deals.json      (padrão: _pipedrive/calls_deals.json)
    --talkratio   pasta com os *.json de talk-ratio (padrão: _talkratio)
    --deal-id     força um deal específico do CRM (senão casa pelo código da call)
    --saida       caminho do .docx de saída
==============================================================================
"""
import os, sys, re, json, argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gerar_docx import Dossie   # mesma pasta

MODELO = "claude-opus-5"

# ---------------------------------------------------------------------------
# 1) SCHEMA da análise (o que o Claude devolve)  — reflete o layout do Andrea
# ---------------------------------------------------------------------------
SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "desfecho", "kpi_desfecho_legenda", "kpi_nota", "kpi_nota_legenda",
        "kpi_fidelidade", "kpi_fidelidade_legenda", "ficha", "resumo_executivo",
        "o_que_intro", "o_que_itens", "por_que", "bonus", "valor", "objecoes",
        "tempo_ritmo", "talk_ratio_texto", "notas_criterios", "aderencia",
        "aderencia_resumo", "momento_virada", "fidelidade_tabela",
        "fidelidade_veredito", "licoes",
    ],
    "properties": {
        "desfecho": {"type": "string", "enum": ["VENDEU", "NÃO VENDEU", "EM ABERTO"],
                     "description": "Desfecho da call segundo o Pipedrive."},
        "kpi_desfecho_legenda": {"type": "string", "description": "Ex.: 'R$ 15.997 (confirmado no Pipedrive)'."},
        "kpi_nota": {"type": "string", "description": "Nota média da call, ex.: '8,7 / 10'."},
        "kpi_nota_legenda": {"type": "string"},
        "kpi_fidelidade": {"type": "string", "description": "Alta / Média / Baixa."},
        "kpi_fidelidade_legenda": {"type": "string"},
        "ficha": {"type": "array", "description": "Ficha técnica: pares [Campo, Informação].",
                  "items": {"type": "array", "items": {"type": "string"}, "minItems": 2, "maxItems": 2}},
        "resumo_executivo": {"type": "string"},
        "o_que_intro": {"type": "string", "description": "Frase de abertura da seção 1."},
        "o_que_itens": {"type": "array", "description": "Blocos da seção 1: cada um tem um título e bullets.",
                        "items": {"type": "object", "additionalProperties": False,
                                  "required": ["titulo", "bullets"],
                                  "properties": {"titulo": {"type": "string"},
                                                 "bullets": {"type": "array", "items": {"type": "string"}}}}},
        "por_que": {"type": "string"},
        "bonus": {"type": "string"},
        "valor": {"type": "string"},
        "objecoes": {"type": "array", "items": {"type": "string"}},
        "tempo_ritmo": {"type": "string"},
        "talk_ratio_texto": {"type": "string", "description": "Parágrafo do talk-ratio (usar o dado real se houver)."},
        "notas_criterios": {"type": "array",
                            "description": "Linhas [Critério, Nota, Observação]. Inclua a última linha MÉDIA.",
                            "items": {"type": "array", "items": {"type": "string"}, "minItems": 3, "maxItems": 3}},
        "aderencia": {"type": "array",
                      "description": "11 linhas [Etapa, Item, ✅/❌].",
                      "items": {"type": "array", "items": {"type": "string"}, "minItems": 3, "maxItems": 3}},
        "aderencia_resumo": {"type": "string"},
        "momento_virada": {"type": "array", "items": {"type": "string"},
                           "description": "1 a 2 parágrafos do momento decisivo (com timestamp)."},
        "fidelidade_tabela": {"type": "array",
                             "description": "Linhas [Ponto, Qualificação (SDR), Na call, Bate?].",
                             "items": {"type": "array", "items": {"type": "string"}, "minItems": 4, "maxItems": 4}},
        "fidelidade_veredito": {"type": "string"},
        "licoes": {"type": "array", "items": {"type": "string"}},
    },
}

SYSTEM = """Você é analista sênior de vendas da ICOMM / TF Treinamentos. Analisa \
UMA call de vendas (closer x lead) cruzando a TRANSCRIÇÃO real com o CRM (Pipedrive), \
no modelo "deu certo / deu errado" — NÃO é o modelo de análise geral.

Regras invioláveis:
- Baseie-se APENAS na transcrição e no CRM fornecidos. NÃO invente números, datas, \
nomes ou fatos. Se um dado não estiver na transcrição nem no CRM, escreva \
"não preenchido no Pipedrive" (para campos de CRM ausentes) ou "não identificado na call".
- O desfecho (VENDEU / NÃO VENDEU) é DADO pelo Status do deal no Pipedrive — respeite-o.
- Cite falas reais entre aspas quando sustentar um ponto (rapport, descoberta, objeção, virada).
- Timestamps: use os que aparecem na transcrição (formato [mm:ss] ou [h:mm:ss]).
- Notas de 0 a 10 por critério seguindo a régua: 10 = impecável e conduzido com maestria; \
7-8 = fez o essencial bem com 1 lacuna; 5-6 = pela metade/superficial; 0-4 = não fez/errado. \
A linha final de notas_criterios deve ser ["MÉDIA", "<média>", "<comentário curto>"].
- aderencia = os 11 itens do playbook, nesta ordem exata de Etapa/Item, marcando ✅ ou ❌:
    Abertura/Rapport - quebra-gelo; Abertura/Definição de agenda da call;
    Descoberta/Diagnóstico da dor antes da solução; Descoberta/Levantou números (fat., ADS/TACOS, margem);
    Descoberta/Dor quantificada (custo de não resolver); Valor/Prova social por nicho;
    Valor/Ancoragem de valor (resultado, não preço); Valor/Conectou solução → dor específica;
    Fechamento/Contorno de objeção; Fechamento/Pedido de fechamento claro;
    Fechamento/Próximo passo datado.
- fidelidade_tabela: compare o que o SDR registrou na qualificação (notas/atividades do CRM) \
com o que apareceu na call, ponto a ponto, marcando ✅ / ⚠️ / ❌. Se não houver dados do SDR, \
diga isso no veredito.
- talk_ratio_texto: se vier um talk-ratio REAL (diarização), use o número; senão, dê uma \
estimativa por leitura e diga explicitamente que é estimativa.
- Português do Brasil, tom objetivo e executivo, sem firulas.

Devolva SOMENTE um objeto JSON válido no schema pedido — nada antes nem depois."""


def carregar_crm(caminho):
    if not caminho or not Path(caminho).exists():
        return []
    try:
        data = json.loads(Path(caminho).read_text(encoding="utf-8"))
        return data if isinstance(data, list) else [data]
    except Exception as e:
        print(f"  (aviso: não consegui ler o CRM: {e})")
        return []


def casar_deal(deals, transcricao_nome, deal_id=None):
    """Escolhe o deal do CRM que corresponde a esta call."""
    if deal_id:
        for d in deals:
            if str(d.get("deal_id")) == str(deal_id):
                return d
    stem = Path(transcricao_nome).stem.lower()
    codigo = stem.split(" ")[0].split("(")[0].strip()   # ex.: 'apa-ydje-tnu'
    for d in deals:
        cc = str(d.get("codigo_call") or "").strip().lower()
        if cc and (cc in stem or codigo and codigo in cc):
            return d
    if len(deals) == 1:
        return deals[0]
    return None


def carregar_talkratio(pasta, transcricao_nome):
    if not pasta:
        return None
    p = Path(pasta)
    if not p.exists():
        return None
    stem = Path(transcricao_nome).stem
    alvo = p / (stem + ".json")
    if alvo.exists():
        try:
            return json.loads(alvo.read_text(encoding="utf-8"))
        except Exception:
            return None
    # tenta casar por prefixo (código da call)
    codigo = stem.split(" ")[0]
    for j in p.glob("*.json"):
        if j.stem.startswith(codigo):
            try:
                return json.loads(j.read_text(encoding="utf-8"))
            except Exception:
                pass
    return None


def status_para_desfecho(deal):
    s = (deal or {}).get("Status", "")
    if s == "Ganho":
        return "VENDEU"
    if s == "Perdido":
        return "NÃO VENDEU"
    return "EM ABERTO"


def chamar_claude(transcricao, deal, talkratio, desfecho):
    try:
        import anthropic
    except ImportError:
        print("!! Falta a lib: pip install anthropic"); sys.exit(1)
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("!! Defina a variável ANTHROPIC_API_KEY (chave da API paga)."); sys.exit(1)

    client = anthropic.Anthropic()

    partes = []
    partes.append(f"### DESFECHO (do Pipedrive): {desfecho}\n")
    partes.append("### CRM (PIPEDRIVE) — deal, campos, notas e atividades do SDR/closer:\n"
                  + json.dumps(deal or {}, ensure_ascii=False, indent=1))
    if talkratio:
        partes.append("### TALK-RATIO REAL (diarização):\n" + json.dumps(talkratio, ensure_ascii=False))
    else:
        partes.append("### TALK-RATIO: não fornecido — estime por leitura e diga que é estimativa.")
    partes.append("### TRANSCRIÇÃO DA CALL:\n" + transcricao)
    partes.append(
        "\nGere a análise no schema JSON pedido. Ajuste os títulos ao desfecho "
        "(se VENDEU, foque no que deu certo; se NÃO VENDEU, no que deu errado / travou). "
        "Se um campo do CRM estiver vazio, escreva exatamente 'não preenchido no Pipedrive'."
    )
    user = "\n\n".join(partes)

    # streaming (input pode ser longo) + thinking adaptativo
    print(f"  Chamando {MODELO} ...", flush=True)
    with client.messages.stream(
        model=MODELO,
        max_tokens=16000,
        thinking={"type": "adaptive"},
        system=SYSTEM + "\n\nSchema esperado:\n" + json.dumps(SCHEMA, ensure_ascii=False),
        messages=[{"role": "user", "content": user}],
    ) as stream:
        final = stream.get_final_message()

    texto = "".join(b.text for b in final.content if getattr(b, "type", "") == "text").strip()
    # extrai o objeto JSON (do primeiro { ao último })
    i, j = texto.find("{"), texto.rfind("}")
    if i == -1 or j == -1:
        print("!! O modelo não devolveu JSON. Resposta:\n", texto[:800]); sys.exit(1)
    try:
        return json.loads(texto[i:j + 1])
    except json.JSONDecodeError as e:
        print(f"!! JSON inválido do modelo: {e}\n", texto[i:i + 800]); sys.exit(1)


# ---------------------------------------------------------------------------
# 2) RENDER — monta o .docx no layout do Andrea
# ---------------------------------------------------------------------------
def render(a, nome_lead, saida):
    venceu = a.get("desfecho") == "VENDEU"
    perdeu = a.get("desfecho") == "NÃO VENDEU"
    palavra = "DEU CERTO" if venceu else ("DEU ERRADO" if perdeu else "EM ABERTO")

    d = Dossie(f"Análise de Call — Reunião que {palavra}",
               "Closer Renato Benedetti · Projeto Análise de Closers")

    kpi_desfecho = "✓ VENDEU" if venceu else ("✗ NÃO VENDEU" if perdeu else "• EM ABERTO")
    d.kpis([
        ("Desfecho", kpi_desfecho, a.get("kpi_desfecho_legenda", "")),
        ("Nota da call", a.get("kpi_nota", ""), a.get("kpi_nota_legenda", "")),
        ("Fidelidade SDR", a.get("kpi_fidelidade", ""), a.get("kpi_fidelidade_legenda", "")),
    ])

    d.tabela(["Campo", "Informação"], a.get("ficha", []))

    d.h1("Resumo executivo")
    d.p(a.get("resumo_executivo", ""))

    t1 = "1. O que deu certo" if venceu else ("1. O que deu errado" if perdeu else "1. Pontos da call")
    d.h1(t1)
    if a.get("o_que_intro"):
        d.p(a["o_que_intro"])
    for bloco in a.get("o_que_itens", []):
        if bloco.get("titulo"):
            d.p(bloco["titulo"])
        for b in bloco.get("bullets", []):
            d.bullet(b)

    t2 = "2. Por que essa deu certo" if venceu else ("2. Por que essa deu errado / travou" if perdeu else "2. Leitura da call")
    d.h1(t2)
    d.p(a.get("por_que", ""))

    d.h1("3. Usou bônus como quebra de objeção?")
    d.p(a.get("bonus", ""))

    d.h1("4. Fez o lead entender o valor? (preço deixou de ser impeditivo?)")
    d.p(a.get("valor", ""))

    d.h1("5. Maiores objeções do cliente")
    for o in a.get("objecoes", []):
        d.bullet(o)

    d.h1("6. Tempo e ritmo")
    d.p(a.get("tempo_ritmo", ""))
    if a.get("talk_ratio_texto"):
        d.p(a["talk_ratio_texto"], italico=True)

    d.h1("⭐ Nota da call (0–10) por critério")
    d.tabela(["Critério", "Nota", "Observação"], a.get("notas_criterios", []))

    d.h1("✅ Aderência ao playbook de vendas")
    d.tabela(["Etapa", "Item", "✓"], a.get("aderencia", []))
    if a.get("aderencia_resumo"):
        d.p(a["aderencia_resumo"], italico=True)

    t_virada = "🎯 Momento da virada" if venceu else ("🎯 Momento em que travou" if perdeu else "🎯 Momento-chave")
    d.h1(t_virada)
    for par in a.get("momento_virada", []):
        d.p(par)

    d.h1("🔗 Fidelidade SDR → Closer")
    d.tabela(["Ponto", "Qualificação (SDR)", "Na call", "Bate?"], a.get("fidelidade_tabela", []))
    if a.get("fidelidade_veredito"):
        d.p(a["fidelidade_veredito"], italico=True)

    t_licao = "Lição para replicar" if venceu else ("O que corrigir na próxima" if perdeu else "Pontos de atenção")
    d.h1(t_licao)
    for l in a.get("licoes", []):
        d.bullet(l)

    # ---- Anexo de rubrica (FIXO, igual em toda análise) ----
    d.h1("Anexo — Como as notas são calculadas (0 a 10)")
    d.p("Regra de ouro: 10 é \"impecável + conduziu com maestria\", não apenas \"fez\". Fez bem, com 1 "
        "detalhe faltando, fica 8–9.")
    d.tabela(["Faixa", "Significado"], [
        ["9 – 10  Excelente", "Fez tudo e conduziu com maestria, sem falha"],
        ["7 – 8  Bom", "Fez o essencial bem, com 1 lacuna pequena"],
        ["5 – 6  Regular", "Fez pela metade / de forma superficial"],
        ["0 – 4  Fraco", "Não fez, ou fez de forma errada"],
    ])
    d.tabela(["Critério", "O que exige o 10", "Cai para 7–8 quando"], [
        ["Rapport / abertura", "Cria o vínculo ativamente (pessoal + propósito) e define agenda", "Conecta só pelo profissional, ou quem puxa é o lead"],
        ["Descoberta / diagnóstico", "Puxa a dor antes da solução, levanta números E amplia a dor", "Boa descoberta, mas não amplia/reenquadra a dor"],
        ["Prova social", "Case do mesmo nicho + número + \"esse seria você\"", "Prova social genérica, sem ser da categoria"],
        ["Ancoragem de valor", "Preço vira escolha de pagamento; usa custo de oportunidade", "Vende resultado, mas não quantifica o valor"],
        ["Contorno de objeção", "Antecipa, contorna E confirma que a objeção caiu", "Contorna, mas reativo ou faltou um recurso (ex.: bônus)"],
        ["Fechamento / próximo passo", "Pede a venda E executa o próximo passo na call", "Fecha, mas o próximo passo fica só \"prometido\""],
    ])
    d.p("")
    d.p("Análise a fundo de call individual, no cruzamento call (fala real) ↔ Pipedrive. "
        "Complementa o compilado de reuniões e o Dossiê Executivo do closer.", italico=True)

    return d.salvar(saida)


def main():
    ap = argparse.ArgumentParser(description="Gera a análise .docx de uma call de vendas.")
    ap.add_argument("transcricao", help="caminho do .txt da transcrição (saída do Colab)")
    ap.add_argument("--crm", default=None, help="calls_deals.json (padrão: _pipedrive/calls_deals.json)")
    ap.add_argument("--talkratio", default=None, help="pasta com os *.json de talk-ratio (padrão: _talkratio)")
    ap.add_argument("--deal-id", default=None, help="força um deal específico do CRM")
    ap.add_argument("--saida", default=None, help="caminho do .docx de saída")
    args = ap.parse_args()

    tpath = Path(args.transcricao)
    if not tpath.exists():
        print("!! Transcrição não encontrada:", tpath); sys.exit(1)
    transcricao = tpath.read_text(encoding="utf-8", errors="ignore")
    base = tpath.resolve().parent

    crm_path = args.crm or (base / "_pipedrive" / "calls_deals.json")
    if not Path(crm_path).exists():
        # tenta na pasta do script
        alt = Path(__file__).resolve().parent / "_pipedrive" / "calls_deals.json"
        crm_path = alt if alt.exists() else crm_path
    deals = carregar_crm(crm_path)

    tr_pasta = args.talkratio or (base / "_talkratio")
    talkratio = carregar_talkratio(tr_pasta, tpath.name)

    deal = casar_deal(deals, tpath.name, args.deal_id)
    if deal:
        print(f"  CRM casado: deal {deal.get('deal_id')} | {deal.get('Titulo','')} | {deal.get('Status','')}")
    else:
        print("  (aviso: nenhum deal do CRM casou com esta call — seguindo só com a transcrição)")
    desfecho = status_para_desfecho(deal)

    analise = chamar_claude(transcricao, deal, talkratio, desfecho)

    # nome do lead p/ o arquivo
    nome_lead = ""
    if deal:
        nome_lead = deal.get("Pessoa") or deal.get("Organizacao") or ""
    if not nome_lead:
        nome_lead = tpath.stem.split(" ")[0]
    slug = re.sub(r"[^A-Za-z0-9]+", "_", str(nome_lead)).strip("_") or "call"

    saida = args.saida or str(base / f"Analise_Call_Renato_{slug}.docx")
    caminho = render(analise, nome_lead, saida)
    print("OK:", caminho)


if __name__ == "__main__":
    main()
