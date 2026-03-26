🌐 Lime IoT Decision Platform - Data Contracts
Overview
Lime IoT Decision Platform defines standardized data contracts for vehicle telemetry processing. These contracts transform raw IoT signals into decision-ready tables for operations, finance, and leadership teams.
​

Data Tables
1. Raw Telemetry Table ⭐ INPUT LAYER
File: data/raw/lime_vehicles_sample.csv
Source: Historical / scraped IoT telemetry (simulated)
Purpose: Unprocessed vehicle signals

Key Columns:

Field	Type	Description
vehicle_id	String	Unique asset identifier
timestamp	Datetime	Telemetry capture time
city	String	Deployment city
battery_level	Integer	Battery percentage (0–100)
rides_today	Integer	Number of rides in last day
distance_km	Float	Total distance traveled
Notes:

Data is incomplete and non-decision-ready

Used only as signal input

Example:
data/raw/lime_vehicles_sample.csv

2. Asset Decision Table (v1) ⭐ CORE OUTPUT
File: data/generated/asset_decision_table_v1.csv
Built by: scripts/build_asset_decision_table.py
Purpose: Single source of truth for asset-level operational decisions

Key Columns:

Field	Type	Description
battery_health_index	Float	Proxy = battery_level / 100
utilization_score	Float	Proxy = rides_today
distance_per_ride	Float	Usage intensity proxy
recommended_action	String	{continue, repair, decommission}
Audience: Ops, Finance, Leadership

3. Asset Proxy Features Table (v1)
File: data/generated/asset_proxy_features_v1.csv
Built by: scripts/build_asset_proxy_features.py
Purpose: Explain decisions; support trend analysis

Key Columns:

All proxy metrics from decision table

Zone/stress/intensity indicators

No direct decisions

Audience: Analysts, reviewers

4. Asset Trend Summary (v1)
File: data/generated/asset_trend_summary_v1.csv
Built by: scripts/build_asset_trend_summary.py
Purpose: Aggregate signals for strategic review

Audience: Leadership, strategy

Pipeline Structure
text
data/
├── raw/lime_vehicles_sample.csv          # Raw IoT input
├── generated/
│   ├── asset_decision_table_v1.csv       # Operational decisions ⭐
│   ├── asset_proxy_features_v1.csv       # Analysis features
│   └── asset_trend_summary_v1.csv        # Strategic aggregates
└── scripts/
    ├── build_asset_decision_table.py     # Decision logic
    ├── build_asset_proxy_features.py     # Feature engineering
    └── build_asset_trend_summary.py      # Aggregation
Key Benefits
Decision Ready: Direct operational actions from raw telemetry

Traceable: Full lineage from raw → decision

Scalable: Modular scripts for new cities/assets

Audience-Tailored: Separate tables for ops vs. strategy

Best Practices
✅ Validate raw data completeness before processing
✅ Version all generated tables (v1 → v2)
✅ Document proxy formulas in code comments
✅ Use consistent naming across tables
