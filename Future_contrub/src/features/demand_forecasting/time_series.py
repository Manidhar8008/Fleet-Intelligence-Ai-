import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def analyze_temporal_patterns():
    """Analyze how scooter availability changes over time"""
    
    conn = sqlite3.connect('data/lime_data.db')
    query = """
    SELECT 
        strftime('%Y-%m-%d %H:00', collected_at) as hour,
        COUNT(*) as total_bikes,
        SUM(CASE WHEN is_disabled=1 THEN 1 ELSE 0 END) as disabled_count,
        SUM(CASE WHEN is_reserved=1 THEN 1 ELSE 0 END) as reserved_count
    FROM vehicles
    GROUP BY hour
    ORDER BY hour DESC
    LIMIT 24
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        print(⚠️ No temporal data found")
        return None
    
    # Calculate availability percentage
    df['availability_percent'] = ((df['total_bikes'] - df['disabled_count'] - df['reserved_count']) 
                                   / df['total_bikes'] * 100).round(2)
    
    print("\n📊 TEMPORAL ANALYSIS (Last 24 Hours):")
    print("=" * 80)
    print(f"{'Time':<20} {'Total':<10} {'Disabled':<12} {'Reserved':<12} {'Available %':<12}")
    print("=" * 80)
    
    for idx, row in df.iterrows():
        print(f"{row['hour']:<20} {row['total_bikes']:<10} {row['disabled_count']:<12} {row['reserved_count']:<12} {row['availability_percent']:<12}")
    
    print("=" * 80)
    
    # Statistics
    print(f"\n📈 STATISTICS:")
    print(f"   Average availability: {df['availability_percent'].mean():.2f}%")
    print(f"   Max availability: {df['availability_percent'].max():.2f}%")
    print(f"   Min availability: {df['availability_percent'].min():.2f}%")
    
    return df

if __name__ == "__main__":
    analyze_temporal_patterns()
