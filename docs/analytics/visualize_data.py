import sqlite3
import matplotlib.pyplot as plt

conn = sqlite3.connect('data/lime_data.db')
cursor = conn.cursor()

cursor.execute("SELECT latitude, longitude FROM vehicles LIMIT 1000")
points = cursor.fetchall()
conn.close()

if points:
    lats, lons = zip(*points)
    plt.figure(figsize=(10, 8))
    plt.scatter(lons, lats, s=3, alpha=0.5)
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title("Vehicle Locations (First 1000)")
    plt.savefig("vehicle_locations.png", dpi=150)
    print("✅ Saved visualization to vehicle_locations.png")
    plt.show()
