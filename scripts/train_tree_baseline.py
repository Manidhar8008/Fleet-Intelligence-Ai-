"""
Purpose:
    Train a baseline Decision Tree model for maintenance risk prediction
    to compare against Logistic Regression.

Input:
    data/training/training_dataset.csv

Output:
    Console metrics + feature importance

Why this exists:
    - Capture non-linear risk thresholds
    - Provide model comparison for decision-making
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report, roc_auc_score

# ----------------------------
# Load training data
# ----------------------------
INPUT_PATH = "data/training/maintenance_training.csv"
df = pd.read_csv(INPUT_PATH)

# ----------------------------
# Features and target
# ----------------------------
FEATURES = [
    "battery_decline_7v14",
    "rides_avg_7d",
    "rides_avg_14d",
    "distance_avg_7d",
    "zone_pressure"
]

TARGET = "maintenance_risk"

X = df[FEATURES]
y = df[TARGET]

# ----------------------------
# Train / test split
# ----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.25,
    random_state=42,
    stratify=y
)

# ----------------------------
# Decision Tree model
# ----------------------------
model = DecisionTreeClassifier(
    max_depth=4,          # keep it interpretable
    min_samples_leaf=10,  # avoid noise
    random_state=42
)

model.fit(X_train, y_train)

# ----------------------------
# Generate predictions
# ----------------------------
y_prob = model.predict_proba(X_test)[:, 1]
y_pred = (y_prob >= 0.5).astype(int)

# ----------------------------
# Save predictions
# ----------------------------
df_out = X_test.copy()
df_out["actual"] = y_test.values
df_out["predicted_prob"] = y_prob
df_out["predicted_label"] = y_pred

OUTPUT_PATH = "data/model_outputs/tree_predictions.csv"
df_out.to_csv(OUTPUT_PATH, index=False)

print(f"✅ Tree predictions saved → {OUTPUT_PATH}")
