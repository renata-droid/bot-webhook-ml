# Comparativo de semanas — Pipedrive

Compara a **mesma semana (01/08 a 06/08)** de dois anos e mostra *o que foi feito
de diferente*: ganhos, por vendedor, por produto, funil/conversão e atividades.

Foi feito para rodar **na sua máquina** (a API do Pipedrive não é acessível do
ambiente do Claude na web). Usa só a biblioteca padrão do Python 3 — sem instalar nada.

## Passo a passo

1. **Gere um token novo** no Pipedrive
   (Configurações pessoais → API → *Seu token de API*).
   > ⚠️ Se você já colou o token antigo em algum chat/arquivo, **revogue-o** e use um novo.

2. Baixe esta pasta (`git pull` da branch `claude/analysis-90nao8`) e rode:

   **Linux / Mac**
   ```bash
   export PD_TOKEN="seu_token_novo"
   python3 comparar_semanas.py
   ```

   **Windows (PowerShell)**
   ```powershell
   $env:PD_TOKEN="seu_token_novo"
   python comparar_semanas.py
   ```

3. Abra **`saida/relatorio.html`** no navegador.

## O que é gerado (pasta `saida/`)

| Arquivo | Conteúdo |
|---|---|
| `relatorio.html` | Relatório visual completo, lado a lado 2025 × 2026 |
| `comparativo.csv` | Métricas principais + variação % |
| `ganhos_2025.csv` / `ganhos_2026.csv` | Lista de negócios ganhos de cada período |
| `resumo.json` | Agregado bruto — **me mande este arquivo** para eu aprofundar a análise |
| `deal_fields.json` | Mapa dos campos do Pipedrive (auditoria) |

## Opções

```bash
python3 comparar_semanas.py \
  --dominio icommescola \   # subdomínio da conta
  --ano-a 2025 --ano-b 2026 \
  --inicio 08-01 --fim 08-06   # janela MM-DD (inclusive)
```

## Como me mandar de volta para eu analisar

Depois de rodar, envie aqui no chat o arquivo **`saida/resumo.json`**
(ele **não** contém seu token — só números agregados). Com ele eu escrevo o
diagnóstico de *"o que fizemos diferente"* e as recomendações.
