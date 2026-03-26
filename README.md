# 🚲 Fleet Operations AI Dashboard

**Production-Ready | Zero External Dependencies | 100% Self-Contained**

---

## ⚡ Quick Start (5 Minutes)

### 1️⃣ **Fresh Environment Setup**

```powershell
# Navigate to project
cd "d:\MY projects\lime-iot-ml-platform-"

# Create NEW virtual environment
python -m venv venv_new

# Activate it
.\venv_new\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### 2️⃣ **Run Dashboard**

```powershell
streamlit run app.py
```

### 3️⃣ **Open in Browser**

```
http://localhost:8501
```

✅ **Done!** Dashboard is live.

---

## 📊 What You Get

### Dashboard Sections
- **Executive Summary** - 4 KPIs (Total Vehicles, Avg Risk, Critical Count, Alerts)
- **Risk Distribution** - Chart showing LOW/MEDIUM/HIGH/CRITICAL breakdown
- **Fleet Operations Table** - All vehicles sortable by risk, with filters
- **AI Decision Insights** - Natural language recommendations
- **Battery Health** - Distribution and statistics
- **Fleet Utilization** - Usage patterns and categories

### Key Features
✅ Real-time risk scoring (0-100 scale)  
✅ Smart filtering (High Risk, Low Battery)  
✅ Color-coded severity levels  
✅ Interactive Plotly charts  
✅ 50 demo vehicles pre-loaded  
✅ Zero external file dependencies  

---

## 🔧 Project Structure

```
lime-iot-ml-platform-/
├── app.py                    ← SINGLE ENTRY POINT
├── requirements.txt          ← DEPENDENCIES
├── README.md                 ← THIS FILE
└── src/
    ├── decision_engine.py    (risk scoring logic)
    └── data_loader.py        (data ingestion)
```

---

## 🛠️ Troubleshooting

### "Module not found" error
```powershell
# Activate correct venv
.\venv_new\Scripts\Activate.ps1

# Reinstall
pip install -r requirements.txt
```

### "Port 8501 already in use"
```powershell
streamlit run app.py --server.port=8502
```

### Dashboard runs slow
```powershell
streamlit cache clear
streamlit run app.py
```

---

## 📈 Demo Data

- **50 vehicles** auto-generated with realistic data
- **4 zones** (downtown, airport, harbor, commercial)  
- **Realistic metrics** (battery %, utilization, idle hours, etc.)
- **Risk scoring** applied automatically

No files to load, no data setup needed. **Just run it.**

---

## 💼 Status

✅ Production Ready  
✅ Tested & Verified  
✅ Zero Dependency Issues  
✅ Deployable on any system with Python 3.8+
