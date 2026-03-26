import sqlite3
import pandas as pd
from geopy.distance import geodesic

def find_hotspots(grid_size_km=1):
    """Find high-density vehicle clusters (hotspots)"""
    
    conn = sqlite3.connect('data/lime_data.db')
    query = "SELECT latitude, longitude, is_disabled FROM vehicles LIMIT 1000"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Group by lat/lon grid
    df['lat_grid'] = (df['latitude'] * 100).astype(int) / 100
    df['lon_grid'] = (df['longitude'] * 100).astype(int) / 100
    
    # Count density per grid cell
    hotspots = df.groupby(['lat_grid', 'lon_grid']).agg({
        'is_disabled': 'count',
        'latitude': 'mean',
        'longitude': 'mean'
    }).rename(columns={'is_disabled': 'vehicle_count'}).reset_index()
    
    # Sort by density
    hotspots = hotspots.sort_values('vehicle_count', ascending=False)
    
    print("\n🔥 TOP VEHICLE HOTSPOTS:")
    print("=" * 70)
    print(f"{'Rank':<6} {'Latitude':<12} {'Longitude':<12} {'Count':<10}")
    print("=" * 70)
    
    for idx, (i, row) in enumerate(hotspots.head(10).iterrows(), 1):
        print(f"{idx:<6} {row['latitude']:<12.4f} {row['longitude']:<12.4f} {row['vehicle_count']:<10.0f}")
    
    print("=" * 70)
    
    return hotspots

if __name__ == "__main__":
    find_hotspots()
