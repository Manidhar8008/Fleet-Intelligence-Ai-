###Hypothesis 1 — Utilization accelerates battery degradation
Business question
Do heavily used vehicles degrade faster than lightly used vehicles, even when average battery level looks acceptable?
This question matters because:
High-utilization assets generate revenue


But they may silently accumulate long-term damage


Late detection leads to sudden downtime and revenue loss

Null hypothesis (H₀)
There is no statistically significant difference in battery health between high-utilization and low-utilization vehicles.

Alternative hypothesis (H₁)
High-utilization vehicles show significantly worse battery health compared to low-utilization vehicles, indicating accelerated degradation.

Data used
Asset-level aggregated table

Metrics:
battery_health_index (proxy for long-term health)
rides_today or utilization proxy
Raw event-level data is intentionally excluded to avoid noise and leakage.

Grouping strategy
Vehicles are segmented into:
High utilization group: top 25% by rides per day

Low utilization group: bottom 25% by rides per day

Quartiles are chosen to:
Reduce sensitivity to outliers

Create interpretable, stable cohorts

Statistical test selection
Mann–Whitney U test (non-parametric)
Reasoning:
Battery health distributions are not assumed to be normal

Operational data often contains skew and outliers

The test compares medians rather than means, aligning better with decision thresholds

Validation approach
To ensure robustness:
Effect size is evaluated alongside statistical significance

The test is repeated with alternative cutoffs (top/bottom 20%, 30%)

Directional consistency is required before acting on results

A statistically significant result without meaningful effect size does not trigger intervention.

Decision implication
If H₁ is supported:
High-utilization assets enter proactive inspection or rotation queues

Thresholds for “continue operation” are tightened for these assets

If H₀ is not rejected:
Utilization alone is insufficient as a degradation signal


Decisions rely more heavily on trend-based indicators

Known limitations
Battery health is a proxy, not a physical measurement

Ride aggressiveness and terrain are not explicitly modeled

Environmental factors may partially explain degradation

These limitations are explicitly acknowledged to avoid overconfidence.

###HYPOTHESIS 2 — TREND-BASED EARLY WARNING
I’ll write this with you now.
Business question
Can deteriorating trends predict asset risk earlier than static thresholds?
Static thresholds answer:
“Is it bad now?”
Trends answer:
“Will it become bad soon?”
Operations care far more about the second.

Null hypothesis (H₀)
Short-term battery and utilization trends do not provide additional predictive signal beyond current battery level.

Alternative hypothesis (H₁)
Assets showing negative battery trends or increasing utilization trends have a higher likelihood of requiring intervention, even if current battery levels appear acceptable.

Data used
Asset-level time-windowed features:

7-day average battery level
30-day average battery level

Utilization trend (slope)


Raw events are aggregated to prevent leakage.

Trend construction (this is where your idea fits)
Battery trend = (7-day avg − 30-day avg)

Utilization trend = change in rides per day
These are derived signals, not raw truths.

Statistical test / evaluation logic
Compare intervention rates between:

Negative-trend assets
Stable or improving assets

Use non-parametric tests or effect-size comparisons

Decision implication
If H₁ is supported:
Assets with degrading trends enter early inspection

Thresholds become dynamic, not static

This reduces:
Sudden failures

Revenue shocks

Emergency maintenance costs

Known limitations
Trend windows are heuristic

Seasonality may distort short windows

Trends are probabilistic, not deterministic


