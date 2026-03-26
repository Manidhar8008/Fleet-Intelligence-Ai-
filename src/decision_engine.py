"""
Production Decision Engine for IoT Fleet Intelligence

Purpose:
    Core business logic for real-time vehicle risk scoring and recommendations.
    This is the authoritative decision-making module.

Key Components:
    - Risk Scoring: Composite risk model (health, utilization, environment)
    - Idle Detection: Identifies vehicles not generating revenue
    - Relocation Logic: Recommends vehicle movements based on demand
    - Alert Generation: Escalates critical situations
    - Explainability: Provides audit trail for all decisions

Usage:
    from decision_engine import FleetDecisionEngine, VehicleState
    
    engine = FleetDecisionEngine()
    decision = engine.score_vehicle(vehicle_state)
"""

import logging
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import numpy as np
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & CONSTANTS
# ============================================================================

class RiskLevel(Enum):
    """Risk categorization for decision policy."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertType(Enum):
    """Alert categories for escalation."""
    BATTERY_CRITICAL = "BATTERY_CRITICAL"
    IDLE_TIMEOUT = "IDLE_TIMEOUT"
    MULTIPLE_FAILURES = "MULTIPLE_FAILURES"
    ZONE_OVERSTOCK = "ZONE_OVERSTOCK"
    MAINTENANCE_DUE = "MAINTENANCE_DUE"


class RecommendationType(Enum):
    """Operational recommendation types."""
    INSPECT = "INSPECT"
    ROTATE = "ROTATE"
    REBALANCE = "REBALANCE"
    REPAIR = "REPAIR"
    DECOMMISSION = "DECOMMISSION"
    MONITOR = "MONITOR"


# Risk Thresholds (configurable in production)
RISK_THRESHOLDS = {
    "battery_critical_pct": 15,  # Battery < 15% is critical
    "battery_low_pct": 30,  # Battery < 30% is low
    "idle_alert_hours": 24,  # Alert if idle > 24h
    "idle_warning_hours": 4,  # Flag if idle > 4h
    "zone_overstock_percentile": 75,  # Top 25% zones are overstocked
}

# Signal Weights (tuned for business impact)
SIGNAL_WEIGHTS = {
    "battery_health": 0.40,
    "utilization_stress": 0.35,
    "zone_pressure": 0.15,
    "maintenance_history": 0.10,
}

# Confidence Thresholds (based on data sufficiency)
CONFIDENCE_THRESHOLDS = {
    "high": 14,  # Days of data required for HIGH confidence
    "medium": 7,  # Days of data required for MEDIUM confidence
}


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class VehicleState:
    """Current state of a vehicle - input to decision engine."""
    vehicle_id: str
    vehicle_type: str  # 'scooter' or 'bike'
    
    # Location & Status
    latitude: float
    longitude: float
    zone_id: str
    
    # Battery & Energy
    battery_pct: float  # Current battery %
    
    # Location & Status (continued)
    is_reserved: bool = False
    is_disabled: bool = False
    
    # Battery (continued)
    battery_pct_prev_day: Optional[float] = None  # Previous day battery
    battery_pct_prev_week: Optional[float] = None  # Week-ago battery
    
    # Trip Activity
    trips_last_24h: int = 0
    trips_last_7d: int = 0
    trips_last_30d: int = 0
    distance_last_24h: float = 0.0  # km
    distance_last_7d: float = 0.0
    
    # Time Signals
    last_trip_timestamp: Optional[datetime] = None
    last_charge_timestamp: Optional[datetime] = None
    days_deployed: int = 0  # Days since first deployment
    
    # Maintenance & History
    maintenance_count_30d: int = 0
    failure_count_90d: int = 0
    is_under_repair: bool = False
    
    # Zone Context (metadata for business logic)
    zone_demand: float = 0.5  # 0-1 scale of zone demand
    zone_supply: float = 0.5  # 0-1 scale of zone supply (1=overstock)
    
    # Metadata
    timestamp: datetime = None  # When this data was collected
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class RiskSignals:
    """Individual risk signals that contribute to composite score."""
    battery_decline_rate: float  # % decline per day
    battery_trend: str  # 'improving', 'stable', 'declining'
    utilization_intensity: float  # 0-1, higher = more stress
    utilization_trend: str  # 'increasing', 'stable', 'decreasing'
    idle_hours: float  # Hours since last trip
    zone_pressure: float  # 0-1, higher = overstocked
    maintenance_pressure: float  # 0-1 based on history
    data_freshness_days: float  # Days of data available


@dataclass
class Decision:
    """Output of decision engine - action to take."""
    vehicle_id: str
    risk_level: RiskLevel
    risk_score: float  # 0-100
    confidence: str  # HIGH, MEDIUM, LOW
    recommended_action: RecommendationType
    reasoning: str  # Human-readable explanation
    
    # Root Cause Analysis
    primary_drivers: List[str]  # Top 3 risk factors
    
    # Optional fields
    signals: RiskSignals = None
    alerts: List[Dict] = None
    decision_id: str = None
    timestamp: datetime = None
    model_version: str = "1.0.0"
    
    def __post_init__(self):
        if self.decision_id is None:
            self.decision_id = f"DEC_{datetime.now().strftime('%Y%m%d%H%M%S')}_{np.random.randint(1000, 9999)}"
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.alerts is None:
            self.alerts = []
    
    def to_dict(self) -> Dict:
        """Convert to JSON-serializable dictionary."""
        return {
            'vehicle_id': self.vehicle_id,
            'risk_level': self.risk_level.value,
            'risk_score': round(self.risk_score, 2),
            'confidence': self.confidence,
            'primary_drivers': self.primary_drivers,
            'recommended_action': self.recommended_action.value,
            'reasoning': self.reasoning,
            'alerts': self.alerts,
            'decision_id': self.decision_id,
            'timestamp': self.timestamp.isoformat(),
            'model_version': self.model_version,
        }


# ============================================================================
# CORE DECISION ENGINE
# ============================================================================

class FleetDecisionEngine:
    """
    Production decision engine for vehicle risk scoring and recommendations.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize decision engine with optional custom config.
        
        Args:
            config: Optional dictionary with custom thresholds/weights
        """
        self.config = config or {}
        self.risk_thresholds = {**RISK_THRESHOLDS, **self.config.get('risk_thresholds', {})}
        self.signal_weights = {**SIGNAL_WEIGHTS, **self.config.get('signal_weights', {})}
        self.confidence_thresholds = {**CONFIDENCE_THRESHOLDS, **self.config.get('confidence_thresholds', {})}
        self.logger = logger
        self.logger.info("FleetDecisionEngine initialized")
    
    def score_vehicle(self, vehicle: VehicleState) -> Decision:
        """
        Main entry point: Score a vehicle and generate decision.
        
        Args:
            vehicle: Current vehicle state
            
        Returns:
            Decision object with risk score and recommendations
        """
        # Validate input data
        self._validate_vehicle_state(vehicle)
        
        # Extract risk signals
        signals = self._extract_signals(vehicle)
        
        # Calculate composite risk score
        risk_score, drivers = self._calculate_risk_score(signals, vehicle)
        
        # Determine risk level
        risk_level = self._map_score_to_level(risk_score, vehicle)
        
        # Assess confidence
        confidence = self._assess_confidence(signals, vehicle)
        
        # Generate alerts
        alerts = self._generate_alerts(vehicle, signals, risk_level)
        
        # Recommend action
        recommended_action = self._recommend_action(risk_level, vehicle, signals)
        
        # Generate explainable reasoning
        reasoning = self._generate_reasoning(risk_level, signals, alerts, vehicle)
        
        # Construct decision
        decision = Decision(
            vehicle_id=vehicle.vehicle_id,
            risk_level=risk_level,
            risk_score=risk_score,
            confidence=confidence,
            primary_drivers=drivers,
            signals=signals,
            recommended_action=recommended_action,
            reasoning=reasoning,
            alerts=alerts,
        )
        
        self.logger.info(f"Vehicle {vehicle.vehicle_id}: {risk_level.value} risk, "
                        f"Score={risk_score:.1f}, Action={recommended_action.value}")
        
        return decision
    
    # ========================================================================
    # SIGNAL EXTRACTION
    # ========================================================================
    
    def _extract_signals(self, vehicle: VehicleState) -> RiskSignals:
        """Extract risk signals from vehicle state."""
        
        # Battery Health Signals
        battery_decline_rate = self._calculate_battery_decline(vehicle)
        battery_trend = self._classify_battery_trend(vehicle)
        
        # Utilization Signals
        utilization_intensity = self._calculate_utilization_intensity(vehicle)
        utilization_trend = self._classify_utilization_trend(vehicle)
        
        # Idle Signals
        idle_hours = self._calculate_idle_hours(vehicle)
        
        # Zone Pressure
        zone_pressure = self._calculate_zone_pressure(vehicle)
        
        # Maintenance Pressure
        maintenance_pressure = self._calculate_maintenance_pressure(vehicle)
        
        # Data Freshness
        data_age = self._calculate_data_freshness(vehicle)
        
        return RiskSignals(
            battery_decline_rate=battery_decline_rate,
            battery_trend=battery_trend,
            utilization_intensity=utilization_intensity,
            utilization_trend=utilization_trend,
            idle_hours=idle_hours,
            zone_pressure=zone_pressure,
            maintenance_pressure=maintenance_pressure,
            data_freshness_days=data_age,
        )
    
    def _calculate_battery_decline(self, vehicle: VehicleState) -> float:
        """Calculate rate of battery percentage decline per day."""
        if vehicle.battery_pct_prev_week is None:
            return 0.0
        
        decline = vehicle.battery_pct_prev_week - vehicle.battery_pct
        days_elapsed = max(7, 1)  # Assume 7 days
        
        return max(0, decline / days_elapsed)  # % decline per day
    
    def _classify_battery_trend(self, vehicle: VehicleState) -> str:
        """Classify battery trend direction."""
        if vehicle.battery_pct_prev_day is None:
            return "unknown"
        
        daily_change = vehicle.battery_pct - vehicle.battery_pct_prev_day
        
        if daily_change > 2:  # Gaining > 2%
            return "improving"
        elif daily_change < -2:  # Declining > 2%
            return "declining"
        else:
            return "stable"
    
    def _calculate_utilization_intensity(self, vehicle: VehicleState) -> float:
        """Calculate mechanical/battery stress from trip frequency."""
        # Normalize trips to 0-1 scale
        # High intensity = more than 10 trips per day
        trips_per_day = vehicle.trips_last_7d / 7.0 if vehicle.trips_last_7d > 0 else 0
        intensity = min(1.0, trips_per_day / 10.0)
        
        return intensity
    
    def _classify_utilization_trend(self, vehicle: VehicleState) -> str:
        """Classify utilization trend."""
        if vehicle.trips_last_7d == 0 or vehicle.trips_last_30d == 0:
            return "unknown"
        
        ratio = vehicle.trips_last_7d / (vehicle.trips_last_30d / 4.3)  # Normalize to weeks
        
        if ratio > 1.2:
            return "increasing"
        elif ratio < 0.8:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_idle_hours(self, vehicle: VehicleState) -> float:
        """Calculate hours since last trip."""
        if vehicle.last_trip_timestamp is None:
            return 24 * 30  # Default to 30 days if unknown
        
        idle_time = datetime.now() - vehicle.last_trip_timestamp
        return idle_time.total_seconds() / 3600  # Return hours
    
    def _calculate_zone_pressure(self, vehicle: VehicleState) -> float:
        """Calculate demand/supply imbalance in zone."""
        # Simple formula: high supply relative to demand = high pressure
        # This would integrate with real demand forecasting in production
        
        if vehicle.zone_supply == 0:
            return 0.0
        
        # Pressure = supply / demand (normalized 0-1)
        pressure = vehicle.zone_supply / (vehicle.zone_demand + 0.1)
        return min(1.0, pressure)
    
    def _calculate_maintenance_pressure(self, vehicle: VehicleState) -> float:
        """Calculate maintenance urgency from history."""
        # Combine maintenance count and failure rate
        maintenance_score = min(1.0, vehicle.maintenance_count_30d / 3.0)
        failure_score = min(1.0, vehicle.failure_count_90d / 2.0)
        
        return (maintenance_score * 0.6 + failure_score * 0.4)
    
    def _calculate_data_freshness(self, vehicle: VehicleState) -> float:
        """Calculate days of historical data available."""
        # In production, this would check data warehouse
        # For now, use deployed days as proxy
        return float(vehicle.days_deployed)
    
    # ========================================================================
    # RISK SCORING
    # ========================================================================
    
    def _calculate_risk_score(self, signals: RiskSignals, 
                            vehicle: VehicleState) -> Tuple[float, List[str]]:
        """
        Calculate composite risk score 0-100 using weighted signal model.
        
        Returns:
            (risk_score, list_of_primary_drivers)
        """
        
        scores = {}
        
        # Battery Health Component (40%)
        battery_score = self._score_battery_health(signals, vehicle)
        scores['battery'] = battery_score
        
        # Utilization Stress Component (35%)
        util_score = self._score_utilization_stress(signals, vehicle)
        scores['utilization'] = util_score
        
        # Zone Pressure Component (15%)
        zone_score = self._score_zone_pressure(signals)
        scores['zone'] = zone_score
        
        # Maintenance History Component (10%)
        maint_score = self._score_maintenance_history(signals, vehicle)
        scores['maintenance'] = maint_score
        
        # Weighted composite score
        composite = (
            scores['battery'] * 0.40 +
            scores['utilization'] * 0.35 +
            scores['zone'] * 0.15 +
            scores['maintenance'] * 0.10
        )
        
        # Identify primary drivers (top 3)
        sorted_drivers = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary_drivers = [f"{name.upper()} ({score:.1f})" 
                          for name, score in sorted_drivers[:3]]
        
        return min(100, composite), primary_drivers
    
    def _score_battery_health(self, signals: RiskSignals, vehicle: VehicleState) -> float:
        """Score battery health risk 0-100."""
        score = 0.0
        
        # Critical battery level
        if vehicle.battery_pct < self.risk_thresholds['battery_critical_pct']:
            score += 50
        # Low battery
        elif vehicle.battery_pct < self.risk_thresholds['battery_low_pct']:
            score += 30
        # Moderate battery
        elif vehicle.battery_pct < 50:
            score += 15
        
        # Battery decline rate (impact if declining > 5% per day)
        if signals.battery_decline_rate > 5:
            score += 30
        elif signals.battery_decline_rate > 2:
            score += 15
        
        # Down-weight if insufficient data
        if signals.battery_trend == "unknown":
            score *= 0.6
        
        return min(100, score)
    
    def _score_utilization_stress(self, signals: RiskSignals, vehicle: VehicleState) -> float:
        """Score mechanical stress from utilization."""
        score = 0.0
        
        # High utilization intensity
        if signals.utilization_intensity > 0.8:
            score += 40
        elif signals.utilization_intensity > 0.5:
            score += 20
        
        # Increasing utilization (wearing out faster)
        if signals.utilization_trend == "increasing":
            score += 20
        
        # Idle penalty (vehicles not generating revenue)
        idle_penalty = min(30, signals.idle_hours / 24)  # 1 pt per day idle, max 30
        score += idle_penalty
        
        return min(100, score)
    
    def _score_zone_pressure(self, signals: RiskSignals) -> float:
        """Score zone-level supply/demand imbalance."""
        # High zone pressure = vehicle in overstocked area
        # Risk: may need rebalancing or repair during availability
        
        if signals.zone_pressure > 0.8:
            return 60  # High pressure zone
        elif signals.zone_pressure > 0.6:
            return 35
        else:
            return 15
    
    def _score_maintenance_history(self, signals: RiskSignals, vehicle: VehicleState) -> float:
        """Score based on maintenance/failure history."""
        score = 0.0
        
        # Recent maintenance
        if vehicle.maintenance_count_30d >= 2:
            score += 40
        elif vehicle.maintenance_count_30d >= 1:
            score += 20
        
        # Recent failures
        if vehicle.failure_count_90d >= 2:
            score += 30
        elif vehicle.failure_count_90d >= 1:
            score += 15
        
        # Currently under repair
        if vehicle.is_under_repair:
            score += 25
        
        return min(100, score)
    
    # ========================================================================
    # RISK LEVEL MAPPING
    # ========================================================================
    
    def _map_score_to_level(self, risk_score: float, vehicle: VehicleState) -> RiskLevel:
        """Map numeric risk score to business risk level."""
        
        # Critical level: Battery critical OR multiple failures
        if (vehicle.battery_pct < self.risk_thresholds['battery_critical_pct'] or
            vehicle.failure_count_90d >= 3):
            return RiskLevel.CRITICAL
        
        # High risk thresholds
        if risk_score >= 70:
            return RiskLevel.HIGH
        
        # Medium risk thresholds
        if risk_score >= 40:
            return RiskLevel.MEDIUM
        
        # Low risk
        return RiskLevel.LOW
    
    def _assess_confidence(self, signals: RiskSignals, vehicle: VehicleState) -> str:
        """
        Assess confidence in decision based on data sufficiency.
        
        Returns: 'HIGH', 'MEDIUM', or 'LOW'
        """
        
        # Insufficient deployment history = low confidence
        if signals.data_freshness_days < self.confidence_thresholds['medium']:
            return "LOW"
        
        # Good data history and stable trends = high confidence
        if (signals.data_freshness_days >= self.confidence_thresholds['high'] and
            signals.battery_trend != "unknown" and
            signals.utilization_trend != "unknown"):
            return "HIGH"
        
        # Everything else = medium
        return "MEDIUM"
    
    # ========================================================================
    # RECOMMENDATIONS & ALERTS
    # ========================================================================
    
    def _generate_alerts(self, vehicle: VehicleState, signals: RiskSignals, 
                        risk_level: RiskLevel) -> List[Dict]:
        """Generate operational alerts for critical conditions."""
        alerts = []
        
        # BATTERY CRITICAL
        if vehicle.battery_pct < self.risk_thresholds['battery_critical_pct']:
            alerts.append({
                'alert_type': AlertType.BATTERY_CRITICAL.value,
                'severity': 'CRITICAL',
                'message': f"Battery critically low: {vehicle.battery_pct:.0f}%",
                'action': 'Route to charge station immediately',
            })
        
        # IDLE TIMEOUT
        if signals.idle_hours > self.risk_thresholds['idle_alert_hours']:
            alerts.append({
                'alert_type': AlertType.IDLE_TIMEOUT.value,
                'severity': 'WARNING' if signals.idle_hours < 72 else 'CRITICAL',
                'message': f"Vehicle idle for {signals.idle_hours:.1f} hours",
                'action': 'Investigate cause and relocate or repair',
            })
        
        # MULTIPLE FAILURES
        if vehicle.failure_count_90d >= 3:
            alerts.append({
                'alert_type': AlertType.MULTIPLE_FAILURES.value,
                'severity': 'WARNING',
                'message': f"Multiple failures in 90 days: {vehicle.failure_count_90d}",
                'action': 'Schedule for comprehensive inspection',
            })
        
        # ZONE OVERSTOCK
        if signals.zone_pressure > 0.8 and vehicle.trips_last_24h == 0:
            alerts.append({
                'alert_type': AlertType.ZONE_OVERSTOCK.value,
                'severity': 'INFO',
                'message': f"Vehicle in overstocked zone (pressure: {signals.zone_pressure:.0%})",
                'action': 'Candidate for rebalancing to high-demand zone',
            })
        
        # MAINTENANCE DUE
        if vehicle.maintenance_count_30d >= 1 and vehicle.trips_last_24h == 0:
            alerts.append({
                'alert_type': AlertType.MAINTENANCE_DUE.value,
                'severity': 'INFO',
                'message': f"Recent maintenance; vehicle idle - verify repairs",
                'action': 'Functional test before return to fleet',
            })
        
        return alerts
    
    def _recommend_action(self, risk_level: RiskLevel, vehicle: VehicleState, 
                         signals: RiskSignals) -> RecommendationType:
        """Generate operational recommendation."""
        
        # CRITICAL: Urgent intervention
        if risk_level == RiskLevel.CRITICAL:
            if vehicle.battery_pct < 10:
                return RecommendationType.REPAIR
            else:
                return RecommendationType.INSPECT
        
        # HIGH: Proactive maintenance or repair
        if risk_level == RiskLevel.HIGH:
            if vehicle.failure_count_90d >= 2:
                return RecommendationType.REPAIR
            elif vehicle.maintenance_count_30d >= 1:
                return RecommendationType.INSPECT
            else:
                return RecommendationType.MONITOR
        
        # MEDIUM: Monitoring or light action
        if risk_level == RiskLevel.MEDIUM:
            if signals.idle_hours > self.risk_thresholds['idle_warning_hours']:
                return RecommendationType.REBALANCE
            else:
                return RecommendationType.MONITOR
        
        # LOW: Continue normal operations
        if signals.idle_hours > 48:
            return RecommendationType.ROTATE
        else:
            return RecommendationType.MONITOR
    
    def _generate_reasoning(self, risk_level: RiskLevel, signals: RiskSignals,
                           alerts: List[Dict], vehicle: VehicleState) -> str:
        """Generate human-readable explanation for decision."""
        
        reasons = []
        
        # Battery context
        if vehicle.battery_pct < 30:
            reasons.append(f"Battery is {vehicle.battery_pct:.0f}% (low)")
        if signals.battery_decline_rate > 2:
            reasons.append(f"Battery declining {signals.battery_decline_rate:.1f}%/day (rapid drain)")
        
        # Usage context
        if signals.utilization_intensity > 0.5:
            reasons.append(f"High utilization ({vehicle.trips_last_7d} trips/week)")
        if signals.idle_hours > self.risk_thresholds['idle_warning_hours']:
            reasons.append(f"Vehicle idle {signals.idle_hours:.0f}h (not generating revenue)")
        
        # Maintenance context
        if vehicle.failure_count_90d > 0:
            reasons.append(f"{vehicle.failure_count_90d} failures in 90 days (elevated)")
        if vehicle.is_under_repair:
            reasons.append("Currently undergoing repair")
        
        # Zone context
        if signals.zone_pressure > 0.7:
            reasons.append(f"Zone overstocked ({signals.zone_pressure:.0%} supply/demand ratio)")
        
        # Alerts
        if alerts:
            alert_msgs = [a['message'] for a in alerts]
            reasons.extend(alert_msgs)
        
        # Construct narrative
        if not reasons:
            return "Vehicle operating normally; no significant risk indicators."
        
        reasoning = f"{risk_level.value} RISK: " + "; ".join(reasons[:3])
        return reasoning
    
    # ========================================================================
    # VALIDATION
    # ========================================================================
    
    def _validate_vehicle_state(self, vehicle: VehicleState) -> None:
        """Validate vehicle state data quality."""
        
        errors = []
        
        # Required fields
        if not vehicle.vehicle_id:
            errors.append("Missing vehicle_id")
        if vehicle.battery_pct < 0 or vehicle.battery_pct > 100:
            errors.append(f"Invalid battery_pct: {vehicle.battery_pct}")
        if not vehicle.zone_id:
            errors.append("Missing zone_id")
        
        if errors:
            error_msg = "; ".join(errors)
            self.logger.error(f"VehicleState validation failed: {error_msg}")
            raise ValueError(error_msg)


# ============================================================================
# BATCH SCORING
# ============================================================================

class FleetDecisionBatch:
    """Batch scorer for fleet-wide decisions."""
    
    def __init__(self, engine: Optional[FleetDecisionEngine] = None):
        self.engine = engine or FleetDecisionEngine()
    
    def score_fleet(self, vehicles: List[VehicleState]) -> Dict[str, Decision]:
        """
        Score entire fleet and return decisions indexed by vehicle_id.
        
        Args:
            vehicles: List of VehicleState objects
            
        Returns:
            Dictionary mapping vehicle_id -> Decision
        """
        decisions = {}
        
        for vehicle in vehicles:
            try:
                decision = self.engine.score_vehicle(vehicle)
                decisions[vehicle.vehicle_id] = decision
            except Exception as e:
                logger.error(f"Error scoring {vehicle.vehicle_id}: {str(e)}")
                # In production, would create error decision with LOW confidence
                continue
        
        return decisions
    
    def get_summary_metrics(self, decisions: Dict[str, Decision]) -> Dict:
        """Get fleet-wide summary metrics."""
        
        if not decisions:
            return {}
        
        risk_counts = {level.value: 0 for level in RiskLevel}
        alert_types = {}
        action_types = {}
        
        for decision in decisions.values():
            risk_counts[decision.risk_level.value] += 1
            
            for alert in decision.alerts:
                alert_type = alert.get('alert_type', 'UNKNOWN')
                alert_types[alert_type] = alert_types.get(alert_type, 0) + 1
            
            action = decision.recommended_action.value
            action_types[action] = action_types.get(action, 0) + 1
        
        return {
            'total_vehicles': len(decisions),
            'risk_distribution': risk_counts,
            'alert_breakdown': alert_types,
            'recommended_actions': action_types,
            'avg_risk_score': np.mean([d.risk_score for d in decisions.values()]),
        }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example: Create and score a vehicle
    
    vehicle = VehicleState(
        vehicle_id="scooter_001",
        vehicle_type="scooter",
        latitude=47.6097,
        longitude=-122.3331,
        zone_id="downtown",
        battery_pct=25,
        battery_pct_prev_day=28,
        battery_pct_prev_week=45,
        trips_last_24h=2,
        trips_last_7d=8,
        trips_last_30d=35,
        distance_last_24h=5.2,
        distance_last_7d=22.5,
        last_trip_timestamp=datetime.now() - timedelta(hours=2),
        days_deployed=45,
        maintenance_count_30d=1,
        failure_count_90d=0,
        zone_demand=0.7,
        zone_supply=0.9,
    )
    
    # Score the vehicle
    engine = FleetDecisionEngine()
    decision = engine.score_vehicle(vehicle)
    
    # Print results
    print("\n" + "=" * 70)
    print("VEHICLE DECISION REPORT")
    print("=" * 70)
    print(f"Vehicle ID:     {decision.vehicle_id}")
    print(f"Risk Level:     {decision.risk_level.value}")
    print(f"Risk Score:     {decision.risk_score:.1f}/100")
    print(f"Confidence:     {decision.confidence}")
    print(f"Recommended:    {decision.recommended_action.value}")
    print(f"Reasoning:      {decision.reasoning}")
    print(f"\nPrimary Drivers:")
    for driver in decision.primary_drivers:
        print(f"  - {driver}")
    
    if decision.alerts:
        print(f"\nAlerts ({len(decision.alerts)}):")
        for alert in decision.alerts:
            print(f"  [{alert['severity']}] {alert['message']}")
    
    print("\n" + "=" * 70)
    
    # Example: Batch scoring
    print("\n\nBATCH SCORING EXAMPLE")
    print("=" * 70)
    
    vehicles = [
        VehicleState(
            vehicle_id=f"vehicle_{i:03d}",
            vehicle_type="scooter" if i % 2 == 0 else "bike",
            latitude=47.6097 + np.random.randn() * 0.02,
            longitude=-122.3331 + np.random.randn() * 0.02,
            zone_id=f"zone_{np.random.randint(1, 5)}",
            battery_pct=np.random.uniform(10, 95),
            trips_last_7d=np.random.randint(0, 20),
            trips_last_30d=np.random.randint(0, 100),
            days_deployed=np.random.randint(7, 365),
            failure_count_90d=np.random.randint(0, 3),
            zone_demand=np.random.uniform(0.3, 1.0),
            zone_supply=np.random.uniform(0.3, 1.0),
        )
        for i in range(10)
    ]
    
    batch = FleetDecisionBatch()
    fleet_decisions = batch.score_fleet(vehicles)
    
    # Print summary
    summary = batch.get_summary_metrics(fleet_decisions)
    print(f"\nFleet Summary:")
    print(f"  Total Vehicles: {summary['total_vehicles']}")
    print(f"  Risk Distribution: {summary['risk_distribution']}")
    print(f"  Avg Risk Score: {summary['avg_risk_score']:.1f}")
    print(f"  Recommended Actions: {summary['recommended_actions']}")
