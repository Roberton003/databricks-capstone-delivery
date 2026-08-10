"""Weather service domain operations."""

try:
    from .weather_broker import WeatherBroker
except ImportError:
    from weather_broker import WeatherBroker


class WeatherService:
    def __init__(self, broker=None):
        self.broker = broker or WeatherBroker()

    @staticmethod
    def _validate_location(location):
        if not isinstance(location, str) or not location.strip():
            raise ValueError("Location must not be empty")
        return location.strip()

    @staticmethod
    def _validate_days(days):
        if not isinstance(days, int) or isinstance(days, bool) or not 1 <= days <= 16:
            raise ValueError("Days must be an integer between 1 and 16")
        return days

    def get_current_weather(self, location):
        location = self._validate_location(location)
        place = self.broker.geocode(location)
        return {
            "location": place["name"],
            "country": place.get("country"),
            "coordinates": {
                "latitude": place["latitude"],
                "longitude": place["longitude"],
            },
            "current": self.broker.get_current(place["latitude"], place["longitude"]),
        }

    def get_forecast(self, location, days=3):
        location = self._validate_location(location)
        days = self._validate_days(days)
        place = self.broker.geocode(location)
        forecast = self.broker.get_forecast(place["latitude"], place["longitude"], days)
        return [
            {
                "location": place["name"],
                "country": place.get("country"),
                **day,
            }
            for day in forecast[:days]
        ]

    @staticmethod
    def should_bring_umbrella(weather):
        return weather.get("precipitation", 0) > 0 or weather.get(
            "precipitation_probability", 0
        ) >= 50

    def predict_umbrella_needed(self, location, days=1):
        forecast = self.get_forecast(location, days)
        return {
            "location": forecast[0]["location"] if forecast else location,
            "days": forecast,
            "umbrella_needed": any(self.should_bring_umbrella(day) for day in forecast),
        }
