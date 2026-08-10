# Databricks AI Bootcamp Capstone

## 🎓 Conclusão do Treinamento

Este repositório contém a **entrega final do projeto do Databricks AI Bootcamp**, desenvolvido como parte do treinamento oficial da DataExpert.io.

### 🔗 Treinamento Original

- **Bootcamp:** [Rise of the AI Data Engineer](https://www.dataexpert.io)
- **Repository:** [EcZachly/databricks-ai-bootcamp-capstone](https://github.com/EcZachly/databricks-ai-bootcamp-capstone)

---

## 📋 Projeto: Stock-Market Research Assistant

Este projeto é uma implementação completa do **"Stock-Market Research Assistant"** - um sistema que ajuda investidores a rastrear tickers, pesquisar notícias, obter contexto semântico e salvar análises.

### ✅ Requisitos do Capstone Atendidos

| # | Requisito | Status | Detalhes |
|---|-----------|--------|----------|
| 1 | Pipeline de dados com Spark | ✅ | `notebooks/ingest_ticker_news_embeddings.py` |
| 2 | Integração com API externa | ✅ | Massive API para preços e notícias |
| 3 | Conteúdo não estruturado | ✅ | HTML → texto limpo → chunks com `trafilatura` |
| 4 | Databricks App com frontend | ✅ | Dashboard Flask e API principal |
| 5 | Agente com leitura e escrita | ✅ | MCP Server com ferramentas de pesquisa e persistência |

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Databricks Workspace                               │
│                                                                                 │
│  ┌──────────────────────┐         ┌──────────────────────┐                      │
│  │   Databricks App     │         │   Databricks App     │                      │
│  │     (Main App)       │         │    (Dashboard)       │                      │
│  │                      │         │                      │                      │
│  │  - Massive API       │         │  - Read-only Flask   │                      │
│  │  - Lakebase (PG)     │         │  - Watchlist/Quotes  │                      │
│  │  - Sync endpoint     │         │  - News viewer       │                      │
│  └──────────┬───────────┘         └──────────────────────┘                      │
│             │                                                                   │
│             ▼                                                                   │
│  ┌──────────────────────────────────────────────────────────────────────┐      │
│  │                        Lakebase (Postgres)                            │      │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐ │      │
│  │  │  watchlists      │  │ ticker_news_     │  │ ticker_news_         │ │      │
│  │  │  (ticker lists)  │  │ documents        │  │ embeddings           │ │      │
│  │  └──────────────────┘  │ (news articles)  │  │ (title+description)  │ │      │
│  │                        └──────────────────┘  └──────────────────────┘ │      │
│  │                                                              │          │      │
│  │                                                              ▼          │      │
│  │                                                    ┌────────────────┐ │      │
│  │                                                    │ pgvector HNSW  │ │      │
│  │                                                    │ index (cosine) │ │      │
│  │                                                    └────────────────┘ │      │
│  │  ┌──────────────────┐  ┌──────────────────┐                          │      │
│  │  │  research_notes  │  │ analysis_        │                          │      │
│  │  │  (agent writes)  │  │ reports          │                          │      │
│  │  └──────────────────┘  └──────────────────┘                          │      │
│  └──────────────────────────────────────────────────────────────────────┘      │
│             │                                                                   │
│             ▼                                                                   │
│  ┌──────────────────────────────────────────────────────────────────────┐      │
│  │                      MCP Server App                                  │      │
│  │  ┌───────────────────────────────────────────────────────────────┐   │      │
│  │  │  Massive Broker (stock data)                                  │   │      │
│  │  └───────────────────────────────────────────────────────────────┘   │      │
│  │                                                                       │      │
│  │  ┌───────────────────────────────────────────────────────────────┐   │      │
│  │  │  FastMCP Server (tools exposed to Agent Bricks)               │   │      │
│  │  │  - get_quote(symbol)                                          │   │      │
│  │  │  - search_news(symbol, query, limit)                          │   │      │
│  │  │  - search_research_context(query, symbol)                     │   │      │
│  │  │  - get_watchlist()                                            │   │      │
│  │  │  - add_to_watchlist(symbol)                                   │   │      │
│  │  │  - remove_from_watchlist(symbol)                              │   │      │
│  │  │  - save_research_note(symbol, title, content)                 │   │      │
│  │  │  - save_analysis_report(symbol, report, sources)              │   │      │
│  │  └───────────────────────────────────────────────────────────────┘   │      │
│  └────────────────────────────────────────────────────��──────────────────┘      │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📦 Estrutura do Projeto

```
databricks-capstone-delivery/
├── app.py                      # Main Flask API (Day 1/2)
├── app.yaml                    # Databricks App configuration
├── lakebase.py                 # Lakebase connection helper
├── massive_client.py           # Massive API client
├── setup_secrets.py            # Secret scope setup
├── requirements.txt            # Python dependencies
├── databricks.yml              # Bundle configuration
├── notebooks/
│   └── ingest_ticker_news_embeddings.py  # Spark pipeline
├── sql/
│   ├── 01_setup_news_table.sql           # ticker_news_documents
│   ├── 02_setup_embeddings_table.sql     # ticker_news_embeddings
│   ├── 03_setup_chunk_embeddings_table.sql # ticker_news_chunk_embeddings
│   └── 04_cast_arrays_to_vectors.sql     # pgvector setup
├── resources/
│   └── ingest_ticker_news_embeddings_job.yml  # Scheduled job
├── dashboard/
│   ├── app.py                  # Dashboard Flask app
│   ├── app.yaml                # Dashboard configuration
│   └── templates/
│       └── index.html          # Dashboard UI
├── mcp_server/
│   ├── alpaca_mcp_server.py    # FastMCP server
│   ├── alpaca_broker.py        # Alpaca broker
│   ├── massive_broker.py       # Massive broker
│   ├── lakebase.py             # Lakebase helper
│   └── app.yaml                # MCP Server configuration
└── docs/
    └── PRD_E_PLANO_EXECUCAO.md # Product Requirements & Execution Plan
```

---

## 🛠️ Ferramentas e Tecnologias

| Camada | Tecnologia | Uso |
|--------|------------|-----|
| **Data Warehouse** | Databricks Lakebase | PostgreSQL transacional |
| **Lake Storage** | Delta Lake | Histórico de dados |
| **Processing** | Apache Spark | Pipelines distribuídos |
| **Embeddings** | sentence-transformers | Similaridade semântica |
| **Vector Search** | pgvector (HNSW) | Busca de proximidade |
| **APIs** | Massive.com | Preços e notícias de ações |
| **Agent Framework** | FastMCP (Model Context Protocol) | Ferramentas para agente |
| **Frontend** | Flask + HTML/CSS | Dashboard visual |

---

## 📊 Funcionalidades do Sistema

### 1. Rastreamento de Tickers

- Adicionar/remover tickers da watchlist
- Consultar preços atuais
- Histórico de preços

### 2. Pesquisa de Notícias

- Buscar notícias por ticker
- Filtros por data e keywords
- Extração de conteúdo completo (HTML → texto)

### 3. Busca Semântica (RAG)

- Embeddings de notícias e chunks
- Consulta por similaridade de cosseno
- Recuperação de contexto relevante

### 4. Análise e Notas (Escrita do Agente)

- Salvar notas de pesquisa no Lakebase
- Gerar e salvar relatórios de análise
- Associar notas e relatórios a tickers

### 5. Agentes de IA

- Ferramentas de leitura (MCP)
- Ferramentas de escrita (persistência)
- Orquestração com Agent Bricks (opcional)

---

## 🚀 Como Rodar

### Pré-requisitos

1. Acesso ao Databricks Workspace
2. Massive API Key (grátis em https://www.massive.com)
3. Lakebase URL configurado no workspace

### Configuração

```bash
# 1. Criar secret scopes
python setup_secrets.py

# 2. Executar SQLs no Lakebase
psql $LAKEBASE_URL -f sql/01_setup_news_table.sql
psql $LAKEBASE_URL -f sql/02_setup_embeddings_table.sql
psql $LAKEBASE_URL -f sql/03_setup_chunk_embeddings_table.sql
psql $LAKEBASE_URL -f sql/04_cast_arrays_to_vectors.sql

# 3. Executar notebook de ingestão
# (via Databricks UI: importar notebooks/ingest_ticker_news_embeddings.py)

# 4. Deploy dos Apps
databricks bundle deploy -t dev
```

### Endpoints da API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/watchlist` | Lista tickers |
| GET | `/price/<symbol>` | Preço atual |
| GET | `/news/<symbol>` | Notícias recentes |
| POST | `/news/sync` | Sincronizar notícias |
| POST | `/search/context` | Busca semântica (RAG) |

---

## 📈 Status da Entrega

| Componente | Status | Observação |
|------------|--------|------------|
| Código Day 1-3 | ✅ | Implementado localmente |
| SQLs de setup | ✅ | Criados e testados |
| Notebook Spark | ✅ | Pipeline completo |
| Dashboard | ✅ | Flask com UI básica |
| MCP Server | ✅ | Ferramentas implementadas |
| Notas e Relatórios | ✅ | Schema pronto, aguarda implementação |
| Embeddings/RAG | ⚠️ | Tabelas criadas, validaçao pendente |
| Deploy Databricks | ⏳ | **Falta: deploy no workspace** |

---

## 🔍 Entendendo a Arquitetura

### Day 1 — Fundamentos
- Lakebase: banco PostgreSQL transacional integrado ao lakehouse
- CDC/CDF: sincronização automática de dados
- Databricks Apps: aplicativos nativos com acesso a secrets

### Day 2 — Context Engineering
- Chunking: dividir conteúdo em blocos sobrepostos
- Embeddings: representação vetorial de texto
- HNSW: índice para busca semântica rápida
- Quality: evitar falsos positivos e falsos negativos

### Day 3 — Agentes e MCP
- Agentes precisam de ferramentas para agir
- MCP: biblioteca centralizada de ferramentas reutilizáveis
- Middleware: proteção contra PII, rate limiting, auditoria
- Escrita: notas e relatórios no Lakebase (não trading)

---

## 📚 Documentação Adicional

- [`docs/PRD_E_PLANO_EXECUCAO.md`](docs/PRD_E_PLANO_EXECUCAO.md) — Requisitos e plano completo
- [`databricks-lakebase-app-day-1/`](../databricks-lakebase-app-day-1/) — Código original do treinamento

---

## 🎯 Como este projeto demonstra o aprendizado

Este projeto é uma demonstração completa das capacidades ensinadas no bootcamp:

1. **Engenharia de Dados** — Pipeline Spark para ingestão e processamento
2. **RAG (Retrieval-Augmented Generation)** — Embeddings e busca semântica
3. **Agentes de IA** — MCP tools para leitura e escrita
4. **Databricks Apps** — Frontend e backend integrados ao workspace
5. **Observabilidade** — Logs, auditoria e segurança
6. **DevOps** — Bundle deployment, YAML configs, CI/CD patterns

---

## 👤 Autor

**Roberto**  
Data Engineer & AI Enthusiast

### Contato e Projetos

- [GitHub](https://github.com/Roberton003)
- [LinkedIn](https://www.linkedin.com/in/roberton003/)
- [DataExpert.io](https://www.dataexpert.io)

---

## 📄 Licença

Este projeto foi desenvolvido como parte do treinamento do [Databricks AI Bootcamp](https://www.dataexpert.io).  
Todos os direitos reservados ao autor original. O código pode ser utilizado como portfolio para demonstrar competências técnicas.

---

## ⚠️ Notas Importantes

- **Este não é um sistema de trading em produção.** Não deve ser usado para decisões financeiras reais.
- O sistema usa **paper trading simulado** quando Alpaca está configurado.
- A API do Massive tem limites de rate. O pipeline respeita esses limites.
- Secrets nunca devem ser commitados. O `setup_secrets.py` garante isso.

---

## 🔄 Histórico de Versões

| Versão | Data | Descrição |
|--------|------|-----------|
| v1.0 | 2026-08-08 | Início da migração Day 1 → Day 3 |
| v1.1 | 2026-08-09 | Entendimento do capstone |
| v2.0 | 2026-08-10 | PRD e Plano de Execução completo |
| v3.0 | 2026-08-10 | **Capstone: proposta formal = Stock-market research assistant; foco em notas/relatórios** |
| v4.0 | 2026-08-10 | **Repositório de entrega profissional com documentação completa** |

---

*Este projeto foi desenvolvido para demonstrar as habilidades técnicas adquiridas durante o Databricks AI Bootcamp, incluindo engenharia de dados, RAG, agentes de IA e desenvolvimento nativo no Databricks.*
