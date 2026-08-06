#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "/home/user/bot-webhook-ml/analise_consultorias")
from gerar_docx import Dossie
SAIDA = "/tmp/claude-0/-home-user-bot-webhook-ml/9065417a-c5bc-546a-a83d-9f9832c88261/scratchpad/Dossie_Pratik_William.docx"

d = Dossie("DOSSIÊ DE CONSULTORIA — Pratik Store (William)",
           "Análise de Consultorias · ICOMM / TF Treinamentos  ·  deal 95121")
d.kpis([
    ("Faturamento inicial", "R$ 1.000", "abr/2026"),
    ("Faturamento atual", "R$ 17.271", "+1625%"),
    ("Julho (30d)", "R$ 18.471", "conforme falas"),
])
d.tabela(["Campo", "Informação"], [
    ["Organização / Loja", "Pratik Store (William Ciscare; loja em nome da esposa, Karina)"],
    ["Nicho / perfil", "Multinichos (acessórios de celular, pet, infantil, papelaria, lar) · loja nova (~1 mês na entrada)"],
    ["Canais", "Shopee (foco); entrada no Mercado Livre planejada"],
    ["Consultor", "Anderson Volpato"],
    ["Produto contratado", "Consultoria Digital Business (8 encontros) — R$ 15.729"],
    ["Período", "Onboarding 23/04/2026 · 1º encontro 29/04 · último transcrito 08/07"],
    ["Sistemas / fiscal", "ERP Bling · Simples Nacional (ME 4%, migração CPF→CNPJ em curso) · Reputação verde escuro"],
    ["Saúde do aluno", "Ativo · aluno recorrente (já havia feito Consultoria Tração em 2025)"],
])

d.h1("1. Resultado — o \"deu certo\"")
d.p("A Pratik saiu de ~R$ 1.000 para R$ 17.271/mês (+1625%), chegando a R$ 18.471 em 30 dias (julho). "
    "Uma operação pequena e nova estruturada do começo, focada na Shopee, com playbook de anúncio + "
    "ADS + cupons.")
d.h2("Evolução (faturamento mensal)")
d.tabela(["Mês", "Faturamento", "Observação"], [
    ["Maio", "R$ 7.237", "1º mês; ativação do Shopee Ads"],
    ["Junho", "R$ 14.000", "+256%; crise de relevância do carro-chefe"],
    ["Julho (30d)", "R$ 18.471", "+84%; diagnóstico de mix por IA; adequação fiscal p/ ML"],
])
d.p("Leitura: crescimento consistente sobre uma base pequena. A conversão oscilou (mudança de mix e "
    "sazonalidade de fim de mês da Shopee), mas o volume e o número de pedidos subiram.", italico=True)

d.h1("2. A jornada do cliente no CRM")
d.p("Aluno recorrente: fez uma Consultoria Tração em 2025 e voltou para a Digital Business em 2026 — "
    "sinal de relacionamento e confiança (foi indicação de um casal da carteira que teve sucesso).")
d.tabela(["Negócio", "Quando", "Produto", "Valor", "Status"], [
    ["39340", "jun/2025", "Consultoria Tração (12 encontros)", "R$ 22.997", "Ganho"],
    ["95121", "abr/2026", "Consultoria Digital Business (8 encontros)", "R$ 15.729", "Ganho"],
])

d.h1("3. O que o cliente queria (discovery)")
d.tabela(["Item", "O que foi registrado"], [
    ["\"O que precisa p/ ficar feliz\"", "\"Aprender e crescer\""],
    ["Situação de entrada", "Loja Shopee com ~1 mês, multinichos, escolheu Shopee \"pela menor burocracia\" (sem CNPJ no início)"],
    ["Dor principal", "Fotos/descrição fracas; ADS feito \"tudo errado\"; conversão baixa e dependência de um carro-chefe"],
    ["Objetivo / Principal Dor (campos CRM)", "Não preenchidos no Pipedrive"],
    ["NPS / CSAT", "Não preenchidos no Pipedrive"],
])

d.h1("4. Dentro dos encontros — método aplicado")
d.tabela(["Encontro", "Tema", "Principais ações"], [
    ["29/04", "SWOT + playbook de anúncio", "Título-indexação (100 caract., Ubersuggest); fotos com quebra de objeção; promoção +20%; relâmpago; duplicar anúncios 3x"],
    ["13/05", "1º Shopee Ads (Curva A)", "Campanha Curva A (5 top sellers), ROAS 3,2; lives no calendário de maratona; canal de vídeo 3x/semana"],
    ["27/05", "Otimização + cupons", "Individualizar campeão; máquina de cupons diários (loja/produto/ticket/seguidor); mineração de produtos"],
    ["25/06", "Crise de relevância", "Recuperar anúncio ferido (foto/palavras-chave/ficha); Leve+/Combo; decoração da loja; Simples 4%"],
    ["08/07", "Diagnóstico por IA + ML", "Queda de conversão = mix (análise por IA); refazer 15 anúncios <1,5%; campanha própria da Shopee; entrada no ML"],
])

d.h1("5. Análise das transcrições — as falas reais")
d.p("As 5 transcrições mostram um aluno engajado e ansioso, aprendendo a ler dados (chega a usar IA para "
    "diagnosticar conversão) e evoluindo o playbook de anúncio na Shopee.")
d.h2("Motor do crescimento")
for b in [
    "Playbook de anúncio refinado: título-indexação, fotos com quebra de objeção, categoria correta, ficha completa.",
    "Promoção + Oferta Relâmpago diária + estoque virtual para forçar entrega do algoritmo.",
    "Shopee Ads (Curva A) + individualização de campeões + gestão por curva ABC / ACOS.",
    "Máquina de cupons diários (loja, produto, ticket, seguidor) — \"95% dos compradores buscam cupom\".",
    "Duplicação de anúncios (3x) e mineração de novos produtos via Assistente de Vendas.",
]:
    d.bullet(b)
d.h2("Dores técnicas recorrentes")
for b in [
    "Anúncios bem posicionados mas conversão baixa (idade da conta) e dependência de um único carro-chefe.",
    "Fotos ruins e descrição 100% GPT sem quebra de objeção no início.",
    "Orçamento de ADS limitado (R$ 50/dia) gerando \"pico e queda\".",
    "Reputação de anúncio: devoluções/avaliações negativas derrubando exposição.",
    "Queda de conversão por mudança de mix e sazonalidade de fim de mês da Shopee.",
]:
    d.bullet(b)
d.h2("Momentos de virada / marcos")
for b in [
    "13/05: ativação do Shopee Ads (Curva A) + lives + canal de vídeo.",
    "27/05: máquina de cupons + individualização de campeões.",
    "25/06: crise de relevância do carro-chefe → decoração da loja + definição fiscal.",
    "08/07: diagnóstico por IA (queda = mix) + campanhas da própria Shopee + adequação fiscal p/ ML.",
]:
    d.bullet(b)
d.h2("Citações marcantes")
for c in [
    "(29/04) \"Escolhi a Shopee pela burocracia menor... não precisava de CNPJ pra iniciar.\"",
    "(29/04, consultor) \"O cliente não lê o título. O título serve pra indexação.\"",
    "(27/05, consultor) \"ROAS de 20 é papo de guru... pelo menos um ROAS de 10\" para conta de ~1 ano.",
    "(08/07) \"A conversão por produto se mantém estável... a queda foi por mudança de mix.\"",
]:
    d.bullet(c)

d.h1("6. Síntese — o que fez a Pratik crescer")
d.p("Motor: playbook de anúncio + Shopee Ads + máquina de cupons, com o aluno aprendendo a ler dados "
    "(inclusive com IA). Multiplicou por ~17 uma base pequena.")
d.p("Método replicável: Digital Business focado em Shopee para iniciante — e o mesmo aluno já é "
    "recorrente (2ª contratação), o que valida o relacionamento.")
d.p("Frentes em aberto: refazer o catálogo inteiro (não só os 15 piores), reduzir dependência de "
    "produtos \"hype\", concluir a migração CNPJ e entrar no Mercado Livre.")

d.h1("7. Recomendações para o time")
for b in [
    "Refazer o catálogo inteiro (título/fotos/ficha), não só os 15 anúncios de menor conversão.",
    "Concluir a migração CPF→CNPJ (Simples 4%) e a entrada no Mercado Livre com o mesmo playbook.",
    "Estabilizar a conversão do novo mix e reduzir dependência de produtos de \"hype\".",
    "Explorar um novo upsell — o aluno já é recorrente e engajado.",
    "Preencher discovery/NPS/CSAT no Pipedrive.",
]:
    d.bullet(b)
d.p("")
d.p("Documento gerado do cruzamento entre CRM (Pipedrive) e as 5 transcrições. Campos ausentes no CRM "
    "marcados como \"não preenchido no Pipedrive\".", italico=True)
print("OK:", d.salvar(SAIDA))
