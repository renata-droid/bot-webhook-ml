# Ver o painel sem abrir o Pipedrive

Renderiza `painel_icomm.html` num navegador aqui mesmo, com dados de mentira,
e tira um print de cada página. Serve para quem mexe no código conferir a tela
**antes** de mandar o arquivo — em vez de descobrir que quebrou pelo print de
quem estava usando.

## Usar

```bash
npm i playwright        # uma vez
node preview/ver.mjs            # todas as páginas
node preview/ver.mjs retorno    # só uma
```

Os prints saem em `preview/saida/`. Sai com código 1 se achar problema.

## O que ele acusa

- página que estourou erro de JavaScript
- bloco que ficou vazio (cartão, tabela, gráfico)
- qualquer coisa visível no print

## O que ele NÃO acusa

Bug que só aparece com o dado real do Pipedrive — campo vazio no CRM,
carteira vindo pela metade, etapa com nome diferente. Para esses, ainda é
preciso abrir o painel de verdade.

## Se o navegador não abrir

Aponte o binário:

```bash
PLAYWRIGHT_CHROMIUM=/caminho/do/chrome node preview/ver.mjs
```
