# Production Readiness Checklist

This checklist defines the criteria for considering this system
complete and production-ready in a portfolio context.

---

## Data

- [x] Raw data is immutable
- [x] Processed data is reproducible
- [x] Data contracts are defined and versioned
- [x] Decision grain is explicitly documented

---

## Decision Logic

- [x] Single authoritative decision table exists
- [x] Decision rules are explicit and explainable
- [x] Predictions do not directly trigger actions
- [x] Business logic is separated from models

---

## Models

- [x] Baseline models evaluated and compared
- [x] Model trade-offs documented
- [x] Evaluation reports persisted
- [x] Explainability supported

---

## Visuals & Communication

- [x] Decision-aligned visual artifacts exist
- [x] Static stakeholder dashboard provided
- [x] Visuals derive from decision-ready data only

---

## Reproducibility

- [x] Scripts generate artifacts deterministically
- [x] File naming reflects data stages
- [x] Authority and ownership are documented

---

## Out of Scope (Intentional)

- Live dashboards
- Automated retraining
- Real-time data ingestion
- Infrastructure orchestration

These are excluded by design to keep the system focused
on decision logic and explainability.
