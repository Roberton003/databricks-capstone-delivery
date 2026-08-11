import hashlib
import os
import re
from datetime import datetime, timezone

import requests

NWS_BASE_URL = "https://api.weather.gov"
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
REQUEST_TIMEOUT = 10
_COORDINATES_RE = re.compile(r"^\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*$")


class WeatherClient:
    def __init__(self, session=None, user_agent=None):
        self.session = session or requests.Session()
        self.user_agent = user_agent or os.environ.get(
            "NWS_USER_AGENT", "databricks-capstone-weather/1.0"
        )

    def _request(self, url, **kwargs):
        headers = {"User-Agent": self.user_agent, "Accept": "application/geo+json"}
        headers.update(kwargs.pop("headers", {}))
        response = self.session.get(
            url, headers=headers, timeout=REQUEST_TIMEOUT, **kwargs
        )
        response.raise_for_status()
        return response.json()

    def resolve_location(self, location):
        if not isinstance(location, str) or not location.strip():
            raise ValueError("Location must not be empty")
        location = location.strip()
        match = _COORDINATES_RE.match(location)
        if match:
            latitude, longitude = map(float, match.groups())
            return {"name": location, "latitude": latitude, "longitude": longitude}

        response = self.session.get(
            GEOCODING_URL,
            params={"name": location, "count": 1, "language": "en", "format": "json"},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        results = response.json().get("results") or []
        if not results:
            raise ValueError(f"Location not found: {location}")
        result = results[0]
        return {
            "name": result.get("name", location),
            "latitude": result["latitude"],
            "longitude": result["longitude"],
        }

    def get_documents(self, location):
        resolved = self.resolve_location(location)
        point = self._request(
            f"{NWS_BASE_URL}/points/{resolved['latitude']},{resolved['longitude']}"
        )
        properties = point["properties"]
        forecast_url = properties["forecast"]
        office = properties.get("cwa")
        grid_x = properties.get("gridX")
        grid_y = properties.get("gridY")
        forecast = self._request(forecast_url)
        alerts = self._request(
            f"{NWS_BASE_URL}/alerts/active",
            params={"point": f"{resolved['latitude']},{resolved['longitude']}"},
        )

        documents = [
            self.normalize_forecast(period, location)
            for period in forecast.get("properties", {}).get("periods", [])
        ]
        documents.extend(
            self.normalize_alert(feature, location)
            for feature in alerts.get("features", [])
        )
        return documents

    @staticmethod
    def normalize_alert(feature, location):
        properties = feature.get("properties", {})
        headline = properties.get("headline") or properties.get("event") or "Weather alert"
        description = properties.get("description") or ""
        return {
            "id": feature.get("id") or WeatherClient._stable_id(location, headline, description),
            "location": location,
            "source_type": "alert",
            "headline": headline,
            "narrative_text": "\n\n".join(part for part in (headline, description) if part),
            "issued_at": properties.get("sent"),
            "effective_at": properties.get("effective"),
            "payload": feature,
        }

    @staticmethod
    def normalize_forecast(period, location):
        number = period.get("number")
        headline = period.get("name") or "Forecast"
        details = period.get("detailedForecast") or period.get("shortForecast") or ""
        return {
            "id": f"forecast:{location}:{number}",
            "location": location,
            "source_type": "forecast",
            "headline": headline,
            "narrative_text": details,
            "issued_at": None,
            "effective_at": period.get("startTime"),
            "payload": period,
        }

    @staticmethod
    def _stable_id(*parts):
        value = "|".join(str(part) for part in parts)
        return hashlib.sha256(value.encode("utf-8")).hexdigest()


def parse_timestamp(value):
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
