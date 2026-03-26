# 🚲 Minimal Fleet Dashboard

A clean, simple Streamlit dashboard showing vehicle risk scores and alerts.

## Features

✅ **Vehicle Table** (50 vehicles)
- Vehicle ID
- Risk Score (0-100)
- Risk Level (LOW/MEDIUM/HIGH/CRITICAL)
- Battery Level
- Primary Alert
- Recommendation
- Zone

✅ **Filters**
- High Risk Only (filter for HIGH/CRITICAL)
- Low Battery Only (filter for battery < 30%)

✅ **Summary Metrics**
- Total Vehicles
- Average Risk Score
- Number of Active Alerts
- Number of Critical Vehicles

✅ **Color-Coded Table**
- GREEN: Low risk
- YELLOW: Medium risk
- ORANGE: High risk
- RED: Critical risk

## Installation

```bash
pip install streamlit plotly pandas
```

## Run

```bash
streamlit run dashboard_minimal.py
```

Then open your browser at `http://localhost:8501`

## Features

### 1. View All Vehicles
See all 50 vehicles with their risk scores and recommendations at a glance.

### 2. Filter High Risk
Click "🔴 High Risk Only" to see only HIGH and CRITICAL vehicles.

### 3. Filter Low Battery
Click "🔋 Low Battery Only" to see vehicles with battery < 30%.

### 4. Summary Metrics
See fleet-wide statistics:
- How many total vehicles
- Average risk across fleet
- How many active alerts
- How many critical vehicles

## Example

```
🚲 Fleet Dashboard
──────────────────
[☑] High Risk Only
[☐] Low Battery Only

────────────────────────────────────
Total: 50  │  Avg Risk: 42  │  Alerts: 8  │  Critical: 2
────────────────────────────────────

Vehicle ID   Risk Score  Risk Level  Battery  Alert                    Recommendation
vehicle_001  65         HIGH        28%      Battery critical: 28%   INSPECT
vehicle_002  45         MEDIUM      52%      Zone overstocked         MONITOR
vehicle_003  22         LOW         88%                              MONITOR
...
```

## The model uses 50 vehicles loaded from sample data. To use real data:

Edit the line in `dashboard_minimal.py`:

```python
vehicles = loader.load_vehicles(source=DataSource.API, limit=50)
```

Replace `DataSource.API` with your actual data source and update `_load_from_api()` in `data_loader.py`.

## Control Update Frequency

The dashboard caches data for 5 minutes. To change:

```python
@st.cache_data(ttl=300)  # Change 300 to your desired seconds
def load_and_score_fleet():
    ...
```

## Troubleshooting

**"ModuleNotFoundError: No module named 'streamlit'"**
```bash
pip install streamlit
```

**Dashboard not updating**
Click the ⟲ button in the top-right corner, or press `R` to rerun.

**Slow performance**
Reduce the limit parameter: `limit=20` instead of `limit=50`

---

**Next Step**: Connect to your real telemetry API! See [PRODUCTION_DEPLOYMENT_GUIDE.md](PRODUCTION_DEPLOYMENT_GUIDE.md)
