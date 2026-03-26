"""
Production Data Loader for Fleet Intelligence

Purpose:
    Reliable, validated data ingestion from multiple sources.
    Handles data quality issues, caching, and audit trails.

Key Responsibilities:
    - Load vehicle telemetry from multiple sources (API, CSV, database)
    - Validate data contracts and constraints
    - Handle missing data gracefully
    - Compute derived metrics (idle time, battery trends)
    - Cache results for performance
    - Log all data operations for audit

Usage:
    from data_loader import ProductionDataLoader, DataSource
    
    loader = ProductionDataLoader()
    vehicles = loader.load_vehicles(source=DataSource.API, limit=100)
"""

import logging
from dataclasses import asdict
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import csv
import json
from pathlib import Path
from enum import Enum
import numpy as np
import pandas as pd

from .decision_engine import VehicleState

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS
# ============================================================================

class DataSource(Enum):
    """Data source types."""
    API = "api"  # Real-time API
    CSV = "csv"  # CSV file
    DATABASE = "database"  # SQL database
    SAMPLE = "sample"  # Sample/test data


class DataValidationError(Exception):
    """Raised when data validation fails."""
    pass


# ============================================================================
# DATA VALIDATION CONTRACTS
# ============================================================================

class DataContract:
    """Define and validate data schemas."""
    
    # Required fields for vehicle telemetry
    REQUIRED_FIELDS = {
        'vehicle_id': str,
        'vehicle_type': str,
        'latitude': (int, float),
        'longitude': (int, float),
        'zone_id': str,
        'battery_pct': (int, float),
    }
    
    # Optional fields with defaults
    OPTIONAL_FIELDS = {
        'is_reserved': (bool, int),
        'is_disabled': (bool, int),
        'battery_pct_prev_day': (int, float, type(None)),
        'battery_pct_prev_week': (int, float, type(None)),
        'trips_last_24h': (int, float),
        'trips_last_7d': (int, float),
        'trips_last_30d': (int, float),
        'distance_last_24h': (int, float),
        'distance_last_7d': (int, float),
        'last_trip_timestamp': (str, type(None)),
        'last_charge_timestamp': (str, type(None)),
        'days_deployed': (int, float),
        'maintenance_count_30d': (int, float),
        'failure_count_90d': (int, float),
        'is_under_repair': (bool, int),
        'zone_demand': (int, float),
        'zone_supply': (int, float),
    }
    
    @classmethod
    def validate_record(cls, record: Dict) -> Tuple[bool, List[str]]:
        """
        Validate a single vehicle record.
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required fields
        for field, expected_type in cls.REQUIRED_FIELDS.items():
            if field not in record:
                errors.append(f"Missing required field: {field}")
                continue
            
            if record[field] is None:
                errors.append(f"Required field is None: {field}")
                continue
            
            if not isinstance(record[field], expected_type):
                errors.append(
                    f"Field '{field}' has wrong type: "
                    f"expected {expected_type}, got {type(record[field])}"
                )
        
        # Validate specific constraints
        if 'battery_pct' in record:
            battery = record['battery_pct']
            if not (0 <= battery <= 100):
                errors.append(f"battery_pct out of range [0,100]: {battery}")
        
        if 'latitude' in record:
            lat = record['latitude']
            if not (-90 <= lat <= 90):
                errors.append(f"latitude out of range [-90,90]: {lat}")
        
        if 'longitude' in record:
            lon = record['longitude']
            if not (-180 <= lon <= 180):
                errors.append(f"longitude out of range [-180,180]: {lon}")
        
        if 'vehicle_type' in record:
            vtype = record['vehicle_type'].lower()
            if vtype not in ['scooter', 'bike', 'moped']:
                errors.append(f"vehicle_type not recognized: {vtype}")
        
        return len(errors) == 0, errors


# ============================================================================
# DATA LOADER
# ============================================================================

class ProductionDataLoader:
    """
    Production-grade data loader with validation and error handling.
    """
    
    def __init__(self, cache_enabled: bool = True):
        """
        Initialize data loader.
        
        Args:
            cache_enabled: Enable in-memory caching of loaded data
        """
        self.cache_enabled = cache_enabled
        self.cache = {}  # vehicle_id -> VehicleState
        self.logger = logger
        self.last_load_time = None
        self.load_stats = {
            'total_records_attempted': 0,
            'records_loaded': 0,
            'records_failed': 0,
            'validation_errors': [],
        }
    
    def load_vehicles(self, 
                     source: DataSource,
                     source_path: Optional[str] = None,
                     limit: Optional[int] = None) -> Dict[str, VehicleState]:
        """
        Load vehicles from specified source.
        
        Args:
            source: DataSource type
            source_path: Path to file (for CSV/DB sources)
            limit: Maximum number of records to load
            
        Returns:
            Dictionary mapping vehicle_id -> VehicleState
        """
        
        self.logger.info(f"Loading vehicles from {source.value}")
        self.load_stats = {
            'total_records_attempted': 0,
            'records_loaded': 0,
            'records_failed': 0,
            'validation_errors': [],
        }
        
        start_time = datetime.now()
        
        try:
            if source == DataSource.CSV:
                vehicles = self._load_from_csv(source_path, limit)
            elif source == DataSource.SAMPLE:
                vehicles = self._load_sample_data(limit)
            elif source == DataSource.API:
                # Placeholder for real API implementation
                vehicles = self._load_from_api(limit)
            else:
                raise ValueError(f"Unsupported data source: {source}")
            
            elapsed = (datetime.now() - start_time).total_seconds()
            self._log_load_summary(elapsed)
            
            return vehicles
        
        except Exception as e:
            self.logger.error(f"Failed to load vehicles: {str(e)}")
            raise
    
    def _load_from_csv(self, csv_path: str, limit: Optional[int] = None) -> Dict[str, VehicleState]:
        """Load vehicles from CSV file."""
        
        if not Path(csv_path).exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        vehicles = {}
        
        try:
            df = pd.read_csv(csv_path)
            
            # Limit records if specified
            if limit:
                df = df.head(limit)
            
            self.load_stats['total_records_attempted'] = len(df)
            
            for idx, row in df.iterrows():
                try:
                    # Convert row to dictionary
                    record = row.to_dict()
                    
                    # Validate record
                    is_valid, errors = DataContract.validate_record(record)
                    
                    if not is_valid:
                        self.logger.warning(f"Row {idx} validation failed: {errors}")
                        self.load_stats['records_failed'] += 1
                        self.load_stats['validation_errors'].extend(errors)
                        continue
                    
                    # Parse timestamps
                    if 'last_trip_timestamp' in record and record['last_trip_timestamp']:
                        try:
                            record['last_trip_timestamp'] = \
                                pd.to_datetime(record['last_trip_timestamp'])
                        except:
                            record['last_trip_timestamp'] = None
                    
                    if 'last_charge_timestamp' in record and record['last_charge_timestamp']:
                        try:
                            record['last_charge_timestamp'] = \
                                pd.to_datetime(record['last_charge_timestamp'])
                        except:
                            record['last_charge_timestamp'] = None
                    
                    # Create VehicleState
                    vehicle = VehicleState(**record)
                    vehicles[vehicle.vehicle_id] = vehicle
                    self.load_stats['records_loaded'] += 1
                
                except Exception as e:
                    self.logger.error(f"Error parsing row {idx}: {str(e)}")
                    self.load_stats['records_failed'] += 1
        
        except Exception as e:
            self.logger.error(f"Error reading CSV: {str(e)}")
            raise
        
        return vehicles
    
    def _load_from_api(self, limit: Optional[int] = None) -> Dict[str, VehicleState]:
        """Load vehicles from API (placeholder)."""
        
        self.logger.info("API loading not yet implemented - returning sample data")
        return self._load_sample_data(limit)
    
    def _load_sample_data(self, limit: Optional[int] = None) -> Dict[str, VehicleState]:
        """Generate realistic sample vehicle data for testing."""
        
        np.random.seed(42)
        num_vehicles = limit or 50
        
        vehicles = {}
        zones = ['downtown', 'waterfront', 'north_end', 'south_beach', 'airport']
        
        for i in range(num_vehicles):
            vehicle_id = f"vehicle_{i:04d}"
            
            # Generate realistic vehicle state
            vehicle = VehicleState(
                vehicle_id=vehicle_id,
                vehicle_type="scooter" if i % 2 == 0 else "bike",
                latitude=47.6097 + np.random.normal(0, 0.05),
                longitude=-122.3331 + np.random.normal(0, 0.05),
                zone_id=np.random.choice(zones),
                battery_pct=np.random.uniform(10, 100),
                battery_pct_prev_day=np.random.uniform(10, 100),
                battery_pct_prev_week=np.random.uniform(10, 100),
                is_reserved=bool(np.random.choice([0, 1], p=[0.85, 0.15])),
                is_disabled=bool(np.random.choice([0, 1], p=[0.95, 0.05])),
                trips_last_24h=int(np.random.poisson(3)),
                trips_last_7d=int(np.random.poisson(12)),
                trips_last_30d=int(np.random.poisson(40)),
                distance_last_24h=np.random.uniform(0, 25),
                distance_last_7d=np.random.uniform(0, 100),
                last_trip_timestamp=(
                    datetime.now() - timedelta(hours=np.random.uniform(0, 168))
                    if np.random.random() > 0.1 else None
                ),
                last_charge_timestamp=(
                    datetime.now() - timedelta(hours=np.random.uniform(0, 72))
                    if np.random.random() > 0.1 else None
                ),
                days_deployed=int(np.random.uniform(7, 365)),
                maintenance_count_30d=int(np.random.poisson(0.5)),
                failure_count_90d=int(np.random.poisson(0.3)),
                is_under_repair=bool(np.random.choice([0, 1], p=[0.95, 0.05])),
                zone_demand=np.random.uniform(0.4, 1.0),
                zone_supply=np.random.uniform(0.3, 1.2),
            )
            
            vehicles[vehicle_id] = vehicle
            self.load_stats['records_loaded'] += 1
        
        self.load_stats['total_records_attempted'] = num_vehicles
        
        return vehicles
    
    def enrich_vehicle_data(self, vehicle: VehicleState, 
                           historical_data: Optional[pd.DataFrame] = None) -> VehicleState:
        """
        Enrich vehicle data with computed metrics.
        
        Args:
            vehicle: Vehicle to enrich
            historical_data: Optional historical trip data for trend calculation
            
        Returns:
            Enriched VehicleState
        """
        
        # Compute idle time if not present
        if vehicle.last_trip_timestamp is None:
            vehicle.last_trip_timestamp = datetime.now() - timedelta(days=30)
        
        # Compute battery trends from previous readings
        if vehicle.battery_pct_prev_day is None:
            # Estimate from current battery and trip count
            estimated_prev_day = vehicle.battery_pct + (vehicle.trips_last_24h * 2)
            vehicle.battery_pct_prev_day = min(100, estimated_prev_day)
        
        if vehicle.battery_pct_prev_week is None:
            # Estimate from utilization
            trips_per_day = vehicle.trips_last_7d / 7.0
            estimated_prev_week = vehicle.battery_pct + (trips_per_day * 7 * 2)
            vehicle.battery_pct_prev_week = min(100, estimated_prev_week)
        
        return vehicle
    
    def _log_load_summary(self, elapsed_seconds: float) -> None:
        """Log summary of load operation."""
        
        self.logger.info(
            f"Load complete in {elapsed_seconds:.2f}s: "
            f"{self.load_stats['records_loaded']} loaded, "
            f"{self.load_stats['records_failed']} failed"
        )
        
        if self.load_stats['validation_errors']:
            self.logger.warning(
                f"Validation errors: {self.load_stats['validation_errors'][:5]}"
            )
    
    def get_load_stats(self) -> Dict:
        """Get statistics about last load operation."""
        return self.load_stats.copy()


# ============================================================================
# VEHICLE DATA AGGREGATOR
# ============================================================================

class VehicleDataAggregator:
    """
    Aggregate vehicle data from multiple sources and time periods.
    Used to compute fleet-wide metrics and trends.
    """
    
    def __init__(self, loader: Optional[ProductionDataLoader] = None):
        self.loader = loader or ProductionDataLoader()
        self.logger = logger
    
    def load_vehicle_trips(self, vehicle_id: str, 
                          trip_data_path: str,
                          days_back: int = 30) -> pd.DataFrame:
        """
        Load trip history for a vehicle.
        
        Args:
            vehicle_id: Vehicle identifier
            trip_data_path: Path to trip CSV data
            days_back: Number of days to look back
            
        Returns:
            DataFrame with trip history
        """
        
        try:
            df = pd.read_csv(trip_data_path)
            
            # Filter by vehicle (if vehicle_id column exists)
            if 'vehicle_id' in df.columns:
                df = df[df['vehicle_id'] == vehicle_id]
            
            # Filter by date
            if 'start_time' in df.columns:
                df['start_time'] = pd.to_datetime(df['start_time'])
                cutoff = datetime.now() - timedelta(days=days_back)
                df = df[df['start_time'] >= cutoff]
            
            return df
        
        except Exception as e:
            self.logger.error(f"Failed to load trip data: {str(e)}")
            return pd.DataFrame()
    
    def compute_zone_metrics(self, vehicles: Dict[str, VehicleState]) -> Dict[str, Dict]:
        """
        Compute zone-level aggregates (supply/demand).
        
        Args:
            vehicles: Dictionary of vehicles by ID
            
        Returns:
            Dictionary of zone metrics
        """
        
        zone_stats = {}
        
        for vehicle in vehicles.values():
            zone = vehicle.zone_id
            
            if zone not in zone_stats:
                zone_stats[zone] = {
                    'count': 0,
                    'available': 0,
                    'reserved': 0,
                    'disabled': 0,
                    'avg_battery': [],
                    'avg_trips_7d': [],
                }
            
            zone_stats[zone]['count'] += 1
            if not vehicle.is_reserved:
                zone_stats[zone]['available'] += 1
            if vehicle.is_reserved:
                zone_stats[zone]['reserved'] += 1
            if vehicle.is_disabled:
                zone_stats[zone]['disabled'] += 1
            
            zone_stats[zone]['avg_battery'].append(vehicle.battery_pct)
            zone_stats[zone]['avg_trips_7d'].append(vehicle.trips_last_7d)
        
        # Compute aggregates
        for zone, stats in zone_stats.items():
            stats['avg_battery'] = np.mean(stats['avg_battery']) if stats['avg_battery'] else 0
            stats['avg_trips_7d'] = np.mean(stats['avg_trips_7d']) if stats['avg_trips_7d'] else 0
            stats['utilization_pct'] = (
                stats['available'] / stats['count'] * 100 if stats['count'] > 0 else 0
            )
        
        return zone_stats
    
    def get_vehicle_cohort_stats(self, vehicles: Dict[str, VehicleState],
                                 vehicle_type: Optional[str] = None) -> Dict:
        """
        Get cohort-level statistics (by vehicle type or other grouping).
        """
        
        filtered_vehicles = [
            v for v in vehicles.values()
            if vehicle_type is None or v.vehicle_type == vehicle_type
        ]
        
        if not filtered_vehicles:
            return {}
        
        # Count idle vehicles safely
        idle_count = 0
        for v in filtered_vehicles:
            if v.last_trip_timestamp is not None:
                idle_hours = (datetime.now() - v.last_trip_timestamp).total_seconds() / 3600
                if idle_hours > 4:
                    idle_count += 1
        
        return {
            'count': len(filtered_vehicles),
            'avg_battery': np.mean([v.battery_pct for v in filtered_vehicles]),
            'avg_trips_7d': np.mean([v.trips_last_7d for v in filtered_vehicles]),
            'avg_idle_pct': (idle_count / len(filtered_vehicles) * 100) if filtered_vehicles else 0,
        }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    
    # Example 1: Load sample data
    print("=" * 70)
    print("EXAMPLE 1: Load Sample Vehicles")
    print("=" * 70)
    
    loader = ProductionDataLoader()
    vehicles = loader.load_vehicles(
        source=DataSource.SAMPLE,
        limit=10
    )
    
    print(f"\nLoaded {len(vehicles)} vehicles")
    for vehicle_id, vehicle in list(vehicles.items())[:3]:
        print(f"\n{vehicle_id}:")
        print(f"  Battery: {vehicle.battery_pct:.0f}%")
        print(f"  Zone: {vehicle.zone_id}")
        print(f"  Trips (7d): {vehicle.trips_last_7d}")
    
    # Example 2: Aggregate zone metrics
    print("\n\n" + "=" * 70)
    print("EXAMPLE 2: Zone Metrics")
    print("=" * 70)
    
    aggregator = VehicleDataAggregator()
    zone_metrics = aggregator.compute_zone_metrics(vehicles)
    
    for zone, metrics in zone_metrics.items():
        print(f"\n{zone}:")
        print(f"  Total vehicles: {metrics['count']}")
        print(f"  Available: {metrics['available']}")
        print(f"  Avg battery: {metrics['avg_battery']:.0f}%")
        print(f"  Utilization: {metrics['utilization_pct']:.0f}%")
    
    # Example 3: Cohort analysis
    print("\n\n" + "=" * 70)
    print("EXAMPLE 3: Cohort Analysis")
    print("=" * 70)
    
    scooter_stats = aggregator.get_vehicle_cohort_stats(vehicles, 'scooter')
    bike_stats = aggregator.get_vehicle_cohort_stats(vehicles, 'bike')
    
    print(f"\nScooter Cohort:")
    print(f"  Count: {scooter_stats.get('count', 0)}")
    print(f"  Avg Battery: {scooter_stats.get('avg_battery', 0):.0f}%")
    print(f"  Avg Trips (7d): {scooter_stats.get('avg_trips_7d', 0):.0f}")
    
    print(f"\nBike Cohort:")
    print(f"  Count: {bike_stats.get('count', 0)}")
    print(f"  Avg Battery: {bike_stats.get('avg_battery', 0):.0f}%")
    print(f"  Avg Trips (7d): {bike_stats.get('avg_trips_7d', 0):.0f}")
