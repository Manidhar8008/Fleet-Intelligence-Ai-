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

def generate_demo_data() -> pd.DataFrame:
    """
    Generate synthetic demo fleet data
    
    Returns:
        Demo dataframe with realistic fleet data
    """
    np.random.seed(42)
    
    data = {
        'vehicle_id': [f'V{i:05d}' for i in range(1, config.DEFAULT_DEMO_VEHICLES + 1)],
        'battery': np.random.uniform(10, 100, config.DEFAULT_DEMO_VEHICLES),
        'utilization': np.random.uniform(0, 100, config.DEFAULT_DEMO_VEHICLES),
        'zone': np.random.choice(config.ZONES, config.DEFAULT_DEMO_VEHICLES),
        'trips_last_7d': np.random.randint(0, 50, config.DEFAULT_DEMO_VEHICLES),
        'maintenance_due': np.random.choice([True, False], config.DEFAULT_DEMO_VEHICLES, p=[0.1, 0.9]),
    }
    
    df = pd.DataFrame(data)
    
    # Clean generated data to ensure consistency
    df = clean_fleet_data(df)
    
    data_logger.info(f"Generated demo fleet with {len(df)} vehicles")
    
    return df

def load_sample_csv() -> Optional[pd.DataFrame]:
    """
    Load sample_vehicles.csv if it exists
    
    Returns:
        Dataframe or None if file not found
    """
    try:
        df = pd.read_csv('sample_vehicles.csv')
        is_valid, _ = validate_csv_schema(df)
        
        if not is_valid:
            data_logger.warning("sample_vehicles.csv has invalid schema, using demo data")
            return None
        
        df = clean_fleet_data(df)
        data_logger.info(f"Loaded sample CSV with {len(df)} vehicles")
        return df
    
    except FileNotFoundError:
        data_logger.info("sample_vehicles.csv not found, will use demo data")
        return None
    except Exception as e:
        data_logger.error(f"Error loading sample CSV: {str(e)}")
        return None
