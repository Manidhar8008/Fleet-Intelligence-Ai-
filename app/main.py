"""
Fleet Intelligence AI - Main Streamlit Application

Professional SaaS MVP for real-time fleet risk & optimization
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Import our modules
from utils.config import config
from utils.logger import app_logger
from core.data_loader import load_csv_file, generate_demo_data, load_sample_csv
from core.preprocessing import clean_fleet_data
from core.feature_engineering import engineer_features, get_feature_statistics
from models.risk_model import risk_model
from core.decision_engine import decision_engine
from core.insights_engine import insights_engine

# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title=config.APP_NAME,
    page_icon=config.APP_ICON,
    layout=config.LAYOUT,
    initial_sidebar_state="expanded"
)

# ============================================================================
# STYLING
# ============================================================================
st.markdown("""
    <style>
    /* Main styling */
    .main { padding: 20px; }
    
    /* Headers */
    h1 { color: #0D4A8F; font-size: 2.8rem; font-weight: 700; margin-bottom: 5px; }
    h2 { color: #1A5FA0; border-bottom: 3px solid #0D4A8F; padding-bottom: 10px; margin: 30px 0 15px 0; }
    h3 { color: #2B6BA8; font-size: 1.3rem; }
    
    /* Subtitle */
    .subtitle { color: #666; font-size: 1.1rem; font-weight: 500; margin: 10px 0 20px 0; }
    
    /* Cards */
    .metric-card { background: #F5F7FA; border-radius: 8px; padding: 20px; margin: 10px 0; border-left: 4px solid #0D4A8F; }
    .insight-card { background: #EBF4FF; border-left: 4px solid #2196F3; padding: 15px; margin: 10px 0; border-radius: 6px; }
    .action-card { background: #FFF3E0; border-left: 4px solid #FF9800; padding: 15px; margin: 10px 0; border-radius: 6px; }
    .critical-card { background: #FFEBEE; border-left: 4px solid #D32F2F; padding: 15px; margin: 10px 0; border-radius: 6px; }
    
    /* Status badges */
    .status-ok { background: #4CAF50; color: white; padding: 5px 10px; border-radius: 4px; font-weight: 600; }
    .status-warning { background: #FF9800; color: white; padding: 5px 10px; border-radius: 4px; font-weight: 600; }
    .status-critical { background: #D32F2F; color: white; padding: 5px 10px; border-radius: 4px; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE
# ============================================================================
if 'fleet_data' not in st.session_state:
    st.session_state.fleet_data = None
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'data_source' not in st.session_state:
    st.session_state.data_source = "demo"

# ============================================================================
# MAIN APP
# ============================================================================
def main():
    # Header
    st.markdown(f"# {config.APP_NAME}")
    st.markdown(f"<p class='subtitle'>{config.APP_SUBTITLE}</p>", unsafe_allow_html=True)
    
    # Sidebar - Data Upload
    st.sidebar.markdown("## 📤 Data Input")
    
    upload_mode = st.sidebar.radio(
        "Choose data source:",
        ["Demo Data", "Upload CSV", "Use Sample"],
        key="data_mode"
    )
    
    fleet_data = None
    data_source_name = ""
    
    if upload_mode == "Upload CSV":
        st.sidebar.markdown("### Upload Your Fleet Data")
        uploaded_file = st.sidebar.file_uploader(
            "Choose CSV file",
            type=['csv'],
            help="Required columns: vehicle_id, battery, utilization, zone"
        )
        
        if uploaded_file is not None:
            fleet_data, status_msg = load_csv_file(uploaded_file)
            st.sidebar.info(status_msg)
            data_source_name = "Uploaded CSV"
        else:
            st.sidebar.info("Please upload a CSV file to proceed")
    
    elif upload_mode == "Use Sample":
        if st.sidebar.button("📥 Load Sample Data", use_container_width=True):
            fleet_data = load_sample_csv()
            if fleet_data is None:
                fleet_data = generate_demo_data()
                st.sidebar.info("Sample file not found, using demo data instead")
            else:
                st.sidebar.success("Sample data loaded successfully")
            data_source_name = "Sample CSV"
    
    else:  # Demo Data
        if st.sidebar.button("🎯 Generate Demo Fleet", use_container_width=True):
            fleet_data = generate_demo_data()
            st.sidebar.success("Demo data loaded successfully")
            data_source_name = "Demo Data"
    
    # Auto-load demo if no data yet
    if fleet_data is None and st.session_state.fleet_data is None:
        fleet_data = generate_demo_data()
        data_source_name = "Demo Data"
    elif fleet_data is None:
        fleet_data = st.session_state.fleet_data
        data_source_name = st.session_state.data_source or "Previous Data"
    
    if fleet_data is not None:
        # Store in session
        st.session_state.fleet_data = fleet_data
        st.session_state.data_source = data_source_name
        
        # Process data through pipeline
        with st.spinner("Processing fleet data..."):
            # Feature engineering
            processed_df = engineer_features(fleet_data)
            
            # Risk scoring
            processed_df = risk_model.calculate_risk_scores(processed_df)
            
            # Decision generation
            processed_df = decision_engine.generate_decisions(processed_df)
            
            st.session_state.processed_data = processed_df
        
        # Display data info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Data Source", data_source_name)
        with col2:
            st.metric("🚗 Vehicles Analyzed", len(processed_df))
        with col3:
            st.metric("⏰ Last Updated", datetime.now().strftime("%H:%M:%S"))
        
        st.divider()
        
        # ====================================================================
        # KPI SECTION
        # ====================================================================
        st.markdown("## 📊 Fleet Performance KPIs")
        
        metrics = decision_engine.get_summary_metrics(processed_df)
        
        kpi_cols = st.columns(4)
        
        with kpi_cols[0]:
            st.metric(
                "Total Fleet",
                f"{metrics['total_vehicles']} vehicles",
                delta="Active",
                delta_color="off"
            )
        
        with kpi_cols[1]:
            status_color = "🔴" if metrics['high_risk_pct'] > 15 else "🟡" if metrics['high_risk_pct'] > 5 else "🟢"
            st.metric(
                "High-Risk %",
                f"{metrics['high_risk_pct']}%",
                delta=f"{metrics['high_risk_count']} vehicles",
                delta_color="off"
            )
        
        with kpi_cols[2]:
            daily_loss = metrics['estimated_daily_loss']
            st.metric(
                "Est. Daily Loss",
                f"₹{daily_loss:,.0f}",
                delta="If not addressed",
                delta_color="inverse"
            )
        
        with kpi_cols[3]:
            opportunity = len(processed_df[processed_df['utilization'] < 20]) * 50
            st.metric(
                "Optimization Opportunity",
                f"₹{opportunity:,.0f}/day",
                delta="Potential recovery",
                delta_color="off"
            )
        
        st.divider()
        
        # ====================================================================
        # AI INSIGHTS
        # ====================================================================
        st.markdown("## 🤖 AI Insights & Recommendations")
        
        insights = insights_engine.generate_insights(processed_df)
        
        for i, insight in enumerate(insights, 1):
            st.markdown(f"<div class='insight-card'>{insight}</div>", unsafe_allow_html=True)
        
        st.divider()
        
        # ====================================================================
        # RISK DISTRIBUTION
        # ====================================================================
        st.markdown("## 📈 Risk Distribution")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            risk_dist = risk_model.get_risk_distribution(processed_df)
            risk_order = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
            colors_map = {'LOW': '#4CAF50', 'MEDIUM': '#FFC107', 'HIGH': '#FF5722', 'CRITICAL': '#D32F2F'}
            
            fig = px.bar(
                x=[risk_order[i] for i in range(len(risk_order))],
                y=[risk_dist.get(level, 0) for level in risk_order],
                color=[risk_order[i] for i in range(len(risk_order))],
                color_discrete_map=colors_map,
                labels={'x': 'Risk Level', 'y': 'Number of Vehicles'},
                title='Fleet Risk Profile'
            )
            fig.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Risk Summary")
            for level in risk_order:
                count = risk_dist.get(level, 0)
                pct = (count / len(processed_df) * 100) if len(processed_df) > 0 else 0
                emoji = "🟢" if level == "LOW" else "🟡" if level == "MEDIUM" else "🟠" if level == "HIGH" else "🔴"
                st.write(f"{emoji} **{level}**: {count} ({pct:.0f}%)")
        
        st.divider()
        
        # ====================================================================
        # CRITICAL ACTIONS
        # ====================================================================
        critical_actions = decision_engine.get_critical_actions(processed_df)
        
        if critical_actions:
            st.markdown("## 🚨 Critical Actions Needed")
            for action in critical_actions:
                st.markdown(f"<div class='action-card'>{action}</div>", unsafe_allow_html=True)
            st.divider()
        
        # ====================================================================
        # CHARTS
        # ====================================================================
        st.markdown("## 📊 Operational Analytics")
        
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            # Battery distribution
            battery_dist = pd.cut(processed_df['battery'], bins=[0, 20, 50, 75, 100])
            battery_counts = battery_dist.value_counts().sort_index()
            
            fig = px.pie(
                values=battery_counts.values,
                names=['Critical (0-20%)', 'Low (20-50%)', 'Normal (50-75%)', 'Good (75-100%)'],
                color_discrete_sequence=['#D32F2F', '#FF9800', '#FFC107', '#4CAF50'],
                title='Battery Level Distribution'
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        with chart_col2:
            # Utilization distribution
            util_stats = {
                'Idle (0-20%)': len(processed_df[processed_df['utilization'] < 20]),
                'Low (20-50%)': len(processed_df[(processed_df['utilization'] >= 20) & (processed_df['utilization'] < 50)]),
                'Normal (50-80%)': len(processed_df[(processed_df['utilization'] >= 50) & (processed_df['utilization'] < 80)]),
                'Active (80-100%)': len(processed_df[processed_df['utilization'] >= 80]),
            }
            
            fig = px.bar(
                x=list(util_stats.keys()),
                y=list(util_stats.values()),
                color_discrete_sequence=['#FF9800', '#FFC107', '#8BC34A', '#4CAF50'],
                title='Fleet Utilization',
                labels={'y': 'Vehicles'}
            )
            fig.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # ====================================================================
        # FLEET TABLE
        # ====================================================================
        st.markdown("## 🚗 Fleet Operations Detail")
        
        # Filters
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        with filter_col1:
            risk_filter = st.multiselect(
                "Risk Level",
                ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'],
                default=['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
            )
        
        with filter_col2:
            battery_filter = st.slider("Min Battery %", 0, 100, 0)
        
        with filter_col3:
            zone_options = processed_df['zone'].unique().tolist()
            zone_filter = st.multiselect(
                "Zone",
                zone_options,
                default=zone_options
            )
        
        # Apply filters
        filtered_df = processed_df[
            (processed_df['risk_level'].isin(risk_filter)) &
            (processed_df['battery'] >= battery_filter) &
            (processed_df['zone'].isin(zone_filter))
        ]
        
        # Display table
        display_cols = ['vehicle_id', 'risk_score', 'risk_level', 'battery', 'utilization', 'action', 'estimated_loss_per_day', 'zone']
        if all(col in filtered_df.columns for col in display_cols):
            display_df = filtered_df[display_cols].copy()
            display_df.columns = ['Vehicle ID', 'Risk Score', 'Risk Level', 'Battery %', 'Utilization %', 'Action', 'Daily Loss (₹)', 'Zone']
            
            st.dataframe(
                display_df.style.format({
                    'Risk Score': '{:.1f}',
                    'Battery %': '{:.1f}',
                    'Utilization %': '{:.1f}',
                    'Daily Loss (₹)': '{:.0f}'
                }),
                use_container_width=True,
                height=400
            )
        
        st.caption(f"Showing {len(filtered_df)} of {len(processed_df)} vehicles")
        
        st.divider()
        
        # ====================================================================
        # ZONE ANALYSIS
        # ====================================================================
        st.markdown("## 📍 Zone Analysis")
        
        zone_summary = insights_engine.get_zone_summary(processed_df)
        
        st.dataframe(
            zone_summary.style.format({
                'Avg Battery': '{:.1f}',
                'Avg Utilization': '{:.1f}',
                'Avg Risk': '{:.1f}',
                'Daily Loss (₹)': '{:.0f}'
            }),
            use_container_width=True
        )
        
        # ====================================================================
        # FOOTER
        # ====================================================================
        st.divider()
        st.markdown("""
        ---
        **Fleet Intelligence AI** | Production-Ready SaaS MVP  
        Reduce downtime. Predict failures. Optimize fleet operations.  
        
        *Data Source:* {}  |  *Last Updated:* {}
        """.format(data_source_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

if __name__ == "__main__":
    main()
