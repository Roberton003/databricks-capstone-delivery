# 🏛️ Arquitetura

Visão geral da arquitetura do Stock-Market Research Assistant.

## Componentes Principais

### Lakebase (PostgreSQL)

Banco transacional gerenciado pelo Databricks:

- `watchlists` - Listas de tickers por usuário
- `watchlist_tickers` - RelaçãoMany-to-Many
- `ticker_news_documents` - Metadados de notícias
- `ticker_news_embeddings` - Embeddings de artigos
- `ticker_news_chunk_embeddings` - Embeddings de chunks
- `research_notes` - Notas salvas pelo agente
- `analysis_reports` - Relatórios salvos pelo agente

### Pipeline de Dados

1. **Ingestão:** Massive API → `ticker_news_documents`
2. **Extração:** HTML → texto com trafilatura
3. **Chunking:** Divisão em blocos sobrepostos
4. **Embeddings:** sentence-transformers (384 dimensões)
5. **Armazenamento:** pgvector com índice HNSW

### RAG (Retrieval-Augmented Generation)

1. Query → embedding
2. Busca vetorial no pgvector
3. Recuperação de top-k chunks
4. Contexto formatado + prompt
5. Resposta fundamentada com citações

## Comunicação entre Camadas

```
Databricks App → Lakebase (via psycopg2)
MCP Server → Lakebase (via psycopg2)
Notebook → Lakebase (via psycopg2 + OAuth)
```

## Segurança

- Secrets em Databricks Secret Scopes
- Rate limiting na API externa
- Input validation em todos os endpoints
- SQL injection prevention (parametrized queries)
