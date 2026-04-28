"""
Arcy — Weather Connector
Fetches current weather using OpenWeatherMap's free API.
Sign up free at: https://openweathermap.org/api
"""

import requests
from arcy.core.config import WEATHER_API_KEY, WEATHER_CITY


def get_weather(city: str = None) -> str:
    """
    Fetch current weather for a city and return a natural language summary.

    Args:
        city: City name (defaults to config WEATHER_CITY)

    Returns:
        Human-readable weather string for Arcy to say
    """
    target_city = city or WEATHER_CITY

    if not WEATHER_API_KEY:
        return (
            f"I'd love to check the weather in {target_city}, "
            f"but I need an OpenWeatherMap API key. "
            f"It's completely free at openweathermap.org — just add it to your .env file as WEATHER_API_KEY."
        )

    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": target_city,
            "appid": WEATHER_API_KEY,
            "units": "metric",
        }
        resp = requests.get(url, params=params, timeout=6)
        resp.raise_for_status()
        data = resp.json()

        temp     = round(data["main"]["temp"])
        feels    = round(data["main"]["feels_like"])
        desc     = data["weather"][0]["description"].capitalize()
        humidity = data["main"]["humidity"]
        city_name = data["name"]

        return (
            f"In {city_name} right now: {desc}, {temp}°C, "
            f"feels like {feels}°C. Humidity is {humidity}%."
        )

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return f"I couldn't find weather data for '{target_city}'. Try a different city name."
        return f"Weather service returned an error: {e}"
    except Exception as e:
        return f"I couldn't reach the weather service right now: {e}"
