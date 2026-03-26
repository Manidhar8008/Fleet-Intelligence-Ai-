"""
Data analysis and insights from collected vehicle data
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path(__file__).parent.parent.parent / "data" / "lime_data.db"

def analyze_vehicle_distribution():
    """Analyze geographic distribution of vehicles"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get bounding box
    cursor.execute('''
    SELECT 
        MIN(latitude) as min_lat,
        MAX(latitude) as max_lat,
        MIN(longitude) as min_lon,
        MAX(longitude) as max_lon,
        COUNT(*) as total_vehicles
    FROM vehicles
    ''')
    
    result = cursor.fetchone()
    
    print("🗺️  GEOGRAPHIC DISTRIBUTION:")
    print(f"   Latitude range: {result[0]:.4f} to {result[1]:.4f}")
    print(f"   Longitude range: {result[2]:.4f} to {result[3]:.4f}")
    print(f"   Total vehicles: {result[4]}")
    
    conn.close()

def analyze_vehicle_types():
    """Analyze distribution by vehicle type"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT vehicle_type, COUNT(*) as count
    FROM vehicles
    GROUP BY vehicle_type
    ORDER BY count DESC
    ''')
    
    print("\n🚗 VEHICLE TYPE DISTRIBUTION:")
    for vehicle_type, count in cursor.fetchall():
        print(f"   {vehicle_type}: {count} vehicles")
    
    conn.close()

def get_collection_timeline():
    """Show data collection timeline"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT DATE(collected_at) as date, COUNT(DISTINCT bike_id) as vehicles
    FROM vehicles
    GROUP BY DATE(collected_at)
    ORDER BY date DESC
    LIMIT 7
    ''')
    
    print("\n📅 COLLECTION TIMELINE (Last 7 days):")
    for date, count in cursor.fetchall():
        print(f"   {date}: {count} vehicles")
    
    conn.close()

if __name__ == "__main__":
    analyze_vehicle_distribution()
    analyze_vehicle_types()
    get_collection_timeline()
