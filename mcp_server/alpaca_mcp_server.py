"""
Alpaca Markets paper-trading MCP server.

Exposes paper-trading tools over MCP (Model Context Protocol) so a
Databricks Agent Bricks agent can call them like any other tool:
    - get_quote(symbol)
    - place_order(account_id, symbol, side, quantity)
    - get_positions(account_id)
    - get_account_summary(account_id)
    - get_order_history(account_id, limit)
    - get_balance(account_id)

These tools are backed by Alpaca Markets' real, hosted paper-trading
account (see alpaca_broker.py).
"""

import logging
import os

import requests
from databricks.sdk import WorkspaceClient

import lakebase
import massive_broker
from alpaca_broker import (
    get_account_summary,
    get_order_history,
    get_positions,
    get_quote,
    place_order,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-server")

_w = WorkspaceClient()


def get_current_user() -> dict:
    """Get the current Databricks user for audit purposes."""
    try:
        user = _w.current_user.me()
        return {
            "status": "ok",
            "user_name": user.user_name,
            "user_id": user.id,
        }
    except Exception as e:
        logger.exception("Failed to get current user")
        return {
            "status": "error",
            "message": f"Failed to get current user: {str(e)}",
        }


def get_watchlist() -> list[dict]:
    """Get the current user's watchlist from Lakebase."""
    try:
        email = _current_user_email()
        with lakebase.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT symbol, latest_price, updated_at FROM watchlist WHERE email = %s ORDER BY symbol",
                    (email,),
                )
                rows = cur.fetchall()
                return [
                    {
                        "symbol": row["symbol"],
                        "latest_price": row.get("latest_price"),
                        "updated_at": row.get("updated_at"),
                    }
                    for row in rows
                ]
    except Exception as e:
        logger.exception("Failed to retrieve watchlist")
        return {
            "status": "error",
            "message": f"Failed to retrieve watchlist: {str(e)}",
        }


def add_to_watchlist(symbol: str) -> dict:
    """Add a symbol to the current user's watchlist."""
    try:
        symbol = symbol.strip().upper()
        email = _current_user_email()
        quote = massive_broker.get_quote(symbol)

        with lakebase.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO watchlist (symbol, email, latest_price, updated_at)
                    VALUES (%s, %s, %s, now())
                    ON CONFLICT (symbol, email) DO UPDATE
                        SET latest_price = EXCLUDED.latest_price,
                            updated_at = EXCLUDED.updated_at
                    """,
                    (symbol, email, quote["price"]),
                )
                conn.commit()

        return {
            "status": "ok",
            "symbol": symbol,
            "price": quote["price"],
        }
    except Exception as e:
        logger.exception(f"Failed to add {symbol} to watchlist")
        return {
            "status": "error",
            "message": f"Failed to add {symbol} to watchlist: {str(e)}",
        }


def remove_from_watchlist(symbol: str) -> dict:
    """Remove a symbol from the current user's watchlist."""
    try:
        symbol = symbol.strip().upper()
        email = _current_user_email()

        with lakebase.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM watchlist WHERE symbol = %s AND email = %s",
                    (symbol, email),
                )
                conn.commit()

        return {
            "status": "ok",
            "symbol": symbol,
            "removed": True,
        }
    except Exception as e:
        logger.exception(f"Failed to remove {symbol} from watchlist")
        return {
            "status": "error",
            "message": f"Failed to remove {symbol} from watchlist: {str(e)}",
        }


def save_research_note(symbol: str, title: str, content: str | None = None) -> dict:
    """Save a research note to the database for a ticker. Returns the created note."""
    try:
        symbol = symbol.strip().upper()
        result = lakebase.save_research_note(ticker=symbol, title=title, content=content)
        if result:
            return {
                "status": "ok",
                "id": result["id"],
                "ticker": result["ticker"],
                "title": result["title"],
                "created_at": str(result.get("created_at", "N/A")),
            }
        return {
            "status": "error",
            "message": "Failed to save research note",
        }
    except Exception as e:
        logger.exception(f"Failed to save research note for {symbol}")
        return {
            "status": "error",
            "message": f"Failed to save research note: {str(e)}",
        }


def save_analysis_report(symbol: str, report: dict | None = None, sources: list | None = None) -> dict:
    """Save an analysis report to the database for a ticker. Returns the created report."""
    try:
        symbol = symbol.strip().upper()
        result = lakebase.save_analysis_report(
            ticker=symbol,
            report=report or {},
            sources=sources or []
        )
        if result:
            return {
                "status": "ok",
                "id": result["id"],
                "ticker": result["ticker"],
                "created_at": str(result.get("created_at", "N/A")),
            }
        return {
            "status": "error",
            "message": "Failed to save analysis report",
        }
    except Exception as e:
        logger.exception(f"Failed to save analysis report for {symbol}")
        return {
            "status": "error",
            "message": f"Failed to save analysis report: {str(e)}",
        }


def _current_user_email() -> str:
    """Resolve the current user's email from Databricks request headers."""
    header_email = os.environ.get("DATABRICKS_CURRENT_USER_EMAIL")
    if header_email:
        return header_email
    return _w.current_user.me().user_name


def run_mcp_server():
    """
    Run the MCP server.

    Note: This is a placeholder for the actual FastMCP server. The real
    implementation would use fastmcp.run() with the tools defined above.

    For Databricks Apps, the MCP server runs as a separate app on port 8000.
    """
    logger.info("MCP Server initialized. Tools available:")
    logger.info("  - get_quote")
    logger.info("  - place_order")
    logger.info("  - get_positions")
    logger.info("  - get_account_summary")
    logger.info("  - get_order_history")
    logger.info("  - get_current_user")
    logger.info("  - get_watchlist")
    logger.info("  - add_to_watchlist")
    logger.info("  - remove_from_watchlist")
    logger.info("  - save_research_note (NEW)")
    logger.info("  - save_analysis_report (NEW)")
    logger.info("\nTo start the server, install fastmcp and run:")
    logger.info("  pip install fastmcp")
    logger.info("  python alpaca_mcp_server.py")


if __name__ == "__main__":
    run_mcp_server()
