"""Weather service integration."""
import requests
from typing import Optional
from datetime import datetime

from src.core import Config, get_logger, GoogleServicesError
from src.models import Weather


logger = get_logger(__name__)


class WeatherService:
    """Handles weather data retrieval and processing."""

    def __init__(self, config: Config):
        """Initialize weather service.

        Args:
            config: Application configuration
        """
        self.config = config
        self.base_url = "https://wttr.in"

    def get_weather(self, city: str) -> Optional[Weather]:
        """Get current weather for a city.

        Args:
            city: City name

        Returns:
            Weather object or None if service disabled

        Raises:
            GoogleServicesError: If weather retrieval fails
        """
        if not self.config.ENABLE_WEATHER:
            logger.debug("Weather service disabled")
            return None

        try:
            response = requests.get(
                f"{self.base_url}/{city}?format=j1",
                timeout=10,
                headers={"User-Agent": "TravelPlanningApp/1.0"},
            )
            response.raise_for_status()

            data = response.json()
            current = data["current_condition"][0]

            weather = Weather(
                temperature=float(current["temp_C"]),
                condition=current["weatherDesc"][0]["value"],
                humidity=float(current["humidity"]),
                wind_speed=float(current["windspeedKmph"]),
                precipitation=float(current.get("precipMM", 0)),
                uv_index=int(current.get("uvIndex", 0)),
                feels_like=float(current.get("FeelsLikeC", current["temp_C"])),
            )

            logger.info(f"Retrieved weather for {city}: {weather.condition}")
            return weather

        except requests.exceptions.Timeout:
            logger.warning(f"Weather request timeout for {city}")
            raise GoogleServicesError(
                f"Weather service timeout for {city}", service="Weather"
            )
        except requests.exceptions.RequestException as e:
            logger.warning(f"Weather service error: {str(e)}")
            # Return default weather on error instead of raising
            return Weather(
                temperature=20.0,
                condition="Unknown",
                humidity=50.0,
                wind_speed=0.0,
            )
        except Exception as e:
            logger.error(f"Unexpected error fetching weather: {str(e)}")
            raise GoogleServicesError(
                f"Failed to fetch weather: {str(e)}", service="Weather"
            )

    def get_weather_forecast(self, city: str, days: int = 7) -> Optional[list]:
        """Get weather forecast for upcoming days.

        Args:
            city: City name
            days: Number of days to forecast (1-10)

        Returns:
            List of weather forecasts or None

        Raises:
            GoogleServicesError: If forecast retrieval fails
        """
        if not self.config.ENABLE_WEATHER:
            return None

        if days < 1 or days > 10:
            raise ValueError("Forecast days must be between 1 and 10")

        try:
            response = requests.get(
                f"{self.base_url}/{city}?format=j1",
                timeout=10,
                headers={"User-Agent": "TravelPlanningApp/1.0"},
            )
            response.raise_for_status()

            data = response.json()
            forecasts = []

            for day_data in data["weather"][:days]:
                day_forecast = {
                    "date": day_data["date"],
                    "max_temp": float(day_data["maxtempC"]),
                    "min_temp": float(day_data["mintempC"]),
                    "condition": day_data["weatherDesc"][0]["value"],
                    "avg_humidity": float(day_data["avghumidity"]),
                    "total_snow": float(day_data.get("totalSnow_cm", 0)),
                    "uv_index": int(day_data.get("uvIndex", 0)),
                }
                forecasts.append(day_forecast)

            logger.info(f"Retrieved {len(forecasts)}-day forecast for {city}")
            return forecasts

        except Exception as e:
            logger.error(f"Forecast retrieval failed: {str(e)}")
            raise GoogleServicesError(
                f"Failed to fetch forecast: {str(e)}", service="Weather"
            )
