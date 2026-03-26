# Block B — Decision Policy

This section translates model outputs into clear, repeatable decisions.  
The objective is to define **how predictions are used**, not just how models perform.

The decision policy ensures that risk scores lead to consistent operational actions.

---

## Objective

Use machine learning risk scores to:
- Identify vehicles likely to fail in the near term
- Prioritize maintenance actions
- Reduce unplanned downtime and operational cost

The focus is on **early intervention**, not perfect prediction.

---

## Inputs

The decision policy consumes the following model outputs:

- Risk probability score (from Logistic Regression)
- Binary risk flag (supporting signal)
- Feature-level insights (from Decision Tree)

These inputs are generated daily as part of the scoring pipeline.

---

## Risk Segmentation Logic

Vehicles are grouped into three operational buckets based on predicted risk probability:

### High Risk
- Risk probability ≥ 0.70
- Indicates strong likelihood of near-term maintenance issues

**Action:**
- Immediate maintenance inspection
- Priority scheduling
- Manual review by operations team

---

### Medium Risk
- Risk probability between 0.40 and 0.70
- Indicates early warning signals

**Action:**
- Increased monitoring
- Deferred maintenance planning
- Re-score in the next cycle

---

### Low Risk
- Risk probability < 0.40
- No immediate failure indicators

**Action:**
- Continue normal operations
- Standard monitoring cadence

---

## Model Roles in the Policy

### Logistic Regression — Primary Decision Driver

- Used for risk scoring and prioritization
- Optimized for recall to avoid missing failures
- Supports ranking assets by urgency

This model determines **who gets flagged first**.

---

### Decision Tree — Decision Support and Validation

- Used to explain *why* a vehicle was flagged
- Highlights dominant operational drivers
- Supports trust and adoption by field teams

This model explains **why the decision makes sense**.

---

## Why Recall Is Prioritized

In this system, the cost of a missed failure is higher than the cost of a false alert.

Examples:
- Vehicle downtime
- Customer impact
- Emergency maintenance cost

Therefore, the policy intentionally favors models and thresholds that maximize recall, even at the expense of precision.

---

## Policy Guardrails

To prevent overreaction or alert fatigue:

- Risk thresholds are reviewed periodically
- Model outputs are monitored for drift
- Decisions are logged for audit and improvement

This ensures the policy remains stable and business-aligned over time.

---

## Summary

This decision policy connects machine learning outputs to real operational actions.

- Logistic Regression drives risk prioritization
- Decision Trees provide transparency
- Thresholds convert scores into actions

The result is a system that is predictive, explainable, and operationally usable.
