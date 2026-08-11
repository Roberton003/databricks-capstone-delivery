import json
from functools import lru_cache

try:
    from . import lakebase
except ImportError:
    import lakebase

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384


@lru_cache(maxsize=1)
def _get_model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(EMBEDDING_MODEL_NAME)


def embed_query(query):
    vector = _get_model().encode([query], show_progress_bar=False)[0]
    return vector.tolist()


def _vector_literal(vector):
    return "[" + ",".join(str(float(value)) for value in vector) + "]"


def search(query, top_k=5):
    vector = _vector_literal(embed_query(query))
    sql = """
        SELECT d.id,
               d.location,
               d.headline,
               d.narrative_text,
               e.chunk_text,
               1 - (e.embedding <=> %s::vector) AS similarity
        FROM weather_embeddings e
        JOIN weather_documents d ON d.id = e.document_id
        ORDER BY e.embedding <=> %s::vector
        LIMIT %s
    """
    return lakebase.run_query(sql, (vector, vector, top_k))
