"""
wbgt_service.py

Responsible ONLY for calculating WBGT and
WBGT-based heatwave indicators.

Input:
    Hourly weather DataFrame

Output:
    Hourly DataFrame containing WBGT values
"""


import numpy as np
import pandas as pd

from pywbgt import wbgt
from metpy.units import units


# ============================================================
# WBGT CALCULATION
# ============================================================

def calculate_hourly_wbgt(
    df: pd.DataFrame,
    latitude: float,
    longitude: float
) -> pd.DataFrame:
    """
    Calculate hourly WBGT from weather data.

    Expected columns:

        valid_time
        temperature
        humidity
        dewpoint
        wind_speed
        solar_radiation
        pressure
    """

    required_columns = [
        "valid_time",
        "temperature",
        "dewpoint",
        "wind_speed",
        "solar_radiation",
        "pressure",
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required weather columns: {missing}"
        )

    result_df = df.copy()

    # --------------------------------------------------------
    # Temperature
    # Open-Meteo gives Celsius.
    # pywbgt requires Kelvin.
    # --------------------------------------------------------

    temp_air = (
        result_df["temperature"].values + 273.15
    ) * units.kelvin

    temp_dew = (
        result_df["dewpoint"].values + 273.15
    ) * units.kelvin

    # --------------------------------------------------------
    # Wind speed
    # Open-Meteo configured to return m/s.
    # --------------------------------------------------------

    wind = (
        result_df["wind_speed"].values
        * units.meter
        / units.second
    )

    # --------------------------------------------------------
    # Solar radiation
    # Open-Meteo gives W/m².
    # --------------------------------------------------------

    solar = (
        result_df["solar_radiation"].values
        * units.watt
        / units.meter**2
    )

    # --------------------------------------------------------
    # Pressure
    # Open-Meteo gives pressure in hPa.
    #
    # Convert to Pa for pywbgt.
    # --------------------------------------------------------

    pressure = (
        result_df["pressure"].values * 100
    ) * units.pascal

    # --------------------------------------------------------
    # Datetime
    # --------------------------------------------------------

    datetime = pd.DatetimeIndex(
        result_df["valid_time"]
    )

    # --------------------------------------------------------
    # Latitude / Longitude arrays
    # --------------------------------------------------------

    lat_array = np.full(
        len(result_df),
        latitude
    )

    lon_array = np.full(
        len(result_df),
        longitude
    )

    # --------------------------------------------------------
    # Calculate WBGT
    # --------------------------------------------------------

    wbgt_result = wbgt(
        datetime=datetime,
        lat=lat_array,
        lon=lon_array,
        solar=solar,
        pres=pressure,
        temp_air=temp_air,
        temp_dew=temp_dew,
        speed=wind,
        method="liljegren"
    )

    wbgt_values = wbgt_result[3]

    result_df["WBGT_C"] = (
        wbgt_values.magnitude
    )

    return result_df


# ============================================================
# DAILY WBGT INDICATORS
# ============================================================

def calculate_daily_wbgt_indicators(
    hourly_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Convert hourly WBGT data into daily WBGT indicators.
    """

    df = hourly_df.copy()

    # --------------------------------------------------------
    # Create date
    # --------------------------------------------------------

    df["date"] = pd.to_datetime(
        df["valid_time"]
    ).dt.date

    # --------------------------------------------------------
    # Daily statistics
    # --------------------------------------------------------

    daily = df.groupby("date").agg(

        max_WBGT=(
            "WBGT_C",
            "max"
        ),

        mean_WBGT=(
            "WBGT_C",
            "mean"
        ),

        max_temperature=(
            "temperature",
            "max"
        ),

        mean_temperature=(
            "temperature",
            "mean"
        ),

        max_humidity=(
            "humidity",
            "max"
        ),

        mean_humidity=(
            "humidity",
            "mean"
        ),

        max_dewpoint=(
            "dewpoint",
            "max"
        ),

        mean_dewpoint=(
            "dewpoint",
            "mean"
        ),

        max_wind_speed=(
            "wind_speed",
            "max"
        ),

        mean_wind_speed=(
            "wind_speed",
            "mean"
        ),

        max_solar_radiation=(
            "solar_radiation",
            "max"
        ),

        mean_solar_radiation=(
            "solar_radiation",
            "mean"
        ),

        mean_pressure=(
            "pressure",
            "mean"
        )

    ).reset_index()

    # --------------------------------------------------------
    # Number of hours with WBGT >= 30°C
    # --------------------------------------------------------

    high_hours = (
        df[df["WBGT_C"] >= 30]
        .groupby("date")
        .size()
        .rename("high_WBGT_hours")
    )

    daily = daily.merge(
        high_hours,
        on="date",
        how="left"
    )

    daily["high_WBGT_hours"] = (
        daily["high_WBGT_hours"]
        .fillna(0)
    )

    # --------------------------------------------------------
    # Rain
    # --------------------------------------------------------

    if "rain" in df.columns:

        rain_daily = (
            df.groupby("date")["rain"]
            .sum()
            .rename("total_rain")
        )

        daily = daily.merge(
            rain_daily,
            on="date",
            how="left"
        )

        daily["total_rain"] = (
            daily["total_rain"]
            .fillna(0)
        )

        daily["rain_status"] = np.where(
            daily["total_rain"] > 0,
            "Rain",
            "No Rain"
        )

    else:

        daily["total_rain"] = 0.0

        daily["rain_status"] = "Unknown"

    return daily


# ============================================================
# HEATWAVE DECISION
# ============================================================

def determine_heatwave(
    daily_df: pd.DataFrame,
    wbgt_threshold: float = 30.0,
    minimum_high_hours: int = 3
) -> pd.DataFrame:
    """
    Determine heatwave conditions using the WBGT rule.

    Heatwave condition:

        WBGT >= 30°C
        for at least 3 hours
    """

    result = daily_df.copy()

    result["heatwave_prediction"] = np.where(
        result["high_WBGT_hours"] >= minimum_high_hours,
        "Heatwave",
        "No Heatwave"
    )

    return result