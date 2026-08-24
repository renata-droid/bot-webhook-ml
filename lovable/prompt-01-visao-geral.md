# Prompt 1 — Visão geral

Cole no Lovable. Antes disso, no projeto Lovable:

1. **Conecte o Supabase existente** (projeto `fsylnexkwfyyaloalrxn`) pela integração nativa.
2. **Suba o arquivo `calculos.ts`** para `src/lib/calculos.ts`.

---

Crie um painel comercial em React + TypeScript + Tailwind, tema escuro, chamado **Painel Comercial ICOMM**.

## Regra que não pode ser quebrada

O arquivo `src/lib/calculos.ts` já existe e contém TODAS as contas do painel.
**Importe e use as funções dele. Não reimplemente, não "melhore", não reescreva
nenhuma conta.** Elas foram validadas contra o painel em produção e qualquer
reescrita muda os números. Se faltar alguma conta, pare e avise — não invente.

Funções disponíveis: `base`, `carteira`, `agg`, `serie`, `ranking`,
`qualificacao`, `ETAPAS_RET`, `dataRef`, `BRL`, `PCT`.

## Dados

Login por Supabase Auth (e-mail e senha). Depois de logado, buscar:

```
GET {SUPABASE_URL}/functions/v1/live?de=AAAA-MM-DD&ate=AAAA-MM-DD
headers: Authorization: Bearer {session.access_token}, apikey: {chave publicável}
```

A resposta traz `deals` (lista de negócios) e `geradoEm`. Passe `deals` e o
objeto de filtros para as funções de `calculos.ts`.

Refazer a busca quando **De** ou **Até** mudarem. Os outros filtros são locais,
sem nova busca.

## Layout

**Barra lateral fixa** (236px): marca "ICOMM / COMERCIAL" e o menu — Visão geral,
Retorno, Churn, SDR, Closers, Reuniões. Só **Visão geral** funciona agora; as
outras ficam visíveis e inertes. No rodapé, o nome do usuário logado.

**Topo:** título "Visão geral", subtítulo `{n} negócios · {de} a {ate}`, e à
direita uma etiqueta roxa "PIPEDRIVE AO VIVO · HH:MM" (de `geradoEm`) mais os
botões Atualizar, Tema e Sair.

**Barra de filtros** em cartão, campos lado a lado: De (data), Até (data),
Base da data (Desfecho ganho/perda | Criação do negócio), Origem, Vendedor,
Produto, Canal, Qualificação. Os selects são preenchidos com os valores
distintos que vierem em `deals`, com uma opção "Todos" no topo. À direita,
em fonte mono pequena: `{X} no período · {Y} abertos hoje`.

**7 cartões em linha**, cada um com um anel de progresso à esquerda e o número
grande à direita. Use `agg(base(deals,f), f)` para os seis primeiros e
`agg(carteira(deals,f), f)` para "Em retorno":

| cartão | valor | anel | linha de baixo |
|---|---|---|---|
| OPP | `opp` | 100% | `{won}G · {lost}L · {ret}R` |
| Ganhos | `won` | `conv` | `BRL(receita)` |
| Lost | `lost` | `lost/opp` | "motivo no drill" |
| Em retorno | `ret` (da carteira) | `ret/opp` | três chips: Q/M/F com `q`,`m`,`f` |
| Conv. bruta | `PCT(conv)` | `conv` | `{won} ÷ {opp}` |
| Churn | `churn` | `churn/won` | `BRL(reemb)` ou "nenhum" |
| Conv. net | `PCT(net)` | `net` | `({won} − {churn}) ÷ {opp}` |

Ganhos, Lost, Em retorno e Churn são **clicáveis** e filtram o resto da página;
clicar de novo desliga.

**Bloco "Conversão líquida"**, largura inteira, fundo em degradê roxo:
número gigante `PCT(net)`, embaixo a fórmula `({won} ganhos − {churn} churn) ÷
{opp} oportunidades`, e um gráfico de área com os pontos de `serie(deals, f)` —
linha tracejada cinza para `bruta`, linha e área verde-limão para `net`, com o
valor escrito acima de cada ponto. Menos de 2 pontos: escreva "Período curto
demais para a série — escolha um intervalo maior".

**Duas colunas embaixo:**

- **Ranking de closers** — de `ranking(base(deals,f), f)`. Cada linha: posição,
  foto, nome, `{won} ganhos · conv. net {PCT(net)}` (e `· {churn} churn` quando
  houver), valor `BRL(receita)` à direita e uma barra proporcional ao maior.
- **Qualificação do que entrou · e o que virou venda** — de
  `qualificacao(base(deals,f))`. Uma barra por letra A–F com a contagem e
  `{PCT(taxa)} ganho`, mais uma linha "Sem qualificação" quando houver.

**Fotos:** bucket público `foto-time` do mesmo Supabase. Case o nome da pessoa
com o nome do arquivo, sem acento e sem diferenciar maiúscula. Sem arquivo,
mostre as iniciais num círculo.

## NÃO incluir nesta página

- Nada de "Carteira em retorno" (a rosca de temperatura e a lista de etapas)
- Nada de "Precisa de atenção" (os cinco cartões)

## Visual

Fundo `#07060B`, cartões `#15121D`, borda `#262130`, texto `#F2F0F7`,
secundário `#948CA8`. Roxo `#A222EF`, lima `#D5FF79`, oliva `#A5D03D`,
rosa `#FF5C8A`, periwinkle `#8B7BFF`, âmbar `#FFB443`, ciano `#3FD6E0`.
Fontes: **Plus Jakarta Sans** no texto e **JetBrains Mono** em todo número.
Cantos 18px nos cartões. Botão de tema alterna claro/escuro.

## Conferência antes de dizer que está pronto

Abra o painel atual e este lado a lado, mesmo período. **Os sete cartões, a
conversão líquida e o ranking têm que dar exatamente o mesmo número.** Se algum
divergir, é porque alguma conta foi reescrita em vez de importada de `calculos.ts`.
