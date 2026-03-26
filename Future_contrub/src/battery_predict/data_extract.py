import sqlite3
import pandas as pd
from pathlib import Path

# Point to the DB in project_root/data/lime_data.db
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data" / "lime_data.db"


def get_battery_data(limit: int = 10000) -> pd.DataFrame:
    """Load battery-related records from the vehicles table."""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT latitude,
               longitude,
               is_disabled,
               is_reserved,
               vehicle_type,
               battery_level,
               collected_at
        FROM vehicles
        WHERE battery_level IS NOT NULL
        LIMIT ?
    """
    df = pd.read_sql_query(query, conn, params=(limit,))
    conn.close()

    print(f"✅ Loaded {len(df)} records from {DB_PATH}")
    print(df.head())
    return df


if __name__ == "__main__":
    get_battery_data()
