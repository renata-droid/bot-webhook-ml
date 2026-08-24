Crie a página **Retorno**, seguindo o mesmo padrão visual das páginas que já existem
(tema claro como padrão, cartões, tabelas e chips iguais aos do resto do dash).

Cole o arquivo `calculos.ts` atualizado que segue depois deste prompt. **Não escreva
nenhuma conta nova**: todos os números desta página saem de funções que já estão lá.

A página tem **três abas**, nesta ordem: `Carteira` · `Lastro das reuniões` · `Funil do retorno`.

---

## Aba 1 — Carteira

Fonte: `const cr = carteiraRet(deals, filtros)`

**a) Quatro cartões** — `cartoesRet(cr, filtros)` devolve os quatro na ordem certa.
Cada um tem `rotulo`, `n`, `valor` e `vazio`. Mostre o número grande; embaixo o valor
em R$ quando `n > 0`, senão o texto de `vazio`. Cores: Vencidos em rosa/vermelho,
Hoje e Lead não apareceu em âmbar, Sem data em cinza.
No cartão "Hoje", quando `filtros.ate` não for a data de hoje, escreva `Em DD/MM/AAAA`.

**b) Retornos por dia** — `retornosPorDia(cr, filtros)`

Se vier `vazio: true`, mostre só a mensagem: *"Nenhum retorno agendado entre DD/MM e DD/MM"*,
e se `depois > 0` acrescente *"— há N marcado(s) depois de DD/MM; estique o Até para vê-los"*.

Senão:
- Legenda no topo com `legenda` (Quente rosa, Morno âmbar, Frio periwinkle, Sem temperatura cinza),
  e à direita `ag.length` retornos · valor total.
- **Gráfico de barras empilhadas**, uma barra por dia de `porDia`. A altura é o `valor`
  de cada `parte`, empilhado na ordem da legenda. Em cima de cada barra, o `n` do dia.
  No eixo, `DD/MM` (só quando houver 24 dias ou menos).
  O dia com `hoje: true` recebe rótulo destacado e uma **linha tracejada vertical** à sua
  esquerda, separando o que já passou do que ainda vem.
  Altura fixa (~210px) e largura 100% — não deixe escalar com a tela.
- **Tabela por closer**, de `porCloser`: Closer · Quente · Morno · Frio · Atrasados · Retornos · Valor.
  Nas colunas de temperatura mostre `n` colorido e o valor em cinza ao lado; `—` quando zero.
  `atras` em vermelho quando maior que zero. Linha de **Total** no rodapé.
  Cada linha **expande** (seta ▸/▾) listando os negócios de `deals` daquele closer:
  bolinha da temperatura, título, produto, estado, data agendada e valor.

**c) Negócios em retorno** — `listaRet(cr, filtros, busca, estadoSelecionado)`

- Campo de **busca** no topo, com botão "limpar".
- **Chips** de `chips`: rótulo, contagem em negrito, valor em cinza. Clicar seleciona;
  clicar de novo desmarca. O chip ativo fica destacado.
- **Tabela** de `lista`: Negócio · Closer · Produto · Estado · Agendado · Atraso · Parado ·
  Temp. · Qualif. · Canal · Toques · Valor.
  - Estado é uma bolha colorida com `ROTULO_EST[estadoRet(d, filtros)]`.
  - Atraso vem de `atrasoDe(d)`, em vermelho quando passa de 2 dias.
  - Parado é `d.dpar`: vermelho a partir de 15 dias, âmbar a partir de 8.
- Subtítulo: `N de M negócios · R$ X · carteira em DD/MM/AAAA` (+ `· busca "termo"` quando houver busca).

---

## Aba 2 — Lastro das reuniões

Fonte: `lastro(deals, filtros)` — repare que lê `deals`, **não** a carteira.

Subtítulo: `DD/MM a DD/MM · N reuniões · X saíram com retorno · Y sem nada`.
Quando `reunioes` estiver vazio: `DD/MM a DD/MM · nenhuma reunião registrada`.

Um **cartão por closer**, de `porCloser`, em duas colunas:
- Cabeçalho: foto + nome, e à direita `ok/total` — verde quando `nada === 0`, vermelho quando não.
- Uma linha de resumo: `X com retorno`, `· Y no-show` (se houver), `· Z sem nada` em vermelho e negrito (se houver).
- Lista de `linhas`, cada uma com um ícone conforme `estado`:
  `ok` → ✓ verde · `ns` → ◑ âmbar · `nada` → ✕ vermelho.
  Ao lado, título do negócio, link e — à direita — `ret. DD/MM` quando tem `retAgendado`,
  senão `no-show` ou `sem retorno`.

Quando não houver nenhuma reunião, mostre no lugar dos cartões:
*"Nenhuma reunião com 'Dia da Reunião' preenchido neste recorte"*.

---

## Aba 3 — Funil do retorno

Fonte: `alvo = deals.filter(d => filtrosComuns(d, filtros))`

**a) Cinco cartões** — `cartoesFunil(alvo, filtros)`:

| Cartão | Valor | Subtexto |
|---|---|---|
| Reuniões | `reunioes.length` | com Dia da Reunião no período |
| Retornos agendados | `agendados.length` | `taxaAgendou` em % das reuniões |
| Retornos realizados | `realizados.length` | `taxaRealizou` em % dos agendados · data ou etapa |
| Viraram venda | `ganhos.length` | `taxaVenda` em % dos realizados |
| Retornos por venda | `porVenda` com 1 casa | quanto custa fechar |

Taxa nula (`null`) vira `—`.

**b) Três tabelas**, todas com `corteRet(alvo, filtros, chave)` e as mesmas colunas:
`<titulo> · Reuniões · Agendou · % · Realizou · % · Vendas · Conv. · Receita`,
com linha de **Total** vinda de `total`. Vendas em verde, receita em verde; `—` quando zero.

1. `corteRet(alvo, filtros, "v")` — "Por closer", **com foto** ao lado do nome
2. `corteRet(alvo, filtros, "canal")` — "Por canal de conexão", subtítulo *"campo preenchido à mão no negócio"*
3. `corteRet(alvo, filtros, "plataforma")` — "Onde a reunião aconteceu", subtítulo
   *"lido da atividade do Pipedrive · é aqui que o Google Meet aparece, porque ele não
   existe como opção do campo Canal"*

Quando `linhas` estiver vazio: *"Sem dados no período"*.

---

## Duas coisas para não "consertar"

1. **Os cartões da Carteira não obedecem o intervalo do filtro, e isso é proposital.**
   Eles mostram o estado da carteira aberta **visto a partir do "Até"**. "Vencido" é
   estado acumulado: um retorno marcado para 19/08 e não feito continua vencido no dia 24.
   Já o gráfico "Retornos por dia" é evento e **obedece** o intervalo. Filtrar um único
   dia mostra as barras daquele dia com os cartões ainda contando a carteira inteira.
   Não alinhe os dois.

2. **Os chips não somam o "Todos".** "Realizado" não ganha chip de propósito — a lista
   é fila de trabalho. O negócio continua na tabela quando "Todos" está selecionado.
