"""Flask dashboard for Lakebase-backed watchlist, news, prices, and weather search."""

import logging
import os
import re

import requests
from flask import Flask, jsonify, render_template, request

try:
    from databricks.sdk import WorkspaceClient
except ModuleNotFoundError:
    WorkspaceClient = None

try:
    from . import lakebase, massive_client
    from .weather_client import WeatherClient
    from .weather_search import search as search_weather
    from .weather_sync import sync_locations
except ImportError:
    import lakebase
    import massive_client
    from weather_client import WeatherClient
    from weather_search import search as search_weather
    from weather_sync import sync_locations


# Keep package and direct-script execution compatible with the App command.
try:
    from . import weather_search as _weather_search_module
    from . import weather_sync as _weather_sync_module
except ImportError:
    import weather_search as _weather_search_module
    import weather_sync as _weather_sync_module

_weather_search_module.lakebase = lakebase
_weather_sync_module.lakebase = lakebase


def _load_workspace_client():
    return WorkspaceClient() if WorkspaceClient else None


_w = _load_workspace_client()


app = Flask(__name__)
logger = logging.getLogger("dashboard-app")

WATCHLIST_TABLE_NAME = os.environ.get("WATCHLIST_TABLE_NAME", "watchlist")
NEWS_TABLE_NAME = os.environ.get("NEWS_TABLE_NAME", "ticker_news_documents")
MASSIVE_TABLE_NAME = os.environ.get("MASSIVE_TABLE_NAME", "massive_records")
DEFAULT_NEWS_TICKERS = [
    ticker.strip().upper()
    for ticker in os.environ.get("NEWS_TICKERS", "AAPL,MSFT,GOOGL,AMZN,TSLA").split(",")
    if ticker.strip()
]
_TICKER_RE = re.compile(r"^[A-Z]{1,10}(\.[A-Z]{1,2})?$")


def ensure_watchlist_table():
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


def _current_user_email():
    header_email = request.headers.get("X-Forwarded-Email")
    if header_email:
        return header_email
    if _w is None:
        return "anonymous"
    return _w.current_user.me().user_name


def _http_error_response(error):
    response = getattr(error, "response", None)
    status_code = getattr(response, "status_code", 502) or 502
    return jsonify({"error": str(error)}), status_code


@app.route("/healthz")
def healthz():
    return jsonify({"status": "ok"})


@app.route("/weather/sync", methods=["POST"])
def weather_sync():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "request body must be a JSON object"}), 400

    locations = payload.get("locations")
    limit = payload.get("limit", 50)
    if not isinstance(locations, list) or not locations:
        return jsonify({"error": "locations must be a non-empty list"}), 400
    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 200:
        return jsonify({"error": "limit must be an integer between 1 and 200"}), 400

    try:
        count = sync_locations(WeatherClient(), locations, limit)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except requests.RequestException as error:
        return _http_error_response(error)
    return jsonify({"synced": count})


@app.route("/weather/search", methods=["POST"])
def weather_search():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "request body must be a JSON object"}), 400

    query = payload.get("query")
    top_k = payload.get("top_k", 5)
    if not isinstance(query, str) or not query.strip():
        return jsonify({"error": "query must be a non-empty string"}), 400
    if not isinstance(top_k, int) or isinstance(top_k, bool) or not 1 <= top_k <= 20:
        return jsonify({"error": "top_k must be an integer between 1 and 20"}), 400

    try:
        return jsonify({"results": search_weather(query.strip(), top_k)})
    except requests.RequestException as error:
        return _http_error_response(error)


@app.errorhandler(Exception)
def handle_exception(err):
    logger.exception("Unhandled exception while processing request")
    status_code = getattr(err, "code", 500)
    if not isinstance(status_code, int):
        status_code = 500
    return jsonify({"error": str(err)}), status_code


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/watchlist")
def get_watchlist():
    ensure_watchlist_table()
    rows = lakebase.run_query(
        f"SELECT symbol, email, latest_price, updated_at FROM {WATCHLIST_TABLE_NAME} "
        "WHERE email = %s ORDER BY symbol ASC",
        (_current_user_email(),),
    )
    return jsonify(rows)


@app.route("/api/watchlist/<symbol>", methods=["POST"])
def add_watchlist(symbol):
    if not _TICKER_RE.fullmatch(symbol.upper()):
        return jsonify({"error": f"Invalid ticker symbol: {symbol!r}"}), 400
    ensure_watchlist_table()
    email = _current_user_email()
    rows = lakebase.run_returning(
        f"""INSERT INTO {WATCHLIST_TABLE_NAME} (symbol, email, updated_at)
        VALUES (%s, %s, now())
        ON CONFLICT (symbol, email) DO UPDATE SET updated_at = now()
        RETURNING symbol, email, latest_price, updated_at""",
        (symbol.upper(), email),
    )
    return jsonify(rows[0]), 201


@app.route("/api/watchlist/<symbol>", methods=["DELETE"])
def remove_watchlist(symbol):
    if not _TICKER_RE.fullmatch(symbol.upper()):
        return jsonify({"error": f"Invalid ticker symbol: {symbol!r}"}), 400
    rows = lakebase.run_query(
        f"DELETE FROM {WATCHLIST_TABLE_NAME} WHERE symbol = %s AND email = %s RETURNING symbol, email",
        (symbol.upper(), _current_user_email()),
    )
    if not rows:
        return jsonify({"deleted": False, "symbol": symbol.upper()}), 404
    return jsonify({"deleted": True, **rows[0]})


@app.route("/api/news")
def get_news():
    ensure_news_table()
    ticker = request.args.get("ticker", "")
    if ticker:
        rows = lakebase.run_query(
            f"SELECT id, ticker, title, published_utc, sentiment FROM {NEWS_TABLE_NAME} "
            "WHERE ticker = %s ORDER BY published_utc DESC LIMIT 20",
            (ticker,),
        )
    else:
        rows = lakebase.run_query(
            f"SELECT id, ticker, title, published_utc, sentiment FROM {NEWS_TABLE_NAME} "
            "ORDER BY published_utc DESC LIMIT 20"
        )
    return jsonify(rows)


@app.route("/api/quote")
def get_quote():
    symbol = request.args.get("symbol", "").strip().upper()
    if not symbol:
        return jsonify({"error": "symbol query param is required"}), 400
    if not _TICKER_RE.match(symbol):
        return jsonify({"error": f"Invalid ticker symbol: {symbol!r}"}), 400

    try:
        data = massive_client.MassiveClient().get_latest_price(symbol)
    except requests.HTTPError:
        return jsonify({"error": f"Unknown ticker symbol: {symbol}"}), 400
    price = _extract_latest_price(data)
    if price is None:
        return jsonify({"error": f"No price data available for ticker: {symbol}"}), 400
    return jsonify({"symbol": symbol, "price": price})


@app.route("/api/account")
def api_account():
    return jsonify({
        "cash": 100000.00,
        "positions": [],
        "total_equity": 100000.00,
        "account_id": "dashboard-read-only",
    })


@app.route("/api/orders")
def api_orders():
    return jsonify([])


@app.route("/api/positions")
def api_positions():
    return jsonify([])


def _extract_latest_price(data: dict) -> float | None:
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


if __name__ == "__main__":
    host = os.getenv("FLASK_RUN_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_RUN_PORT", 8001))
    app.run(debug=True, host=host, port=port)

