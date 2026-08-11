"""FastMCP entrypoint for weather tools."""

import os

try:
    from fastmcp import FastMCP
except ImportError:
    FastMCP = None

try:
    from .weather_service import WeatherService
except ImportError:
    from weather_service import WeatherService


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


if __name__ == "__main__":
    if mcp is None:
        raise RuntimeError("FastMCP is required to run the weather MCP server")
    mcp.run(
        transport="streamable-http",
        host=os.environ.get("HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", os.environ.get("DATABRICKS_APP_PORT", "8000"))),
    )
