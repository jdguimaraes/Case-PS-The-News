# Case Palavritas — Analista de Dados, Produto & Growth

Análise de retenção do Palavritas (the news), a partir do dataset
`Case Analista de Dados — the news [Dataset Palavritas].xlsx` (na pasta acima).

## Comece por aqui

- **[Analise_Palavritas_the_news.docx](Analise_Palavritas_the_news.docx)** — documento final para o Head de Produto: diagnóstico de limpeza, achados e proposta. Leia este primeiro.
- **[dashboard_palavritas.xlsx](dashboard_palavritas.xlsx)** — dashboard com KPIs em destaque, gráficos nativos e abas separadas por tema (visão geral, drivers de D30, ausência de driver de D+1, dados de apoio por perfil).

## Como o código está organizado

Os scripts rodam em sequência, cada um lendo o resultado do anterior. Todos usam Python
(pandas, scipy, openpyxl, python-docx) e foram executados com Python 3.12.

| Script | O que faz | Entrada | Saída |
|---|---|---|---|
| `01_explore.py` | Primeira leitura das 3 abas: shape, tipos, nulos, duplicatas | xlsx original | print no console |
| `02_quality.py` | Investiga valores fora do domínio esperado (attempts, device, datas, etc.) e cruza `sessions` x `attempts` x `user_profile` | xlsx original | print no console |
| `03_quality2.py` | Aprofunda nos achados do 02: formato misto de datas, divergência entre `sessions.attempts` e a contagem real de tentativas, confirmação de que o encoding corrompido já vem corrompido no arquivo original (não é bug de leitura) | xlsx original | print no console |
| `04_clean_and_analyze.py` | Aplica e **documenta** cada decisão de limpeza (duplicatas, datas, encoding, domínio de valores) | xlsx original | `sessions_clean.csv`, `attempts_clean.csv`, `user_profile_clean.csv`, `cleaning_log.txt` |
| `05_stats_analysis.py` | Testes estatísticos (qui-quadrado e teste-t de Welch, 95% de confiança) cruzando cada variável candidata com `played_next_day` (D+1) e `active_d30` (D30) | CSVs limpos | `stats_results.txt` |
| `06_dashboard.py` | Monta o dashboard (KPIs, tabelas e gráficos nativos) | CSVs limpos | `dashboard_palavritas.xlsx` |
| `07_build_report.py` | Gera o `.docx` final a partir dos achados (texto e tabelas já com os números extraídos da análise) | resultados das etapas acima | `Analise_Palavritas_the_news.docx` |

Para reproduzir do zero, rode os scripts na ordem numérica (`01` → `07`).
Cada um é independente e pode ser reaberto/editado no VS Code.

## Arquivos de log (a "prova de trabalho" da limpeza e da análise)

- **`cleaning_log.txt`** — toda decisão de limpeza, linha por linha, com o motivo.
- **`stats_results.txt`** — saída completa de todos os testes estatísticos (p-values, médias, taxas), incluindo variáveis que NÃO deram resultado significativo (testadas e descartadas).

## Decisões importantes que vale destacar
- **400 dos 1.200 usuários não têm perfil de pesquisa** — qualquer corte por setor/salário/device de perfil cobre só os 800 que responderam (67% da base). Isso está marcado no documento final como limitação, não escondido.
- **Encoding corrompido no arquivo original** (ex.: "finanças" salvo como "finan�as") foi reconstruído manualmente por contexto — são poucas palavras, todas reconhecíveis. Está documentado linha a linha no `cleaning_log.txt`.

## Dependências

```
pip install pandas numpy scipy openpyxl matplotlib statsmodels python-docx
```
