# Decision Authority

## Authoritative Output

The single authoritative output of this system is:

data/Decision/asset_decision_final.csv

All operational decisions, interpretations, and visualizations
must derive from this table.

No other file, model output, or visualization is considered a
source of truth.

---

## What This Table Represents

Each row represents a post-trip decision for an asset based on:
- factual trip and asset data
- derived operational signals
- model-supported risk indicators
- explicit business rules

The table is designed to be:
- auditable
- explainable
- reproducible

---

## What This Table Is NOT

- It is not raw data
- It is not a model prediction dump
- It is not a dashboard extract
- It is not statistically representative of production systems

It is a **decision artifact**, not an analytics artifact.

---

## Authority Hierarchy

1. Decision Table (authoritative)
2. Evaluation Reports (context)
3. Visual Artifacts (explanation)
4. Dashboards (communication)
5. Models (supporting logic)

If conflicts arise, the decision table takes precedence.

---

## Change Policy

Any change to:
- schema
- grain
- decision logic

must be explicitly documented and versioned.

Silent changes are not allowed.
