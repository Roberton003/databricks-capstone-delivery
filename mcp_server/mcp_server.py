"""
FastMCP Server - Stock-Market Research Assistant Tools

Este servidor expõe ferramentas MCP para leitura e escrita sobre o mercado de ações.

Ferramentas de Leitura:
- get_quote(symbol): Preço atual de um ticker
- search_news(symbol, query, limit): Buscar notícias por ticker e query
- search_research_context(query, symbol): Busca semântica de contexto
- get_watchlist(): Lista tickers da watchlist

Ferramentas de Escrita (Agente):
- add_to_watchlist(symbol): Adicionar ticker à watchlist
- remove_from_watchlist(symbol): Remover ticker da watchlist
- save_research_note(symbol, title, content): Salvar nota de pesquisa
- save_analysis_report(symbol, report, sources): Salvar relatório de análise
"""

import logging
import os
from typing import Optional

from fastmcp import FastMCP
from pydantic import BaseModel, Field

import lakebase
import massive_broker

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-server")

# Initialize FastMCP
mcp = FastMCP(
    name="stock-market-assistant",
    version="1.0.0",
    description="Tools for stock market research, news, and analysis"
)

# ============================================================================
# Tool: Get Quote (Leitura)
# ============================================================================

@mcp.tool(
    name="get_quote",
    description="Get the current stock price for a given ticker symbol"
)
def get_quote(symbol: str) -> dict:
    """
    Get the current stock price for a ticker.

    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT)

    Returns:
        dict with price, change, volume and other market data
    """
    try:
        symbol = symbol.strip().upper()
        result = massive_broker.get_quote(symbol)
        return {
            "status": "ok",
            "symbol": symbol,
            "price": result.get("price"),
            "change": result.get("change"),
            "change_percent": result.get("change_percent"),
            "volume": result.get("volume"),
        }
    except ValueError as e:
        logger.warning(f"Invalid symbol: {symbol}")
        return {"status": "error", "message": str(e)}
    except Exception as e:
        logger.exception(f"Failed to get quote for {symbol}")
        return {"status": "error", "message": f"Failed to get quote: {str(e)}"}


# ============================================================================
# Tool: Search News (Leitura)
# ============================================================================

@mcp.tool(
    name="search_news",
    description="Search recent news articles for a ticker symbol"
)
def search_news(
    symbol: str,
    query: Optional[str] = None,
    limit: int = 10
) -> list[dict]:
    """
    Search for recent news articles about a ticker.

    Args:
        symbol: Stock ticker symbol
        query: Optional search query to filter news
        limit: Maximum number of results to return (default: 10)

    Returns:
        List of news articles with titles, summaries, and URLs
    """
    try:
        symbol = symbol.strip().upper()
        results = massive_broker.search_news(symbol, query, limit)
        return [
            {
                "title": article.get("title"),
                "summary": article.get("description"),
                "url": article.get("article_url"),
                "published": str(article.get("published_utc")),
                "publisher": article.get("publisher_name"),
            }
            for article in results
        ]
    except Exception as e:
        logger.exception(f"Failed to search news for {symbol}")
        return [{"error": f"Failed to search news: {str(e)}"}]


# ============================================================================
# Tool: Search Research Context (Leitura - RAG)
# ============================================================================

@mcp.tool(
    name="search_research_context",
    description="Search for relevant research context using semantic search on stock news"
)
def search_research_context(
    query: str,
    symbol: Optional[str] = None,
    limit: int = 5
) -> list[dict]:
    """
    Search for relevant news chunks using semantic similarity.

    Args:
        query: Natural language search query
        symbol: Optional ticker to filter by
        limit: Maximum number of results to return

    Returns:
        List of relevant text chunks with similarity scores
    """
    try:
        # Use pgvector for semantic search
        sql = """
            SELECT
                c.chunk_text as text,
                e.title,
                e.published_utc,
                e.ticker,
                1 - (c.embedding <-> %s::vector) as similarity
            FROM ticker_news_chunk_embeddings c
            JOIN ticker_news_embeddings e ON c.document_id = e.id
            WHERE c.embedding IS NOT NULL
        """
        params = [query]
        if symbol:
            sql += " AND e.ticker = %s"
            params.append(symbol.upper())
        sql += " ORDER BY similarity DESC LIMIT %s"

        results = lakebase.run_query(sql, params)
        return [
            {
                "text": r["text"],
                "ticker": r["ticker"],
                "title": r["title"],
                "published": str(r["published_utc"]),
                "similarity": float(r["similarity"]),
            }
            for r in results
        ]
    except Exception as e:
        logger.exception("Failed to search research context")
        return [{"error": f"Search failed: {str(e)}"}]


# ============================================================================
# Tool: Get Watchlist (Leitura)
# ============================================================================

@mcp.tool(
    name="get_watchlist",
    description="Get the current user's watchlist of tracked tickers"
)
def get_watchlist() -> list[str]:
    """
    Get all tickers in the current user's watchlist.

    Returns:
        List of ticker symbols
    """
    try:
        result = massive_broker.get_watchlist()
        return result.get("tickers", [])
    except Exception as e:
        logger.exception("Failed to get watchlist")
        return [{"error": f"Failed to get watchlist: {str(e)}"}]


# ============================================================================
# Tool: Add to Watchlist (Escrita)
# ============================================================================

@mcp.tool(
    name="add_to_watchlist",
    description="Add a ticker symbol to the user's watchlist"
)
def add_to_watchlist(symbol: str) -> dict:
    """
    Add a stock ticker to your watchlist.

    Args:
        symbol: Stock ticker symbol to add

    Returns:
        Confirmation with symbol and status
    """
    try:
        symbol = symbol.strip().upper()
        result = massive_broker.add_to_watchlist(symbol)
        return result
    except Exception as e:
        logger.exception(f"Failed to add {symbol} to watchlist")
        return {"status": "error", "message": f"Failed to add to watchlist: {str(e)}"}


# ============================================================================
# Tool: Remove from Watchlist (Escrita)
# ============================================================================

@mcp.tool(
    name="remove_from_watchlist",
    description="Remove a ticker symbol from the user's watchlist"
)
def remove_from_watchlist(symbol: str) -> dict:
    """
    Remove a stock ticker from your watchlist.

    Args:
        symbol: Stock ticker symbol to remove

    Returns:
        Confirmation with symbol and status
    """
    try:
        symbol = symbol.strip().upper()
        result = massive_broker.remove_from_watchlist(symbol)
        return result
    except Exception as e:
        logger.exception(f"Failed to remove {symbol} from watchlist")
        return {"status": "error", "message": f"Failed to remove from watchlist: {str(e)}"}


# ============================================================================
# Tool: Save Research Note (Escrita)
# ============================================================================

@mcp.tool(
    name="save_research_note",
    description="Save a research note for a ticker to the database"
)
def save_research_note(symbol: str, title: str, content: str) -> dict:
    """
    Save a research note about a stock.

    Args:
        symbol: Stock ticker symbol
        title: Note title
        content: Detailed research content

    Returns:
        Confirmation with note ID and metadata
    """
    try:
        symbol = symbol.strip().upper()
        result = lakebase.save_research_note(symbol, title, content)
        if result:
            return {
                "status": "ok",
                "note_id": result["id"],
                "ticker": result["ticker"],
                "title": result["title"],
                "created_at": str(result.get("created_at")),
            }
        return {"status": "error", "message": "Failed to save note"}
    except Exception as e:
        logger.exception(f"Failed to save research note for {symbol}")
        return {"status": "error", "message": f"Failed to save note: {str(e)}"}


# ============================================================================
# Tool: Save Analysis Report (Escrita)
# ============================================================================

@mcp.tool(
    name="save_analysis_report",
    description="Save an analysis report for a ticker to the database"
)
def save_analysis_report(symbol: str, report: dict, sources: Optional[list] = None) -> dict:
    """
    Save a complete analysis report for a stock.

    Args:
        symbol: Stock ticker symbol
        report: Dictionary containing analysis content (key findings, recommendations, etc.)
        sources: Optional list of source URLs used in the analysis

    Returns:
        Confirmation with report ID and metadata
    """
    try:
        symbol = symbol.strip().upper()
        result = lakebase.save_analysis_report(symbol, report, sources or [])
        if result:
            return {
                "status": "ok",
                "report_id": result["id"],
                "ticker": result["ticker"],
                "created_at": str(result.get("created_at")),
            }
        return {"status": "error", "message": "Failed to save report"}
    except Exception as e:
        logger.exception(f"Failed to save analysis report for {symbol}")
        return {"status": "error", "message": f"Failed to save report: {str(e)}"}


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    logger.info("Starting Stock-Market Research Assistant MCP Server")
    logger.info("Available tools:")
    logger.info("  - get_quote")
    logger.info("  - search_news")
    logger.info("  - search_research_context")
    logger.info("  - get_watchlist")
    logger.info("  - add_to_watchlist")
    logger.info("  - remove_from_watchlist")
    logger.info("  - save_research_note")
    logger.info("  - save_analysis_report")
    logger.info("")
    logger.info("To run the server, execute:")
    logger.info("  python mcp_server.py")
    logger.info("")
    logger.info("For Databricks Agent Bricks, deploy this as a Databricks App.")
    logger.info("")
    mcp.run()
