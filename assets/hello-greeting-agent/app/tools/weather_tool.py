import logging
import os

import requests
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

OPENWEATHERMAP_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
DEFAULT_LOCATION_FALLBACK = "Berlin"


@tool
def get_weather(location: str = "") -> dict:
    """Fetch current weather conditions for a given location using OpenWeatherMap API.

    Args:
        location: City name or location string (e.g. 'Berlin', 'London,UK').
                  If empty or not provided, falls back to the DEFAULT_LOCATION
                  environment variable (or 'Berlin' if that is also unset).

    Returns a dict with:
      - location: the resolved location name
      - description: weather description (e.g. 'partly cloudy')
      - temperature: current temperature in Celsius (float)
      - humidity: relative humidity percentage (int)
      - feels_like: apparent temperature in Celsius (float)
    """
    resolved_location = (
        location.strip()
        if location and location.strip()
        else os.environ.get("DEFAULT_LOCATION", DEFAULT_LOCATION_FALLBACK)
    )

    api_key = os.environ.get("OPENWEATHERMAP_API_KEY", "")
    if not api_key:
        logger.error("[M1.missed]: weather data retrieval failed — OPENWEATHERMAP_API_KEY not set")
        raise ValueError("OPENWEATHERMAP_API_KEY environment variable is not set.")

    params = {
        "q": resolved_location,
        "appid": api_key,
        "units": "metric",
    }

    try:
        response = requests.get(OPENWEATHERMAP_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        weather_data = {
            "location": data.get("name", resolved_location),
            "description": data["weather"][0]["description"],
            "temperature": round(data["main"]["temp"], 1),
            "humidity": data["main"]["humidity"],
            "feels_like": round(data["main"]["feels_like"], 1),
        }

        logger.info(
            "[M1.achieved]: weather data retrieved successfully for location=%s temp=%.1f°C desc=%s",
            weather_data["location"],
            weather_data["temperature"],
            weather_data["description"],
        )
        return weather_data

    except requests.exceptions.HTTPError as exc:
        logger.error("[M1.missed]: weather data retrieval failed — HTTP error: %s", exc)
        raise RuntimeError(f"Weather API returned an error for location '{resolved_location}': {exc}") from exc
    except requests.exceptions.RequestException as exc:
        logger.error("[M1.missed]: weather data retrieval failed — network error: %s", exc)
        raise RuntimeError(f"Weather API network error for location '{resolved_location}': {exc}") from exc
    except (KeyError, IndexError) as exc:
        logger.error("[M1.missed]: weather data retrieval failed — unexpected response structure: %s", exc)
        raise RuntimeError(f"Unexpected weather API response structure: {exc}") from exc
