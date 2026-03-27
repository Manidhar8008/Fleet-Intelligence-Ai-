"""
Data loader for Fleet Intelligence AI

Handles:
- CSV file uploads
- Demo data generation
- Data validation
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Tuple
import os
import sys

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import data_logger
from utils.config import config
from core.preprocessing import clean_fleet_data, validate_csv_schema

def load_csv_file(file_upload) -> Tuple[Optional[pd.DataFrame], str]:
    """
    Load CSV file from Streamlit file uploader
    
    Args:
        file_upload: Streamlit uploaded file object
    
    Returns:
        Tuple of (dataframe, status_message)
    """
    try:
        df = pd.read_csv(file_upload)
        data_logger.info(f"Loaded CSV with {len(df)} rows")
        
        # Validate schema
        is_valid, message = validate_csv_schema(df)
        if not is_valid:
            return None, f"❌ {message}"
        
        # Clean data
        df = clean_fleet_data(df)
        
        return df, f"✅ Loaded {len(df)} vehicles from CSV"
    
    except Exception as e:
        data_logger.error(f"Error loading CSV: {str(e)}")
        return None, f"❌ Error: {str(e)}"

def generate_demo_data(num_vehicles: int = None) -> pd.DataFrame:
    """
    Generate synthetic demo fleet data
    
    Args:
        num_vehicles: Number of vehicles to generate (default from config)
    
    Returns:
        Demo dataframe with realistic fleet data
    """
    if num_vehicles is None:
        num_vehicles = getattr(config, 'DEFAULT_DEMO_VEHICLES', 150)
    
    np.random.seed(42)
    
    zones = getattr(config, 'ZONES', ['Zone-A', 'Zone-B', 'Zone-C', 'Zone-D'])
    
    data = {
        'vehicle_id': [f'V-{i:05d}' for i in range(1, num_vehicles + 1)],
        'battery': np.random.uniform(10, 100, num_vehicles),
        'utilization': np.random.uniform(0, 100, num_vehicles),
        'zone': np.random.choice(zones, num_vehicles),
        'trips_last_7d': np.random.randint(0, 50, num_vehicles),
        'maintenance_due': np.random.choice([True, False], num_vehicles, p=[0.1, 0.9]),
    }
    
    df = pd.DataFrame(data)
    
    # Clean generated data to ensure consistency
    df = clean_fleet_data(df)
    
    data_logger.info(f"Generated demo fleet with {len(df)} vehicles")
    
    return df

def load_sample_csv(file_path: str = 'data/sample_fleet.csv') -> Optional[pd.DataFrame]:
    """
    Load sample CSV if it exists
    
    Args:
        file_path: Path to sample CSV file
    
    Returns:
        Dataframe or None if file not found
    """
    try:
        if not os.path.exists(file_path):
            data_logger.info(f"Sample file not found at {file_path}, will use demo data")
            return None
        
        df = pd.read_csv(file_path)
        is_valid, _ = validate_csv_schema(df)
        
        if not is_valid:
            data_logger.warning(f"{file_path} has invalid schema, using demo data")
            return None
        
        df = clean_fleet_data(df)
        data_logger.info(f"Loaded sample CSV with {len(df)} vehicles")
        return df
    
    except Exception as e:
        data_logger.error(f"Error loading sample CSV: {str(e)}")
        return None
