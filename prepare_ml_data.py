import pandas as pd


# ============================================================
# 1. LOAD DAILY DATA
# ============================================================

df = pd.read_csv("daily_heatwave_data.csv")


# ============================================================
# 2. SELECT FEATURES
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

X = df[features]

# Target
y = df["heatwave_day"].astype(int)


# ============================================================
# 3. DISPLAY FEATURES AND TARGET
# ============================================================

print("\nFEATURES:")
print(X.head())

print("\nTARGET:")
print(y.head())

print("\nFEATURE SHAPE:")
print(X.shape)

print("\nTARGET DISTRIBUTION:")
print(y.value_counts())


# ============================================================
# 4. CHECK MISSING VALUES
# ============================================================

print("\nMISSING VALUES:")
print(X.isnull().sum())

print("\nTARGET MISSING VALUES:")
print(y.isnull().sum())


# ============================================================
# 5. CREATE ML DATASET
# ============================================================

ml_data = X.copy()

ml_data["heatwave_day"] = y


# ============================================================
# 6. SAVE ML DATASET
# ============================================================

ml_data.to_csv(
    "ml_dataset.csv",
    index=False
)

print("\nML dataset saved successfully!")

print("\nML DATASET SHAPE:")
print(ml_data.shape)

print("\nML DATASET PREVIEW:")
print(ml_data.head())