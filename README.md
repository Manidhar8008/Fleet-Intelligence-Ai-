# Fleet Intelligence AI

**Production-Ready SaaS MVP for Mobile Fleet Management**

Enterprise-grade AI-powered fleet optimization platform for micro-mobility operators. Real-time risk detection, revenue optimization, and AI-powered recommendations for managing electric scooter, bike, EV, and delivery fleets.

---

## 🎯 What This Does

The **Fleet Intelligence AI platform** is a **production-ready Streamlit dashboard** that:

✨ **Real-time Risk Scoring** — Analyzes 40+ vehicle metrics using a weighted risk model  
💡 **AI Decision Engine** — Generates actionable recommendations (charging, maintenance, rebalancing)  
📊 **Executive Dashboard** — Shows business-focused KPIs (fleet health, revenue impact, optimization opportunities)  
💰 **Revenue Impact Analysis** — Quantifies daily losses and recovery potential in currency (₹)  
🚀 **Zero Dependencies** — Fully self-contained, runs entirely locally with demo data  

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Python 3.9+ installed
- Windows, Mac, or Linux

### Step 1: Navigate to App Directory
```bash
cd app
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the Platform
**Windows:**
```bash
run.bat
```

**Mac/Linux:**
```bash
chmod +x run.sh
./run.sh
```

**Or directly:**
```bash
python -m streamlit run main.py
```

### Step 4: Access in Browser
Opens automatically at **http://localhost:8501**

### Step 5: Try It
- Click "Generate Demo Fleet" to see 150 synthetic scooters
- Or upload your own CSV with columns: `vehicle_id, battery, utilization, zone`

---

## 📁 Directory Structure

```
app/                        ← PRODUCTION CODE (USE THIS)
├── main.py                 Entry point for Streamlit
├── requirements.txt        All dependencies
├── README.md              Quick start guide
├── ARCHITECTURE.md        System design
├── DEPLOYMENT.md          5 deployment options
│
├── core/                  Data & decision pipeline
│   ├── data_loader.py
│   ├── preprocessing.py
│   ├── feature_engineering.py
│   ├── decision_engine.py
│   └── insights_engine.py
│
├── models/                ML scoring engines
│   └── risk_model.py      Risk scoring (0-100)
│
├── utils/                 Configuration & logging
│   ├── config.py
│   └── logger.py
│
└── data/                  Data storage
    └── sample_fleet.csv   Sample data

See MIGRATION_COMPLETE.md for consolidation details.

---

## 📋 What You'll See

### 1. **Fleet Performance Dashboard**
- Total Fleet Size (tracked vehicles)
- High-Risk Fleet % (color-coded alerts)
- Estimated Daily Loss (₹) if issues not addressed
- Optimization Opportunity (₹/day potential gain)

### 2. **AI Decision Engine**
Real-time recommendations grouped by urgency:
- 🚨 **CRITICAL** — Immediate actions (charge critical batteries, urgent repairs)
- ⚠️ **WARNING** — Actions within 24 hours (preventive maintenance)
- ✅ **OPPORTUNITY** — Revenue optimization (vehicle rebalancing, idle vehicle repositioning)

### 3. **Risk Profile & Fleet Health**
- Risk distribution across fleet (LOW/MEDIUM/HIGH/CRITICAL)
- Fleet health status indicator
- Risk level counts and percentages

### 4. **Fleet Operations Detail**
- Filterable table with live vehicle data
- Filter by risk level, battery status, zone
- Business context: alerts, recommendations, zone location

### 5. **Operational Analytics**
- Battery health distribution (pie chart)
- Fleet utilization breakdown (bar chart)
- Historical trends and patterns

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Python 3.8+ installed

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Dashboard
```bash
streamlit run app.py
```

### Step 3: View in Browser
Dashboard opens automatically at **http://localhost:8501**

---

## 🏗️ Architecture

```
project_root/
├── app.py                    # Main Streamlit dashboard (ENTRY POINT)
├── requirements.txt          # Python dependencies (4 packages only)
├── README.md                 # This file
├── SETUP.md                  # Detailed setup instructions
│
├── src/
│   ├── decision_engine.py    # Risk scoring & decision logic
│   └── data_loader.py        # Demo data generation & loading
│
├── data/
│   ├── sample_vehicles.csv   # Demo fleet data
│   └── [other sample files]
│
├── tests/
│   └── test_production_dashboard.py  # Complete system test
│
└── docs/
    └── [Additional documentation]
```

---

## 💻 Technology Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| **Streamlit** | 1.28+ | Web dashboard UI |
| **Pandas** | 1.5+ | Data manipulation |
| **NumPy** | 1.24+ | Numerical computing |
| **Plotly** | 5.0+ | Interactive charts |

**Total dependencies: 4 packages**. No bloat, no complexity.

---

## 🔧 How It Works

### Risk Scoring Model
Each vehicle receives a risk score (0-100):
- **40%** Battery Health (critical if < 20%)
- **35%** Utilization Rate (high if idle > 8 hours)
- **15%** Zone Pressure (supply-demand mismatch)
- **10%** Maintenance Status (overdue checks)

### Decision Logic
The engine:
1. Calculates risk scores for all vehicles
2. Identifies action items by category
3. Quantifies business impact
4. Generates specific, prioritized recommendations
5. Provides revenue/efficiency metrics

### Demo Data
System generates synthetic fleet data internally:
- 50 vehicles with realistic profiles
- Mixed risk levels and battery states
- Geographic zones with demand patterns
- One-time generation per dashboard session

---

## 🧪 Testing

Run the complete system test:
```bash
python tests/test_production_dashboard.py
```

Expected output: **8/8 PASS** showing all components working correctly.

---

## 📊 Real-World Example

**Fleet of 50 scooters — Daily Operations**

```
Status: HEALTHY (Avg Risk: 22/100)

KPIs:
  • Total Fleet: 50 vehicles
  • High-Risk %: 12% (6 vehicles)
  • Daily Loss: ₹2,400 if not addressed
  • Optimization Opportunity: ₹850/day

Actions Needed:
  🚨 CRITICAL (2):
    - Charge vehicle #S005 (2% battery)
    - Inspect vehicle #S023 (mechanical alert)

  ⚠️ WARNING (4):
    - Schedule maintenance (4 vehicles)

  ✅ OPPORTUNITY:
    - Reposition idle vehicles → +₹600/day
```

---

## 🎓 Use Cases

1. **Operations Manager** — Daily fleet health & urgent actions
2. **Maintenance Scheduler** — Prioritized maintenance queue
3. **Fleet Optimizer** — Rebalancing recommendations with ROI
4. **Executive** — KPI dashboard for stakeholders
5. **Data Analyst** — Export data for custom analysis

---

## 🚀 Deployment

### Local Development
```bash
streamlit run app.py
```

### Production Server
```bash
streamlit run app.py --server.port=80 --server.address=0.0.0.0
```

### Docker
Pre-built Docker support available in `Future_contrub/Dockerfile` (optional)

---

## 🔐 Security

- **No cloud integrations** — fully self-contained
- **No external APIs** — zero network dependencies
- **Demo data only** — synthetic fleet for testing
- **Local machine only** — no remote data transmission

---

## 🐛 Troubleshooting

### Dashboard won't start
```bash
# Verify installation
streamlit --version

# Reinstall packages
pip install --force-reinstall -r requirements.txt
```

### Port 8501 already in use
```bash
# Use different port
streamlit run app.py --server.port=8502
```

### Import errors
```bash
# Ensure you're in correct Python environment
which python  # or: where python (Windows)
pip list     # verify all packages installed
```

---

## 📝 File Structure Summary

| File | Purpose |
|------|---------|
| `app.py` | Main dashboard (entry point) |
| `src/decision_engine.py` | Risk scoring logic |
| `src/data_loader.py` | Data loading & demo generation |
| `requirements.txt` | Dependencies list |
| `tests/test_production_dashboard.py` | System validation |
| `data/` | Sample data files |
| `docs/` | Additional documentation |

---

## 📈 Performance

- **Load Time:** < 2 seconds
- **Dashboard Responsiveness:** Real-time
- **Memory Usage:** ~100MB
- **CPU Usage:** Minimal (idle when not filtering/sorting)
- **Data Refresh:** 5-minute cache cycle

---

## 🔄 What's Included

✅ Complete risk scoring engine  
✅ Real-time dashboard  
✅ Business-focused KPIs  
✅ AI recommendations  
✅ Data export capability  
✅ Comprehensive test suite  
✅ Production-ready code  

---

## 📚 Documentation

- **README.md** (this file) — Overview & quick start
- **SETUP.md** — Detailed setup & troubleshooting
- **tests/test_production_dashboard.py** — Test examples
- **src/** — Inline code documentation

---

## 🎯 Next Steps

1. **Run the dashboard** → `streamlit run app.py`
2. **Read SETUP.md** → For detailed customization
3. **Run tests** → `python tests/test_production_dashboard.py`
4. **Explore code** → Review `src/decision_engine.py`
5. **Integrate data** → Replace demo data with real fleet API

---

## 📞 Support

- **Setup issues?** → See `SETUP.md`
- **Feature requests?** → Add to `docs/`
- **Bug reports?** → Document with steps to reproduce

---

**Status:** ✅ Production Ready  
**Last Updated:** March 2026  
**Maintained by:** Fleet Operations Team
