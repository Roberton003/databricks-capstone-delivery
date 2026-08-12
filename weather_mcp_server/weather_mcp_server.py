"""FastMCP entrypoint for weather tools."""

import os

try:
    from fastmcp import FastMCP
except ImportError:
    FastMCP = None

try:
    from .weather_service import WeatherService
    from .weather_notes import (
        add_to_watchlist,
        remove_from_watchlist,
        save_research_note,
    )
except ImportError:
    from weather_service import WeatherService
    from weather_notes import add_to_watchlist, remove_from_watchlist, save_research_note


service = WeatherService()
mcp = FastMCP("Weather Forecast MCP") if FastMCP else None


def _error_response(error):
    return {"error": str(error)}


if mcp:
    @mcp.tool()
    def get_current_weather(location: str):
        """Get current weather for a city or place."""
        try:
            return service.get_current_weather(location)
        except (ValueError, OSError) as error:
            return _error_response(error)

    @mcp.tool()
    def get_forecast(location: str, days: int = 3):
        """Get a daily precipitation forecast for a location."""
        try:
            return service.get_forecast(location, days)
        except (ValueError, OSError) as error:
            return _error_response(error)

    @mcp.tool()
    def predict_umbrella_needed(location: str, days: int = 1):
        """Recommend whether an umbrella is useful based on forecast data."""
        try:
            return service.predict_umbrella_needed(location, days)
        except (ValueError, OSError) as error:
            return _error_response(error)

    @mcp.tool()
    def save_weather_note(location: str, title: str, content: str, owner_email: str):
        """Save a weather research note for the authenticated user."""
        try:
            return save_research_note(location, title, content, owner_email)
        except (ValueError, OSError, RuntimeError) as error:
            return _error_response(error)

    @mcp.tool()
    def add_weather_watchlist(symbol: str, owner_email: str):
        """Add a symbol to the authenticated user's watchlist."""
        try:
            return add_to_watchlist(symbol, owner_email)
        except (ValueError, OSError, RuntimeError) as error:
            return _error_response(error)

    @mcp.tool()
    def remove_weather_watchlist(symbol: str, owner_email: str):
        """Remove a symbol from the authenticated user's watchlist."""
        try:
            return remove_from_watchlist(symbol, owner_email)
        except (ValueError, OSError, RuntimeError) as error:
            return _error_response(error)


if __name__ == "__main__":
    if mcp is None:
        raise RuntimeError("FastMCP is required to run the weather MCP server")
    mcp.run(
        transport="streamable-http",
        host=os.environ.get("HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", os.environ.get("DATABRICKS_APP_PORT", "8000"))),
    )
