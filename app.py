"""
🚲 Fleet Operations AI Dashboard - PRODUCTION
Cleaned up, simplified, production-ready Streamlit app
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from collections import defaultdict

# Import our production modules
from src.decision_engine import FleetDecisionEngine, VehicleState, RiskLevel, RecommendationType
from src.data_loader import ProductionDataLoader, DataSource


# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="Fleet Operations AI",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    h1 { color: #1a73e8; }
    .metric-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   color: white; padding: 20px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)


# ============================================================================
# DEMO DATA GENERATOR (NO FILE DEPENDENCIES)
# ============================================================================
def generate_demo_fleet(num_vehicles: int = 50) -> dict:
    """Generate realistic demo vehicles without loading files"""
    
    vehicles = {}
    zones = ['downtown', 'airport', 'harbor', 'commercial']
    
    np.random.seed(42)  # Reproducible
    
    for i in range(num_vehicles):
        vehicle_id = f"vehicle_{i:04d}"
        
        # Random but realistic values
        battery = np.random.uniform(10, 100)
        trips_7d = np.random.randint(0, 50)
        failure_count = np.random.randint(0, 3)
        
        # Realistic timestamps
        last_trip = datetime.now() - timedelta(hours=np.random.randint(1, 200))
        
        vehicle = VehicleState(
            vehicle_id=vehicle_id,
            vehicle_type=np.random.choice(['scooter', 'bike']),
            latitude=float(np.random.uniform(37.7, 37.8)),
            longitude=float(np.random.uniform(-122.5, -122.4)),
            zone_id=np.random.choice(zones),
            battery_pct=battery,
            is_reserved=False,
            is_disabled=False,
            trips_last_24h=np.random.randint(0, 10),
            trips_last_7d=trips_7d,
            trips_last_30d=max(trips_7d, np.random.randint(trips_7d, trips_7d+50)),
            last_trip_timestamp=last_trip,
            last_charge_timestamp=datetime.now() - timedelta(hours=np.random.randint(1, 48)),
            days_deployed=np.random.randint(30, 365),
            maintenance_count_30d=np.random.randint(0, 2),
            failure_count_90d=failure_count,
            is_under_repair=False,
            zone_demand=np.random.uniform(0.3, 0.9),
            zone_supply=np.random.uniform(0.3, 0.9),
            timestamp=datetime.now()
        )
        
        vehicles[vehicle_id] = vehicle
    
    return vehicles


# ============================================================================
# CACHED DATA LOADING
# ============================================================================
@st.cache_data(ttl=300)
def load_and_score_fleet():
    """Load demo data and score with decision engine"""
    
    # Generate demo fleet
    vehicles = generate_demo_fleet(50)
    
    # Score all vehicles
    engine = FleetDecisionEngine()
    decisions = {}
    
    for vehicle_id, vehicle_state in vehicles.items():
        decision = engine.score_vehicle(vehicle_state)
        decisions[vehicle_id] = decision
    
    return vehicles, decisions, engine


@st.cache_data(ttl=300)
def build_dataframe(vehicles, decisions):
    """Convert to DataFrame for display"""
    data = []
    
    for vehicle_id, decision in decisions.items():
        vs = vehicles[vehicle_id]
        
        # Calculate metrics
        idle_hours = 0
        if vs.last_trip_timestamp:
            idle_hours = (datetime.now() - vs.last_trip_timestamp).total_seconds() / 3600
        
        utilization = (vs.trips_last_7d / 7.0) * 100 if vs.trips_last_7d > 0 else 0
        alert_text = decision.alerts[0]['alert_type'] if decision.alerts else 'None'
        
        data.append({
            'vehicle_id': vehicle_id,
            'risk_score': round(decision.risk_score, 1),
            'risk_level': decision.risk_level.name,
            'battery_pct': round(vs.battery_pct, 1),
            'alert': alert_text,
            'recommendation': decision.recommended_action.name,
            'zone': vs.zone_id,
            'idle_hours': round(idle_hours, 1),
            'utilization': round(utilization, 1),
        })
    
    return pd.DataFrame(data).sort_values('risk_score', ascending=False).reset_index(drop=True)


# ============================================================================
# MAIN APP
# ============================================================================
def main():
    # Load data
    vehicles, decisions, engine = load_and_score_fleet()
    fleet_df = build_dataframe(vehicles, decisions)
    
    # ========================================================================
    # HEADER
    # ========================================================================
    st.markdown("# 🚲 Fleet Operations AI")
    st.markdown("*Real-time Risk Intelligence | Smart Optimization*")
    st.divider()
    
    # ========================================================================
    # KPIs
    # ========================================================================
    st.markdown("## 📊 Executive Summary")
    
    total = len(fleet_df)
    avg_risk = fleet_df['risk_score'].mean()
    critical = len(fleet_df[fleet_df['risk_level'] == 'CRITICAL'])
    alerts = len(fleet_df[fleet_df['alert'] != 'None'])
    health = 'HEALTHY' if avg_risk < 25 else 'CAUTION' if avg_risk < 50 else 'AT_RISK'
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Vehicles", total)
    with col2:
        st.metric("Avg Risk", f"{avg_risk:.0f}/100", health)
    with col3:
        st.metric("🚨 Critical", critical)
    with col4:
        st.metric("⚠️ Alerts", alerts)
    
    st.divider()
    
    # ========================================================================
    # RISK DISTRIBUTION CHART
    # ========================================================================
    st.markdown("### 📈 Risk Distribution")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        risk_counts = fleet_df['risk_level'].value_counts()
        risk_order = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        risk_counts = risk_counts.reindex(risk_order, fill_value=0)
        
        colors = {'LOW': '#4CAF50', 'MEDIUM': '#FFC107', 'HIGH': '#FF5722', 'CRITICAL': '#D32F2F'}
        
        fig = px.bar(
            x=risk_counts.index,
            y=risk_counts.values,
            color=risk_counts.index,
            color_discrete_map=colors,
            title='Fleet Risk Profile'
        )
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col1:
        st.markdown("**Distribution:**")
        for level in risk_order:
            count = risk_counts.get(level, 0)
            pct = (count / total * 100) if total > 0 else 0
            st.write(f"🟢 {level}: {count} ({pct:.0f}%)" if level == 'LOW' else 
                    f"🟡 {level}: {count} ({pct:.0f}%)" if level == 'MEDIUM' else
                    f"🟠 {level}: {count} ({pct:.0f}%)" if level == 'HIGH' else
                    f"🔴 {level}: {count} ({pct:.0f}%)")
    
    st.divider()
    
    # ========================================================================
    # FLEET TABLE
    # ========================================================================
    st.markdown("### 🚗 Fleet Operations")
    
    col1, col2 = st.columns(2)
    with col1:
        high_risk_filter = st.checkbox("🔴 High Risk Only")
    with col2:
        low_battery_filter = st.checkbox("🔋 Low Battery (<30%)")
    
    # Apply filters
    filtered_df = fleet_df.copy()
    if high_risk_filter:
        filtered_df = filtered_df[filtered_df['risk_level'].isin(['HIGH', 'CRITICAL'])]
    if low_battery_filter:
        filtered_df = filtered_df[filtered_df['battery_pct'] < 30]
    
    # Display table
    display_cols = ['vehicle_id', 'risk_score', 'risk_level', 'battery_pct', 'alert', 'recommendation', 'zone']
    st.dataframe(
        filtered_df[display_cols],
        use_container_width=True,
        height=300
    )
    st.caption(f"Showing {len(filtered_df)} of {total} vehicles")
    
    st.divider()
    
    # ========================================================================
    # AI INSIGHTS
    # ========================================================================
    st.markdown("### 💡 AI Decision Insights")
    
    critical_battery = len(fleet_df[(fleet_df['risk_level'] == 'CRITICAL') & (fleet_df['battery_pct'] < 20)])
    high_risk_veh = len(fleet_df[fleet_df['risk_level'].isin(['HIGH', 'CRITICAL'])])
    maintenance_due = len(fleet_df[fleet_df['recommendation'] == 'REPAIR'])
    idle_count = len(fleet_df[fleet_df['idle_hours'] > 8])
    
    insights = []
    
    if critical_battery > 0:
        insights.append(f"🔋 **Charge {critical_battery} vehicles immediately** - CRITICAL battery risk")
    
    if high_risk_veh > 2:
        insights.append(f"🚨 **Inspect {high_risk_veh} high-risk vehicles** - Action needed within 2 hours")
    
    if maintenance_due > 0:
        insights.append(f"🔧 **Schedule maintenance for {maintenance_due} vehicles** - Preventive care overdue")
    
    if idle_count > 3:
        insights.append(f"♻️ **Rebalance {idle_count} idle vehicles** - Move to high-demand zones")
    
    if not insights:
        st.success("✅ **Fleet Status: GREEN** - All systems optimal")
    else:
        for insight in insights:
            st.warning(insight)
    
    st.divider()
    
    # ========================================================================
    # BATTERY ANALYSIS
    # ========================================================================
    st.markdown("### 🔋 Battery Health")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.histogram(
            fleet_df,
            x='battery_pct',
            nbins=15,
            title='Battery Distribution',
            labels={'battery_pct': 'Battery %'}
        )
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.write("**Battery Stats:**")
        st.write(f"Min: {fleet_df['battery_pct'].min():.0f}%")
        st.write(f"Max: {fleet_df['battery_pct'].max():.0f}%")
        st.write(f"Avg: {fleet_df['battery_pct'].mean():.0f}%")
        st.write(f"Median: {fleet_df['battery_pct'].median():.0f}%")
        
        # Critical batteries
        critical_batt = len(fleet_df[fleet_df['battery_pct'] < 20])
        if critical_batt > 0:
            st.error(f"⚠️ {critical_batt} vehicles < 20%")
    
    st.divider()
    
    # ========================================================================
    # UTILIZATION ANALYSIS
    # ========================================================================
    st.markdown("### 📊 Fleet Utilization")
    
    util_stats = {
        'Idle (0-20%)': len(fleet_df[fleet_df['utilization'] < 20]),
        'Low (20-50%)': len(fleet_df[(fleet_df['utilization'] >= 20) & (fleet_df['utilization'] < 50)]),
        'Normal (50-80%)': len(fleet_df[(fleet_df['utilization'] >= 50) & (fleet_df['utilization'] < 80)]),
        'Active (80-100%)': len(fleet_df[fleet_df['utilization'] >= 80]),
    }
    
    fig = px.bar(
        x=list(util_stats.keys()),
        y=list(util_stats.values()),
        color_discrete_sequence=['#ff9800', '#ffc107', '#8bc34a', '#4caf50'],
        title='Utilization Categories'
    )
    fig.update_layout(height=300, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # ========================================================================
    # FOOTER
    # ========================================================================
    st.markdown("""
    ---
    **Fleet Operations AI Dashboard** | Production Grade
    
    Last Updated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """
    """)


if __name__ == "__main__":
    main()
