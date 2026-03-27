"""
Data preprocessing module for Fleet Intelligence AI

Handles:
- CSV validation
- Missing value imputation
- Data type conversion
- Schema validation
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any
from utils.logger import data_logger
from utils.config import config

def validate_csv_schema(df: pd.DataFrame) -> Tuple[bool, str]:
    """
    Validate that CSV has required columns
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_cols = ["vehicle_id", "battery", "utilization", "zone"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        return False, f"Missing required columns: {', '.join(missing_cols)}"
    
    if len(df) == 0:
        return False, "CSV is empty (0 rows)"
    
    if len(df) > config.MAX_UPLOAD_ROWS:
        return False, f"CSV exceeds max rows ({config.MAX_UPLOAD_ROWS})"
    
    return True, "✅ Schema valid"

def clean_fleet_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and preprocess fleet data
    
    Args:
        df: Raw dataframe from CSV
    
    Returns:
        Cleaned dataframe
    """
    df = df.copy()
    
    # Convert vehicle_id to string
    df['vehicle_id'] = df['vehicle_id'].astype(str).str.strip()
    
    # Handle battery (0-100%)
    if 'battery' in df.columns:
        df['battery'] = pd.to_numeric(df['battery'], errors='coerce')
        df['battery'] = df['battery'].clip(0, 100)
        df['battery'].fillna(50, inplace=True)
    
    # Handle utilization (0-100%)
    if 'utilization' in df.columns:
        df['utilization'] = pd.to_numeric(df['utilization'], errors='coerce')
        df['utilization'] = df['utilization'].clip(0, 100)
        df['utilization'].fillna(50, inplace=True)
    
    # Standardize zone names
    if 'zone' in df.columns:
        df['zone'] = df['zone'].astype(str).str.lower().str.strip()
        # Map to valid zones, otherwise 'other'
        valid_zones = config.ZONES
        df['zone'] = df['zone'].where(df['zone'].isin(valid_zones), 'other')
    
    # Handle trips_last_7d
    if 'trips_last_7d' in df.columns:
        df['trips_last_7d'] = pd.to_numeric(df['trips_last_7d'], errors='coerce')
        df['trips_last_7d'] = df['trips_last_7d'].clip(0, None)
        df['trips_last_7d'].fillna(0, inplace=True).astype(int)
    else:
        df['trips_last_7d'] = 0
    
    # Handle maintenance_due
    if 'maintenance_due' in df.columns:
        df['maintenance_due'] = df['maintenance_due'].fillna(False).astype(bool)
    else:
        df['maintenance_due'] = False
    
    # Remove duplicates by vehicle_id (keep first)
    df = df.drop_duplicates(subset=['vehicle_id'], keep='first')
    
    data_logger.info(f"Cleaned {len(df)} vehicle records")
    
    return df.reset_index(drop=True)

def detect_outliers(df: pd.DataFrame) -> Dict[str, list]:
    """
    Detect potential data quality issues
    
    Returns:
        Dictionary of outliers by column
    """
    outliers = {}
    
    # Battery outliers (abnormally low)
    if 'battery' in df.columns:
        critical_battery = df[df['battery'] < config.BATTERY_CRITICAL_THRESHOLD]
        if len(critical_battery) > 0:
            outliers['critical_battery'] = critical_battery['vehicle_id'].tolist()
    
    # Utilization outliers (all idle)
    if 'utilization' in df.columns:
        all_idle = df[df['utilization'] < config.UTILIZATION_IDLE_THRESHOLD]
        if len(all_idle) > len(df) * 0.5:  # If >50% idle, it's notable
            outliers['high_idle_rate'] = len(all_idle)
    
    return outliers
