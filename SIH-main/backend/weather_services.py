"""
weather_service.py

Responsible ONLY for talking to the weather provider (Open-Meteo).

Input:  latitude, longitude
Output: a clean hourly pandas DataFrame

This module knows nothing about WBGT, ML models, or heatwave logic.
"""

import requests
import pandas as pd


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

HOURLY_VARIABLES = [
    "temperature_2m",
    "relative_humidity_2m",
    "dew_point_2m",
    "wind_speed_10m",
    "shortwave_radiation",
    "surface_pressure",
    "precipitation",
]

# Rename Open-Meteo's field names to the internal names used
# throughout the rest of the pipeline (matches original predict.py).
COLUMN_RENAME_MAP = {
    "time": "valid_time",
    "temperature_2m": "temperature",
    "relative_humidity_2m": "humidity",
    "dew_point_2m": "dewpoint",
    "wind_speed_10m": "wind_speed",
    "shortwave_radiation": "solar_radiation",
    "surface_pressure": "pressure",
    "precipitation": "rain",
}


class WeatherServiceError(Exception):
    """Raised when the upstream weather API cannot be reached or returns bad data."""


def fetch_hourly_weather(
    latitude: float,
    longitude: float,
    forecast_days: int = 7,
) -> pd.DataFrame:
    """
    Fetch hourly forecast data from Open-Meteo for the given coordinates
    and return it as a DataFrame with standardized column names.
    """

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ",".join(HOURLY_VARIABLES),
        "forecast_days": forecast_days,
        "temperature_unit": "celsius",
        "wind_speed_unit": "ms",
        "timezone": "Asia/Kolkata",
    }

    try:
        response = requests.get(OPEN_METEO_URL, params=params, timeout=30)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise WeatherServiceError(f"Failed to fetch weather data: {exc}") from exc

    try:
        payload = response.json()
        hourly = payload["hourly"]
    except (ValueError, KeyError) as exc:
        raise WeatherServiceError(
            "Weather API returned an unexpected response format"
        ) from exc

    df = pd.DataFrame(hourly)

    if df.empty:
        raise WeatherServiceError("Weather API returned no hourly data")

    df["time"] = pd.to_datetime(df["time"])
    df = df.rename(columns=COLUMN_RENAME_MAP)

    return df