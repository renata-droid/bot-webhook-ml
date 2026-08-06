#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "/home/user/bot-webhook-ml/analise_consultorias")
from gerar_docx import Dossie
SAIDA = "/tmp/claude-0/-home-user-bot-webhook-ml/9065417a-c5bc-546a-a83d-9f9832c88261/scratchpad/Dossie_Centermed_Carol.docx"

d = Dossie("DOSSIÊ DE CONSULTORIA — Centermed (Carol Coelho)",
           "Análise de Consultorias · ICOMM / TF Treinamentos  ·  deal 9099")
d.kpis([
    ("Foco", "Mentoria Shopee", "4 encontros"),
    ("Faturamento (CRM)", "não preenchido", "campos zerados no Pipedrive"),
    ("Shopee (nas falas)", "~R$ 15 mil/mês", "+79% em 30 dias"),
])
d.tabela(["Campo", "Informação"], [
    ["Organização", "Centermed Oliveira (Carolina)"],
    ["Nicho / perfil", "Vendedora já forte no Mercado Livre; almofadas de gel, utilidades; margem ~30%"],
    ["Canais", "Mercado Livre (base) + Shopee (foco da mentoria)"],
    ["Consultor (gravações)", "Anderson Volpato — divergente do CRM, que registra Mateus Fogaça"],
    ["Produto contratado", "CRM: Consultoria Tração (12 encontros); gravações: Mentoria Shopee (4 encontros)"],
    ["Período", "Gravações jan–fev/2025; CRM registra onboarding 20/05/2025 (ver nota de divergência)"],
    ["Sistemas / fiscal", "Sem ERP · Simples Nacional"],
    ["Saúde do aluno", "Não preenchido no Pipedrive · já era aluna (fez ADS avançado antes)"],
])

d.h1("Nota de fidelidade (divergências CRM × gravações)")
for b in [
    "Nas gravações o consultor se apresenta como Anderson Volpato; o CRM registra Mateus Fogaça.",
    "As 4 gravações são de jan–fev/2025; o CRM registra onboarding 20/05/2025 e 1º encontro 04/06/2025.",
    "O CRM registra \"Consultoria Tração (12 encontros)\"; as gravações são \"Mentoria Shopee\" e o consultor fala em 4 encontros (a aluna diz que o combo foi \"erro da escola\").",
    "Todos os campos de faturamento estão zerados/não preenchidos no Pipedrive — os números abaixo vêm só das falas.",
]:
    d.bullet(b)

d.h1("1. Resultado — o que dá para afirmar")
d.p("Como o CRM não tem faturamento, o resultado se apoia nas falas: a Carol já era forte no Mercado "
    "Livre (~R$ 340 mil citados) e a mentoria estruturou a Shopee do zero de método, levando a loja a "
    "~R$ 15 mil/mês com +79–81% de crescimento em janelas de 7–30 dias, taxa de utilização de cupom de "
    "40% (média do mercado é 15%) e recuperação do nível \"excelente\".")
d.h2("Marcos ditos nos encontros")
d.tabela(["Encontro", "Marco", "Números"], [
    ["22/01", "Setup completo da Shopee", "cupons, relâmpago, Upseller, afiliados, 1º ADS (GMV Max)"],
    ["29/01", "Prova de valor", "afiliados R$ 1.200 / ROI ~190x; +81% em 7 dias; ~R$ 15 mil/mês"],
    ["05/02", "Escala curva A+B", "recarga automática de ADS; ACOS 8,2 (30d); afiliados escalando"],
    ["12/02", "Encerramento", "+79% em 30 dias; cupom 40% de uso; afiliados = 15% do faturamento"],
])

d.h1("2. A jornada do cliente no CRM")
d.tabela(["Negócio", "Produto", "Valor", "Status"], [
    ["9099", "Consultoria Tração (12 encontros)", "R$ 16.997", "Ganho"],
])
d.p("Contexto do CRM: \"já é nossa aluna, ano passado fez ADS avançado com o Reinaldo\" — cliente de "
    "relacionamento, contratou nova frente (Shopee).", italico=True)

d.h1("3. O que a cliente queria (discovery)")
d.tabela(["Item", "O que foi registrado"], [
    ["Objetivo declarado", "Aprender a operar a Shopee (já dominava o Mercado Livre)"],
    ["Situação de entrada", "\"De Shopee eu não entendo muito, fui tateando... botei dinheiro no ADS e perdi tudo\""],
    ["Dor principal", "Traduzir a lógica do ML (ACOS/TACOS) para a Shopee (ROAS/GMV Max); insegurança com orçamento de ADS"],
    ["Objetivo / Principal Dor (campos CRM)", "Não preenchidos no Pipedrive"],
    ["NPS / CSAT", "Não preenchidos no Pipedrive"],
])

d.h1("4. Dentro dos encontros — método aplicado")
d.tabela(["Encontro", "Tema", "Principais ações"], [
    ["22/01", "Onboarding + setup Shopee", "Cupons (seguidor/loja/produto/ticket); relâmpago (estoque 9); Upseller (impulso automático); afiliados 7%; 1º ADS GMV Max"],
    ["29/01", "SWOT + ACOS/TACOS", "Combo e Leve+; transmissão de chat (4x/semana); públicos personalizados; análise de ADS 30/15/7"],
    ["05/02", "Recarga + curva ABC", "Recarga automática (gatilho R$ 40); comissão afiliados 7%→8%; escalar curva A+B via planilha ABC"],
    ["12/02", "Otimização 1-a-1 + campanha de loja", "Poda de campanhas ruins; campanha de loja (branding, 20 palavras-chave); regra de orçamento por curva"],
])

d.h1("5. Análise das transcrições — as falas reais")
d.p("As 4 transcrições mostram uma vendedora experiente no ML aprendendo a lógica da Shopee. O grande "
    "valor foi montar toda a estrutura da Shopee em um único encontro e provar valor rápido (afiliados "
    "ROI 190x).")
d.h2("Foco da mentoria")
for b in [
    "Estruturação completa da Shopee do zero para quem já era forte no Mercado Livre.",
    "Ferramentas de marketing da Shopee: cupons, oferta relâmpago, combo, leve+, transmissão de chat, decoração.",
    "Marketing de afiliados como alavanca de baixo custo e alto ROI.",
    "Shopee Ads (GMV Max + lance manual por palavra-chave) e rotina de otimização por Curva ABC.",
]:
    d.bullet(b)
d.h2("Dores técnicas recorrentes")
for b in [
    "Dificuldade de traduzir ACOS/TACOS (ML) para a linguagem da Shopee (ROAS/ROI/GMV Max).",
    "Insegurança com gestão de orçamento de ADS (quando escalar/parar) e medo de \"gastar mais\".",
    "ADS da Shopee contabiliza vendas não pagas (boleto/Pix) — motivo do fracasso anterior.",
    "Bugs frequentes (edição de anúncios, decoração de loja, relâmpago).",
    "Operação unipessoal sobrecarregada; falta material de referência sobre Shopee.",
]:
    d.bullet(b)
d.h2("Marcos / decisões")
for b in [
    "22/01: setup completo da Shopee em um único encontro.",
    "29/01: prova de valor — afiliados R$ 1.200 / ROI 190x; +81% em 7 dias.",
    "05/02: escala estruturada de curva A+B e recarga automática de ADS.",
    "12/02: crescimento acumulado 79%/30 dias; nível \"excelente\"; afiliados = 15% do faturamento.",
]:
    d.bullet(b)
d.h2("Citações marcantes")
for c in [
    "(22/01) \"De Shopee eu não entendo muito, fui tateando... botei um dinheiro lá e perdi tudo.\"",
    "(29/01) \"Já aumentou 80% em sete dias meu faturamento. Já deu um norte, porque eu não sabia nada.\"",
    "(12/02) \"Semana que vem tu não tá comigo... tenho medo de não saber o que fazer e gastar mais.\"",
    "(12/02) \"40% de taxa de utilização [de cupom]. Primeira vez que eu vejo... a média é 15%.\"",
]:
    d.bullet(c)

d.h1("6. Síntese — o que a mentoria entregou")
d.p("Motor: montar a Shopee inteira (cupons, relâmpago, afiliados, ADS) e provar valor rápido para uma "
    "vendedora que já dominava o ML. Em ~1 mês a loja saltou +79% e recuperou o nível \"excelente\".")
d.p("Método replicável: o playbook de Shopee (cupons em cascata, relâmpago com escassez, afiliados, GMV "
    "Max por curva) — o mesmo que aparece nos alunos de Shopee (William, Inova).")
d.p("Ponto de atenção: só 4 encontros para um conteúdo denso (a própria aluna considerou insuficiente e "
    "sinalizou querer nova mentoria); autonomia frágil em gestão de orçamento de ADS ao fim.")

d.h1("7. Recomendações para o time")
for b in [
    "Corrigir os dados do negócio no Pipedrive: consultor, datas e produto divergem das gravações; faturamento em branco.",
    "Oferecer continuidade (a aluna sinalizou querer nova mentoria) — relacionamento já existe.",
    "Concluir pendências técnicas citadas: vídeos dos anúncios e decoração/banners da loja.",
    "Reforçar autonomia em gestão de orçamento de ADS (principal insegurança declarada).",
    "Preencher discovery/NPS/CSAT no Pipedrive.",
]:
    d.bullet(b)
d.p("")
d.p("Documento gerado do cruzamento entre CRM (Pipedrive) e as 4 transcrições. Divergências entre CRM e "
    "gravações foram sinalizadas; campos ausentes no CRM marcados como \"não preenchido no Pipedrive\".",
    italico=True)
print("OK:", d.salvar(SAIDA))
