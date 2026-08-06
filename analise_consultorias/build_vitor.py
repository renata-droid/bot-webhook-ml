#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "/home/user/bot-webhook-ml/analise_consultorias")
from gerar_docx import Dossie
SAIDA = "/tmp/claude-0/-home-user-bot-webhook-ml/9065417a-c5bc-546a-a83d-9f9832c88261/scratchpad/Dossie_RedeClip_Vitor.docx"

d = Dossie("DOSSIÊ DE CONSULTORIA — Rede Clip (Vitor)",
           "Análise de Consultorias · ICOMM / TF Treinamentos  ·  deal 96041")
d.kpis([
    ("Faturamento inicial", "≈ R$ 0", "começou do zero no ML"),
    ("Faturamento atual", "R$ 12.576", "operação nascendo"),
    ("Acumulado", "171 vendas", "84 anúncios ao fim"),
])
d.tabela(["Campo", "Informação"], [
    ["Organização", "Rede Clip (Vitor) · sócio de rede de lojas físicas em Ijuí/RS"],
    ["Perfil da rede", "3 lojas, ~50 mil SKUs, ~50 anos, faturamento físico ~R$ 28 mi/ano (\"uma Havan sem roupa\")"],
    ["Nicho / perfil", "Arte, papelaria, armarinho, cama-mesa-banho, brinquedos, utilidades"],
    ["Canais", "Mercado Livre"],
    ["Consultor", "Renan Rezende"],
    ["Produto contratado", "Consultoria Digital Business (14 encontros) — R$ 20.000"],
    ["Período", "Onboarding 29/04/2026 · 1º encontro 07/05 (encontros quinzenais)"],
    ["Sistemas / fiscal", "Sem ERP · Simples/Lucro Presumido · reputação em construção (Decola)"],
    ["Saúde do aluno", "Ativo"],
])

d.h1("1. Resultado — construção do zero")
d.p("O Vitor começou sem operação de marketplace (base não preenchida no Pipedrive — na prática, do "
    "zero) e chegou a R$ 12.576, com 171 vendas acumuladas e 84 anúncios ao fim do período coberto. É "
    "um case de arrancada: sair do zero, fazer as primeiras vendas e estruturar as alavancas.")
d.h2("Evolução (marcos ditos nos encontros)")
d.tabela(["Encontro", "Marco", "Números"], [
    ["07/05", "Onboarding", "R$ 0 vendidos; 5 alavancas; 1º anúncio de catálogo criado"],
    ["28/05", "Reputação verde (Decola)", "R$ 250 pagos; ainda 0 vendas"],
    ["11/06", "PRIMEIRAS VENDAS", "16 anúncios → 3 vendas; 183 visitas (7d)"],
    ["25/06", "Tração inicial", "R$ 6.830 (15d); conversão 1,7%; ~150 vendas acumuladas"],
    ["09/07", "ADS + Minha Página", "84 anúncios; 171 vendas; 1ª campanha de ADS (ROAS 10)"],
])
d.p("Leitura: o gargalo não foi método, foi partir do zero (validação de conta, primeiras vendas, "
    "logística no Correio). Vantagem estrutural enorme: rede física com ~50 mil SKUs comprados direto de "
    "fábrica.", italico=True)

d.h1("2. A jornada do cliente no CRM")
d.tabela(["Negócio", "Produto", "Valor", "Status"], [
    ["96041", "Consultoria Digital Business (14 encontros)", "R$ 20.000", "Ganho"],
])

d.h1("3. O que o cliente queria (discovery)")
d.tabela(["Item", "O que foi registrado"], [
    ["Objetivo declarado", "Tirar a rede física do papel no digital: \"tenho condições de fazer bonito pela nossa história\""],
    ["Situação de entrada", "Rede física forte (~R$ 28 mi/ano), zero em marketplace; trava cultural de vender online"],
    ["Dor principal", "Falta de tempo/pessoa dedicada; validação de conta (sócio não administrador); margem \"pagando para aprender\""],
    ["Objetivo / Principal Dor (campos CRM)", "Não preenchidos no Pipedrive"],
    ["NPS / CSAT", "Não preenchidos no Pipedrive"],
])

d.h1("4. Dentro dos encontros — método aplicado")
d.tabela(["Encontro", "Tema", "Principais ações"], [
    ["07/05", "Onboarding + 5 alavancas", "Pesquisa de mercado, anúncio de alta performance, palavras-chave, tráfego pago, funil; precificação; catálogo por código de barras; logística Correio→Agência→Full"],
    ["28/05", "Validação + Decola", "Cadastro em catálogo; R$ 250 Decola (reputação verde); saúde da conta (máx 2% reclamação)"],
    ["11/06", "Primeiras vendas + afiliados", "Promoção mensal nomeada; rebate (tag verde); frete abaixo de R$ 79; afiliados começando em 5%"],
    ["25/06", "Pesquisa/análise de mercado", "Funil e mapa de calor; Análise de Mercado nativa do ML; garrafa térmica como próxima aposta"],
    ["09/07", "ADS + Minha Página", "Conceito de ROAS (catálogo começa em 10, R$ 5/dia); Minha Página p/ carrinho abandonado; afiliados 5%→6%"],
])

d.h1("5. Análise das transcrições — as falas reais")
d.p("As 5 transcrições mostram um aluno consciente do atraso e do próprio gargalo (não consegue operar "
    "no dia a dia), construindo do zero com forte vantagem de custo/estoque da rede física.")
d.h2("Motor do crescimento")
for b in [
    "Volume de catálogo cadastrado por código de barras (rápido, alta exposição) + preço competitivo das promoções.",
    "Migração logística Correio → Agência (elevou conversão e reduziu prazo) rumo ao Full.",
    "Vantagem estrutural: rede física de ~50 mil SKUs, compra direto de fábrica (Stanley, Faber-Castell, Termolar).",
    "Alavancas progressivas: promoções com rebate → afiliados (custo baixíssimo) → ADS → carrinho abandonado.",
]:
    d.bullet(b)
d.h2("Dores técnicas recorrentes")
for b in [
    "Validação de conta (Vitor é sócio não administrador; conta no CNPJ com o pai como administrador).",
    "Confusão persistente com a regra do frete grátis > R$ 79 (aparece em quase todos os encontros).",
    "Estoque não segregado do físico → rupturas, anúncios pausados por falta, erro de cor/SKU.",
    "Falta de integração ERP/ML (notas e baixa de estoque manuais).",
    "Bloqueio de anúncios originais (Stanley) por suspeita de falsificação.",
]:
    d.bullet(b)
d.h2("Momentos de virada / marcos")
for b in [
    "28/05 — reputação verde ativada (Decola pago).",
    "11/06 — primeiras 3 vendas e primeiro despacho (saída do zero).",
    "25/06 — R$ 6.830 em 15 dias; migração para Agência; térmica identificada como próxima aposta.",
    "09/07 — 84 anúncios, 171 vendas acumuladas, 1ª campanha de ADS e Minha Página ativadas.",
]:
    d.bullet(b)
d.h2("Citações marcantes")
for c in [
    "(07/05) \"A gente é uma Havan sem roupa.\"",
    "(07/05) \"No Mercado Livre você começa no difícil para o fácil. O cara quer que você desista.\"",
    "(11/06) \"Você colocou 16 anúncios... são três vendas. Imagina se tivesse uns 160 anúncios aí.\"",
    "(09/07) \"Quase todos os itens eu estou vendendo pra pagar os impostos... tô pagando pra aprender. Mas em algum momento vou ter que virar essa bolacha.\"",
]:
    d.bullet(c)

d.h1("6. Síntese — o que está fazendo o Rede Clip andar")
d.p("Motor: catálogo em volume + promoções com rebate + logística evoluindo (Correio→Agência→Full), "
    "com a vantagem enorme de estoque/custo da rede física. Em ~2 meses saiu do zero para 171 vendas.")
d.p("Método replicável: as 5 alavancas do Digital Business aplicadas a um iniciante com forte retaguarda "
    "física — o desafio é execução/tempo, não método.")
d.p("Frentes em aberto: margem (vendendo quase no zero-a-zero \"para aprender\"), integração ERP↔ML "
    "(crítica para escalar) e uma pessoa dedicada para tocar a operação.")

d.h1("7. Recomendações para o time")
for b in [
    "Precificar com lucro (o consultor já sinalizou que é hora de \"virar a bolacha\").",
    "Integração ERP↔ML — provável desenvolvimento comum aos 16 associados da rede (oportunidade coletiva).",
    "Resolver a sucessão operacional: Vitor não consegue executar; falta pessoa dedicada.",
    "Acelerar o Full e a garrafa térmica (oportunidade de catálogo já mapeada).",
    "Preencher discovery/NPS/CSAT e registrar a base inicial como \"início do zero\" no Pipedrive.",
]:
    d.bullet(b)
d.p("")
d.p("Documento gerado do cruzamento entre CRM (Pipedrive) e as 5 transcrições. Campos ausentes no CRM "
    "marcados como \"não preenchido no Pipedrive\".", italico=True)
print("OK:", d.salvar(SAIDA))
