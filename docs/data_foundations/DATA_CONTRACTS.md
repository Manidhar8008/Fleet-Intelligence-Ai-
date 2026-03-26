1. Trips Dataset
What this dataset represents

Each row represents a completed or attempted customer ride.

What decisions depend on it

Demand forecasting

Zone performance evaluation

Revenue per vehicle analysis

Peak vs off-peak capacity planning

What happens if this data lies

Fleet is deployed to the wrong zones

Demand is overestimated → idle vehicles & wasted ops cost

Demand is underestimated → stockouts & customer dissatisfaction

Revenue projections become meaningless

What must always be true (Invariants)

A trip cannot exist without a zone

A trip must reference exactly one vehicle

Start time < End time

Trip duration > 0

Distance ≥ 0

A trip cannot overlap with another trip for the same vehicle

2. Vehicles Dataset
What this dataset represents

Each row represents a physical scooter or bike in the fleet.

What decisions depend on it

Maintenance scheduling

Battery replacement cycles

Utilization optimization

Decommissioning vs redeployment

What happens if this data lies

Healthy vehicles get retired too early

Broken vehicles stay in circulation

Battery failures appear “random”

Cost-per-ride metrics become untrustworthy

What must always be true (Invariants)

Vehicle ID is globally unique

Battery percentage ∈ [0, 100]

Battery % must not increase during a trip

A vehicle cannot be “active” in two zones at once

Vehicle status must be one of:

active

charging

maintenance

retired

3. Zones Dataset
What this dataset represents

Each row represents a geofenced operational area where rides are allowed.

What decisions depend on it

Fleet allocation per zone

Pricing adjustments

Zone expansion or contraction

Policy & regulatory compliance

What happens if this data lies

Vehicles get deployed where riding is restricted

Zone-level metrics become misleading

Leadership optimizes the wrong geography

Regulatory risk increases

What must always be true (Invariants)

A zone must map to exactly one city

Zone boundaries must not overlap within the same city

A zone must have at least one valid trip to be considered “active”

Zone IDs must be stable over time

A trip must reference a valid zone ID

4. Weather Dataset
What this dataset represents

Each row represents environmental conditions at a given time and location.

What decisions depend on it

Demand suppression modeling

Staffing & rebalancing plans

Safety thresholds for vehicle availability

Forecast adjustment logic

What happens if this data lies

Demand drops are misattributed to product issues

Weather-driven risk is ignored

Forecast models overfit noise

Ops teams respond too late to real conditions

What must always be true (Invariants)

Weather timestamp must align with trip timestamp windows

Temperature must be within physically plausible bounds

Rainfall and snowfall cannot both spike unrealistically

Weather data must never be null for prediction windows

Weather must map to a valid city or zone
