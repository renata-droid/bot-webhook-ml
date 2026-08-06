#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "/home/user/bot-webhook-ml/analise_consultorias")
from gerar_docx import Dossie
SAIDA = "/tmp/claude-0/-home-user-bot-webhook-ml/9065417a-c5bc-546a-a83d-9f9832c88261/scratchpad/Analise_Geral_10_Consultorias.docx"

d = Dossie("ANÁLISE GERAL — 10 Consultorias",
           "Síntese consolidada · ICOMM / TF Treinamentos · cruzamento CRM (Pipedrive) + ~100 transcrições")

d.kpis([
    ("Alunos analisados", "10", "≈ 100 encontros"),
    ("Palavras transcritas", "~735 mil", "≈ 5.600 páginas"),
    ("Playbook", "1 método", "replicável em 5 nichos"),
])

d.h1("1. Panorama dos 10 alunos")
d.tabela(["Aluno / Loja", "Nicho", "Canal", "Consultor", "Inicial → Atual", "Var."], [
    ["Limendes", "Calçados", "ML+Shopee", "Lucas Gobor", "40.328 → 360.328", "+793%"],
    ["Ultra Online (Raphael)", "Calçados", "ML+Shopee+TikTok", "Anderson Volpato", "260.953 → 1.026.854", "+293%"],
    ["Eficácia (Savio)", "Saúde/farmácia", "ML", "Anderson Volpato", "≈0 → 169.529", "do zero"],
    ["ICONNECT (Lucas)", "Atacado multinicho", "5 marketplaces", "Mateus Fogaça", "117.599 → 216.337", "+84%"],
    ["Aster (Daniel)", "Construção", "ML", "Pedro Sousa", "95.000 → 172.884", "+82%"],
    ["Rafha/Inova", "Farmácia/perfumaria", "Shopee+ML", "Mateus Fogaça", "611.437 → n/d", "—"],
    ["Pratik (William)", "Multinicho", "Shopee", "Anderson Volpato", "1.000 → 17.271", "+1625%"],
    ["Rede Clip (Vitor)", "Papelaria", "ML", "Renan Rezende", "≈0 → 12.576", "do zero"],
    ["Habitare (Gabriel)", "Construção", "ML", "Liara Silva", "≈0 → 10.464", "do zero"],
    ["Centermed (Carol)", "Saúde", "ML+Shopee", "Anderson/Mateus*", "n/d", "—"],
])
d.p("*Divergência de registro (ver dossiê da Carol). n/d = não preenchido no Pipedrive. As bases \"≈0\" "
    "são alunos que começaram do zero no marketplace (base inicial não preenchida no CRM).", italico=True)
d.p("Dois recortes claros: (a) contas GRANDES que escalam por estruturação (Ultra R$ 1 mi, Rafha R$ 600 "
    "mil+, ICONNECT, Limendes, Aster, Eficácia); (b) contas PEQUENAS/DO ZERO que constroem a operação "
    "(Pratik, Rede Clip, Habitare). O mesmo método serve aos dois — muda a ênfase.")

d.h1("2. O playbook replicável — o método que se repete em TODOS")
d.p("Independente do nicho (calçados, saúde, construção, papelaria, atacado) e do canal (ML ou Shopee), "
    "o mesmo playbook aparece em todos os dossiês. É o ativo mais valioso do time — um método "
    "institucional, não do consultor individual.")
d.h2("1) Anúncio de alta performance")
for b in [
    "Título = indexação (encher de palavras-chave via Avante Pro/Ubersuggest/Nubimetrics; ML 60 / Shopee 100 caracteres).",
    "Fotos com quebra de objeção (benefício, medidas, material) + clipe/vídeo obrigatório; ficha técnica completa.",
    "Fugir de catálogo com EAN/MPN únicos (protege margem); entrar no catálogo só para herdar histórico inicial.",
]:
    d.bullet(b)
d.h2("2) Pesquisa de mercado antes de cadastrar")
for b in [
    "Shopping de Preços / Avante Pro para escolher categoria válida (≥ R$ 1 mi/mês) e precificar pela média dos ~10 líderes.",
    "Cadastrar primeiro a curva A / top de linha para tracionar rápido (\"assertividade acima de volume\").",
]:
    d.bullet(b)
d.h2("3) Motor promocional (a alavanca nº 1 de conversão)")
for b in [
    "Oferta Relâmpago em TODOS os horários, todo dia, nos 20 principais anúncios (estoque de campanha baixo p/ escassez).",
    "Cupons diários em cascata: loja, produto, ticket (eleva a cesta), seguidores e carrinho abandonado.",
    "Participar de TODAS as campanhas do marketplace (priorizando as com rebate) + campanha base da própria loja.",
    "Precificar +20–30% acima do alvo para viabilizar os descontos; Clássico (<R$ 70/79) vs Premium (parcelado) na mesma opção de venda.",
]:
    d.bullet(b)
d.h2("4) Curva ABC governando Full e ADS")
for b in [
    "Curva ABC (Mercado Turbo/planilha) por unidades vendidas: Full a 120% (curva A) / 100% (B) / C sob demanda.",
    "ADS por curva: A (ROAS alto/ACOS 0–10%), B (intermediário), C (agressivo) + campanhas \"Fora de Curva\"/\"Incubadora\" (gastões) e \"Lançamentos\".",
    "Gestão por ROAS/ACOS/TACOS (meta TACOS < 5%), leitura 30/15/7 dias, escalar orçamento +20–30% quando bate a meta, \"o menos é mais\".",
]:
    d.bullet(b)
d.h2("5) Alavancas de tráfego e escala")
for b in [
    "Full como prioridade competitiva (\"quem vai pro Full vende bem\"); logística Correio → Agência → Full.",
    "Programa de Afiliados como canal de altíssimo ROI e baixo custo (paga só venda direta).",
    "Duplicar/triplicar anúncios vencedores (EAN novo, capa/ângulo diferente, novas palavras-chave).",
    "Métricas-guia sempre à vista: 3 pilares — visita, conversão e ticket médio.",
]:
    d.bullet(b)

d.h1("3. As dores que se repetem (e onde o time perde faturamento)")
d.h2("Ruptura de estoque — a dor nº 1")
d.p("Aparece em quase todos (Ultra, ICONNECT, Aster, Habitare, Eficácia, Rafha). O padrão é sempre o "
    "mesmo: ruptura → queda de visitas → queda de faturamento (a conversão costuma se manter). Em vários "
    "casos o consultor mostrou, comparando as abas, que \"a perda veio 100% das visitas por falta de "
    "estoque\".")
d.h2("Integração ERP ↔ marketplace")
d.p("ERP apartado/estoque manual gera vendas com estoque zerado, reservas fantasmas e envios atrasados "
    "(Aster, Habitare, Rede Clip, Rafha, e o bug grave do Olist na Ultra — que virou processo judicial). "
    "É o gargalo estrutural que trava o próximo degrau de crescimento.")
d.h2("Outras dores comuns")
for b in [
    "Margem apertada e taxas do marketplace subindo para ~40% (Eficácia, Aster, Habitare).",
    "Bloqueios de produto / bugs de plataforma (nichos saúde e construção sofrem mais).",
    "Conversão % caindo conforme o volume/visitas crescem (Ultra, William) — vale monitorar.",
    "Dependência de um único carro-chefe (Eficácia: DAPA ~90%) e de poucas pessoas na operação.",
    "Coleta/Full intermitentes e penalidades de envio atrasado punindo a reputação.",
]:
    d.bullet(b)

d.h1("4. Padrões comerciais — o que gera recompra")
d.p("O resultado é o motor da renovação. Entre os 10:")
for b in [
    "ICONNECT recomprou (R$ 22.497 → R$ 24.997) já mirando a Shopee; Limendes recomprou (6 → 12 encontros).",
    "William é aluno recorrente (Tração em 2025 → Digital Business em 2026, por indicação de casal da carteira).",
    "Ultra Online tem renovação prevista; Carol já era aluna (fez ADS avançado antes).",
    "Lição comercial: escutar o feedback (\"6 encontros é pouco\" no Limendes) e oferecer a expansão natural — 2ª metade do método, novo canal (Amazon/Shopee/TikTok) ou marca própria (tese levantada na Rafha).",
]:
    d.bullet(b)

d.h1("5. Qualidade do CRM — um achado transversal")
d.p("Ao cruzar os 10, ficou evidente que o Pipedrive está subaproveitado. Isso empobrece o "
    "acompanhamento e a régua de recompra:")
for b in [
    "Campos de discovery (Objetivo, Principal Dor) quase sempre em branco.",
    "NPS e CSAT enviados (há a atividade), mas os valores não preenchidos.",
    "Bases iniciais zeradas em quem começou do zero (Savio, Vitor, Gabriel, Carol) — dificulta medir o \"de/para\".",
    "Rafha/Inova sem faturamento atual (é um dos maiores cases — o resultado fica sem fechar).",
    "Aster com negócio \"Aberto\" e produto/valor incompletos; Carol com consultor/datas/produto divergentes das gravações.",
]:
    d.bullet(b)
d.p("Recomendação: uma rotina simples de higienização do CRM (preencher discovery, NPS/CSAT, "
    "faturamento inicial/atual) transformaria esses dossiês em algo automático e comparável.")

d.h1("6. Nuances por nicho e canal")
for b in [
    "Conversão varia MUITO por nicho: calçados no ML rodam ~1–2% (Limendes/Ultra), enquanto saúde/manipulação chega a 9–11% (Eficácia). Não comparar conversão entre nichos.",
    "Shopee tem playbook próprio e paralelo (cupons em cascata, relâmpago com escassez, afiliados, GMV Max por curva) — visto em Pratik, Centermed e Rafha.",
    "Construção (Aster, Habitare) é ticket alto e margem apertada: o jogo é mix de fornecedor, profundidade e ADS por curva.",
    "Contas do zero levam ~2 meses só para validar conta + primeiras vendas + reputação (Decola) antes de tracionar.",
]:
    d.bullet(b)

d.h1("7. Recomendações para a escola/time")
for b in [
    "Tratar ruptura de estoque e integração ERP↔marketplace como TEMA de consultoria (não só operacional) — é o teto de crescimento da maioria.",
    "Padronizar o playbook em um material de referência (o método já é único e comprovado em 5 nichos) — reduz dependência do consultor e acelera alunos novos.",
    "Criar um material específico de Shopee (Carol pediu explicitamente; Pratik e Rafha reforçam) — hoje há lacuna percebida pelos alunos.",
    "Instituir régua de recompra baseada em resultado: quando o aluno vira case, oferecer a expansão (novo canal / marca própria / mais encontros).",
    "Higienizar o CRM (discovery, NPS/CSAT, faturamento) — vira insumo para dossiês automáticos e para o comercial.",
    "Monitorar a queda de conversão % nas contas que escalam volume (fotos/quebra de objeção/preço competitivo).",
]:
    d.bullet(b)

d.h1("8. Conclusão")
d.p("Os 10 casos, somados, contam uma história coerente: existe UM playbook de tração (anúncio de alta "
    "performance + pesquisa de mercado + motor promocional + curva ABC no Full e no ADS + afiliados) que "
    "funciona de calçados a farmácia, de conta de R$ 1 milhão a conta nascendo do zero. Onde ele patina, "
    "o motivo quase nunca é o método — é estoque/ERP, margem ou execução. Resolver esses três e manter a "
    "disciplina semanal de otimização é o que separa o aluno que cresce 80% do que cresce 8×.")
d.p("")
d.p("Documento gerado a partir do cruzamento entre o CRM (Pipedrive: deals, jornada, notas e atividades) "
    "e as ~100 transcrições dos encontros dos 10 alunos. Campos ausentes no CRM foram marcados como "
    "\"não preenchido no Pipedrive\".", italico=True)
print("OK:", d.salvar(SAIDA))
