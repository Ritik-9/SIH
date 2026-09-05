"""
prediction_service.py

Responsible for combining:

hourly weather
    -> WBGT calculation
    -> daily WBGT indicators
    -> WBGT heatwave decision
    -> ML risk prediction
    -> clean API response

The WBGT-based rule is the authoritative heatwave decision.

The ML heatwave model is retained internally for validation,
but is NOT exposed to the frontend.
"""

import os
import pandas as pd
import joblib

from backend.wbgt_services import (
    calculate_hourly_wbgt,
    calculate_daily_wbgt_indicators,
    determine_heatwave,
)


# ============================================================
# CONFIGURATION
# ============================================================

MODELS_DIR = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    ),
    "models"
)

HEATWAVE_MODEL_PATH = os.path.join(
    MODELS_DIR,
    "heatwave_model.pkl"
)

RISK_MODEL_PATH = os.path.join(
    MODELS_DIR,
    "risk_model.pkl"
)


# ============================================================
# FEATURES USED BY THE ML MODELS
# ============================================================

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


# ============================================================
# MODEL LOADING
# ============================================================

class ModelLoadError(Exception):
    """
    Raised when trained ML models cannot be loaded.
    """
    pass


_heatwave_model = None
_risk_model = None


def load_models():
    """
    Load trained ML models into memory.

    Called once when the backend starts.
    """

    global _heatwave_model
    global _risk_model

    try:

        _heatwave_model = joblib.load(
            HEATWAVE_MODEL_PATH
        )

        _risk_model = joblib.load(
            RISK_MODEL_PATH
        )

    except FileNotFoundError as exc:

        raise ModelLoadError(
            f"Model file not found: {exc}"
        ) from exc

    except Exception as exc:

        raise ModelLoadError(
            f"Failed to load models: {exc}"
        ) from exc


def models_ready():
    """
    Check whether both ML models are loaded.
    """

    return (
        _heatwave_model is not None
        and _risk_model is not None
    )


# ============================================================
# ML PREDICTIONS
# ============================================================

def run_ml_predictions(
    daily: pd.DataFrame
) -> pd.DataFrame:
    """
    Run the trained ML models.

    These predictions are used internally for validation.

    They are NOT exposed directly to the frontend.
    """

    if not models_ready():

        raise ModelLoadError(
            "Prediction models are not loaded"
        )

    result = daily.copy()

    X = result[FEATURES]

    # ML heatwave prediction
    result["ml_heatwave"] = (
        _heatwave_model.predict(X) == 1
    )

    # ML risk prediction
    result["ml_risk_level"] = (
        _risk_model.predict(X)
    )

    return result


# ============================================================
# BUILD FINAL FORECAST
# ============================================================

def build_forecast(
    latitude: float,
    longitude: float,
    hourly_df: pd.DataFrame
) -> dict:
    """
    Complete prediction pipeline.

    Pipeline:

        hourly weather
            ↓
        WBGT calculation
            ↓
        daily indicators
            ↓
        WBGT heatwave rule
            ↓
        ML risk prediction
            ↓
        API response
    """

    # --------------------------------------------------------
    # 1. Calculate hourly WBGT
    # --------------------------------------------------------

    hourly_wbgt = calculate_hourly_wbgt(
        hourly_df,
        latitude,
        longitude
    )


    # --------------------------------------------------------
    # 2. Convert hourly WBGT into daily indicators
    # --------------------------------------------------------

    daily = calculate_daily_wbgt_indicators(
        hourly_wbgt
    )


    # --------------------------------------------------------
    # 3. Determine heatwave using WBGT rule
    # --------------------------------------------------------

    daily = determine_heatwave(
        daily,
        wbgt_threshold=30.0,
        minimum_high_hours=3
    )


    # --------------------------------------------------------
    # 4. Run ML models
    #
    # These are internal validation signals.
    # They are NOT returned directly to frontend.
    # --------------------------------------------------------

    daily = run_ml_predictions(
        daily
    )


    # --------------------------------------------------------
    # 5. Build clean API response
    # --------------------------------------------------------

    forecast = []

    for _, row in daily.iterrows():

        forecast.append({

            # Date
            "date": str(
                row["date"]
            ),

            # FINAL HEATWAVE DECISION
            "heatwave": (
                row["heatwave_prediction"]
                == "Heatwave"
            ),

            # FINAL RISK
            "risk": str(
                row["ml_risk_level"]
            ),

            # Temperature
            "temperature": {

                "max": round(
                    float(
                        row["max_temperature"]
                    ),
                    2
                ),

                "mean": round(
                    float(
                        row["mean_temperature"]
                    ),
                    2
                ),
            },

            # WBGT information
            "wbgt": {

                "max": round(
                    float(
                        row["max_WBGT"]
                    ),
                    2
                ),

                "mean": round(
                    float(
                        row["mean_WBGT"]
                    ),
                    2
                ),
            },

            # Rain information
            "rain": {

                "total": round(
                    float(
                        row["total_rain"]
                    ),
                    2
                ),

                "status": str(
                    row["rain_status"]
                ),
            },
        })


    # --------------------------------------------------------
    # 6. Final response
    # --------------------------------------------------------

    return {

        "location": {

            "latitude": latitude,

            "longitude": longitude,
        },

        "forecast": forecast,
    }