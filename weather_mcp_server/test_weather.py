"""Contract tests for the weather MCP service."""

import unittest
from unittest.mock import Mock, patch


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


def mock_response(payload):
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = payload
    return response


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
