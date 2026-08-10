"""
Lakebase (Databricks-managed Postgres) connection helper for MCP Server.

Connects using a single LAKEBASE_URL (a standard Postgres connection URL,
e.g. postgresql://role:password@host:5432/databricks_postgres?sslmode=require)
pointing at a native Postgres role with a static, non-expiring password.
"""

import base64
import os
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictCursor
from databricks.sdk import WorkspaceClient
from sqlalchemy import create_engine

_w = WorkspaceClient()

_SCOPE = os.environ.get("LAKEBASE_SECRET_SCOPE", "database")
_KEY = os.environ.get("LAKEBASE_SECRET_KEY", "lakebase-url")


def _lakebase_url() -> str:
    """Fetch and decode the Lakebase connection URL from the Databricks secret scope."""
    secret = _w.secrets.get_secret(scope=_SCOPE, key=_KEY)
    return base64.b64decode(secret.value).decode("utf-8")


@contextmanager
def get_connection():
    """Yield a raw psycopg2 connection with a RealDictCursor factory."""
    conn = psycopg2.connect(_lakebase_url(), cursor_factory=RealDictCursor)
    try:
        yield conn
    finally:
        conn.close()


def get_engine():
    """Return a SQLAlchemy engine for Lakebase."""
    return create_engine(_lakebase_url())


def run_query(sql: str, params: tuple | dict | None = None) -> list[dict]:
    """Run a read query against Lakebase and return rows as list[dict]."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()


def run_write(sql: str, params: tuple | dict | None = None) -> int:
    """Run an INSERT/UPDATE/DELETE against Lakebase, return affected row count."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            conn.commit()
            return cur.rowcount


def save_research_note(ticker: str, title: str, content: str | None = None) -> dict:
    """Save a research note to the database. Returns the created note."""
    sql = """
        INSERT INTO research_notes (ticker, title, content)
        VALUES (%s, %s, %s)
        RETURNING id, ticker, title, created_at
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (ticker, title, content))
            conn.commit()
            result = cur.fetchone()
            return dict(result) if result else None


def save_analysis_report(ticker: str, report: dict, sources: list | None = None) -> dict:
    """Save an analysis report to the database. Returns the created report."""
    import json
    sql = """
        INSERT INTO analysis_reports (ticker, report, sources)
        VALUES (%s, %s::jsonb, %s::jsonb)
        RETURNING id, ticker, created_at
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (ticker, json.dumps(report), json.dumps(sources or [])))
            conn.commit()
            result = cur.fetchone()
            return dict(result) if result else None


def get_research_notes(ticker: str, limit: int = 10) -> list[dict]:
    """Get research notes for a ticker."""
    sql = """
        SELECT id, ticker, title, content, created_at, updated_at
        FROM research_notes
        WHERE ticker = %s
        ORDER BY created_at DESC
        LIMIT %s
    """
    return run_query(sql, (ticker, limit))


def get_analysis_reports(ticker: str, limit: int = 10) -> list[dict]:
    """Get analysis reports for a ticker."""
    sql = """
        SELECT id, ticker, report, sources, created_at
        FROM analysis_reports
        WHERE ticker = %s
        ORDER BY created_at DESC
        LIMIT %s
    """
    return run_query(sql, (ticker, limit))
