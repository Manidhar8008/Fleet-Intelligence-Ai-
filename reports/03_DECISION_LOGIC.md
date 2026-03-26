# Decision Logic — From Prediction to Action

## Problem
Model predictions alone do not create operational value.
Actions must be derived through explicit business rules.

## Inputs
- Trip-level factual data
- Derived risk indicators
- Model prediction scores

## Decision Rules (Simplified)
- High risk + low battery health → schedule maintenance
- Repeated short trips + low margin → pricing or rebalancing review
- High utilization + healthy asset → continue operation

## Why Rules Are Explicit
- Enables auditability
- Prevents silent automation errors
- Allows business teams to challenge assumptions

## Outcome
The final output is a single authoritative decision table that
recommends actions per asset after each trip.

This separation between prediction and decision is intentional
and mirrors real production systems.
