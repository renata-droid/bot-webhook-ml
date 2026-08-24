# Regras que valem para o dash inteiro

Todo prompt de página do Lovable tem que carregar estas regras. Elas não são de
nenhuma página específica — são do app — e por isso somem com facilidade: cada
prompt descreve uma tela, ninguém descreve o app.

Esta lista existe porque a regra 1 foi consertada no painel HTML e **não** foi
passada para o Lovable. A página Retorno nasceu com o mesmo bug que tinha
acabado de ser corrigido do outro lado, e quem descobriu foi a Renata, olhando
a tela.

---

## 1. Estreitar o período nunca busca de novo

Mudar "De" ou "Até" **não** pode disparar uma chamada nova à Edge Function
`live` quando o novo recorte cabe dentro do que já veio.

- Guarde `janela = { de, ate }` logo depois de cada `fetch` bem-sucedido, com os
  mesmos `de`/`ate` que foram enviados na URL.
- Se `novoDe >= janela.de && novoAte <= janela.ate`: só atualize os filtros no
  estado e deixe os componentes recalcularem a partir do array em memória.
- Só chame a Edge Function quando o recorte sair da janela (quando o usuário
  **alargar** o período).
- O botão "Atualizar" sempre busca.

**Por quê:** a conta tem mais de 15 mil negócios abertos e a varredura não
devolve sempre o mesmo conjunto. Buscando de novo a cada mudança de data,
filtrar 24/08 mostrava "nenhum retorno agendado" com os mesmos retornos do dia
24 visíveis um segundo antes no filtro do mês. A mesma pergunta, duas respostas.

Com a regra, a resposta do dia é um pedaço da resposta do período por
construção — não por sorte da varredura.

## 2. O `calculos.ts` é a única fonte dos números

Nenhuma página escreve conta própria. Se um número não sai de uma função do
módulo, ele não vai para a tela — o número é acertado no módulo, conferido
contra o painel HTML, e só então usado.

## 3. Tema claro é o padrão

O escuro é opção de quem quiser.

## 4. Bloco de ESTADO e bloco de EVENTO usam réguas diferentes

- **Estado** (carteira, cartões de ação, listas de pendência): lê o livro aberto
  inteiro, visto a partir do "Até". Não leva recorte de intervalo. "Vencido" é
  estado acumulado — um retorno marcado para 19/08 e não feito continua vencido
  no dia 24.
- **Evento** (lastro, retornos por dia, funil, ranking do período): leva o
  intervalo.

Os dois convivem na mesma tela de propósito. Não alinhe um com o outro.

## 5. Não "consertar" o que está explicado

Quando um prompt disser que algo é proposital, é proposital. Os dois casos que
um gerador de código tenta arrumar sozinho:

- os cartões da Carteira não obedecem o intervalo (regra 4);
- os chips da lista de retorno não somam o "Todos" — "realizado" não ganha chip,
  porque a lista é fila de trabalho.
