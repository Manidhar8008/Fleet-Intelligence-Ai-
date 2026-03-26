# 🌐 Lime GBFS API - Complete Guide

## Overview
Lime provides **real-time vehicle location data** through the General Bikeshare Feed 
Specification (GBFS) API. This guide documents everything you need to collect and 
process Lime's micromobility data.

## API Endpoints

### Base URL
https://data.lime.bike/api/partners/v1/gbfs/{city}

text

### Available Endpoints

#### 1. System Information
**Endpoint:** `/system_information.json`
**Purpose:** Static information about the system
**Example:** 
https://data.lime.bike/api/partners/v1/gbfs/seattle/system_information.json

text

#### 2. Free Bike Status ⭐ PRIMARY DATA SOURCE
**Endpoint:** `/free_bike_status.json`
**Purpose:** Real-time location of all available vehicles
**Update Frequency:** Real-time (updated every 30 seconds)
**Example:**
https://data.lime.bike/api/partners/v1/gbfs/seattle/free_bike_status.json

text

## Sample Response Structure

{
"last_updated": 1699460400,
"data": {
"bikes": [
{
"bike_id": "lime_e8a9e3c8f2",
"lat": 47.606209,
"lon": -122.332071,
"is_reserved": false,
"is_disabled": false,
"jump_vehicle_type": "electric_scooter",
"jump_ebike_battery_level": "85%"
}
]
}
}

text

## Key Data Fields

| Field | Type | Description |
|-------|------|-------------|
| `bike_id` | String | Unique vehicle identifier |
| `lat` | Float | Latitude (GPS coordinate) |
| `lon` | Float | Longitude (GPS coordinate) |
| `is_reserved` | Boolean | Whether vehicle is reserved |
| `is_disabled` | Boolean | Whether vehicle is disabled |
| `jump_vehicle_type` | String | "electric_scooter" or "electric_bike" |
| `jump_ebike_battery_level` | String | Battery level (e.g., "85%") |

## Data Collection Plan

### Collection Strategy
- **Frequency:** Every 5 minutes
- **Daily collections:** 288 times/day
- **Expected vehicles:** 200-500 per collection
- **Daily records:** ~57,600-144,000 data points

## Analysis Opportunities

### 1. Demand Forecasting
Predict vehicle demand by location and time

### 2. Battery Analytics
Optimize battery management and maintenance

### 3. Fleet Optimization
Improve rebalancing and resource allocation

### 4. Quantitative Modeling
Apply GARCH, VaR, and portfolio optimization

## Best Practices
✅ Use 5+ minute collection intervals  
✅ Include User-Agent header  
✅ Handle errors gracefully  
✅ Validate data before processing  

