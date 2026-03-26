Data Quality Report — Mobility Dataset
Purpose

This document explains how raw data was made decision-safe,
not how it was “cleaned for modeling.”

The goal is trust, not perfection.

1. What Was Wrong in the Raw Data

The raw dataset contained issues that would invalidate leadership decisions if left unchecked:

Timestamps stored as strings

Records with impossible values (negative demand, invalid hours)

Inconsistent categorical labels (holiday, functioning day)

Environmental values outside plausible physical ranges

These issues were expected in observational data.

2. What Was Fixed (Contract Enforcement)

The following fixes were applied because they violate non-negotiable invariants:

Converted date fields to true timestamps

Removed records with:

Negative rental counts

Hours outside 0–23

Physically implausible temperatures

Normalized categorical fields to stable, lowercase values

Created time features (day, month, season) for decision analysis

These changes reduce ambiguity without adding assumptions.

3. What Was Explicitly NOT Fixed (And Why)

Some issues were intentionally not corrected:

Missing or unparseable timestamps were not inferred

Outliers caused by extreme but plausible weather were retained

Demand spikes were not smoothed or normalized

Reason:
Imputing or smoothing would manufacture certainty and hide real operational risk.

4. Known Limitations That Remain

No zone-level granularity

No vehicle-specific identifiers

No true trip lifecycle data

These limitations are accepted because this dataset is a proxy for decision reasoning, not production telemetry.

5. Why This Data Is Still Decision-Usable

Despite limitations, the dataset is safe for:

Demand pattern analysis

Weather sensitivity evaluation

Time-based operational risk assessment

It is not suitable for:

Vehicle-level maintenance optimization

Zone-specific regulatory decisions

Using it beyond these bounds would violate the data contract.

Final Principle

Data was modified only when reality was impossible.
Ambiguity was preserved when uncertainty was real.

This preserves trust in downstream decisions.
