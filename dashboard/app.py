"""
Dashboard Flask app - read-only view of the watchlist and prices.

This app is a simplified version of the original Day 2 app.py. It only
provides read operations for the watchlist, news, and prices - no write
or sync endpoints. This separation allows the MCP server to handle
trade operations while the dashboard provides human-readable feedback.

Run locally:
    python app.py
Deploy as a Databricks App using app.yaml.
"""

import logging
import os
import re

import requests
from databricks.sdk import WorkspaceClient
from flask import Flask, jsonify, render_template, request

from . import lakebase
from . import massive_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dashboard-app")

app = Flask(__name__)
_w = WorkspaceClient()

WATCHLIST_TABLE_NAME = os.environ.get("WATCHLIST_TABLE_NAME", "watchlist")
NEWS_TABLE_NAME = os.environ.get("NEWS_TABLE_NAME", "ticker_news_documents")
MASSIVE_TABLE_NAME = os.environ.get("MASSIVE_TABLE_NAME", "massive_records")

# Tickers to fetch news for by default (comma-separated)
DEFAULT_NEWS_TICKERS = [
    t.strip().upper()
    for t in os.environ.get("NEWS_TICKERS", "AAPL,MSFT,GOOGL,AMZN,TSLA").split(",")
    if t.strip()
]

_TICKER_RE = re.compile(r"^[A-Z]{1,10}(\.[A-Z]{1,2})?$")


def ensure_watchlist_table():
    """Create the watchlist table in Lakebase if it doesn't exist yet."""
    lakebase.run_write(
        f"""
        CREATE TABLE IF NOT EXISTS {WATCHLIST_TABLE_NAME} (
            symbol TEXT NOT NULL,
            email TEXT NOT NULL,
            latest_price NUMERIC,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            PRIMARY KEY (symbol, email)
        )
        """
    )


def ensure_news_table():
    """Create the news documents table in Lakebase if it doesn't exist yet."""
    lakebase.run_write(
        f"""
        CREATE TABLE IF NOT EXISTS {NEWS_TABLE_NAME} (
            id TEXT PRIMARY KEY,
            ticker TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            author TEXT,
            article_url TEXT,
            publisher_name TEXT,
            keywords JSONB,
            sentiment TEXT,
            sentiment_reasoning TEXT,
            published_utc TIMESTAMPTZ,
            payload JSONB NOT NULL,
            synced_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    lakebase.run_write(
        f"CREATE INDEX IF NOT EXISTS idx_{NEWS_TABLE_NAME}_ticker "
        f"ON {NEWS_TABLE_NAME} (ticker)"
    )


def _current_user_email() -> str:
    """
    Resolve the current user's email for the watchlist.

    Databricks Apps inject the logged-in user's identity via the
    X-Forwarded-Email header.
    """
    header_email = request.headers.get("X-Forwarded-Email")
    if header_email:
        return header_email
    return _w.current_user.me().user_name


@app.route("/healthz")
def healthz():
    return jsonify({"status": "ok"})


@app.errorhandler(Exception)
def handle_exception(err):
    """Ensure all unhandled errors return JSON."""
    logger.exception("Unhandled exception while processing request")
    status_code = getattr(err, "code", 500)
    if not isinstance(status_code, int):
        status_code = 500
    return jsonify({"error": str(err)}), status_code


@app.route("/")
def index():
    """Dashboard UI showing the watchlist."""
    return render_template("index.html")


@app.route("/api/watchlist")
def get_watchlist():
    """Return the current user's watchlist symbols with their last known price."""
    ensure_watchlist_table()
    email = _current_user_email()
    rows = lakebase.run_query(
        f"SELECT symbol, email, latest_price, updated_at FROM {WATCHLIST_TABLE_NAME} "
        f"WHERE email = %s ORDER BY symbol ASC",
        (email,),
    )
    return jsonify(rows)


@app.route("/api/news")
def get_news():
    """Return recent news for a ticker (for dashboard preview)."""
    ensure_news_table()
    ticker = request.args.get("ticker", "")
    if ticker:
        rows = lakebase.run_query(
            f"SELECT id, ticker, title, published_utc, sentiment "
            f"FROM {NEWS_TABLE_NAME} WHERE ticker = %s ORDER BY published_utc DESC LIMIT 20",
            (ticker,),
        )
        return jsonify(rows)
    else:
        rows = lakebase.run_query(
            f"SELECT id, ticker, title, published_utc, sentiment "
            f"FROM {NEWS_TABLE_NAME} ORDER BY published_utc DESC LIMIT 20"
        )
        return jsonify(rows)


@app.route("/api/quote")
def get_quote():
    """Fetch latest price for a single symbol from Massive (one API call)."""
    symbol = request.args.get("symbol", "").strip().upper()
    if not symbol:
        return jsonify({"error": "symbol query param is required"}), 400

    if not _TICKER_RE.match(symbol):
        return jsonify({"error": f"Invalid ticker symbol: {symbol!r}"}), 400

    client = massive_client.MassiveClient()
    try:
        data = client.get_latest_price(symbol)
    except requests.HTTPError:
        return jsonify({"error": f"Unknown ticker symbol: {symbol}"}), 400

    price = _extract_latest_price(data)
    if price is None:
        return jsonify({"error": f"No price data available for ticker: {symbol}"}), 400

    return jsonify({"symbol": symbol, "price": price})


@app.route("/api/account")
def api_account():
    """Account summary (placeholder - will be implemented with Alpaca broker)."""
    return jsonify({
        "cash": 100000.00,
        "positions": [],
        "total_equity": 100000.00,
        "account_id": "dashboard-read-only"
    })


@app.route("/api/orders")
def api_orders():
    """Order history (placeholder - will be implemented with Alpaca broker)."""
    return jsonify([])


@app.route("/api/positions")
def api_positions():
    """Positions (placeholder - will be implemented with Alpaca broker)."""
    return jsonify([])


def _extract_latest_price(data: dict) -> float | None:
    """Pull the trade price out of the Massive 'previous close' response."""
    if not isinstance(data, dict):
        return None
    if data.get("status") not in (None, "OK") or data.get("resultsCount") == 0:
        return None
    results = data.get("results", data)
    if isinstance(results, list):
        results = results[0] if results else None
    if isinstance(results, dict):
        for key in ("c", "p", "price", "last_price", "vw"):
            if key in results:
                return results[key]
    return None


if __name__ == '__main__':
    host = os.getenv('FLASK_RUN_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_RUN_PORT', 8001))
    app.run(debug=True, host=host, port=port)
    print(f"Dashboard app running on http://{host}:{port}")
