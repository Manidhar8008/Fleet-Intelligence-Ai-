# 🏗️ System Architecture

## Overview

The Fleet Intelligence Decision System is a production-grade AI system designed for real-time vehicle risk scoring and operational decision-making in a micromobility fleet.

The design prioritizes:
- **Explainability**: Every decision explains why
- **Reliability**: Handles incomplete/noisy data gracefully
- **Performance**: Sub-second latency per vehicle
- **Auditability**: Full decision trail for compliance
- **Simplicity**: Transparent business logic, not black-box ML

---

## Design Philosophy

### Not a Black-Box

Unlike many "AI" systems, this engine is **radically transparent**:

```python
# Every decision includes:
decision.risk_score       # 0-100 (exact calculation shown)
decision.primary_drivers  # Top 3 factors with scores
decision.reasoning        # Human-readable narrative
decision.confidence       # Data quality assessment
decision.signals          # Raw signals used
```

This means:
- ✅ Operations team can trust recommendations
- ✅ Compliance/audit can verify decisions
- ✅ Model changes are validated and documented
- ❌ Cannot hide "because the model said so"

### Conservative by Design

The system assumes:
- **False alarms are cheaper than missed failures**
- **Uncertainty means lower risk scores, not higher**
- **Actionable signals matter, statistical significance doesn't**

This manifests as:
- Recall-focused thresholds (catch problems early)
- Down-weighting unreliable signals
- Confidence levels that gate aggressive actions

---

## Core Components

### 1. Data Layer (`data_loader.py`)

**Responsibility**: Ingest, validate, and enrich vehicle telemetry data.

```
Raw Data Sources
    ↓
Data Contract Validation (required fields, constraints)
    ↓
Type Conversion & Normalization
    ↓
Enrichment (compute missing metrics)
    ↓
VehicleState Objects (ready for scoring)
```

**Key Functions:**
- `ProductionDataLoader` - Multi-source ingestion (API, CSV, DB, sample)
- `DataContract` - Define and validate schemas
- `VehicleDataAggregator` - Compute zone/cohort metrics

**Design Rationale:**
- Separation of concerns (data ≠ logic)
- Fail-safe validation (catch bad data early)
- Multiple source support (flexible deployment)
- Enrichment layer (auto-compute missing signals)

---

### 2. Decision Engine (`decision_engine.py`)

**Responsibility**: Score vehicles and generate recommendations.

```
VehicleState
    ↓
Extract Risk Signals (battery trends, utilization, idle time)
    ↓
Calculate Component Scores (battery, utilization, zone, maintenance)
    ↓
Weighted Composite Score (0-100)
    ↓
Map to Risk Level + Confidence
    ↓
Generate Alerts (threshold-based)
    ↓
Recommend Action (policy-based)
    ↓
Decision Object (with full audit trail)
```

**Key Modules:**

#### Signal Extraction
Converts raw telemetry into business-meaningful signals.

Raw data:
```python
battery_pct=45, battery_pct_prev_day=52, battery_pct_prev_week=78
```

Extracted signals:
```python
battery_decline_rate = 4.7  # % per day
battery_trend = "declining"
```

#### Risk Scoring
Weighted model combining health, utilization, environment, and history:

```python
risk_score = (
    battery_score (0-100) * 0.40 +  # 40%
    utilization_score (0-100) * 0.35 +  # 35%
    zone_pressure_score (0-100) * 0.15 +  # 15%
    maintenance_score (0-100) * 0.10  # 10%
)
# Result: 0-100 scale
```

Example breakdown:
```
Road Breakdown:
├─ Battery: 45/100 (low battery, but stable) · weight 0.40 = 18.0
├─ Utilization: 62/100 (15 trips/week, high stress) · weight 0.35 = 21.7
├─ Zone: 25/100 (low supply pressure) · weight 0.15 = 3.75
└─ Maintenance: 20/100 (no recent issues) · weight 0.10 = 2.0
   ────────────────────────────────────────
   Composite Risk Score:                    45.5
```

#### Decision Policy
Converts risk score into actionable recommendations:

```python
Risk Score Distribution | Risk Level | Action           | Confidence Gate
────────────────────────┼────────────┼─────────────────┼─────────────────
     >= 85              | CRITICAL   | INSPECT URGENT  | Any
     70-85              | HIGH       | INSPECT         | High/Med
     40-70              | MEDIUM     | MONITOR         | High/Med
     < 40               | LOW        | MONITOR         | Any
```

#### Confidence Assessment
Gate recommendations based on data sufficiency:

```python
Days of Data | Trend Stability | Confidence
─────────────┼─────────────────┼───────────
< 7 days     | Any             | LOW
7-14 days    | Any             | MEDIUM
> 14 days    | Stable trends   | HIGH
> 14 days    | Changing trends | MEDIUM
```

Actions gated by confidence:
- **LOW**: Only non-invasive monitoring
- **MEDIUM**: Inspection/monitoring
- **HIGH**: Aggressive maintenance allowed

---

### 3. Recommendation Engine

**Policy Rules** (deterministic, not probabilistic):

```python
if risk_level == CRITICAL:
    if battery < 10%:
        recommend REPAIR
    else:
        recommend INSPECT
        
elif risk_level == HIGH:
    if failure_count_90d >= 2:
        recommend REPAIR
    elif maintenance_count_30d >= 1:
        recommend INSPECT
    else:
        recommend MONITOR

elif risk_level == MEDIUM:
    if idle_hours > 4:
        recommend REBALANCE
    else:
        recommend MONITOR

elif risk_level == LOW:
    if idle_hours > 48:
        recommend ROTATE
    else:
        recommend MONITOR
```

---

### 4. Alert System

**Alert Categories:**

| Alert Type | Trigger | Severity | Action |
|---|---|---|---|
| BATTERY_CRITICAL | battery < 15% | CRITICAL | Immediate charge |
| IDLE_TIMEOUT | idle > 24h | WARNING | Investigate + relocate |
| MULTIPLE_FAILURES | failures >= 3 | WARNING | Schedule inspection |
| ZONE_OVERSTOCK | supply > demand | INFO | Candidate for rebalance |
| MAINTENANCE_DUE | recent maintenance + idle | INFO | Functional test |

Alerts are independent of risk score (e.g., can generate CRITICAL battery alert with LOW overall risk).

---

### 5. Dashboard (`dashboard.py`)

**Responsibility**: Visualize fleet metrics and decisions for operations teams.

**Pages:**

1. **Fleet Overview**
   - Total vehicles, critical count, avg risk, idle count
   - Risk distribution (pie chart)
   - Recommended actions breakdown

2. **Critical Alerts**
   - High-priority vehicles with WHY and recommended action
   - Alert type breakdown

3. **Vehicle Details**
   - Sortable/filterable table
   - Status, risk, battery, zone, idle time
   - Per-vehicle decision reasoning

4. **Zone Analysis**
   - Supply/demand heat map
   - Utilization by zone
   - Maintenance pressure

**Features:**
- Real-time data refresh (5 minute cache)
- Multi-filter exploration
- Mobile responsive
- Production-grade error handling

---

## Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         REAL-TIME OPERATIONS                               │
└──────────────────┬───────────────────────────────────────────────────────┘
                   │
      ┌────────────▼────────────┐
      │  Vehicle Telemetry API  │  (Battery, location, trips, etc.)
      └────────────┬────────────┘
                   │
      ┌────────────▼────────────┐    ┌──────────────────────┐
      │  ProductionDataLoader   │◄───┤  Historical Data     │
      │  - CSV/API/DB connector │    │  (CSV files)         │
      │  - Data validation      │    └──────────────────────┘
      └────────────┬────────────┘
                   │
      ┌────────────▼────────────┐
      │  VehicleState objects   │  (Normalized, validated)
      │  (30-50 fields each)    │
      └────────────┬────────────┘
                   │
      ┌────────────▼────────────┐
      │ FleetDecisionEngine      │
      │  ├─ Signal extraction   │
      │  ├─ Risk scoring        │
      │  ├─ Risk level mapping  │
      │  ├─ Alert generation    │
      │  ├─ Action recommend    │
      │  └─ Reasoning narrative │
      └────────────┬────────────┘
                   │
      ┌────────────▼────────────┐
      │  Decision objects       │  (Vehicle ID → Decision)
      │  - Risk score           │
      │  - Confidence level     │
      │  - Alerts               │
      │  - Audit trail          │
      └────────────┬────────────┘
                   │
       ┌───────────┼───────────┐
       │           │           │
   ┌───▼──┐  ┌─────▼───┐  ┌────▼────┐
   │Log   │  │Dashboard│  │Alert    │
   │JSON  │  │Streamlit│  │Slack/   │
   │      │  │UI       │  │Email    │
   └──────┘  └─────────┘  └─────────┘
```

---

## Decision Scoring Model

### Weighted Component Model

Rather than a black-box neural net, we use **transparent weighted components**:

```
Risk Score = 
  (Battery Health Score         × 0.40) +
  (Utilization Stress Score     × 0.35) +
  (Zone Pressure Score          × 0.15) +
  (Maintenance History Score    × 0.10)

Result: 0-100
```

### Component Scoring Details

#### Battery Health (40%)
```python
score = 0
if battery_pct < 15:         # Critical
    score += 50
elif battery_pct < 30:       # Low
    score += 30
elif battery_pct < 50:       # Medium-low
    score += 15

if decline_rate > 5%/day:    # Rapid drain
    score += 30
elif decline_rate > 2%/day:  # Moderate drain
    score += 15

# Confidence gate: down-weight if insufficient trend data
if battery_trend == "unknown":
    score *= 0.6

return min(100, score)
```

#### Utilization Stress (35%)
```python
score = 0

intensity = normalize(trips_per_day / 10.0)  # 0-1
if intensity > 0.8:
    score += 40
elif intensity > 0.5:
    score += 20

if utilization_trend == "increasing":
    score += 20

idle_penalty = min(30, idle_hours / 24)  # 1 pt per day
score += idle_penalty

return min(100, score)
```

#### Zone Pressure (15%)
```python
pressure = zone_supply / zone_demand  # normalized
if pressure > 0.8:
    return 60   # High pressure zone
elif pressure > 0.6:
    return 35
else:
    return 15
```

#### Maintenance History (10%)
```python
score = 0
if maintenance_count_30d >= 2:
    score += 40
elif maintenance_count_30d >= 1:
    score += 20

if failure_count_90d >= 2:
    score += 30
elif failure_count_90d >= 1:
    score += 15

if is_under_repair:
    score += 25

return min(100, score)
```

---

## Confidence Model

**Why Confidence?**

Decisions with insufficient data are less reliable. Rather than hiding uncertainty, we make it explicit.

```python
Confidence Assessment:
├─ Data Age (days_deployed)
│  ├─ < 7d  → insufficient for ANY confidence
│  ├─ 7-14d → can reach MEDIUM
│  └─ > 14d → can reach HIGH
│
├─ Trend Stability (signal_variance)
│  ├─ High variance → cap at MEDIUM
│  └─ Stable trends → can reach HIGH
│
└─ Signal Freshness
   ├─ Last 24h data → most recent
   └─ Older than 48h → reduce confidence
```

**Implications:**

| Confidence | What it means | Actions allowed |
|---|---|---|
| HIGH | Well-established pattern, good data flow | Aggressive maintenance |
| MEDIUM | Mixed signals or moderate data | Inspection, monitoring |
| LOW | New vehicle or insufficient data | Only non-invasive actions |

---

## Performance Characteristics

### Computational Complexity

- **Per vehicle**: O(1) - constant time signal extraction and scoring
- **Per fleet**: O(n) - linear in fleet size
- **Storage**: ~1KB per vehicle (decision)

### Throughput

| Scale | Time | Rate |
|---|---|---|
| 1 vehicle | <50ms | - |
| 10 vehicles | <100ms | - |
| 100 vehicles | <1s | 100 vehicles/sec |
| 1,000 vehicles | <15s | 60-70 vehicles/sec |
| 10,000 vehicles | <150s | 65-70 vehicles/sec |

Bottleneck: data loading, not scoring.

### Memory Usage

- Decision engine: ~5MB (models + state)
- Per 1000 vehicles: ~10MB (decisions cached)
- Dashboard: lightweight Streamlit app

Total: <100MB for full fleet of 10K vehicles.

---

## Extensibility

### Adding New Signals

```python
# 1. Update VehicleState to include new data
@dataclass
class VehicleState:
    # ... existing fields ...
    repair_cost_90d: float = 0.0  # NEW: repair spending

# 2. Update RiskSignals
@dataclass
class RiskSignals:
    # ... existing signals ...
    repair_cost_pressure: float = 0.0  # NEW

# 3. Add extraction logic in _extract_signals()
def _extract_signals(self, vehicle):
    # ... existing ...
    repair_pressure = self._calculate_repair_cost_pressure(vehicle)
    
    return RiskSignals(
        # ... existing ...
        repair_cost_pressure=repair_pressure
    )

# 4. Add scoring method
def _score_repair_cost(self, signals):
    score = 0
    if signals.repair_cost_pressure > 0.8:
        score += 35
    return min(100, score)

# 5. Update composite scoring
composite = (
    # ... existing weights ...
    scores['repair_cost'] * 0.05  # NEW: 5% weight
)
```

### Adding New Alerts

```python
# 1. Add enum
class AlertType(Enum):
    # ... existing ...
    REPAIR_COST_HIGH = "REPAIR_COST_HIGH"

# 2. Add alert generation logic
alerts.append({
    'alert_type': AlertType.REPAIR_COST_HIGH.value,
    'severity': 'WARNING',
    'message': f"Repair costs elevated: ${signals.repair_cost_90d:.0f}",
    'action': 'Review maintenance logs for recurring issues',
})
```

---

## Error Handling Strategy

```
Invalid Vehicle Data
    ↓
DataContract.validate_record()
    ├─ Required fields missing → ValueError
    ├─ Type mismatch → ValueError
    └─ Constraint violation → ValueError
    ↓
Validation Error Logged
    ├─ Counted in load_stats
    └─ Decision skipped for this vehicle
    ↓
Batch Processing Continues
    (graceful degradation, not cascade failure)
```

---

## Deployment Scenarios

### Scenario 1: Batch Analysis (Daily)
```
Cloud Schedule (Airflow, etc.)
    ↓
Load all vehicles from API
    ↓
Score fleet (5K vehicles = 60-90 sec)
    ↓
Export decisions to database
    ↓
Generate alerts for ops team
    ↓
Update dashboard cache
```

**Risk**: Latency OK for batch, not for real-time

**Mitigation**: Pre-cache, run overnight

### Scenario 2: Real-Time API
```
Vehicle API
    ↓
API Gateway (auth, rate limit)
    ↓
Decision Engine Service (containerized)
    ├─ Stateless (scale horizontally)
    ├─ <100ms per request
    └─ Audit logging to database
    ↓
Response w/ decision + confidence
```

**Risk**: Need to handle high QPS

**Mitigation**: Load balancing, caching, queue batching

### Scenario 3: Edge/Local
```
Mobile app / field device
    ↓
Lightweight inference engine
    (quantized model, <5MB)
    ↓
Score locally (minimal latency)
    ↓
Sync decisions to cloud
    ↓
Merge with fleet-wide context
```

**Risk**: Model version skew

**Mitigation**: Version control, periodic sync

---

## Testing Strategy

```
Unit Tests
├─ Signal extraction: verify trends computed correctly
├─ Risk scoring: verify math exact
├─ Alerts: verify triggers at exact thresholds
└─ Data validation: verify schema enforcement

Integration Tests
├─ Load + score pipeline
├─ End-to-end vehicle data → decision
└─ Dashboard data binding

Regression Tests
├─ Golden dataset: score, verify output matches
├─ Historical decisions: re-score, check consistency
└─ Edge cases: battery=0, idle=1000h, etc.

Performance Tests
├─ Throughput: N vehicles in time T
├─ Latency: p50, p95, p99 decision time
└─ Memory: fleet size vs memory used
```

---

## Future Evolution

### Phase 2 (Months 3-6)

- [ ] Predictive maintenance (time-to-failure model)
- [ ] Dynamic zone demand forecasting
- [ ] Integration with work orders system
- [ ] Real-time weather impact on battery

### Phase 3 (Months 9-12)

- [ ] Reinforcement learning: learn optimal thresholds
- [ ] Anomaly detection: identify unusual patterns
- [ ] Multi-fleet federation: shared model across cities
- [ ] Advanced visualization: 3D fleet heatmap

### Phase 4 (1+ Years)

- [ ] Autonomous fleet rebalancing optimization
- [ ] Predictive maintenance parts procurement
- [ ] Supply chain integration
- [ ] Revenue impact modeling

---

## Conclusion

The Fleet Intelligence system is built on:

✅ **Simplicity**: Transparent weighted model, not black-box
✅ **Reliability**: Handles noisy data gracefully
✅ **Explainability**: Every decision includes "why"
✅ **Performance**: Sub-second latency at scale
✅ **Maintainability**: Clean separation of concerns
✅ **Auditability**: Full decision trail

It prioritizes **operational value** over statistical perfection, and **human trust** over model complexity.
