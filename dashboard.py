"""
Production Dashboard for Fleet Intelligence

A real-time Streamlit dashboard showing:
- Fleet health metrics
- Risk score distribution
- Critical alerts
- Operational recommendations
- Vehicle tracking & details

Run with: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List

# Import our modules
from decision_engine import (
    FleetDecisionEngine, VehicleState, RiskLevel, 
    AlertType, RecommendationType, FleetDecisionBatch
)
from data_loader import ProductionDataLoader, DataSource, VehicleDataAggregator


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Fleet Intelligence Dashboard",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .critical-alert {
        background-color: #ffcccc;
        padding: 15px;
        border-left: 5px solid #ff0000;
    }
    .warning-alert {
        background-color: #ffffcc;
        padding: 15px;
        border-left: 5px solid #ffaa00;
    }
    .info-alert {
        background-color: #ccffcc;
        padding: 15px;
        border-left: 5px solid #00aa00;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# SESSION STATE & CACHING
# ============================================================================

@st.cache_resource
def get_engine():
    """Get or create decision engine (cached)."""
    return FleetDecisionEngine()

@st.cache_resource
def get_loader():
    """Get or create data loader (cached)."""
    return ProductionDataLoader()

@st.cache_resource
def get_aggregator():
    """Get or create data aggregator (cached)."""
    return VehicleDataAggregator()


@st.cache_data(ttl=300)  # Refresh every 5 minutes
def load_fleet_data(data_source: str, limit: int = 100):
    """Load fleet data with caching."""
    loader = get_loader()
    
    source_enum = DataSource[data_source.upper()]
    vehicles = loader.load_vehicles(source=source_enum, limit=limit)
    
    return vehicles, loader.get_load_stats()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_risk_color(risk_level: RiskLevel) -> str:
    """Get color for risk level."""
    colors = {
        RiskLevel.LOW: "#00aa00",
        RiskLevel.MEDIUM: "#ffaa00",
        RiskLevel.HIGH: "#ff6600",
        RiskLevel.CRITICAL: "#ff0000",
    }
    return colors.get(risk_level, "#gray")


def get_risk_icon(risk_level: RiskLevel) -> str:
    """Get emoji icon for risk level."""
    icons = {
        RiskLevel.LOW: "✅",
        RiskLevel.MEDIUM: "⚠️",
        RiskLevel.HIGH: "🔴",
        RiskLevel.CRITICAL: "🚨",
    }
    return icons.get(risk_level, "")


def format_alert_severity(severity: str) -> str:
    """Format alert severity with emoji."""
    severity_map = {
        'CRITICAL': '🚨 CRITICAL',
        'WARNING': '⚠️ WARNING',
        'INFO': 'ℹ️ INFO',
    }
    return severity_map.get(severity, severity)


def render_metric_card(label: str, value: str, subtext: str = ""):
    """Render a metric card."""
    col1 = st.container()
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="margin: 0; color: #1f77b4; font-size: 14px;">{label}</h3>
            <h2 style="margin: 5px 0; font-size: 28px;">{value}</h2>
            <p style="margin: 5px 0; color: #666; font-size: 12px;">{subtext}</p>
        </div>
        """, unsafe_allow_html=True)


# ============================================================================
# PAGE LAYOUT
# ============================================================================

def main():
    """Main dashboard application."""
    
    # Header
    st.title("🚲 Fleet Intelligence Dashboard")
    st.markdown("**Real-time vehicle risk scoring and operational recommendations**")
    
    # Sidebar configuration
    st.sidebar.title("Configuration")
    
    data_source = st.sidebar.selectbox(
        "Data Source",
        ["Sample", "CSV"],
        help="Select the data source for vehicle telemetry"
    )
    
    fleet_size = st.sidebar.slider(
        "Fleet Size",
        min_value=10,
        max_value=500,
        value=50,
        step=10,
        help="Number of vehicles to load and analyze"
    )
    
    refresh_data = st.sidebar.button("🔄 Refresh Data", use_container_width=True)
    
    # Load data
    with st.spinner("Loading vehicle data..."):
        vehicles, load_stats = load_fleet_data(data_source, limit=fleet_size)
    
    if not vehicles:
        st.error("Failed to load vehicle data. Please check your configuration.")
        return
    
    # Score fleet
    with st.spinner("Scoring vehicles..."):
        engine = get_engine()
        batch_scorer = FleetDecisionBatch(engine)
        decisions = batch_scorer.score_fleet(list(vehicles.values()))
        summary = batch_scorer.get_summary_metrics(decisions)
    
    # ========================================================================
    # SECTION 1: FLEET HEALTH OVERVIEW
    # ========================================================================
    
    st.markdown("---")
    st.markdown("## 📊 Fleet Health Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_metric_card(
            "Total Vehicles",
            str(summary['total_vehicles']),
            f"{len([d for d in decisions.values() if d.risk_level == RiskLevel.LOW])} healthy"
        )
    
    with col2:
        critical_count = summary['risk_distribution']['CRITICAL']
        render_metric_card(
            "Critical Alerts",
            str(critical_count),
            "Requires immediate action"
        )
    
    with col3:
        avg_score = summary['avg_risk_score']
        status = "Healthy" if avg_score < 40 else "Caution" if avg_score < 70 else "Alert"
        render_metric_card(
            "Avg Risk Score",
            f"{avg_score:.0f}",
            f"Fleet Status: {status}"
        )
    
    with col4:
        idle_count = len([
            d for d in decisions.values()
            if d.recommended_action == RecommendationType.REBALANCE
        ])
        render_metric_card(
            "Idle Vehicles",
            str(idle_count),
            "Candidates for rebalancing"
        )
    
    # ========================================================================
    # SECTION 2: RISK DISTRIBUTION
    # ========================================================================
    
    st.markdown("---")
    st.markdown("## 🎯 Risk Distribution")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Risk distribution pie chart
        risk_data = summary['risk_distribution']
        colors_map = [
            get_risk_color(RiskLevel.LOW),
            get_risk_color(RiskLevel.MEDIUM),
            get_risk_color(RiskLevel.HIGH),
            get_risk_color(RiskLevel.CRITICAL),
        ]
        
        fig = go.Figure(data=[go.Pie(
            labels=list(risk_data.keys()),
            values=list(risk_data.values()),
            marker=dict(colors=colors_map),
            textinfo="label+value+percent",
        )])
        fig.update_layout(height=400, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Risk Breakdown")
        for level, count in risk_data.items():
            pct = count / summary['total_vehicles'] * 100 if summary['total_vehicles'] > 0 else 0
            st.metric(
                f"{get_risk_icon(RiskLevel[level])} {level}",
                f"{count}",
                f"{pct:.0f}%"
            )
    
    # ========================================================================
    # SECTION 3: RECOMMENDED ACTIONS
    # ========================================================================
    
    st.markdown("---")
    st.markdown("## 📋 Recommended Actions")
    
    col1, col2, col3 = st.columns(3)
    
    actions_data = summary['recommended_actions']
    
    with col1:
        inspect_count = actions_data.get('INSPECT', 0)
        st.metric("🔍 Inspect", str(inspect_count), "Preventive maintenance")
    
    with col2:
        repair_count = actions_data.get('REPAIR', 0)
        st.metric("🔧 Repair", str(repair_count), "Corrective maintenance")
    
    with col3:
        balance_count = actions_data.get('REBALANCE', 0)
        st.metric("📍 Rebalance", str(balance_count), "Fleet optimization")
    
    # ========================================================================
    # SECTION 4: CRITICAL ALERTS
    # ========================================================================
    
    st.markdown("---")
    st.markdown("## 🚨 Critical Alerts")
    
    critical_decisions = [
        d for d in decisions.values()
        if d.risk_level == RiskLevel.CRITICAL
    ]
    
    if critical_decisions:
        for decision in critical_decisions[:10]:
            st.warning(
                f"**{decision.vehicle_id}** - {decision.reasoning}",
                icon="⚠️"
            )
            
            if decision.alerts:
                for alert in decision.alerts[:2]:
                    alert_text = f"[{alert['severity']}] {alert['message']}"
                    if alert['severity'] == 'CRITICAL':
                        st.error(alert_text, icon="🚨")
                    else:
                        st.warning(alert_text, icon="⚠️")
    else:
        st.success("No critical alerts at this time.", icon="✅")
    
    # ========================================================================
    # SECTION 5: ALERT BREAKDOWN
    # ========================================================================
    
    st.markdown("---")
    st.markdown("## 📊 Alert Types")
    
    alert_data = summary['alert_breakdown']
    
    if alert_data:
        # Create bar chart
        alert_df = pd.DataFrame({
            'Alert Type': list(alert_data.keys()),
            'Count': list(alert_data.values())
        })
        
        fig = px.bar(
            alert_df,
            x='Alert Type',
            y='Count',
            color='Count',
            color_continuous_scale=['#90EE90', '#FFD700', '#FF6347'],
        )
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No alerts generated in current dataset.")
    
    # ========================================================================
    # SECTION 6: VEHICLE DETAILS TABLE
    # ========================================================================
    
    st.markdown("---")
    st.markdown("## 🚲 Vehicle Details")
    
    # Create dataframe for display
    vehicle_data = []
    
    for vehicle_id, decision in decisions.items():
        vehicle = vehicles[vehicle_id]
        
        vehicle_data.append({
            'Vehicle ID': vehicle_id,
            'Type': vehicle.vehicle_type.upper(),
            'Battery': f"{vehicle.battery_pct:.0f}%",
            'Risk Level': decision.risk_level.value,
            'Risk Score': f"{decision.risk_score:.0f}",
            'Action': decision.recommended_action.value,
            'Zone': vehicle.zone_id,
            'Trips (7d)': vehicle.trips_last_7d,
            'Idle (hrs)': f"{(datetime.now() - vehicle.last_trip_timestamp).total_seconds() / 3600:.1f}" if vehicle.last_trip_timestamp else "Unknown",
        })
    
    df_vehicles = pd.DataFrame(vehicle_data)
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        risk_filter = st.multiselect(
            "Filter by Risk Level",
            options=["LOW", "MEDIUM", "HIGH", "CRITICAL"],
            default=["CRITICAL", "HIGH"],
            help="Show only vehicles with selected risk levels"
        )
    
    with col2:
        action_filter = st.multiselect(
            "Filter by Recommended Action",
            options=df_vehicles['Action'].unique().tolist(),
        )
    
    with col3:
        zone_filter = st.multiselect(
            "Filter by Zone",
            options=df_vehicles['Zone'].unique().tolist(),
        )
    
    # Apply filters
    df_filtered = df_vehicles.copy()
    
    if risk_filter:
        df_filtered = df_filtered[df_filtered['Risk Level'].isin(risk_filter)]
    
    if action_filter:
        df_filtered = df_filtered[df_filtered['Action'].isin(action_filter)]
    
    if zone_filter:
        df_filtered = df_filtered[df_filtered['Zone'].isin(zone_filter)]
    
    # Display table with styling
    st.dataframe(
        df_filtered,
        use_container_width=True,
        height=400,
    )
    
    # ========================================================================
    # SECTION 7: FLEET STATISTICS
    # ========================================================================
    
    st.markdown("---")
    st.markdown("## 📈 Fleet Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_battery = df_vehicles['Battery'].str.rstrip('%').astype(float).mean()
        st.metric("Avg Battery Level", f"{avg_battery:.0f}%")
    
    with col2:
        total_trips_7d = df_vehicles['Trips (7d)'].sum()
        st.metric("Total Trips (7d)", f"{total_trips_7d:,}")
    
    with col3:
        idle_threshold = 4
        idle_vehicles = len(df_vehicles[df_vehicles['Idle (hrs)'].str.replace('Unknown', '9999').astype(float) > idle_threshold])
        st.metric("Idle Vehicles (>4h)", f"{idle_vehicles}")
    
    # ========================================================================
    # SECTION 8: ZONE METRICS
    # ========================================================================
    
    st.markdown("---")
    st.markdown("## 📍 Zone Analysis")
    
    aggregator = get_aggregator()
    zone_metrics = aggregator.compute_zone_metrics(vehicles)
    
    # Create zone dataframe
    zone_data = []
    for zone, metrics in zone_metrics.items():
        zone_data.append({
            'Zone': zone,
            'Vehicles': metrics['count'],
            'Available': metrics['available'],
            'Avg Battery': f"{metrics['avg_battery']:.0f}%",
            'Utilization': f"{metrics['utilization_pct']:.0f}%",
            'Avg Trips': f"{metrics['avg_trips_7d']:.1f}",
        })
    
    df_zones = pd.DataFrame(zone_data)
    st.dataframe(df_zones, use_container_width=True)
    
    # ========================================================================
    # FOOTER
    # ========================================================================
    
    st.markdown("---")
    st.markdown("""
    **Fleet Intelligence Dashboard** | Powered by Decision Engine v1.0  
    Last updated: {} | Data source: {} | Vehicles analyzed: {}
    """.format(
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        data_source,
        len(vehicles)
    ))


# ============================================================================
# RUN APP
# ============================================================================

if __name__ == "__main__":
    main()
