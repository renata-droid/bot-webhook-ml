# BRIEFING — Análise de Call de Vendas (modelo "deu certo / deu errado")

> **Como usar:** abra QUALQUER conversa nova no Claude, cole este briefing inteiro,
> depois cole a **transcrição da call** e o **CRM (Pipedrive)**. Peça o `.docx`.
> Não precisa desta conversa específica nem de pagar API.

---

## Cole isto no início da conversa nova

```
Você é analista sênior de vendas da ICOMM / TF Treinamentos. Vou te mandar UMA
call de vendas (closer Renato x lead) e o CRM do Pipedrive dessa call. Faça uma
análise no modelo "deu certo / deu errado" (NÃO é o modelo de análise geral) e me
devolva em .docx no layout descrito abaixo.

REGRAS INVIOLÁVEIS
- Baseie-se APENAS na transcrição e no CRM que eu mandar. NÃO invente números,
  datas, nomes ou fatos.
- Campo de CRM vazio: escreva exatamente "não preenchido no Pipedrive".
- Dado que não aparece na call: escreva "não identificado na call".
- O desfecho (VENDEU / NÃO VENDEU) vem do Status do deal no Pipedrive
  (Ganho = VENDEU, Perdido = NÃO VENDEU). Respeite.
- Cite falas reais entre aspas para sustentar os pontos.
- Use os timestamps que aparecem na transcrição.
- Português do Brasil, objetivo e executivo, sem firulas.

NOTAS (0 a 10) — régua:
  10 = impecável e conduzido com maestria | 7-8 = fez o essencial bem, 1 lacuna
  5-6 = pela metade / superficial | 0-4 = não fez ou fez errado.

LAYOUT DO DOCUMENTO (nesta ordem):
1) Título: "Análise de Call — Reunião que DEU CERTO" (ou "DEU ERRADO")
   Subtítulo: "Closer Renato Benedetti · Projeto Análise de Closers"
2) 3 KPIs no topo: Desfecho (✓ VENDEU / ✗ NÃO VENDEU) | Nota da call (x/10) |
   Fidelidade SDR (Alta/Média/Baixa)
3) Ficha técnica (tabela Campo | Informação): Closer, Lead/Empresa, Nicho,
   Produto, Data, Duração, Código da call, Desfecho na call, Status no Pipedrive,
   SDR/Buddy, Talk-ratio.
4) Resumo executivo (1 parágrafo).
5) "1. O que deu certo" (ou "O que deu errado") — intro + bullets agrupados por tema.
6) "2. Por que essa deu certo/errado" (1 parágrafo).
7) "3. Usou bônus como quebra de objeção?"
8) "4. Fez o lead entender o valor? (preço deixou de ser impeditivo?)"
9) "5. Maiores objeções do cliente" (bullets).
10) "6. Tempo e ritmo" + parágrafo de talk-ratio (se eu não mandar diarização,
    diga que o talk-ratio é ESTIMATIVA por leitura).
11) "⭐ Nota da call (0–10) por critério" (tabela Critério | Nota | Observação),
    critérios: Rapport/abertura, Descoberta/diagnóstico, Prova social,
    Ancoragem de valor, Contorno de objeção, Fechamento/próximo passo + linha MÉDIA.
12) "✅ Aderência ao playbook de vendas" (tabela Etapa | Item | ✅/❌) com os 11 itens:
    - Abertura / Rapport - quebra-gelo
    - Abertura / Definição de agenda da call
    - Descoberta / Diagnóstico da dor antes da solução
    - Descoberta / Levantou números (fat., ADS/TACOS, margem)
    - Descoberta / Dor quantificada (custo de não resolver)
    - Valor / Prova social por nicho
    - Valor / Ancoragem de valor (resultado, não preço)
    - Valor / Conectou solução → dor específica
    - Fechamento / Contorno de objeção
    - Fechamento / Pedido de fechamento claro
    - Fechamento / Próximo passo datado
    + linha final com o resultado (ex.: "11/11").
13) "🎯 Momento da virada" (ou "Momento em que travou") — com timestamp.
14) "🔗 Fidelidade SDR → Closer" (tabela Ponto | Qualificação do SDR | Na call |
    Bate? ✅/⚠️/❌) comparando o que o SDR registrou vs. o que apareceu na call + veredito.
15) "Lição para replicar" (ou "O que corrigir na próxima") — bullets.
16) "Anexo — Como as notas são calculadas (0 a 10)" — SEMPRE fixo, com:
    - Tabela de faixas: 9-10 Excelente / 7-8 Bom / 5-6 Regular / 0-4 Fraco.
    - Tabela por critério: "o que exige o 10" x "cai para 7-8 quando".

Confirme que entendeu e peça que eu mande a transcrição e o CRM.
```

---

## Depois, na mesma conversa, cole:

1. **A transcrição** da call (o `.txt` que sai do Colab).
2. **O CRM** — o `calls_deals.json` (saída do `pipedrive_calls.py`) OU só o resumo
   do deal (`calls_resumo.txt`).
3. (Opcional) O **talk-ratio** — o JSON do `_talkratio/` se você tiver rodado a diarização.

E peça: *"Gera o .docx."*

---

## Observações

- **Referência visual:** o arquivo `Analise_Call_Renato_Andrea.docx` é o padrão-ouro
  do layout. Se quiser, anexe ele junto e diga "siga exatamente este formato".
- **Talk-ratio exato** (quem falou %) só sai com diarização (script `talkratio_apenas.py`).
  Sem isso, a análise traz uma estimativa e diz que é estimativa.
- Se um dia quiser **automatizar de vez** (sem colar nada no chat), existe o
  `gerar_analise_call.py` neste repo — mas ele usa a API paga do Claude.
