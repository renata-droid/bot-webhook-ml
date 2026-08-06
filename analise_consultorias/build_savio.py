#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "/home/user/bot-webhook-ml/analise_consultorias")
from gerar_docx import Dossie
SAIDA = "/tmp/claude-0/-home-user-bot-webhook-ml/9065417a-c5bc-546a-a83d-9f9832c88261/scratchpad/Dossie_Farmacia_Eficacia_Savio.docx"

d = Dossie("DOSSIÊ DE CONSULTORIA — Farmácia Eficácia (Savio)",
           "Análise de Consultorias · ICOMM / TF Treinamentos  ·  deal 77283")
d.kpis([
    ("Faturamento inicial", "≈ R$ 0", "começou do zero no ML"),
    ("Faturamento atual", "R$ 169.529", "jul/2026"),
    ("Em ~4,5 meses", "R$ 52k → 169k", "1º mês já foi R$ 52.543"),
])
d.tabela(["Campo", "Informação"], [
    ["Organização / Loja", "Eficácia Farmácia de Manipulação (Savio Aguiar)"],
    ["Operação", "Conduzida por Jéssica (gerente de e-commerce) e Luísa (conteúdo/cadastro)"],
    ["Nicho / perfil", "Saúde · farmácia de manipulação · já tinha e-commerce próprio (~R$ 1 mi/mês), zero em marketplace"],
    ["Canais", "Mercado Livre (único)"],
    ["Consultor", "Anderson Volpato"],
    ["Produto contratado", "Consultoria Tração (12 encontros) — R$ 24.297"],
    ["Período", "Onboarding 26/02/2026 · 1º encontro 09/03 · encerramento 30/07/2026"],
    ["Sistemas / fiscal", "Sem ERP · Lucro Real · Reputação: não se aplica (conta nova)"],
    ["Saúde do aluno", "Ativo"],
])

d.h1("1. Resultado — o \"deu certo\"")
d.p("A Eficácia entrou na consultoria sem operação de marketplace (a base inicial não foi preenchida no "
    "Pipedrive — na prática começou do zero no Mercado Livre) e chegou a R$ 169.529/mês em julho/2026. "
    "O 1º mês já fechou em R$ 52.543 e o ritmo foi de dobra: R$ 109 mil no 2º, R$ 118 mil no 3º e R$ 169 "
    "mil no 4º. É um case de construção do zero num nicho difícil (saúde/manipulação).")
d.h2("Evolução (fotografias de 30 dias ditas nos encontros)")
d.tabela(["Encontro", "Fat. 30d", "Conversão", "Ticket", "Observação"], [
    ["23/04", "R$ 35.732", "4,7%", "R$ 93", "384 vendas; modelo de curvas consolidado"],
    ["07/05", "R$ 52.543 (abril)", "3,6%", "R$ 88", "fechou o 1º mês"],
    ["28/05", "R$ 108.466", "11%", "R$ 136", "+147% — rompeu os R$ 100 mil"],
    ["18/06", "R$ 118.403", "3,2% / 11,5% (7d)", "R$ 90", "duplicação de vencedores"],
    ["16/07", "R$ 147.382", "10,2%", "R$ 83", "+79% conversão"],
    ["30/07", "R$ 162.727", "8,9%", "R$ 84", "21.791 visitas (+91%); Full ativado"],
])
d.p("Leitura: o crescimento veio de conversão altíssima para a categoria (subiu de ~3,6% para ~9–11%) "
    "sobre um carro-chefe dominante (a DAPA-glifosina, ~90% do faturamento), sustentado por um motor "
    "promocional pesado e por Product Ads bem geridos. As visitas até caíram em alguns períodos, mas a "
    "conversão compensou.", italico=True)

d.h1("2. A jornada do cliente no CRM")
d.p("Um único negócio até aqui (primeira consultoria). O aluno é Ativo e o contexto (e-commerce próprio "
    "forte) favorece upsell futuro.")
d.tabela(["Negócio", "Quando", "Produto", "Valor", "Status"], [
    ["77283", "fev/2026", "Consultoria Tração (12 encontros)", "R$ 24.297", "Ganho"],
])

d.h1("3. O que o cliente queria (discovery)")
d.tabela(["Item", "O que foi registrado"], [
    ["Objetivo declarado", "\"Do zero até o Mercado Full com Mercado Livre Platinum; até lá não espero lucro\" (09/03)"],
    ["Situação de entrada", "Domínio de e-commerce próprio (~R$ 1 mi/mês) e mídia (R$ 80–100k/mês), mas ZERO em marketplace"],
    ["Dor principal", "Aprender a lógica do Mercado Livre (vindo do Google Ads) e não queimar reputação"],
    ["Objetivo / Principal Dor (campos CRM)", "Não preenchidos no Pipedrive — inferidos das falas"],
    ["NPS / CSAT", "Não preenchidos no Pipedrive"],
])

d.h1("4. Dentro dos encontros — método aplicado")
d.tabela(["Encontro", "Tema / dor", "Principais ações"], [
    ["09/03", "Onboarding + 1º anúncio", "Fugir de catálogo com EAN/MPN únicos; fotos (solução/técnico/objeção); título 60 caracteres de palavra-chave; sacrificar 1 produto no zero-a-zero"],
    ["16/03", "Pesquisa de mercado", "Avante Pro + Shopping de Preços; categoria válida ≥ R$ 1 mi/mês; média de ~10 concorrentes p/ precificar"],
    ["23/03", "Decola + Ads + catálogo", "Ativar Decola (libera Ads e promoções); campanha ROAS 4→baixar p/ tracionar; Clips com avisos legais"],
    ["30/03", "Motor promocional", "Relâmpago em todos os horários nos top-20; cupons (diário/carrinho/seguidores); campanha base da loja; todas as campanhas do Meli"],
    ["06/04", "Full/curva ABC/afiliados", "Ativar Mercado Turbo (curva ABC); competir com oferta agressiva sem Full; afiliados"],
    ["23/04", "Campanhas por curva", "Curva A ROAS≥8, C ROAS 3, campanha Novidades; desativar orçamento compartilhado"],
    ["07/05", "TACOS + Fora de Curva", "Cálculo de TACOS ao vivo (meta ~5%); ACOS por curva (A 0-10/B 10-20/C 20-35); campanha \"Fora de Curva\""],
    ["28/05", "Alta de custo + IA", "Reprecificar via anúncio novo (não mexer no ranqueado); IA no garimpo; rompeu R$ 100k"],
    ["11–18/06", "Duplicação de vencedores", "Triplicar anúncios campeões (capa diferente, benefícios na imagem); campanha base recriada"],
    ["02–16/07", "Avaliações + guerra de preço", "Avaliações internas; manter-se ~5% acima do menor preço; régua de afiliados por ROI"],
    ["30/07", "Encerramento + Full", "Full ativado; critério de matar produto (30d/100 visitas s/ conversão); SWOT final; suporte por WhatsApp"],
])

d.h1("5. Análise das transcrições — as falas reais")
d.p("As 14 transcrições mostram um aluno tecnicamente exigente (vem do Google Ads) construindo do zero. "
    "Quem opera é a Jéssica; o Savio entra nas decisões. Nicho saúde traz bloqueios constantes de "
    "produtos pela IA do Meli.")
d.h2("Motor do crescimento")
for b in [
    "DAPA-glifosina como carro-chefe absoluto (~90%): baixa concorrência, subida a preço agressivo (4 meses de tratamento pelo preço de 1 dos concorrentes) e ranqueada cedo.",
    "Motor promocional pesado e diário: relâmpago em todos os horários nos top-20 + cupons + todas as campanhas do Meli + campanha base da loja.",
    "Product Ads organizado por curva ABC (A/B/C + Novidades + Fora de Curva), com gestão semanal de ROAS/ACOS/TACOS.",
    "Clips como tráfego orgânico + duplicação/triplicação de anúncios vencedores (mais palavras-chave/indexações).",
    "Conversão altíssima para a categoria (de ~3,6% em abril para ~9–11% em julho) compensando a queda de visitas.",
]:
    d.bullet(b)
d.h2("Dores técnicas recorrentes")
for b in [
    "Bloqueios constantes de produtos \"proibidos\"/medicamento (NAC, Empa, Clomifeno...) — IA do Meli inconsistente.",
    "Produção just-in-time incompatível com prazos do Meli; atrasos e retenção de saldo.",
    "Dependência crítica da DAPA (~90%) e dificuldade de tracionar os demais.",
    "Guerra de preço e taxas do Meli subindo de ~30% para ~40%.",
    "Curva de aprendizado dolorosa vinda do Google Ads.",
]:
    d.bullet(b)
d.h2("Momentos de virada")
for b in [
    "Mar/26: setup completo (Avante, Decola, Ads, promoções) → 1º mês R$ 52.543.",
    "Abr/26: motor promocional + curva ABC + DAPA firmando → R$ 109 mil.",
    "Mai/26: rompeu R$ 100k em 30 dias; domínio de TACOS → R$ 118 mil.",
    "Jun–Jul/26: duplicação de vencedores + afiliados escalados + Full ativado → R$ 169 mil.",
]:
    d.bullet(b)
d.h2("Citações marcantes")
for c in [
    "(09/03) \"Eu quero do zero a estar no Mercado Full com o Mercado Livre Platinum, até lá eu não espero lucro.\"",
    "(11/06) \"Só tô tendo venda em DAPA, o resto não tá vendendo. Ela é 90%. Eu tô dependendo de DAPA para tudo.\"",
    "(16/07) \"Não aguento mais depender da DAPA... que profissão é essa que você está me dando de presente?\"",
    "(30/07, consultor) \"Você não vai ter o encontro da vitória... você vai repetir todo esse ciclo sempre. Só vai mudar de desafio.\"",
]:
    d.bullet(c)

d.h1("6. Síntese — o que fez a Eficácia dar certo")
d.p("Motor: um carro-chefe forte (DAPA) + motor promocional diário + Ads por curva + conversão altíssima. "
    "Construiu do zero uma operação de R$ 169 mil/mês em ~4,5 meses num nicho difícil.")
d.p("Método replicável: é o mesmo playbook de tração (curva ABC, ACOS/ROAS objetivo, relâmpago/cupons, "
    "duplicação de vencedores), provado agora no nicho Saúde.")
d.p("Risco nº 1: dependência de ~90% de um único produto (DAPA) sob guerra de preço crescente — "
    "diversificar os carros-chefe é a próxima frente. Full só foi ativado no último encontro; margem "
    "corroída por ~40% de taxas.")

d.h1("7. Recomendações para o time")
for b in [
    "Reduzir a dependência da DAPA: aplicar o playbook de duplicação/Ads nos produtos secundários já validados.",
    "Consolidar o Full (ativado no fim) e resolver a pendência fiscal (18% vs 8% de imposto / possível novo CNPJ).",
    "Plano de avaliações para os produtos novos (concorrente tem 5.000; a conta ainda tem poucas).",
    "Avaliar expansão para Shopee (cogitada) usando a mesma base de produtos e método.",
    "Preencher discovery/NPS/CSAT no Pipedrive (hoje em branco) e registrar a base inicial como \"início do zero\".",
    "Aproveitar o perfil (e-commerce próprio forte) para um upsell/recompra — o resultado já é o argumento.",
]:
    d.bullet(b)
d.p("")
d.p("Documento gerado do cruzamento entre CRM (Pipedrive) e as 14 transcrições. Campos ausentes no CRM "
    "marcados como \"não preenchido no Pipedrive\".", italico=True)
print("OK:", d.salvar(SAIDA))
