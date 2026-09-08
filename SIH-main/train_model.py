import pandas as pd
import joblib

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

df["date"] = pd.to_datetime(df["date"])


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
# 3. CHRONOLOGICAL TRAIN / TEST SPLIT
# ============================================================

train_df = df[df["date"].dt.year <= 2023].copy()
test_df = df[df["date"].dt.year == 2024].copy()


X_train = train_df[features]
y_train = train_df["heatwave_day"]

X_test = test_df[features]
y_test = test_df["heatwave_day"]


print("\n============================================================")
print("       CHRONOLOGICAL MODEL VALIDATION")
print("============================================================")

print("\nTRAINING PERIOD:")
print("2020 - 2023")

print("\nTESTING PERIOD:")
print("2024")

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

accuracy = accuracy_score(
    y_test,
    y_pred
)

print("\nMODEL ACCURACY:")
print("-----------------------------")
print(f"{accuracy:.4f}")


# ============================================================
# 7. CLASSIFICATION REPORT
# ============================================================

print("\nCLASSIFICATION REPORT:")
print("-----------------------------")

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
print("-----------------------------")

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
print("-----------------------------")

print(importance.to_string(index=False))


# ============================================================
# 10. SAVE VALIDATED MODEL
# ============================================================

joblib.dump(
    model,
    "models/heatwave_model.pkl"
)

print("\n============================================================")
print("Validated model saved successfully!")
print("Location: models/heatwave_model.pkl")
print("============================================================")