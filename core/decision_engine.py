"""
Decision Engine for Fleet Intelligence AI

Generates actionable recommendations:
1. Risk-based categorization (CRITICAL/HIGH/MEDIUM/LOW)
2. Recommended actions (inspection, maintenance, rebalancing)
3. Revenue impact estimates
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from utils.logger import model_logger
from utils.config import config

class DecisionEngine:
    """Generates business decisions and recommendations"""
    
    def __init__(self):
        model_logger.info("DecisionEngine initialized")
    
    def generate_decisions(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate recommendations for each vehicle
        
        Args:
            df: Dataframe with risk scores
        
        Returns:
            Dataframe with added decision columns
        """
        df = df.copy()
        
        # Generate actions
        df['action'] = df.apply(self._assign_action, axis=1)
        df['urgency'] = df['risk_level'].map({
            'CRITICAL': '🚨 Immediate',
            'HIGH': '⚠️ 24 hours',
            'MEDIUM': '📅 1 week',
            'LOW': '✓ Monitor'
        })
        
        # Calculate impact
        df['estimated_loss_per_day'] = df.apply(self._calculate_loss, axis=1)
        
        model_logger.info(f"Generated decisions for {len(df)} vehicles")
        
        return df
    
    def _assign_action(self, row: pd.Series) -> str:
        """Assign recommended action based on vehicle state"""
        risk_level = row['risk_level']
        battery = row.get('battery', 50)
        maintenance_due = row.get('maintenance_due', False)
        utilization = row.get('utilization', 50)
        
        # Critical actions
        if risk_level == 'CRITICAL':
            if battery < 20:
                return "🔋 Charge immediately"
            if maintenance_due:
                return "🔧 Inspect immediately"
            return "🚨 Review status"
        
        # High risk actions
        if risk_level == 'HIGH':
            if battery < 30:
                return "🔋 Charge soon"
            if maintenance_due:
                return "🔧 Schedule maintenance"
            if utilization < 20:
                return "♻️ Rebalance"
            return "⚠️ Monitor closely"
        
        # Medium risk actions
        if risk_level == 'MEDIUM':
            if battery < 50:
                return "🔋 Consider charging"
            if utilization < 30:
                return "♻️ Consider rebalancing"
            return "📅 Schedule maintenance"
        
        # Low risk
        return "✓ Optimal"
    
    def _calculate_loss(self, row: pd.Series) -> float:
        """Estimate daily revenue loss if vehicle is not addressed"""
        risk_level = row['risk_level']
        battery = row.get('battery', 50)
        
        # Base loss rates (in ₹ or dollars)
        base_losses = {
            'CRITICAL': 500,  # Critical issue = high loss
            'HIGH': 200,      # High risk = moderate loss
            'MEDIUM': 50,     # Medium risk = low loss
            'LOW': 0           # Low risk = no loss
        }
        
        loss = base_losses.get(risk_level, 0)
        
        # Increase loss if battery is very low
        if battery < 20:
            loss = loss * 1.5
        
        return round(loss, 2)
    
    def get_summary_metrics(self, df: pd.DataFrame) -> Dict:
        """Get high-level metrics for dashboard"""
        total_vehicles = len(df)
        high_risk_count = len(df[df['risk_level'].isin(['HIGH', 'CRITICAL'])])
        estimated_daily_loss = df['estimated_loss_per_day'].sum()
        avg_battery = df['battery'].mean()
        avg_utilization = df['utilization'].mean()
        
        return {
            'total_vehicles': total_vehicles,
            'high_risk_count': high_risk_count,
            'high_risk_pct': round((high_risk_count / total_vehicles * 100), 1) if total_vehicles > 0 else 0,
            'estimated_daily_loss': round(estimated_daily_loss, 0),
            'avg_battery': round(avg_battery, 1),
            'avg_utilization': round(avg_utilization, 1),
        }
    
    def get_critical_actions(self, df: pd.DataFrame) -> List[str]:
        """Get list of critical actions needed"""
        actions = []
        
        critical_vehicles = df[df['risk_level'] == 'CRITICAL']
        if len(critical_vehicles) > 0:
            actions.append(f"🚨 {len(critical_vehicles)} vehicles need immediate attention")
        
        low_battery = df[df['battery'] < 20]
        if len(low_battery) > 0:
            actions.append(f"🔋 {len(low_battery)} vehicles have critical battery levels")
        
        maintenance_overdue = df[df.get('maintenance_due', False)]
        if len(maintenance_overdue) > 0:
            actions.append(f"🔧 {len(maintenance_overdue)} vehicles need maintenance")
        
        high_idle = df[df['utilization'] < 20]
        if len(high_idle) > 0:
            actions.append(f"♻️ {len(high_idle)} idle vehicles could be rebalanced")
        
        return actions

# Create global instance
decision_engine = DecisionEngine()
