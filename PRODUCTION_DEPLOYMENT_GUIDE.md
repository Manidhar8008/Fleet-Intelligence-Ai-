# 🚀 Production Deployment Guide

## Executive Summary

This guide covers deploying the **Fleet Intelligence AI Decision System** as a production-grade service. The system provides real-time vehicle risk scoring and operational recommendations for a micromobility fleet.

### Key Features
- ✅ Real-time risk scoring (0-100 scale)
- ✅ Explainable recommendations (6 action types)
- ✅ Automated alert escalation (5 alert categories)
- ✅ Fleet-wide health metrics
- ✅ Audit trail and compliance logging
- ✅ Sub-second decision latency

---

## System Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Production Dashboard                      │
│              (Streamlit - Fleet Health Visualization)        │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│         Decision Engine API                                  │
│  (Flask/FastAPI wrapper around decision_engine.py)          │
│                                                              │
│  Endpoints:                                                 │
│  - POST /score_vehicle      → Single vehicle decision       │
│  - POST /score_fleet        → Batch scoring                 │
│  - GET  /fleet_metrics      → Fleet-wide summary            │
│  - GET  /vehicle/{id}       → Individual vehicle details    │
│  - GET  /alerts             → Active alerts                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│         Decision Engine Core                                 │
│  (decision_engine.py - Risk Scoring & Logic)                │
│                                                              │
│  - RiskSignals: Extract vehicle telemetry                   │
│  - RiskScore: Weighted composite model (0-100)              │
│  - Decisions: Generated recommendations                      │
│  - Alerts: Escalation logic                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│         Data Layer                                           │
│  (data_loader.py - Validated Data Ingestion)                │
│                                                              │
│  - CSV loader (historical data)                             │
│  - API connector (real-time telemetry)                      │
│  - Data validation (contracts & constraints)                │
│  - Enrichment & transformation                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│         Data Sources                                         │
│  - Telemetry API (vehicle location, battery, trips)         │
│  - CSV/Database (historical trips and maintenance)          │
│  - Real-time feeds (GPS, sensor data)                       │
└──────────────────────────────────────────────────────────────┘
```

---

## Installation

### Prerequisites
- Python 3.8+
- pip or conda
- Access to fleet telemetry data (API endpoint or CSV)

### Step 1: Clone & Setup Environment

```bash
# Navigate to project
cd d:\MY\ projects\lime-iot-ml-platform-

# Create virtual environment
python -m venv env
source env/Scripts/activate  # On Windows: .\env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Verify Installation

```bash
# Test imports
python -c "from src.decision_engine import FleetDecisionEngine; print('✅ Decision Engine loaded')"
python -c "from src.data_loader import ProductionDataLoader; print('✅ Data Loader loaded')"
```

---

## Configuration

### Decision Engine Tuning

The system uses configurable thresholds and weights. Modify `src/decision_engine.py`:

```python
# RISK THRESHOLDS (customize for your fleet)
RISK_THRESHOLDS = {
    "battery_critical_pct": 15,      # Alert if < 15%
    "battery_low_pct": 30,           # Warning if < 30%
    "idle_alert_hours": 24,          # Alert if idle > 24h
    "idle_warning_hours": 4,         # Watch if idle > 4h
    "zone_overstock_percentile": 75, # Flag if supply > 75th percentile
}

# SIGNAL WEIGHTS (by business impact)
SIGNAL_WEIGHTS = {
    "battery_health": 0.40,          # 40% of score
    "utilization_stress": 0.35,      # 35% of score
    "zone_pressure": 0.15,           # 15% of score
    "maintenance_history": 0.10,     # 10% of score
}

# CONFIDENCE THRESHOLDS (data sufficiency)
CONFIDENCE_THRESHOLDS = {
    "high": 14,      # 14 days = HIGH confidence
    "medium": 7,     # 7 days = MEDIUM confidence
}
```

### Risk Level Policy

```python
RISK_LEVEL_MAPPING = {
    "CRITICAL": risk_score >= 85 OR battery < 10% OR failures >= 3,
    "HIGH":     risk_score >= 70,
    "MEDIUM":   risk_score >= 40,
    "LOW":      risk_score < 40,
}
```

---

## Running the Dashboard

### Development Mode

```bash
# Start dashboard (local testing)
streamlit run dashboard.py

# Opens at http://localhost:8501
```

### Production Mode (via Docker or Server)

```bash
# Using Streamlit Cloud or self-hosted
streamlit run dashboard.py \
  --logger.level=info \
  --client.showErrorDetails=false \
  --server.address=0.0.0.0 \
  --server.port=8080
```

### Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["streamlit", "run", "dashboard.py", \
     "--server.address=0.0.0.0", \
     "--server.port=8080"]
```

Build and run:

```bash
docker build -t fleet-intelligence:latest .
docker run -p 8080:8080 fleet-intelligence:latest
```

---

## Integration with Telemetry API

### Expected Data Format

Your telemetry API should return vehicle data in this format:

```json
{
  "vehicle_id": "scooter_001",
  "vehicle_type": "scooter",
  "latitude": 47.6097,
  "longitude": -122.3331,
  "zone_id": "downtown",
  "battery_pct": 45,
  "is_reserved": false,
  "is_disabled": false,
  "trips_last_24h": 5,
  "trips_last_7d": 25,
  "trips_last_30d": 95,
  "distance_last_7d": 75.5,
  "last_trip_timestamp": "2024-01-15T14:30:00Z",
  "days_deployed": 60,
  "maintenance_count_30d": 1,
  "failure_count_90d": 0,
  "zone_demand": 0.8,
  "zone_supply": 0.9
}
```

### Implementing API Loader

Add to `src/data_loader.py`:

```python
def _load_from_api(self, limit: Optional[int] = None) -> Dict[str, VehicleState]:
    """Load vehicles from fleet telemetry API."""
    import requests
    
    api_url = "https://your-api.com/vehicles"
    headers = {"Authorization": f"Bearer {your_api_key}"}
    
    response = requests.get(api_url, headers=headers, params={"limit": limit})
    response.raise_for_status()
    
    vehicles = {}
    for record in response.json():
        vehicle = VehicleState(**record)
        vehicles[vehicle.vehicle_id] = vehicle
    
    return vehicles
```

---

## Usage Examples

### Example 1: Score a Single Vehicle

```python
from src.decision_engine import FleetDecisionEngine, VehicleState

engine = FleetDecisionEngine()

vehicle = VehicleState(
    vehicle_id="scooter_001",
    vehicle_type="scooter",
    latitude=47.6097,
    longitude=-122.3331,
    zone_id="downtown",
    battery_pct=25,
    trips_last_7d=8,
    trips_last_30d=35,
    days_deployed=45,
    failure_count_90d=0,
    zone_demand=0.7,
    zone_supply=0.9,
)

decision = engine.score_vehicle(vehicle)

print(f"Vehicle: {decision.vehicle_id}")
print(f"Risk: {decision.risk_level.value} ({decision.risk_score:.0f}/100)")
print(f"Recommendation: {decision.recommended_action.value}")
print(f"Reasoning: {decision.reasoning}")
```

Output:
```
Vehicle: scooter_001
Risk: MEDIUM (52/100)
Recommendation: MONITOR
Reasoning: MEDIUM RISK: Battery is 25% (low); High utilization (8 trips/week)
```

### Example 2: Batch Score Fleet

```python
from src.decision_engine import FleetDecisionEngine, FleetDecisionBatch
from src.data_loader import ProductionDataLoader, DataSource

loader = ProductionDataLoader()
vehicles = loader.load_vehicles(source=DataSource.API, limit=100)

batch = FleetDecisionBatch()
decisions = batch.score_fleet(list(vehicles.values()))

summary = batch.get_summary_metrics(decisions)

print(f"Fleet Summary:")
print(f"  Total: {summary['total_vehicles']}")
print(f"  Risk Distribution: {summary['risk_distribution']}")
print(f"  Recommended Actions: {summary['recommended_actions']}")
```

### Example 3: Extract Alerts for Ops Team

```python
critical_vehicles = [
    d for d in decisions.values()
    if d.risk_level.value == 'CRITICAL'
]

for decision in critical_vehicles:
    print(f"\n🚨 {decision.vehicle_id}")
    for alert in decision.alerts:
        print(f"  [{alert['severity']}] {alert['message']}")
        print(f"  → Action: {alert['action']}")
```

---

## Monitoring & Maintenance

### Health Checks

Add this to your monitoring system:

```python
def health_check():
    """Check system health."""
    engine = FleetDecisionEngine()
    
    # Test engine
    test_vehicle = VehicleState(
        vehicle_id="health_check",
        vehicle_type="scooter",
        latitude=0, longitude=0,
        zone_id="test",
        battery_pct=50,
    )
    
    decision = engine.score_vehicle(test_vehicle)
    
    return {
        'status': 'healthy' if decision else 'degraded',
        'timestamp': datetime.now().isoformat(),
    }
```

### Logging & Audit Trail

All decisions are logged automatically:

```python
# Example: Query audit trail
import json

# Each decision has:
decision.decision_id      # Unique identifier
decision.timestamp        # When decided
decision.confidence       # Data quality assessment
decision.signals          # Raw signals used
decision.model_version    # Model version

# Convert to JSON for logging
audit_record = json.dumps(decision.to_dict())
```

### Performance Monitoring

```python
import time

start = time.time()
decisions = batch.score_fleet(vehicles)
elapsed = time.time() - start

latency_per_vehicle = (elapsed / len(vehicles)) * 1000
print(f"Throughput: {len(vehicles)/elapsed:.0f} vehicles/sec")
print(f"Latency: {latency_per_vehicle:.1f}ms per vehicle")
```

Expected performance:
- **Single vehicle**: <50ms
- **100 vehicles**: <2s
- **1000 vehicles**: <15s

---

## Troubleshooting

### Issue: Dashboard not loading

```bash
# Check Streamlit logs
streamlit run dashboard.py --logger.level=debug

# Verify imports
python -c "import streamlit; print(streamlit.__version__)"
```

### Issue: Data validation errors

```python
# Enable verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check data contract
from src.data_loader import DataContract
is_valid, errors = DataContract.validate_record(your_record)
print(errors)
```

### Issue: Low confidence decisions

This means insufficient historical data. Solutions:
- Wait 7+ days for MEDIUM confidence
- Wait 14+ days for HIGH confidence
- Provide historical battery trends manually

---

## Production Checklist

- [ ] **Data Pipeline**: Telemetry API connected and tested
- [ ] **Configuration**: Risk thresholds tuned to business requirements
- [ ] **Monitoring**: Logging, alerting, and audit trail in place
- [ ] **Testing**: Validated with representative vehicle data
- [ ] **Documentation**: Team trained on dashboard and recommendations
- [ ] **Backup**: Data export and disaster recovery procedures
- [ ] **SLA**: Uptime target defined (e.g., 99.9%)
- [ ] **Support**: On-call support for algorithm/data issues
- [ ] **Compliance**: Audit trail meets regulatory requirements
- [ ] **Cost**: Cloud infrastructure costs estimated and approved

---

## Business Impact

### Expected Benefits

| Metric | Baseline | Expected | Improvement |
|--------|----------|----------|------------|
| Mean Time to Failure Detection | 48h | 4h | 12x faster |
| Preventive Maintenance Coverage | 40% | 85% | +2.1x |
| Unplanned Downtime | 8% of fleet | 2% of fleet | -75% |
| Spare Parts Utilization | 60% | 85% | +42% |
| Operational Cost Reduction | — | — | 15-20% |

### ROI Calculation

```
Annual Fleet Size: 5,000 scooters
Average Failure Cost: $150 per unplanned event
Baseline Failures/Year: 400
Expected Failures/Year: 100
Annual Failure Reduction: 300 events × $150 = $45,000

System Cost (annual): $15,000
Net Benefit: $30,000
ROI: 200% in Year 1
```

---

## Support & Escalation

### Levels of Support

**L1 (Dashboard Issues)**: Dashboard UI, data loading, visualization
**L2 (Decision Logic)**: Risk scoring, threshold tuning, alerts
**L3 (Engineering)**: Model improvements, feature additions, infrastructure

### Escalation Path

1. Check dashboard logs: `streamlit logs`
2. Review decision engine logic: See `src/decision_engine.py`
3. Contact engineering with: Decision ID, vehicle details, expected vs actual

---

## Next Steps

1. **Start**: Run `python src/decision_engine.py` to verify core logic
2. **Test**: Load sample data with `streamlit run dashboard.py`
3. **Connect**: Implement API loader for your telemetry
4. **Deploy**: Follow Docker deployment steps
5. **Monitor**: Set up logging and alerts

---

## Questions?

For implementation questions, see:
- `src/decision_engine.py` - Core business logic with extensive comments
- `src/data_loader.py` - Data ingestion patterns
- `dashboard.py` - UI/UX for stakeholders
- `docs/` directory - Additional technical documentation
