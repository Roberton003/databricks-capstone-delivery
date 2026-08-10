-- Cast DOUBLE PRECISION arrays to VECTOR type
-- Run this after the notebook writes embeddings

UPDATE ticker_news_embeddings SET embedding = embedding::vector WHERE embedding IS NOT NULL;
UPDATE ticker_news_chunk_embeddings SET embedding = embedding::vector WHERE embedding IS NOT NULL;

-- Verify
SELECT 'ticker_news_embeddings' AS table_name, COUNT(*) AS total, COUNT(embedding) AS with_embedding FROM ticker_news_embeddings
UNION ALL
SELECT 'ticker_news_chunk_embeddings', COUNT(*), COUNT(embedding) FROM ticker_news_chunk_embeddings;
