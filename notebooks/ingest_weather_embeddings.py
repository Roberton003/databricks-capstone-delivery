# Databricks notebook source
"""Generate idempotent pgvector chunks for weather documents in Lakebase."""

import hashlib
import os
import sys
from pathlib import Path

from psycopg2.extras import execute_values
from sentence_transformers import SentenceTransformer

try:
    notebook_path = dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()
    sys.path.insert(0, str(Path("/Workspace" + notebook_path).parent.parent))
except NameError:
    sys.path.insert(0, str(Path.cwd().parent))

from dashboard import lakebase

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    if not isinstance(text, str) or not text:
        return []
    if not 0 <= overlap < chunk_size:
        raise ValueError("overlap must be between 0 and chunk_size - 1")
    step = chunk_size - overlap
    return [text[start : start + chunk_size] for start in range(0, len(text), step)]


def _chunk_id(document_id, index, text):
    value = f"{document_id}:{index}:{text}"
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def ingest(model=None, batch_size=64):
    model = model or SentenceTransformer(EMBEDDING_MODEL_NAME)
    documents = lakebase.run_query(
        "SELECT id, narrative_text FROM weather_documents "
        "WHERE narrative_text IS NOT NULL AND narrative_text <> ''"
    )
    rows = []
    for document in documents:
        for index, text in enumerate(chunk_text(document["narrative_text"])):
            rows.append((_chunk_id(document["id"], index, text), document["id"], index, text))

    if not rows:
        return 0

    with lakebase.get_connection() as connection:
        with connection.cursor() as cursor:
            for start in range(0, len(rows), batch_size):
                batch = rows[start : start + batch_size]
                vectors = model.encode([row[3] for row in batch], show_progress_bar=False)
                values = [
                    (
                        *row,
                        "[" + ",".join(str(float(value)) for value in vector) + "]",
                        EMBEDDING_MODEL_NAME,
                    )
                    for row, vector in zip(batch, vectors)
                ]
                execute_values(
                    cursor,
                    """
                    INSERT INTO weather_embeddings
                        (id, document_id, chunk_index, chunk_text, embedding, model_name)
                    VALUES %s
                    ON CONFLICT (id) DO UPDATE SET
                        chunk_text = EXCLUDED.chunk_text,
                        embedding = EXCLUDED.embedding,
                        model_name = EXCLUDED.model_name,
                        embedded_at = now()
                    """,
                    values,
                    template="(%s, %s, %s, %s, %s::vector, %s)",
                )
        connection.commit()
    return len(rows)


if __name__ == "__main__":
    print(f"Embedded chunks: {ingest()}")
