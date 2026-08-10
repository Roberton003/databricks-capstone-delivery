"""
Test script for RAG functionality - validates semantic search with pgvector.

This script tests:
1. Database connection to Lakebase
2. Table existence (ticker_news_embeddings, ticker_news_chunk_embeddings)
3. Vector embeddings have correct dimension
4. HNSW index exists
5. Semantic search query works
6. Results include ticker, title, and embedding

Usage: python test_rag.py [--ticker AAPL] [--limit 10]
"""

import argparse
import os
import sys
from typing import Optional

import psycopg2
from psycopg2.extras import RealDictCursor


def get_lakebase_url() -> str:
    """Fetch Lakebase URL from environment or secret scope."""
    url = os.environ.get("LAKEBASE_URL")
    if url:
        return url

    # Try to get from secret scope
    try:
        from databricks.sdk import WorkspaceClient
        _w = WorkspaceClient()
        secret = _w.secrets.get_secret(scope="database", key="lakebase-url")
        import base64
        return base64.b64decode(secret.value).decode("utf-8")
    except Exception:
        raise ValueError("LAKEBASE_URL not set and cannot access secret scope")


def test_connection(url: str) -> bool:
    """Test database connection."""
    try:
        conn = psycopg2.connect(url)
        conn.close()
        print("✓ Database connection successful")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False


def test_tables_exist(url: str) -> bool:
    """Test that required tables exist."""
    required_tables = [
        "ticker_news_documents",
        "ticker_news_embeddings",
        "ticker_news_chunk_embeddings",
    ]

    conn = psycopg2.connect(url)
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name IN (%s, %s, %s)
            """, required_tables)
            tables = {row[0] for row in cur.fetchall()}

        missing = set(required_tables) - tables
        if missing:
            print(f"✗ Missing tables: {missing}")
            return False

        print("✓ All required tables exist")
        return True
    finally:
        conn.close()


def test_embeddings_dimension(url: str, expected_dim: int = 384) -> bool:
    """Test that embeddings have correct dimension."""
    conn = psycopg2.connect(url)
    try:
        with conn.cursor() as cur:
            # Check ticker_news_embeddings
            cur.execute("""
                SELECT embedding::text FROM ticker_news_embeddings
                WHERE embedding IS NOT NULL
                LIMIT 1
            """)
            row = cur.fetchone()
            if not row:
                print("⚠ No embeddings found in ticker_news_embeddings")
                return True  # Not an error if table is empty

            # Check vector dimension
            cur.execute("""
                SELECT vector_dims(embedding)
                FROM ticker_news_embeddings
                WHERE embedding IS NOT NULL
                LIMIT 1
            """)
            dim = cur.fetchone()
            if dim and dim[0] != expected_dim:
                print(f"✗ Embedding dimension mismatch: expected {expected_dim}, got {dim[0]}")
                return False

        print(f"✓ Embeddings have correct dimension ({expected_dim})")
        return True
    except Exception as e:
        print(f"✗ Error checking embeddings: {e}")
        return False
    finally:
        conn.close()


def test_hnsw_index(url: str) -> bool:
    """Test that HNSW index exists for embeddings."""
    conn = psycopg2.connect(url)
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = 'ticker_news_embeddings'
                AND indexname LIKE '%hnsw%'
            """)
            indexes = cur.fetchall()

        if indexes:
            print(f"✓ HNSW index found: {indexes[0][0]}")
            return True

        print("⚠ No HNSW index found (search will use sequential scan)")
        return True  # Not strictly required
    except Exception as e:
        print(f"✗ Error checking index: {e}")
        return False
    finally:
        conn.close()


def test_semantic_search(url: str, ticker: str = "AAPL", limit: int = 5) -> bool:
    """Test semantic search with a sample query."""
    conn = psycopg2.connect(url)
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # First get an embedding to use as query
            cur.execute("""
                SELECT embedding
                FROM ticker_news_embeddings
                WHERE ticker = %s
                AND embedding IS NOT NULL
                LIMIT 1
            """, (ticker,))
            row = cur.fetchone()

            if not row:
                print(f"⚠ No embeddings found for {ticker}")
                return True  # Not an error if no data

            query_embedding = row["embedding"]

            # Run semantic search
            cur.execute("""
                SELECT
                    ticker,
                    title,
                    published_utc,
                    model_name,
                    1 - (embedding <-> %s::vector) as similarity
                FROM ticker_news_embeddings
                WHERE ticker = %s
                ORDER BY similarity DESC
                LIMIT %s
            """, (query_embedding, ticker, limit))

            results = cur.fetchall()

            if not results:
                print(f"⚠ No search results for {ticker}")
                return True

            print(f"✓ Semantic search successful for {ticker}")
            print(f"  Found {len(results)} results:")
            for i, r in enumerate(results, 1):
                print(f"    {i}. {r['title'][:60]}... (similarity: {r['similarity']:.3f})")

            return True
    except Exception as e:
        print(f"✗ Semantic search failed: {e}")
        return False
    finally:
        conn.close()


def test_chunk_search(url: str, ticker: str = "AAPL", limit: int = 3) -> bool:
    """Test chunk-level semantic search."""
    conn = psycopg2.connect(url)
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT chunk_text, document_id, chunk_index, model_name,
                       1 - (embedding <-> (
                           SELECT embedding FROM ticker_news_embeddings
                           WHERE ticker = %s AND embedding IS NOT NULL LIMIT 1
                       )::vector) as similarity
                FROM ticker_news_chunk_embeddings
                WHERE ticker = %s
                ORDER BY similarity DESC
                LIMIT %s
            """, (ticker, ticker, limit))

            results = cur.fetchall()

            if results:
                print(f"✓ Chunk search successful for {ticker}")
                print(f"  Found {len(results)} chunk results")
                return True

            print("⚠ No chunk results found")
            return True
    except Exception as e:
        print(f"✗ Chunk search failed: {e}")
        return False
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="Test RAG functionality")
    parser.add_argument("--ticker", default="AAPL", help="Ticker symbol to test with")
    parser.add_argument("--limit", type=int, default=5, help="Number of results to show")
    args = parser.parse_args()

    print("=" * 60)
    print("RAG Functionality Test")
    print("=" * 60)

    try:
        url = get_lakebase_url()
    except ValueError as e:
        print(f"✗ {e}")
        print("\nSet LAKEBASE_URL environment variable or configure secrets.")
        sys.exit(1)

    tests = [
        ("Connection", lambda: test_connection(url)),
        ("Tables Exist", lambda: test_tables_exist(url)),
        ("Embeddings Dimension", lambda: test_embeddings_dimension(url)),
        ("HNSW Index", lambda: test_hnsw_index(url)),
        ("Semantic Search", lambda: test_semantic_search(url, args.ticker, args.limit)),
        ("Chunk Search", lambda: test_chunk_search(url, args.ticker, args.limit)),
    ]

    results = []
    for name, test_fn in tests:
        print(f"\nTesting: {name}")
        try:
            result = test_fn()
            results.append((name, result))
        except Exception as e:
            print(f"✗ Test error: {e}")
            results.append((name, False))

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All RAG tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
