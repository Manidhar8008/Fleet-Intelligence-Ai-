"""
Minimal Fleet Dashboard - Clean & Simple

Shows:
- 50 vehicles with risk scores and alerts
- Filters: High risk, Low battery
- Summary metrics

Run: streamlit run dashboard_minimal.py
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from src.decision_engine import FleetDecisionEngine, FleetDecisionBatch, RiskLevel
from src.data_loader import ProductionDataLoader, DataSource


st.set_page_config(page_title="Fleet Dashboard", layout="wide", initial_sidebar_state="collapsed")

# ============================================================================
# STYLING
# ============================================================================

st.markdown("""
<style>
    .metric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .metric-title { font-size: 12px; opacity: 0.9; }
    .metric-value { font-size: 32px; font-weight: bold; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# LOAD DATA & SCORE
# ============================================================================

@st.cache_data(ttl=300)
def load_and_score_fleet():
    """Load vehicles and score them."""
    loader = ProductionDataLoader()
    vehicles = loader.load_vehicles(source=DataSource.SAMPLE, limit=50)
    
    engine = FleetDecisionEngine()
    batch = FleetDecisionBatch(engine)
    decisions = batch.score_fleet(list(vehicles.values()))
    
    return vehicles, decisions


vehicles, decisions = load_and_score_fleet()

# ============================================================================
# PREPARE DATA FOR DISPLAY
# ============================================================================

data = []
for vehicle_id, decision in decisions.items():
    vehicle = vehicles[vehicle_id]
    
    # Get primary alert
    alert = ""
    if decision.alerts:
        alert = decision.alerts[0]['message']
    
    data.append({
        'Vehicle ID': vehicle_id,
        'Risk Score': f"{decision.risk_score:.0f}",
        'Risk Level': decision.risk_level.value,
        'Battery': f"{vehicle.battery_pct:.0f}%",
        'Alert': alert,
        'Recommendation': decision.recommended_action.value,
        'Zone': vehicle.zone_id,
    })

df = pd.DataFrame(data)

# ============================================================================
# FILTERS
# ============================================================================

st.title("🚲 Fleet Dashboard")

col1, col2 = st.columns(2)

with col1:
    high_risk_only = st.checkbox("🔴 High Risk Only", value=False)

with col2:
    low_battery_only = st.checkbox("🔋 Low Battery Only", value=False)

# Apply filters
df_filtered = df.copy()

if high_risk_only:
    df_filtered = df_filtered[df_filtered['Risk Level'].isin(['HIGH', 'CRITICAL'])]

if low_battery_only:
    df_filtered = df_filtered[df_filtered['Battery'].str.rstrip('%').astype(int) < 30]

# ============================================================================
# SUMMARY METRICS
# ============================================================================

st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Vehicles", len(df))

with col2:
    avg_risk = df['Risk Score'].astype(int).mean()
    st.metric("Avg Risk Score", f"{avg_risk:.0f}/100")

with col3:
    alert_count = len([a for a in df['Alert'] if a])
    st.metric("Active Alerts", alert_count)

with col4:
    critical_count = len(df[df['Risk Level'] == 'CRITICAL'])
    st.metric("🚨 Critical", critical_count)

# ============================================================================
# VEHICLE TABLE
# ============================================================================

st.markdown("---")
st.subheader(f"Vehicles ({len(df_filtered)} shown)")

# Color function for risk level
def color_risk(val):
    if val == 'CRITICAL':
        return 'background-color: #ffcccc'
    elif val == 'HIGH':
        return 'background-color: #ffe6cc'
    elif val == 'MEDIUM':
        return 'background-color: #ffffcc'
    else:
        return 'background-color: #ccffcc'

# Display table
st.dataframe(
    df_filtered.style.applymap(color_risk, subset=['Risk Level']),
    use_container_width=True,
    height=400
)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
