# Model Comparison — Decision Support Models

## Objective
The goal of modeling in this system is not prediction accuracy alone,
but early identification of operational risk at the trip level.

Models are evaluated based on their usefulness for decision-making,
not theoretical optimality.

## Models Evaluated
### Logistic Regression
- Strength: High recall for risky scenarios
- Behavior: Conservative, flags issues early
- Trade-off: May over-flag low-risk cases

### Decision Tree
- Strength: Clear decision boundaries
- Behavior: More selective, fewer false positives
- Trade-off: Misses some early risk signals

## Decision Rationale
Logistic Regression is preferred when early intervention is critical.
Decision Trees are useful for explaining thresholds to stakeholders.

Both models are retained to support different operational contexts.
