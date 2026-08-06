# Análise de Consultorias (transcrições + CRM)

Fluxo para gerar dossiês de consultoria (individual por aluno + análise geral),
no mesmo molde do dossiê do Limendes.

## Pipeline

```
vídeos dos encontros ──> transcrever_consultorias.py ──> .txt/.json por aluno
Pipedrive (deals)   ──> pipedrive_consultorias.py   ──> _pipedrive/consultorias_negocios.json
                                    │
                                    ▼
                    empacotar_para_analise.py  ──>  _para_analise.zip
                                    │
                                    ▼
                         análise (dossiê por aluno + geral)
```

## Scripts

- **`transcrever_consultorias.py`** *(fora deste repo — roda local/Colab)*
  Transcreve os vídeos de cada aluno com faster-whisper. Gera `.txt` e `.json`
  na pasta de cada aluno. Incremental (pula o que já tem `.json`).

- **`pipedrive_consultorias.py`** *(fora deste repo — roda local)*
  Para cada aluno em `clientes.csv` (`slug,deal_id`), puxa do Pipedrive o
  negócio + jornada + notas + atividades + discovery, já traduzindo as chaves
  personalizadas (hash) para nomes legíveis. Gera
  `_pipedrive/consultorias_negocios.json`. Precisa de `.env` com
  `PIPEDRIVE_API_TOKEN` e `PIPEDRIVE_DOMAIN`.

- **`empacotar_para_analise.py`** *(este repo)*
  Junta só os `.txt`/`.json` das transcrições (nunca os vídeos) + o
  `consultorias_negocios.json` num único `_para_analise.zip`, leve, pronto para
  subir no chat. Sem dependências externas.

## Como usar o empacotador

1. Confirme `PASTA_BASE` no topo de `empacotar_para_analise.py`.
2. `python empacotar_para_analise.py`
3. Suba o `_para_analise.zip` gerado.

## Mapa CRM → dossiê

Campos do Pipedrive usados em cada seção do dossiê (chaves personalizadas):

| Seção | Campo | Chave |
|---|---|---|
| Resultado | Faturamento Inicial / Atual | `035d05bb…` / `a48e5817…` |
| Resultado | Faturamento 1º/2º/3º mês | `10c37c8d…` / `a58c4eb6…` / `8f1a7b45…` |
| Resultado | Variação / Aumento | `392b1399…` / `0049ccee…` |
| Jornada | Produto / Status / Ganho / Perda | `6621eda2…` / status / won_time / lost_time |
| Perfil | Consultor / Buddy | `062c7860…` / `b62372b1…` |
| Perfil | Categoria / Marketplaces / Reputação / ERP | `4feca3e6…` / `85835cea…` / `634f45b3…` / `2acfb831…` |
| Perfil | Link do Drive do aluno | `a5d45295…` |
| Discovery | Objetivo / Principal Dor | `c99ef8ae…` / `88dbdbde…` |
| Encontros | Data 1º encontro / Onboarding | `4b22cddf…` / `8f3d3745…` |
| Satisfação | NPS / CSAT / Saúde / Churn | `73c1199a…` / `c5cc049a…` / `57f99940…` / `9755e115…` |
