"""
prediction_service.py

Responsible for turning hourly weather into a final structured forecast:

hourly weather -> daily aggregation -> WBGT -> heatwave rule -> ML risk -> results

The WBGT-based rule is treated as the authoritative heatwave decision
(see project roadmap section 6). The ML heatwave model is kept as an
internal, additional validation signal and is NOT currently exposed
through the API response.
"""

import os
import numpy as np
import pandas as pd
import joblib


# ============================================================
# CONFIGURATION (matches original predict.py)
# ============================================================

WBGT_THRESHOLD = 30.0
REQUIRED_HOURS = 3
RAIN_THRESHOLD = 0.1

MODELS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models"
)
HEATWAVE_MODEL_PATH = os.path.join(MODELS_DIR, "heatwave_model.pkl")
RISK_MODEL_PATH = os.path.join(MODELS_DIR, "risk_model.pkl")

FEATURES = [
    "max_temperature",
    "mean_temperature",
    "max_humidity",
    "mean_humidity",
    "max_dewpoint",
    "mean_dewpoint",
    "max_wind_speed",
    "mean_wind_speed",
    "max_solar_radiation",
    "mean_solar_radiation",
    "mean_pressure",
]


class ModelLoadError(Exception):
    """Raised when the trained models cannot be loaded or used."""


_heatwave_model = None
_risk_model = None


def load_models() -> None:
    """Load both trained models into memory. Call once at API startup."""
    global _heatwave_model, _risk_model

    try:
        _heatwave_model = joblib.load(HEATWAVE_MODEL_PATH)
        _risk_model = joblib.load(RISK_MODEL_PATH)
    except FileNotFoundError as exc:
        raise ModelLoadError(f"Model file not found: {exc}") from exc
    except Exception as exc:  # corrupted file, version mismatch, etc.
        raise ModelLoadError(f"Failed to load models: {exc}") from exc


def models_ready() -> bool:
    return _heatwave_model is not None and _risk_model is not None


# ============================================================
# WBGT CALCULATION (simplified outdoor approximation)
# ============================================================

def calculate_wbgt(temperature, humidity, solar_radiation, wind_speed):
    wet_bulb = (
        temperature * np.arctan(0.151977 * np.sqrt(humidity + 8.313659))
        + np.arctan(temperature + humidity)
        - np.arctan(humidity - 1.676331)
        + 0.00391838 * humidity ** 1.5 * np.arctan(0.023101 * humidity)
        - 4.686035
    )

    globe_temperature = (
        temperature + 0.025 * solar_radiation - 0.1 * wind_speed
    )

    wbgt = 0.7 * wet_bulb + 0.2 * globe_temperature + 0.1 * temperature

    return wbgt


def classify_risk(wbgt_value: float) -> str:
    if wbgt_value < 23:
        return "Low"
    elif wbgt_value < 25:
        return "Elevated"
    elif wbgt_value < 28:
        return "Moderate"
    elif wbgt_value < 30:
        return "High"
    elif wbgt_value < 33:
        return "Very High"
    else:
        return "Extreme"


# ============================================================
# DAILY FEATURE ENGINEERING
# ============================================================

def build_daily_features(hourly_df: pd.DataFrame) -> pd.DataFrame:
    """
    Hourly weather -> daily aggregated features + WBGT-based heatwave decision.
    """
    df = hourly_df.copy()

    df["WBGT_C"] = calculate_wbgt(
        df["temperature"], df["humidity"], df["solar_radiation"], df["wind_speed"]
    )

    df["date"] = df["valid_time"].dt.date
    df["high_WBGT"] = df["WBGT_C"] >= WBGT_THRESHOLD

    daily = df.groupby("date").agg(
        max_temperature=("temperature", "max"),
        mean_temperature=("temperature", "mean"),
        max_humidity=("humidity", "max"),
        mean_humidity=("humidity", "mean"),
        max_dewpoint=("dewpoint", "max"),
        mean_dewpoint=("dewpoint", "mean"),
        max_wind_speed=("wind_speed", "max"),
        mean_wind_speed=("wind_speed", "mean"),
        max_solar_radiation=("solar_radiation", "max"),
        mean_solar_radiation=("solar_radiation", "mean"),
        mean_pressure=("pressure", "mean"),
        max_WBGT=("WBGT_C", "max"),
        mean_WBGT=("WBGT_C", "mean"),
        high_WBGT_hours=("high_WBGT", "sum"),
        total_rain=("rain", "sum"),
    ).reset_index()

    # Rain is contextual only - it must NOT cancel a heatwave decision.
    daily["wbgt_heatwave"] = daily["high_WBGT_hours"] >= REQUIRED_HOURS
    daily["rain_status"] = np.where(
        daily["total_rain"] >= RAIN_THRESHOLD, "Rain", "No Rain"
    )
    daily["risk_level"] = daily["max_WBGT"].apply(classify_risk)

    return daily


def run_ml_predictions(daily: pd.DataFrame) -> pd.DataFrame:
    """
    Attach ML heatwave/risk predictions as internal validation columns.
    These are NOT returned to the frontend (see roadmap section 17).
    """
    if not models_ready():
        raise ModelLoadError("Prediction models are not loaded")

    daily = daily.copy()
    X = daily[FEATURES]

    daily["ml_heatwave"] = _heatwave_model.predict(X) == 1
    daily["ml_risk_level"] = _risk_model.predict(X)

    return daily


# ============================================================
# PUBLIC ENTRY POINT
# ============================================================

def build_forecast(latitude: float, longitude: float, hourly_df: pd.DataFrame) -> dict:
    """
    Full pipeline: hourly weather -> daily features -> WBGT decision
    -> ML validation (internal) -> clean JSON-ready dict.
    """
    daily = build_daily_features(hourly_df)
    daily = run_ml_predictions(daily)  # internal only, not exposed below

    forecast = []
    for _, row in daily.iterrows():
        forecast.append(
            {
                "date": str(row["date"]),
                "heatwave": bool(row["wbgt_heatwave"]),
                "risk": row["risk_level"],
                "temperature": {
                    "max": round(float(row["max_temperature"]), 2),
                    "mean": round(float(row["mean_temperature"]), 2),
                },
                "wbgt": {
                    "max": round(float(row["max_WBGT"]), 2),
                    "mean": round(float(row["mean_WBGT"]), 2),
                },
                "rain": {
                    "total": round(float(row["total_rain"]), 2),
                    "status": row["rain_status"],
                },
            }
        )

    return {
        "location": {"latitude": latitude, "longitude": longitude},
        "forecast": forecast,
    }
