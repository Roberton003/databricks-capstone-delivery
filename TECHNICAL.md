# Documentação Técnica

Este documento fornece detalhes técnicos para recrutadores e tech leads avaliarem o projeto.

---

## Visão Geral Técnica

| Categoria | Detalhe |
|-----------|---------|
| **Propósito** | Stock-Market Research Assistant - Databricks AI Bootcamp Capstone |
| **Data Engineer Skills** | Pipeline Spark, Lakebase, pgvector, Massive API |
| **AI/ML Skills** | Embeddings, RAG, MCP, Agent Bricks |
| **Cloud Platform** | Databricks (Lakebase, Apps, Jobs) |
| **Backend** | Flask, Python 3.12, SQLAlchemy |
| **Frontend** | HTML/CSS/JavaScript |
| **Database** | PostgreSQL (via Lakebase) com pgvector |

---

## Arquitetura de Dados

### Schema do Lakebase

```
┌──────────────────────────────┐
│          watchlists          │
├──────────────────────────────┤
│ id (PK)                      │
│ name                         │
│ user_id                      │
│ created_at                   │
└──────────────────────────────┘
           │
           │ 1:N
           ▼
┌──────────────────────────────┐
│      watchlist_tickers       │
├──────────────────────────────┤
│ id (PK)                      │
│ watchlist_id (FK)            │
│ ticker (PK)                  │
│ added_at                     │
└──────────────────────────────┘

┌──────────────────────────────┐
│     ticker_news_documents    │
├──────────────────────────────┤
│ id (PK)                      │
│ ticker                       │
│ title                        │
│ description                  │
│ author                       │
│ article_url                  │
│ publisher_name               │
│ keywords (JSONB)             │
│ sentiment                    │
│ sentiment_reasoning          │
│ published_utc                │
│ payload (JSONB)              │
│ synced_at                    │
└──────────────────────────────┘

┌──────────────────────────────┐
│    ticker_news_embeddings    │
├──────────────────────────────┤
│ id (PK)                      │
│ ticker                       │
│ title                        │
│ published_utc                │
│ embedding (VECTOR)           │
│ model_name                   │
│ embedded_at                  │
└──────────────────────────────┘

┌──────────────────────────────┐
│ ticker_news_chunk_embeddings │
├──────────────────────────────┤
│ id (PK)                      │
│ document_id (FK)             │
│ chunk_index                  │
│ chunk_text                   │
│ embedding (VECTOR)           │
│ model_name                   │
│ embedded_at                  │
└──────────────────────────────┘

┌──────────────────────────────┐
│       research_notes         │
├──────────────────────────────┤
│ id (PK)                      │
│ ticker                       │
│ title                        │
│ content                      │
│ created_at                   │
│ updated_at                   │
└──────────────────────────────┘

┌──────────────────────────────┐
│      analysis_reports        │
├──────────────────────────────┤
│ id (PK)                      │
│ ticker                       │
│ report (JSONB)               │
│ sources (JSONB)              │
│ created_at                   │
└──────────────────────────────┘
```

---

## Pipeline de Dados

### Processo de Ingestão

```
1. Watchlist (Lakebase)
   │
   ▼
2. Massive API /v2/reference/news
   - Busca notícias por ticker
   - Rate limited (free tier: 10 req/min)
   - Salva em ticker_news_documents
   │
   ▼
3. Extração de conteúdo (trafilatura)
   - Remove HTML boilerplate
   - Extrai texto limpo
   │
   ▼
4. Chunking (sentences)
   - Divide em chunks sobrepostos
   - Tamanho: ~256 tokens
   │
   ▼
5. Embeddings (sentence-transformers/all-MiniLM-L6-v2)
   - 384 dimensões
   - Similaridade de cosseno
   - Salva em ticker_news_embeddings
   │
   ▼
6. HNSW Index (pgvector)
   - Índice para busca rápida
   - Metric: cosine distance
```

---

## RAG (Retrieval-Augmented Generation)

### Fluxo de Consulta

```
1. Usuário pergunta: "Dê uma análise da AAPL"
   │
   ▼
2. Embedding da pergunta
   - Modelo: all-MiniLM-L6-v2
   - Dimensões: 384
   │
   ▼
3. Busca vetorial no Lakebase
   ```sql
   SELECT title, 1 - (embedding <-> %s::vector) as similarity
   FROM ticker_news_embeddings
   WHERE ticker = 'AAPL'
   ORDER BY similarity DESC
   LIMIT 10;
   ```
   │
   ▼
4. Recuperação de chunks
   - Top-k chunks mais relevantes
   - Formatação para contexto
   │
   ▼
5. Prompt ao LLM
   - Contexto: chunks recuperados
   - Pergunta: pergunta original
   - Instrução: responda com base apenas no contexto
   │
   ▼
6. Resposta fundamentada
   - Citação das fontes recuperadas
   - Referências às notícias
```

---

## MCP (Model Context Protocol)

### Ferramentas Disponíveis

#### Leitura

| Ferramenta | Descrição | Retorno |
|------------|-----------|---------|
| `get_quote(symbol)` | Preço atual de um ticker | `{"symbol", "price", "change", "volume"}` |
| `search_news(symbol, query, limit)` | Buscar notícias por ticker e query | Lista de notícias com scores |
| `search_research_context(query, symbol)` | Busca semântica de contexto | Top-k chunks com scores |
| `get_watchlist()` | Lista tickers da watchlist | Lista de tickers |

#### Escrita

| Ferramenta | Descrição | Retorno |
|------------|-----------|---------|
| `add_to_watchlist(symbol)` | Adicionar ticker à watchlist | `{"status", "symbol"}` |
| `remove_from_watchlist(symbol)` | Remover ticker da watchlist | `{"status", "symbol"}` |
| `save_research_note(symbol, title, content)` | Salvar nota de pesquisa | `{"id", "symbol", "title"}` |
| `save_analysis_report(symbol, report, sources)` | Salvar relatório de análise | `{"id", "symbol"}` |

---

## Deploy no Databricks

### Componentes como Apps

| Componente | Arquivo | Porta | Endpoints |
|------------|---------|-------|-----------|
| Main App | `app.py` | 8000 | `/watchlist`, `/price`, `/news`, `/search` |
| Dashboard | `dashboard/app.py` | 8001 | `/watchlist`, `/price`, `/news`, `/` |
| MCP Server | `mcp_server/alpaca_mcp_server.py` | 8002 | `/mcp/message` |

### Comandos de Deploy

```bash
# 1. Deploy bundle (Main App + MCP)
databricks bundle deploy -t dev

# 2. Deploy dashboard
cd dashboard
databricks apps deploy

# 3. Verificar status
databricks apps get databricks-lakebase-app-day-3
```

---

## Security

### Secrets Management

```
Secret Scope: "database"
├── lakebase-url (Base64 encoded)
├── alpaca-key-id
└── alpaca-secret-key

Secret Scope: "massive"
└── api-key (Base64 encoded)
```

### Validations Implementadas

- Ticker validation (alphanumeric, max length)
- Query length limits
- Rate limiting (API externa)
- PII filtering (middleware)
- SQL injection prevention (SQLAlchemy ORM)
- Input sanitization

---

## Observabilidade

### Logs

```
INFO: massive-app - Processing request
INFO: massive-app - API call: Massive /v2/reference/news
INFO: massive-app - News saved: 15 records
INFO: massive-app - Embeddings computed: 15 records
```

### Métricas

- Latência de query RAG
- Throughput de embeddings
- Taxa de erro da API
- Contagem de documentos ingestidos
- Contagem de embeddings

---

## Performance

| Operação | Tempo Esperado | Otimização |
|----------|----------------|------------|
| Query RAG (top-10) | < 500ms | HNSW index, cosine |
| Embedding (batch 100) | < 2s | Spark parallelism |
| Ingestion (per ticker) | < 30s | Batch, rate limiting |
| Dashboard load | < 1s | Caching, simple queries |

---

## Idempotency

### Regras Implementadas

| Tabela | Strategy | Chave |
|--------|----------|-------|
| `ticker_news_documents` | UPSERT | `id` (artigo único) |
| `ticker_news_embeddings` | UPSERT | `id, model_name` |
| `ticker_news_chunk_embeddings` | UPSERT | `document_id, chunk_index` |
| `research_notes` | INSERT | Auto-increment ID |
| `analysis_reports` | INSERT | Auto-increment ID |

---

## Conformidade com Capstone

| Requisito | Implementação | Estado |
|-----------|---------------|--------|
| Pipeline Spark | `ingest_ticker_news_embeddings.py` | ✅ |
| API externa | Massive API | ✅ |
| Conteúdo não estruturado | HTML → chunks | ✅ |
| Databricks App | `app.py` + `dashboard/app.py` | ✅ |
| Agente leitura | MCP Server | ✅ |
| Agente escrita | `save_research_note`, `save_analysis_report` | ✅ |

---

## Próximos Passos para Produção

1. **Deploy no Databricks Workspace** (próximo passo)
2. **Validação RAG** (testar busca semântica)
3. **Teste de carga** (pipeline Spark)
4. **Monitoramento** (Dashboards de métricas)
5. **CI/CD** (automatizar deploy)

---

*Este documento foi gerado automaticamente para demonstração técnica.*