"""Contract tests for the weather MCP service."""

import os
import types
import unittest
from unittest.mock import Mock, patch


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


def mock_response(payload):
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = payload
    return response


class WeatherNotesConnectionTests(unittest.TestCase):
    @patch.dict(os.environ, {
        "PGHOST": "db.example",
        "PGPORT": "5432",
        "PGDATABASE": "weather",
        "PGUSER": "e275f7b1-7bae-4b0e-a183-3b71b91229f3",
        "PGSSLMODE": "require",
    }, clear=False)
    @patch("weather_mcp_server.weather_notes._generate_token", return_value="oauth-token")
    def test_app_connection_uses_injected_lakebase_identity(self, generate_token):
        from weather_mcp_server import weather_notes

        weather_notes._w = types.SimpleNamespace()
        params = weather_notes._connection_params(weather_notes._w)

        self.assertEqual(params["user"], "e275f7b1-7bae-4b0e-a183-3b71b91229f3")
        self.assertEqual(params["password"], "oauth-token")
        self.assertEqual(params["dbname"], "weather")

    @patch.dict(os.environ, {
        "DATABRICKS_CLIENT_ID": "e275f7b1-7bae-4b0e-a183-3b71b91229f3",
    }, clear=True)
    @patch("weather_mcp_server.weather_notes._generate_token", return_value="oauth-token")
    @patch("weather_mcp_server.weather_notes._lakebase_url", return_value="postgresql://roberto.m0010%40gmail.com:stale@db.example:5432/weather?sslmode=require")
    def test_legacy_url_uses_app_identity_and_oauth_token(self, lakebase_url, generate_token):
        from weather_mcp_server import weather_notes

        weather_notes._w = types.SimpleNamespace(
            config=types.SimpleNamespace(
                client_id="e275f7b1-7bae-4b0e-a183-3b71b91229f3"
            ),
            current_user=types.SimpleNamespace(
                me=lambda: types.SimpleNamespace(
                    user_name="roberto.m0010@gmail.com"
                )
            )
        )
        params = weather_notes._connection_params(weather_notes._w)

        self.assertEqual(params["user"], "e275f7b1-7bae-4b0e-a183-3b71b91229f3")
        self.assertEqual(params["password"], "oauth-token")
        self.assertEqual(params["sslmode"], "require")
        self.assertNotEqual(params["password"], "stale")
        lakebase_url.assert_called_once_with(weather_notes._w)
        generate_token.assert_called_once_with(weather_notes._w)


class WeatherServiceTests(unittest.TestCase):
    def load_service(self):
        from weather_mcp_server.weather_service import WeatherService

        return WeatherService()

    @patch("requests.get")
    def test_current_weather_geocodes_city_before_fetching_weather(self, get):
        service = self.load_service()
        get.side_effect = [
            mock_response({"results": [{"name": "Lisbon", "latitude": 38.7223, "longitude": -9.1393}]}),
            mock_response({"current": {"temperature_2m": 22.4, "precipitation": 0.0, "rain": 0.0}}),
        ]

        result = service.get_current_weather("Lisbon")

        self.assertEqual(result["location"], "Lisbon")
        self.assertEqual(result["current"]["temperature_2m"], 22.4)
        self.assertEqual(get.call_count, 2)
        self.assertEqual(get.call_args_list[0].args, (GEOCODING_URL,))
        self.assertEqual(get.call_args_list[0].kwargs["params"]["name"], "Lisbon")
        self.assertEqual(get.call_args_list[1].args, (WEATHER_URL,))
        self.assertEqual(get.call_args_list[1].kwargs["params"]["latitude"], 38.7223)
        self.assertEqual(get.call_args_list[1].kwargs["params"]["longitude"], -9.1393)

    @patch("requests.get")
    def test_forecast_is_limited_to_requested_number_of_days(self, get):
        service = self.load_service()
        get.side_effect = [
            mock_response({"results": [{"name": "Porto", "latitude": 41.1579, "longitude": -8.6291}]}),
            mock_response({
                "daily": {
                    "time": ["2026-08-10", "2026-08-11", "2026-08-12", "2026-08-13"],
                    "precipitation_sum": [0.0, 4.2, 1.1, 0.0],
                    "precipitation_probability_max": [10, 80, 45, 5],
                }
            }),
        ]

        result = service.get_forecast("Porto", days=2)

        self.assertEqual(len(result), 2)
        self.assertEqual([day["date"] for day in result], ["2026-08-10", "2026-08-11"])
        self.assertEqual(get.call_args_list[1].kwargs["params"]["forecast_days"], 2)

    def test_umbrella_is_recommended_for_nonzero_precipitation(self):
        service = self.load_service()
        self.assertTrue(service.should_bring_umbrella({"precipitation": 0.1, "precipitation_probability": 10}))

    def test_umbrella_is_recommended_for_high_precipitation_probability(self):
        service = self.load_service()
        self.assertTrue(service.should_bring_umbrella({"precipitation": 0.0, "precipitation_probability": 60}))
        self.assertFalse(service.should_bring_umbrella({"precipitation": 0.0, "precipitation_probability": 40}))


if __name__ == "__main__":
    unittest.main()
