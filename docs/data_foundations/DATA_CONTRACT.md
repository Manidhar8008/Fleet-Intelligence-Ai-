## DATA CONTRACT — Lime Micromobility Decision Dataset
Purpose

---

This data contract defines the canonical structure, semantics, and assumptions of the core trip-level dataset (lime_final.csv) used across analytics, metrics, and decision scenarios in this repository.
The goal is not descriptive reporting, but decision enablement.

---

##1. Dataset Overview

Granularity: One row = one completed trip
Primary Entity: Trip
Source: Public micromobility e-scooter trip data
Row Count: ~200,000 sampled trips
Geography: City-level (Chicago)
Time Coverage: Multi-month historical sample

##2. Entity Model

Core Entities
Entity	Description
Trip	Individual micromobility ride
Zone	Operational area proxy
Time	Start / end timestamps
Economics	Pricing & revenue signals
Conditions	Environmental context (if available)

##3. Column Definitions

Trip Identity & Time
Column	Meaning	Source
trip_id	Unique trip identifier	Raw dataset
start_time	Trip start timestamp	Raw dataset
end_time	Trip end timestamp	Raw dataset
duration_min	Trip duration in minutes	Raw dataset
Location Signals
Column	Meaning	Source
start_lat	Start latitude	Raw dataset
start_lng	Start longitude	Raw dataset
end_lat	End latitude	Raw dataset
end_lng	End longitude	Raw dataset
Economic Signals
Column	Meaning	Source
Trip cost	Base ride cost (pricing rule)	Derived
Discount	Applied discount	Assumed (0)
Invoice	Final charged amount	Derived
Operational Proxies
Column	Meaning	Source
zone_id	Operational zone proxy	Assumed
vehicle_type	Scooter / bike	Assumed
city	City of operation	Fixed
User Proxy
Column	Meaning	Source
User_id	User identifier (anonymized)	Placeholder
User_catgo	Behavioral proxy	Placeholder
Environmental Context
Column	Meaning	Source
temperature	Ambient temperature	Not available
rain	Rain indicator	Not available
wind	Wind speed	Not available

##4. Explicit Assumptions (Important)

Vehicle-level telemetry (vehicle_id, battery %) is not available
Battery health and fleet efficiency are inferred via behavioral proxies
Pricing model is simplified to enable comparative analysis
Dataset is designed for relative insights, not accounting-grade precision

##5. Decisions This Dataset Enables

Identify demand concentration risk
Detect pricing inefficiencies
Highlight operationally volatile zones
Surface abnormal trip behavior
Prioritize areas for deeper telemetry investment

##6. Known Gaps & Future Data Requirements

To move from inference to diagnosis, the following data is required:
Vehicle-level identifiers
Battery telemetry (start %, end %)
Maintenance and downtime logs
Deployment & rebalancing events

This contract is the single source of truth for all downstream analysis.
