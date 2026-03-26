"""
Purpose:
    Generate vehicle-day telemetry dataset for ML training

Input:
    data/raw/lime_vehicles_sample.csv

Output:
    data/processed/telemetry.csv

Grain:
    One row per vehicle per day
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ----------------------------
# Paths
# ----------------------------
INPUT_PATH = "data/raw/lime_vehicles_sample.csv"
OUTPUT_PATH = "data/processed/telemetry.csv"

Path("data/processed").mkdir(parents=True, exist_ok=True)

# ----------------------------
# Load base vehicle data
# ----------------------------
df_base = pd.read_csv(INPUT_PATH)

# ----------------------------
# Create date range
# ----------------------------
date_range = pd.date_range(
    start="2025-10-01",
    end="2025-12-31",
    freq="D"
)

# ----------------------------
# Expand to vehicle-day level
# ----------------------------
records = []

for _, row in df_base.iterrows():
    for d in date_range:
        records.append({
            "vehicle_id": row["vehicle_id"],
            "date": d,
            "battery_level": max(
                5,
                row["battery_level"] - np.random.normal(0.15, 0.05)
            ),
            "rides_today": max(
                0,
                int(row["rides_today"] + np.random.normal(0, 2))
            ),
            "distance_km": max(
                0.5,
                row["distance_km"] + np.random.normal(0, 1)
            ),
            "zone_id": row["city"]
        })

df_telemetry = pd.DataFrame(records)

# ----------------------------
# Save
# ----------------------------
df_telemetry.to_csv(OUTPUT_PATH, index=False)

print("✅ telemetry.csv generated")
print(f"Rows: {len(df_telemetry)}")
print(f"Vehicles: {df_telemetry['vehicle_id'].nunique()}")
print(f"Date range: {df_telemetry['date'].min()} → {df_telemetry['date'].max()}")
