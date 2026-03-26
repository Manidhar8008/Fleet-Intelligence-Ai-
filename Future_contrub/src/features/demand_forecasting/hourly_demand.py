import sqlite3
import pandas as pd

def get_hourly_demand():
    """Get demand statistics by hour"""
    conn = sqlite3.connect('data/lime_data.db')
    query = "SELECT * FROM vehicles LIMIT 100"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    print(f"✅ Retrieved {len(df)} records")
    print(f"   Columns: {df.columns.tolist()}")
    return df

if __name__ == "__main__":
    get_hourly_demand()
