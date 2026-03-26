import sqlite3
import pandas as pd

def generate_quality_report():
    """Generate data quality metrics"""
    
    conn = sqlite3.connect('data/lime_data.db')
    
    # Overall stats
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM vehicles")
    total_records = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT bike_id) FROM vehicles")
    unique_bikes = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM vehicles WHERE is_disabled = 1")
    disabled_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM vehicles WHERE is_reserved = 1")
    reserved_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM vehicles WHERE battery_level IS NULL")
    missing_battery = cursor.fetchone()[0]
    
    conn.close()
    
    print("\n📋 DATA QUALITY REPORT:")
    print("=" * 60)
    print(f"Total Records: {total_records:,}")
    print(f"Unique Bikes: {unique_bikes:,}")
    print(f"Disabled Bikes: {disabled_count:,} ({disabled_count/total_records*100:.2f}%)")
    print(f"Reserved Bikes: {reserved_count:,} ({reserved_count/total_records*100:.2f}%)")
    print(f"Missing Battery Data: {missing_battery:,} ({missing_battery/total_records*100:.2f}%)")
    print(f"Data Completeness: {(1 - missing_battery/total_records)*100:.2f}%")
    print("=" * 60)
    
    # Status
    if missing_battery/total_records > 0.2:
        print("⚠️ WARNING: High missing battery data (>20%)")
    else:
        print("✅ Data quality is good")

if __name__ == "__main__":
    generate_quality_report()
