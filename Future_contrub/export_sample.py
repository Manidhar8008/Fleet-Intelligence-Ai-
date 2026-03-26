import pandas as pd
import json

# Load the Lime sample JSON
with open("sample_lime_data_20251109_123053.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Extract the real list of vehicles
bikes = data["data"]["bikes"]

# Convert to DataFrame
df = pd.DataFrame(bikes)

# Take first 100
sample = df.head(100)

# Save to CSV
sample.to_csv("sample_vehicles.csv", index=False)
print("✅ Export complete:", len(sample), "rows saved to sample_vehicles.csv")
print("Columns:", list(df.columns))
