#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "/home/user/bot-webhook-ml/analise_consultorias")
from gerar_docx import Dossie
SAIDA = "/tmp/claude-0/-home-user-bot-webhook-ml/9065417a-c5bc-546a-a83d-9f9832c88261/scratchpad/Dossie_INOVA_Rafha.docx"

d = Dossie("DOSSIÊ DE CONSULTORIA — INOVA (Rafha Farmácia)",
           "Análise de Consultorias · ICOMM / TF Treinamentos  ·  deal 86338")
d.kpis([
    ("Faturamento inicial", "R$ 611.437", "mar/2026"),
    ("Faturamento atual", "não preenchido", "no Pipedrive"),
    ("Loja principal Shopee", "R$ 189k → 211k", "30d (1 de 3 lojas)"),
])
d.tabela(["Campo", "Informação"], [
    ["Organização", "Rafha Farmácia e Perfumaria Ltda · loja INOVA"],
    ["Operação", "David (operação/anúncios) + Lisanes (proprietário) + Brian (ML/precificação) + Michelle (analista, entra 24/07)"],
    ["Nicho / perfil", "Saúde/Farmácia/Perfumaria (MIP/OTC, cosmético, suplemento) · cliente grande"],
    ["Canais", "Shopee (3 lojas), Mercado Livre (implantação em jul), Magalu"],
    ["Consultor", "Mateus Fogaça"],
    ["Produto contratado", "Consultoria Tração (12 encontros) — R$ 35.000"],
    ["Período", "Onboarding 25/03/2026 · 1º encontro 01/04 · sessões passaram a semanais"],
    ["Sistemas / fiscal", "ERP Tiny/Olist · Lucro Real · Reputação verde escuro"],
    ["Saúde do aluno", "Ativo"],
])

d.h1("1. Resultado — atenção ao dado")
d.p("A INOVA entrou como um cliente grande (faturamento inicial R$ 611.437 no CRM). O campo de "
    "faturamento atual NÃO está preenchido no Pipedrive, e as transcrições também não trazem um total "
    "consolidado das 3 lojas — portanto o resultado final consolidado fica pendente de dado.")
d.h2("O que dá para afirmar pelas falas (parciais)")
d.tabela(["Referência", "Valor", "Observação"], [
    ["Loja principal Shopee (05/05)", "R$ 189k → R$ 211k (30d)", "apenas 1 das 3 lojas Shopee"],
    ["Janeiro (loja principal)", "~R$ 292.700", "3.678 pedidos, conversão 3,07%"],
    ["Quinzena de jul", "+71%", "recuperação após quedas"],
    ["Shopee (semana 31/07)", "+70%", "puxando o mês; ML ainda caindo (em implantação)"],
])
d.p("Recomendação: preencher o \"Faturamento Atual\" no Pipedrive somando as 3 lojas para fechar o "
    "resultado deste case (é um dos maiores da base).", italico=True)

d.h1("2. A jornada do cliente no CRM")
d.tabela(["Negócio", "Produto", "Valor", "Status"], [
    ["86338", "Consultoria Tração (12 encontros)", "R$ 35.000", "Ganho"],
])

d.h1("3. O que o cliente queria (discovery)")
d.tabela(["Item", "O que foi registrado"], [
    ["Objetivo declarado", "Profissionalizar a operação sem quebrar: \"estamos nos tornando um navio, precisamos de rebocador e prático\""],
    ["Situação de entrada", "Cresceu ~4–5 meses \"na raça\", 3 lojas Shopee, sem acompanhamento/DRE"],
    ["Dor de entrada", "~R$ 100 mil de afiliados descontados SEM campanha ativa; não sabiam direcionar verba de ADS"],
    ["Objetivo / Principal Dor (campos CRM)", "Não preenchidos no Pipedrive"],
    ["NPS / CSAT", "Não preenchidos no Pipedrive"],
])

d.h1("4. Dentro dos encontros — método aplicado")
d.tabela(["Encontro", "Tema", "Principais ações"], [
    ["01/04", "Diagnóstico Shopee", "3 pilares; melhoria de anúncios (7 fotos + vídeo, SEO); precificar +30%; responder 10.486 avaliações; chamado dos afiliados"],
    ["15/04", "Shopee Ads (GMV Max)", "Curva A (≥20 vendas) unitária ROAS 15–20; curva B agrupada ROAS 10–14; teto R$ 10/dia; otimizar a cada 7 dias"],
    ["05/05", "Exposição orgânica", "Regras de soma cupom/desconto/relâmpago; cupom seguidores/exclusivo; programa de devolução (R$ 0,50); mesmo preço nas 3 plataformas"],
    ["17/07", "Queda + fraude interna", "Diagnóstico: queda de visita (mercado); IA p/ recursos; carta de autorização p/ MIP; base/WMS + câmera (devoluções 60→1)"],
    ["24/07", "Otimização por custo/venda", "Custo por venda e TACOS (não só ROAS); desligar ADS p/ forçar orgânico; onboarding da analista Michelle"],
    ["31/07", "Entrada no Mercado Livre", "Sair do Correio; \"boi de piranha\" p/ liberar Full; clássico+premium; kits p/ fugir do catálogo; tese de marca própria"],
])
d.p("Observação: há um vão de transcrições entre 05/05 e 17/07 (o arquivo de 22/05 veio vazio).", italico=True)

d.h1("5. Análise das transcrições — as falas reais")
d.p("As 7 transcrições úteis mostram um cliente grande sendo profissionalizado: base bem-feita destrava "
    "orgânico, ADS por curva, e um episódio marcante de fraude interna resolvido com WMS + câmera.")
d.h2("Motor do crescimento")
for b in [
    "Base bem estruturada (anúncios excelentes: foto/vídeo/título/ficha) destravando venda orgânica.",
    "Ferramentas gratuitas de exposição (cupom, oferta relâmpago, desconto, moedas, novos seguidores, transmissão por chat).",
    "ADS eficiente por curva (A unitária / B agrupada) medido por custo por venda / TACOS, não só ROAS.",
    "Expansão de canais: 3 lojas Shopee → Mercado Livre (Full/catálogo/kits) → tese de marca própria de encapsulados.",
]:
    d.bullet(b)
d.h2("Dores técnicas recorrentes")
for b in [
    "Afiliados cobrando sem campanha ativa (~R$ 100 mil acumulados; segue gerando notas) — arrasta desde o 1º encontro.",
    "Bugs da Shopee: duplicidade de etiquetas/envios e ADS consumindo acima do limite (R$ 400–450/dia sumindo).",
    "Penalidades por atraso e por \"produto proibido\" (MIP: Hipoglós, AD Forte) e propriedade intelectual.",
    "Margem apertada (contribuição ~9–11%); itens no prejuízo revelados pela planilha de custos.",
    "Fraude interna: gerentes desviando (~R$ 60–70 mil) e abrindo CNPJ clone com os curva A.",
]:
    d.bullet(b)
d.h2("Momentos de virada")
for b in [
    "Loja principal Shopee: R$ 189 mil → R$ 211 mil (30d) após melhoria de anúncios + exposição orgânica.",
    "Base/WMS + câmera: devoluções de 60 → 1 e fim da fraude interna (remove dreno de ~R$ 60–70 mil).",
    "Recuperação de +71% na quinzena e Shopee +70% na semana de 31/07.",
    "Abertura do eixo Mercado Livre/Full e da tese de marca própria como próximos degraus de margem.",
]:
    d.bullet(b)
d.h2("Citações marcantes")
for c in [
    "(01/04) \"Para manobrar um navio você precisa de rebocador e o prático. A gente está se tornando um navio.\"",
    "(01/04) \"Foi um tiro no pé esses afiliados\" — sobre os ~R$ 100 mil cobrados sem campanha.",
    "(17/07) \"Vi roubando, moço. Justa causa. Pegaram meu CNPJ, abriram igualzinho, vendendo meus produtos, só os curva A.\"",
    "(24/07) \"Os dados estão bonitos? Estão. Só que eu gastei R$ 5,90 para fazer uma venda, não os 83 centavos.\"",
    "(31/07) \"Vocês que têm drogaria têm que ter a marca de encapsulado de vocês... é o que eu mais ganho dinheiro hoje.\"",
]:
    d.bullet(c)

d.h1("6. Síntese — o que está fazendo a INOVA dar certo")
d.p("Motor: profissionalização de um cliente que cresceu \"na raça\" — base de anúncios excelente + "
    "exposição orgânica + ADS por custo/venda + WMS que estancou fraude e devoluções. Agora expandindo "
    "para Mercado Livre e marca própria.")
d.p("Método replicável: mesmo playbook (curva ABC, cupons/relâmpago, precificar +30%), aqui numa "
    "operação multiloja de farmácia/perfumaria.")
d.p("Pendências críticas: recuperar os ~R$ 100 mil de afiliados, resolver o bug de ADS, mitigar o CNPJ "
    "clone dos ex-funcionários e — importante para este dossiê — preencher o faturamento atual no CRM.")

d.h1("7. Recomendações para o time")
for b in [
    "PREENCHER o \"Faturamento Atual\" no Pipedrive (somando as 3 lojas) — hoje é o dado que falta para fechar o case.",
    "Escalar a cobrança dos afiliados (ouvidoria/jurídico) e o chamado do bug de ADS.",
    "Concluir a entrada no Mercado Livre (Full) e executar a tese de marca própria de encapsulados.",
    "Formalizar a estratégia contra o CNPJ clone (jurídico) e blindar os curva A.",
    "Preencher discovery/NPS/CSAT no Pipedrive.",
]:
    d.bullet(b)
d.p("")
d.p("Documento gerado do cruzamento entre CRM (Pipedrive) e as transcrições. Campos ausentes no CRM "
    "marcados como \"não preenchido no Pipedrive\".", italico=True)
print("OK:", d.salvar(SAIDA))
