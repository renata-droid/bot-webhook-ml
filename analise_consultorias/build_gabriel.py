#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "/home/user/bot-webhook-ml/analise_consultorias")
from gerar_docx import Dossie
SAIDA = "/tmp/claude-0/-home-user-bot-webhook-ml/9065417a-c5bc-546a-a83d-9f9832c88261/scratchpad/Dossie_Habitare_Gabriel.docx"

d = Dossie("DOSSIÊ DE CONSULTORIA — Habitare (Gabriel)",
           "Análise de Consultorias · ICOMM / TF Treinamentos  ·  deal 72858")
d.kpis([
    ("Faturamento inicial", "≈ R$ 0", "começou do zero no ML"),
    ("Faturamento atual", "R$ 10.464", "~R$ 200 → R$ 14 mil (falas)"),
    ("Conversão final", "2,7%", "negócio consistente"),
])
d.tabela(["Campo", "Informação"], [
    ["Organização / Loja", "Habitare Acabamentos Finos (Gabriel Machado Guimarães)"],
    ["Operação", "\"Dani\" (responsável operacional) opera as aulas; Gabriel é o dono/decisor"],
    ["Nicho / perfil", "Construção / acabamentos finos (torneiras, cubas, chuveiros, papeleiras)"],
    ["Canais", "Mercado Livre"],
    ["Consultora", "Liara Silva"],
    ["Produto contratado", "Consultoria Digital Business (8 encontros) — R$ 14.757 · 6 encontros transcritos"],
    ["Período", "Onboarding 05/02/2026 · 1º encontro 10/02 · último transcrito 14/07"],
    ["Sistemas / fiscal", "ERP próprio (não integrado ao ML) · Simples Nacional"],
    ["Saúde do aluno", "Ativo"],
])

d.h1("1. Resultado — construção do zero")
d.p("A Habitare começou praticamente do zero no marketplace (base não preenchida no Pipedrive) e chegou "
    "a R$ 10.464/mês no CRM. Nas falas, a consultora resume o salto: \"quando começamos no dia 5 você "
    "vendia muito pouquinho (~R$ 200 em 30 dias); hoje já foi para R$ 14 mil\". Um case de arrancada num "
    "nicho de acabamentos.")
d.h2("Evolução (marcos ditos nos encontros)")
d.tabela(["Encontro", "Marco", "Números"], [
    ["05/05", "Estrutura-base montada", "~12 vendas; afiliados + cupom + central de promoções + curvas"],
    ["19/05", "Reação ao ADS", "ajuste de ROAS (5,5) → vendeu 2 torneiras \"na hora\""],
    ["16/06", "Salto de vendas", "22 vendas/30 dias; estoque/ERP vira o gargalo"],
    ["30/06", "Consolidação", "faturamento ~R$ 14 mil; oportunidade do FULL descoberta"],
    ["14/07", "Encerramento", "R$ 6.333/15 dias; conversão 2,7%; negócio consistente"],
])
d.p("Leitura: crescimento consistente sobre base pequena. O motor mais visível foi a Central de "
    "Promoções sempre ligada (desligou = parou de vender; ligou = voltou) + afiliados baratos + clipes.",
    italico=True)

d.h1("2. A jornada do cliente no CRM")
d.tabela(["Negócio", "Produto", "Valor", "Status"], [
    ["72858", "Consultoria Digital Business (8 encontros)", "R$ 14.757", "Ganho"],
])

d.h1("3. O que o cliente queria (discovery)")
d.tabela(["Item", "O que foi registrado"], [
    ["Situação de entrada", "Loja de acabamentos começando no ML, do zero, com ERP próprio não integrado"],
    ["Dor principal", "Estar entre os mais caros do catálogo; ruptura de estoque nos campeões; conflito interno sobre gasto em ADS"],
    ["Objetivo / Principal Dor (campos CRM)", "Não preenchidos no Pipedrive"],
    ["NPS / CSAT", "Não preenchidos no Pipedrive"],
])

d.h1("4. Dentro dos encontros — método aplicado")
d.tabela(["Encontro", "Tema", "Principais ações"], [
    ["05/05", "Diagnóstico + estrutura-base", "Cancelar Decola (já fez 10 vendas); afiliados 12%+12%; cupom carrinho; central de promoções; ADS por curva (A/B/Tração); clipes"],
    ["19/05", "ACOS/ROAS + títulos", "Palavra repetida encarece ADS; baixar ROAS 6,6→5,5; Brand Ads; cupom novos seguidores; Mercado Turbo (curva ABC/DRE)"],
    ["02/06", "Preço vs. catálogo + margem", "Catálogo caro não se ganha; margem de entrada apertada p/ girar; desovar estoque parado; rebates primeiro"],
    ["16/06", "Salto + ruptura + ERP", "Funil 484 visitas→48 intenções; ruptura = perda direta; cobrar API do ERP; NF nos dados do pagador"],
    ["30/06", "Shopping de Preços + FULL", "Pesquisa profunda; FULL como grande oportunidade (quase sem concorrentes); fotos/ambientação (\"vendedor de balcão não pode ser mudo\")"],
    ["14/07", "Atacado B2B + kits + público", "Kits em construção; atacado B2B (CNPJ, desconto progressivo); catálogo puro (ROAS 15–20); leitura de público (Audiências)"],
])

d.h1("5. Análise das transcrições — as falas reais")
d.p("As 6 transcrições mostram a operadora \"Dani\" executando e o Gabriel decidindo. O grande aprendizado "
    "é que um catálogo caro não se ganha por preço — o jogo vira anúncios tradicionais, promoções e "
    "afiliados.")
d.h2("Motor do crescimento")
for b in [
    "Central de Promoções ligada o tempo todo (correlação direta: desligou = parou; ligou = voltou).",
    "Afiliados como fonte barata de tráfego (chegou a metade das vendas quinzenais; comissão efetiva <10%).",
    "Clipes/vídeos nos anúncios (os produtos que venderam foram \"por clipes\").",
    "Product Ads por curva (A/B/Tração) com ajuste fino de ROAS/ACOS.",
    "Cupons de carrinho abandonado e de novos seguidores gerando urgência.",
]:
    d.bullet(b)
d.h2("Dores técnicas recorrentes")
for b in [
    "Estar sistematicamente entre as opções mais caras do catálogo (não ganha por preço).",
    "Ruptura de estoque nos campeões (medo de comprar × giro real) — perda direta de vendas.",
    "ERP próprio não integrado ao ML (sem API; estoque na mão; anúncios finalizados).",
    "Títulos com palavras repetidas encarecendo o ADS; fotos fracas → clique sem conversão.",
    "Travas operacionais (Shopping de Preços com autenticação, acesso perdido ao Facebook da ex-dona).",
]:
    d.bullet(b)
d.h2("Momentos de virada / marcos")
for b in [
    "19/05 — reação instantânea ao ajuste de ROAS (venda de 2 torneiras na hora).",
    "16/06 — salto para 22 vendas/30 dias; estoque/ERP reconhecido como gargalo.",
    "30/06 — de ~R$ 200 (30d) para ~R$ 14 mil; descoberta da oportunidade do FULL.",
    "14/07 — encerramento com R$ 6.333/15 dias e conversão 2,7%.",
]:
    d.bullet(b)
d.h2("Citações marcantes")
for c in [
    "(19/05) \"A gente acabou de mexer no ACOS dela... ela teve reação. Instantâneo.\"",
    "(02/06) \"Faz uma semana que você não vende. Está tudo no preço cheio, ninguém compra.\"",
    "(16/06) \"Por isso a gente precisa de ERP para controlar estoque? Você está perdendo venda dentro do Mercado Livre.\"",
    "(30/06) \"Não tem concorrentes de vocês dentro do FULL. E quem vai pro FULL vende bem.\"",
]:
    d.bullet(c)

d.h1("6. Síntese — o que fez a Habitare andar")
d.p("Motor: central de promoções sempre ligada + afiliados baratos + clipes + ADS por curva. Saiu do "
    "zero para um negócio consistente (~R$ 10–14 mil/mês) num nicho de acabamentos.")
d.p("Método replicável: Digital Business para iniciante em construção — o desafio é preço/margem "
    "(entrar competitivo e ganhar barganha com volume) e estoque.")
d.p("Frentes em aberto: FULL (oportunidade mapeada, não executada), integração ERP↔ML, atacado B2B e "
    "melhora de fotos/conteúdo.")

d.h1("7. Recomendações para o time")
for b in [
    "Habilitar o FULL — oportunidade competitiva mapeada (quase sem concorrência no nicho).",
    "Integração ERP↔ML para acabar com a ruptura de estoque dos campeões.",
    "Estratégia de margem de entrada → volume → barganha com fornecedor; explorar atacado B2B.",
    "Melhorar fotos/ambientação dos anúncios que recebem clique mas não convertem.",
    "Preencher discovery/NPS/CSAT no Pipedrive e registrar a base inicial como \"início do zero\".",
]:
    d.bullet(b)
d.p("")
d.p("Documento gerado do cruzamento entre CRM (Pipedrive) e as 6 transcrições. Campos ausentes no CRM "
    "marcados como \"não preenchido no Pipedrive\".", italico=True)
print("OK:", d.salvar(SAIDA))
