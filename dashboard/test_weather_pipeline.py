import json
import sys
import types
import unittest
from unittest.mock import patch


if "databricks.sdk" not in sys.modules:
    databricks = types.ModuleType("databricks")
    databricks_sdk = types.ModuleType("databricks.sdk")

    class WorkspaceClient:
        def __init__(self):
            self.current_user = types.SimpleNamespace(
                me=lambda: types.SimpleNamespace(user_name="test@example.com")
            )

    databricks_sdk.WorkspaceClient = WorkspaceClient
    databricks.sdk = databricks_sdk
    sys.modules["databricks"] = databricks
    sys.modules["databricks.sdk"] = databricks_sdk


# The local test environment does not need Databricks authentication.


if "dashboard.lakebase" not in sys.modules:
    pass


if "databricks.sdk" not in sys.modules:
    raise AssertionError("Databricks SDK test stub was not installed")


class WeatherClientTests(unittest.TestCase):
    def test_normalizes_alert_feature(self):
        from dashboard.weather_client import WeatherClient

        feature = {
            "id": "https://api.weather.gov/alerts/123",
            "properties": {
                "event": "Flood Warning",
                "headline": "Flood warning issued",
                "description": "Move to higher ground.",
                "sent": "2026-08-10T12:00:00+00:00",
                "effective": "2026-08-10T12:30:00+00:00",
            },
        }

        document = WeatherClient.normalize_alert(feature, "Chicago, IL")

        self.assertEqual(document["id"], "https://api.weather.gov/alerts/123")
        self.assertEqual(document["source_type"], "alert")
        self.assertEqual(document["location"], "Chicago, IL")
        self.assertIn("Flood warning issued", document["narrative_text"])

    def test_normalizes_forecast_period(self):
        from dashboard.weather_client import WeatherClient

        period = {
            "number": 1,
            "name": "Today",
            "startTime": "2026-08-10T12:00:00-05:00",
            "endTime": "2026-08-10T18:00:00-05:00",
            "temperature": 80,
            "temperatureUnit": "F",
            "shortForecast": "Mostly sunny",
            "detailedForecast": "Mostly sunny with a high near 80.",
        }

        document = WeatherClient.normalize_forecast(period, "Chicago, IL")

        self.assertEqual(document["id"], "forecast:Chicago, IL:1")
        self.assertEqual(document["source_type"], "forecast")
        self.assertIn("Mostly sunny with a high near 80.", document["narrative_text"])


class WeatherEndpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from dashboard.app import app

        cls.client = app.test_client()

    def test_sync_rejects_invalid_locations(self):
        response = self.client.post(
            "/weather/sync",
            data=json.dumps({"locations": []}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    def test_search_rejects_missing_query(self):
        response = self.client.post(
            "/weather/search",
            json={"top_k": 5},
        )

        self.assertEqual(response.status_code, 400)

    def test_search_rejects_invalid_top_k(self):
        response = self.client.post(
            "/weather/search",
            json={"query": "flood", "top_k": 21},
        )

        self.assertEqual(response.status_code, 400)

    @patch("dashboard.lakebase._generate_token", return_value="oauth-token")
    @patch("dashboard.lakebase._legacy_url", return_value="postgresql://roberto.m0010%2540gmail.com:secret@db.example:5432/weather?sslmode=require")
    def test_legacy_connection_params_use_decoded_identity_and_valid_sslmode(self, legacy_url, generate_token):
        from dashboard import lakebase

        params = lakebase._connection_params(object())

        self.assertEqual(params["sslmode"], "require")
        self.assertEqual(params["user"], "roberto.m0010@gmail.com")
        self.assertEqual(params["password"], "oauth-token")

    def test_generate_token_uses_rest_fallback_for_older_sdk(self):
        from dashboard import lakebase

        calls = []

        class ApiClient:
            def do(self, method, path, body):
                calls.append((method, path, body))
                return {"token": "rest-oauth-token"}

        workspace = types.SimpleNamespace(api_client=ApiClient())

        self.assertEqual(lakebase._generate_token(workspace), "rest-oauth-token")
        self.assertEqual(calls, [("POST", "/api/2.0/postgres/credentials", {
            "endpoint": lakebase._ENDPOINT,
        })])

    @patch.dict("os.environ", {
        "PGHOST": "db.example",
        "PGDATABASE": "weather",
        "PGUSER": "roberto.m0010%2540gmail.com",
    }, clear=False)

    @patch("dashboard.lakebase._generate_token", return_value="oauth-token")
    def test_app_connection_params_use_lakebase_database_identity(self, generate_token):
        from dashboard import lakebase

        workspace = types.SimpleNamespace(
            current_user=types.SimpleNamespace(
                me=lambda: types.SimpleNamespace(user_name="different@example.com")
            )
        )

        params = lakebase._connection_params(workspace)

        self.assertEqual(params["user"], "roberto.m0010@gmail.com")

    @patch("dashboard.weather_search.embed_query")


    @patch("dashboard.lakebase.run_query")
    def test_search_uses_parameterized_cosine_distance(self, run_query, embed_query):
        from dashboard import weather_search

        embed_query.return_value = [0.1] * 384
        run_query.return_value = [
            {
                "location": "Chicago, IL",
                "headline": "Flood warning",
                "chunk_text": "Move to higher ground.",
                "similarity": 0.92,
            }
        ]

        results = weather_search.search("flood", 5)

        self.assertEqual(results[0]["location"], "Chicago, IL")
        sql = run_query.call_args.args[0]
        self.assertIn("<=>", sql)
        self.assertNotIn("flood", sql)
        self.assertEqual(run_query.call_args.args[1][2], 5)


if __name__ == "__main__":
    unittest.main()
