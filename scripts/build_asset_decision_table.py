"""
Purpose:
    Generate decision-ready asset table from raw IoT telemetry

Input:
    data/raw/lime_vehicles_sample.csv

Output:
    data/final/asset_decision_final.csv

Decisions Enabled:
    - Continue operation
    - Inspect asset
    - Repair / Rotate asset

Assumptions:
    - Battery health inferred from battery_level
    - Utilization inferred from rides_today
    - Zone stress inferred from deployment density
"""

import pandas as pd
import numpy as np

# ----------------------------
# Utility
# ----------------------------
def log_shape(df, label):
    print(f"[{label}] rows={len(df)} cols={len(df.columns)}")

# ----------------------------
# 1. Load raw data
# ----------------------------
df = pd.read_csv("data/raw/lime_vehicles_sample.csv")
df_raw = df.copy()

# ----------------------------
# 2. Battery health proxy
# ----------------------------
df["battery_health_index"] = df["battery_level"] / 100

# ----------------------------
# 3. Time-based aggregates
# ----------------------------
df["battery_level_avg_7d"] = df["battery_level"].rolling(7, min_periods=1).mean()
df["battery_level_avg_30d"] = df["battery_level"].rolling(30, min_periods=1).mean()

df["battery_trend_7d_vs_30d"] = (
    df["battery_level_avg_7d"] - df["battery_level_avg_30d"]
)
df["health_decline_rate"] = -df["battery_trend_7d_vs_30d"]

# ----------------------------
# 4. Usage features
# ----------------------------
df["rides_per_day_avg"] = df["rides_today"].rolling(7, min_periods=1).mean()
df["utilization_trend"] = df["rides_today"].diff().fillna(0)
df["utilization_percentile"] = df["rides_per_day_avg"].rank(pct=True)

# ----------------------------
# 5. Zone construction
# ----------------------------
df["zone_id"] = df["city"]

zone_stats = (
    df.groupby("zone_id")
      .agg(
          zone_rides=("rides_today", "mean"),
          zone_assets=("vehicle_id", "nunique")
      )
      .reset_index()
)

zone_stats["deployment_density"] = (
    zone_stats["zone_rides"] / zone_stats["zone_assets"]
)

df = df.merge(zone_stats, on="zone_id", how="left")

# ----------------------------
# 6. Zone stress index (ROBUST)
# ----------------------------
df["zone_stress_index"] = pd.cut(
    df["deployment_density"],
    bins=[-np.inf, 1.0, 2.5, np.inf],
    labels=["low", "medium", "high"],
    include_lowest=True
)

# ----------------------------
# 7. Intervention risk score
# ----------------------------
df["intervention_risk_score"] = (
    0.5 * df["health_decline_rate"].clip(lower=0)
    + 0.3 * df["utilization_trend"].clip(lower=0)
    + 0.2 * (df["zone_stress_index"] == "high").astype(int)
)

# ----------------------------
# 8. Confidence level
# ----------------------------
conditions = [
    (df["battery_level_avg_30d"].notna()) & (df["rides_per_day_avg"] > 0),
    (df["battery_level_avg_30d"].notna()),
]
choices = ["High", "Medium"]

df["confidence_level"] = np.select(conditions, choices, default="Low")

# ----------------------------
# 9. Decision logic
# ----------------------------
def decide(row):
    if row["intervention_risk_score"] > 1.0 and row["confidence_level"] == "High":
        return "repair_or_rotate"
    if row["intervention_risk_score"] > 1.0:
        return "inspect"
    return "continue"

df["recommended_action"] = df.apply(decide, axis=1)

# ----------------------------
# 10. Final decision table (LOCKED)
# ----------------------------
final_cols = [
    "vehicle_id",
    "city",
    "zone_id",
    "battery_health_index",
    "battery_level_avg_7d",
    "battery_level_avg_30d",
    "health_decline_rate",
    "rides_per_day_avg",
    "utilization_percentile",
    "battery_trend_7d_vs_30d",
    "zone_stress_index",
    "deployment_density",
    "intervention_risk_score",
    "confidence_level",
    "recommended_action",
]

df_final = df[final_cols].copy()

# ----------------------------
# 11. Logging
# ----------------------------
log_shape(df_raw, "RAW")
log_shape(df, "FEATURE_ENGINEERED")
log_shape(df_final, "FINAL_DECISION_TABLE")

print("\nSignals available in FINAL dataset:")
for c in df_final.columns:
    print(" -", c)

# ----------------------------
# 12. Write final output
# ----------------------------
OUTPUT_PATH = "data/final/asset_decision_final.csv"
df_final.to_csv(OUTPUT_PATH, index=False)

print("\nFINAL DATASET LOCKED AT:", OUTPUT_PATH)






