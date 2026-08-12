"""Lakebase write operations for the Weather MCP server.

These helpers persist agent-driven actions (saving research notes and adding to
the user's watchlist) using the same psycopg2 + secret scope pattern as the
read path. They are kept separate from the broker / service so the read flow
stays pure.
"""

from __future__ import annotations

import base64
import hashlib
import os
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictCursor

try:
    from databricks.sdk import WorkspaceClient
except ModuleNotFoundError:
    WorkspaceClient = None

_w = WorkspaceClient() if WorkspaceClient else None
_SCOPE = os.environ.get("LAKEBASE_SECRET_SCOPE", "database")
_KEY = os.environ.get("LAKEBASE_SECRET_KEY", "lakebase-url")


def _lakebase_url() -> str:
    if _w is None:
        raise RuntimeError("Databricks SDK is required for Lakebase access")
    secret = _w.secrets.get_secret(scope=_SCOPE, key=_KEY)
    return base64.b64decode(secret.value).decode("utf-8")


@contextmanager
def get_connection():
    conn = psycopg2.connect(_lakebase_url(), cursor_factory=RealDictCursor)
    try:
        yield conn
    finally:
        conn.close()


def _note_id(owner_email: str, title: str) -> str:
    seed = f"{owner_email.lower().strip()}|{title.strip().lower()}"
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


def save_research_note(location: str, title: str, content: str, owner_email: str) -> dict:
    """Persist a research note tied to the acting user email.

    Upserts by `(owner_email, title)` so re-saves replace the previous entry.
    Returns the stored row.
    """
    if not isinstance(location, str) or not location.strip():
        raise ValueError("location must not be empty")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("title must not be empty")
    if not isinstance(content, str) or not content.strip():
        raise ValueError("content must not be empty")
    if not isinstance(owner_email, str) or not owner_email.strip():
        raise ValueError("owner_email must not be empty")

    note_id = _note_id(owner_email, title)
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
                (note_id, owner_email.strip().lower(), location.strip(),
                 title.strip(), content.strip()),
            )
            row = cur.fetchone()
        conn.commit()
    return dict(row)


def add_to_watchlist(symbol: str, owner_email: str) -> dict:
    """Upsert a watchlist symbol for the acting user.

    Stores in `watchlist` (created lazily if missing) and returns the row.
    """
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
