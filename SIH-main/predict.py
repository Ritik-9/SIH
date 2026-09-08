import requests
import pandas as pd
import numpy as np
import joblib


# ============================================================
# 1. CONFIGURATION
# ============================================================

LATITUDE = 28.50
LONGITUDE = 77.25

FORECAST_DAYS = 7

WBGT_THRESHOLD = 30.0
REQUIRED_HOURS = 3

RAIN_THRESHOLD = 0.1


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
        "surface_pressure",
        "precipitation"
    ]),

    "forecast_days": FORECAST_DAYS,

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
# 4. CREATE HOURLY DATAFRAME
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
    "surface_pressure": "pressure",
    "precipitation": "rain"
})


# ============================================================
# 5. WBGT CALCULATION
# ============================================================

print("Calculating hourly WBGT...")


def calculate_wbgt(
    temperature,
    humidity,
    solar_radiation,
    wind_speed
):

    # Simplified outdoor WBGT approximation
    # using air temperature, humidity and solar radiation.

    # Natural wet-bulb approximation
    wet_bulb = (
        temperature * np.arctan(
            0.151977 * np.sqrt(humidity + 8.313659)
        )
        + np.arctan(temperature + humidity)
        - np.arctan(humidity - 1.676331)
        + 0.00391838 * humidity ** 1.5
        * np.arctan(0.023101 * humidity)
        - 4.686035
    )

    globe_temperature = (
        temperature
        + 0.025 * solar_radiation
        - 0.1 * wind_speed
    )

    wbgt = (
        0.7 * wet_bulb
        + 0.2 * globe_temperature
        + 0.1 * temperature
    )

    return wbgt


df["WBGT_C"] = calculate_wbgt(
    df["temperature"],
    df["humidity"],
    df["solar_radiation"],
    df["wind_speed"]
)


# ============================================================
# 6. DAILY FEATURES
# ============================================================

df["date"] = df["valid_time"].dt.date

df["high_WBGT"] = (
    df["WBGT_C"] >= WBGT_THRESHOLD
)


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
    ),

    max_WBGT=(
        "WBGT_C",
        "max"
    ),

    mean_WBGT=(
        "WBGT_C",
        "mean"
    ),

    high_WBGT_hours=(
        "high_WBGT",
        "sum"
    ),

    total_rain=(
        "rain",
        "sum"
    )

).reset_index()


# ============================================================
# 7. PHYSICAL WBGT HEATWAVE DECISION
# ============================================================

daily["heatwave_prediction"] = np.where(
    daily["high_WBGT_hours"] >= REQUIRED_HOURS,
    "Heatwave",
    "No Heatwave"
)


# ============================================================
# 8. RAIN STATUS
# ============================================================

daily["rain_status"] = np.where(
    daily["total_rain"] >= RAIN_THRESHOLD,
    "Rain",
    "No Rain"
)


# ============================================================
# 9. RISK LEVEL FROM MAXIMUM WBGT
# ============================================================

def classify_risk(wbgt):

    if wbgt < 23:
        return "Low"

    elif wbgt < 25:
        return "Elevated"

    elif wbgt < 28:
        return "Moderate"

    elif wbgt < 30:
        return "High"

    elif wbgt < 33:
        return "Very High"

    else:
        return "Extreme"


daily["risk_level"] = daily["max_WBGT"].apply(
    classify_risk
)


# ============================================================
# 10. ML MODEL PREDICTIONS
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


X = daily[features]


ml_heatwave_predictions = heatwave_model.predict(X)

ml_risk_predictions = risk_model.predict(X)


daily["ml_heatwave_prediction"] = np.where(
    ml_heatwave_predictions == 1,
    "Heatwave",
    "No Heatwave"
)

daily["ml_risk_level"] = ml_risk_predictions


# ============================================================
# 11. FINAL EXPLANATION / STATUS
# ============================================================

def create_status(row):

    if row["heatwave_prediction"] == "Heatwave":

        if row["rain_status"] == "Rain":

            return (
                "HEATWAVE CONDITIONS DETECTED "
                "(rain present)"
            )

        return "HEATWAVE CONDITIONS DETECTED"

    else:

        if row["max_WBGT"] >= WBGT_THRESHOLD:

            return (
                "HIGH HEAT STRESS, BUT "
                "DURATION THRESHOLD NOT MET"
            )

        return "HEATWAVE CONDITIONS NOT DETECTED"


daily["final_status"] = daily.apply(
    create_status,
    axis=1
)


# ============================================================
# 12. DISPLAY RESULTS
# ============================================================

print("\n")
print("=" * 78)
print("                 AUTOMATED HEATWAVE PREDICTION")
print("=" * 78)

print("\nLocation:")
print(f"Latitude : {LATITUDE}")
print(f"Longitude: {LONGITUDE}")

print("\nFORECAST PREDICTIONS:")
print("-" * 78)

display_columns = [
    "date",
    "max_temperature",
    "mean_temperature",
    "max_WBGT",
    "mean_WBGT",
    "high_WBGT_hours",
    "total_rain",
    "rain_status",
    "heatwave_prediction",
    "risk_level",
    "final_status"
]

print(
    daily[display_columns].to_string(
        index=False
    )
)


# ============================================================
# 13. ML COMPARISON
# ============================================================

print("\n")
print("=" * 78)
print("                       ML MODEL COMPARISON")
print("=" * 78)

ml_columns = [
    "date",
    "heatwave_prediction",
    "ml_heatwave_prediction",
    "risk_level",
    "ml_risk_level"
]

print(
    daily[ml_columns].to_string(
        index=False
    )
)


# ============================================================
# 14. WBGT VALIDATION
# ============================================================

print("\n")
print("=" * 78)
print("                         WBGT VALIDATION")
print("=" * 78)

print(
    f"\nHeatwave rule:"
    f" WBGT >= {WBGT_THRESHOLD}°C "
    f"for at least {REQUIRED_HOURS} hours"
)

print(
    "\nRain is treated as contextual information."
)

print(
    "A rainy day is NOT automatically classified "
    "as 'No Heatwave'."
)

print(
    "The final heatwave decision is based on "
    "WBGT duration."
)


# ============================================================
# 15. SAVE RESULTS
# ============================================================

output_file = "forecast_predictions.csv"

daily.to_csv(
    output_file,
    index=False
)

print("\n")
print("=" * 78)
print("Prediction completed successfully!")
print("=" * 78)

print(
    f"\nForecast predictions saved to: {output_file}"
)