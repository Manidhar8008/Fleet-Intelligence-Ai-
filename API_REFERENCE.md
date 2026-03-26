# 📚 API Reference

Complete documentation for the Fleet Intelligence Decision Engine API.

---

## Table of Contents

1. [Core Classes](#core-classes)
2. [Data Models](#data-models)
3. [Decision Engine](#decision-engine)
4. [Data Loader](#data-loader)
5. [Error Handling](#error-handling)
6. [Examples](#examples)

---

## Core Classes

### RiskLevel (Enum)

Risk categorization for operational decision-making.

```python
class RiskLevel(Enum):
    LOW = "LOW"           # No immediate action needed
    MEDIUM = "MEDIUM"     # Monitor and plan intervention
    HIGH = "HIGH"         # Urgent intervention required
    CRITICAL = "CRITICAL" # Immediate action required
```

### AlertType (Enum)

Categories of operational alerts.

```python
class AlertType(Enum):
    BATTERY_CRITICAL = "BATTERY_CRITICAL"      # Battery < 15%
    IDLE_TIMEOUT = "IDLE_TIMEOUT"              # Vehicle idle > 24h
    MULTIPLE_FAILURES = "MULTIPLE_FAILURES"    # 3+ failures in 90d
    ZONE_OVERSTOCK = "ZONE_OVERSTOCK"          # Zone supply excess
    MAINTENANCE_DUE = "MAINTENANCE_DUE"        # Recent maintenance
```

### RecommendationType (Enum)

Operational actions recommended by the engine.

```python
class RecommendationType(Enum):
    INSPECT = "INSPECT"           # Preventive inspection
    ROTATE = "ROTATE"             # Rotate to different zone
    REBALANCE = "REBALANCE"       # Move to high-demand area
    REPAIR = "REPAIR"             # Corrective maintenance
    DECOMMISSION = "DECOMMISSION" # Remove from fleet
    MONITOR = "MONITOR"           # Continue monitoring
```

---

## Data Models

### VehicleState

Input data structure representing a vehicle's current state.

```python
@dataclass
class VehicleState:
    # Identification
    vehicle_id: str                          # Unique vehicle ID
    vehicle_type: str                        # 'scooter' or 'bike'
    
    # Location
    latitude: float                          # GPS latitude (-90 to 90)
    longitude: float                         # GPS longitude (-180 to 180)
    zone_id: str                             # Operational zone ID
    
    # Status
    is_reserved: bool = False                # Reserved by user
    is_disabled: bool = False                # Out of service
    
    # Battery
    battery_pct: float                       # Current battery 0-100
    battery_pct_prev_day: Optional[float]    # Yesterday's battery
    battery_pct_prev_week: Optional[float]   # Last week's battery
    
    # Activity
    trips_last_24h: int = 0                  # Trips in 24 hours
    trips_last_7d: int = 0                   # Trips in 7 days
    trips_last_30d: int = 0                  # Trips in 30 days
    distance_last_24h: float = 0.0           # Distance (kilometers)
    distance_last_7d: float = 0.0
    
    # Timing
    last_trip_timestamp: Optional[datetime]  # Last trip start time
    last_charge_timestamp: Optional[datetime] # Last charge time
    days_deployed: int = 0                   # Days in fleet
    
    # Maintenance
    maintenance_count_30d: int = 0           # Maintenance events (30d)
    failure_count_90d: int = 0               # Failures (90d)
    is_under_repair: bool = False            # Currently being repaired
    
    # Zone Context
    zone_demand: float = 0.5                 # Demand level 0-1
    zone_supply: float = 0.5                 # Supply level 0-1
    
    # Metadata
    timestamp: datetime = None               # Data collection time
```

**Example:**

```python
vehicle = VehicleState(
    vehicle_id="scooter_001",
    vehicle_type="scooter",
    latitude=47.6097,
    longitude=-122.3331,
    zone_id="downtown",
    battery_pct=45,
    battery_pct_prev_day=52,
    battery_pct_prev_week=78,
    trips_last_24h=3,
    trips_last_7d=15,
    trips_last_30d=65,
    last_trip_timestamp=datetime.now() - timedelta(hours=2),
    days_deployed=120,
    zone_demand=0.9,
    zone_supply=0.8,
)
```

### RiskSignals

Intermediate signals extracted from vehicle state (internal use).

```python
@dataclass
class RiskSignals:
    battery_decline_rate: float      # % decline per day
    battery_trend: str               # 'improving', 'stable', 'declining'
    utilization_intensity: float     # 0-1 scale
    utilization_trend: str           # 'increasing', 'stable', 'decreasing'
    idle_hours: float                # Hours since last trip
    zone_pressure: float             # 0-1, higher = overstocked
    maintenance_pressure: float      # 0-1 based on history
    data_freshness_days: float       # Days of data available
```

### Decision

Output structure with risk score, confidence, and recommendations.

```python
@dataclass
class Decision:
    vehicle_id: str                      # Which vehicle
    risk_level: RiskLevel                # LOW/MEDIUM/HIGH/CRITICAL
    risk_score: float                    # 0-100 score
    confidence: str                      # HIGH/MEDIUM/LOW
    
    # Analysis
    primary_drivers: List[str]           # Top 3 risk factors
    signals: RiskSignals = None          # Underlying signals
    
    # Recommendation
    recommended_action: RecommendationType  # What to do
    reasoning: str                       # Human-readable explanation
    
    # Alerts
    alerts: List[Dict] = None            # Examples:
                                         # {
                                         #   'alert_type': 'BATTERY_CRITICAL',
                                         #   'severity': 'CRITICAL',
                                         #   'message': 'Battery critically low: 12%',
                                         #   'action': 'Route to charge station'
                                         # }
    
    # Audit Trail
    decision_id: str = None              # Unique decision ID
    timestamp: datetime = None           # Decision timestamp
    model_version: str = "1.0.0"         # Model version
    
    def to_dict(self) -> Dict:           # Convert to JSON
        pass
```

**Example:**

```python
{
    "vehicle_id": "scooter_001",
    "risk_level": "MEDIUM",
    "risk_score": 52.3,
    "confidence": "HIGH",
    "primary_drivers": [
        "UTILIZATION (45.2)",
        "BATTERY (32.1)",
        "ZONE (18.5)"
    ],
    "recommended_action": "MONITOR",
    "reasoning": "MEDIUM RISK: Battery is 45% (low); High utilization (15 trips/week)",
    "alerts": [
        {
            "alert_type": "BATTERY_CRITICAL",
            "severity": "WARNING",
            "message": "Battery below 50%",
            "action": "Plan charging in next 2 hours"
        }
    ],
    "decision_id": "DEC_20240115143022_7834",
    "timestamp": "2024-01-15T14:30:22.123456",
    "model_version": "1.0.0"
}
```

---

## Decision Engine

### FleetDecisionEngine

Main scoring engine for risk assessment and recommendations.

#### Constructor

```python
engine = FleetDecisionEngine(config: Optional[Dict] = None)
```

**Parameters:**
- `config` (dict, optional): Custom configuration with keys:
  - `risk_thresholds`: Override default thresholds
  - `signal_weights`: Override default signal weights

**Example:**

```python
custom_config = {
    'risk_thresholds': {
        'battery_critical_pct': 10,  # More aggressive
        'idle_alert_hours': 12,
    },
    'signal_weights': {
        'battery_health': 0.50,  # Prioritize battery
        'utilization_stress': 0.30,
    }
}

engine = FleetDecisionEngine(config=custom_config)
```

#### score_vehicle()

Score a single vehicle and generate decision.

```python
decision = engine.score_vehicle(vehicle: VehicleState) -> Decision
```

**Parameters:**
- `vehicle` (VehicleState): Current vehicle state

**Returns:**
- Decision object with risk score and recommendations

**Example:**

```python
vehicle = VehicleState(vehicle_id="scooter_001", ...)
decision = engine.score_vehicle(vehicle)

print(f"Risk: {decision.risk_level.value}")
print(f"Score: {decision.risk_score:.0f}/100")
print(f"Action: {decision.recommended_action.value}")
```

**Raises:**
- `ValueError`: If vehicle data fails validation

### FleetDecisionBatch

Batch scorer for fleet-wide analysis.

#### Constructor

```python
batch = FleetDecisionBatch(engine: Optional[FleetDecisionEngine] = None)
```

#### score_fleet()

Score all vehicles in a fleet.

```python
decisions = batch.score_fleet(vehicles: List[VehicleState]) -> Dict[str, Decision]
```

**Parameters:**
- `vehicles`: List of VehicleState objects

**Returns:**
- Dictionary mapping vehicle_id → Decision

**Example:**

```python
vehicles = [vehicle1, vehicle2, vehicle3, ...]
decisions = batch.score_fleet(vehicles)

for vehicle_id, decision in decisions.items():
    print(f"{vehicle_id}: {decision.risk_level.value}")
```

#### get_summary_metrics()

Get fleet-wide statistics.

```python
summary = batch.get_summary_metrics(decisions: Dict[str, Decision]) -> Dict
```

**Returns:**
```python
{
    'total_vehicles': 150,
    'risk_distribution': {
        'LOW': 95,
        'MEDIUM': 40,
        'HIGH': 12,
        'CRITICAL': 3
    },
    'alert_breakdown': {
        'BATTERY_CRITICAL': 3,
        'IDLE_TIMEOUT': 8,
        'MAINTENANCE_DUE': 2
    },
    'recommended_actions': {
        'MONITOR': 95,
        'INSPECT': 12,
        'REPAIR': 3,
        'ROTATE': 40
    },
    'avg_risk_score': 38.5
}
```

---

## Data Loader

### ProductionDataLoader

Reliable data ingestion with validation.

#### Constructor

```python
loader = ProductionDataLoader(cache_enabled: bool = True)
```

#### load_vehicles()

Load vehicle data from a source.

```python
vehicles = loader.load_vehicles(
    source: DataSource,
    source_path: Optional[str] = None,
    limit: Optional[int] = None
) -> Dict[str, VehicleState]
```

**Parameters:**
- `source`: DataSource enum (API, CSV, SAMPLE, DATABASE)
- `source_path`: Path to file (required for CSV)
- `limit`: Maximum vehicles to load

**Example:**

```python
# Load from sample data
vehicles = loader.load_vehicles(
    source=DataSource.SAMPLE,
    limit=100
)

# Load from CSV
vehicles = loader.load_vehicles(
    source=DataSource.CSV,
    source_path="data/vehicles.csv",
    limit=500
)
```

#### get_load_stats()

Get statistics about last load operation.

```python
stats = loader.get_load_stats() -> Dict
```

**Returns:**
```python
{
    'total_records_attempted': 500,
    'records_loaded': 485,
    'records_failed': 15,
    'validation_errors': [
        "Row 3: Invalid latitude",
        "Row 7: Missing required field: vehicle_id"
    ]
}
```

### DataContract

Validate data schemas and constraints.

```python
is_valid, errors = DataContract.validate_record(record: Dict) -> Tuple[bool, List[str]]
```

**Example:**

```python
record = {
    'vehicle_id': 'scooter_001',
    'vehicle_type': 'scooter',
    'latitude': 47.6097,
    'longitude': -122.3331,
    'zone_id': 'downtown',
    'battery_pct': 45,
}

is_valid, errors = DataContract.validate_record(record)

if not is_valid:
    for error in errors:
        print(f"Error: {error}")
```

### VehicleDataAggregator

Compute fleet-wide metrics and trends.

#### Constructor

```python
aggregator = VehicleDataAggregator(loader: Optional[ProductionDataLoader] = None)
```

#### compute_zone_metrics()

Aggregate metrics by zone.

```python
zone_metrics = aggregator.compute_zone_metrics(
    vehicles: Dict[str, VehicleState]
) -> Dict[str, Dict]
```

**Returns:**
```python
{
    'downtown': {
        'count': 45,                    # Vehicles in zone
        'available': 38,                # Not reserved
        'reserved': 5,
        'disabled': 2,
        'avg_battery': 62.3,            # % battery
        'avg_trips_7d': 12.5,           # Avg trips
        'utilization_pct': 84.4,        # % available
    },
    'waterfront': {
        'count': 32,
        'available': 28,
        'avg_battery': 71.2,
        'utilization_pct': 87.5,
    }
}
```

#### get_vehicle_cohort_stats()

Statistics for vehicle subset (e.g., by type).

```python
stats = aggregator.get_vehicle_cohort_stats(
    vehicles: Dict[str, VehicleState],
    vehicle_type: Optional[str] = None
) -> Dict
```

**Example:**

```python
scooter_stats = aggregator.get_vehicle_cohort_stats(vehicles, 'scooter')

print(f"Scooter Cohort:")
print(f"  Count: {scooter_stats['count']}")
print(f"  Avg Battery: {scooter_stats['avg_battery']:.0f}%")
print(f"  Avg Trips: {scooter_stats['avg_trips_7d']:.1f}")
print(f"  Idle %: {scooter_stats['avg_idle_pct']:.0f}%")
```

---

## Error Handling

### DataValidationError

Raised when vehicle data doesn't meet contract requirements.

```python
raise DataValidationError("Invalid battery_pct: -5")
```

### ValueError

Raised by decision engine when input validation fails.

```python
try:
    decision = engine.score_vehicle(vehicle)
except ValueError as e:
    print(f"Invalid vehicle data: {e}")
```

---

## Examples

### Complete Workflow

```python
from src.decision_engine import FleetDecisionEngine, FleetDecisionBatch, RiskLevel
from src.data_loader import ProductionDataLoader, DataSource, VehicleDataAggregator

# 1. Load Data
loader = ProductionDataLoader()
vehicles = loader.load_vehicles(
    source=DataSource.CSV,
    source_path="data/vehicles.csv",
    limit=1000
)
print(f"Loaded {len(vehicles)} vehicles")

# 2. Score Fleet
engine = FleetDecisionEngine()
batch = FleetDecisionBatch(engine)
decisions = batch.score_fleet(list(vehicles.values()))

# 3. Analyze Results
summary = batch.get_summary_metrics(decisions)
print(f"\nFleet Summary:")
print(f"  Total: {summary['total_vehicles']}")
print(f"  Critical: {summary['risk_distribution']['CRITICAL']}")
print(f"  Avg Risk: {summary['avg_risk_score']:.1f}")

# 4. Extract Critical Alerts
critical = [d for d in decisions.values() if d.risk_level == RiskLevel.CRITICAL]
print(f"\nCritical Alerts ({len(critical)}):")
for decision in critical[:5]:
    print(f"  {decision.vehicle_id}: {decision.primary_drivers[0]}")

# 5. Aggregate by Zone
aggregator = VehicleDataAggregator()
zone_stats = aggregator.compute_zone_metrics(vehicles)
print(f"\nZone Analysis:")
for zone, metrics in zone_stats.items():
    print(f"  {zone}: {metrics['count']} vehicles, {metrics['utilization_pct']:.0f}% util")

# 6. Export Results
import json
results = {
    'summary': summary,
    'decisions': {vid: d.to_dict() for vid, d in decisions.items()},
    'zones': zone_stats,
}
with open('fleet_analysis.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)
```

### Alerting Integration

```python
def send_to_slack(messages: List[str], channel: str):
    """Example: Send alerts to Slack."""
    import requests
    webhook_url = "https://hooks.slack.com/services/..."
    for msg in messages:
        requests.post(webhook_url, json={"text": msg, "channel": channel})

# Extract critical alerts
critical_messages = []
for decision in decisions.values():
    if decision.risk_level == RiskLevel.CRITICAL:
        for alert in decision.alerts:
            critical_messages.append(
                f"🚨 {decision.vehicle_id}: {alert['message']}"
            )

# Send to ops team
send_to_slack(critical_messages, "#fleet-ops-alerts")
```

### Custom Risk Configuration

```python
# Aggressive mode (prevent all failures)
aggressive_config = {
    'risk_thresholds': {
        'battery_critical_pct': 25,
        'battery_low_pct': 50,
        'idle_alert_hours': 12,
    },
    'signal_weights': {
        'battery_health': 0.50,
        'maintenance_history': 0.20,
    }
}

engine = FleetDecisionEngine(config=aggressive_config)
decisions = batch.score_fleet(vehicles)
```

---

## Performance Characteristics

- **Single vehicle scoring**: <50ms
- **Fleet of 1000**: <15 seconds
- **Throughput**: 60-100 vehicles/second
- **Memory**: ~10MB per 1000 vehicles
- **Dependencies**: pandas, numpy, scikit-learn (no GPU required)

---

## Versioning

Current API version: **1.0.0**

Changes are tracked in `decision_engine.py` model_version field.
