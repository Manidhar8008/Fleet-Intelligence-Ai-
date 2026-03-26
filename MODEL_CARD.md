Model Purpose

This system does not predict asset failure.
It prioritizes assets for preventive operational intervention under uncertainty.

The output is a decision support signal, not an automated action.

Prediction Target

The model estimates the relative risk that an asset will require operational intervention (inspection, repair, or rotation) within a short forward-looking window.

Risk is expressed as a composite score, not a probability.

Signal Construction

The risk score is constructed from three categories of signals:

Asset Health Momentum

Battery level trends (short-term vs long-term averages)

Interpreted as early-warning momentum, not degradation certainty

Utilization Pressure

Recent ride frequency and changes in usage

Represents mechanical and battery stress

Zone Stress

Deployment density at the city / zone level

Captures environmental and operational load

Uncertainty Handling (Critical)

Not all signals are equally reliable at all times.

To account for this:

Signals derived from short temporal windows (e.g., battery trend) are treated as conditionally valid

Signal influence is down-weighted or suppressed when data sufficiency is low

All recommendations are gated by a confidence level (High / Medium / Low)

When confidence is Low, the system defaults to non-invasive actions or no action.

Validation Strategy

Traditional accuracy metrics are not used.

Validation focuses on:

Intervention precision for high-risk assets

Stability of recommendations over time

Coverage balance (avoiding over- or under-flagging)

Evaluation is performed using time-aware validation, ensuring no information leakage from future data.

Known Limitations

Battery health is inferred from proxy measurements

Short-term trends may be noisy in sparse data scenarios

The system does not establish causality

Outputs should be interpreted as risk prioritization, not predictions of failure

Appropriate Use

This model is suitable for:

Preventive maintenance planning

Asset rotation prioritization

Operational monitoring dashboards

It is not suitable for:

Automated decommissioning

Safety-critical decisions

Warranty or compliance enforcement