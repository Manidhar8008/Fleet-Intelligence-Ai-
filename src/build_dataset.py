import pandas as pd
import os

RAW_DIR = "data/raw"
FINAL_DIR = "data/final"
os.makedirs(FINAL_DIR, exist_ok=True)

SOURCE_FILE = "E-Scooter_Trips.csv"
CITY = "Chicago"

print("Loading raw data in chunks...")

chunks = []
MAX_ROWS = 200_000

use_cols = [
    "Trip ID",
    "Start Time",
    "End Time",
    "Trip Duration",
    "Start Centroid Latitude",
    "Start Centroid Longitude",
    "End Centroid Latitude",
    "End Centroid Longitude"
]

rows_read = 0

for chunk in pd.read_csv(
    os.path.join(RAW_DIR, SOURCE_FILE),
    usecols=lambda c: c in use_cols,
    chunksize=50_000,
    low_memory=False
):
    rows_read += len(chunk)
    chunks.append(chunk)
    if rows_read >= MAX_ROWS:
        break

df = pd.concat(chunks, ignore_index=True)

print("Rows loaded:", len(df))

df.rename(columns={
    "Trip ID": "trip_id",
    "Start Time": "start_time",
    "End Time": "end_time",
    "Trip Duration": "duration_min",
    "Start Centroid Latitude": "start_lat",
    "Start Centroid Longitude": "start_lng",
    "End Centroid Latitude": "end_lat",
    "End Centroid Longitude": "end_lng"
}, inplace=True)

df["start_time"] = pd.to_datetime(df["start_time"], errors="coerce")
df["end_time"] = pd.to_datetime(df["end_time"], errors="coerce")

df = df.dropna(subset=["start_time", "end_time", "start_lat", "start_lng"])

df["User_id"] = "UNKNOWN"
df["User_catgo"] = "unknown"
df["vehicle_type"] = "scooter"
df["zone_id"] = "UNASSIGNED"
df["Trip cost"] = 1 + 0.2 * df["duration_min"]
df["Discount"] = 0.0
df["Invoice"] = df["Trip cost"]
df["city"] = CITY
df["temperature"] = None
df["rain"] = None
df["wind"] = None

final_cols = [
    "User_id", "User_catgo", "trip_id",
    "start_time", "end_time",
    "start_lat", "start_lng", "end_lat", "end_lng",
    "duration_min", "vehicle_type", "zone_id",
    "Trip cost", "Discount", "Invoice",
    "city", "temperature", "rain", "wind"
]

df_final = df[final_cols]

out = os.path.join(FINAL_DIR, "lime_final.csv")
df_final.to_csv(out, index=False)

print("FINAL dataset created:", out)
print("Final rows:", len(df_final))
