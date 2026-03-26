import pandas as pd
import matplotlib.pyplot as plt
import os

# -----------------------------
# Resolve project root
# -----------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "Decision",
    "asset_decision_final.csv"
)

OUTPUT_DIR = os.path.join(
    PROJECT_ROOT,
    "artifacts",
    "visuals"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# -----------------------------
# Load data
# -----------------------------
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"Decision file not found at: {DATA_PATH}")

df = pd.read_csv(DATA_PATH)

print("Available columns:")
print(df.columns.tolist())

# -----------------------------
# 1. Intervention Risk Score Distribution
# -----------------------------
plt.figure()
plt.hist(df["intervention_risk_score"], bins=30)
plt.axvline(0.8)
plt.title("Intervention Risk Score Distribution")
plt.xlabel("Intervention Risk Score")
plt.ylabel("Count")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "01_intervention_risk_distribution.png"))
plt.close()

# -----------------------------
# 2. Risk vs Battery Health
# -----------------------------
plt.figure()
plt.scatter(df["battery_health_index"], df["intervention_risk_score"])
plt.title("Risk vs Battery Health")
plt.xlabel("Battery Health Index")
plt.ylabel("Intervention Risk Score")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "02_risk_vs_battery_health.png"))
plt.close()

# -----------------------------
# 3. Utilization vs Risk
# -----------------------------
plt.figure()
plt.scatter(df["utilization_percentile"], df["intervention_risk_score"])
plt.title("Utilization vs Intervention Risk")
plt.xlabel("Utilization Percentile")
plt.ylabel("Intervention Risk Score")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "03_utilization_vs_risk.png"))
plt.close()

# -----------------------------
# 4. Recommended Actions Breakdown
# -----------------------------
action_counts = df["recommended_action"].value_counts()

plt.figure()
action_counts.plot(kind="bar")
plt.title("Recommended Actions Breakdown")
plt.xlabel("Action")
plt.ylabel("Count")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "04_recommended_actions_breakdown.png"))
plt.close()

print("✅ Visualization artifacts generated successfully.")
print(f"📁 Output directory: {OUTPUT_DIR}")
# -------------------------------------------------------------------------------------------------------------------------------------------------------------