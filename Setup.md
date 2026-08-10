# ⚙️ Setup

Guia detalhado de configuração.

## 1. Acesso ao Databricks Workspace

- Solicite acesso ao workspace do treinamento
- Configure o profile em `~/.databricks-profiles`

## 2. Massive API Key

1. Acesse https://www.massive.com
2. Crie uma conta gratuita
3. Gere uma API Key
4. Salve em um Secret Scope:

```python
# setup_secrets.py
python setup_secrets.py --scope massive --key api-key --value <sua-api-key>
```

## 3. Lakebase Configuration

O Lakebase é gerenciado automaticamente pelo Databricks. Verifique:

```bash
databricks secrets list-scopes
databricks secrets list --scope database
```

## 4. Executar SQLs

```bash
databricks sql execute -f sql/01_setup_news_table.sql
databricks sql execute -f sql/02_setup_embeddings_table.sql
databricks sql execute -f sql/03_setup_chunk_embeddings_table.sql
databricks sql execute -f sql/04_cast_arrays_to_vectors.sql
databricks sql execute -f sql/05_setup_research_tables.sql
```

## 5. Executar Notebook

```bash
databricks notebooks run \
  --path notebooks/ingest_ticker_news_embeddings.py \
  --region us-east-1
```

## 6. Testar RAG

```bash
python3 test_rag.py --ticker AAPL --limit 5
```

## 7. Deploy dos Apps

```bash
databricks bundle deploy -t dev
```
