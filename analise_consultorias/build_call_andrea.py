#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "/home/user/bot-webhook-ml/analise_consultorias")
from gerar_docx import Dossie
SAIDA = "/tmp/claude-0/-home-user-bot-webhook-ml/9065417a-c5bc-546a-a83d-9f9832c88261/scratchpad/Analise_Call_Renato_DEU_CERTO_Andrea.docx"

d = Dossie("Análise de Call — Reunião que DEU CERTO",
           "Closer Renato Benedetti · Projeto Análise de Closers")
d.kpis([
    ("Desfecho", "✓ VENDEU", "R$ 15.997 (confirmado no Pipedrive)"),
    ("Nota da call", "8,7 / 10", "aderência 11/11 ao playbook"),
    ("Fidelidade SDR", "Alta", "Leticia entregou lead A aderente"),
])

d.tabela(["Campo", "Informação"], [
    ["Closer", "Renato Benedetti"],
    ["Lead / Empresa", "Andrea Assalve (mãe, ex-bancária) + Thiago (filho, opera a conta) — Celebre Store"],
    ["Nicho", "Eletrônicos com marca própria (catálogo protegido BPP, classe 9 INPI) · 3 contas no ML"],
    ["Produto fechado", "Consultoria Tração (6 encontros) — Carteira Prime, consultor nível 4"],
    ["Data da reunião", "06/08/2026"],
    ["Duração", "~108 min (1:48)"],
    ["Código da call", "apa-ydje-tnu"],
    ["Desfecho na call", "Pagamento no cartão (PF) confirmado + grupo WhatsApp + onboarding para o dia seguinte"],
    ["Status no Pipedrive", "GANHO — R$ 15.997 (8x de R$ 1.999,62) · deal 115090"],
    ["SDR / Buddy", "SDR: Leticia · Buddy/CS: Allana Bueno"],
    ["Talk-ratio (estimativa)", "≈ Closer 60% × Lead 40% — estimativa por leitura (sem diarização automática)"],
])

d.h1("Resumo executivo")
d.p("Clássico de descoberta bem feita. O lead chegou convicto de que o problema era só ADS (\"o Edis "
    "come tudo\"): 70% das vendas via ADS, TACOS 10,9%, R$ 38 mil/mês investidos, margem 19–20%. O Renato "
    "ampliou a dor — mostrou que o problema real é falta de visão de dados de mercado (market share, teto "
    "de demanda) —, quantificou o prejuízo (~R$ 100 mil jogados fora em 4–5 meses), ancorou no custo de "
    "oportunidade com cases da mesma categoria e contornou uma objeção real de orçamento (o cliente falou "
    "R$ 7–9 mil; fechou R$ 15.997 em 8x). Saiu com pagamento confirmado e onboarding datado. Venda "
    "confirmada no pipe.")

d.h1("1. O que deu certo")
d.p("Descoberta que reenquadra a dor (o ponto alto da call):", italico=False)
d.bullet("\"Lembra que lá no comecinho você falou que o seu único problema era Edis? Tá começando a ficar claro pra você que não é só sobre Edis?\" — abriu a visão de market share/demanda.")
d.bullet("\"Adianta você ter visibilidade sem ter um anúncio 100% preparado pra converter?\" / \"Se o produto atingiu o teto, você pode colocar 5 milhões que não aumenta a demanda.\"")
d.p("Quantificação da dor:")
d.bullet("Fez o próprio cliente chegar em \"uns 20, 25 mil por mês\" desperdiçados → \"mais ou menos 100k foi jogado fora, vai\" (e o cliente confirmou).")
d.p("Prova social por categoria (a marca do Renato):")
d.bullet("Empower: entrou faturando R$ 38 mi/mês → quase R$ 50 mi em 3 meses; +R$ 60 mil no caixa em economia de ADS. Ecossistema Thiago Franco (WEG, Next10/Neymar, G4).")
d.bullet("Diretório de cases de eletrônicos ao vivo: \"um cara que começa com 360 e em 3 meses vai pra 800\" — \"esse seria vocês\".")
d.p("Fechamento com próximo passo concreto:")
d.bullet("Pediu o compromisso (\"de 0 a 10, quão engajados vocês estão?\" → \"dez, quinze, vinte\"), gerou o link, preencheu o cadastro, confirmou o pagamento e já criou o grupo e agendou o onboarding.")

d.h1("2. Por que essa deu certo")
d.p("Três coisas se somaram: (a) a descoberta ampliou a dor para além do ADS, justificando a consultoria "
    "completa em vez de um \"remendo\" barato; (b) a prova social por nicho tornou o resultado crível "
    "(\"esse seria vocês\"); (c) o custo de oportunidade (R$ 100 mil desperdiçados + o que deixaram de "
    "crescer) fez o preço parecer pequeno diante do problema. Com isso, mesmo com o dobro do orçamento "
    "informado, o cliente fechou.")

d.h1("3. Usou bônus como quebra de objeção?")
d.p("Pouco. O peso ficou na prova social e no custo de oportunidade. Para o preço, usou desconto "
    "(à vista Pix até 10%; \"fechamento\" 15% → R$ 13.597) — mas o cliente optou pelo cartão em 8x. "
    "Padronizar um bônus de fechamento (ex.: encontro extra / diagnóstico prioritário) poderia ter "
    "reduzido a fricção do gap de preço sem precisar dar desconto.")

d.h1("4. Fez o lead entender o valor? (preço deixou de ser impeditivo?)")
d.p("Sim. O preço foi apresentado depois de toda a construção de valor e do custo de oportunidade. "
    "Quando surgiu o gap (\"eu falei em sete, oito, nove, aí você me vem com quinze, o dobro\"), o Renato "
    "não brigou por preço — voltou aos cases da categoria e ao \"bolso que vocês terão com a "
    "consultoria\". O preço virou escolha de forma de pagamento (cartão 8x), não um \"não\".")

d.h1("5. Maiores objeções do cliente")
d.bullet("**Orçamento (a principal):** \"vendendo a janta pra pagar o almoço\"; limite de cartão ~R$ 7–9 mil; pediram algo mais barato/focado só em ADS. → Renato trouxe o orçamento à tona ANTES do preço (metáfora do restaurante) e depois contornou o gap de 2x com custo de oportunidade + cases + a pausa para o casal decidir.")
d.bullet("**Medo da queda de faturamento ao \"desmamar\" o ADS** (a conta \"viciada\" em diário de R$ 1.000/produto). → Tratado com o consultor nível 4 e o acompanhamento (gerente + grupo), dando a \"palavra de conforto\" que o próprio cliente pediu.")
d.bullet("**\"Vai funcionar pro meu caso?\"** → cases da categoria eletrônicos ao vivo.")

d.h1("6. Tempo e ritmo")
d.p("~108 min — call longa, típica do Renato, que investe em construir valor. Houve uma pausa de ~7 min "
    "(1:28→1:35) para o casal conversar a sós — e voltaram decididos a pagar no cartão. O ritmo foi "
    "consultivo (perguntas → cliente conclui sozinho), o que sustentou o fechamento mesmo com o preço "
    "acima do esperado.")
d.p("Talk-ratio (estimativa por leitura): ≈ Closer 60% × Lead 40%. O Renato fez monólogos longos na "
    "apresentação da metodologia e da prova social, mas abriu bastante espaço para o lead na descoberta. "
    "Referência de venda consultiva: closer ≤ ~50%. Número exato depende da diarização automática (a "
    "configurar).", italico=True)

d.h1("⭐ Nota da call (0–10) por critério")
d.tabela(["Critério", "Nota", "Observação"], [
    ["Rapport / abertura", "9", "Conectou pelo propósito (galpão, empregar, importar)"],
    ["Descoberta / diagnóstico", "10", "SPIN forte; reenquadrou a dor para market share"],
    ["Prova social", "9", "Empower + cases de eletrônicos (\"esse seria vocês\")"],
    ["Ancoragem de valor", "9", "Custo de oportunidade (R$ 100k) > preço"],
    ["Contorno de objeção", "8", "Orçamento 2x contornado; faltou bônus de fechamento"],
    ["Fechamento / próximo passo", "9", "Link, cadastro, pagamento e onboarding datado"],
    ["MÉDIA", "8,7", "Call de alto padrão"],
])

d.h1("✅ Aderência ao playbook de vendas")
d.tabela(["Etapa", "Item", "✓"], [
    ["Abertura", "Rapport / quebra-gelo", "✅"],
    ["Abertura", "Definição de agenda da call", "✅"],
    ["Descoberta", "Diagnóstico da dor antes da solução", "✅"],
    ["Descoberta", "Levantou números (fat., ADS/TACOS, margem)", "✅"],
    ["Descoberta", "Dor quantificada (custo de não resolver)", "✅"],
    ["Valor", "Prova social por nicho", "✅"],
    ["Valor", "Ancoragem de valor (resultado, não preço)", "✅"],
    ["Valor", "Conectou solução → dor específica", "✅"],
    ["Fechamento", "Contorno de objeção", "✅"],
    ["Fechamento", "Pedido de fechamento claro", "✅"],
    ["Fechamento", "Próximo passo datado (onboarding)", "✅"],
])
d.p("Resultado: **11/11**. Único reforço possível: um bônus de fechamento padronizado para o gap de "
    "preço, em vez de recorrer a desconto.", italico=True)

d.h1("🎯 Momento da virada")
d.p("**Estratégico (o que destravou a venda) — ~32–36 min:** quando o Renato faz o Thiago admitir que "
    "\"não é só sobre Edis\" e introduz a visão de market share/demanda (\"vocês sabiam que conseguem ver "
    "o quanto representam do mercado global?\" → \"Não\"). Aí a dor deixou de ser um ajuste barato de ADS "
    "e passou a justificar a consultoria completa.")
d.p("**Comercial — pausa de ~7 min (1:28→1:35):** o casal conversou a sós e voltou com o \"vai ter que "
    "ser feito mesmo, a gente vai pagar no cartão\". A construção anterior segurou a decisão mesmo com o "
    "preço no dobro do orçamento informado.")

d.h1("🔗 Fidelidade SDR → Closer")
d.p("SDR responsável: **Leticia**. O que ela registrou na qualificação × o que apareceu na call:")
d.tabela(["Ponto", "Qualificação (Leticia)", "Na call", "Bate?"], [
    ["Tempo de ML", "3 anos", "3 anos, Platinum", "✅"],
    ["Nicho", "Eletrônicos, revenda + fabricação, marca registrada", "Idem (marca própria, BPP)", "✅"],
    ["Faturamento", "R$ 340–370k/mês", "R$ 300–380k (conta principal)", "✅"],
    ["Investimento ADS", "R$ 30–40k/mês", "R$ 38k/mês", "✅"],
    ["Margem", "23%", "19–20%", "⚠️ leve divergência"],
    ["Origem", "Indicação", "Confiança no Thiago Franco / indicação", "✅"],
    ["Perfil", "Lead A · Score marketplaces 6", "Decisores na call, orçamento apertado", "✅"],
    ["Ponto crítico", "\"Cliente ansioso\"", "Thiago ansioso/agressivo; Andrea equilibra", "✅"],
])
d.p("Veredito: **alta fidelidade**. A Leticia entregou um lead A aderente e com os dados corretos "
    "(só a margem veio um pouco acima do real). O ponto crítico \"cliente ansioso\" se confirmou na call. "
    "Bom handoff SDR → closer — o closer só precisou converter.", italico=True)

d.h1("Lição para replicar")
for b in [
    "Ampliar a dor na descoberta: quando o lead chega com \"o problema é X\", mostrar a camada acima (aqui: de ADS para market share) — foi o que justificou a consultoria completa em vez de um remendo barato.",
    "Quantificar o desperdício pela boca do cliente (\"~R$ 100 mil jogados fora\") — vira a régua contra a qual o preço parece pequeno.",
    "Trazer o orçamento à tona ANTES do preço (metáfora do restaurante) para não apresentar valor no vácuo.",
    "Prova social por categoria do cliente (\"esse case seria vocês\") — ponto forte do Renato, replicável.",
    "Sair da call com o próximo passo executado (cadastro + pagamento + grupo + onboarding datado), não só \"prometido\".",
    "Padronizar um bônus de fechamento para o gap de preço (evita queimar margem com desconto).",
]:
    d.bullet(b)

d.h1("Anexo — Como as notas são calculadas (0 a 10)")
d.p("Regra de ouro: 10 é \"impecável + conduziu com maestria\", não apenas \"fez\". Fez bem, com 1 "
    "detalhe faltando, fica 8–9.")
d.tabela(["Faixa", "Significado"], [
    ["9 – 10  Excelente", "Fez tudo e conduziu com maestria, sem falha"],
    ["7 – 8  Bom", "Fez o essencial bem, com 1 lacuna pequena"],
    ["5 – 6  Regular", "Fez pela metade / de forma superficial"],
    ["0 – 4  Fraco", "Não fez, ou fez de forma errada"],
])
d.tabela(["Critério", "O que exige o 10", "Cai para 7–8 quando"], [
    ["Rapport / abertura", "Cria o vínculo ativamente (pessoal + propósito) e define agenda", "Conecta só pelo profissional, ou quem puxa é o lead"],
    ["Descoberta / diagnóstico", "Puxa a dor antes da solução, levanta números E amplia a dor", "Boa descoberta, mas não amplia/reenquadra a dor"],
    ["Prova social", "Case do mesmo nicho + número + \"esse seria você\"", "Prova social genérica, sem ser da categoria"],
    ["Ancoragem de valor", "Preço vira escolha de pagamento; usa custo de oportunidade", "Vende resultado, mas não quantifica o valor"],
    ["Contorno de objeção", "Antecipa, contorna E confirma que a objeção caiu", "Contorna, mas reativo ou faltou um recurso (ex.: bônus)"],
    ["Fechamento / próximo passo", "Pede a venda E executa o próximo passo na call", "Fecha, mas o próximo passo fica só \"prometido\""],
])
d.p("Nesta call: rapport 9 (conexão mais profissional que pessoal) e contorno 8 (faltou um bônus de "
    "fechamento) — o restante ficou em 9–10. Média 8,7.", italico=True)

d.p("")
d.p("Análise a fundo de call individual, no cruzamento call (fala real) ↔ Pipedrive (deal 115090). "
    "Status confirmado pelo código do Google Meet (apa-ydje-tnu). Complementa o compilado de reuniões e "
    "o Dossiê Executivo do closer.", italico=True)

print("OK:", d.salvar(SAIDA))
