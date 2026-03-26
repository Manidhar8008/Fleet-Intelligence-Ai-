"""
Production-Grade Fleet Management AI Dashboard
Enterprise SaaS Quality - Real-time Risk Intelligence & Optimization
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from collections import defaultdict, Counter

# Import our production modules
from src.decision_engine import FleetDecisionEngine, VehicleState
from src.data_loader import ProductionDataLoader, DataContract

# ============================================================================
# PAGE CONFIGURATION & THEME
# ============================================================================
st.set_page_config(
    page_title="Fleet Operations AI | Risk Intelligence Dashboard",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
    <style>
    /* Main styling */
    .main {
        padding-top: 2rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Alert styling */
    .alert-critical {
        background-color: #fee;
        border-left: 4px solid #d32f2f;
        padding: 12px;
        border-radius: 4px;
        margin: 8px 0;
    }
    
    .alert-high {
        background-color: #fff3cd;
        border-left: 4px solid #ff9800;
        padding: 12px;
        border-radius: 4px;
        margin: 8px 0;
    }
    
    /* Title styling */
    h1 {
        color: #1a73e8;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    h2 {
        color: #202124;
        border-bottom: 3px solid #1a73e8;
        padding-bottom: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)


# ============================================================================
# DATA LOADING & CACHING
# ============================================================================
@st.cache_data(ttl=300)  # 5-minute cache
def load_fleet_data():
    """Load and score entire fleet"""
    try:
        from src.data_loader import DataSource
        loader = ProductionDataLoader()
        vehicles = loader.load_vehicles(source=DataSource.SAMPLE)
        
        engine = FleetDecisionEngine()
        scored_vehicles = {}
        decisions = {}
        
        for vehicle_id, vehicle_state in vehicles.items():
            decision = engine.score_vehicle(vehicle_state)
            scored_vehicles[vehicle_id] = vehicle_state
            decisions[vehicle_id] = decision
            
        return scored_vehicles, decisions, engine
    except Exception as e:
        st.error(f"❌ Error loading fleet data: {str(e)}")
        return {}, {}, None


@st.cache_data(ttl=300)
def build_fleet_dataframe(scored_vehicles, decisions):
    """Convert fleet data to DataFrame for display"""
    from datetime import datetime
    data = []
    for vehicle_id, decision in decisions.items():
        vs = scored_vehicles[vehicle_id]
        alert_text = decision.alerts[0]['alert_type'] if decision.alerts else 'None'
        # Calculate idle hours from last trip
        idle_hours = 0
        if vs.last_trip_timestamp:
            idle_hours = (datetime.now() - vs.last_trip_timestamp).total_seconds() / 3600
        # Calculate utilization from trips
        utilization = (vs.trips_last_7d / 7.0) * 100 if vs.trips_last_7d > 0 else 0
        data.append({
            'vehicle_id': vehicle_id,
            'risk_score': decision.risk_score,
            'risk_level': decision.risk_level,
            'battery_pct': vs.battery_pct,
            'alert': alert_text,
            'recommendation': decision.recommended_action.name,
            'zone': vs.zone_id,
            'idle_hours': round(idle_hours, 1),
            'utilization': round(utilization, 1),
            'maintenance_due': 'Yes' if vs.failure_count_90d > 0 or vs.maintenance_count_30d > 0 else 'No',
        })
    
    return pd.DataFrame(data).sort_values('risk_score', ascending=False).reset_index(drop=True)


# ============================================================================
# ZONE OPTIMIZATION ENGINE
# ============================================================================
class ZoneOptimizationEngine:
    """AI-powered zone optimization"""
    
    def __init__(self, fleet_df):
        self.fleet_df = fleet_df
        
    def analyze_zone_efficiency(self):
        """Analyze which zones have idle vehicles that should be relocated"""
        zone_stats = defaultdict(lambda: {'total': 0, 'idle': 0, 'avg_battery': 0, 'critical': 0})
        zone_vehicles = defaultdict(list)
        
        for _, row in self.fleet_df.iterrows():
            zone = row['zone']
            zone_stats[zone]['total'] += 1
            zone_stats[zone]['avg_battery'] += row['battery_pct']
            
            if row['risk_level'] == 'CRITICAL':
                zone_stats[zone]['critical'] += 1
            
            # Consider vehicle idle if idle_hours > 8 OR risk_level is LOW (not being used)
            if row['idle_hours'] > 8 or (row['risk_level'] == 'LOW' and row['utilization'] < 20):
                zone_stats[zone]['idle'] += 1
                zone_vehicles[zone].append(row['vehicle_id'])
        
        # Calculate averages
        for zone in zone_stats:
            if zone_stats[zone]['total'] > 0:
                zone_stats[zone]['avg_battery'] /= zone_stats[zone]['total']
        
        # Identify surplus and deficit zones
        recommendations = self._generate_recommendations(zone_stats, zone_vehicles)
        
        return zone_stats, zone_vehicles, recommendations
    
    def _generate_recommendations(self, zone_stats, zone_vehicles):
        """Generate zone rebalancing recommendations"""
        recommendations = []
        
        # Find zones with high idle vehicles (potential sources)
        idle_prone_zones = sorted(
            [(z, s['idle']) for z, s in zone_stats.items() if s['idle'] > 2],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Find zones with high utilization (potential destinations)
        high_demand_zones = sorted(
            [(z, s['critical']) for z, s in zone_stats.items()],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Create rebalancing recommendations
        for source_zone, idle_count in idle_prone_zones[:2]:
            if high_demand_zones:
                dest_zone, _ = high_demand_zones[0]
                if source_zone != dest_zone and idle_count > 0:
                    vehicles_to_move = min(idle_count, 3)
                    recommendations.append({
                        'from_zone': source_zone,
                        'to_zone': dest_zone,
                        'vehicle_count': vehicles_to_move,
                        'reason': f'Move {vehicles_to_move} underutilized vehicles from {source_zone.title()} to {dest_zone.title()} to reduce idle time and optimize utilization'
                    })
        
        return recommendations


# ============================================================================
# INSIGHTS GENERATION ENGINE
# ============================================================================
class InsightsEngine:
    """Generate business insights from fleet data"""
    
    def __init__(self, fleet_df):
        self.fleet_df = fleet_df
        
    def generate_critical_actions(self):
        """Generate top action items"""
        actions = []
        
        # Critical battery
        critical_battery = len(self.fleet_df[
            (self.fleet_df['risk_level'] == 'CRITICAL') & 
            (self.fleet_df['battery_pct'] < 20)
        ])
        if critical_battery > 0:
            actions.append({
                'priority': 'CRITICAL',
                'action': 'Immediate Charging Required',
                'count': critical_battery,
                'detail': f'{critical_battery} vehicles need immediate charging to prevent service downtime'
            })
        
        # Maintenance
        maintenance_due = len(self.fleet_df[self.fleet_df['maintenance_due'] == 'Yes'])
        if maintenance_due > 0:
            actions.append({
                'priority': 'HIGH',
                'action': 'Maintenance Inspection Scheduled',
                'count': maintenance_due,
                'detail': f'{maintenance_due} vehicles require preventive maintenance checks'
            })
        
        # High-risk inspection
        high_risk = len(self.fleet_df[self.fleet_df['risk_level'].isin(['HIGH', 'CRITICAL'])])
        if high_risk > 0:
            actions.append({
                'priority': 'HIGH',
                'action': 'Risk Assessment Required',
                'count': high_risk,
                'detail': f'{high_risk} vehicles flagged for immediate risk mitigation'
            })
        
        # Zone rebalancing
        low_utilization = len(self.fleet_df[self.fleet_df['utilization'] < 20])
        if low_utilization > 3:
            actions.append({
                'priority': 'MEDIUM',
                'action': 'Fleet Rebalancing',
                'count': low_utilization,
                'detail': f'{low_utilization} underutilized vehicles could be relocated'
            })
        
        return actions
    
    def generate_executive_summary(self):
        """Generate executive-level summary"""
        total_vehicles = len(self.fleet_df)
        avg_risk = self.fleet_df['risk_score'].mean()
        critical_count = len(self.fleet_df[self.fleet_df['risk_level'] == 'CRITICAL'])
        alert_count = len(self.fleet_df[self.fleet_df['alert'] != 'None'])
        
        health_status = 'HEALTHY' if avg_risk < 25 else 'CAUTION' if avg_risk < 50 else 'AT_RISK'
        
        return {
            'total_vehicles': total_vehicles,
            'avg_risk_score': round(avg_risk, 1),
            'critical_vehicles': critical_count,
            'active_alerts': alert_count,
            'fleet_health': health_status,
            'critical_percentage': round((critical_count / total_vehicles * 100), 1) if total_vehicles > 0 else 0
        }


# ============================================================================
# MAIN DASHBOARD
# ============================================================================
def main():
    # Load data
    scored_vehicles, decisions, engine = load_fleet_data()
    
    if not decisions:
        st.stop()
    
    fleet_df = build_fleet_dataframe(scored_vehicles, decisions)
    
    # ========================================================================
    # HEADER
    # ========================================================================
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("# 🚲 Fleet Operations AI Dashboard")
        st.markdown("*Real-time Risk Intelligence | Predictive Optimization | Decision Automation*")
    
    with col2:
        st.metric("Last Update", datetime.now().strftime("%H:%M:%S"))
    
    st.divider()
    
    # ========================================================================
    # EXECUTIVE SUMMARY (TOP KPIs)
    # ========================================================================
    insights = InsightsEngine(fleet_df)
    summary = insights.generate_executive_summary()
    
    st.markdown("## 📊 Executive Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Vehicles",
            value=summary['total_vehicles'],
            delta="Active Fleet"
        )
    
    with col2:
        color = "🔴" if summary['avg_risk_score'] > 40 else "🟡" if summary['avg_risk_score'] > 25 else "🟢"
        st.metric(
            label="Avg Risk Score",
            value=f"{summary['avg_risk_score']}/100",
            delta=f"{color} {summary['fleet_health']}",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            label="🚨 Critical Vehicles",
            value=summary['critical_vehicles'],
            delta=f"{summary['critical_percentage']}% of fleet",
            delta_color="off"
        )
    
    with col4:
        st.metric(
            label="⚠️  Active Alerts",
            value=summary['active_alerts'],
            delta="Require Action",
            delta_color="off"
        )
    
    st.divider()
    
    # ========================================================================
    # RISK DISTRIBUTION & INSIGHTS
    # ========================================================================
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📈 Risk Distribution")
        
        risk_counts = fleet_df['risk_level'].value_counts()
        risk_order = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        risk_counts = risk_counts.reindex(risk_order, fill_value=0)
        
        # Create distribution chart
        colors = {'LOW': '#4CAF50', 'MEDIUM': '#FFC107', 'HIGH': '#FF5722', 'CRITICAL': '#D32F2F'}
        fig = px.bar(
            x=risk_counts.index,
            y=risk_counts.values,
            color=risk_counts.index,
            color_discrete_map=colors,
            labels={'x': 'Risk Level', 'y': 'Number of Vehicles'},
            title='Fleet Risk Profile'
        )
        fig.update_layout(
            height=300,
            showlegend=False,
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🎯 Action Items")
        actions = insights.generate_critical_actions()
        
        if actions:
            for action in actions[:3]:
                if action['priority'] == 'CRITICAL':
                    st.markdown(f"""
                    <div class="alert-critical">
                    <strong>🚨 {action['action']}</strong><br>
                    {action['detail']}
                    </div>
                    """, unsafe_allow_html=True)
                elif action['priority'] == 'HIGH':
                    st.markdown(f"""
                    <div class="alert-high">
                    <strong>⚠️ {action['action']}</strong><br>
                    {action['detail']}
                    </div>
                    """, unsafe_allow_html=True)
    
    st.divider()
    
    # ========================================================================
    # FLEET TABLE WITH FILTERS
    # ========================================================================
    st.markdown("### 🚗 Fleet Operations Table")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        high_risk_filter = st.checkbox("🔴 High Risk Only", value=False)
    with col2:
        low_battery_filter = st.checkbox("🔋 Low Battery (<30%)", value=False)
    with col3:
        zone_filter = st.multiselect(
            "📍 Zone Filter",
            options=sorted(fleet_df['zone'].unique()),
            default=None
        )
    
    # Apply filters
    filtered_df = fleet_df.copy()
    
    if high_risk_filter:
        filtered_df = filtered_df[filtered_df['risk_level'].isin(['HIGH', 'CRITICAL'])]
    
    if low_battery_filter:
        filtered_df = filtered_df[filtered_df['battery_pct'] < 30]
    
    if zone_filter:
        filtered_df = filtered_df[filtered_df['zone'].isin(zone_filter)]
    
    # Create styled dataframe
    def style_risk_level(val):
        """Color code risk levels"""
        if val == 'CRITICAL':
            return 'background-color: #ffcdd2; color: #d32f2f; font-weight: bold;'
        elif val == 'HIGH':
            return 'background-color: #fff9c4; color: #ff9800; font-weight: bold;'
        elif val == 'MEDIUM':
            return 'background-color: #fff3e0; color: #f57c00;'
        else:
            return 'background-color: #e8f5e9; color: #388e3c;'
    
    def style_battery(val):
        """Color code battery level"""
        if val < 15:
            return 'background-color: #ffcdd2; font-weight: bold;'
        elif val < 30:
            return 'background-color: #fff9c4; font-weight: bold;'
        elif val < 50:
            return 'background-color: #fff3e0;'
        else:
            return 'background-color: #e8f5e9;'
    
    display_df = filtered_df[[
        'vehicle_id', 'risk_score', 'risk_level', 'battery_pct',
        'alert', 'recommendation', 'zone'
    ]].copy()
    
    display_df = display_df.rename(columns={
        'vehicle_id': '🆔 Vehicle',
        'risk_score': '📊 Risk',
        'risk_level': '⚠️ Level',
        'battery_pct': '🔋 Battery %',
        'alert': '🚨 Alert',
        'recommendation': '💡 Action',
        'zone': '📍 Zone'
    })
    
    styled_df = display_df.style.applymap(
        style_risk_level, subset=['⚠️ Level']
    ).applymap(
        style_battery, subset=['🔋 Battery %']
    )
    
    st.dataframe(styled_df, use_container_width=True, height=400)
    st.caption(f"Showing {len(filtered_df)} of {len(fleet_df)} vehicles")
    
    st.divider()
    
    # ========================================================================
    # CRITICAL VEHICLES ALERT PANEL
    # ========================================================================
    st.markdown("### 🚨 Critical Vehicle Alert Panel")
    
    critical_vehicles = fleet_df[fleet_df['risk_level'] == 'CRITICAL'].nlargest(5, 'risk_score')
    
    if len(critical_vehicles) > 0:
        for idx, (_, vehicle) in enumerate(critical_vehicles.iterrows(), 1):
            with st.container():
                col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
                
                with col1:
                    st.markdown(f"### #{idx}")
                
                with col2:
                    st.markdown(f"""
                    **🆔 {vehicle['vehicle_id']}**
                    
                    Risk: **{vehicle['risk_score']}/100**
                    """)
                
                with col3:
                    st.markdown(f"""
                    🔋 Battery: {vehicle['battery_pct']}%
                    
                    📍 Zone: {vehicle['zone']}
                    """)
                
                with col4:
                    st.markdown(f"""
                    **Action:** {vehicle['recommendation']}
                    """)
                    st.info(vehicle['alert'], icon="⚠️")
    else:
        st.success("✅ No critical vehicles detected!")
    
    st.divider()
    
    # ========================================================================
    # DECISION INSIGHTS BOX
    # ========================================================================
    st.markdown("### 💡 AI Decision Insights")
    
    critical_count = len(fleet_df[fleet_df['risk_level'] == 'CRITICAL'])
    battery_critical = len(fleet_df[
        (fleet_df['risk_level'] == 'CRITICAL') & 
        (fleet_df['battery_pct'] < 20)
    ])
    maintenance_count = len(fleet_df[fleet_df['maintenance_due'] == 'Yes'])
    idle_count = len(fleet_df[fleet_df['idle_hours'] > 8])
    
    insights_text = []
    
    if battery_critical > 0:
        insights_text.append(
            f"🔋 **Charge {battery_critical} vehicles immediately** to prevent service downtime. "
            f"Critical battery depletion risk detected."
        )
    
    if critical_count > 2:
        insights_text.append(
            f"🚨 **Prioritize inspection of {critical_count} high-risk vehicles**. "
            f"AI model recommends preventive intervention within 2 hours."
        )
    
    if maintenance_count > 0:
        insights_text.append(
            f"🔧 **Schedule maintenance for {maintenance_count} vehicles**. "
            f"Predictive maintenance alerts indicate scheduled service due."
        )
    
    if idle_count > 3:
        insights_text.append(
            f"♻️ **{idle_count} vehicles are idle**. "
            f"Recommend rebalancing to high-demand zones (see Zone Optimization below)."
        )
    
    if not insights_text:
        st.success("✅ **Fleet Status: GREEN** - All systems optimal. Continue standard monitoring.")
    else:
        for insight in insights_text:
            st.warning(insight)
    
    st.divider()
    
    # ========================================================================
    # ZONE OPTIMIZATION RECOMMENDATION
    # ========================================================================
    st.markdown("### 🗺️ Zone Optimization Recommendation")
    
    zone_engine = ZoneOptimizationEngine(fleet_df)
    zone_stats, zone_vehicles, rebalancing_recs = zone_engine.analyze_zone_efficiency()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if rebalancing_recs:
            for rec in rebalancing_recs:
                st.success(f"""
                ✅ **Relocation Opportunity**
                
                **Recommendation:** {rec['reason']}
                
                📊 Move {rec['vehicle_count']} vehicles from **{rec['from_zone'].title()}** → **{rec['to_zone'].title()}**
                """)
        else:
            st.info("📊 Fleet distribution is well-balanced. Continue monitoring.")
    
    with col2:
        st.markdown("**Zone Metrics:**")
        zone_summary = []
        for zone in sorted(zone_stats.keys()):
            s = zone_stats[zone]
            zone_summary.append({
                'Zone': zone.title(),
                'Total': s['total'],
                'Idle': s['idle'],
                'Avg Battery': f"{s['avg_battery']:.0f}%"
            })
        
        if zone_summary:
            st.dataframe(
                pd.DataFrame(zone_summary),
                use_container_width=True,
                height=150
            )
    
    st.divider()
    
    # ========================================================================
    # BATTERY ANALYSIS
    # ========================================================================
    st.markdown("### 🔋 Battery Health Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        battery_by_risk = fleet_df.groupby('risk_level')['battery_pct'].mean().sort_values()
        fig = px.bar(
            x=battery_by_risk.index,
            y=battery_by_risk.values,
            color=battery_by_risk.index,
            color_discrete_map={'LOW': '#4CAF50', 'MEDIUM': '#FFC107', 'HIGH': '#FF5722', 'CRITICAL': '#D32F2F'},
            labels={'x': 'Risk Level', 'y': 'Avg Battery %'},
            title='Average Battery by Risk Level'
        )
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        battery_dist = pd.cut(fleet_df['battery_pct'], bins=[0, 20, 50, 75, 100])
        battery_counts = battery_dist.value_counts().sort_index()
        
        fig = px.pie(
            values=battery_counts.values,
            names=['0-20% (Critical)', '20-50% (Low)', '50-75% (Normal)', '75-100% (Good)'],
            title='Battery Distribution',
            color_discrete_sequence=['#d32f2f', '#ff9800', '#ffc107', '#4caf50']
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # ========================================================================
    # UTILIZATION ANALYSIS
    # ========================================================================
    st.markdown("### 📊 Fleet Utilization Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.histogram(
            fleet_df,
            x='utilization',
            nbins=20,
            title='Vehicle Utilization Distribution',
            labels={'utilization': 'Utilization %', 'count': 'Vehicles'}
        )
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        utilization_stats = {
            ' 0-20% (Idle)': len(fleet_df[fleet_df['utilization'] < 20]),
            '20-50% (Low)': len(fleet_df[(fleet_df['utilization'] >= 20) & (fleet_df['utilization'] < 50)]),
            '50-80% (Normal)': len(fleet_df[(fleet_df['utilization'] >= 50) & (fleet_df['utilization'] < 80)]),
            '80-100% (Active)': len(fleet_df[fleet_df['utilization'] >= 80])
        }
        
        fig = px.bar(
            x=list(utilization_stats.keys()),
            y=list(utilization_stats.values()),
            color_discrete_sequence=['#ff9800', '#ffc107', '#8bc34a', '#4caf50'],
            labels={'x': 'Utilization Category', 'y': 'Vehicles'},
            title='Vehicle Utilization Categories'
        )
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # ========================================================================
    # FOOTER
    # ========================================================================
    st.markdown("""
    ---
    
    **Fleet Operations AI Dashboard** | Production Grade Intelligence
    
    *Powered by Advanced Risk Scoring, Predictive Models & Optimization Algorithms*
    
    Last Updated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """
    """)


if __name__ == "__main__":
    main()
