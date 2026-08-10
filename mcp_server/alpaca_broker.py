"""
Alpaca Markets paper-trading engine backing the MCP server.

This module is a thin wrapper around Alpaca's real, hosted paper-trading
account via alpaca-py (https://alpaca.markets/sdks/python/).
Quotes, fills, positions, cash, and order history are all real Alpaca
paper-trading data.

Alpaca's paper trading is one account per API key pair, so account_id
is accepted for signature compatibility but is not used to select an account.
"""

import base64
import os

import requests
from databricks.sdk import WorkspaceClient

_w = WorkspaceClient()

_SECRET_SCOPE = os.environ.get("ALPACA_SECRET_SCOPE", "database")
_KEY_ID_SECRET_KEY = os.environ.get("ALPACA_KEY_ID_SECRET_KEY", "alpaca-key-id")
_SECRET_KEY_SECRET_KEY = os.environ.get("ALPACA_SECRET_KEY_SECRET_KEY", "alpaca-secret-key")

_base_url = "https://api.alpaca.markets"
_paper_base_url = "https://paper-api.alpaca.markets"

_api_key: str | None = None
_api_secret: str | None = None


def _secret(key: str) -> str:
    """Fetch and base64-decode a value from the Databricks secret scope."""
    secret = _w.secrets.get_secret(scope=_SECRET_SCOPE, key=key)
    return base64.b64decode(secret.value).decode("utf-8")


def _get_api_key() -> str:
    global _api_key
    if _api_key is None:
        _api_key = _secret(_KEY_ID_SECRET_KEY)
    return _api_key


def _get_api_secret() -> str:
    global _api_secret
    if _api_secret is None:
        _api_secret = _secret(_SECRET_KEY_SECRET_KEY)
    return _api_secret


def _get_auth_headers() -> dict:
    """Get basic auth headers for Alpaca API."""
    return {
        "Content-Type": "application/json",
        "APCA-API-KEY-ID": _get_api_key(),
        "APCA-API-SECRET-KEY": _get_api_secret(),
    }


def _request(method: str, path: str, **kwargs) -> dict:
    """Make a request to Alpaca API."""
    url = f"{_paper_base_url}{path}"
    resp = requests.request(
        method,
        url,
        headers=_get_auth_headers(),
        timeout=30,
        **kwargs,
    )
    resp.raise_for_status()
    return resp.json()


def get_quote(symbol: str) -> dict:
    """
    Get latest quote for a stock ticker symbol from Alpaca.

    Args:
        symbol: Stock ticker symbol, e.g. "AAPL".

    Returns:
        A dict with symbol, price, volume, change, change_percent.
    """
    symbol = symbol.strip().upper()
    resp = _request("GET", f"/v2/stocks/{symbol}/trades/latest")
    trade = resp.get("trade", {})
    return {
        "symbol": symbol,
        "price": trade.get("p", 0),
        "volume": trade.get("s", 0),
        "as_of": trade.get("t", ""),
        "timestamp": trade.get("t", ""),
    }


def place_order(account_id: str, symbol: str, side: str, quantity: float) -> dict:
    """
    Place a market order for the Alpaca paper trading account.

    Args:
        account_id: Accepted for signature compatibility; not used.
        symbol: Stock ticker symbol, e.g. "AAPL".
        side: "BUY" or "SELL".
        quantity: Number of shares to trade.

    Returns:
        A dict describing the order (id, symbol, side, quantity, price, status).
    """
    symbol = symbol.strip().upper()
    side = side.upper()
    if side not in ("BUY", "SELL"):
        raise ValueError(f"side must be 'BUY' or 'SELL', got {side!r}")
    if quantity <= 0:
        raise ValueError(f"quantity must be positive, got {quantity!r}")

    resp = _request(
        "POST",
        "/v2/orders",
        json={
            "symbol": symbol,
            "qty": str(int(quantity)),
            "side": side,
            "type": "market",
            "time_in_force": "day",
        },
    )
    return {
        "id": resp.get("id"),
        "symbol": resp.get("symbol"),
        "side": resp.get("side"),
        "quantity": float(resp.get("qty", 0)),
        "status": resp.get("status"),
        "created_at": resp.get("created_at"),
    }


def get_positions(account_id: str) -> list[dict]:
    """
    Get all open positions for the Alpaca paper trading account.

    Args:
        account_id: Accepted for signature compatibility; not used.

    Returns:
        A list of dicts, each with symbol, qty, avg_entry_price, market_value.
    """
    resp = _request("GET", "/v2/positions")
    positions = []
    for pos in resp:
        positions.append({
            "symbol": pos.get("symbol"),
            "qty": float(pos.get("qty", 0)),
            "avg_entry_price": float(pos.get("avg_entry_price", 0)),
            "market_value": float(pos.get("market_value", 0)),
            "cost_basis": float(pos.get("cost_basis", 0)),
        })
    return positions


def get_account_summary(account_id: str) -> dict:
    """
    Get account summary for the Alpaca paper trading account.

    Args:
        account_id: Accepted for signature compatibility; not used.

    Returns:
        A dict with cash, equity, buying_power, total_equity, etc.
    """
    resp = _request("GET", "/v2/account")
    return {
        "account_id": resp.get("id"),
        "account_number": resp.get("account_number"),
        "status": resp.get("status"),
        "cash": float(resp.get("cash", 0)),
        "buying_power": float(resp.get("buying_power", 0)),
        "equity": float(resp.get("equity", 0)),
        "total_equity": float(resp.get("total_equity", 0)),
        "day_trading_buying_power": float(resp.get("day_trading_buying_power", 0)),
        "long_market_value": float(resp.get("long_market_value", 0)),
        "short_market_value": float(resp.get("short_market_value", 0)),
        "pattern_day_trader": resp.get("pattern_day_trader", False),
    }


def get_order_history(account_id: str, limit: int = 50) -> list[dict]:
    """
    Get recent orders for the Alpaca paper trading account.

    Args:
        account_id: Accepted for signature compatibility; not used.
        limit: Maximum number of orders to return.

    Returns:
        A list of dicts describing orders.
    """
    resp = _request("GET", "/v2/orders", params={"status": "all", "limit": limit})
    orders = []
    for o in resp:
        orders.append({
            "id": o.get("id"),
            "symbol": o.get("symbol"),
            "side": o.get("side"),
            "qty": float(o.get("qty", 0)),
            "filled_qty": float(o.get("filled_qty", 0)),
            "status": o.get("status"),
            "created_at": o.get("created_at"),
            "filled_at": o.get("filled_at"),
        })
    return orders
