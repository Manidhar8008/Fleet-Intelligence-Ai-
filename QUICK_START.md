# ⚡ Quick Start Guide

Get the Fleet Intelligence Decision System running in 5 minutes.

---

## Installation (2 minutes)

### 1. Clone and Setup

```bash
cd d:\MY\ projects\lime-iot-ml-platform-

# Create virtual environment
python -m venv env
.\env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Verify Installation

```bash
python src/decision_engine.py
python src/data_loader.py
```

You should see sample output and no errors.

---

## Example 1: Score a Single Vehicle (30 seconds)

```python
from src.decision_engine import FleetDecisionEngine, VehicleState
from datetime import datetime, timedelta

# Initialize engine
engine = FleetDecisionEngine()

# Create a vehicle
vehicle = VehicleState(
    vehicle_id="scooter_001",
    vehicle_type="scooter",
    latitude=47.6097,
    longitude=-122.3331,
    zone_id="downtown",
    battery_pct=35,
    battery_pct_prev_day=42,
    battery_pct_prev_week=65,
    trips_last_24h=4,
    trips_last_7d=18,
    trips_last_30d=75,
    last_trip_timestamp=datetime.now() - timedelta(hours=3),
    days_deployed=60,
    failure_count_90d=1,
    zone_demand=0.8,
    zone_supply=0.9,
)

# Get decision
decision = engine.score_vehicle(vehicle)

# Print results
print(f"Vehicle: {decision.vehicle_id}")
print(f"Risk Level: {decision.risk_level.value}")
print(f"Risk Score: {decision.risk_score:.0f}/100")
print(f"Recommendation: {decision.recommended_action.value}")
print(f"Reasoning: {decision.reasoning}")

# Output:
# Vehicle: scooter_001
# Risk Level: MEDIUM
# Risk Score: 52/100
# Recommendation: MONITOR
# Reasoning: MEDIUM RISK: Battery is 35% (low); High utilization (18 trips/week); Zone overstocked (112% supply/demand ratio)
```

---

## Example 2: Load & Score a Fleet (1 minute)

```python
from src.decision_engine import FleetDecisionBatch
from src.data_loader import ProductionDataLoader, DataSource

# Load 50 sample vehicles
loader = ProductionDataLoader()
vehicles = loader.load_vehicles(
    source=DataSource.SAMPLE,
    limit=50
)
print(f"Loaded {len(vehicles)} vehicles")

# Score all vehicles
batch_scorer = FleetDecisionBatch()
decisions = batch_scorer.score_fleet(list(vehicles.values()))

# Get fleet summary
summary = batch_scorer.get_summary_metrics(decisions)

print(f"\nFleet Summary:")
print(f"  Total: {summary['total_vehicles']}")
print(f"  Critical: {summary['risk_distribution']['CRITICAL']}")
print(f"  High: {summary['risk_distribution']['HIGH']}")
print(f"  Medium: {summary['risk_distribution']['MEDIUM']}")
print(f"  Low: {summary['risk_distribution']['LOW']}")
print(f"  Avg Risk: {summary['avg_risk_score']:.1f}/100")

# Get critical vehicles for ops team
critical = [d for d in decisions.values() if d.risk_level.value == 'CRITICAL']
print(f"\n🚨 Critical Vehicles: {len(critical)}")
for decision in critical[:5]:
    print(f"  - {decision.vehicle_id}: {decision.reasoning}")
```

---

## Example 3: Run the Dashboard (1 minute)

```bash
# Start dashboard
cd d:\MY\ projects\lime-iot-ml-platform-
streamlit run dashboard.py

# Opens at http://localhost:8501
```

**Dashboard Features:**
- 📊 Fleet health metrics
- 🎯 Risk distribution pie chart
- 🚨 Critical alerts with explanations
- 📋 Vehicle details table with filters
- 📍 Zone analysis and heatmaps
- 📈 Fleet statistics

---

## Understanding Risk Scores

The system uses a **0-100 scale**:

```
0-40    = LOW RISK    ✅ Continue monitoring
├─ No immediate action needed
└─ Normal operations

40-70   = MEDIUM RISK  ⚠️ Plan intervention
├─ Elevated signals detected
└─ Schedule inspection/maintenance

70-85   = HIGH RISK    🔴 Urgent action
├─ Multiple risk factors align
└─ Prioritize for maintenance

85-100  = CRITICAL     🚨 Immediate action
├─ Critical battery, multiple failures
└─ Remove from service or repair immediately
```

---

## Key Concepts

### VehicleState (Input)

```python
VehicleState(
    vehicle_id="scooter_001",          # Unique ID
    vehicle_type="scooter",             # 'scooter' or 'bike'
    latitude=47.6097,                   # GPS location
    longitude=-122.3331,
    zone_id="downtown",                 # Operational zone
    battery_pct=45,                     # Current battery %
    battery_pct_prev_day=50,            # Yesterday's battery
    battery_pct_prev_week=75,           # 7 days ago
    trips_last_24h=3,                   # Trip activity
    trips_last_7d=15,
    trips_last_30d=65,
    last_trip_timestamp=datetime(...),  # When used last
    days_deployed=120,                  # How long in fleet
    failure_count_90d=0,                # Reliability history
    maintenance_count_30d=1,
    zone_demand=0.8,                    # Zone context
    zone_supply=0.9,
)
```

### Decision (Output)

```python
Decision(
    vehicle_id="scooter_001",
    risk_level=RiskLevel.MEDIUM,           # LOW/MEDIUM/HIGH/CRITICAL
    risk_score=52.3,                        # 0-100
    confidence="HIGH",                      # Data sufficiency
    recommended_action=RecommendationType.MONITOR,  # What to do
    reasoning="MEDIUM RISK: ...",          # Why
    primary_drivers=[                       # Top 3 factors
        "ZONE (60.5)",
        "UTILIZATION (45.2)",
        "BATTERY (32.1)"
    ],
    alerts=[                                # Critical conditions
        {
            'alert_type': 'BATTERY_CRITICAL',
            'severity': 'WARNING',
            'message': 'Battery below 50%',
            'action': 'Plan charging in next 2 hours'
        }
    ],
    decision_id="DEC_20240115143022_7834", # Audit trail
    timestamp=datetime.now(),
    model_version="1.0.0"
)
```

### Risk Components (40% Battery + 35% Utilization + 15% Zone + 10% Maintenance)

```
Battery Health (40%)
├─ Current battery level (critical if <15%)
├─ Battery trend (improving/stable/declining)
└─ Decline rate (% per day)

Utilization Stress (35%)
├─ Trip frequency (mechanical wear)
├─ Distance traveled
└─ Idle time (not generating revenue)

Zone Pressure (15%)
├─ Supply/demand ratio
└─ Overstock penalty

Maintenance History (10%)
├─ Recent maintenance (30d)
├─ Recent failures (90d)
└─ Currently under repair
```

---

## Common Tasks

### Task 1: Get Critical Alerts for Ops Team

```python
from src.decision_engine import RiskLevel

critical_decisions = [d for d in decisions.values() if d.risk_level == RiskLevel.CRITICAL]

for decision in critical_decisions:
    print(f"\n🚨 {decision.vehicle_id}")
    print(f"   Action: {decision.recommended_action.value}")
    print(f"   Reason: {decision.reasoning}")
    
    for alert in decision.alerts:
        print(f"   [{alert['severity']}] {alert['message']}")
        print(f"   → {alert['action']}")
```

### Task 2: Export Decisions to JSON

```python
import json

# Convert to JSON-serializable format
results = {
    vid: decision.to_dict()
    for vid, decision in decisions.items()
}

# Save to file
with open('fleet_decisions.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

# Load for reporting
with open('fleet_decisions.json', 'r') as f:
    decisions_json = json.load(f)
```

### Task 3: Filter by Action Type

```python
from src.decision_engine import RecommendationType

# Find vehicles needing inspection
inspection_required = [
    d for d in decisions.values()
    if d.recommended_action == RecommendationType.INSPECT
]

print(f"Vehicles requiring inspection: {len(inspection_required)}")
for decision in inspection_required:
    print(f"  - {decision.vehicle_id}: {decision.primary_drivers[0]}")
```

### Task 4: Analyze by Zone

```python
from src.data_loader import VehicleDataAggregator

aggregator = VehicleDataAggregator()
zone_stats = aggregator.compute_zone_metrics(vehicles)

for zone, metrics in zone_stats.items():
    print(f"\nZone: {zone}")
    print(f"  Vehicles: {metrics['count']}")
    print(f"  Available: {metrics['available']}")
    print(f"  Avg Battery: {metrics['avg_battery']:.0f}%")
    print(f"  Utilization: {metrics['utilization_pct']:.0f}%")
```

---

## Production Deployment (See PRODUCTION_DEPLOYMENT_GUIDE.md)

### Local Testing
```bash
streamlit run dashboard.py
```

### Docker Deployment
```bash
docker build -t fleet-intelligence:latest .
docker run -p 8080:8080 fleet-intelligence:latest
```

### Integration with Your API
```python
from src.data_loader import ProductionDataLoader, DataSource

# Implement _load_from_api() to connect to your telemetry
loader = ProductionDataLoader()
vehicles = loader.load_vehicles(source=DataSource.API, limit=1000)
```

---

## Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'streamlit'"

```bash
pip install -r requirements.txt
```

### Problem: "TypeError: non-default argument follows default argument"

This is fixed in the current version. Make sure you have the latest code:

```bash
git pull
```

### Problem: Low confidence on new vehicles

New vehicles need ~7 days for MEDIUM confidence, ~14 days for HIGH confidence. This is by design to prevent false alerts.

---

## Next Steps

1. ✅ **Understand**: Read `SYSTEM_ARCHITECTURE.md` for design philosophy
2. ✅ **Integrate**: Connect your telemetry API via `data_loader.py`
3. ✅ **Configure**: Tune risk thresholds in `decision_engine.py`
4. ✅ **Deploy**: Follow `PRODUCTION_DEPLOYMENT_GUIDE.md`
5. ✅ **Monitor**: Set up logging and alerting

---

## Files You'll Use

| File | Purpose |
|------|---------|
| `src/decision_engine.py` | Core scoring + recommendations |
| `src/data_loader.py` | Data ingestion + validation |
| `dashboard.py` | Streamlit UI |
| `PRODUCTION_DEPLOYMENT_GUIDE.md` | Deployment instructions |
| `SYSTEM_ARCHITECTURE.md` | Design & philosophy |
| `API_REFERENCE.md` | Complete API documentation |

---

## Support

- 📖 See `API_REFERENCE.md` for complete API docs
- 🏗️ See `SYSTEM_ARCHITECTURE.md` for design decisions
- 🚀 See `PRODUCTION_DEPLOYMENT_GUIDE.md` for deployment
- 💬 Inline comments in code explain the logic

---

**You're ready!** Start with Example 1, then try the dashboard. Questions? Check the docs.
