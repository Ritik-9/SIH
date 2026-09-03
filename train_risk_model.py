import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

import joblib


# ============================================================
# 1. LOAD DAILY DATA
# ============================================================

df = pd.read_csv("daily_heatwave_data.csv")


# ============================================================
# 2. FEATURES
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

# Target = daily risk level
y = df["daily_risk_level"]


# ============================================================
# 3. CHECK DATA
# ============================================================

print("\nFEATURES:")
print(X.head())

print("\nTARGET:")
print(y.head())

print("\nFEATURE SHAPE:")
print(X.shape)

print("\nRISK LEVEL DISTRIBUTION:")
print(y.value_counts())

print("\nMISSING VALUES:")
print(X.isnull().sum())

print("\nTARGET MISSING VALUES:")
print(y.isnull().sum())


# ============================================================
# 4. TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


print("\nDATA SPLIT:")
print("-----------------------------")
print(f"Training samples: {len(X_train)}")
print(f"Testing samples : {len(X_test)}")

print("\nTraining risk distribution:")
print(y_train.value_counts())

print("\nTesting risk distribution:")
print(y_test.value_counts())


# ============================================================
# 5. TRAIN RANDOM FOREST
# ============================================================

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced",
    n_jobs=-1
)

model.fit(X_train, y_train)


# ============================================================
# 6. PREDICTION
# ============================================================

y_pred = model.predict(X_test)


# ============================================================
# 7. MODEL ACCURACY
# ============================================================

accuracy = accuracy_score(y_test, y_pred)

print("\nMODEL ACCURACY:")
print(accuracy)


# ============================================================
# 8. CLASSIFICATION REPORT
# ============================================================

risk_labels = [
    "Low",
    "Elevated",
    "Moderate",
    "High",
    "Very High",
    "Extreme"
]

print("\nCLASSIFICATION REPORT:")

print(
    classification_report(
        y_test,
        y_pred,
        labels=risk_labels,
        target_names=risk_labels,
        zero_division=0
    )
)


# ============================================================
# 9. CONFUSION MATRIX
# ============================================================

print("\nCONFUSION MATRIX:")

cm = confusion_matrix(
    y_test,
    y_pred,
    labels=risk_labels
)

print(pd.DataFrame(
    cm,
    index=risk_labels,
    columns=risk_labels
))


# ============================================================
# 10. FEATURE IMPORTANCE
# ============================================================

importance = pd.DataFrame({
    "feature": features,
    "importance": model.feature_importances_
})

importance = importance.sort_values(
    by="importance",
    ascending=False
)

print("\nFEATURE IMPORTANCE:")
print(importance)


# ============================================================
# 11. SAVE MODEL
# ============================================================

joblib.dump(
    model,
    "models/risk_model.pkl"
)

print("\nRisk model saved successfully!")
print("Location: models/risk_model.pkl")