"""Open-Meteo adapter for weather data."""

import requests


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
REQUEST_TIMEOUT = 10


class WeatherBroker:
    def geocode(self, location):
        response = requests.get(
            GEOCODING_URL,
            params={"name": location, "count": 1, "language": "en", "format": "json"},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        results = response.json().get("results", [])
        if not results:
            raise ValueError(f"Location not found: {location}")
        place = results[0]
        return {
            "name": place["name"],
            "latitude": place["latitude"],
            "longitude": place["longitude"],
            "country": place.get("country"),
        }

    def get_current(self, latitude, longitude):
        response = requests.get(
            WEATHER_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,precipitation,rain",
                "timezone": "auto",
            },
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        return response.json().get("current", {})

    def get_forecast(self, latitude, longitude, days):
        response = requests.get(
            WEATHER_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "daily": "precipitation_sum,precipitation_probability_max",
                "forecast_days": days,
                "timezone": "auto",
            },
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        daily = response.json().get("daily", {})
        dates = daily.get("time", [])
        precipitation = daily.get("precipitation_sum", [])
        probability = daily.get("precipitation_probability_max", [])
        return [
            {
                "date": date,
                "precipitation": precipitation[index] if index < len(precipitation) else 0,
                "precipitation_probability": probability[index] if index < len(probability) else 0,
            }
            for index, date in enumerate(dates[:days])
        ]
