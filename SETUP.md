# Setup Guide

Detailed instructions for setting up and running the Fleet Decision Intelligence System.

---

## 📋 Prerequisites

- **Python 3.8+** — Download from [python.org](https://www.python.org/downloads/)
- **pip package manager** — Comes with Python
- **Text editor or IDE** — VS Code, PyCharm, or similar (optional)
- **200 MB disk space** — For dependencies
- **Internet** — For first-time pip install only

---

## 🔧 Installation

### Windows

#### Step 1: Create Project Directory
```powershell
mkdir C:\projects\fleet-decision-system
cd C:\projects\fleet-decision-system
```

#### Step 2: Clone or Extract Project Files
Copy all project files to the directory.

#### Step 3: Create Virtual Environment
```powershell
python -m venv .venv
```

#### Step 4: Activate Virtual Environment
```powershell
.\.venv\Scripts\Activate.ps1
```

If you get a permission error, run PowerShell as Administrator or execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Step 5: Install Dependencies
```powershell
pip install -r requirements.txt
```

#### Step 6: Run Dashboard
```powershell
streamlit run app.py
```

Dashboard should open automatically at **http://localhost:8501**

---

### macOS/Linux

#### Step 1: Create Project Directory
```bash
mkdir ~/fleet-decision-system
cd ~/fleet-decision-system
```

#### Step 2: Clone or Extract Project Files
Copy all project files to the directory.

#### Step 3: Create Virtual Environment
```bash
python3 -m venv .venv
```

#### Step 4: Activate Virtual Environment
```bash
source .venv/bin/activate
```

#### Step 5: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 6: Run Dashboard
```bash
streamlit run app.py
```

Dashboard should open automatically at **http://localhost:8501**

---

## ✅ Verify Installation

### Check Python Version
```bash
python --version
# Should show: Python 3.8 or higher
```

### Check Installed Packages
```bash
pip list
# Should show: streamlit, pandas, numpy, plotly
```

### Run System Test
```bash
python tests/test_production_dashboard.py
```

Expected output:
```
✅ PASS  Data Loading
✅ PASS  Risk Scoring
✅ PASS  Alert Generation
✅ PASS  Zone Analysis
✅ PASS  Filtering Logic
✅ PASS  Optimization Engine
✅ PASS  AI Insights
✅ PASS  Executive Summary

Dashboard is Production Ready!
```

---

## 🚀 Running the Dashboard

### Start Dashboard
```bash
streamlit run app.py
```

### Access Dashboard
- **Local** → http://localhost:8501
- **Network** → http://<your-ip>:8501

### Stop Dashboard
Press `Ctrl+C` in terminal

### Common Options
```bash
# Different port
streamlit run app.py --server.port=8502

# Headless (no browser)
streamlit run app.py --logger.level=error

# Server mode (production)
streamlit run app.py --server.port=80 --server.address=0.0.0.0
```

---

## 📊 Dashboard Walkthrough

### 1. Fleet Performance Dashboard (Top)
This shows 4 key business KPIs:
- **Total Fleet Size** — Number of vehicles being tracked
- **High-Risk Fleet %** — Percentage of fleet at risk (🔴 CAUTION if >15%, 🟡 MONITOR if >5%)
- **Est. Daily Loss (₹)** — Revenue loss if issues not addressed (₹500 per critical, ₹200 per high-risk)
- **Optimization Gain (₹/day)** — Potential revenue if all recommendations implemented

### 2. AI Decision Engine Section
Shows prioritized recommendations:

**🚨 CRITICAL — Immediate Action Required**
- Battery charging orders for critical vehicles
- Impact: Specific ₹ value
- Specific action and zones

**⚠️ WARNING — Action Needed Within 24 Hours**
- Preventive maintenance recommendation
- Risk reduction estimate
- Specific action required

**✅ OPPORTUNITY — Revenue Optimization**
- Vehicle rebalancing opportunities
- Potential ₹ gain
- Specific zones and vehicle count

### 3. Fleet Risk Profile
Shows visual breakdown:
- Bar chart of vehicles by risk level
- Status indicators (🔴 🟠 🟡 🟢)
- Fleet overall health status

### 4. Fleet Operations Detail
Interactive table with filters:
- **Filter by Risk Level** — See only high-risk or specific levels
- **Filter by Battery** — Critical battery alerts (<30%)
- **Filter by Zone** — Specific geographic areas
- **Columns:** Vehicle ID, Risk Score, Alert Type, Recommendations, Zone

### 5. Battery & Utilization Insights
Dual visualization:
- **Left:** Battery level distribution (pie chart)
- **Right:** Vehicle utilization categories (bar chart)

---

## 🔌 Data Integration

### Current System (Demo Data)
The dashboard ships with **internal demo data generation**:
- Automatically generates 50 realistic vehicles on startup
- No files to load or external dependencies
- Perfect for testing and demos

### Integrating Real Data

To use real fleet data, edit `src/data_loader.py`:

```python
# Current (demo mode):
vehicles = generate_demo_fleet()

# To use CSV:
vehicles = load_from_csv('path/to/vehicles.csv')

# To use API:
vehicles = load_from_api('https://api.fleet.com/vehicles')

# To use Database:
vehicles = load_from_database('connection_string')
```

See `src/data_loader.py` for implementation details.

---

## 🧪 Testing & Validation

### Run Full System Test
```bash
python tests/test_production_dashboard.py
```

### Run Individual Components
```bash
# Test decision engine
python -c "from src.decision_engine import FleetDecisionEngine; print('✅ Decision Engine OK')"

# Test data loader
python -c "from src.data_loader import ProductionDataLoader; print('✅ Data Loader OK')"
```

### Manual Testing Checklist
- [ ] Dashboard loads without errors
- [ ] KPI metrics display correctly
- [ ] Decision panel shows recommendations
- [ ] Risk chart renders
- [ ] Fleet table shows data
- [ ] Filters work (risk, battery, zone)
- [ ] Charts are interactive (hover, zoom, pan)
- [ ] No console errors

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'streamlit'"

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: Port 8501 already in use

**Solution:**
```bash
# Use different port
streamlit run app.py --server.port=8502

# Or kill the process using port 8501
# Windows:
netstat -ano | findstr :8501
taskkill /PID <pid> /F

# macOS/Linux:
lsof -i :8501
kill -9 <pid>
```

### Issue: Virtual environment not activating

**Windows:**
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
source .venv/bin/activate
# Should show (.venv) in terminal prompt
```

### Issue: Dashboard loads but shows errors

**Solution:**
1. Check console for errors
2. Run test: `python tests/test_production_dashboard.py`
3. Reinstall packages: `pip install --force-reinstall -r requirements.txt`
4. Check Python version: `python --version` (should be 3.8+)

### Issue: Dashboard slow or unresponsive

**Solution:**
1. Close browser and restart dashboard
2. Clear browser cache
3. Try different port: `streamlit run app.py --server.port=8502`
4. Check system resources (memory, CPU)

---

## 📁 Project Structure Explained

```
project_root/
│
├── app.py                          # MAIN ENTRY POINT
│   └── Main Streamlit application
│       Imports: src.decision_engine, src.data_loader
│
├── requirements.txt                # DEPENDENCIES
│   └── streamlit, pandas, numpy, plotly (4 packages only!)
│
├── README.md                       # PROJECT OVERVIEW
│
├── SETUP.md                        # THIS FILE
│
├── src/                            # SOURCE CODE
│   ├── decision_engine.py
│   │   └── Risk scoring, decision logic
│   │
│   └── data_loader.py
│       └── Data loading, demo generation
│
├── data/                           # SAMPLE DATA
│   └── sample_vehicles.csv
│
├── tests/                          # TEST FILES
│   └── test_production_dashboard.py
│
├── docs/                           # DOCUMENTATION
│
├── reports/                        # OUTPUT FILES
│
└── artifacts/                      # VISUALIZATIONS
```

---

## 🐛 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| Port 8501 in use | `streamlit run app.py --server.port=8502` |
| venv won't activate | Run as Administrator |
| Slow dashboard | Reduce fleet size in `data_loader.py` |
| Blank dashboard | Check browser console for errors |

---

## 📈 Performance Tuning

### Reduce Load Time
```python
# In src/data_loader.py, reduce fleet size:
return [generate_vehicle() for _ in range(30)]  # Instead of 50
```

### Enable Real-Time Updates
```python
@st.cache_data(ttl=60)  # Cache for 60 seconds instead of 300
```

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

### With Docker
```bash
docker run -p 8501:8501 fleet-decision
```

---

## ✅ You're Done!

Next steps:
1. Run: `streamlit run app.py`
2. Explore the dashboard
3. Read the code in `src/`
4. Integrate your real data
5. Deploy to production

---

**Status:** ✅ Production Ready
