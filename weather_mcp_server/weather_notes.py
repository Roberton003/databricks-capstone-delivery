"""Lakebase write operations for the Weather MCP server.

These helpers persist agent-driven actions (saving research notes and adding to
the user's watchlist) using OAuth credentials from the App's Lakebase resource.
The secret-scope URL remains a legacy fallback for local development.
"""

from __future__ import annotations

import base64
import hashlib
import os
from contextlib import contextmanager
from urllib.parse import unquote, urlsplit

import psycopg2
from psycopg2.extras import RealDictCursor

try:
    from databricks.sdk import WorkspaceClient
except ModuleNotFoundError:
    WorkspaceClient = None

_w = WorkspaceClient() if WorkspaceClient else None
_SCOPE = os.environ.get("LAKEBASE_SECRET_SCOPE", "database")
_KEY = os.environ.get("LAKEBASE_SECRET_KEY", "lakebase-url")
_ENDPOINT = os.environ.get(
    "LAKEBASE_ENDPOINT_NAME",
    "projects/weather-intelligence/branches/production/endpoints/primary",
)


def _generate_token(w) -> str:
    if not hasattr(w, "postgres"):
        raise RuntimeError(
            "Databricks SDK with WorkspaceClient.postgres is required for Lakebase access"
        )
    return w.postgres.generate_database_credential(endpoint=_ENDPOINT).token


def _lakebase_url(w) -> str:
    if w is None:
        raise RuntimeError("Databricks SDK is required for Lakebase access")
    secret = w.secrets.get_secret(scope=_SCOPE, key=_KEY)
    return base64.b64decode(secret.value).decode("utf-8")


def _connection_params(w) -> dict:
    host = os.environ.get("PGHOST")
    database = os.environ.get("PGDATABASE")
    user = os.environ.get("PGUSER")
    if host and database and user:
        return {
            "host": host,
            "port": int(os.environ.get("PGPORT", "5432")),
            "dbname": database.lstrip("/") or "weather",
            "user": unquote(unquote(user)),
            "password": _generate_token(w),
            "sslmode": os.environ.get("PGSSLMODE", "require"),
        }
    parts = urlsplit(_lakebase_url(w))
    app_identity = os.environ.get("PGUSER")
    app_identity = app_identity or os.environ.get("DATABRICKS_CLIENT_ID")
    app_identity = app_identity or getattr(getattr(w, "config", None), "client_id", None)
    sdk_user = w.current_user.me().user_name
    app_identity = app_identity or sdk_user
    return {
        "host": parts.hostname,
        "port": parts.port or 5432,
        "dbname": (parts.path or "/weather").lstrip("/") or "weather",
        "user": unquote(unquote(app_identity or sdk_user or parts.username or "")),
        "password": _generate_token(w),
        "sslmode": parts.query.removeprefix("sslmode=") if parts.query else "require",
    }
@contextmanager
def get_connection():
    if _w is None:
        raise RuntimeError("Databricks SDK is required for Lakebase access")
    conn = psycopg2.connect(cursor_factory=RealDictCursor, **_connection_params(_w))
    try:
        yield conn
    finally:
        conn.close()


def _note_id(owner_email: str, title: str) -> str:
    seed = f"{owner_email.lower().strip()}|{title.strip().lower()}"
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


def save_research_note(location: str, title: str, content: str, owner_email: str) -> dict:
    """Persist a research note tied to the acting user email."""
    if not isinstance(location, str) or not location.strip():
        raise ValueError("location must not be empty")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("title must not be empty")
    if not isinstance(content, str) or not content.strip():
        raise ValueError("content must not be empty")
    if not isinstance(owner_email, str) or not owner_email.strip():
        raise ValueError("owner_email must not be empty")

    location_clean = location.strip()
    title_clean = title.strip()
    content_clean = content.strip()
    email_clean = owner_email.strip().lower()
    note_id = _note_id(email_clean, title_clean)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO research_notes
                    (id, owner_email, location, title, content, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, now(), now())
                ON CONFLICT (id) DO UPDATE SET
                    location = EXCLUDED.location,
                    content = EXCLUDED.content,
                    updated_at = now()
                RETURNING id, owner_email, location, title,
                          length(content) AS content_length,
                          created_at, updated_at
                """,
                (note_id, email_clean, location_clean, title_clean, content_clean),
            )
            row = cur.fetchone()
        conn.commit()
    return dict(row)


def add_to_watchlist(symbol: str, owner_email: str) -> dict:
    """Upsert a watchlist symbol for the acting user."""
    if not isinstance(symbol, str) or not symbol.strip():
        raise ValueError("symbol must not be empty")
    if not isinstance(owner_email, str) or not owner_email.strip():
        raise ValueError("owner_email must not be empty")

    symbol_clean = symbol.strip().upper()
    email_clean = owner_email.strip().lower()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS watchlist (
                    symbol TEXT NOT NULL,
                    email TEXT NOT NULL,
                    latest_price NUMERIC,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    PRIMARY KEY (symbol, email)
                )
                """
            )
            cur.execute(
                """
                INSERT INTO watchlist (symbol, email, updated_at)
                VALUES (%s, %s, now())
                ON CONFLICT (symbol, email) DO UPDATE SET updated_at = now()
                RETURNING symbol, email, latest_price, updated_at
                """,
                (symbol_clean, email_clean),
            )
            row = cur.fetchone()
        conn.commit()
    return dict(row)


def remove_from_watchlist(symbol: str, owner_email: str) -> dict:
    if not isinstance(symbol, str) or not symbol.strip():
        raise ValueError("symbol must not be empty")
    if not isinstance(owner_email, str) or not owner_email.strip():
        raise ValueError("owner_email must not be empty")
    symbol_clean = symbol.strip().upper()
    email_clean = owner_email.strip().lower()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM watchlist
                WHERE symbol = %s AND email = %s
                RETURNING symbol, email
                """,
                (symbol_clean, email_clean),
            )
            row = cur.fetchone()
        conn.commit()
    return dict(row) if row else {"deleted": False, "symbol": symbol_clean, "email": email_clean}
