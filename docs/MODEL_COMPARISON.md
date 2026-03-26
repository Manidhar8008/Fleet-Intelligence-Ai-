# Model Performance Comparison — Decision Context

This document compares baseline machine learning models used to support
operational decision-making in a micromobility maintenance context.

The goal is not to chase model complexity, but to understand how different
models behave on the same business problem and what trade-offs they introduce
when used inside a real decision system.

---

## Decision Context

- Decision grain: Trip-level
- Objective: Early identification of maintenance risk
- Cost asymmetry: Missing a risky asset is costlier than investigating a false alert
- Priority metric: Recall over precision

Models are evaluated based on how well they support **operational decisions**,
not purely on statistical performance.

---

## Model Performance Summary

| Model               | Accuracy     | Recall (Risk = 1) | ROC AUC | Strength |
|---------------------|--------------|-------------------|---------|----------|
| Logistic Regression | ~0.96–0.97   | High (≈1.0)       | ~0.99   | Stable and consistent risk scoring |
| Decision Tree       | ~0.98        | Moderate (~0.71)  | ~0.86   | Clear rules and interpretability   |

---

## Interpretation (Why these results matter)

### Logistic Regression — Primary Risk Scoring Model

Logistic Regression performs strongly when the objective is to **catch risky assets early**.
Instead of producing hard yes/no decisions, it assigns probability scores, which makes it
useful for ranking assets by risk level.

This behavior is especially valuable in maintenance scenarios where missing a true failure
can lead to higher operational cost than investigating a false alert.

In this project, Logistic Regression consistently shows:
- High recall on risky cases
- Stable performance across samples
- Better ranking quality, reflected in ROC AUC

**Key takeaway:**

> Logistic Regression is best suited as the primary model when early risk
> identification is more important than strict rule enforcement.

---

### Decision Tree — Explainability and Policy Model

Decision Trees answer a different but equally important question: **why** risk is being flagged.

They break decisions into simple, human-readable rules and highlight which features influence
outcomes the most. This makes them valuable for:
- Operational discussions
- Policy validation
- Stakeholder trust

Feature importance analysis indicates:
- Recent usage intensity is the dominant signal
- Battery degradation provides a secondary but meaningful contribution

**Key takeaway:**

> Decision Trees trade some recall for transparency and are best used to
> explain and validate model-driven decisions.

---

## Final Position in the System

Both models are intentionally retained:

- **Logistic Regression** serves as the **primary risk scoring engine**
- **Decision Trees** serve as a **supporting explainability layer**

Predictions alone do not trigger action.
Final decisions are made through explicit business rules applied on top
of model outputs.

This separation ensures:
- Auditability
- Interpretability
- Safe operational use

Model choice is driven by decision context, not leaderboard metrics.
