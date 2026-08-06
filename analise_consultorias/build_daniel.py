#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "/home/user/bot-webhook-ml/analise_consultorias")
from gerar_docx import Dossie
SAIDA = "/tmp/claude-0/-home-user-bot-webhook-ml/9065417a-c5bc-546a-a83d-9f9832c88261/scratchpad/Dossie_ASTER_Daniel.docx"

d = Dossie("DOSSIÊ DE CONSULTORIA — ASTER (Daniel)",
           "Análise de Consultorias · ICOMM / TF Treinamentos  ·  deal 87231")
d.kpis([
    ("Faturamento inicial", "R$ 95.000", "mar/2026"),
    ("Faturamento atual", "R$ 172.884", "+82%"),
    ("Meta declarada", "R$ 300 mil", "até fim do ano"),
])
d.tabela(["Campo", "Informação"], [
    ["Organização", "Aster Distribuidora de Materiais para Construção (Daniel) · Projeto WEG"],
    ["Operação", "Maiara (dedicada) + Gabriele + Isabel + Felipe (compras)"],
    ["Nicho / perfil", "Construção civil · distribuidora · ticket alto (fechaduras, chuveiros, telas, ferramentas)"],
    ["Canais", "Mercado Livre"],
    ["Consultor", "Pedro Sousa"],
    ["Produto contratado", "Consultoria WEG/Tração — campo \"Produto\" não preenchido no Pipedrive"],
    ["Período", "Onboarding 23/03/2026 · 1º encontro 27/03 · último transcrito 03/07"],
    ["Sistemas / fiscal", "ERP próprio (apartado do ML, estoque manual) · Lucro Real · Reputação verde escuro"],
    ["Status do negócio", "Aberto (no Pipedrive)"],
])

d.h1("1. Resultado — o \"deu certo\"")
d.p("A ASTER saiu de R$ 95.000 para R$ 172.884/mês (+82%), com pico de faturamento citado em ~R$ 179 mil "
    "em julho. O crescimento veio de profissionalizar o ADS (que era feito \"no escuro\"), enxugar de "
    "~600 SKUs para poucos fornecedores com profundidade, e entrar em produtos de ticket maior "
    "(fechadura WEG, ferramentas Ancora).")
d.h2("Evolução (faturamento CRM + variações ditas nos encontros)")
d.tabela(["Marco", "Faturamento", "Observação"], [
    ["Inicial (mar)", "R$ 95.000", "linha de base"],
    ["1º mês", "R$ 100.080", "estruturação de ADS por curva"],
    ["22/05", "+34%", "menos SKUs, mais profundidade; ticket maior"],
    ["2º mês", "R$ 172.884", "fechadura WEG + ferramentas Ancora"],
    ["19/06", "+47%", "visitas +28%, preço médio +16%"],
    ["03/07", "~R$ 179.000", "conversão em queda (-0,8 p.p.) → teto sinalizado"],
])
d.p("Leitura: disciplina nos 3 indicadores (visitas, conversão, preço médio) com diagnóstico anúncio a "
    "anúncio (Ishikawa). O preço médio subiu com o mix de ticket alto; a conversão em queda no fim é o "
    "alerta principal.", italico=True)

d.h1("2. A jornada do cliente no CRM")
d.tabela(["Negócio", "Produto", "Valor", "Status"], [
    ["87231", "Consultoria WEG/Tração (produto não preenchido)", "R$ 4.000", "Aberto"],
    ["(2º na jornada)", "outro negócio da organização", "—", "—"],
])
d.p("Observação: o negócio ainda consta como \"Aberto\" e com valor R$ 4.000 — provável registro "
    "parcial/pendência de atualização no Pipedrive (o produto também não foi preenchido).", italico=True)

d.h1("3. O que o cliente queria (discovery)")
d.tabela(["Item", "O que foi registrado"], [
    ["Objetivo declarado", "\"A ideia da Aster não é escalar/ser o maior; a gente queria ter uma operação saudável\" (que pague os salários do setor e deixe caixa)"],
    ["Dor principal", "Margem: \"ou o produto vende bem mas a margem é zero, ou dá margem e não vende\""],
    ["Situação de entrada", "Distribuidora de construção com ~600 SKUs, ERP próprio apartado do ML"],
    ["Objetivo / Principal Dor (campos CRM)", "Não preenchidos no Pipedrive"],
    ["NPS / CSAT", "Não preenchidos no Pipedrive"],
])

d.h1("4. Dentro dos encontros — método aplicado")
d.tabela(["Encontro", "Tema", "Principais ações"], [
    ["27/03", "Onboarding + 4 P's", "3 indicadores; 4 P's de Kotler; market share (mirar concorrentes atingíveis); precificação correta; ME1 p/ itens grandes"],
    ["10/04", "ADS + Curva ABC + Full", "Funil de ADS (Visibilidade/Crescimento/Rentabilidade + Catálogo); máx 5 anúncios/campanha; Full = 100% do vendido em 30d"],
    ["24/04", "Otimização + afiliados", "Diagnóstico por participação %; campanha de afiliados (subsidiada pelo ML); reduzir SKUs; frete grátis embutido"],
    ["07/05", "Reputação/Full/Ishikawa", "Prazo <97% custa 20–40% das visitas; documentar falhas do ML; diagrama de Ishikawa; pontuação Full 49→meta 71"],
    ["22/05", "Precificação detalhada", "Margem ideal ~20% (real 2–7% em vários itens); Ancora Tools como teste antes da WEG; sazonais sem controle de reposição"],
    ["08/06", "Estratégia R$ 300 mil", "Poucos SKUs com profundidade por fornecedor; foto de capa IA (Canva + Gemini); prazo de disponibilidade p/ vender antes do estoque"],
    ["19/06", "Rupturas + otimização", "Não deixar cair 2 períodos seguidos; campanha de recuperação (ROAS 14,3); otimização de ADS diária"],
    ["03/07", "Teste ABC / Lançamentos", "Duplicar curva A e catálogos perdendo; teste ABC de títulos (campanha \"Lançamentos\"); impacto financeiro da conversão (+R$ 48,9 mil)"],
])

d.h1("5. Análise das transcrições — as falas reais")
d.p("As 8 transcrições mostram um aluno estratégico (Daniel) e uma operadora dedicada (Maiara) saindo do "
    "\"ADS no escuro\" para uma gestão por curva e por indicador. Nicho de construção, ticket alto e "
    "margens apertadas.")
d.h2("Motor do crescimento")
for b in [
    "Disciplina nos 3 indicadores com diagnóstico anúncio a anúncio (Ishikawa).",
    "ADS profissional por Curva ABC + catálogo, com otimização diária e campanhas de visibilidade/recuperação/lançamento.",
    "De ~600 SKUs pulverizados para poucos SKUs com profundidade por fornecedor estratégico (WEG, Ancora, Vago, Zagonel).",
    "Entrada de produtos de ticket maior (fechadura WEG, ferramentas Ancora) elevando o preço médio.",
    "Alavancas de tráfego: Full, afiliados (subsidiado pelo ML) e replicação de anúncios campeões (market share).",
]:
    d.bullet(b)
d.h2("Dores técnicas recorrentes")
for b in [
    "Ruptura de estoque por ERP apartado do ML e gestão manual — derruba visita e conversão juntas.",
    "Precificação em Lucro Real com margens apertadas (2–7% em vários itens; ideal ~20%).",
    "Full: pontuação baixa (49 vs meta 71), falta de espaço, custo de retirada de encalhe.",
    "Falhas do ML: etiqueta não imprimindo (atraso/reputação), anúncio trocando de categoria sozinho, \"perder no catálogo\".",
    "Otimização de ADS ainda dependente da reunião.",
]:
    d.bullet(b)
d.h2("Momentos de virada")
for b in [
    "Abr/26: estruturação de ADS por curva + afiliados + disciplina de Full.",
    "22/05: +34% com foco em menos SKUs/mais profundidade e ticket maior.",
    "19/06: +47% (visitas +28%, preço médio +16%) com fechadura WEG e Ancora.",
    "03/07: ~R$ 179 mil, mas conversão em queda (-0,8 p.p.) → ênfase em teste ABC/lançamentos.",
]:
    d.bullet(b)
d.h2("Citações marcantes")
for c in [
    "(27/03) \"A ideia da Aster não é nem escalar... a gente só queria ter uma operação saudável.\"",
    "(10/04) \"Eu fazia a Edis no escuro. Fiz a campanha e deixei rodando.\" (Maiara)",
    "(22/05) \"Do recebido dos R$ 408 do Mercado Livre, eu fico só com R$ 102.\" (Felipe, compras)",
    "(19/06, consultor) \"Esquece mesmo. Tem que tocar nisso [otimização de ADS] todo dia.\"",
]:
    d.bullet(c)

d.h1("6. Síntese — o que fez a ASTER dar certo")
d.p("Motor: profissionalização do ADS por curva + foco em poucos fornecedores com profundidade + "
    "produtos de ticket alto. Dobrou o faturamento com foco em \"operação saudável\".")
d.p("Método replicável: mesmo playbook de tração, adaptado a um distribuidor de construção (ticket alto, "
    "margem apertada, Lucro Real).")
d.p("Ponto de atenção nº 1: conversão em queda no fim (impacto quantificado ~R$ 48,9 mil) e margens "
    "apertadas. Resolver estoque/ERP e a fechadura que \"perde no catálogo\" é o próximo degrau.")

d.h1("7. Recomendações para o time")
for b in [
    "Integrar ERP ao ML (estoque em tempo real) — a ruptura é a causa nº 1 das quedas.",
    "Institucionalizar o teste ABC / campanhas de \"Lançamentos\" para escalar novos produtos.",
    "Resolver a fechadura WEG no catálogo (regulação da loja oficial) e a troca automática de categoria da tela.",
    "Atualizar o negócio no Pipedrive: status (consta \"Aberto\"), produto e valor; preencher discovery/NPS.",
    "Perseguir a meta de R$ 300 mil com ~R$ 50 mil por fornecedor-chave, como o próprio Daniel planejou.",
]:
    d.bullet(b)
d.p("")
d.p("Documento gerado do cruzamento entre CRM (Pipedrive) e as 8 transcrições. Campos ausentes no CRM "
    "marcados como \"não preenchido no Pipedrive\".", italico=True)
print("OK:", d.salvar(SAIDA))
