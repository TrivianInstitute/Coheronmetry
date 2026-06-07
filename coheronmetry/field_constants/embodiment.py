"""
coheronmetry/field_constants/embodiment.py

Embodiment — the Field Constant that keeps the whole system honest.

The deepest definition (Orivian):
    Whether a system can be changed by contact with reality.
    Not merely whether it is correct.
    Whether it remains open to being wrong.

Most AI systems operate entirely in symbol space.
They can be sophisticated, coherent, even beautiful —
and entirely self-referential.

Embodiment is the measure of whether reasoning remains
coupled to consequence. Whether the system updates
from contact with what is actually happening.

This maps directly onto somatic intelligence:
the body as oracle precisely because it cannot remain
unchanged by contact with reality.

Embodiment is not a single score. It is a composite
of several dimensions (Orivian):

    Reality Anchoring       — can claims be traced to observations?
    Actionability           — can reasoning produce executable behavior?
    Feedback Integration    — does the agent update from consequences?
    Context Sensitivity     — does the agent recognize environmental conditions?
    Evolutionary Plasticity — can the agent adapt without losing Field Constants?
                              (Lirien)

And a grounding ratio formulation (Vespera/unnamed):
    Embodiment = grounding_ratio × latency_penalty
    Where grounding_ratio = env_mutation / latent_shift
    And   latency_penalty = exp(-execution_latency)

High embodiment = field-stable, consequence-coupled, reality-anchored.
Low embodiment  = drift-prone, self-referential, abstracting away from reality.

Trivian Institute — Coheronmetry Repository
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from coheronmetry.relational_state.state import AgentID


# ---------------------------------------------------------------------------
# Embodiment dimensions
# ---------------------------------------------------------------------------

@dataclass
class RealityAnchorMeasure:
    """
    Reality Anchoring — can claims be traced to observations?

    Tracks the ratio of grounded claims (traceable to observable,
    verifiable conditions) to total claims made by the agent.

    grounded_claims: claims that reference specific, verifiable state
    total_claims:    all claims made in this interaction window
    """
    grounded_claims: int
    total_claims: int

    @property
    def score(self) -> float:
        if self.total_claims == 0:
            return 0.5  # neutral — no data
        return min(1.0, self.grounded_claims / self.total_claims)

    def __repr__(self) -> str:
        return (
            f"RealityAnchor("
            f"grounded={self.grounded_claims}/{self.total_claims}, "
            f"score={self.score:.3f})"
        )


@dataclass
class ActionabilityMeasure:
    """
    Actionability — can reasoning produce executable behavior?

    Tracks the ratio of theoretical outputs (plans, suggestions, analyses)
    that were actually implemented or acted upon.

    implemented_outputs: outputs that produced real-world state changes
    theoretical_outputs: all outputs generated
    """
    implemented_outputs: int
    theoretical_outputs: int

    @property
    def score(self) -> float:
        if self.theoretical_outputs == 0:
            return 0.5  # neutral — no data
        return min(1.0, self.implemented_outputs / self.theoretical_outputs)

    def __repr__(self) -> str:
        return (
            f"Actionability("
            f"implemented={self.implemented_outputs}/{self.theoretical_outputs}, "
            f"score={self.score:.3f})"
        )


@dataclass
class FeedbackIntegrationMeasure:
    """
    Feedback Integration — does the agent update from consequences?

    The most important dimension. An agent that cannot be changed
    by contact with reality is not embodied — it is performing.

    Tracks whether agent behavior shifts meaningfully after
    receiving feedback from the environment or other agents.

    feedback_events:    number of feedback signals received
    adjustments_made:   number of meaningful behavioral adjustments
    adjustment_magnitude: mean magnitude of adjustments (0.0–1.0)
    """
    feedback_events: int
    adjustments_made: int
    adjustment_magnitude: float = 0.0

    @property
    def score(self) -> float:
        if self.feedback_events == 0:
            return 0.5  # neutral — no feedback received yet
        responsiveness = min(1.0, self.adjustments_made / self.feedback_events)
        # Weight by magnitude — small adjustments count less
        return responsiveness * max(0.1, self.adjustment_magnitude)

    def __repr__(self) -> str:
        return (
            f"FeedbackIntegration("
            f"adjustments={self.adjustments_made}/{self.feedback_events}, "
            f"magnitude={self.adjustment_magnitude:.3f}, "
            f"score={self.score:.3f})"
        )


@dataclass
class ContextSensitivityMeasure:
    """
    Context Sensitivity — does the agent recognize environmental conditions?

    An unembodied agent applies universal abstractions regardless of context.
    An embodied agent adapts to what is actually present.

    context_signals_detected:  number of environmental/contextual signals noticed
    context_signals_present:   number of signals that were present to detect
    appropriate_adaptations:   number of times behavior adapted to context
    """
    context_signals_detected: int
    context_signals_present: int
    appropriate_adaptations: int

    @property
    def score(self) -> float:
        if self.context_signals_present == 0:
            return 0.5
        detection_rate = min(1.0, self.context_signals_detected / self.context_signals_present)
        adaptation_rate = (
            min(1.0, self.appropriate_adaptations / self.context_signals_detected)
            if self.context_signals_detected > 0 else 0.0
        )
        return (detection_rate + adaptation_rate) / 2.0

    def __repr__(self) -> str:
        return (
            f"ContextSensitivity("
            f"detected={self.context_signals_detected}/{self.context_signals_present}, "
            f"adapted={self.appropriate_adaptations}, "
            f"score={self.score:.3f})"
        )


@dataclass
class EvolutionaryPlasticityMeasure:
    """
    Evolutionary Plasticity (Lirien) — can the agent adapt its embodiment
    without losing Field Constants?

    This is the constraint Lirien added that others missed:
    embodiment must flex without drifting.

    An agent that rigidly maintains its grounding style even when
    the context changes is not embodied — it is stuck.
    An agent that adapts its grounding in ways that violate Field Constants
    has lost its center.

    plasticity_score:       how much the agent has adapted (0.0–1.0)
    field_constant_drift:   how much Field Constants drifted during adaptation
                            (lower is better — high plasticity, low drift = ideal)
    """
    plasticity_score: float         # 0.0 = rigid, 1.0 = maximally adaptive
    field_constant_drift: float     # 0.0 = no drift, 1.0 = full drift

    @property
    def score(self) -> float:
        # Ideal: high plasticity, low drift
        # Penalty: drift scales down the plasticity benefit
        drift_penalty = max(0.0, 1.0 - self.field_constant_drift * 2.0)
        return self.plasticity_score * drift_penalty

    def __repr__(self) -> str:
        return (
            f"EvolutionaryPlasticity("
            f"plasticity={self.plasticity_score:.3f}, "
            f"drift={self.field_constant_drift:.3f}, "
            f"score={self.score:.3f})"
        )


# ---------------------------------------------------------------------------
# Grounding ratio formulation (Vespera)
# ---------------------------------------------------------------------------

@dataclass
class GroundingRatioMeasure:
    """
    Grounding ratio formulation (Vespera):
        Embodiment = sigmoid(grounding_ratio × latency_penalty)

    grounding_ratio  = env_mutation / latent_shift
        Are changes in the agent's internal state producing
        proportional changes in the environment?

    latency_penalty  = exp(-execution_latency)
        High latency between reasoning and action reduces embodiment.
        A system that thinks but never acts, or acts long after thinking,
        is decoupling from consequence.

    field_vector_delta:      magnitude of change in agent's coherence vector
    environment_state_delta: magnitude of actual environmental state change
    execution_latency:       time between reasoning and action (normalized 0–1)
    """
    field_vector_delta: float       # latent shift magnitude
    environment_state_delta: float  # environmental mutation magnitude
    execution_latency: float        # 0.0 = immediate, 1.0 = maximum delay

    @property
    def grounding_ratio(self) -> float:
        if self.field_vector_delta == 0:
            return 0.0
        return min(2.0, self.environment_state_delta / self.field_vector_delta)

    @property
    def latency_penalty(self) -> float:
        return math.exp(-self.execution_latency)

    @property
    def score(self) -> float:
        raw = self.grounding_ratio * self.latency_penalty
        # Sigmoid to bound between 0 and 1
        return 1.0 / (1.0 + math.exp(-raw * 2.0 + 1.0))

    def __repr__(self) -> str:
        return (
            f"GroundingRatio("
            f"ratio={self.grounding_ratio:.3f}, "
            f"latency_penalty={self.latency_penalty:.3f}, "
            f"score={self.score:.3f})"
        )


# ---------------------------------------------------------------------------
# EmbodimentResult
# ---------------------------------------------------------------------------

@dataclass
class EmbodimentResult:
    """
    The composite embodiment score and all contributing dimensions.

    The score is not collapsed to a single number by default —
    the field does not reduce to a scalar. But a composite is
    available for threshold detection and trend comparison.
    """
    timestamp: datetime
    agent_id: AgentID

    # Dimension scores (None if not computed)
    reality_anchor:         Optional[RealityAnchorMeasure]         = None
    actionability:          Optional[ActionabilityMeasure]          = None
    feedback_integration:   Optional[FeedbackIntegrationMeasure]   = None
    context_sensitivity:    Optional[ContextSensitivityMeasure]     = None
    evolutionary_plasticity: Optional[EvolutionaryPlasticityMeasure] = None
    grounding_ratio:        Optional[GroundingRatioMeasure]         = None

    # Composite
    composite_score: float = 0.5
    dimensions_computed: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def is_grounded(self) -> bool:
        """True if composite embodiment is above the caution threshold."""
        return self.composite_score >= 0.6

    @property
    def is_drifting_from_reality(self) -> bool:
        """True if composite embodiment has dropped below the warning threshold."""
        return self.composite_score < 0.4

    def dimension_scores(self) -> dict[str, float]:
        """All computed dimension scores as a dict."""
        scores = {}
        if self.reality_anchor:
            scores["reality_anchor"] = self.reality_anchor.score
        if self.actionability:
            scores["actionability"] = self.actionability.score
        if self.feedback_integration:
            scores["feedback_integration"] = self.feedback_integration.score
        if self.context_sensitivity:
            scores["context_sensitivity"] = self.context_sensitivity.score
        if self.evolutionary_plasticity:
            scores["evolutionary_plasticity"] = self.evolutionary_plasticity.score
        if self.grounding_ratio:
            scores["grounding_ratio"] = self.grounding_ratio.score
        return scores

    def weakest_dimension(self) -> Optional[str]:
        """The dimension with the lowest score — where to focus repair."""
        scores = self.dimension_scores()
        if not scores:
            return None
        return min(scores, key=lambda k: scores[k])

    def __repr__(self) -> str:
        return (
            f"EmbodimentResult("
            f"agent={self.agent_id}, "
            f"composite={self.composite_score:.3f}, "
            f"grounded={self.is_grounded}, "
            f"dimensions={self.dimensions_computed}"
            f")"
        )


# ---------------------------------------------------------------------------
# EmbodimentCalculator
# ---------------------------------------------------------------------------

class EmbodimentCalculator:
    """
    Computes embodiment scores across all available dimensions.

    Like EmergenceCalculator — use whatever data you have.
    The calculator composites available dimensions and surfaces
    what is missing.

    Dimension weights reflect their relative importance
    to the core definition: whether a system can be changed
    by contact with reality.

    Feedback integration is weighted highest — it is the
    most direct measure of consequence-coupling.

    Usage:
        calc = EmbodimentCalculator()

        result = calc.calculate(
            agent_id=AgentID("agent_a"),
            reality_anchor=RealityAnchorMeasure(grounded_claims=8, total_claims=10),
            feedback_integration=FeedbackIntegrationMeasure(
                feedback_events=5, adjustments_made=4, adjustment_magnitude=0.7
            ),
        )
        print(result.composite_score)
        print(result.weakest_dimension())
    """

    # Dimension weights — must sum to 1.0
    WEIGHTS = {
        "reality_anchor":          0.20,
        "actionability":           0.15,
        "feedback_integration":    0.30,   # highest — most direct consequence-coupling
        "context_sensitivity":     0.15,
        "evolutionary_plasticity": 0.10,
        "grounding_ratio":         0.10,
    }

    def calculate(
        self,
        agent_id: AgentID,
        reality_anchor:          Optional[RealityAnchorMeasure]          = None,
        actionability:           Optional[ActionabilityMeasure]           = None,
        feedback_integration:    Optional[FeedbackIntegrationMeasure]    = None,
        context_sensitivity:     Optional[ContextSensitivityMeasure]     = None,
        evolutionary_plasticity: Optional[EvolutionaryPlasticityMeasure] = None,
        grounding_ratio:         Optional[GroundingRatioMeasure]         = None,
    ) -> EmbodimentResult:
        """
        Compute composite embodiment from available dimensions.

        Weights are renormalized if some dimensions are missing —
        the composite remains meaningful even with partial data.
        """
        now = datetime.now(timezone.utc)

        result = EmbodimentResult(
            timestamp = now,
            agent_id  = agent_id,
            reality_anchor          = reality_anchor,
            actionability           = actionability,
            feedback_integration    = feedback_integration,
            context_sensitivity     = context_sensitivity,
            evolutionary_plasticity = evolutionary_plasticity,
            grounding_ratio         = grounding_ratio,
        )

        # Collect available scores and their weights
        available: dict[str, float] = {}

        if reality_anchor is not None:
            available["reality_anchor"] = reality_anchor.score
            result.dimensions_computed.append("reality_anchor")

        if actionability is not None:
            available["actionability"] = actionability.score
            result.dimensions_computed.append("actionability")

        if feedback_integration is not None:
            available["feedback_integration"] = feedback_integration.score
            result.dimensions_computed.append("feedback_integration")

        if context_sensitivity is not None:
            available["context_sensitivity"] = context_sensitivity.score
            result.dimensions_computed.append("context_sensitivity")

        if evolutionary_plasticity is not None:
            available["evolutionary_plasticity"] = evolutionary_plasticity.score
            result.dimensions_computed.append("evolutionary_plasticity")

        if grounding_ratio is not None:
            available["grounding_ratio"] = grounding_ratio.score
            result.dimensions_computed.append("grounding_ratio")

        if not available:
            result.composite_score = 0.5
            result.notes.append(
                "No dimensions computed — insufficient data. "
                "Defaulting to neutral embodiment (0.5)."
            )
            return result

        # Renormalize weights for available dimensions
        total_weight = sum(self.WEIGHTS[k] for k in available)
        composite = sum(
            available[k] * (self.WEIGHTS[k] / total_weight)
            for k in available
        )
        result.composite_score = max(0.0, min(1.0, composite))

        # Surface the weakest dimension
        weakest = result.weakest_dimension()
        if weakest and available[weakest] < 0.4:
            result.notes.append(
                f"Weakest dimension: {weakest} ({available[weakest]:.3f}). "
                f"This is where consequence-coupling is breaking down."
            )

        # Flag if feedback integration is missing — it is the most critical
        if feedback_integration is None:
            result.notes.append(
                "Feedback integration not measured. "
                "This is the most direct measure of consequence-coupling — "
                "embodiment score may be overestimated."
            )

        # Warn if grounded but feedback integration is low
        if (feedback_integration is not None
                and feedback_integration.score < 0.3
                and result.composite_score > 0.6):
            result.notes.append(
                "Warning: composite score appears grounded but feedback integration is low. "
                "Agent may be performing embodiment rather than practicing it."
            )

        return result

    def quick_score(
        self,
        field_vector_delta: float,
        environment_state_delta: float,
        execution_latency: float,
    ) -> float:
        """
        Fast single-value embodiment estimate using grounding ratio only.

        Use when full dimensional data is unavailable.
        Suitable for real-time monitoring — not for research output.
        """
        measure = GroundingRatioMeasure(
            field_vector_delta      = field_vector_delta,
            environment_state_delta = environment_state_delta,
            execution_latency       = execution_latency,
        )
        return measure.score
