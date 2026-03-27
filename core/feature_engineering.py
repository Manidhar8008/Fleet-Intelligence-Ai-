"""
Feature engineering module for Fleet Intelligence AI

Generates derived features for risk scoring:
- battery_health_score (0-100)
- usage_intensity_score (0-100)
- maintenance_urgency_score (0-100)
- zone_pressure_score (0-100)
"""

import pandas as pd
import numpy as np
from utils.logger import model_logger
from utils.config import config

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate features for risk scoring
    
    Args:
        df: Cleaned dataframe
    
    Returns:
        Dataframe with engineered features
    """
    df = df.copy()
    
    # 1. Battery Health Score (inverse of battery level)
    # Low battery = high risk
    df['battery_health_score'] = 100 - df['battery']  # 0-100
    
    # 2. Usage Intensity Score
    # Low utilization = potential revenue loss = higher risk
    if 'utilization' in df.columns:
        df['usage_intensity_score'] = 100 - df['utilization']  # 0-100
    else:
        df['usage_intensity_score'] = 50
    
    # 3. Maintenance Urgency Score
    # Boolean to score: maintenance_due=True -> 80, False -> 20
    if 'maintenance_due' in df.columns:
        df['maintenance_urgency_score'] = df['maintenance_due'].map({True: 80, False: 20})
    else:
        df['maintenance_urgency_score'] = 20
    
    # 4. Zone Pressure Score
    # Calculate supply/demand imbalance per zone
    df['zone_pressure_score'] = _calculate_zone_pressure(df)
    
    # 5. Usage Velocity (recent activity indicator)
    if 'trips_last_7d' in df.columns:
        # High trips = high velocity = lower risk
        df['usage_velocity'] = df['trips_last_7d'].clip(0, 100)
    else:
        df['usage_velocity'] = 50
    
    # 6. Overall utilization category
    df['utilization_category'] = df['utilization'].apply(_categorize_utilization)
    
    model_logger.info(f"Engineered features for {len(df)} vehicles")
    
    return df

def _categorize_utilization(util_pct: float) -> str:
    """Categorize utilization percentage"""
    if util_pct < 20:
        return "Idle"
    elif util_pct < 50:
        return "Low"
    elif util_pct < 80:
        return "Normal"
    else:
        return "Active"

def _calculate_zone_pressure(df: pd.DataFrame) -> pd.Series:
    """
    Calculate zone pressure score
    
    Higher supply (more vehicles) in same zone = higher pressure
    """
    zone_counts = df['zone'].value_counts()
    max_count = zone_counts.max()
    
    # Normalize zone counts to 0-100 score
    df['zone_vehicle_count'] = df['zone'].map(zone_counts)
    zone_pressure = (df['zone_vehicle_count'] / max_count * 100).clip(0, 100)
    
    return zone_pressure

def get_feature_statistics(df: pd.DataFrame) -> dict:
    """
    Get summary statistics for features
    
    Returns:
        Dictionary with stats
    """
    stats = {
        'avg_battery': df['battery'].mean(),
        'avg_utilization': df['utilization'].mean(),
        'maintenance_overdue_count': df['maintenance_due'].sum() if 'maintenance_due' in df.columns else 0,
        'vehicles_by_zone': df['zone'].value_counts().to_dict() if 'zone' in df.columns else {}
    }
    
    return stats
