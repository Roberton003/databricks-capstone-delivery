"""Lakebase Autoscaling Postgres connection helpers.

Supports two configurations:

1. Databricks App with a declared Lakebase resource. Environment variables
   `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGSSLMODE` are injected by the
   App. A short-lived OAuth token is fetched from
   `WorkspaceClient.postgres.generate_database_credential(endpoint=...)`
   before every connection so the credential rotates automatically.

2. Local development. The legacy `LAKEBASE_SECRET_SCOPE` / `LAKEBASE_SECRET_KEY`
   secret path is still supported for command-line testing.
"""

from __future__ import annotations

import base64
import os
from contextlib import contextmanager
from urllib.parse import urlsplit, urlunsplit

import psycopg2
from psycopg2.extras import RealDictCursor

try:
    from databricks.sdk import WorkspaceClient
except ModuleNotFoundError:  # pragma: no cover - SDK always present in Apps
    WorkspaceClient = None


_SCOPE = os.environ.get("LAKEBASE_SECRET_SCOPE", "database")
_KEY = os.environ.get("LAKEBASE_SECRET_KEY", "lakebase-url")
_ENDPOINT = os.environ.get(
    "LAKEBASE_ENDPOINT_NAME",
    "projects/weather-intelligence/branches/production/endpoints/primary",
)


def _workspace_client() -> WorkspaceClient | None:
    return WorkspaceClient() if WorkspaceClient else None


def _generate_token(w: WorkspaceClient) -> str:
    credential = w.postgres.generate_database_credential(endpoint=_ENDPOINT)
    return credential.token


def _legacy_url(w: WorkspaceClient | None) -> str:
    if w is None:
        raise RuntimeError("Databricks SDK is required for Lakebase access")
    secret = w.secrets.get_secret(scope=_SCOPE, key=_KEY)
    return base64.b64decode(secret.value).decode("utf-8")


def _connection_params(w: WorkspaceClient) -> dict:
    """Resolve connection params from env (preferred) or legacy secret."""
    host = os.environ.get("PGHOST")
    database = os.environ.get("PGDATABASE")
    user = os.environ.get("PGUSER")
    port = int(os.environ.get("PGPORT", "5432"))
    sslmode = os.environ.get("PGSSLMODE", "require")
    if host and database and user:
        return {
            "host": host,
            "port": port,
            "dbname": database.lstrip("/") or "weather",
            "user": user,
            "password": _generate_token(w),
            "sslmode": sslmode,
        }
    url = _legacy_url(w)
    parts = urlsplit(url)
    token = _generate_token(w) if "@" in url else (parts.password or "")
    return {
        "host": parts.hostname,
        "port": parts.port or 5432,
        "dbname": (parts.path or "/weather").lstrip("/") or "weather",
        "user": parts.username,
        "password": token,
        "sslmode": parts.query or "sslmode=require",
    }


@contextmanager
def get_connection():
    """Yield a fresh psycopg2 connection using a short-lived OAuth token."""
    w = _workspace_client()
    if w is None:
        raise RuntimeError("Databricks SDK is required for Lakebase access")
    params = _connection_params(w)
    print("[lakebase] params", {k:v if k!='password' else '***'+v[-6:] for k,v in params.items()}, flush=True)
    conn = psycopg2.connect(cursor_factory=RealDictCursor, **params)
    try:
        yield conn
    finally:
        conn.close()


def run_query(sql: str, params: tuple | dict | None = None) -> list[dict]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()


def run_write(sql: str, params: tuple | dict | None = None) -> int:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            conn.commit()
            return cur.rowcount


def run_returning(sql: str, params: tuple | dict | None = None) -> list[dict]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
            conn.commit()
            return [dict(row) for row in rows]
