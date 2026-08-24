# O que a Edge Function `live` devolve

`GET https://fsylnexkwfyyaloalrxn.supabase.co/functions/v1/live?de=AAAA-MM-DD&ate=AAAA-MM-DD`

Cabeçalhos: `Authorization: Bearer <access_token da sessão Supabase>` e `apikey: <chave publicável>`.

Ela consulta o Pipedrive na hora. Não grava nada. **Não precisa mexer nela.**

## Raiz da resposta

| campo | o que é |
|---|---|
| `ok` | `true` em sucesso; em erro vem `ok:false` e `erro` |
| `periodo` | `{ de, ate, dias }` |
| `geradoEm` | ISO — vira o "Pipedrive ao vivo HH:MM" do topo |
| `ms` | tempo da consulta |
| `deals` | **o principal** — lista de negócios (abaixo) |
| `contagem` | `{ total, ganhos, perdidos, abertos, com_analise, fora_sem_vendedor }` |
| `conferencia.ae_ganhos` | confere com o card [AE] do Insights: `{ negocios, valor, por_vendedor }` |
| `avisos` | lista de textos com HTML — hoje vão para o console |
| `preenchimento` | % de preenchimento dos campos, sobre os abertos |
| `churn12` | cancelamentos dos últimos 12 meses (usado na página Churn) |
| `recebimento12` | `[{ mes, ganhos, valor, recebido }]` por mês |
| `plataformas` | de onde saiu a reunião, lido das atividades |
| `varredura` | quanto cada varredura leu — diagnóstico, não é para a tela |

## Cada item de `deals`

| campo | tipo | o que é |
|---|---|---|
| `id` | número | id do Pipedrive — link é `https://icommescola.pipedrive.com/deal/{id}` |
| `t` | texto | título do negócio |
| `v` | texto | **closer** (campo "Vendedor" do Pipedrive, não o proprietário) |
| `p` | texto | produto |
| `pFonte` | texto | de onde saiu o produto: contratado, apresentado ou sugerido |
| `s` | `won` \| `lost` \| `open` | situação |
| `val` | número | valor do negócio |
| `valPago` | número | o que de fato entrou; `0` quando ninguém preencheu |
| `et` | texto | etapa do funil |
| `funil` | texto | nome do funil |
| `tmp` | texto\|null | Quente, Morno ou Frio |
| `lead` | texto\|null | qualificação A..F |
| `canal` | texto\|null | canal de conexão |
| `orig` | texto\|null | origem contratual (ICOMM ou TF) |
| `sdr`, `buddy` | texto\|null | SDR e time de CS |
| `dCriacao`, `dGanho`, `dPerda`, `dDesfecho` | AAAA-MM-DD\|null | datas |
| `dpar` | número\|null | dias parado na etapa (só para abertos) |
| `nret` | número\|null | nº de retornos |
| `retAgendado`, `retRealizado`, `noShow`, `diaReuniao` | AAAA-MM-DD\|null | datas do retorno |
| `churn` | boolean | cancelou |
| `reemb` | número | reembolsado |
| `dc` | AAAA-MM-DD\|null | data do cancelamento |
| `cm` | texto[] | motivos do churn (múltipla escolha) |
| `saude` | texto\|null | Risco, Ativo, Saudável, Cancelado, Revertido |
| `lm`, `ld` | texto\|null | motivo e descrição da perda |
| `precoLista` | número | preço de tabela; `0` quando o produto não está no catálogo |
| `an` | objeto\|null | análise da call: `{ nota, dur, cp, lp, resumo, certo[], erro[], cond[], porque }` |
| `obj` | `{nome, origem}[]` | objeções — origem `call` ou `perda` |
| `plataforma` | texto\|null | Google Meet, Zoom, Meetime… lido da atividade |

## Armadilhas que já custaram caro

- **`diaReuniao` quase nunca vem em negócio aberto.** A API v2 traz só 15 campos
  customizados e esse não está entre eles; ele só chega em negócio ganho ou
  criado no período. Não conte reunião sem saber disso.
- **`valPago` costuma vir `0`.** Para recebimento, use `valPago > 0 ? valPago : val`.
- **`precoLista` vem `0`** quando o produto não está cadastrado no catálogo do
  Pipedrive. Não calcule desconto sem checar.
- **A carteira aberta é a conta inteira**, não só o comercial. Já vem filtrada
  por quem tem "Vendedor" preenchido.
