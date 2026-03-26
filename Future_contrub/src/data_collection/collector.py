"""
Synthetic IoT data generator for micromobility fleet analytics
"""

import random
from datetime import datetime
from src.data_collection.database import create_database, insert_vehicle, get_daily_stats

def collect_vehicles():
    print("🚀 Generating synthetic fleet data...")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)

    create_database()

    vehicle_types = ["scooter", "ebike"]
    count = 5000

    inserted = 0
    for i in range(count):
        lat = 47.60 + random.uniform(-0.05, 0.05)
        lon = -122.33 + random.uniform(-0.05, 0.05)
        vtype = random.choice(vehicle_types)
        disabled = random.choice([0,0,0,1])  # 25% disabled
        reserved = random.choice([0,0,1])    # 33% reserved
        battery = max(0, min(100, random.gauss(60, 25)))  # mean 60, sigma 25

        success = insert_vehicle(
            bike_id=f"DEV-{i}",
            lat=lat,
            lon=lon,
            vehicle_type=vtype,
            is_disabled=disabled,
            is_reserved=reserved,
            battery=battery
        )

        if success:
            inserted += 1

    stats = get_daily_stats()
    print("-" * 60)
    print(f"📊 Synthetic Vehicles: {inserted}")
    print(f"Avg Battery: {stats['avg_battery']:.1f}%")
    print(f"Disabled: {stats['disabled']}")
    print(f"Reserved: {stats['reserved']}")
    print("-" * 60)
    print("🎉 Synthetic collection complete!")

if __name__ == "__main__":
    collect_vehicles()
