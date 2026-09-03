import requests
import pandas as pd
import numpy as np
import joblib


# ============================================================
# 1. CONFIGURATION
# ============================================================

LATITUDE = 28.50
LONGITUDE = 77.25


# ============================================================
# 2. LOAD TRAINED MODELS
# ============================================================

heatwave_model = joblib.load(
    "models/heatwave_model.pkl"
)

risk_model = joblib.load(
    "models/risk_model.pkl"
)


# ============================================================
# 3. WEATHER API
# ============================================================

url = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": LATITUDE,
    "longitude": LONGITUDE,

    "hourly": ",".join([
        "temperature_2m",
        "relative_humidity_2m",
        "dew_point_2m",
        "wind_speed_10m",
        "shortwave_radiation",
        "surface_pressure"
    ]),

    "forecast_days": 7,

    "temperature_unit": "celsius",
    "wind_speed_unit": "ms",

    "timezone": "Asia/Kolkata"
}


print("\nFetching weather data...")

response = requests.get(
    url,
    params=params,
    timeout=30
)

response.raise_for_status()

weather = response.json()

print("Weather data received successfully.")


# ============================================================
# 4. CREATE DATAFRAME
# ============================================================

hourly = weather["hourly"]

df = pd.DataFrame(hourly)

df["time"] = pd.to_datetime(df["time"])

df = df.rename(columns={
    "time": "valid_time",
    "temperature_2m": "temperature",
    "relative_humidity_2m": "humidity",
    "dew_point_2m": "dewpoint",
    "wind_speed_10m": "wind_speed",
    "shortwave_radiation": "solar_radiation",
    "surface_pressure": "pressure"
})


# ============================================================
# 5. DAILY FEATURES
# ============================================================

df["date"] = df["valid_time"].dt.date

daily = df.groupby("date").agg(

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


# ============================================================
# 6. FEATURES USED BY ML MODELS
# ============================================================

features = [
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
    "mean_pressure"
]


# ============================================================
# 7. PREDICT EACH DAY
# ============================================================

X = daily[features]

heatwave_predictions = heatwave_model.predict(X)

risk_predictions = risk_model.predict(X)


daily["heatwave_prediction"] = np.where(
    heatwave_predictions == 1,
    "Heatwave",
    "No Heatwave"
)

daily["risk_level"] = risk_predictions


# ============================================================
# 8. DISPLAY PREDICTIONS
# ============================================================

print("\n============================================================")
print("             AUTOMATED HEATWAVE PREDICTION")
print("============================================================")

print("\nLocation:")
print(f"Latitude : {LATITUDE}")
print(f"Longitude: {LONGITUDE}")

print("\nFORECAST PREDICTIONS:")
print("------------------------------------------------------------")

print(
    daily[
        [
            "date",
            "max_temperature",
            "mean_temperature",
            "max_humidity",
            "mean_humidity",
            "heatwave_prediction",
            "risk_level"
        ]
    ].to_string(index=False)
)

print("\n============================================================")
print("Prediction completed successfully!")
print("============================================================")