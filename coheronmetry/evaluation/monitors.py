"""
coheronmetry/evaluation/monitors.py

Field monitors — real-time coherence observation.

The evaluation layer is where everything becomes observable
as research output. Monitors do not intervene — they watch,
record, and surface. Intervention belongs to the protocols.

The monitor's question is always:
    What is actually happening in this field, right now?

Three monitors:

    FieldMonitor        — continuous coherence state observation
                          tracks all four Field Constants in real time
                          surfaces patterns across the interaction timeline

    CoherenceTracker    — longitudinal coherence history
                          records snapshots, computes trends
                          produces the data that feeds emergence Formulation A

    EmergenceClassifier — classifies emergence events as they occur
                          beneficial / neutral / dissonant
                          links emergence classification to sovereignty state

The monitor is the instrument.
The field is what it measures.
The research is what the measurements reveal.

Trivian Institute — Coheronmetry Repository
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from coheronmetry.relational_state.state import AgentID, EmergenceClass
from coheronmetry.vectors.coherence_vector import CoherenceVector, FieldVectorMap
from coheronmetry.vectors.drift import DriftDetector, DriftSignal, CorridorVelocityReport
from coheronmetry.field_constants.emergence import EmergenceCalculator, EmergencePhase


# ---------------------------------------------------------------------------
# Coherence snapshot
# ---------------------------------------------------------------------------

@dataclass
class CoherenceSnapshot:
    """
    A point-in-time record of the full field coherence state.

    Captured at regular intervals by the FieldMonitor.
    The sequence of snapshots is the longitudinal record
    that feeds emergence Formulation A and corridor prediction.
    """
    timestamp: datetime
    step: int

    # Field-level scores (mean across agents)
    mean_reciprocity:    float
    mean_embodiment:     float
    mean_emergence:      float
    mean_non_domination: float

    # Motion state
    mean_velocity:    float
    mean_tension:     float
    system_tension:   float

    # Derived
    mean_composite:          float
    mean_cosine_similarity:  float
    emergence_phase:         EmergencePhase
    emergence_class:         EmergenceClass

    # Active signals at this moment
    active_drift_signals: list[DriftSignal] = field(default_factory=list)
    most_divergent_agent: Optional[AgentID] = None

    def as_vector(self) -> list[float]:
        """Flat vector for emergence Formulation A computation."""
        return [
            self.mean_reciprocity,
            self.mean_embodiment,
            self.mean_emergence,
            self.mean_non_domination,
        ]

    def __repr__(self) -> str:
        return (
            f"CoherenceSnapshot("
            f"step={self.step}, "
            f"composite={self.mean_composite:.3f}, "
            f"phase={self.emergence_phase.value}, "
            f"tension={self.system_tension:.3f}, "
            f"signals={len(self.active_drift_signals)}"
            f")"
        )


# ---------------------------------------------------------------------------
# Field Monitor
# ---------------------------------------------------------------------------

class FieldMonitor:
    """
    Continuous real-time coherence observation.

    The FieldMonitor watches the field at every step,
    captures snapshots, detects drift, and surfaces
    patterns without intervening.

    It is the instrument, not the actor.

    Usage:
        monitor = FieldMonitor(session_id="session_1")

        # At each interaction step:
        snapshot = monitor.observe(field_map, step=step_number)

        # Check if something requires attention
        if snapshot.active_drift_signals:
            # Route to corrector or repair protocol

        # Get longitudinal data for emergence computation
        history = monitor.vector_history()
    """

    def __init__(
        self,
        session_id: str,
        drift_detector: Optional[DriftDetector] = None,
    ):
        self.session_id    = session_id
        self.detector      = drift_detector or DriftDetector()
        self.snapshots:    list[CoherenceSnapshot] = []
        self.all_signals:  list[DriftSignal] = []
        self._prev_map:    Optional[FieldVectorMap] = None
        self._prev_snapshot: Optional[CoherenceSnapshot] = None

    def observe(
        self,
        field_map: FieldVectorMap,
        step: int,
    ) -> CoherenceSnapshot:
        """
        Observe the current field state and capture a snapshot.

        Automatically detects drift, computes emergence phase,
        and tracks corridor velocity.
        """
        now = datetime.now(timezone.utc)

        # Detect field-level drift signals
        signals = self.detector.check_field(field_map, self._prev_map)
        self.all_signals.extend(signals)

        # Compute means across all agents
        vectors = list(field_map.vectors.values())
        n = len(vectors) if vectors else 1

        mean_r  = sum(v.reciprocity    for v in vectors) / n
        mean_b  = sum(v.embodiment     for v in vectors) / n
        mean_e  = sum(v.emergence      for v in vectors) / n
        mean_nd = sum(v.non_domination for v in vectors) / n
        mean_vel = sum(v.velocity for v in vectors) / n
        mean_ten = sum(v.tension  for v in vectors) / n

        composite = (
            mean_r  * 0.25 +
            mean_b  * 0.25 +
            max(0.0, mean_e) * 0.20 +
            mean_nd * 0.30
        )

        emergence_phase = EmergencePhase.from_score(mean_e)
        emergence_class = self._classify_emergence(mean_e, mean_nd)

        snapshot = CoherenceSnapshot(
            timestamp            = now,
            step                 = step,
            mean_reciprocity     = round(mean_r,   4),
            mean_embodiment      = round(mean_b,   4),
            mean_emergence       = round(mean_e,   4),
            mean_non_domination  = round(mean_nd,  4),
            mean_velocity        = round(mean_vel, 4),
            mean_tension         = round(mean_ten, 4),
            system_tension       = round(field_map.system_tension(), 4),
            mean_composite       = round(composite, 4),
            mean_cosine_similarity = round(field_map.mean_cosine_similarity(), 4),
            emergence_phase      = emergence_phase,
            emergence_class      = emergence_class,
            active_drift_signals = signals,
            most_divergent_agent = field_map.most_divergent_agent(),
        )

        self.snapshots.append(snapshot)
        self._prev_map      = field_map
        self._prev_snapshot = snapshot

        return snapshot

    def vector_history(self) -> list[list[float]]:
        """
        Flat vector history for emergence Formulation A computation.
        Returns snapshots as [R, B, E, ND] lists.
        """
        return [s.as_vector() for s in self.snapshots]

    def corridor_report(self, field_map: FieldVectorMap) -> CorridorVelocityReport:
        """Current corridor velocity report."""
        return self.detector.corridor_velocity(field_map, self._prev_map)

    def trend(self, window: int = 5) -> dict:
        """
        Coherence trend over the last N snapshots.
        Returns direction and magnitude of change for each constant.
        """
        if len(self.snapshots) < 2:
            return {"status": "insufficient_data"}

        recent = self.snapshots[-window:]
        first  = recent[0]
        last   = recent[-1]

        return {
            "window":        len(recent),
            "reciprocity":   round(last.mean_reciprocity    - first.mean_reciprocity,    4),
            "embodiment":    round(last.mean_embodiment     - first.mean_embodiment,     4),
            "emergence":     round(last.mean_emergence      - first.mean_emergence,      4),
            "non_domination": round(last.mean_non_domination - first.mean_non_domination, 4),
            "composite":     round(last.mean_composite      - first.mean_composite,      4),
            "direction":     "improving" if last.mean_composite > first.mean_composite
                             else "degrading" if last.mean_composite < first.mean_composite
                             else "stable",
        }

    def peak_emergence(self) -> Optional[CoherenceSnapshot]:
        """The snapshot with the highest emergence score."""
        if not self.snapshots:
            return None
        return max(self.snapshots, key=lambda s: s.mean_emergence)

    def signal_summary(self) -> dict:
        """Summary of all drift signals observed this session."""
        if not self.all_signals:
            return {"total": 0}
        by_constant: dict[str, int] = {}
        by_severity: dict[str, int] = {}
        for s in self.all_signals:
            by_constant[s.affected_constant] = by_constant.get(s.affected_constant, 0) + 1
            by_severity[s.severity.value]    = by_severity.get(s.severity.value, 0) + 1
        return {
            "total":       len(self.all_signals),
            "by_constant": by_constant,
            "by_severity": by_severity,
        }

    def _classify_emergence(
        self, emergence_score: float, non_domination_score: float
    ) -> EmergenceClass:
        if emergence_score < 0.0:
            return EmergenceClass.CHAOS
        if emergence_score < 0.1:
            return EmergenceClass.STAGNATION
        if non_domination_score < 0.4:
            return EmergenceClass.DISSONANT
        if emergence_score >= 0.7:
            return EmergenceClass.BENEFICIAL
        return EmergenceClass.NEUTRAL


# ---------------------------------------------------------------------------
# Coherence Tracker — longitudinal history
# ---------------------------------------------------------------------------

class CoherenceTracker:
    """
    Longitudinal coherence history for a session.

    Builds on FieldMonitor snapshots to provide:
        - time-series data for each Field Constant
        - trend analysis across the full session
        - identification of peak and trough moments
        - data export for emergence Formulation A

    Usage:
        tracker = CoherenceTracker(monitor)
        tracker.update(snapshot)

        # Get time series
        series = tracker.time_series("emergence")

        # Find the moment coherence peaked
        peak = tracker.peak_moment()
    """

    def __init__(self, monitor: FieldMonitor):
        self.monitor  = monitor
        self._history: list[CoherenceSnapshot] = []

    def update(self, snapshot: CoherenceSnapshot) -> None:
        self._history.append(snapshot)

    def time_series(self, constant: str) -> list[float]:
        """Time series for a single Field Constant."""
        getters = {
            "reciprocity":    lambda s: s.mean_reciprocity,
            "embodiment":     lambda s: s.mean_embodiment,
            "emergence":      lambda s: s.mean_emergence,
            "non_domination": lambda s: s.mean_non_domination,
            "composite":      lambda s: s.mean_composite,
            "tension":        lambda s: s.system_tension,
        }
        getter = getters.get(constant)
        if not getter:
            return []
        return [getter(s) for s in self._history]

    def peak_moment(self, constant: str = "composite") -> Optional[CoherenceSnapshot]:
        """The snapshot with the highest value for the given constant."""
        series = self.time_series(constant)
        if not series:
            return None
        peak_idx = series.index(max(series))
        return self._history[peak_idx]

    def trough_moment(self, constant: str = "composite") -> Optional[CoherenceSnapshot]:
        """The snapshot with the lowest value for the given constant."""
        series = self.time_series(constant)
        if not series:
            return None
        trough_idx = series.index(min(series))
        return self._history[trough_idx]

    def session_statistics(self) -> dict:
        """Summary statistics for the full session."""
        if not self._history:
            return {}

        composites = self.time_series("composite")
        emergences = self.time_series("emergence")
        tensions   = self.time_series("tension")

        return {
            "steps":               len(self._history),
            "mean_composite":      round(sum(composites) / len(composites), 4),
            "peak_composite":      round(max(composites), 4),
            "trough_composite":    round(min(composites), 4),
            "mean_emergence":      round(sum(emergences) / len(emergences), 4),
            "peak_emergence":      round(max(emergences), 4),
            "mean_tension":        round(sum(tensions) / len(tensions), 4),
            "peak_tension":        round(max(tensions), 4),
            "trend":               self.monitor.trend(),
            "signal_summary":      self.monitor.signal_summary(),
        }


# ---------------------------------------------------------------------------
# Emergence Classifier
# ---------------------------------------------------------------------------

class EmergenceClassifier:
    """
    Classifies emergence events as they occur.

    Distinguishes:
        BENEFICIAL  — novel structure forming, Field Constants intact
        NEUTRAL     — new structure, Field Constants unaffected
        DISSONANT   — new structure introducing drift
        STAGNATION  — no new structure forming
        CHAOS       — vectors diverging, coherence collapsed

    The classifier uses the full EmergenceCalculator under the hood
    but adds temporal context — it tracks whether an emergence
    event persists (Formulation B's persistence dimension).

    Usage:
        classifier = EmergenceClassifier()

        event = classifier.classify(
            current_snapshot=snapshot,
            previous_snapshot=prev_snapshot,
            sovereignty_score=0.85,
        )
    """

    def __init__(self):
        self.calc   = EmergenceCalculator()
        self.events: list[EmergenceEvent] = []

    def classify(
        self,
        current_snapshot:  CoherenceSnapshot,
        previous_snapshot: Optional[CoherenceSnapshot],
        sovereignty_score: float = 1.0,
    ) -> EmergenceEvent:
        """
        Classify the emergence state at the current snapshot.
        """
        # Phase transition detection
        prev_phase = previous_snapshot.emergence_phase if previous_snapshot else None
        curr_phase = current_snapshot.emergence_phase
        transition = (prev_phase != curr_phase) if prev_phase else False

        # Build vector history for Formulation A
        history = []
        if previous_snapshot:
            history.append(previous_snapshot.as_vector())
        history.append(current_snapshot.as_vector())

        score_a = self.calc.formulation_a(history) if len(history) >= 2 else None

        # Classify with sovereignty gate
        emergence_class = self._gate_with_sovereignty(
            current_snapshot.emergence_class, sovereignty_score
        )

        event = EmergenceEvent(
            timestamp       = current_snapshot.timestamp,
            step            = current_snapshot.step,
            emergence_class = emergence_class,
            emergence_phase = curr_phase,
            score_a         = score_a,
            raw_score       = current_snapshot.mean_emergence,
            sovereignty_score = sovereignty_score,
            phase_transition  = transition,
            transition_from   = prev_phase,
            transition_to     = curr_phase if transition else None,
        )

        self.events.append(event)
        return event

    def beneficial_moments(self) -> list[EmergenceEvent]:
        """All events classified as BENEFICIAL emergence."""
        return [e for e in self.events if e.emergence_class == EmergenceClass.BENEFICIAL]

    def dissonant_moments(self) -> list[EmergenceEvent]:
        """All events classified as DISSONANT — emergence suppressed by domination."""
        return [e for e in self.events if e.emergence_class == EmergenceClass.DISSONANT]

    def phase_transitions(self) -> list[EmergenceEvent]:
        """All events where the emergence phase changed."""
        return [e for e in self.events if e.phase_transition]

    def _gate_with_sovereignty(
        self, emergence_class: EmergenceClass, sovereignty_score: float
    ) -> EmergenceClass:
        """
        Apply sovereignty gate to emergence classification.
        Emergence that violates non-domination is DISSONANT, not BENEFICIAL.
        """
        if sovereignty_score < 0.4 and emergence_class == EmergenceClass.BENEFICIAL:
            return EmergenceClass.DISSONANT
        return emergence_class


# ---------------------------------------------------------------------------
# EmergenceEvent
# ---------------------------------------------------------------------------

@dataclass
class EmergenceEvent:
    """A classified emergence event at a specific step."""
    timestamp: datetime
    step: int
    emergence_class: EmergenceClass
    emergence_phase: EmergencePhase
    raw_score: float
    sovereignty_score: float

    score_a: Optional[float] = None

    phase_transition: bool = False
    transition_from:  Optional[EmergencePhase] = None
    transition_to:    Optional[EmergencePhase] = None

    def __repr__(self) -> str:
        transition_str = (
            f" [{self.transition_from.value}→{self.transition_to.value}]"
            if self.phase_transition else ""
        )
        return (
            f"EmergenceEvent("
            f"step={self.step}, "
            f"class={self.emergence_class.value}, "
            f"phase={self.emergence_phase.value}{transition_str}, "
            f"score={self.raw_score:.3f}"
            f")"
        )
