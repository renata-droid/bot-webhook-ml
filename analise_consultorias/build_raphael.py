#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Monta o dossie do Raphael (Ultra Online) em .docx."""
import sys
sys.path.insert(0, "/home/user/bot-webhook-ml/analise_consultorias")
from gerar_docx import Dossie

SAIDA = "/tmp/claude-0/-home-user-bot-webhook-ml/9065417a-c5bc-546a-a83d-9f9832c88261/scratchpad/Dossie_Ultra_Online_Raphael.docx"

d = Dossie("DOSSIÊ DE CONSULTORIA — Ultra Online (Raphael)",
           "Análise de Consultorias · ICOMM / TF Treinamentos  ·  deal 74172")

d.kpis([
    ("Faturamento inicial", "R$ 260.953", "fev/2026"),
    ("Faturamento atual", "R$ 1.026.854", "jun/2026 · passou de R$ 1 mi/mês"),
    ("Crescimento", "+293%", "≈ 3,9× em ~4 meses"),
])

# ---------- Cabeçalho ----------
d.tabela(["Campo", "Informação"], [
    ["Organização / Loja", "Ultra Online (calçados, roupas e bolsas) · ~20 lojas físicas, +20 anos, RJ"],
    ["Contato", "Raphael (dono) · operação conduzida pela gerente Lívia"],
    ["Nicho / perfil", "Calçados (forte) · revendedor multimarcas · loja física há +20 anos"],
    ["Canais", "Mercado Livre + Shopee + TikTok Shop · Amazon criada (não operada) · Reputação verde escuro"],
    ["Consultor", "Anderson Volpato  ·  Buddy/CS: Luis Castagne  ·  Closer/SDR: Matheus Medeiros"],
    ["Produto contratado", "Consultoria Tração (12 encontros) + 4 encontros extras — proposta especial de R$ 41.000"],
    ["Escopo especial", "28 encontros táticos + 2 estratégicos com Thiago Franco + acompanhamento da assessora Bruna + apoio no bloqueio de marcas/NF na Shopee"],
    ["Período", "Ganho 29/01/2026 · Onboarding 04/02 · 1º encontro 10/02 · fim esperado 26/08/2026"],
    ["Sistemas / fiscal", "ERP Tiny/Olist (migrando p/ Atom) · Lucro Real"],
    ["Saúde do aluno", "Ativo"],
])

# ---------- 1. Resultado ----------
d.h1("1. Resultado — o \"deu certo\"")
d.p("O faturamento do Ultra Online saiu de R$ 260.953 (fevereiro/2026, linha de base do onboarding) "
    "para R$ 1.026.854 (junho/2026) — um crescimento de +293,5% (≈ 3,9×) em cerca de 4 meses, "
    "cruzando a marca de R$ 1 milhão/mês. O valor confere com o campo de resultado do Pipedrive "
    "(Variação R$ 765.901). É um dos cases mais fortes da base: um operador de calçados que já "
    "faturava alto e triplicou.")
d.p("Marcos do CRM: Faturamento inicial R$ 260.953 · 2º mês R$ 865.726 · 3º mês / atual R$ 1.026.854.")

d.h2("De onde veio o crescimento (fotografias de 30 dias do Mercado Livre, ditas nos encontros)")
d.p("Os números abaixo são \"últimos 30 dias\" do Mercado Livre citados em cada reunião (não o total "
    "consolidado). Mostram a montanha-russa de estoque e a retomada forte no fim.", italico=True)
d.tabela(["Data do encontro", "Fat. 30d ML", "Conversão", "Visitas", "Ticket", "Leitura"], [
    ["03/03", "R$ 432.945", "2,5%", "—", "R$ 153", "+105% — decolagem"],
    ["10/03", "R$ 377.991", "2,4%", "—", "R$ 148", "queda por ruptura/suspensão"],
    ["17/03", "R$ 337.500", "2,2%", "100 mil", "R$ 150", "estoque rompendo"],
    ["31/03", "R$ 168.000", "1,9%", "—", "—", "mês fraco (visitas −50%)"],
    ["16/04", "R$ 235.000", "2,3%", "70 mil", "R$ 146", "reabastecendo; 7d +70%"],
    ["26/05", "R$ 734.000", "1,7%", "256 mil", "R$ 166", "+61% — rumo ao milhão"],
    ["03/06", "R$ 706.000", "1,8%", "—", "R$ 163", "consolidando"],
    ["18/06", "R$ 772.000", "—", "—", "—", "exposição em recuperação"],
    ["24/06", "R$ 813.000", "1,9%", "—", "R$ 163", "\"800k mesmo no caos\""],
])
d.p("Leitura: o salto veio de volume e tráfego (visitas subiram de ~70 mil para 256 mil/mês) somados "
    "à Shopee (que fechou meses de R$ 460–530 mil). A conversão % do Meli caiu (de 2,9% para 1,7–1,9%) "
    "à medida que o volume/visitas cresceram — ponto a monitorar. O consultor Anderson resumiu o motor "
    "em uma frase do aluno: \"se não fosse o Ads a gente não ia chegar nesse faturamento.\"")

# ---------- 2. Jornada ----------
d.h1("2. A jornada do cliente no CRM")
d.p("Diferente do Limendes, aqui há um único negócio (ainda não houve recompra). É um contrato grande "
    "e diferenciado, com renovação já prevista para quando o contrato expira.")
d.tabela(["Negócio", "Quando", "Produto", "Valor", "Status"], [
    ["74172", "jan/2026", "Consultoria Tração (12 enc.) + 4 extras — proposta especial", "R$ 41.000", "Ganho"],
    ["Renovação", "prevista fev/2027", "Contato de renovação — contrato expirado (tarefa criada)", "—", "Em aberto"],
])
d.p("Nota comercial (closer Matheus): \"proposta diferente do padrão\" — fechada em ligação com o Thiago, "
    "incluindo 2 encontros estratégicos direto com o Thiago Franco e a solução do bloqueio de marcas de "
    "tênis na Shopee por questão de NF.")

# ---------- 3. Discovery ----------
d.h1("3. O que o cliente queria (discovery)")
d.tabela(["Item", "O que foi registrado"], [
    ["Objetivo declarado", "Escalar os marketplaces (já faturava ~R$ 500 mil/mês) e destravar problemas operacionais (NF/marcas na Shopee, sistema único)"],
    ["Situação de entrada", "20 lojas físicas no RJ há +20 anos; forte no físico, estruturando o digital com gestão nova"],
    ["Faturamento de entrada", "R$ 260.953 (marketplaces, base fev/2026)"],
    ["Dor principal", "Ruptura de estoque, integração de sistema (Olist) e margem apertada limitando campanhas"],
    ["Objetivo / Principal Dor (campos CRM)", "Não preenchidos no Pipedrive — inferidos das notas e transcrições"],
    ["\"O que precisa p/ ficar feliz\"", "Não preenchido no Pipedrive (campo em branco)"],
    ["NPS / CSAT", "Pesquisas enviadas (atividades no CRM), mas os valores não estão preenchidos no Pipedrive"],
])

# ---------- 4. Dentro dos encontros ----------
d.h1("4. Dentro dos encontros — método aplicado")
d.p("Base: notas de acompanhamento do buddy (Luis Castagne) + as 20 transcrições. O método é o mesmo "
    "playbook de tração, aplicado sobre uma operação grande e cheia de solavancos de estoque.")
d.tabela(["Encontro", "Tema / dor trabalhada", "Principais ações / estratégia"], [
    ["10/02", "SWOT e diagnóstico do ML", "Rotina de métricas (reputação/selo Full); Clássico<R$70 vs Premium>R$140; entrar em TODAS as campanhas/rebates; duplicar top-10 anúncios (EAN novo, +preço, novas palavras-chave)"],
    ["24/02", "Relâmpago + estruturar Shopee", "Relâmpago em todos os horários com os 20 principais MLB; 3 cupons Shopee/dia; Programa de Afiliados Shopee (10%); lives"],
    ["03/03", "Curva ABC + Mercado Turbo", "Assinou Mercado Turbo; curva ABC por MLB; Full A=120%/B=100%/C sob demanda; Ads por curva (ROAS A=10, B=6, C agressivo)"],
    ["10/03", "Rupturas e catálogo", "Produto novo direto na relâmpago; palavras-chave genéricas no Modelo; cortar anúncio que gasta >R$25 sem retorno"],
    ["17/03", "Coleta e margem", "Duplicar curva A com preço alto p/ entrar na relâmpago sem histórico; preço de atacado p/ nota de qualidade ≥70; personalizar a página"],
    ["24/03", "Vendedor Indicado (Shopee)", "Full por curva A/MLB; braço de finanças (venda líquida por anúncio); ajuste de preço gradual (R$3–5/semana)"],
    ["31/03", "Mês fraco — diagnóstico", "Aula comparando abas: queda = 100% visitas = ruptura de estoque; decisão de investir ~R$40 mil no ecossistema WMS (Uzzy/OMIE)"],
    ["07/04", "Recuperação + catálogo", "Quebrar envios p/ ter mais anúncios com estoque no Full; campanha de \"vazão Full\" (ROAS 6–7); como migrar p/ catálogo"],
    ["16/04", "Otimização de Ads", "Campanha \"fora de curva\" p/ isolar anúncio de ACOS alto; escalar orçamento ~+20% do gasto médio; subir ROAS 1 ponto por vez"],
    ["21/04", "Ads da Shopee por curva", "Planilha de curva do Anderson (export → A/B/C automático); campanha só de catálogo (ROAS 15)"],
    ["28/04", "Crescimento forte", "Escalonar orçamentos; vazão Full; preparar Amazon (subir caro p/ depois promocionar); meta explícita: \"buscar 1 milhão\""],
    ["19/05", "Coleta quebrada", "Técnica do robô do Meli p/ reverter punição de reputação; priorizar curva A mesmo cara; Full A a 120%"],
    ["26/05", "Bateu R$ 1 milhão", "Migrar Olist→Atom; palavras-chave de concorrentes (Nubimetrics); Amazon 100% Full; contratou Maria só p/ anúncios do Meli"],
    ["03/06", "R$ 1,2–1,3M", "Reorganizar curva por MLB no Mercado Turbo (anúncios patrocinados); processo contra o Olist; meta: \"1 milhão só no ML\""],
    ["18/06", "Foco Shopee", "Shopee \"Leve+\" e Combo p/ compensar falta de relâmpago; recurso de penalidade via ChatGPT + comprovante de energia"],
    ["24/06", "R$ 813k \"no caos\"", "Reconstruir anúncio \"morto\"; escalar campanhas fortes +20%; cupons diários Shopee; verificar penalidades (atraso, recorrível)"],
])
d.p("Feedback de saúde (CRM): aluno \"Ativo\". CSAT e NPS foram enviados, mas os valores não estão "
    "preenchidos no Pipedrive.", italico=True)

# ---------- 5. Análise das transcrições ----------
d.h1("5. Análise das transcrições — as falas reais")
d.p("As 20 transcrições confirmam e aprofundam o método. Observação técnica: quem conduz quase todas "
    "as reuniões é a gerente Lívia (o dono, Raphael, quase não aparece na chamada). A trilha destes "
    "arquivos é Mercado Livre + Shopee; a trilha de TikTok corre em separado (com o João e a Maria) e "
    "não está neste pacote. Três arquivos vieram vazios/ilegíveis (05/05, 02/06, 01/07).")

d.h2("Motor do crescimento (o que puxou de R$ 260k para R$ 1M+)")
for b in [
    "Relâmpago + cupons diários industrializados nas duas plataformas — a alavanca nº 1 de conversão (20 principais MLB em todos os horários; 3 cupons Shopee todo dia, \"um centavo a menos\").",
    "Curva ABC via Mercado Turbo governando Full (A=120%, B=100%, C sob demanda) e a estrutura de Ads (campanhas A/B/C + \"fora de curva\" + \"vazão Full\"), com escala disciplinada (~+20% do gasto médio) e ROAS ajustado \"1 ponto por vez\".",
    "Ads/ACOS muito eficientes: o ACOS caiu de ~11% (início) para ~2% do faturamento no ML, sustentando o orgânico.",
    "Programa de Afiliados da Shopee (comissão 10%) como canal de altíssimo ROI (12× → 22×).",
    "Participar de TODAS as campanhas/rebates do ML + selo \"Vendedor Indicado\" na Shopee (envios aos sábados + tempo de resposta) e recuperação recorrente do Mercado Líder Platinum.",
]:
    d.bullet(b)

d.h2("Dores técnicas recorrentes do aluno")
for b in [
    "Ruptura de estoque crônica (marcas de edição limitada, ex. Via Marte, que não repõem) — apontada pelo consultor como a causa nº 1 das quedas de faturamento (via queda de visitas).",
    "Bug de integração do ERP (Olist/Tiny): vendas com estoque zerado e reservas fantasmas → dezenas de envios atrasados e reclamações (virou processo judicial contra o Olist).",
    "Coleta do Mercado Livre falhando → reputação punida e perda do selo.",
    "Margem baixa limitando entrada em relâmpago/campanhas.",
    "Mão de obra escassa na região (Teresópolis/Serra) e financeiro \"no escuro\" (pouca herança da gestão anterior).",
]:
    d.bullet(b)

d.h2("Momentos de virada ligados aos saltos")
for b in [
    "Fev: reverter despacho em atraso de 200+ itens → recupera o selo → base da retomada.",
    "03/03: Mercado Turbo + Curva ABC + Ads por curva → o método que sustentou a escala.",
    "24/03: vira \"Vendedor Indicado\" na Shopee.",
    "Abr: reabastecimento pós-ruptura → 7 dias saltam +70% / +345% vs. base; \"buscar 1 milhão\".",
    "26/05: R$ 1 milhão atingido (≈ R$ 600k ML + R$ 400k Shopee); contrata a Maria; foco vira \"manter/estruturar\".",
    "Jun: consolida em ~R$ 1,2–1,3M apesar do caos de estoque/sistema.",
]:
    d.bullet(b)

d.h2("Citações marcantes")
for c in [
    "(10/02) \"todos os anúncios que forem possíveis de participar das campanhas, a gente vai estar entrando... a gente vai estar em todas.\"",
    "(31/03) \"tá muito claro que essa perda de faturamento tá vindo pelas visitas... a gente perdeu muita visita por quebra de estoque.\"",
    "(26/05) \"a gente vai ter um milhão... 400 na Shopee e 600 no Mercado Livre.\"",
    "(26/05) \"se a gente chegou no milhão na bagunça, a gente sobe desse milhão aí.\"",
    "(24/06) \"se não fosse o Ads a gente não ia chegar nesse faturamento.\" — \"800k mesmo no caos.\"",
]:
    d.bullet(c)

# ---------- 6. Síntese ----------
d.h1("6. Síntese — o que fez o Ultra Online dar certo")
d.p("Motor do crescimento: relâmpago/cupons industrializados + Curva ABC (Mercado Turbo) governando "
    "Full e Ads + Afiliados Shopee, tudo com ACOS baixíssimo. Isso puxou visitas e volume nas duas "
    "plataformas até passar de R$ 1 milhão/mês.")
d.p("Método replicável: é o mesmo playbook de tração do Limendes (curva A/B/C, ACOS objetivo, "
    "otimização contínua, disciplina de métricas), agora provado numa operação grande e caótica — "
    "o que reforça que o padrão escala.")
d.p("Ponto de atenção nº 1: a operação cresceu apesar de rupturas de estoque e bug de ERP graves. "
    "Resolver estoque/sistema (migração p/ Atom) é o que sustenta e destrava o próximo degrau. "
    "A conversão % do ML caiu com o volume — vale investigar.")
d.p("Frentes em aberto: TikTok (trilha separada, fraca), Amazon (criada mas nunca operada), saldo "
    "Shopee bloqueado (~R$ 90 mil por divergência de nome PJ) e penalidades recorrentes de envio.")

# ---------- 7. Recomendações ----------
d.h1("7. Recomendações para o time")
for b in [
    "Tratar estoque/ERP como projeto nº 1: concluir a migração p/ Atom e a rotina de reposição por curva — é o teto atual do crescimento.",
    "Destravar Amazon (100% Full, começando pela curva A) — é faturamento parado há 5 meses.",
    "Preencher no Pipedrive os campos de discovery, NPS/CSAT e \"o que precisa p/ ficar feliz\" — hoje em branco, empobrecem o acompanhamento e o próximo upsell.",
    "Antecipar a conversa de renovação (contrato expira fev/2027): o resultado (+293%, R$ 1 mi) já é o argumento — mirar recompra maior, como no Limendes.",
    "Monitorar a queda de conversão % do ML conforme o volume cresce (fotos/quebra de objeção/preço competitivo).",
]:
    d.bullet(b)

d.p("")
d.p("Documento gerado a partir do cruzamento entre o CRM (Pipedrive: deal, jornada, notas e atividades) "
    "e as 20 transcrições dos encontros. Campos ausentes no CRM foram marcados como \"não preenchido no "
    "Pipedrive\".", italico=True)

caminho = d.salvar(SAIDA)
print("OK:", caminho)
