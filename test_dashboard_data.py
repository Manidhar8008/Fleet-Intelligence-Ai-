"""
Test script to show dashboard data without running Streamlit

This loads 50 vehicles, scores them, applies filters, and shows the output.
"""

import pandas as pd
from datetime import datetime

from src.decision_engine import FleetDecisionEngine, FleetDecisionBatch, RiskLevel
from src.data_loader import ProductionDataLoader, DataSource


def main():
    print("\n" + "=" * 90)
    print("MINIMAL FLEET DASHBOARD - DATA PREVIEW")
    print("=" * 90)
    
    # Load & Score
    print("\n📊 Loading 50 vehicles...")
    loader = ProductionDataLoader()
    vehicles = loader.load_vehicles(source=DataSource.SAMPLE, limit=50)
    print(f"   ✅ Loaded {len(vehicles)} vehicles")
    
    print("\n🧠 Scoring vehicles...")
    engine = FleetDecisionEngine()
    batch = FleetDecisionBatch(engine)
    decisions = batch.score_fleet(list(vehicles.values()))
    print(f"   ✅ Scored {len(decisions)} vehicles")
    
    # Prepare data
    data = []
    for vehicle_id, decision in decisions.items():
        vehicle = vehicles[vehicle_id]
        alert = ""
        if decision.alerts:
            alert = decision.alerts[0]['message']
        
        data.append({
            'Vehicle ID': vehicle_id,
            'Risk Score': int(decision.risk_score),
            'Risk Level': decision.risk_level.value,
            'Battery': int(vehicle.battery_pct),
            'Alert': alert,
            'Recommendation': decision.recommended_action.value,
            'Zone': vehicle.zone_id,
        })
    
    df = pd.DataFrame(data)
    
    # ========================================================================
    # SUMMARY METRICS
    # ========================================================================
    print("\n" + "=" * 90)
    print("SUMMARY METRICS")
    print("=" * 90)
    
    total_vehicles = len(df)
    avg_risk = df['Risk Score'].mean()
    alert_count = len([a for a in df['Alert'] if a])
    critical_count = len(df[df['Risk Level'] == 'CRITICAL'])
    high_count = len(df[df['Risk Level'] == 'HIGH'])
    medium_count = len(df[df['Risk Level'] == 'MEDIUM'])
    low_count = len(df[df['Risk Level'] == 'LOW'])
    
    print(f"  Total Vehicles:     {total_vehicles}")
    print(f"  Avg Risk Score:     {avg_risk:.0f}/100")
    print(f"  Active Alerts:      {alert_count}")
    print(f"  Critical Vehicles:  {critical_count}")
    print(f"\n  Risk Distribution:")
    print(f"    🟢 Low:      {low_count} vehicles ({low_count/total_vehicles*100:.0f}%)")
    print(f"    🟡 Medium:   {medium_count} vehicles ({medium_count/total_vehicles*100:.0f}%)")
    print(f"    🟠 High:     {high_count} vehicles ({high_count/total_vehicles*100:.0f}%)")
    print(f"    🔴 Critical: {critical_count} vehicles ({critical_count/total_vehicles*100:.0f}%)")
    
    # ========================================================================
    # FULL TABLE
    # ========================================================================
    print("\n" + "=" * 90)
    print("VEHICLE TABLE (All 50 vehicles)")
    print("=" * 90)
    print()
    
    # Format for display
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)
    
    print(df.to_string(index=False))
    
    # ========================================================================
    # FILTER: HIGH RISK ONLY
    # ========================================================================
    print("\n" + "=" * 90)
    print("FILTER: HIGH RISK ONLY")
    print("=" * 90)
    
    df_high_risk = df[df['Risk Level'].isin(['HIGH', 'CRITICAL'])]
    print(f"\nFound {len(df_high_risk)} high-risk vehicles:\n")
    
    if len(df_high_risk) > 0:
        print(df_high_risk.to_string(index=False))
    else:
        print("  (No high-risk vehicles)")
    
    # ========================================================================
    # FILTER: LOW BATTERY ONLY
    # ========================================================================
    print("\n" + "=" * 90)
    print("FILTER: LOW BATTERY ONLY (< 30%)")
    print("=" * 90)
    
    df_low_battery = df[df['Battery'] < 30]
    print(f"\nFound {len(df_low_battery)} low-battery vehicles:\n")
    
    if len(df_low_battery) > 0:
        print(df_low_battery.to_string(index=False))
    else:
        print("  (No low-battery vehicles)")
    
    # ========================================================================
    # FILTER: HIGH RISK AND LOW BATTERY
    # ========================================================================
    print("\n" + "=" * 90)
    print("FILTER: HIGH RISK AND LOW BATTERY")
    print("=" * 90)
    
    df_both = df[(df['Risk Level'].isin(['HIGH', 'CRITICAL'])) & (df['Battery'] < 30)]
    print(f"\nFound {len(df_both)} critical vehicles (high risk + low battery):\n")
    
    if len(df_both) > 0:
        print(df_both.to_string(index=False))
    else:
        print("  (None found - good news!)")
    
    # ========================================================================
    # TOP ALERTS
    # ========================================================================
    print("\n" + "=" * 90)
    print("TOP ALERTS (First 5)")
    print("=" * 90)
    
    df_alerts = df[df['Alert'] != ''].head(5)
    for idx, row in df_alerts.iterrows():
        print(f"\n  {row['Vehicle ID']}")
        print(f"    Risk: {row['Risk Level']} ({row['Risk Score']}/100)")
        print(f"    Battery: {row['Battery']}%")
        print(f"    Alert: {row['Alert']}")
        print(f"    Action: {row['Recommendation']}")
    
    print("\n" + "=" * 90)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 90 + "\n")


if __name__ == "__main__":
    main()
