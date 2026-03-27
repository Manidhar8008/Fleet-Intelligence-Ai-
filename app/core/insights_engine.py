"""
AI Insights Engine for Fleet Intelligence AI

Generates business-friendly insights and recommendations
"""

import pandas as pd
from typing import List
import os
import sys

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import model_logger
from utils.config import config

class InsightsEngine:
    """Generates actionable business insights"""
    
    def __init__(self):
        model_logger.info("InsightsEngine initialized")
    
    def generate_insights(self, df: pd.DataFrame) -> List[str]:
        """
        Generate list of business insights
        
        Args:
            df: Processed dataframe with risk scores and decisions
        
        Returns:
            List of insight strings
        """
        insights = []
        
        total = len(df)
        if total == 0:
            return ["No data available for analysis"]
        
        # Insight 1: Fleet health overview
        critical_count = len(df[df['risk_level'] == 'CRITICAL'])
        high_count = len(df[df['risk_level'] == 'HIGH'])
        critical_pct = round((critical_count / total) * 100, 1)
        
        if critical_count > 0:
            insights.append(
                f"⚠️ {critical_count} vehicles ({critical_pct}%) are in CRITICAL condition and need immediate action"
            )
        
        if critical_count + high_count > total * 0.3:
            insights.append(
                f"🔴 {critical_count + high_count} vehicles ({round((critical_count + high_count) / total * 100, 1)}%) are high-risk. "
                "Consider immediate intervention."
            )
        else:
            insights.append(
                f"🟢 Fleet health is good - {total - critical_count - high_count} vehicles ({round((total - critical_count - high_count) / total * 100, 1)}%) are in safe condition"
            )
        
        # Insight 2: Battery analysis
        low_battery = df[df['battery'] < 30]
        if len(low_battery) > 0:
            insights.append(
                f"🔋 {len(low_battery)} vehicles have low battery (<30%). "
                f"Estimated cost: ₹{len(low_battery) * 100:,.0f} in potential downtime"
            )
        
        # Insight 3: Utilization analysis
        idle_vehicles = df[df['utilization'] < 20]
        if len(idle_vehicles) > 0:
            insights.append(
                f"♻️ {len(idle_vehicles)} vehicles are idle (<20% utilization). "
                f"Rebalancing could generate ₹{len(idle_vehicles) * 50:,.0f}/day"
            )
        
        # Insight 4: Zone analysis
        if 'zone' in df.columns:
            zone_dist = df['zone'].value_counts()
            max_zone = zone_dist.idxmax()
            min_zone = zone_dist.idxmin()
            
            if zone_dist[max_zone] > zone_dist[min_zone] * 2:
                insights.append(
                    f"📍 Zone imbalance detected: '{max_zone}' has {zone_dist[max_zone]} vehicles "
                    f"vs '{min_zone}' has {zone_dist[min_zone]}. Consider rebalancing."
                )
        
        # Insight 5: Maintenance
        if 'maintenance_due' in df.columns:
            maintenance_needed = df[df['maintenance_due']]
            if len(maintenance_needed) > 0:
                insights.append(
                    f"🔧 {len(maintenance_needed)} vehicles need maintenance. "
                    f"Preventive maintenance could reduce downtime by 30-40%"
                )
        
        # Insight 6: Revenue opportunity
        potential_gain = len(idle_vehicles) * 50 + len(low_battery) * 100
        if potential_gain > 0:
            insights.append(
                f"💰 Potential daily revenue recovery: ₹{potential_gain:,.0f} through optimization"
            )
        
        # Insight 7: Battery trend
        avg_battery = df['battery'].mean()
        critical_battery = len(df[df['battery'] < 20])
        if critical_battery > total * 0.15:
            insights.append(
                f"📉 Battery health is concerning: {critical_battery} vehicles (<20%). "
                f"Average fleet battery: {avg_battery:.1f}%"
            )
        
        # Insight 8: Predictive warning
        if 'maintenance_due' in df.columns:
            high_risk_maintenance_combo = df[
                (df['risk_level'].isin(['HIGH', 'CRITICAL'])) & 
                (df['maintenance_due'])
            ]
            if len(high_risk_maintenance_combo) > 0:
                insights.append(
                    f"🚨 {len(high_risk_maintenance_combo)} vehicles are high-risk AND need maintenance. "
                    "Address these immediately to prevent breakdowns."
                )
        
        model_logger.info(f"Generated {len(insights)} insights")
        
        return insights[:8]  # Return top 8 insights
    
    def get_zone_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Get summary by zone
        
        Returns:
            Dataframe with zone-level statistics
        """
        if 'zone' not in df.columns or len(df) == 0:
            return pd.DataFrame()
        
        zone_summary = df.groupby('zone').agg({
            'vehicle_id': 'count',
            'battery': 'mean',
            'utilization': 'mean',
            'risk_score': 'mean' if 'risk_score' in df.columns else ('risk_level', 'first'),
            'estimated_loss_per_day': 'sum' if 'estimated_loss_per_day' in df.columns else ('vehicle_id', 'count')
        }).round(1)
        
        zone_summary.columns = ['Vehicles', 'Avg Battery', 'Avg Utilization', 'Avg Risk', 'Daily Loss (₹)']
        
        return zone_summary.sort_values('Daily Loss (₹)', ascending=False)

# Create global instance
insights_engine = InsightsEngine()
