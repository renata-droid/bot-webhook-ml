#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "/home/user/bot-webhook-ml/analise_consultorias")
from gerar_docx import Dossie
SAIDA = "/tmp/claude-0/-home-user-bot-webhook-ml/9065417a-c5bc-546a-a83d-9f9832c88261/scratchpad/Dossie_ICONNECT_Lucas.docx"

d = Dossie("DOSSIÊ DE CONSULTORIA — ICONNECT (Lucas)",
           "Análise de Consultorias · ICOMM / TF Treinamentos  ·  deal 87269")
d.kpis([
    ("Faturamento inicial", "R$ 117.599", "mar/2026"),
    ("Faturamento atual", "R$ 216.337", "+84%"),
    ("Recompra", "R$ 24.997", "renovou em mai/2026"),
])
d.tabela(["Campo", "Informação"], [
    ["Organização / Loja", "ICONNECT (Lucas)"],
    ["Operação", "Carlos (gerente, opera a tela) + Lucas (sócio/decisor) + Eduardo (gerente Shopee)"],
    ["Nicho / perfil", "Multinicho de atacado (tintas/permeabilizantes Eurodecor, cilindros Malta), evitando eletrônico"],
    ["Canais", "Mercado Livre, Shopee, Amazon, Magalu, Shein (todos no Full)"],
    ["Consultor", "Mateus Fogaça"],
    ["Produtos contratados", "Consultoria Tração (12 encontros) R$ 22.497 → Recompra 12 encontros R$ 24.997"],
    ["Período", "Onboarding 27/03/2026 · 1º encontro 30/03 · recompra 26/05/2026"],
    ["Sistemas / fiscal", "ERP Upseller · Simples Nacional · Reputação verde escuro · conta com ~5 meses"],
    ["Saúde do aluno", "Ativo"],
])

d.h1("1. Resultado — o \"deu certo\"")
d.p("A ICONNECT saiu de R$ 117.599 (mar/2026) para R$ 216.337/mês (+84%) numa conta jovem (~5 meses de "
    "vida). O salto veio de estruturar antes de gastar: pesquisa de mercado para cadastrar os produtos "
    "certos, curva A no Full e ADS assertivo. O objetivo declarado no CRM é rentabilidade (\"quer fazer "
    "a empresa ter mais rentabilidade\").")
d.h2("Evolução (fotografias de 30 dias ditas nos encontros — Mercado Livre)")
d.tabela(["Encontro", "Fat. 30d ML", "Destaque"], [
    ["30/03", "~R$ 121.000", "diagnóstico; ~R$ 468 mil de intenção de compra \"na mesa\""],
    ["20/04", "~R$ 100.000", "mês anterior R$ 170k; começou a criar anúncios novos"],
    ["29/04", "R$ 99.000", "incubadora de ADS; TACOS < 3"],
    ["04/05", "R$ 108.000", "curva A no Full: \"vai dobrar seu faturamento\""],
    ["11/05", "15 dias +150%", "curva A no Full + reestruturação de ADS"],
    ["19/05", "15 dias +128%", "cilindro vira \"bala\" (produto de alta receita)"],
    ["26/05", "R$ 215.000", "consolidação; recompra fechada"],
])
d.p("Leitura: 3 pilares sempre à vista (visita, conversão, ticket). A virada mais citada foi levar a "
    "curva A para o Full e reestruturar o ADS por curva — de ~R$ 40–50 mil (início da conta) para "
    "R$ 215 mil em ~5 meses.", italico=True)

d.h1("2. A jornada do cliente no CRM")
d.p("Case clássico de recompra: primeira consultoria → resultado → renovação de 12 encontros já com "
    "foco na Shopee (2ª metade do método).")
d.tabela(["Negócio", "Quando", "Produto", "Valor", "Status"], [
    ["87269", "mar/2026", "Consultoria Tração (12 encontros)", "R$ 22.497", "Ganho"],
    ["102295 (recompra)", "mai/2026", "Consultoria Tração (12 encontros)", "R$ 24.997", "Ganho"],
])
d.p("Nota comercial: fechou após 1 reunião em dezembro que não converteu (\"não era o momento\"). "
    "Bônus registrados: +2 encontros p/ Amazon, ingressos MeliXP e jantar G4.")

d.h1("3. O que o cliente queria (discovery)")
d.tabela(["Item", "O que foi registrado"], [
    ["Situação de entrada", "Vende em ML, Shopee, Magalu, Amazon — todos no Full; multinicho de atacado"],
    ["Problema", "\"Quer fazer tudo de maneira correta, escalar as vendas e ter melhor gerenciamento\""],
    ["\"O que precisa p/ ficar feliz\"", "\"Fazer a empresa ter mais rentabilidade (maior objetivo da consultoria)\""],
    ["Objetivo / Principal Dor (campos)", "Não preenchidos no Pipedrive — inferidos das notas"],
    ["NPS / CSAT", "Não preenchidos no Pipedrive"],
])

d.h1("4. Dentro dos encontros — método aplicado")
d.tabela(["Encontro", "Tema", "Principais ações"], [
    ["30/03", "SWOT / diagnóstico ML", "3 pilares; anúncio de qualidade (5–7 fotos + clipe); curva A no Full; cupom carrinho; dividir 6 encontros ML / 6 Shopee"],
    ["06/04", "ADS + Curva ABC", "Só anunciar quem já vende; 6–10 anúncios/campanha; ROAS por curva (A 15–20, B 8–12, C 4–6); desativar ajuste automático"],
    ["13/04", "Pesquisa de mercado", "Shop de Preços: categoria vs. próprio; cadastrar curva A primeiro; renovar identidade a cada 45–90 dias"],
    ["20/04", "Arquitetura de ADS", "Campanha \"Estrela\" (1 anúncio top); reestruturação na virada de mês; truque clássico/premium na mesma opção"],
    ["29/04", "Otimização + incubadora", "Campanha \"Incubadora\" (curva que gastou e não vendeu); TACOS < 3 ideal, máx 5"],
    ["04/05", "Minha Página + Full", "Cupons estratégicos; antecipar promoções nos dias 28/29/30; gestão de Full por curva A"],
    ["11/05", "Escala + ROAS", "\"O menos é mais\" (mexer no máx 2 pontos); Minha Página; foco mobile"],
    ["19/05", "Relógio do Full + ruptura", "Estratégia de ruptura (deixar zerar com conversão alta, não subir preço); marca oficial p/ derrubar catálogo"],
    ["26/05", "Full na Shopee + curva A", "Montagem do Full Shopee (alíquota 0,01% p/ Full); produto errado impacta menos que atraso; recompra fechada"],
])

d.h1("5. Análise das transcrições — as falas reais")
d.p("As 9 transcrições (30/03 a 26/05) mostram a transição de \"gastar para vender\" para \"estruturar "
    "para vender\". Quem opera é o Carlos; Lucas (sócio) viaja muito e decide.")
d.h2("Motor do crescimento")
for b in [
    "Anúncios de alta performance (foto de benefício/quebra de objeção por IA, clipe obrigatório) + curva A no Full + ADS só em quem já vende.",
    "Pesquisa de mercado (Shop de Preço) como bússola para cadastrar os produtos certos primeiro — assertividade acima de volume.",
    "Portfólio de atacado com \"1.000 SKUs fáceis de curva A/B\" ainda inexplorados — principal vetor de escala futura.",
]:
    d.bullet(b)
d.h2("Dores técnicas recorrentes")
for b in [
    "Ruptura de estoque em curva A (óculos, cilindro, mantas) derrubando faturamento e ADS.",
    "Bugs do painel ML e dificuldade de rever aulas; FULL da Shopee travado por erro fiscal (2 meses).",
    "Logística: despacho com atraso, transição para Envio Coletas, entregas para SP.",
    "Estoque \"infinito\" (fake) a migrar para estoque real via ERP Upseller.",
]:
    d.bullet(b)
d.h2("Momentos de virada")
for b in [
    "Encontro 3 (pesquisa de mercado): \"jogo no centro, saio de 100 mil para 500 mil\".",
    "Encontros 6→7: curva A no Full + reestruturação de ADS → 15 dias +150%.",
    "Encontro 8: 15 dias +128%; cilindro vira produto de alta receita.",
    "Encontro 9: consolidação em R$ 215 mil/30 dias (de R$ 40–50 mil no início) + recompra.",
]:
    d.bullet(b)
d.h2("Citações marcantes")
for c in [
    "(30/03) \"Curva A precisa estar no Full. Isso é na conta dele, na sua, na minha, é na conta do mundo.\"",
    "(20/04) \"Publicidade não vende. Ela impulsiona... o que vende é meu título e minhas fotos.\"",
    "(13/04) \"Cara, essa aula é a mais importante da consultoria.\" — sobre pesquisa de mercado.",
    "(26/05) \"Quem que em cinco meses cresce... vai pra 215 mil?\"",
]:
    d.bullet(c)

d.h1("6. Síntese — o que fez a ICONNECT dar certo")
d.p("Motor: estruturação (anúncio de alta performance + pesquisa de mercado + curva A no Full + ADS por "
    "curva) sobre um portfólio de atacado enorme. Resultado: dobrou uma conta de 5 meses e recomprou.")
d.p("Método replicável: mesmo playbook de tração dos demais alunos; aqui o diferencial é o multinicho "
    "de atacado com centenas de SKUs prontos para escalar.")
d.p("Frentes em aberto: Shopee ainda pequena (foco dos 6 encontros da recompra), ruptura recorrente em "
    "produtos-âncora, migração para estoque real (Upseller) e bugs de plataforma.")

d.h1("7. Recomendações para o time")
for b in [
    "Aproveitar a recompra para atacar a Shopee (Full destravado) e Amazon (bônus de 2 encontros).",
    "Processo de compras/estoque de segurança para a curva A — a ruptura é o principal freio.",
    "Explorar sistematicamente os \"1.000 SKUs\" de atacado com o método de pesquisa de mercado.",
    "Preencher no Pipedrive discovery, NPS/CSAT (hoje em branco).",
]:
    d.bullet(b)
d.p("")
d.p("Documento gerado do cruzamento entre CRM (Pipedrive) e as 9 transcrições. Campos ausentes no CRM "
    "marcados como \"não preenchido no Pipedrive\".", italico=True)
print("OK:", d.salvar(SAIDA))
