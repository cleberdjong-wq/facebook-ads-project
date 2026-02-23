# Facebook Ads — Pipeline de Análise e Dashboard

Pipeline em Python que extrai dados da **Facebook Ads API**, gera CSVs por segmento e produz um **dashboard HTML interativo** com Chart.js.

---

## Visão geral

```
01_campanhas.py       → campanhas.csv
02_cpv_diario.py      → cpv_diario.csv
03_posicionamentos.py → posicionamentos.csv
04_idade_genero.py    → idade_genero.csv
05_horarios.py        → horarios.csv
06_funil.py           → funil.csv
                              ↓
07_dashboard.py       → dashboard.html  ← abre no navegador
```

Execute tudo de uma vez com `python run_all.py`.

---

## Dashboard

O `dashboard.html` gerado contém:

| # | Visualização | Dados |
|---|-------------|-------|
| — | KPI Cards | Gasto total · Impressões · CTR médio · CPV médio |
| 1 | Barras | Gasto por campanha |
| 2 | Linha | Evolução diária do CPV |
| 3 | Donut | Distribuição por posicionamento |
| 4 | Barras agrupadas | Gasto por faixa etária e gênero |
| 5 | Barras (heat-like) | Cliques por horário do dia |
| 6 | Funil | Impressões → Alcance → Cliques → Leads → Conversões |
| 7 | Scatter | CTR vs CPV por campanha (identificação de outliers) |

> Se algum CSV não existir, o dashboard usa dados de amostra automaticamente.

---

## Instalação

```bash
pip install -r requirements.txt
```

**Dependências:**
- `facebook-business==19.0.0`
- `python-dotenv`
- `pandas`

---

## Configuração

Crie o arquivo `.env` na raiz do projeto (nunca commitar):

```env
FACEBOOK_ACCESS_TOKEN=EAAxxxxxxxxxxxxxxx
FACEBOOK_AD_ACCOUNT_ID=act_xxxxxxxxxx
FACEBOOK_APP_ID=xxxxxxxxxx
FACEBOOK_APP_SECRET=xxxxxxxxxx
```

| Variável | Onde obter |
|----------|-----------|
| `FACEBOOK_ACCESS_TOKEN` | [Graph API Explorer](https://developers.facebook.com/tools/explorer) → gerar token com `ads_read` + `read_insights` |
| `FACEBOOK_AD_ACCOUNT_ID` | URL do Ads Manager: `?act=XXXXXXXXXX` → `act_XXXXXXXXXX` |
| `FACEBOOK_APP_ID` | Meta for Developers → seu app → Configurações básicas |
| `FACEBOOK_APP_SECRET` | Meta for Developers → seu app → Configurações básicas |

---

## Uso

```bash
# Rodar pipeline completo (extrai dados + gera dashboard + abre no navegador)
python run_all.py

# Ou rodar scripts individualmente
python 01_campanhas.py
python 07_dashboard.py
```

---

## Estrutura do projeto

```
facebook-ads-project/
├── config.py               # Inicializa a Facebook Ads API
├── 01_campanhas.py         # Métricas por campanha
├── 02_cpv_diario.py        # CPV diário (últimos 30 dias)
├── 03_posicionamentos.py   # Distribuição por posicionamento
├── 04_idade_genero.py      # Segmentação por idade e gênero
├── 05_horarios.py          # Performance por horário do dia
├── 06_funil.py             # Funil de conversão
├── 07_dashboard.py         # Gerador do dashboard HTML
├── run_all.py              # Executor do pipeline completo
├── requirements.txt
├── .env                    # Credenciais (não versionado)
└── .gitignore
```

---

## Período de análise

Por padrão todos os scripts usam `last_30d`. Para alterar, edite a constante `DATE_PRESET` em cada script:

```python
DATE_PRESET = "last_7d"   # últimos 7 dias
DATE_PRESET = "last_30d"  # últimos 30 dias (padrão)
DATE_PRESET = "last_90d"  # últimos 90 dias
```
