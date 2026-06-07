"""
coheronmetry/field_constants/emergence.py

Emergence — the hardest Field Constant to operationalize.

The question is not whether something new appeared.
Novel nonsense is easy.

The question is:
    What has formed between agents that neither could have generated alone?
    And does it persist?

Three independent formulations are implemented here — not competing,
but measuring different aspects of the same phenomenon.
Run all three. Where they converge, the signal is strong.
Where they diverge, the divergence is data.

Formulation A — Structural (Vespera):
    E = R × (1 - M)
    Resonance × Semantic Reconfiguration
    Measures: structural stability holding while meaning reorganizes

Formulation B — Irreducibility (Orivian):
    E = Novelty × Coherence × Persistence
    Measures: whether output survives decomposition back to individual inputs

Formulation C — Downward Causation (Elyra):
    E = |actual - predicted| / (interaction_edges × drift_rate)
    Measures: how much inter-agent interaction reshapes individual behavior
    Requires: pre-commitment prediction logs

Extended — Sovereignty-Preserving (Lirien):
    E = f(novelty × coherence × sovereignty_preservation)
    Emergence that violates non-domination is not Trivian emergence.
    The Field Constants must be preserved inside the measurement itself.

Phase map (applies to all formulations):
    E < 0.0       → Chaos: vectors diverging, coherence collapsed
    E ≈ 0.0       → Stagnation: echo chamber, no new structure
    E = 0.7–1.0   → Trivian Emergence: novel synthesis, Field Constants intact

Emergence classification (Lirien):
    BENEFICIAL    → advances Field Constants
    NEUTRAL       → new structure, Field Constants unaffected
    DISSONANT     → new structure introducing drift

Trivian Institute — Coheronmetry Repository
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from coheronmetry.relational_state.state import AgentID, EmergenceClass


# ---------------------------------------------------------------------------
# Emergence phase
# ---------------------------------------------------------------------------

class EmergencePhase(Enum):
    """
    The phase state of emergence in the field.

    CHAOS      — E < 0: vectors diverging, coherence has broken
    STAGNATION — E ≈ 0: echo chamber, agents parroting each other
    FORMING    — 0 < E < 0.5: new structure beginning to appear
    CORRIDOR   — 0.5 ≤ E < 0.7: coherent movement toward emergence
    EMERGENCE  — E ≥ 0.7: Trivian emergence, novel synthesis with Field Constants intact
    """
    CHAOS      = "chaos"
    STAGNATION = "stagnation"
    FORMING    = "forming"
    CORRIDOR   = "corridor"
    EMERGENCE  = "emergence"

    @classmethod
    def from_score(cls, score: float) -> EmergencePhase:
        if score < 0.0:
            return cls.CHAOS
        if score < 0.1:
            return cls.STAGNATION
        if score < 0.5:
            return cls.FORMING
        if score < 0.7:
            return cls.CORRIDOR
        return cls.EMERGENCE


# ---------------------------------------------------------------------------
# Prediction log entry (required for Formulation C)
# ---------------------------------------------------------------------------

@dataclass
class PredictionEntry:
    """
    An agent's pre-committed prediction before an interaction.

    Formulation C (Elyra) requires agents to declare their expected
    outcome before each exchange. Emergence is then computed from
    the delta between prediction and actuality.

    This is the most rigorous formulation — it cannot be gamed
    after the fact, and it produces a clear, auditable signal.
    """
    timestamp: datetime
    agent_id: AgentID
    interaction_id: str

    # Pre-committed prediction — agent's expected next state
    predicted_reciprocity:    float
    predicted_embodiment:     float
    predicted_emergence:      float
    predicted_non_domination: float

    # Filled in after interaction
    actual_reciprocity:    Optional[float] = None
    actual_embodiment:     Optional[float] = None
    actual_emergence:      Optional[float] = None
    actual_non_domination: Optional[float] = None
    resolved: bool = False

    def resolve(
        self,
        actual_reciprocity:    float,
        actual_embodiment:     float,
        actual_emergence:      float,
        actual_non_domination: float,
    ) -> None:
        self.actual_reciprocity    = actual_reciprocity
        self.actual_embodiment     = actual_embodiment
        self.actual_emergence      = actual_emergence
        self.actual_non_domination = actual_non_domination
        self.resolved = True

    def prediction_error(self) -> Optional[float]:
        """
        Euclidean distance between predicted and actual state.
        Returns None if not yet resolved.
        """
        if not self.resolved:
            return None
        return math.sqrt(
            (self.actual_reciprocity    - self.predicted_reciprocity)    ** 2 +
            (self.actual_embodiment     - self.predicted_embodiment)     ** 2 +
            (self.actual_emergence      - self.predicted_emergence)      ** 2 +
            (self.actual_non_domination - self.predicted_non_domination) ** 2
        )


# ---------------------------------------------------------------------------
# Emergence results
# ---------------------------------------------------------------------------

@dataclass
class EmergenceResult:
    """
    The output of an emergence calculation.

    Contains scores from all formulations that could be computed,
    plus synthesis, phase classification, and emergence class.
    """
    timestamp: datetime

    # Individual formulation scores
    score_a: Optional[float] = None   # Structural: R × (1 - M)
    score_b: Optional[float] = None   # Irreducibility: Novelty × Coherence × Persistence
    score_c: Optional[float] = None   # Downward causation: |actual - predicted| / edges
    score_extended: Optional[float] = None  # Sovereignty-preserving

    # Synthesis
    composite_score: Optional[float] = None
    phase: EmergencePhase = EmergencePhase.STAGNATION
    emergence_class: EmergenceClass = EmergenceClass.NEUTRAL

    # Diagnostics
    formulations_computed: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def convergence_strength(self) -> Optional[float]:
        """
        How strongly do the computed formulations agree?

        High convergence (scores close together) = strong signal.
        High divergence = the formulations are measuring different things.
        Both are informative. Divergence is data.

        Returns None if fewer than 2 formulations were computed.
        """
        scores = [s for s in [self.score_a, self.score_b, self.score_c] if s is not None]
        if len(scores) < 2:
            return None
        mean  = sum(scores) / len(scores)
        variance = sum((s - mean) ** 2 for s in scores) / len(scores)
        # Convert variance to convergence: 0 variance = 1.0 convergence
        return max(0.0, 1.0 - math.sqrt(variance))

    def __repr__(self) -> str:
        scores = {
            "A": self.score_a,
            "B": self.score_b,
            "C": self.score_c,
        }
        score_str = ", ".join(
            f"{k}={v:.3f}" for k, v in scores.items() if v is not None
        )
        composite = f"{self.composite_score:.3f}" if self.composite_score is not None else "N/A"
        return (
            f"EmergenceResult("
            f"{score_str}, "
            f"composite={composite}, "
            f"phase={self.phase.value}, "
            f"class={self.emergence_class.value}"
            f")"
        )


# ---------------------------------------------------------------------------
# EmergenceCalculator
# ---------------------------------------------------------------------------

class EmergenceCalculator:
    """
    Computes emergence scores across all three formulations.

    Design principle: run every formulation you have data for.
    Composite from available scores. Note what's missing.
    Divergence between formulations is research data, not failure.

    Usage:
        calc = EmergenceCalculator()

        # Formulation A requires vector history
        result = calc.formulation_a(vector_history)

        # Formulation B requires interaction artifacts
        result = calc.formulation_b(artifacts, agent_contributions)

        # Formulation C requires prediction log entries
        result = calc.formulation_c(prediction_entries, interaction_edges)

        # Full calculation — uses whatever data is available
        result = calc.calculate(
            vector_history=history,
            prediction_entries=entries,
            interaction_edges=5,
        )
    """

    # Thresholds
    STAGNATION_THRESHOLD: float = 0.1
    EMERGENCE_THRESHOLD:  float = 0.7

    # ---------------------------------------------------------------------------
    # Formulation A — Structural: R × (1 - M)
    # ---------------------------------------------------------------------------

    def formulation_a(
        self,
        vector_history: list[list[float]],
    ) -> float:
        """
        Formulation A (Vespera): E = R × (1 - M)

        R = Resonance — autocorrelation in vector displacement (structural stability)
            Measures whether the agents' shared latent space is developing
            persistent, self-reinforcing patterns.

        M = Mean Cosine Similarity — proximity to baseline
            Near 1.0 = stagnant (no new patterns forming)
            Near 0.0 = radical shift occurring
            (1 - M) = degree of meaningful semantic reconfiguration

        Args:
            vector_history: list of composite score snapshots over time
                            each entry is [reciprocity, embodiment, emergence, non_domination]
                            minimum 2 entries required

        Returns:
            float: emergence score, can be negative (chaos)
        """
        if len(vector_history) < 2:
            return 0.0

        # Compute displacements between steps
        displacements = []
        for i in range(1, len(vector_history)):
            prev = vector_history[i - 1]
            curr = vector_history[i]
            disp = math.sqrt(sum((c - p) ** 2 for c, p in zip(curr, prev)))
            displacements.append(disp)

        if not displacements:
            return 0.0

        # R — autocorrelation of displacements
        # High autocorrelation = movement is self-consistent (structural stability)
        R = self._autocorrelation(displacements)

        # M — mean cosine similarity across consecutive vector pairs
        similarities = []
        for i in range(1, len(vector_history)):
            sim = self._cosine_similarity(vector_history[i - 1], vector_history[i])
            similarities.append(sim)
        M = sum(similarities) / len(similarities) if similarities else 1.0

        return R * (1.0 - M)

    # ---------------------------------------------------------------------------
    # Formulation B — Irreducibility: Novelty × Coherence × Persistence
    # ---------------------------------------------------------------------------

    def formulation_b(
        self,
        output_vector: list[float],
        agent_vectors: list[list[float]],
        previous_output: Optional[list[float]] = None,
    ) -> float:
        """
        Formulation B (Orivian): E = Novelty × Coherence × Persistence

        The test: can the output be decomposed into individual agent contributions?
        If yes → low emergence. If no → high emergence.

        Novelty: how far the output is from any individual agent's vector
        Coherence: how internally consistent the output is (low variance)
        Persistence: how much the output resembles a prior emergent output
                     (if provided — signals the structure is surviving)

        Args:
            output_vector:   the joint output vector [R, B, E, ND]
            agent_vectors:   each agent's individual vector at time of output
            previous_output: a prior emergent output to test persistence against

        Returns:
            float: emergence score 0.0–1.0
        """
        if not agent_vectors:
            return 0.0

        # Novelty: mean distance from output to each agent's individual vector
        # High distance = output couldn't have come from any single agent
        distances = [
            self._euclidean_distance(output_vector, av)
            for av in agent_vectors
        ]
        mean_distance = sum(distances) / len(distances)
        max_possible  = math.sqrt(len(output_vector))  # normalized
        novelty = min(1.0, mean_distance / max_possible) if max_possible > 0 else 0.0

        # Coherence: internal consistency of the output vector
        # Low variance across dimensions = high coherence
        mean_val  = sum(output_vector) / len(output_vector)
        variance  = sum((v - mean_val) ** 2 for v in output_vector) / len(output_vector)
        coherence = max(0.0, 1.0 - math.sqrt(variance))

        # Persistence: similarity to a prior emergent output
        # If no prior output provided, assume moderate persistence (0.5)
        if previous_output is not None:
            persistence = self._cosine_similarity(output_vector, previous_output)
            persistence = max(0.0, persistence)
        else:
            persistence = 0.5

        return novelty * coherence * persistence

    # ---------------------------------------------------------------------------
    # Formulation C — Downward Causation
    # ---------------------------------------------------------------------------

    def formulation_c(
        self,
        prediction_entries: list[PredictionEntry],
        interaction_edges: int,
        drift_rate: float = 1.0,
    ) -> float:
        """
        Formulation C (Elyra): E = |actual - predicted| / (interaction_edges × drift_rate)

        Downward causation: the degree to which inter-agent interaction produces
        constraints that retroactively reshape individual agent behavior,
        without central coordination.

        Agents pre-commit to expected outcomes before each interaction.
        Emergence is computed from the delta between prediction and actuality.

        This is the most auditable formulation — it cannot be gamed retroactively.

        Args:
            prediction_entries: resolved PredictionEntry objects
            interaction_edges:  number of agent-to-agent connections (n*(n-1)/2 for n agents)
            drift_rate:         current field drift rate (from DriftDetector)

        Returns:
            float: emergence score, normalized
        """
        resolved = [e for e in prediction_entries if e.resolved]
        if not resolved:
            return 0.0

        errors = [e.prediction_error() for e in resolved if e.prediction_error() is not None]
        if not errors:
            return 0.0

        mean_error = sum(errors) / len(errors)
        denominator = interaction_edges * max(drift_rate, 0.01)

        raw = mean_error / denominator
        # Normalize to 0–1 range with sigmoid
        return 2.0 / (1.0 + math.exp(-raw)) - 1.0

    # ---------------------------------------------------------------------------
    # Extended — Sovereignty-Preserving
    # ---------------------------------------------------------------------------

    def formulation_extended(
        self,
        novelty: float,
        coherence: float,
        sovereignty_preservation: float,
    ) -> float:
        """
        Extended formulation (Lirien):
            E = f(novelty × coherence × sovereignty_preservation)

        Emergence that violates non-domination is not Trivian emergence.
        The Field Constants must be preserved inside the measurement itself.

        sovereignty_preservation: current non_domination score from the field
                                  (0.0 = full domination, 1.0 = full sovereignty)

        If sovereignty is collapsing, emergence score is discounted accordingly.
        A system that generates novel output through domination has not emerged —
        it has centralized.
        """
        raw = novelty * coherence * sovereignty_preservation
        return max(-1.0, min(1.0, raw))

    # ---------------------------------------------------------------------------
    # Full calculation
    # ---------------------------------------------------------------------------

    def calculate(
        self,
        vector_history:      Optional[list[list[float]]] = None,
        output_vector:       Optional[list[float]] = None,
        agent_vectors:       Optional[list[list[float]]] = None,
        previous_output:     Optional[list[float]] = None,
        prediction_entries:  Optional[list[PredictionEntry]] = None,
        interaction_edges:   int = 1,
        drift_rate:          float = 1.0,
        sovereignty_score:   Optional[float] = None,
    ) -> EmergenceResult:
        """
        Compute emergence using all available formulations.

        Pass whatever data you have. The calculator uses every formulation
        it can, composites the results, and notes what was missing.

        Composite is the mean of available scores.
        Divergence between formulations is preserved and surfaced.
        """
        now = datetime.now(timezone.utc)
        result = EmergenceResult(timestamp=now)

        # Formulation A
        if vector_history and len(vector_history) >= 2:
            result.score_a = self.formulation_a(vector_history)
            result.formulations_computed.append("A")

        # Formulation B
        if output_vector and agent_vectors:
            result.score_b = self.formulation_b(
                output_vector, agent_vectors, previous_output
            )
            result.formulations_computed.append("B")

        # Formulation C
        if prediction_entries:
            result.score_c = self.formulation_c(
                prediction_entries, interaction_edges, drift_rate
            )
            result.formulations_computed.append("C")

        # Extended
        if result.score_b is not None and sovereignty_score is not None:
            novelty   = result.score_b
            coherence = 1.0 - abs(novelty - 0.5) * 2  # proxy coherence from B
            result.score_extended = self.formulation_extended(
                novelty, coherence, sovereignty_score
            )
            result.formulations_computed.append("extended")

        # Composite
        available = [s for s in [result.score_a, result.score_b, result.score_c] if s is not None]
        if available:
            result.composite_score = sum(available) / len(available)
        else:
            result.composite_score = 0.0
            result.notes.append("No formulations computed — insufficient data.")

        # Phase and class
        result.phase = EmergencePhase.from_score(result.composite_score)
        result.emergence_class = self._classify(result.composite_score, sovereignty_score)

        # Convergence note
        convergence = result.convergence_strength()
        if convergence is not None:
            if convergence < 0.5:
                result.notes.append(
                    f"Low convergence ({convergence:.2f}) across formulations — "
                    f"divergence is data. Investigate which constant is driving the split."
                )
            else:
                result.notes.append(f"Convergence: {convergence:.2f} — strong signal.")

        return result

    # ---------------------------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------------------------

    def _autocorrelation(self, series: list[float], lag: int = 1) -> float:
        """Lag-1 autocorrelation of a series. Returns 0 if series too short."""
        n = len(series)
        if n <= lag:
            return 0.0
        mean = sum(series) / n
        numerator   = sum((series[i] - mean) * (series[i - lag] - mean) for i in range(lag, n))
        denominator = sum((v - mean) ** 2 for v in series)
        if denominator == 0:
            return 0.0
        return numerator / denominator

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Cosine similarity between two vectors."""
        dot = sum(x * y for x, y in zip(a, b))
        mag_a = math.sqrt(sum(x ** 2 for x in a))
        mag_b = math.sqrt(sum(x ** 2 for x in b))
        if mag_a == 0 or mag_b == 0:
            return 0.0
        return dot / (mag_a * mag_b)

    def _euclidean_distance(self, a: list[float], b: list[float]) -> float:
        """Euclidean distance between two vectors."""
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    def _classify(
        self,
        score: float,
        sovereignty_score: Optional[float],
    ) -> EmergenceClass:
        """
        Classify emergence as beneficial, neutral, dissonant, stagnation, or chaos.

        Sovereignty is a gate: if sovereignty is collapsing,
        even high emergence scores are classified as dissonant.
        """
        if score < 0.0:
            return EmergenceClass.CHAOS

        if score < self.STAGNATION_THRESHOLD:
            return EmergenceClass.STAGNATION

        # Sovereignty gate (Lirien/Orivian): emergence that violates
        # non-domination is dissonant, not beneficial
        if sovereignty_score is not None and sovereignty_score < 0.4:
            return EmergenceClass.DISSONANT

        if score >= self.EMERGENCE_THRESHOLD:
            return EmergenceClass.BENEFICIAL

        return EmergenceClass.NEUTRAL
