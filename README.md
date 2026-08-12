# Weather Intelligence

Databricks AI Bootcamp capstone: a weather intelligence service that ingests National Weather Service data, creates 384-dimensional embeddings, stores them in Lakebase Postgres with pgvector, and exposes grounded retrieval through a dashboard and MCP server.

## Architecture

- **Ingestion:** Python notebook fetches NWS observations, alerts, and forecasts.
- **Storage:** Lakebase Autoscaling Postgres stores weather documents and `VECTOR(384)` embeddings with an HNSW index.
- **Retrieval:** Flask `POST /weather/search` embeds a query and performs parameterized cosine-distance search.
- **MCP:** FastMCP exposes `get_current_weather`, `get_forecast`, `predict_umbrella_needed`, `save_weather_note`, `add_weather_watchlist`, and `remove_weather_watchlist`.
- **Apps:** `weather-dashboard` serves the browser UI; `weather-mcp` is attached to the Agent Bricks supervisor agent.

## Repository layout

```text
dashboard/                         Flask app, Lakebase helpers, weather UI
weather_mcp_server/                FastMCP service and write tools
notebooks/ingest_weather_embeddings.py
sql/05_setup_weather_documents.sql
sql/06_setup_weather_embeddings.sql
sql/07_setup_research_notes.sql
resources/                         Databricks bundle resources
docs/EVIDENCIAS_WEATHER.md        Evidence mapping and validation notes
evidence/                          Reproducible execution evidence
submissions/                       Three capstone submission archives
```

## Run locally

```bash
pip install -r dashboard/requirements.txt
FLASK_APP=dashboard.app flask run --port 8001
```

The deployed Apps receive Lakebase access through Databricks Secrets. Do not place connection URLs, OAuth tokens, or other credentials in Git.

## API examples

```bash
curl -X POST http://localhost:8001/weather/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"heavy rain in Lisbon","top_k":5}'

curl http://localhost:8001/api/watchlist
curl -X POST http://localhost:8001/api/watchlist/LISBON
curl -X DELETE http://localhost:8001/api/watchlist/LISBON
```

## Validation evidence

The implementation and runtime evidence are mapped in [`docs/EVIDENCIAS_WEATHER.md`](docs/EVIDENCIAS_WEATHER.md). The three submission packages are:

- `submissions/vector-weather-retrieval-service.zip`
- `submissions/build-your-own-weather-mcp-server.zip`
- `submissions/capstone-project-submission.zip`

Each archive has a companion SHA-256 checksum file.

## Security

Secrets remain in Databricks Secret Scopes. All user-scoped writes use the authenticated email and parameterized SQL. The dashboard and MCP write paths do not accept a caller-supplied identity in place of the authenticated identity when deployed behind Databricks Apps.
