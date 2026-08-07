#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Monta o dossie do Limendes Calcados (Tracao 27877 + MELI 52256) em .docx."""
import sys
sys.path.insert(0, "/home/user/bot-webhook-ml/analise_consultorias")
from gerar_docx import Dossie

SAIDA = "/tmp/claude-0/-home-user-bot-webhook-ml/9065417a-c5bc-546a-a83d-9f9832c88261/scratchpad/Dossie_Limendes_Calcados.docx"

d = Dossie("DOSSIÊ DE CONSULTORIA — Limendes Calçados (Aurélio)",
           "Análise de Consultorias · ICOMM / TF Treinamentos  ·  deals 27877 (Tração) + 52256 (MELI)")

d.kpis([
    ("Faturamento inicial", "R$ 40.328", "abr/2025 · base da Tração"),
    ("Faturamento atual", "R$ 360.328", "registro do Pipedrive (ML + Shopee)"),
    ("Crescimento", "+793%", "≈ 8,9× · 2 consultorias"),
])

# ---------- Cabeçalho ----------
d.tabela(["Campo", "Informação"], [
    ["Organização / Loja", "Limendes Calçados Ltda · loja física de calçados no interior de SP (~16 anos, desde 2009)"],
    ["Contato", "Aurélio (dono) · participação da esposa Eliana (MELI) e de Wesley + Daiane (Tração)"],
    ["Nicho / perfil", "Calçados · loja física madura migrando para o digital"],
    ["Canais", "Mercado Livre (principal) + Shopee (aberta durante a MELI, dez/2025)"],
    ["Consultor / Buddy", "Aurélio (Lucas Gobor)"],
    ["Produtos contratados", "1) Consultoria Tração (6 encontros, abr–jun/2025) · 2) Consultoria MELI (recompra/expansão, 14 encontros, out/2025–jan/2026)"],
    ["Regime fiscal", "Simples Nacional (migração p/ Lucro Real avaliada, adiada p/ 2026)"],
    ["Ferramentas prescritas", "Mercado Turbo (financeiro / curva ABC) · Shopping de Preços (concorrência) · EconPrecifique (precificação)"],
    ["Jornada no CRM (notas, saúde, NPS/CSAT)", "Não preenchido no Pipedrive (dossiê montado sobre as 19 transcrições + números-chave do deal)"],
])

# ---------- 1. Resultado ----------
d.h1("1. Resultado — o \"deu certo\"")
d.p("O Limendes é um case de recompra: fez a Consultoria Tração (6 encontros, abr–jun/2025) e, "
    "satisfeito, recomprou a Consultoria MELI (out/2025–jan/2026) para aprofundar publicidade e abrir a "
    "Shopee. No registro do Pipedrive, o faturamento saiu de R$ 40.328 para R$ 360.328 (+793%).")
d.p("Ressalva de transparência: a cifra de R$ 360.328 (+793%) é o valor consolidado no CRM. Nas falas "
    "das reuniões, a trajetória documentada de \"últimos 30 dias\" vai de ~R$ 37 mil (abr/2025) a "
    "~R$ 257 mil no Mercado Livre (pico em 26/12) somados a ~R$ 33 mil de Shopee — ou seja, o número do "
    "CRM inclui canais/mês além do que aparece isolado numa única fala. A tendência, porém, é a mesma: "
    "crescimento forte e consistente ao longo das duas consultorias.", italico=True)

d.h2("De onde veio o crescimento (fotografias de 30 dias ditas nos encontros)")
d.p("Os números abaixo são \"últimos 30 dias\" citados no início de cada encontro (não o total "
    "consolidado). Mostram os dois blocos: a decolagem na Tração e a escala rentável na MELI.", italico=True)
d.tabela(["Encontro", "Fat. 30d", "Var.", "Publicidade / ACOS / leitura"], [
    ["08/04/25 · Tração E1", "R$ 37.287", "—", "1,4% conv · ticket R$ 137 · ACOS 19,07% (base)"],
    ["22/04/25 · E2", "R$ 30.560", "−44,6%", "queda ao desligar ADS p/ reestruturar"],
    ["06/05/25 · E3", "R$ 44.779", "+14%", "ACOS caindo (~9–10%)"],
    ["20/05/25 · E4", "R$ 68.407", "+118%", "vendas publi 30d R$ 47 mil (+244%)"],
    ["03/06/25 · E5", "R$ 99.189", "+154%", "publi R$ 74 mil dos R$ 99 mil (+286%)"],
    ["17/06/25 · E6 (últ.)", "R$ 109.769", "+72,5%", "período Tração: +87,7% geral / +179% publicidade"],
    ["15/10/25 · MELI E1", "R$ 188.000", "—", "945 un · ticket R$ 200 · ACOS 20,15% · invest. R$ 25 mil"],
    ["23/10/25 · E2", "R$ 201.073", "+45,3%", "realocação em 4 campanhas (curva ABC)"],
    ["05/11/25 · E3", "R$ 233.820", "+66,1%", "publicidade R$ 157.888 (+62,4%)"],
    ["12/11/25 · E4", "R$ 197.975", "+8,8%", "conversão publi 2,2 (recorde) · ACOS 7% em 7d"],
    ["26/12/25 · E10", "R$ 256.654", "+42,1%", "pico documentado · + Shopee ~R$ 33 mil"],
    ["14/01/26 · E12", "R$ 220.054", "+7,2%", "ACOS 8,21% (7d) · pontuação full 35→66"],
    ["21/01/26 · E13 (últ.)", "R$ 197.382", "−21%", "período MELI: +41% · ACOS ~11,4%"],
])
d.p("Leitura: na Tração, a alavanca foi a reestruturação da publicidade por curva ABC (de R$ 30 mil "
    "para ~R$ 100 mil em ~2 meses). Na MELI, a virada foi de eficiência: manter o faturamento alto "
    "derrubando o ACOS de ~20% para 8–11% (o orgânico assumindo) — de \"faturar sem caixa\" para "
    "operação rentável. Marco: em out/25 gastava R$ 25 mil de ADS (ACOS 20%) p/ ~R$ 188 mil; em jan/26, "
    "R$ 14.854 de ADS (ACOS 11,3%) com o resto vindo do orgânico.")

# ---------- 2. Jornada ----------
d.h1("2. A jornada do cliente — duas consultorias")
d.p("Case clássico de recompra por satisfação e por feedback bem aproveitado. É a mesma dinâmica citada "
    "na análise geral: o cliente disse que \"6 encontros é pouco\" e a ICOMM ofereceu a expansão natural.")
d.tabela(["Negócio", "Quando", "Produto", "Motivação", "Status"], [
    ["27877", "abr–jun/2025", "Consultoria Tração (6 encontros)", "Profissionalizar a operação no ML (entraram \"por brincadeira\")", "Concluída"],
    ["52256", "out/2025–jan/2026", "Consultoria MELI (14 encontros)", "Aprofundar ADS/ROAS + abrir Shopee", "Concluída"],
])
d.p("Gatilho da recompra (o cliente, 17/06): \"Eu achei que ia ter mais encontros. Seis encontros era um "
    "pouco... de oito a dez ajudava bastante.\" A MELI veio com 14 encontros — exatamente a ampliação "
    "sugerida. Motivo declarado (05/11): \"Eu tinha pego muito ainda essa parte do ADES... por isso que a "
    "gente optou de novo em fazer consultoria pra aprender mais.\"", italico=True)

# ---------- 3. Discovery ----------
d.h1("3. O que o cliente queria (discovery)")
d.tabela(["Item", "O que foi registrado (Tração E1, 08/04)"], [
    ["Objetivo declarado", "\"Vamos se tornar profissional vendendo no Mercado Livre\" — entender e-commerce, publicidade, gestão e criação de anúncios"],
    ["Postura de entrada", "Aprender antes de escalar: \"Tô nem muito preocupado com vender bastante... vamos aprender primeiro pra depois começar a vender\""],
    ["Situação da conta", "62 anúncios (22 inativos, 40 ativos) · conversão 1,4% · ACOS 19% · ticket R$ 137,10"],
    ["Estrutura", "Sem ERP dedicado (emitiam nota pelo próprio ML) · sem ferramenta de análise de mercado"],
    ["Dor central", "Operação cresceu sem controle: \"o patrimônio tá aumentando e a gente tá meio perdido... não estamos conseguindo administrar\""],
    ["Interesse futuro", "Expandir para Shopee (concretizado na MELI)"],
    ["Objetivo / Dor principal (campos CRM)", "Não preenchido no Pipedrive — inferidos das transcrições"],
    ["NPS / CSAT", "Não preenchido no Pipedrive"],
])

# ---------- 4. Dentro dos encontros ----------
d.h1("4. Dentro dos encontros — método aplicado")
d.p("Base: as 19 transcrições (6 da Tração, 13 da MELI). É o mesmo playbook de tração dos demais alunos "
    "(diagnóstico → curva ABC → publicidade por curva → full → precificação → gestão), aqui aplicado em "
    "duas ondas.")
d.h2("Consultoria Tração (abr–jun/2025)")
d.tabela(["Encontro", "Tema / dor", "Principais ações / estratégia"], [
    ["08/04", "Diagnóstico + SWOT", "Contratar Mercado Turbo e Shopping de Preços; excluir anúncios inativos (efeito âncora); qualidade ~100%; central de promoção em 100% dos anúncios; rotina diária de estoque no full; planilha de KPIs"],
    ["22/04", "Financeiro + campanhas", "Custo/imposto no Mercado Turbo (margem de contribuição); curva ABC por MLB; reestruturar publicidade em 4 campanhas (A / A-fim / B / C); custo por clique por faixa"],
    ["06/05", "Jornada de compra + mercado", "Fotos, vídeo/clipe, foto ambientada, quebra de objeção; Shopping de Preços (market share, favoritar concorrentes)"],
    ["20/05", "Otimização de publicidade", "ACOS × TACOS; perdido por orçamento/classificação; otimizar a cada 7 dias; campanha de \"sem vendas\" e incubadora"],
    ["03/06", "Anúncio de alta performance + full", "Estruturação da jornada; envio ao full com grade completa; regra \"no máx. 20% acima do vendido nos 30 dias\""],
    ["17/06", "Gestão / fechamento", "DRE, custo fixo diluído, ponto de equilíbrio, balanço; foco: \"crescer saudável\""],
])
d.h2("Consultoria MELI (out/2025–jan/2026)")
d.tabela(["Encontro", "Tema / dor", "Principais ações / estratégia"], [
    ["15/10", "Diagnóstico da recompra", "ACOS 20% alto; migração ACOS→ROAS; transição MLB→MLBU; Minha Página + canal + cupom seguidores; pausar anúncio sem estoque/variação furada"],
    ["23/10", "Realocação", "Tabela conversora ACOS↔ROAS; realocação em 4 campanhas curva ABC (~R$ 18 mil); resumo financeiro no Mercado Turbo"],
    ["05/11", "Precificação + otimização", "Clássico × prêmio; frete grátis abaixo de R$ 79; planilha EconPrecifique; incubadora; ruptura de estoque × Shopping de Preços"],
    ["12/11", "Otimização + full + reputação", "Brand/Display Ads (ainda não); pontuação do full e tempo de estoque; carrinho abandonado (1.602); Simples × lucro real"],
    ["19/11", "Análise de queda", "Comparar períodos no Mercado Turbo p/ achar anúncio em queda; Minha Página; carrinho abandonado; afiliados 6%"],
    ["26/11", "Nova realocação", "6 campanhas curva ABC; loja oficial (registro de marca); métricas de afiliados; oferta de ticket alto no full; menção a TikTok Shop"],
    ["03/12", "Revisão + início Shopee", "Passo-a-passo ACOS/ROAS; abertura da Shopee (informações gerenciais, assistente de vendas, descontos, afiliados)"],
    ["10/12", "Shopee Ads + processos", "Campanha unitária no Shopee; regimento interno / prioridades da equipe (7 pessoas); curva ABC Shopee"],
    ["17/12", "Otimização Meli + Shopee", "Otimização por impressões/cliques; oferta relâmpago; desconto"],
    ["26/12", "Otimização (pico R$ 256 mil)", "Incubadora; subir ROAS no Shopee; oferta relâmpago; pôr anúncio parado em campanha (deu certo)"],
    ["07/01", "Pós-ano-novo", "Erro de orçamento (R$ 10 em vez de R$ 100); Shopee ticket alto >R$ 500 (comissão travada)"],
    ["14/01", "Otimização + full", "Nova aba \"Anúncios\" (queda de visitas/vendas); full 35→66; loja oficial; penalidade Shopee por atraso"],
    ["21/01", "Fechamento", "Prints set/25→jan/26; +41% no período; realocar Shopee; registro de marca pendente"],
])

# ---------- 5. Análise das transcrições ----------
d.h1("5. Análise das transcrições — as falas reais")
d.p("As 19 transcrições confirmam o método e mostram a evolução do próprio dono, que ao final já conduzia "
    "sozinho a otimização (\"agora peguei o jeito\").")

d.h2("Motor do crescimento")
for b in [
    "Reestruturação da publicidade por curva ABC (Tração, 22/04) — a alavanca que destravou o salto de R$ 30 mil para ~R$ 100 mil em ~2 meses.",
    "Qualidade/relevância dos anúncios + IA de fotos do ML + full com grade completa — apontados como motor do salto para R$ 188 mil no início da MELI.",
    "Migração ACOS → ROAS e redução da agressividade do ADS: o orgânico assumiu, o TACOS caiu e o ACOS foi de ~20% para 8–11% mantendo o faturamento — virada de rentabilidade.",
    "Central de promoção, frete grátis abaixo de R$ 79, recuperação de carrinho abandonado (1.602) e afiliados — alavancas de conversão somadas na MELI.",
    "Expansão de canal (Shopee, dez/25) e de mix (chinelos/sandálias sazonais, ticket alto no Shopee) ampliando o funil.",
]:
    d.bullet(b)

d.h2("Dores técnicas recorrentes do aluno")
for b in [
    "Ruptura de estoque / grade de variação furada (dor nº 1 da MELI): dependência de distribuidores e fábricas que não repõem. Consultor: \"não deixa esse cara faltar variação... é um câncer pra publicidade.\"",
    "ACOS/ADS alto e falta de domínio de otimização — seguia as sugestões automáticas do ML, \"colocava grana na frente\".",
    "Estoque full: pontuação de qualidade baixa (35→66), tempo de armazenamento e espaço limitado.",
    "Curva ABC muda muito mês a mês — exige realocação a cada ~30–60 dias.",
    "Precificação/margem (clássico × prêmio, margem ~10–12%) e o EconPrecifique postergado por semanas.",
    "ERP/custos: usava o emissor do ML; custo e imposto não preenchidos no Mercado Turbo.",
    "Gestão de equipe (prioridades: vendas → estoque → anúncios) e questão tributária (Simples × lucro real).",
]:
    d.bullet(b)

d.h2("Momentos de virada ligados aos saltos")
for b in [
    "22/04 (Tração): reestruturação da publicidade por curva ABC — de R$ 30 mil para ~R$ 100 mil em ~2 meses.",
    "15/10 (MELI): relevância dos anúncios + IA de fotos + full com grade completa → salto para R$ 188 mil.",
    "out→jan: migração para ROAS + redução do ADS → ACOS de ~20% para 8–11% mantendo o faturamento (rentabilidade).",
    "dez/25: abertura da Shopee e mix de verão (chinelos/sandálias) ampliando o volume.",
    "26/12: pico documentado de R$ 256.654 no ML + ~R$ 33 mil de Shopee.",
]:
    d.bullet(b)

d.h2("Citações marcantes")
for c in [
    "(08/04) \"Entramos assim por brincadeira... o patrimônio tá aumentando e a gente tá meio perdido. Não estamos conseguindo administrar isso daí.\" — Aurélio",
    "(08/04) \"Vamos se tornar profissional vendendo no Mercado Livre.\"",
    "(22/04) \"Tô nem muito preocupado com vender bastante... vamos aprender primeiro pra depois começar a vender.\"",
    "(03/06) \"A gente saiu de 30 para 100. Em quê? Em um mês, dois meses.\"",
    "(17/06) \"Eu achei que ia ter mais encontros. Seis encontros era um pouco... de oito a dez ajudava bastante.\"",
    "(05/11) \"O faturamento veio, só que o investimento foi muito alto... estava colocando grana na frente para fazer a venda.\"",
    "(14/01) \"Graças a vocês aí, a gente aprendeu.\"",
    "(21/01) \"Esse mês de janeiro que está começando vai ser recorde de faturamento ali da empresa.\"",
    "(26/11) \"Esse negócio de trabalhar com estoque não é fácil não, quando a gente não é produtor nem fabricante.\" — Lucas",
]:
    d.bullet(c)

# ---------- 6. Síntese ----------
d.h1("6. Síntese — o que fez o Limendes dar certo")
d.p("Disposição do dono em aprender antes de escalar + execução consistente das ações (limpeza de "
    "anúncios, curva ABC, central de promoção, full com grade completa). Na Tração, a alavanca foi a "
    "publicidade por curva ABC; na recompra (MELI), a virada de mentalidade de \"faturamento a qualquer "
    "custo\" para rentabilidade (ROAS/TACOS, ACOS de 20% para 8–11%).")
d.p("A base física madura (16 anos) deu fôlego de caixa para aguentar o crescimento (30 → 100 → ~250 mil) "
    "sem quebrar, e o cliente passou a separar a operação online da física.")
d.p("Método replicável e internalizado: rotina de otimização a cada 7 dias + realocação de curva a cada "
    "~30–60 dias — ao final, o próprio Aurélio conduzia a otimização. É o mesmo playbook do Ultra Online "
    "(Raphael), aqui em versão \"do zero ao profissional\".")
d.p("Frentes em aberto ao final (21/01): ruptura de estoque / grade furada (gargalo dependente de "
    "distribuidores); loja oficial / registro de marca no ML (pendente); penalidade de atraso na Shopee; "
    "realocação de curva ABC e cadastro de anúncios na Shopee (conta ainda \"nas escuras\"); EconPrecifique "
    "e preenchimento de custos no Mercado Turbo sempre postergados; migração tributária (Simples → lucro "
    "real) adiada para 2026.")

# ---------- 7. Recomendações ----------
d.h1("7. Recomendações para o time")
for b in [
    "Atacar a ruptura de estoque como projeto nº 1: a programação de compras jan–mar/26 (full 940 → 1.600 → 1.800 un) precisa virar rotina — é o teto atual do crescimento.",
    "Estruturar a Shopee de verdade (realocação de curva ABC + cadastro de anúncios + Ads) — canal aberto mas ainda subaproveitado.",
    "Concluir a loja oficial / registro de marca no Mercado Livre (pendência arrastada).",
    "Implementar de fato a precificação (EconPrecifique) e preencher custos/impostos no Mercado Turbo para enxergar a margem real.",
    "Preencher no Pipedrive os campos de discovery, jornada e NPS/CSAT — hoje em branco, empobrecem o acompanhamento e o próximo upsell.",
    "Explorar a 3ª recompra: o histórico de recompra e o resultado (+793% no CRM) já são o argumento — mirar novo canal (TikTok Shop, citado) ou aprofundar Shopee.",
]:
    d.bullet(b)

d.p("")
d.p("Documento gerado a partir do cruzamento entre o CRM (Pipedrive: deals 27877 e 52256 + números-chave) "
    "e as 19 transcrições dos encontros das duas consultorias. Campos ausentes no CRM foram marcados como "
    "\"não preenchido no Pipedrive\". A cifra de R$ 360.328 (+793%) é o registro consolidado do CRM; a "
    "trajetória documentada nas falas está detalhada na seção 1.", italico=True)

caminho = d.salvar(SAIDA)
print("OK:", caminho)
