# System Overview — Lime IoT Decision Platform

## Purpose
This system converts raw micromobility trip and telemetry data into
repeatable, auditable operational decisions.

The focus is not model complexity, but decision reliability under
real-world constraints such as noisy data, incomplete telemetry,
and operational trade-offs.

## What This System Does
- Ingests and cleans trip-level mobility data
- Enforces data contracts and invariants
- Generates decision-ready tables at trip granularity
- Uses simple, explainable models to support decisions
- Outputs recommended operational actions per asset

## What This System Does NOT Do
- It does not claim statistical representativeness
- It does not optimize for leaderboard metrics
- It does not rely on dashboards for decision-making

## Core Design Principles
- One authoritative decision table
- Explicit data contracts
- Deterministic pipeline stages
- Explainability over complexity

This structure mirrors how early-stage applied ML systems are built
inside mobility and operations-focused companies.
