"""
Database setup and schema for Lime IoT ML Platform
Stores real-time vehicle location and status data
"""

import sqlite3
from datetime import datetime
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent.parent.parent / "data" / "lime_data.db"

def create_database():
    """Create SQLite database with vehicle tracking schema"""
    
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create vehicles table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vehicles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bike_id TEXT UNIQUE NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        vehicle_type TEXT,
        is_disabled BOOLEAN DEFAULT 0,
        is_reserved BOOLEAN DEFAULT 0,
        battery_level REAL,
        collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create daily summary table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS daily_summary (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        collection_date DATE UNIQUE,
        total_vehicles INTEGER,
        available_vehicles INTEGER,
        disabled_vehicles INTEGER,
        reserved_vehicles INTEGER,
        avg_battery REAL,
        collection_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    print("✅ Database created successfully!")
    print(f"📁 Database location: {DB_PATH}")
    
    return conn

def insert_vehicle(bike_id, lat, lon, vehicle_type, is_disabled, is_reserved, battery):
    """Insert vehicle data into database"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        INSERT OR REPLACE INTO vehicles 
        (bike_id, latitude, longitude, vehicle_type, is_disabled, is_reserved, battery_level)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (bike_id, lat, lon, vehicle_type, is_disabled, is_reserved, battery))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Error inserting vehicle: {e}")
        return False
    finally:
        conn.close()

def get_vehicle_count():
    """Get total vehicles in database"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM vehicles')
    count = cursor.fetchone()[0]
    conn.close()
    
    return count

def get_daily_stats(collection_date=None):
    """Get daily statistics"""
    
    if collection_date is None:
        collection_date = datetime.now().strftime('%Y-%m-%d')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN is_disabled=0 AND is_reserved=0 THEN 1 ELSE 0 END) as available,
        SUM(CASE WHEN is_disabled=1 THEN 1 ELSE 0 END) as disabled,
        SUM(CASE WHEN is_reserved=1 THEN 1 ELSE 0 END) as reserved,
        AVG(battery_level) as avg_battery
    FROM vehicles
    WHERE DATE(collected_at) = ?
    ''', (collection_date,))
    
    result = cursor.fetchone()
    conn.close()
    
    return {
        'total': result[0],
        'available': result[1],
        'disabled': result[2],
        'reserved': result[3],
        'avg_battery': result[4]
    }

if __name__ == "__main__":
    create_database()
    print(f"📊 Current vehicles in database: {get_vehicle_count()}")
    print(f"📈 Today's stats: {get_daily_stats()}")
