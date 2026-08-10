"""
Script para iniciar o servidor MCP localmente.

Este script configura as variáveis de ambiente necessárias e inicia
o servidor FastMCP para teste e desenvolvimento.
"""

import os
import sys

# Configurar variáveis de ambiente (substituir com seus valores reais)
os.environ.setdefault("LAKEBASE_SECRET_SCOPE", "database")
os.environ.setdefault("LAKEBASE_SECRET_KEY", "lakebase-url")

# Importar e iniciar o servidor
from mcp_server import mcp

if __name__ == "__main__":
    print("=" * 60)
    print("Stock-Market Research Assistant - MCP Server")
    print("=" * 60)
    print("")
    print("Iniciando servidor FastMCP...")
    print("")
    print("Ferramentas disponíveis:")
    print("  1. get_quote - Get stock price for a ticker")
    print("  2. search_news - Search news for a ticker")
    print("  3. search_research_context - Semantic search on news")
    print("  4. get_watchlist - Get tracked tickers")
    print("  5. add_to_watchlist - Add ticker to watchlist")
    print("  6. remove_from_watchlist - Remove ticker from watchlist")
    print("  7. save_research_note - Save research notes")
    print("  8. save_analysis_report - Save analysis report")
    print("")
    print("O servidor está rodando no endpoint HTTP padrão (localhost:3000)")
    print("")

    try:
        mcp.run()
    except KeyboardInterrupt:
        print("\nServidor MCP encerrado.")
        sys.exit(0)
    except Exception as e:
        print(f"Erro ao iniciar servidor: {e}")
        sys.exit(1)
