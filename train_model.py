import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)


# ============================================================
# 1. LOAD ML DATASET
# ============================================================

df = pd.read_csv("ml_dataset.csv")


# ============================================================
# 2. FEATURES AND TARGET
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
y = df["heatwave_day"]


# ============================================================
# 3. TRAIN / TEST SPLIT
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

print("\nTraining target distribution:")
print(y_train.value_counts())

print("\nTesting target distribution:")
print(y_test.value_counts())


# ============================================================
# 4. TRAIN RANDOM FOREST
# ============================================================

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced",
    n_jobs=-1
)

model.fit(X_train, y_train)


# ============================================================
# 5. PREDICTIONS
# ============================================================

y_pred = model.predict(X_test)


# ============================================================
# 6. MODEL ACCURACY
# ============================================================

accuracy = accuracy_score(y_test, y_pred)

print("\nMODEL ACCURACY:")
print(accuracy)


# ============================================================
# 7. CLASSIFICATION REPORT
# ============================================================

print("\nCLASSIFICATION REPORT:")

print(
    classification_report(
        y_test,
        y_pred,
        labels=[0, 1],
        target_names=[
            "No Heatwave",
            "Heatwave"
        ],
        zero_division=0
    )
)


# ============================================================
# 8. CONFUSION MATRIX
# ============================================================

print("\nCONFUSION MATRIX:")

cm = confusion_matrix(
    y_test,
    y_pred,
    labels=[0, 1]
)

print(cm)


# ============================================================
# 9. FEATURE IMPORTANCE
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
# 10. SAVE MODEL
# ============================================================

import joblib

joblib.dump(
    model,
    "heatwave_model.pkl"
)

print("\nModel saved successfully!")