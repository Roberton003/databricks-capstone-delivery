# Evidências de Execução

Este documento contém as evidências de execução do projeto.

---

## 1. Execução do Notebook de Ingestão

### Script: `notebooks/ingest_ticker_news_embeddings.py`

**Comando:**
```bash
databricks jobs run-now --job-id <job-id>
```

**Saída esperada:**
```
Run ID: 12345
Run Name: ingest_ticker_news_embeddings-2026-08-10T04:00:00+00:00
Start Time: 2026-08-10T04:00:05.231Z
End Time: 2026-08-10T04:05:23.456Z
State: SUCCESS
Metrics:
  - Tickers processados: 5
  - Notícias extraídas: 1,234
  - Embeddings criados: 8,567
```

---

## 2. Execução do SQL Setup (pgvector)

### Script: `sql/04_cast_arrays_to_vectors.sql`

**Comando (via psql ou Databricks SQL):**
```sql
-- Criar tabela com embeddings
CREATE TABLE IF NOT EXISTS ticker_news_chunk_embeddings (
  id BIGINT GENERATED ALWAYS AS IDENTITY,
  document_id BIGINT NOT NULL,
  chunk_index INTEGER NOT NULL,
  chunk_text TEXT NOT NULL,
  embedding vector(384) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  FOREIGN KEY (document_id) REFERENCES ticker_news_embeddings(id)
);

-- Criar índice HNSW
CREATE INDEX IF NOT EXISTS ticker_news_embedding_idx
ON ticker_news_chunk_embeddings
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Verificar dimensão
SELECT pgvector.vector_dims(embedding) 
FROM ticker_news_chunk_embeddings 
LIMIT 1;
```

**Resultado esperado:**
```
 pgvector.vector_dims 
----------------------
                  384
(1 row)
```

**Verificar índice:**
```sql
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'ticker_news_chunk_embeddings';
```

---

## 3. Teste RAG (test_rag.py)

### Comando:
```bash
cd /path/to/project && python test_rag.py
```

### Saída esperada:
```
=== Teste de Busca Semântica ===

Teste 1: Busca por "AAPL earnings"
Results:
  1. AAPL Q3 2026 Earnings Preview (similarity: 0.89)
  2. Apple Reports Record Quarterly Results (similarity: 0.82)

Teste 2: Busca por "MSFT Copilot integration"
Results:
  1. Microsoft Copilot Integration Analysis (similarity: 0.85)
  2. MSFT Revenue Growth Driven by AI (similarity: 0.76)

=== Todos os testes passaram! ===
```

---

## 4. Execução do Servidor MCP

### Comando:
```bash
cd mcp_server && python run_server.py
```

### Saída esperada:
```
============================================================
Stock-Market Research Assistant - MCP Server
============================================================

Iniciando servidor FastMCP...

Ferramentas disponíveis:
  1. get_quote
  2. search_news
  3. search_research_context
  4. get_watchlist
  5. add_to_watchlist
  6. remove_from_watchlist
  7. save_research_note
  8. save_analysis_report

O servidor está rodando no endpoint HTTP padrão (localhost:3000)
```

### Teste de ferramenta:
```bash
curl -X POST http://localhost:3000/tools/get_quote -d '{"symbol": "AAPL"}'
```

---

## 5. Execução do Dashboard

### Comando:
```bash
cd dashboard && python app.py
```

### Saída esperada:
```
* Running on http://127.0.0.1:5000
* Press Ctrl+C to quit
[2026-08-10 04:30:00] INFO: Dashboard started
```

### Teste de endpoints:
```bash
# Get watchlist
curl http://localhost:5000/watchlist

# Get price
curl "http://localhost:5000/price?symbol=AAPL"
```

---

## 6. Verificação do Banco de Dados

### Comando (via Databricks SQL):
```sql
-- Verificar tabelas criadas
SHOW TABLES;

-- Verificar contagens
SELECT 'ticker_watchlist' as table_name, COUNT(*) as count FROM ticker_watchlist
UNION ALL
SELECT 'ticker_prices', COUNT(*) FROM ticker_prices
UNION ALL
SELECT 'ticker_news_embeddings', COUNT(*) FROM ticker_news_embeddings
UNION ALL
SELECT 'ticker_news_chunk_embeddings', COUNT(*) FROM ticker_news_chunk_embeddings;
```

---

## Resumo de Status

| Componente | Status | Evidência |
|------------|--------|-----------|
| Notebook ingestão | ⚠️ Aguardando deploy | Run ID + metrics |
| SQL pgvector setup | ⚠️ Aguardando deploy | Vector dims query |
| Teste RAG | ⚠️ Aguardando deploy | Output test_rag.py |
| Servidor MCP | ⚠️ Aguardando deploy | Log do run_server.py |
| Dashboard | ⚠️ Aguardando deploy | Access to /healthz |
| Banco de dados | ⚠️ Aguardando deploy | Query results |

---

**Próximo passo:** Fazer deploy no Databricks Workspace e capturar as evidências reais.
