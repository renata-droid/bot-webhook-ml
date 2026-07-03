import os
import json
import unicodedata
import requests
from datetime import datetime
from flask import Flask, request
from auth import get_token

API_BASE = "https://api.mercadolibre.com"
SELLER_ID = 3231879246  # conta de TESTE (na Box Fan real: 1087616640)
FAMILIAS_FILE = "familias.json"
ESCALADAS_FILE = "perguntas_para_humano.json"

# Segurança: começa em simulação. Na nuvem, controla pela variável SIMULACAO.
SIMULACAO = os.environ.get("SIMULACAO", "true").lower() == "true"

app = Flask(__name__)


def normalizar(txt):
    txt = str(txt).lower()
    return "".join(c for c in unicodedata.normalize("NFD", txt)
                   if unicodedata.category(c) != "Mn")


with open(FAMILIAS_FILE, "r", encoding="utf-8") as f:
    GRUPO_POR_ITEM = json.load(f)

ESCALAR = [
    "faltando", "faltou", "veio errado", "veio quebrado", "quebrado", "quebrada",
    "quebraram", "defeito", "danificado", "nao funciona", "devolver", "devolucao",
    "reembolso", "troca", "trocar", "arrependi", "emperrando", "emperra", "nao abre",
    "reclamacao", "falar com vendedor", "falar com o vendedor", "comprei", "ja comprei",
    "recebi", "veio sem", "nao veio", "sem manual", "meu pedido", "cancelar",
    "nao chegou", "atraso", "ebook",
]

RESPOSTAS = {
    "gato": {
        ("manual", "montagem", "montar", "monta", "instruçao", "instrucao", "instruç", "como monto"):
            "Olá! Sim, o produto acompanha manual de montagem. Qualquer dúvida na montagem, estamos à disposição!",
        ("fixar", "fixaçao", "fixacao", "parede", "furar", "furo", "cola", "colar", "bucha", "parafuso", "prego"):
            "Olá! A fixação é feita na parede e o produto acompanha as buchas e parafusos necessários. Qualquer dúvida estamos à disposição!",
        ("aguenta", "suporta", "peso", "quilos", "quilo", "kilo", "kilos", "kg"):
            "Olá! A capacidade de peso suportada está informada na descrição do anúncio. Qualquer dúvida estamos à disposição!",
        ("mdf", "material", "madeira", "resistente", "carpete", "sisal"):
            "Olá! Nossos produtos são feitos em MDF, resistente e seguro para o seu pet.",
        ("cor", "cores", "caramelo", "marrom", "tabaco", "cru", "crua", "ocre", "cinza", "pintado", "pintada", "natural"):
            "Olá! As cores disponíveis estão indicadas no anúncio. Confira a opção escolhida antes de comprar.",
        ("verniz", "envernizar", "envernizada", "xixi", "impermeabiliz"):
            "Olá! Sim, o produto em MDF pode ser envernizado.",
        ("medida", "tamanho", "altura", "largura", "comprimento", "dimensao", " cm"):
            "Olá! As medidas completas estão na descrição do anúncio. Confira antes de comprar.",
        ("quantos gatos", "quantos pets", "quantos bichos", "dois gatos"):
            "Olá! Depende do tamanho dos gatos, mas em média cabem dois gatos médios por espaço.",
        ("externa", "externo", "area externa", "chuva", "sol", "tempo", "fora de casa"):
            "Olá! O produto deve ser mantido em local coberto e sem umidade, não sendo indicado para área externa.",
        ("quantas peca", "quantas pcs", "quantos itens", "quantas pecas", "vem quantas"):
            "Olá! A quantidade de peças está indicada no título e na descrição do anúncio.",
        ("coelho", "cachorro", "pet pequeno"):
            "Olá! O produto é indicado para gatos, mas alguns clientes utilizam para outros pets pequenos também.",
        ("completa", "completo", "igual a foto", "igual da foto", "identico", "como na foto"):
            "Olá! Sim, o produto é enviado conforme o anúncio.",
        ("nota", "fiscal", "nf", "nfe"):
            "Olá! Sim, acompanha nota fiscal.",
        ("frete", "entrega", "prazo", "chega", "chegar", "envio", "enviar", "demora", "quanto tempo"):
            "Olá! O frete e o prazo são calculados automaticamente pelo Mercado Livre ao informar seu CEP na página do anúncio.",
        ("estoque", "disponivel", "pronta entrega", "tem pronta"):
            "Olá! Temos estoque disponível, pode comprar com tranquilidade.",
    },
    "bandeja": {
        ("capsula", "capsulas", "capsua", "nespresso", "nespreso", "dolce", "gusto", "coracoes", "compativel", "cafeteira", "maquina", "genius", "passione", "serve para", "serve pra"):
            "Olá! A compatibilidade de cápsulas está indicada no anúncio (confira o modelo escolhido). Qualquer dúvida, estamos à disposição!",
        ("quantas", "cabem", "capacidade", "quantidade", "comporta"):
            "Olá! A capacidade de cápsulas está indicada no anúncio. Qualquer dúvida estamos à disposição!",
        ("cor", "cores", "preto", "preta", "marrom", "tabaco", "espelhada", "branca"):
            "Olá! As cores disponíveis estão indicadas no anúncio. Confira a opção escolhida antes de comprar.",
        ("sem o escrito", "cantinho", "sem escrita", "sem nome", "sem frase"):
            "Olá! No momento não temos um modelo sem o escrito '#cantinho do café'.",
        ("medida", "tamanho", "altura", "largura", "dimensao", " cm"):
            "Olá! As medidas completas estão na descrição do anúncio.",
        ("nota", "fiscal", "nf", "nfe"):
            "Olá! Sim, acompanha nota fiscal.",
        ("frete", "entrega", "prazo", "chega", "chegar", "envio", "enviar", "demora", "quanto tempo"):
            "Olá! O frete e o prazo são calculados automaticamente pelo Mercado Livre ao informar seu CEP na página do anúncio.",
        ("estoque", "disponivel", "pronta entrega", "tem pronta"):
            "Olá! Temos estoque disponível, pode comprar com tranquilidade.",
    },
    "sofa": {
        ("cor", "cores", "caramelo", "marrom", "tabaco", "preta", "preto", "azul", "cinza", "branca"):
            "Olá! As cores disponíveis estão indicadas no anúncio. Confira a opção escolhida antes de comprar.",
        ("medida", "tamanho", "altura", "largura", "comprimento", "dimensao", " cm"):
            "Olá! As medidas completas estão na descrição do anúncio.",
        ("porta copo", "porta controle", "porta celular", "acompanha", "vem com", "quantas peca", "itens"):
            "Olá! Os itens inclusos e a quantidade estão descritos no anúncio.",
        ("encaixa", "instala", "como usa", "apoio", "braço", "braco"):
            "Olá! O produto é de apoio/encaixe no braço do sofá, conforme descrito no anúncio.",
        ("nota", "fiscal", "nf", "nfe"):
            "Olá! Sim, acompanha nota fiscal.",
        ("frete", "entrega", "prazo", "chega", "chegar", "envio", "enviar", "demora", "quanto tempo"):
            "Olá! O frete e o prazo são calculados automaticamente pelo Mercado Livre ao informar seu CEP na página do anúncio.",
        ("estoque", "disponivel", "pronta entrega", "tem pronta"):
            "Olá! Temos estoque disponível, pode comprar com tranquilidade.",
    },
}


def classificar(item_id, texto):
    t = normalizar(texto)
    if any(normalizar(p) in t for p in ESCALAR):
        return ("humano", "reclamacao/pos-venda")
    grupo = GRUPO_POR_ITEM.get(str(item_id))
    if grupo is None:
        return ("humano", "produto nao mapeado")
    for palavras, resposta in RESPOSTAS.get(grupo, {}).items():
        if any(normalizar(p) in t for p in palavras):
            return ("responder", resposta)
    return ("humano", f"nao reconhecido ({grupo})")


def registrar_humano(item):
    dados = []
    if os.path.exists(ESCALADAS_FILE):
        with open(ESCALADAS_FILE, "r", encoding="utf-8") as f:
            dados = json.load(f)
    dados.append(item)
    with open(ESCALADAS_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def responder_pergunta(question_id, resposta, token):
    resp = requests.post(f"{API_BASE}/answers",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"question_id": question_id, "text": resposta}, timeout=20)
    resp.raise_for_status()


# ===== Rota que o Mercado Livre chama quando chega pergunta =====
@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}

    # so nos interessa o topico de perguntas
    if data.get("topic") != "questions":
        return "", 200

    # pega o ID da pergunta do campo "resource" (ex: "/questions/123456")
    resource = data.get("resource", "")
    qid = resource.rstrip("/").split("/")[-1]

    try:
        token = get_token()
        q = requests.get(f"{API_BASE}/questions/{qid}?api_version=4",
                         headers={"Authorization": f"Bearer {token}"}, timeout=20).json()

        # so responde se ainda estiver sem resposta
        if q.get("status") != "UNANSWERED":
            return "", 200

        item_id = q.get("item_id")
        texto = q.get("text", "") or ""
        acao, info = classificar(item_id, texto)

        if acao == "humano":
            print(f"HUMANO ({info}): {texto[:60]}")
            registrar_humano({"id": qid, "item_id": item_id, "texto": texto,
                              "motivo": info, "data": datetime.now().isoformat()})
        elif SIMULACAO:
            print(f"[SIMULA] {texto[:50]} -> {info[:60]}")
        else:
            print(f"Respondendo: {texto[:50]}")
            responder_pergunta(qid, info, token)

    except Exception as e:
        print(f"Erro ao processar pergunta {qid}: {e}")

    # SEMPRE responde 200 rapido pro ML nao ficar reenviando
    return "", 200


# ===== Rota de "saude" (pra testar se o servidor esta no ar) =====
@app.route("/", methods=["GET"])
def health():
    return "Bot webhook ativo!", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
