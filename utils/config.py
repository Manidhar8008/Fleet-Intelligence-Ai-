"""
Configuration module for Fleet Intelligence AI
"""

from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class AppConfig:
    """Application configuration"""
    APP_NAME = "Fleet Intelligence AI"
    APP_SUBTITLE = "Real-Time Fleet Risk & Optimization Platform"
    APP_ICON = "🚗"
    
    # UI Configuration
    LAYOUT = "wide"
    THEME = "dark"
    
    # Data Configuration
    DEFAULT_DEMO_VEHICLES = 50
    MAX_UPLOAD_ROWS = 10000
    
    # Risk Configuration
    BATTERY_CRITICAL_THRESHOLD = 20
    BATTERY_LOW_THRESHOLD = 50
    UTILIZATION_IDLE_THRESHOLD = 20
    
    # Risk Weights (must sum to 1.0)
    RISK_WEIGHTS = {
        "battery_health": 0.40,
        "utilization": 0.35,
        "zone_pressure": 0.15,
        "maintenance": 0.10
    }
    
    # Risk Thresholds
    RISK_THRESHOLDS = {
        "LOW": (0, 25),
        "MEDIUM": (25, 50),
        "HIGH": (50, 75),
        "CRITICAL": (75, 100)
    }
    
    # Zone Configuration
    ZONES = ["downtown", "airport", "harbor", "commercial"]
    
    # Color Scheme (SaaS theme)
    COLORS = {
        "primary": "#0D4A8F",
        "secondary": "#1A5FA0",
        "success": "#4CAF50",
        "warning": "#FF9800",
        "danger": "#D32F2F",
        "info": "#2196F3"
    }
    
    # CSV Schema
    EXPECTED_CSV_COLUMNS = [
        "vehicle_id",
        "battery",
        "utilization",
        "zone",
        "trips_last_7d",
        "maintenance_due",
        "last_trip_hours_ago"
    ]

# Create config instance
config = AppConfig()
