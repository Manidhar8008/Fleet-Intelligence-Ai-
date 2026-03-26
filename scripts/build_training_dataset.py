"""
Purpose:
    Build training dataset for maintenance risk prediction

Input:
    data/processed/telemetry.csv

Output:
    data/training/maintenance_training.csv

Target:
    maintenance_risk (binary)
"""

import pandas as pd
import numpy as np
from pathlib import Path

INPUT_PATH = "data/processed/telemetry.csv"
OUTPUT_PATH = "data/training/maintenance_training.csv"

# ----------------------------
# Load telemetry
# ----------------------------
df = pd.read_csv(INPUT_PATH, parse_dates=["date"])
df = df.sort_values(["vehicle_id", "date"])

# ----------------------------
# Rolling feature engineering
# ----------------------------
group = df.groupby("vehicle_id")

df["battery_avg_7d"] = group["battery_level"].rolling(7, min_periods=3).mean().reset_index(level=0, drop=True)
df["battery_avg_14d"] = group["battery_level"].rolling(14, min_periods=5).mean().reset_index(level=0, drop=True)

df["battery_decline_7v14"] = df["battery_avg_7d"] - df["battery_avg_14d"]

df["rides_avg_7d"] = group["rides_today"].rolling(7, min_periods=3).mean().reset_index(level=0, drop=True)
df["rides_avg_14d"] = group["rides_today"].rolling(14, min_periods=5).mean().reset_index(level=0, drop=True)

df["distance_avg_7d"] = group["distance_km"].rolling(7, min_periods=3).mean().reset_index(level=0, drop=True)

# ----------------------------
# Zone pressure (cross-asset signal)
# ----------------------------
zone_pressure = (
    df.groupby("zone_id")["rides_today"]
    .mean()
    .rename("zone_pressure")
)

df = df.merge(zone_pressure, on="zone_id", how="left")

# ----------------------------
# Calibrated maintenance risk label (quantile-based)
# ----------------------------

battery_decline_threshold = df["battery_decline_7v14"].quantile(0.20)
usage_threshold = df["rides_avg_7d"].quantile(0.60)

df["maintenance_risk"] = (
    (df["battery_decline_7v14"] <= battery_decline_threshold) &
    (df["rides_avg_7d"] >= usage_threshold)
).astype(int)

# ----------------------------
# Final training table
# ----------------------------
final_cols = [
    "vehicle_id",
    "date",
    "battery_avg_7d",
    "battery_avg_14d",
    "battery_decline_7v14",
    "rides_avg_7d",
    "rides_avg_14d",
    "distance_avg_7d",
    "zone_pressure",
    "maintenance_risk",
]

train_df = df[final_cols].dropna()

# ----------------------------
# Save
# ----------------------------
Path("data/training").mkdir(parents=True, exist_ok=True)
train_df.to_csv(OUTPUT_PATH, index=False)

# ----------------------------
# Logging
# ----------------------------
print("✅ Training dataset generated")
print(f"Rows: {len(train_df)}")
print("Class distribution:")
print(train_df['maintenance_risk'].value_counts())
print(f"Date range: {train_df['date'].min()} → {train_df['date'].max()}")
