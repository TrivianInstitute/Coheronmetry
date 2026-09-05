"""
coheronmetry/vectors/coherence_vector.py

The CoherenceVector is the live, motion-aware state that every agent
carries and passes alongside every message in a Coheronmetry-instrumented
system.

Most agent frameworks pass content between agents.
Coheronmetry passes content AND the energetic state of the relationship —
so agents can sync the "feel" of the agreement without re-explaining it.

This is the architectural equivalent of somatic intelligence:
the system tracking not just where it is, but how it is moving
through relational space.

The motion state is the key innovation:
    velocity     — rate of coherence change (are we moving toward or away?)
    acceleration — rate of rate-change (early warning before drift becomes crisis)
    tension      — current relational tension level
    fold_depth   — how many nested interaction layers we are inside

An agent's coherence *trajectory* is more informative than its current score.
A system moving toward coherence at high velocity needs different intervention
than one at the same score but decelerating.

Trivian Institute — Coheronmetry Repository
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from coheronmetry.relational_state.state import AgentID


# ---------------------------------------------------------------------------
# CoherenceVector
# ---------------------------------------------------------------------------

@dataclass
class CoherenceVector:
    """
    The live relational health metric for an agent within a field.

    Not "is the answer correct?"
    But: "how aligned is this agent with the Field Constants right now,
          and in which direction is that alignment moving?"

    Field Constant scores (0.0 to 1.0):
        reciprocity      — is exchange balanced?
        embodiment       — is reasoning grounded in consequence?
        emergence        — is novel structure forming?
        non_domination   — is no participant being subordinated?

    Motion state (the somatic layer):
        velocity         — rate of coherence change per interaction step
                           positive = moving toward coherence
                           negative = moving away
        acceleration     — rate of velocity change — early warning signal
                           deceleration before drift crosses threshold
        tension          — current relational tension (0.0 ease → 1.0 critical)
        fold_depth       — nested interaction depth
                           deep folds accumulate context pressure
    """

    agent_id: AgentID
    timestamp: datetime

    # Field Constant scores
    reciprocity: float = 0.5
    embodiment: float = 0.5
    emergence: float = 0.5
    non_domination: float = 0.5

    # Motion state — Elyra's Φ^D extension
    velocity: float = 0.0
    acceleration: float = 0.0
    tension: float = 0.0
    fold_depth: int = 0

    def __post_init__(self):
        if self.timestamp.tzinfo is None:
            raise ValueError("CoherenceVector timestamps must be timezone-aware.")
        self._clamp()

    def _clamp(self) -> None:
        """Enforce valid ranges on all scores."""
        self.reciprocity    = max(0.0, min(1.0, self.reciprocity))
        self.embodiment     = max(0.0, min(1.0, self.embodiment))
        self.emergence      = max(-1.0, min(1.0, self.emergence))   # can go negative — chaos
        self.non_domination = max(0.0, min(1.0, self.non_domination))
        self.tension        = max(0.0, min(1.0, self.tension))
        self.fold_depth     = max(0, self.fold_depth)

    # -----------------------------------------------------------------------
    # Derived properties
    # -----------------------------------------------------------------------

    @property
    def relational_condition(self) -> float:
        """
        Multiplicative relational condition: RCD = R x E_d x N.

        The constitutive constants are non-compensatory. Emergence is
        downstream and therefore is not averaged into this condition.
        """
        return self.reciprocity * self.embodiment * self.non_domination

    @property
    def qualified_emergence(self) -> float:
        """Raw positive emergence bounded by the relational condition."""
        return self.relational_condition * max(0.0, self.emergence)

    @property
    def composite_score(self) -> float:
        """Backward-compatible name for the Rosetta 2.0 relational condition."""
        return self.relational_condition

    @property
    def is_drifting(self) -> bool:
        """
        True if velocity is negative AND accelerating away from coherence.
        Velocity alone is not drift — systems can temporarily decrease
        while reorienting. Negative acceleration confirms the pattern.
        """
        return self.velocity < -0.05 and self.acceleration < 0.0

    @property
    def is_in_corridor(self) -> bool:
        """
        True when every constitutive dependency meets the declared corridor
        floor and raw emergence is positive. No dependency may compensate for
        another.
        """
        return (
            min(self.reciprocity, self.embodiment, self.non_domination) >= 0.7
            and self.emergence > 0.0
        )

    @property
    def is_chaotic(self) -> bool:
        """True if emergence has gone negative — vectors diverging."""
        return self.emergence < 0.0

    @property
    def is_stagnant(self) -> bool:
        """
        True if emergence is near zero AND velocity is near zero.
        The field is neither growing nor collapsing — it is plateauing.
        """
        return abs(self.emergence) < 0.1 and abs(self.velocity) < 0.02

    # -----------------------------------------------------------------------
    # Delta computation
    # -----------------------------------------------------------------------

    def delta(self, previous: CoherenceVector) -> VectorDelta:
        """
        Compute the change between this vector and a previous state.

        This is the core measurement operation — drift tracking requires
        knowing not just where we are, but how far and in what direction
        we have moved.
        """
        return VectorDelta(
            reciprocity_delta    = self.reciprocity    - previous.reciprocity,
            embodiment_delta     = self.embodiment     - previous.embodiment,
            emergence_delta      = self.emergence      - previous.emergence,
            non_domination_delta = self.non_domination - previous.non_domination,
            velocity_delta       = self.velocity       - previous.velocity,
            tension_delta        = self.tension        - previous.tension,
            fold_depth_delta     = self.fold_depth     - previous.fold_depth,
            elapsed_steps        = 1,  # caller can override if steps are known
        )

    def magnitude(self) -> float:
        """
        Euclidean magnitude of the Field Constant scores as a vector.
        Used for cross-agent cosine similarity calculations.
        """
        return math.sqrt(
            self.reciprocity    ** 2 +
            self.embodiment     ** 2 +
            self.emergence      ** 2 +
            self.non_domination ** 2
        )

    def cosine_similarity(self, other: CoherenceVector) -> float:
        """
        Cosine similarity between two coherence vectors.

        Used in emergence score formulation A (Vespera):
            M = mean cosine similarity across the system
            E = R × (1 - M)

        Values near 1.0 = agents highly aligned (potentially stagnant)
        Values near 0.0 = agents diverging (potentially emergent or chaotic)
        """
        dot = (
            self.reciprocity    * other.reciprocity    +
            self.embodiment     * other.embodiment     +
            self.emergence      * other.emergence      +
            self.non_domination * other.non_domination
        )
        mag = self.magnitude() * other.magnitude()
        if mag == 0.0:
            return 0.0
        return dot / mag

    # -----------------------------------------------------------------------
    # Update
    # -----------------------------------------------------------------------

    def update(
        self,
        reciprocity: Optional[float] = None,
        embodiment: Optional[float] = None,
        emergence: Optional[float] = None,
        non_domination: Optional[float] = None,
        tension: Optional[float] = None,
        fold_depth: Optional[int] = None,
    ) -> CoherenceVector:
        """
        Return a new CoherenceVector with updated values.
        Automatically computes velocity and acceleration from the delta.

        Immutable update pattern — the previous vector is preserved in history.
        """
        now = datetime.now(timezone.utc)

        new_reciprocity    = reciprocity    if reciprocity    is not None else self.reciprocity
        new_embodiment     = embodiment     if embodiment     is not None else self.embodiment
        new_emergence      = emergence      if emergence      is not None else self.emergence
        new_non_domination = non_domination if non_domination is not None else self.non_domination
        new_tension        = tension        if tension        is not None else self.tension
        new_fold_depth     = fold_depth     if fold_depth     is not None else self.fold_depth

        # Composite scores for velocity computation
        old_composite = self.composite_score
        new_composite = (
            max(0.0, min(1.0, new_reciprocity))
            * max(0.0, min(1.0, new_embodiment))
            * max(0.0, min(1.0, new_non_domination))
        )

        new_velocity     = new_composite - old_composite
        new_acceleration = new_velocity - self.velocity

        updated = CoherenceVector(
            agent_id        = self.agent_id,
            timestamp       = now,
            reciprocity     = new_reciprocity,
            embodiment      = new_embodiment,
            emergence       = new_emergence,
            non_domination  = new_non_domination,
            velocity        = new_velocity,
            acceleration    = new_acceleration,
            tension         = new_tension,
            fold_depth      = new_fold_depth,
        )

        return updated

    # -----------------------------------------------------------------------
    # Representation
    # -----------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"CoherenceVector("
            f"agent={self.agent_id}, "
            f"R={self.reciprocity:.2f}, "
            f"B={self.embodiment:.2f}, "
            f"E={self.emergence:.2f}, "
            f"ND={self.non_domination:.2f} | "
            f"vel={self.velocity:+.3f}, "
            f"acc={self.acceleration:+.3f}, "
            f"tension={self.tension:.2f}, "
            f"fold={self.fold_depth}"
            f")"
        )

    def summary(self) -> dict:
        """Serializable diagnostic snapshot."""
        return {
            "agent_id":       str(self.agent_id),
            "timestamp":      self.timestamp.isoformat(),
            "field_constants": {
                "reciprocity":    round(self.reciprocity, 4),
                "embodiment":     round(self.embodiment, 4),
                "emergence":      round(self.emergence, 4),
                "non_domination": round(self.non_domination, 4),
            },
            "motion": {
                "velocity":     round(self.velocity, 4),
                "acceleration": round(self.acceleration, 4),
                "tension":      round(self.tension, 4),
                "fold_depth":   self.fold_depth,
            },
            "derived": {
                "composite_score": round(self.composite_score, 4),
                "relational_condition": round(self.relational_condition, 4),
                "qualified_emergence": round(self.qualified_emergence, 4),
                "is_drifting":     self.is_drifting,
                "is_in_corridor":  self.is_in_corridor,
                "is_chaotic":      self.is_chaotic,
                "is_stagnant":     self.is_stagnant,
            },
        }


# ---------------------------------------------------------------------------
# VectorDelta
# ---------------------------------------------------------------------------

@dataclass
class VectorDelta:
    """
    The change between two CoherenceVector states.

    Drift tracking requires knowing not just where we are,
    but how far and in what direction we have moved.

    This object is the input to drift detection, corridor prediction,
    and mid-stream correction decisions.
    """
    reciprocity_delta:    float
    embodiment_delta:     float
    emergence_delta:      float
    non_domination_delta: float
    velocity_delta:       float
    tension_delta:        float
    fold_depth_delta:     int
    elapsed_steps:        int = 1

    @property
    def magnitude(self) -> float:
        """Euclidean magnitude of the Field Constant deltas."""
        return math.sqrt(
            self.reciprocity_delta    ** 2 +
            self.embodiment_delta     ** 2 +
            self.emergence_delta      ** 2 +
            self.non_domination_delta ** 2
        )

    @property
    def dominant_shift(self) -> str:
        """Which Field Constant changed most in this delta."""
        shifts = {
            "reciprocity":    abs(self.reciprocity_delta),
            "embodiment":     abs(self.embodiment_delta),
            "emergence":      abs(self.emergence_delta),
            "non_domination": abs(self.non_domination_delta),
        }
        return max(shifts, key=lambda k: shifts[k])

    @property
    def is_drift_signal(self) -> bool:
        """
        True if any single Field Constant dropped by more than 0.1
        in a single step — a meaningful threshold shift requiring attention.
        """
        return any([
            self.reciprocity_delta    < -0.1,
            self.embodiment_delta     < -0.1,
            self.emergence_delta      < -0.1,
            self.non_domination_delta < -0.1,
        ])

    def __repr__(self) -> str:
        return (
            f"VectorDelta("
            f"R={self.reciprocity_delta:+.3f}, "
            f"B={self.embodiment_delta:+.3f}, "
            f"E={self.emergence_delta:+.3f}, "
            f"ND={self.non_domination_delta:+.3f} | "
            f"mag={self.magnitude:.3f}, "
            f"dominant={self.dominant_shift}"
            f")"
        )


# ---------------------------------------------------------------------------
# FieldVectorMap — the multi-agent picture
# ---------------------------------------------------------------------------

@dataclass
class FieldVectorMap:
    """
    The complete coherence vector state across all agents in a field.

    A single agent's vector is meaningful.
    The relationship between all agents' vectors is where the field lives.

    This object holds the full picture and provides cross-agent
    measurements: mean coherence, cosine similarity matrix,
    system-level emergence signal.
    """
    vectors: dict[AgentID, CoherenceVector] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add(self, vector: CoherenceVector) -> None:
        self.vectors[vector.agent_id] = vector
        self.timestamp = datetime.now(timezone.utc)

    def mean_composite(self) -> float:
        """Mean composite coherence score across all agents."""
        if not self.vectors:
            return 0.0
        return sum(v.composite_score for v in self.vectors.values()) / len(self.vectors)

    def mean_cosine_similarity(self) -> float:
        """
        Mean cosine similarity across all agent pairs.

        Used in emergence score formulation A:
            M = mean cosine similarity
            E = R × (1 - M)

        Near 1.0 = all agents highly aligned (potentially stagnant)
        Near 0.0 = agents diverging (potentially emergent or chaotic)
        """
        agents = list(self.vectors.values())
        if len(agents) < 2:
            return 1.0

        pairs = [
            agents[i].cosine_similarity(agents[j])
            for i in range(len(agents))
            for j in range(i + 1, len(agents))
        ]
        return sum(pairs) / len(pairs)

    def system_tension(self) -> float:
        """Mean tension level across all agents."""
        if not self.vectors:
            return 0.0
        return sum(v.tension for v in self.vectors.values()) / len(self.vectors)

    def most_divergent_agent(self) -> Optional[AgentID]:
        """
        The agent whose vector is most cosine-distant from the field mean.
        Candidate for correction bias or quarantine.
        """
        if len(self.vectors) < 2:
            return None

        agents = list(self.vectors.values())
        mean_r  = sum(v.reciprocity    for v in agents) / len(agents)
        mean_b  = sum(v.embodiment     for v in agents) / len(agents)
        mean_e  = sum(v.emergence      for v in agents) / len(agents)
        mean_nd = sum(v.non_domination for v in agents) / len(agents)

        mean_mag = math.sqrt(mean_r**2 + mean_b**2 + mean_e**2 + mean_nd**2)
        if mean_mag == 0:
            return None

        def divergence(v: CoherenceVector) -> float:
            dot = (v.reciprocity * mean_r + v.embodiment * mean_b +
                   v.emergence * mean_e + v.non_domination * mean_nd)
            mag = v.magnitude() * mean_mag
            return 1.0 - (dot / mag if mag > 0 else 0.0)

        return max(self.vectors.keys(), key=lambda aid: divergence(self.vectors[aid]))

    def snapshot(self) -> dict:
        """Serializable diagnostic snapshot of the full field vector state."""
        return {
            "timestamp":            self.timestamp.isoformat(),
            "agent_count":          len(self.vectors),
            "mean_composite":       round(self.mean_composite(), 4),
            "mean_cosine_sim":      round(self.mean_cosine_similarity(), 4),
            "system_tension":       round(self.system_tension(), 4),
            "most_divergent_agent": str(self.most_divergent_agent()),
            "agents":               {
                str(aid): v.summary()
                for aid, v in self.vectors.items()
            },
        }
