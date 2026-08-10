# 🐛 Troubleshooting

Problemas comuns e soluções.

## Erro: LAKEBASE_URL not set

**Solução:** Configure o secret scope:

```bash
databricks secrets put --scope database --key lakebase-url --value <base64-encoded-url>
```

## Erro: Massive API rate limit

**Solução:** O pipeline já tem rate limiting (5 req/min). Espere 60 segundos e tente novamente.

## Embeddings vazios

**Causas:**
- Tabela `ticker_news_documents` está vazia
- Embedding não foi computado pelo notebook
- Model name incorreto no schema

**Verificação:**
```sql
SELECT COUNT(*) FROM ticker_news_documents;
SELECT COUNT(*) FROM ticker_news_embeddings WHERE embedding IS NOT NULL;
```

## Query RAG sem resultados

**Verifique:**
1. Tabela `ticker_news_embeddings` tem dados
2. Índice HNSW existe: `SHOW INDEX FROM ticker_news_embeddings`
3. Dimensão do embedding é 384

## MCP Server não inicia

**Verifique:**
1. Dependências instaladas: `pip install fastmcp`
2. LAKEBASE_URL e MASSIVE_API_KEY estão configuradas
3. Secret scopes existem e têm permissão

## Auth failed no Databricks

**Solução:**
```bash
databricks auth login
databricks auth token acquire
```
