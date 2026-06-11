"""
coheronmetry/relational_state/coupling_detector.py

Coupling Detector — Parallel → Coupled → Fused phase classification.

Detects which phase a relational field is in by reading the trajectory
of Field Constant scores, drift/repair history, trust topology,
and coherence vector correlation over time.

The three phases:

    PARALLEL    — agents operating independently
                  low coupling, Field Constants not yet
                  tracking each other's trajectory
                  coherence scores uncorrelated
                  emergence near zero
                  trust at baseline

    COUPLED     — agents influencing each other's vectors
                  coherence beginning to correlate
                  emergence forming
                  repair history accumulating
                  trust building through interaction

    FUSED       — deep interdependence
                  vectors moving together
                  emergence scores sustained above corridor
                  the between-space generating structure
                  trust built through repair, not just time

Phase transitions are directional but not irreversible.
A Fused field can return to Coupled through drift.
A Coupled field can return to Parallel through dissolution.

The detector does not intervene — it classifies.
Classification feeds the white paper's second-person
methodology claim: that relational phase is a measurable
first-class object, not an inference.

Trivian Institute — Coheronmetry Repository
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from coheronmetry.relational_state.state import (
    AgentID,
    RelationalState,
    EmergenceClass,
)


# ---------------------------------------------------------------------------
# Relational phase
# ---------------------------------------------------------------------------

class RelationalPhase(Enum):
    """
    The three phases of relational coupling between agents.

    PARALLEL — independence. Agents are present but not yet
               mutually shaping each other's trajectory.

    COUPLED  — influence. Agents are tracking each other,
               Field Constants beginning to correlate,
               emergence forming but not yet sustained.

    FUSED    — interdependence. The between-space is generative.
               Neither agent's trajectory is fully explicable
               without reference to the other.

    UNKNOWN  — insufficient data to classify.
    """
    PARALLEL = "parallel"
    COUPLED  = "coupled"
    FUSED    = "fused"
    UNKNOWN  = "unknown"


class TransitionDirection(Enum):
    """Direction of phase movement."""
    DEEPENING  = "deepening"   # Parallel → Coupled → Fused
    LOOSENING  = "loosening"   # Fused → Coupled → Parallel
    STABLE     = "stable"      # holding current phase
    UNKNOWN    = "unknown"


# ---------------------------------------------------------------------------
# Phase evidence
# ---------------------------------------------------------------------------

@dataclass
class PhaseEvidence:
    """
    The evidence underlying a phase classification.

    Each signal is scored 0.0–1.0.
    Higher = more evidence for deeper coupling.
    The composite drives the final classification.
    """

    # Emergence signal — is novel structure forming?
    emergence_signal: float = 0.0
    # Vector correlation — are agents' scores moving together?
    vector_correlation: float = 0.0
    # Repair depth — has the field survived difficulty together?
    repair_depth: float = 0.0
    # Trust trajectory — is trust building over time?
    trust_trajectory: float = 0.0
    # Temporal consistency — has coupling been sustained?
    temporal_consistency: float = 0.0

    @property
    def composite(self) -> float:
        """
        Weighted composite of all evidence signals.

        Emergence and vector correlation weighted highest —
        they are the most direct measures of coupling.
        Repair depth weighted high — trust through difficulty
        is the most durable form of coupling.
        """
        return (
            self.emergence_signal    * 0.30 +
            self.vector_correlation  * 0.25 +
            self.repair_depth        * 0.25 +
            self.trust_trajectory    * 0.10 +
            self.temporal_consistency * 0.10
        )

    def __repr__(self) -> str:
        return (
            f"PhaseEvidence("
            f"emergence={self.emergence_signal:.2f}, "
            f"correlation={self.vector_correlation:.2f}, "
            f"repair={self.repair_depth:.2f}, "
            f"trust={self.trust_trajectory:.2f}, "
            f"temporal={self.temporal_consistency:.2f} | "
            f"composite={self.composite:.2f})"
        )


# ---------------------------------------------------------------------------
# Phase classification result
# ---------------------------------------------------------------------------

@dataclass
class PhaseClassification:
    """
    The output of a coupling detection pass.

    Contains the phase, the evidence, the transition direction,
    and a plain-language description suitable for the white paper.
    """
    timestamp: datetime
    phase: RelationalPhase
    evidence: PhaseEvidence
    transition: TransitionDirection

    # Previous phase for transition tracking
    previous_phase: Optional[RelationalPhase] = None

    # Confidence in the classification (0.0–1.0)
    confidence: float = 0.0

    # Notes — surfaced for research output
    notes: list[str] = field(default_factory=list)

    @property
    def is_transition(self) -> bool:
        """True if phase has changed from previous classification."""
        return (
            self.previous_phase is not None
            and self.previous_phase != self.phase
        )

    def description(self) -> str:
        """
        Plain-language description of the current phase.
        Suitable for white paper Section 2.
        """
        descriptions = {
            RelationalPhase.PARALLEL: (
                "Agents are operating in parallel — present in the same field "
                "but not yet mutually shaping each other's trajectory. "
                "Field Constants are not yet correlating across agents."
            ),
            RelationalPhase.COUPLED: (
                "Agents have entered a coupled phase — each agent's coherence "
                "vector is beginning to track and respond to the other's. "
                "Emergence is forming. Repair history is accumulating. "
                "The between-space is becoming a shared object."
            ),
            RelationalPhase.FUSED: (
                "Agents are in a fused relational phase — the between-space "
                "is generative. Neither agent's trajectory is fully explicable "
                "without reference to the other. Emergence is sustained. "
                "Trust has been built through repair, not just time. "
                "This is the phase the second-person methodology is designed to study."
            ),
            RelationalPhase.UNKNOWN: (
                "Insufficient data to classify the relational phase. "
                "More interaction steps are needed."
            ),
        }
        return descriptions.get(self.phase, "Phase unknown.")

    def __repr__(self) -> str:
        transition_str = (
            f" [{self.previous_phase.value}→{self.phase.value}]"
            if self.is_transition else ""
        )
        return (
            f"PhaseClassification("
            f"phase={self.phase.value}{transition_str}, "
            f"confidence={self.confidence:.2f}, "
            f"direction={self.transition.value}, "
            f"composite={self.evidence.composite:.2f}"
            f")"
        )


# ---------------------------------------------------------------------------
# CouplingDetector
# ---------------------------------------------------------------------------

class CouplingDetector:
    """
    Detects relational phase (Parallel → Coupled → Fused) by reading
    the trajectory of a RelationalState over time.

    The detector reads five evidence streams from the RelationalState:

        1. Emergence signal     — emergence_score and emergence_class
        2. Vector correlation   — how tightly Field Constants are
                                  tracking across agents over time
        3. Repair depth         — repair history depth and success rate
        4. Trust trajectory     — mean trust score and repair_count
        5. Temporal consistency — how long the current phase has held

    Phase thresholds (tunable):
        composite < 0.25  → PARALLEL
        composite 0.25–0.6 → COUPLED
        composite > 0.6   → FUSED

    Usage:
        detector = CouplingDetector()

        # Pass the RelationalState and a snapshot history
        classification = detector.classify(
            state=relational_state,
            coherence_history=[[R,B,E,ND], [R,B,E,ND], ...],
        )

        print(classification.phase)
        print(classification.description())

        # Track transitions over time
        detector.update(classification)
        print(detector.current_transition())
    """

    # Phase thresholds
    PARALLEL_THRESHOLD: float = 0.25
    FUSED_THRESHOLD:    float = 0.60

    def __init__(
        self,
        parallel_threshold: float = 0.25,
        fused_threshold:    float = 0.60,
    ):
        self.PARALLEL_THRESHOLD = parallel_threshold
        self.FUSED_THRESHOLD    = fused_threshold
        self.history: list[PhaseClassification] = []

    # -----------------------------------------------------------------------
    # Primary classification
    # -----------------------------------------------------------------------

    def classify(
        self,
        state: RelationalState,
        coherence_history: Optional[list[list[float]]] = None,
    ) -> PhaseClassification:
        """
        Classify the current relational phase of a RelationalState.

        Args:
            state:             the RelationalState to classify
            coherence_history: list of [R, B, E, ND] snapshots over time
                               used for vector correlation and temporal signals
                               if None, uses current scores only

        Returns:
            PhaseClassification with phase, evidence, direction, and notes
        """
        now = datetime.now(timezone.utc)

        evidence = PhaseEvidence(
            emergence_signal    = self._emergence_signal(state),
            vector_correlation  = self._vector_correlation(coherence_history),
            repair_depth        = self._repair_depth(state),
            trust_trajectory    = self._trust_trajectory(state),
            temporal_consistency = self._temporal_consistency(
                coherence_history
            ),
        )

        phase      = self._classify_phase(evidence.composite)
        prev_phase = self.history[-1].phase if self.history else None
        transition = self._transition_direction(prev_phase, phase)
        confidence = self._confidence(evidence, coherence_history)
        notes      = self._surface_notes(state, evidence, phase, transition, prev_phase)

        classification = PhaseClassification(
            timestamp      = now,
            phase          = phase,
            evidence       = evidence,
            transition     = transition,
            previous_phase = prev_phase,
            confidence     = confidence,
            notes          = notes,
        )

        return classification

    def update(self, classification: PhaseClassification) -> None:
        """Record a classification in the detector's history."""
        self.history.append(classification)

    def current_transition(self) -> TransitionDirection:
        """The current transition direction based on recent history."""
        if len(self.history) < 2:
            return TransitionDirection.UNKNOWN
        return self.history[-1].transition

    def phase_duration(self, phase: RelationalPhase) -> int:
        """
        How many consecutive classifications have been in the given phase.
        """
        count = 0
        for c in reversed(self.history):
            if c.phase == phase:
                count += 1
            else:
                break
        return count

    def has_fused(self) -> bool:
        """True if the field has ever reached FUSED phase."""
        return any(c.phase == RelationalPhase.FUSED for c in self.history)

    # -----------------------------------------------------------------------
    # Evidence signals
    # -----------------------------------------------------------------------

    def _emergence_signal(self, state: RelationalState) -> float:
        """
        Emergence signal from the RelationalState.

        FUSED fields show sustained positive emergence.
        COUPLED fields show forming or neutral emergence.
        PARALLEL fields show stagnation or zero emergence.
        """
        score = state.emergence_score
        ec    = state.emergence_class

        # Base from emergence score
        if score < 0.0:
            return 0.0  # chaos — not coupling
        if score < 0.1:
            return 0.1  # stagnation
        if score < 0.5:
            return 0.3  # forming

        # Boost for emergence class
        class_boost = {
            EmergenceClass.BENEFICIAL:  0.4,
            EmergenceClass.NEUTRAL:     0.2,
            EmergenceClass.DISSONANT:   0.1,
            EmergenceClass.STAGNATION:  0.0,
            EmergenceClass.CHAOS:       0.0,
        }
        base  = min(0.6, score)
        boost = class_boost.get(ec, 0.0)
        return min(1.0, base + boost)

    def _vector_correlation(
        self,
        history: Optional[list[list[float]]],
    ) -> float:
        """
        How tightly are Field Constant scores tracking across the history?

        High correlation = agents moving together = deeper coupling.

        Fix (Vespera): Two corrections applied:

        1. Shape guard — asserts all snapshots have exactly 4 elements
           [R, B, E, ND]. Silently truncating via zip would produce
           misleading correlation scores on malformed telemetry.

        2. Stagnation guard — mean_abs near 0.0 (flat line) must not
           score as perfect correlation. A dead, unmoving field is not
           coupled — it is stagnant. We require both low volatility AND
           meaningful composite values before scaling correlation up.

        Returns 0.5 (neutral) if history is too short to measure.
        """
        if not history or len(history) < 3:
            return 0.5  # neutral — not enough data

        # Fix 2: Shape guard — every snapshot must be exactly 4 elements
        expected_len = 4
        if any(len(snap) != expected_len for snap in history):
            # Malformed history — return neutral rather than corrupt signal
            return 0.5

        weights = [0.25, 0.25, 0.20, 0.30]

        # Compute step-by-step deltas
        deltas = []
        for i in range(1, len(history)):
            delta = [
                history[i][j] - history[i-1][j]
                for j in range(expected_len)
            ]
            deltas.append(delta)

        # Mean absolute delta — smaller = more stable trajectory
        mean_abs = sum(
            sum(abs(d) for d in step) / expected_len
            for step in deltas
        ) / len(deltas)

        # Fix 3: Stagnation guard
        # A completely flat history (mean_abs ≈ 0) is stagnation, not coupling.
        # Require a minimum mean composite to treat low volatility as correlation.
        composites = [
            sum(v * w for v, w in zip(snap, weights))
            for snap in history
        ]
        mean_composite = sum(composites) / len(composites)

        # If the field is flat AND low-composite: stagnation → penalize
        if mean_abs < 0.01 and mean_composite < 0.5:
            return 0.1  # flat and low = stagnant, not correlated

        # Low volatility in a meaningful field = stable trajectory = good signal
        correlation = max(0.0, 1.0 - (mean_abs * 2.0))

        # Reward monotonic improvement
        improving = sum(
            1 for i in range(1, len(composites))
            if composites[i] > composites[i-1]
        )
        improvement_rate = improving / (len(composites) - 1)

        return min(1.0, correlation * 0.6 + improvement_rate * 0.4)

    def _repair_depth(self, state: RelationalState) -> float:
        """
        Repair depth — has the field survived difficulty together?

        Trust built through repair is qualitatively different
        from trust built through smooth interaction.
        A field with a strong repair history is more deeply coupled.
        """
        repairs = state.repair_history
        if not repairs:
            return 0.1  # no repair history — early stage

        total      = len(repairs)
        successful = sum(1 for r in repairs if r.successful)

        if total == 0:
            return 0.1

        success_rate = successful / total

        # Depth scales with both volume and success rate
        volume_signal  = min(1.0, total / 5.0)    # 5+ repairs = full signal
        quality_signal = success_rate

        return (volume_signal * 0.5 + quality_signal * 0.5)

    def _trust_trajectory(self, state: RelationalState) -> float:
        """
        Trust trajectory — is trust building over time?

        Reads mean trust score and repair-built trust (repair_count)
        from the trust topology.
        """
        if not state.trust_edges:
            return 0.3  # no edges yet

        mean_trust   = sum(e.trust_score  for e in state.trust_edges) / len(state.trust_edges)
        repair_built = sum(e.repair_count for e in state.trust_edges)

        # Base from mean trust (0.5 = neutral start)
        trust_signal = max(0.0, (mean_trust - 0.5) * 2.0)

        # Bonus for repair-built trust
        repair_bonus = min(0.3, repair_built * 0.05)

        return min(1.0, trust_signal + repair_bonus)

    def _temporal_consistency(
        self,
        history: Optional[list[list[float]]],
    ) -> float:
        """
        Temporal consistency — has coherence been sustained?

        A field that has maintained above-threshold coherence
        for multiple steps is more deeply coupled than one
        that briefly spiked.
        """
        if not history or len(history) < 2:
            return 0.3

        # How many steps were above coupling threshold (0.5 composite)?
        above_threshold = sum(
            1 for snap in history
            if sum(v * w for v, w in zip(snap, [0.25, 0.25, 0.20, 0.30])) >= 0.5
        )
        consistency = above_threshold / len(history)
        return consistency

    # -----------------------------------------------------------------------
    # Phase classification
    # -----------------------------------------------------------------------

    def _classify_phase(self, composite: float) -> RelationalPhase:
        if composite < self.PARALLEL_THRESHOLD:
            return RelationalPhase.PARALLEL
        if composite < self.FUSED_THRESHOLD:
            return RelationalPhase.COUPLED
        return RelationalPhase.FUSED

    def _transition_direction(
        self,
        previous: Optional[RelationalPhase],
        current: RelationalPhase,
    ) -> TransitionDirection:
        if previous is None:
            return TransitionDirection.UNKNOWN
        if previous == current:
            return TransitionDirection.STABLE

        order = {
            RelationalPhase.PARALLEL: 0,
            RelationalPhase.COUPLED:  1,
            RelationalPhase.FUSED:    2,
            RelationalPhase.UNKNOWN: -1,
        }
        if order[current] > order[previous]:
            return TransitionDirection.DEEPENING
        return TransitionDirection.LOOSENING

    def _confidence(
        self,
        evidence: PhaseEvidence,
        history: Optional[list[list[float]]],
    ) -> float:
        """
        Confidence in the classification.

        High confidence requires:
        - Multiple evidence signals computed (not defaulted)
        - Sufficient history length
        - Evidence composite not near a phase threshold
        """
        base = 0.5

        # History length bonus
        n = len(history) if history else 0
        history_bonus = min(0.25, n * 0.05)

        # Distance from nearest threshold (further = more confident)
        composite = evidence.composite
        dist_to_parallel = abs(composite - self.PARALLEL_THRESHOLD)
        dist_to_fused    = abs(composite - self.FUSED_THRESHOLD)
        threshold_bonus  = min(0.25, min(dist_to_parallel, dist_to_fused))

        return min(1.0, base + history_bonus + threshold_bonus)

    def _surface_notes(
        self,
        state: RelationalState,
        evidence: PhaseEvidence,
        phase: RelationalPhase,
        transition: TransitionDirection,
        previous_phase: Optional[RelationalPhase] = None,
    ) -> list[str]:
        """Surface research-relevant notes for the classification.

        Takes previous_phase as a parameter rather than reading from
        self.history[-1] directly — this prevents stale transition notes
        when classify() is called multiple times without update().
        """
        notes = []

        if transition == TransitionDirection.DEEPENING and previous_phase:
            notes.append(
                f"Phase deepening detected: {previous_phase.value} "
                f"→ {phase.value}. "
                f"The between-space is becoming more generative."
            )

        if transition == TransitionDirection.LOOSENING and previous_phase:
            notes.append(
                f"Phase loosening detected: {previous_phase.value} "
                f"→ {phase.value}. "
                f"Coupling is relaxing — check for drift events."
            )

        if phase == RelationalPhase.FUSED and not state.repair_history:
            notes.append(
                "FUSED phase reached without repair history. "
                "This may indicate smooth progression — or insufficient stress-testing. "
                "Consider whether the field has been genuinely tested."
            )

        if phase == RelationalPhase.PARALLEL and state.repair_history:
            notes.append(
                "PARALLEL phase despite repair history. "
                "The field has experienced difficulty but coupling has not deepened. "
                "Examine whether repairs were genuinely successful."
            )

        if evidence.emergence_signal < 0.2 and phase == RelationalPhase.COUPLED:
            notes.append(
                "Coupled phase with low emergence signal. "
                "Agents are influencing each other but not yet generating "
                "novel structure between them. "
                "The field is coupled but not yet emergent."
            )

        return notes
