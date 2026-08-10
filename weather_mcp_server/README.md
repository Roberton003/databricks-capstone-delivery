# Weather-Prediction MCP Server

**Project status: In progress**

A small FastMCP server that gives a Databricks Agent Bricks agent weather data and a transparent umbrella recommendation. It uses Open-Meteo, which does not require an API key for this use case.

The local MCP implementation, prompt, tests, and App configuration are present. Databricks Workspace deployment, Agent Bricks registration, end-to-end validation, and the final App URL or screenshots are still pending.

---

## Current status

- **Implemented:** broker, service layer, MCP tools, App manifest, system prompt, tests, and documentation.
- **Validated locally:** unit tests, Python compilation, YAML parsing, and tool registration.
- **In progress:** Databricks App deployment and Agent Bricks integration.
- **Pending:** Workspace URL or screenshots and end-to-end validation through Agent Bricks.
- **Not claimed:** production readiness or completed Workspace deployment.

---

## Architecture

```text
Agent Bricks -> MCP tools -> WeatherService -> WeatherBroker -> Open-Meteo
```

`WeatherBroker` owns HTTP calls and normalizes the external API response. `WeatherService` validates inputs and applies the umbrella rule. `weather_mcp_server.py` exposes only serializable MCP tool results.

## Local setup

```bash
python3 -m venv weather_mcp_server/.venv
weather_mcp_server/.venv/bin/pip install -r weather_mcp_server/requirements.txt
python3 -m unittest weather_mcp_server.test_weather
python3 -m py_compile weather_mcp_server/*.py
```

Run the server with:

```bash
weather_mcp_server/.venv/bin/python weather_mcp_server/weather_mcp_server.py
```

No credentials are hardcoded or required by Open-Meteo. Network calls use an explicit timeout.

## Tools

- `get_current_weather(location)` returns resolved location, coordinates, and current temperature/precipitation.
- `get_forecast(location, days=3)` returns daily precipitation and maximum precipitation probability for 1–16 days.
- `predict_umbrella_needed(location, days=1)` returns the forecast days and a recommendation.

The recommendation is `true` when precipitation is greater than zero or precipitation probability is at least 50%; it is a rule-based recommendation, not a new meteorological model.

## Agent Bricks configuration

1. Deploy this directory as a Databricks App when the target Workspace is available.
2. Register the App's MCP endpoint in the Agent Bricks agent tool configuration.
3. Use the contents of `SYSTEM_PROMPT.md` as the agent's system instructions.
4. Test ambiguous locations, invalid day counts, current-weather questions, forecast questions, and recommendation questions.

The exact endpoint and Workspace resource identifiers are environment-specific and are intentionally not committed here. Workspace deployment remains pending.

## Example questions

- “What is the current weather in Lisbon?”
- “What is the forecast for Porto for the next three days?”
- “Should I bring an umbrella in London tomorrow?”
- “Which Lisbon do you mean?” should be asked when the location cannot be resolved confidently.

## Validation status

- `IMPLEMENTED`: broker, service, MCP tools, App manifest, prompt, and documentation are present in this directory.
- `VALIDATED`: local unit tests and Python compilation after implementation.
- `UNKNOWN`: Databricks Workspace deployment and Agent Bricks runtime behavior until deployment is authorized and performed.
