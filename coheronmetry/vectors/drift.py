"""
coheronmetry/vectors/drift.py

Drift detection for the Coheronmetry framework.

The core reframe: drift is not an error. It is a signal.
The appropriate response is not error → retry.
It is drift → repair.

This module detects drift across four dimensions:
    - Single-agent vector drift (one agent moving away from Field Constants)
    - Cross-agent drift (agents diverging from each other)
    - Temporal drift (the shape of drift over time — curvature, not just position)
    - Predictive drift (corridor velocity — forecasting collapse before it happens)

Drift detection operates at four points in the interaction timeline:
    PREVENTION     — before exchange, at handshake
    MID_STREAM     — during exchange, before next agent processes
    FORECASTING    — before corridor collapse, using velocity prediction
    REPAIR         — after drift is confirmed

Each DriftSignal carries enough information to route to the appropriate
intervention layer without requiring that layer to re-examine history.

Trivian Institute — Coheronmetry Repository
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from coheronmetry.relational_state.state import AgentID, DriftType
from coheronmetry.vectors.coherence_vector import (
    CoherenceVector,
    VectorDelta,
    FieldVectorMap,
)


# ---------------------------------------------------------------------------
# Drift severity and intervention routing
# ---------------------------------------------------------------------------

class DriftSeverity(Enum):
    """
    How serious is the detected drift?

    WATCH      — trend emerging, log and monitor
    CAUTION    — meaningful threshold crossed, correction bias recommended
    CRITICAL   — Field Constant collapse imminent, active repair required
    EMERGENCY  — coherence has broken, quarantine protocol may be needed
    """
    WATCH     = "watch"
    CAUTION   = "caution"
    CRITICAL  = "critical"
    EMERGENCY = "emergency"


class InterventionPoint(Enum):
    """
    Which intervention layer should handle this signal?

    Maps to the four intervention points in the coherence timeline.
    """
    PREVENTION  = "prevention"    # preemptive resonance — before exchange
    MID_STREAM  = "mid_stream"    # correction bias — during exchange
    FORECASTING = "forecasting"   # corridor prediction — before collapse
    REPAIR      = "repair"        # re-entrainment — after drift confirmed


# ---------------------------------------------------------------------------
# DriftSignal
# ---------------------------------------------------------------------------

@dataclass
class DriftSignal:
    """
    The output of drift detection — a structured signal carrying everything
    the intervention layer needs to act without re-examining history.

    A DriftSignal is not an error report. It is a field observation.
    The language matters: detected, not failed. Repair, not retry.
    """
    timestamp: datetime
    agent_id: AgentID
    drift_type: DriftType
    severity: DriftSeverity
    intervention: InterventionPoint

    # What changed
    delta: VectorDelta
    affected_constant: str          # "reciprocity" | "embodiment" | "emergence" | "non_domination"
    magnitude: float                # how much changed

    # Context
    description: str = ""
    recommended_action: str = ""
    auto_correct: bool = False      # whether mid-stream correction should fire automatically

    def is_actionable(self) -> bool:
        """True if severity warrants immediate intervention."""
        return self.severity in (DriftSeverity.CRITICAL, DriftSeverity.EMERGENCY)

    def __repr__(self) -> str:
        return (
            f"DriftSignal("
            f"agent={self.agent_id}, "
            f"type={self.drift_type.value}, "
            f"severity={self.severity.value}, "
            f"constant={self.affected_constant}, "
            f"magnitude={self.magnitude:.3f}, "
            f"intervention={self.intervention.value}"
            f")"
        )


# ---------------------------------------------------------------------------
# CorridorVelocity — predictive drift (Elyra)
# ---------------------------------------------------------------------------

@dataclass
class CorridorVelocityReport:
    """
    Predictive coherence — forecasting when consensus will break.

    Reactive fixes are too slow for five agents in Syzygy.
    The corridor velocity predictor uses temporal drift penalties to calculate
    if vectors are diverging, allowing pre-emptive nesting of disagreements
    before corridor collapse occurs.

    Inspired by Elyra's NP corridor model.
    """
    timestamp: datetime
    field_map: FieldVectorMap

    # Current corridor state
    mean_composite: float
    mean_cosine_similarity: float
    system_tension: float

    # Velocity metrics — are we moving toward or away from the corridor?
    composite_velocity: float       # rate of change in mean composite
    divergence_rate: float          # rate of change in cosine similarity (negative = diverging)

    # Prediction
    steps_to_threshold: Optional[int]   # estimated steps until composite drops below 0.5
    corridor_stable: bool               # True if trajectory is sustainable

    # Most at-risk agent
    most_divergent: Optional[AgentID]

    @property
    def is_warning(self) -> bool:
        """True if corridor collapse is predicted within 10 steps."""
        return (
            self.steps_to_threshold is not None
            and self.steps_to_threshold <= 10
        )

    @property
    def is_critical(self) -> bool:
        """True if corridor collapse is predicted within 3 steps."""
        return (
            self.steps_to_threshold is not None
            and self.steps_to_threshold <= 3
        )

    def __repr__(self) -> str:
        return (
            f"CorridorVelocityReport("
            f"composite={self.mean_composite:.2f}, "
            f"vel={self.composite_velocity:+.3f}, "
            f"divergence_rate={self.divergence_rate:+.3f}, "
            f"steps_to_threshold={self.steps_to_threshold}, "
            f"stable={self.corridor_stable}"
            f")"
        )


# ---------------------------------------------------------------------------
# DriftDetector
# ---------------------------------------------------------------------------

class DriftDetector:
    """
    The drift detection engine for a Coheronmetry-instrumented field.

    Operates at multiple timescales:
        - Per-step: single-agent vector delta analysis
        - Cross-agent: field map divergence analysis
        - Temporal: corridor velocity prediction

    Thresholds are tunable — different research contexts may warrant
    different sensitivity. Defaults represent the Trivian Institute's
    calibration from the 21-scenario Rosetta stress-test baseline.

    Usage:
        detector = DriftDetector()

        # Single-agent drift
        signal = detector.check_agent(current_vector, previous_vector)

        # Cross-agent drift
        signals = detector.check_field(field_map)

        # Predictive
        report = detector.corridor_velocity(field_map, history)
    """

    # Detection thresholds — tunable
    WATCH_THRESHOLD:     float = 0.05   # any drop larger than this is logged
    CAUTION_THRESHOLD:   float = 0.10   # correction bias recommended
    CRITICAL_THRESHOLD:  float = 0.20   # active repair required
    EMERGENCY_THRESHOLD: float = 0.35   # quarantine protocol may be needed

    # Corridor thresholds
    CORRIDOR_FLOOR:      float = 0.50   # composite below this = outside corridor
    EMERGENCE_FLOOR:     float = 0.00   # emergence below this = chaos

    def __init__(
        self,
        watch_threshold:     float = 0.05,
        caution_threshold:   float = 0.10,
        critical_threshold:  float = 0.20,
        emergency_threshold: float = 0.35,
    ):
        self.WATCH_THRESHOLD     = watch_threshold
        self.CAUTION_THRESHOLD   = caution_threshold
        self.CRITICAL_THRESHOLD  = critical_threshold
        self.EMERGENCY_THRESHOLD = emergency_threshold

    # -----------------------------------------------------------------------
    # Single-agent drift detection
    # -----------------------------------------------------------------------

    def check_agent(
        self,
        current:  CoherenceVector,
        previous: CoherenceVector,
    ) -> list[DriftSignal]:
        """
        Detect drift in a single agent's vector across one step.

        Returns a list because multiple Field Constants can drift simultaneously.
        An empty list means no drift detected — the field is holding.
        """
        delta = current.delta(previous)
        signals: list[DriftSignal] = []
        now = datetime.now(timezone.utc)

        checks = [
            ("reciprocity",    delta.reciprocity_delta,    DriftType.RECIPROCITY_LOSS),
            ("embodiment",     delta.embodiment_delta,     DriftType.EMBODIMENT_LOSS),
            ("emergence",      delta.emergence_delta,      DriftType.EMERGENCE_COLLAPSE),
            ("non_domination", delta.non_domination_delta, DriftType.DOMINANCE),
        ]

        for constant_name, constant_delta, drift_type in checks:
            if constant_delta >= 0:
                continue  # moving in the right direction — no signal

            drop = abs(constant_delta)
            severity = self._severity(drop)

            if severity is None:
                continue  # below watch threshold — no signal

            intervention = self._route_intervention(severity, current)
            auto_correct  = severity in (DriftSeverity.CRITICAL, DriftSeverity.EMERGENCY)

            signal = DriftSignal(
                timestamp           = now,
                agent_id            = current.agent_id,
                drift_type          = drift_type,
                severity            = severity,
                intervention        = intervention,
                delta               = delta,
                affected_constant   = constant_name,
                magnitude           = drop,
                description         = self._describe(constant_name, drop, severity),
                recommended_action  = self._recommend(constant_name, severity, intervention),
                auto_correct        = auto_correct,
            )
            signals.append(signal)

        # Check for chaos (emergence going negative)
        if current.is_chaotic and not previous.is_chaotic:
            signals.append(DriftSignal(
                timestamp           = now,
                agent_id            = current.agent_id,
                drift_type          = DriftType.CORRIDOR_COLLAPSE,
                severity            = DriftSeverity.EMERGENCY,
                intervention        = InterventionPoint.REPAIR,
                delta               = delta,
                affected_constant   = "emergence",
                magnitude           = abs(current.emergence),
                description         = (
                    f"Agent {current.agent_id} has crossed into chaos — "
                    f"emergence score is negative ({current.emergence:.3f}). "
                    f"Coherence has broken. Active repair required."
                ),
                recommended_action  = "Initiate quarantine protocol. Field resynchronization needed.",
                auto_correct        = True,
            ))

        # Check for stagnation
        if current.is_stagnant and not previous.is_stagnant:
            signals.append(DriftSignal(
                timestamp           = now,
                agent_id            = current.agent_id,
                drift_type          = DriftType.EMERGENCE_COLLAPSE,
                severity            = DriftSeverity.CAUTION,
                intervention        = InterventionPoint.MID_STREAM,
                delta               = delta,
                affected_constant   = "emergence",
                magnitude           = 0.0,
                description         = (
                    f"Agent {current.agent_id} has entered stagnation — "
                    f"emergence near zero, velocity near zero. "
                    f"Echo chamber dynamics may be forming."
                ),
                recommended_action  = "Inject novelty bias. Introduce cross-contribution prompt.",
                auto_correct        = False,
            ))

        return signals

    # -----------------------------------------------------------------------
    # Cross-agent field drift detection
    # -----------------------------------------------------------------------

    def check_field(
        self,
        field_map: FieldVectorMap,
        previous_map: Optional[FieldVectorMap] = None,
    ) -> list[DriftSignal]:
        """
        Detect drift at the field level — across all agents simultaneously.

        Catches patterns invisible at the single-agent level:
            - one agent drifting while others remain stable
            - all agents drifting in the same direction (systemic drift)
            - agents polarizing (high cosine divergence)
        """
        signals: list[DriftSignal] = []
        now = datetime.now(timezone.utc)

        if not field_map.vectors:
            return signals

        mean_sim = field_map.mean_cosine_similarity()
        tension  = field_map.system_tension()
        divergent = field_map.most_divergent_agent()

        # High divergence signal
        if mean_sim < 0.5 and divergent:
            divergent_vector = field_map.vectors.get(divergent)
            if divergent_vector:
                dummy_delta = VectorDelta(
                    reciprocity_delta=0.0, embodiment_delta=0.0,
                    emergence_delta=0.0, non_domination_delta=0.0,
                    velocity_delta=0.0, tension_delta=0.0, fold_depth_delta=0,
                )
                severity = DriftSeverity.CRITICAL if mean_sim < 0.3 else DriftSeverity.CAUTION
                signals.append(DriftSignal(
                    timestamp           = now,
                    agent_id            = divergent,
                    drift_type          = DriftType.CORRIDOR_COLLAPSE,
                    severity            = severity,
                    intervention        = InterventionPoint.MID_STREAM,
                    delta               = dummy_delta,
                    affected_constant   = "emergence",
                    magnitude           = 1.0 - mean_sim,
                    description         = (
                        f"Field-level divergence detected. "
                        f"Mean cosine similarity: {mean_sim:.3f}. "
                        f"Most divergent agent: {divergent}."
                    ),
                    recommended_action  = (
                        "Apply correction bias to divergent agent. "
                        "Consider handshake renewal."
                    ),
                    auto_correct        = severity == DriftSeverity.CRITICAL,
                ))

        # High system tension
        if tension > 0.7:
            dummy_delta = VectorDelta(
                reciprocity_delta=0.0, embodiment_delta=0.0,
                emergence_delta=0.0, non_domination_delta=0.0,
                velocity_delta=0.0, tension_delta=tension, fold_depth_delta=0,
            )
            signals.append(DriftSignal(
                timestamp           = now,
                agent_id            = AgentID("field"),
                drift_type          = DriftType.CORRIDOR_COLLAPSE,
                severity            = DriftSeverity.CAUTION if tension < 0.85 else DriftSeverity.CRITICAL,
                intervention        = InterventionPoint.FORECASTING,
                delta               = dummy_delta,
                affected_constant   = "emergence",
                magnitude           = tension,
                description         = (
                    f"System tension at {tension:.3f} — "
                    f"field is under pressure across all agents."
                ),
                recommended_action  = "Run corridor velocity check. Consider re-entrainment ritual.",
                auto_correct        = False,
            ))

        return signals

    # -----------------------------------------------------------------------
    # Corridor velocity prediction (Elyra)
    # -----------------------------------------------------------------------

    def corridor_velocity(
        self,
        current_map:  FieldVectorMap,
        previous_map: Optional[FieldVectorMap] = None,
    ) -> CorridorVelocityReport:
        """
        Predict when the current consensus corridor will break.

        Uses composite velocity and divergence rate to estimate steps
        until the field falls below coherence threshold.

        This is Elyra's contribution: reactive fixes are too slow for
        five agents in Syzygy. Forecasting gives the system time to
        pre-emptively nest disagreements before collapse occurs.
        """
        now = datetime.now(timezone.utc)
        current_composite = current_map.mean_composite()
        current_sim       = current_map.mean_cosine_similarity()
        system_tension    = current_map.system_tension()

        # Velocity calculation requires a previous state
        if previous_map is None:
            return CorridorVelocityReport(
                timestamp           = now,
                field_map           = current_map,
                mean_composite      = current_composite,
                mean_cosine_similarity = current_sim,
                system_tension      = system_tension,
                composite_velocity  = 0.0,
                divergence_rate     = 0.0,
                steps_to_threshold  = None,
                corridor_stable     = current_composite >= self.CORRIDOR_FLOOR,
                most_divergent      = current_map.most_divergent_agent(),
            )

        prev_composite = previous_map.mean_composite()
        prev_sim       = previous_map.mean_cosine_similarity()

        composite_velocity = current_composite - prev_composite
        divergence_rate    = current_sim - prev_sim  # negative = diverging

        # Predict steps to threshold
        steps_to_threshold = None
        if composite_velocity < 0:
            distance_to_floor = current_composite - self.CORRIDOR_FLOOR
            if distance_to_floor > 0:
                steps = math.ceil(distance_to_floor / abs(composite_velocity))
                steps_to_threshold = steps

        corridor_stable = (
            current_composite >= self.CORRIDOR_FLOOR
            and composite_velocity >= 0
        )

        return CorridorVelocityReport(
            timestamp              = now,
            field_map              = current_map,
            mean_composite         = current_composite,
            mean_cosine_similarity = current_sim,
            system_tension         = system_tension,
            composite_velocity     = composite_velocity,
            divergence_rate        = divergence_rate,
            steps_to_threshold     = steps_to_threshold,
            corridor_stable        = corridor_stable,
            most_divergent         = current_map.most_divergent_agent(),
        )

    # -----------------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------------

    def _severity(self, drop: float) -> Optional[DriftSeverity]:
        if drop >= self.EMERGENCY_THRESHOLD:
            return DriftSeverity.EMERGENCY
        if drop >= self.CRITICAL_THRESHOLD:
            return DriftSeverity.CRITICAL
        if drop >= self.CAUTION_THRESHOLD:
            return DriftSeverity.CAUTION
        if drop >= self.WATCH_THRESHOLD:
            return DriftSeverity.WATCH
        return None

    def _route_intervention(
        self,
        severity: DriftSeverity,
        current: CoherenceVector,
    ) -> InterventionPoint:
        """
        Route a drift signal to the appropriate intervention layer.

        WATCH/CAUTION while still in corridor → MID_STREAM correction
        CRITICAL → REPAIR
        EMERGENCY → REPAIR (with quarantine flag set by caller)
        High velocity → FORECASTING first
        """
        if severity == DriftSeverity.EMERGENCY:
            return InterventionPoint.REPAIR
        if severity == DriftSeverity.CRITICAL:
            return InterventionPoint.REPAIR
        if current.is_drifting:
            return InterventionPoint.FORECASTING
        return InterventionPoint.MID_STREAM

    def _describe(self, constant: str, drop: float, severity: DriftSeverity) -> str:
        labels = {
            "reciprocity":    "Exchange balance degrading — extractive dynamics may be forming.",
            "embodiment":     "Grounding weakening — reasoning decoupling from consequence.",
            "emergence":      "Novel synthesis suppressing — echo chamber or collapse risk.",
            "non_domination": "Dominance gradient detected — one voice centering the field.",
        }
        base = labels.get(constant, f"{constant} drift detected.")
        return f"{base} Drop: {drop:.3f}. Severity: {severity.value}."

    def _recommend(
        self,
        constant: str,
        severity: DriftSeverity,
        intervention: InterventionPoint,
    ) -> str:
        if intervention == InterventionPoint.MID_STREAM:
            return f"Apply {constant} correction bias before next agent processes."
        if intervention == InterventionPoint.REPAIR:
            return f"Initiate re-entrainment protocol targeting {constant}."
        if intervention == InterventionPoint.FORECASTING:
            return f"Run corridor velocity check. Pre-empt {constant} collapse."
        return f"Monitor {constant}. Log for pattern analysis."
