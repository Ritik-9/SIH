import pandas as pd
import joblib


# ============================================================
# 1. LOAD MODELS
# ============================================================

heatwave_model = joblib.load(
    "models/heatwave_model.pkl"
)

risk_model = joblib.load(
    "models/risk_model.pkl"
)


# ============================================================
# 2. LOAD DATA
# ============================================================

df = pd.read_csv("ml_dataset.csv")


# ============================================================
# 3. FEATURES
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
# 4. SELECT A DAY AUTOMATICALLY
# ============================================================

# For testing, select one row automatically.
# Later this will come from the weather API.

sample = df.iloc[[0]]

X = sample[features]


# ============================================================
# 5. HEATWAVE PREDICTION
# ============================================================

heatwave_prediction = heatwave_model.predict(X)[0]


if heatwave_prediction == 1:
    heatwave_result = "Heatwave"
else:
    heatwave_result = "No Heatwave"


# ============================================================
# 6. RISK LEVEL PREDICTION
# ============================================================

risk_prediction = risk_model.predict(X)[0]


# ============================================================
# 7. DISPLAY RESULT
# ============================================================

print("\n============================================================")
print("                 HEATWAVE PREDICTION")
print("============================================================")

print("\nINPUT WEATHER FEATURES:")
print(X.to_string(index=False))

print("\n------------------------------------------------------------")

print(f"Heatwave Prediction : {heatwave_result}")
print(f"Risk Level          : {risk_prediction}")

print("============================================================")