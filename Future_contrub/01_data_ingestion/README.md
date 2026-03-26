Data Ingestion – Bringing Raw Data Into the System

Purpose
This folder contains scripts responsible for fetching or exporting raw micromobility data used in the project.

The goal of this layer is reliability and simplicity:
- Get data from the source
- Store it locally in a reproducible format
- Avoid premature transformation or assumptions

What lives here
- Lightweight scripts that export or fetch raw telemetry data
- Sample data exporters used for demos and testing
- Simple command-line interfaces for generating local datasets

How this is used
The outputs of this layer are treated as raw inputs.
They are passed downstream to the data engineering layer for cleaning, validation, and transformation.

Notes
This layer intentionally avoids business logic and analytics.
Keeping ingestion simple makes the rest of the system easier to reason about and debug.
