Data Engineering – Making Data Usable and Trustworthy

Purpose
This folder contains the logic that transforms raw micromobility data into clean, consistent, analytics-ready datasets.

The goal of this layer is trust:
- Ensure data is complete and consistent
- Handle missing or malformed records
- Standardize schemas and timestamps
- Prepare data for downstream analytics and modeling

What lives here
- Data cleaning and preprocessing functions
- Validation and sanity checks
- Feature preparation required by analytics and ML layers
- Schema definitions or expectations

How this is used
This layer sits between raw ingestion and analytics.
Downstream consumers should be able to rely on this data without re-checking basic quality issues.

Notes
Data quality problems are handled here once, instead of repeatedly in analytics or models.
This reduces ambiguity and prevents silent errors from propagating.
