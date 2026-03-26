"""
Purpose:
    Train baseline logistic regression model for maintenance risk

Input:
    data/training/maintenance_training.csv
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, roc_auc_score

# ----------------------------
# Load training data
# ----------------------------
df = pd.read_csv("data/training/maintenance_training.csv")

FEATURES = [
    "battery_decline_7v14",
    "rides_avg_7d",
    "rides_avg_14d",
    "distance_avg_7d",
    "zone_pressure"
]

TARGET = "maintenance_risk"

X = df[FEATURES]
y = df["maintenance_risk"]

# ----------------------------
# Train / validation split
# ----------------------------
X_train, X_val, y_train, y_val = train_test_split(
    X,
    y,
    test_size=0.25,
    stratify=y,
    random_state=42
)

# ----------------------------
# Pipeline
# ----------------------------
model = Pipeline(
    steps=[
        ("scaler", StandardScaler()),
        ("logreg", LogisticRegression(
            class_weight="balanced",
            max_iter=1000,
            random_state=42
        )),
    ]
)

# ----------------------------
# ----------------------------
# Recreate test frame safely
# ----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.25,
    random_state=42,
    stratify=y
)

model.fit(X_train, y_train)

y_prob = model.predict_proba(X_test)[:, 1]
y_pred = (y_prob >= 0.5).astype(int)

# ----------------------------
# Save predictions
# ----------------------------
df_out = X_test.copy()
df_out["actual"] = y_test.values
df_out["predicted_prob"] = y_prob
df_out["predicted_label"] = y_pred

OUTPUT_PATH = "data/model_outputs/logistic_predictions.csv"
df_out.to_csv(OUTPUT_PATH, index=False)

print(f"✅ Logistic predictions saved → {OUTPUT_PATH}")
