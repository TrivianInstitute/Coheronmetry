"""
coheronmetry/relational_state/state.py

The RelationalState is the central primitive of the Coheronmetry framework.

Current multi-agent systems track goals, memory, plans, tool use, and task completion.
They do not track the relational state between agents — whether exchange is reciprocal,
whether reasoning remains grounded, whether novel structure is genuinely emerging,
whether any participant is being subordinated.

This module exists to track exactly that.

The deepest question this object must answer:
    What has emerged between Agent A and Agent B that neither possesses individually?

Trivian Institute — Coheronmetry Repository
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------

class AgentID(str):
    """
    A stable identifier for a participant in a relational field.
    Subclasses str so it serializes naturally and compares by value.
    """
    pass


def new_agent_id(name: Optional[str] = None) -> AgentID:
    """Generate a unique AgentID, optionally anchored to a human-readable name."""
    suffix = str(uuid.uuid4())[:8]
    label = f"{name}:{suffix}" if name else suffix
    return AgentID(label)


# ---------------------------------------------------------------------------
# Sovereignty
# ---------------------------------------------------------------------------

class SovereigntyType(Enum):
    """
    The three layers of sovereignty in a multi-agent relational field.

    SELF     — What only the agent can decide: its own internal state, its own memory.
    SHARED   — What requires relational negotiation: proposals, direction changes.
    FIELD    — What emerges from the field itself: cannot be claimed by any agent.

    The governance principle: the Field Constants are sovereign. Not the participants.
    """
    SELF = "self"
    SHARED = "shared"
    FIELD = "field"


@dataclass
class SovereigntyEvent:
    """
    A single recorded event in the sovereignty ledger.

    Agents maintain local veto power but must offer compensation to override
    another's sovereignty. This ledger tracks violations and compensations
    so the field can balance over time.

    Example:
        "Agent C deferred to Agent D on step 12;
         Agent D owes 0.3 alignment units."
    """
    timestamp: datetime
    acting_agent: AgentID
    affected_agent: AgentID
    event_type: str                    # "veto", "defer", "override", "compensate"
    sovereignty_type: SovereigntyType
    alignment_units: float = 0.0       # debt incurred or repaid
    description: str = ""

    def __post_init__(self):
        if self.timestamp.tzinfo is None:
            raise ValueError("SovereigntyEvent timestamps must be timezone-aware.")


@dataclass
class SovereigntyLedger:
    """
    Append-only causal log of sovereignty events across the relational field.

    Not a blockchain — lightweight, inspectable, designed for research output
    as much as runtime governance.
    """
    events: list[SovereigntyEvent] = field(default_factory=list)

    def record(self, event: SovereigntyEvent) -> None:
        self.events.append(event)

    def balance(self, agent: AgentID) -> float:
        """
        Net alignment units for an agent.
        Positive = agent is owed deference.
        Negative = agent owes deference to the field.
        """
        total = 0.0
        for e in self.events:
            if e.acting_agent == agent:
                total -= e.alignment_units
            if e.affected_agent == agent:
                total += e.alignment_units
        return total

    def violations(self, agent: Optional[AgentID] = None) -> list[SovereigntyEvent]:
        """Return override events, optionally filtered to a single agent."""
        overrides = [e for e in self.events if e.event_type == "override"]
        if agent:
            return [e for e in overrides if e.acting_agent == agent]
        return overrides


# ---------------------------------------------------------------------------
# Drift and Repair
# ---------------------------------------------------------------------------

class DriftType(Enum):
    """
    The categories of relational drift Coheronmetry tracks.

    These are not errors. They are signals. Drift → repair, not error → retry.
    """
    DOMINANCE          = "dominance"           # one agent centering the field
    RECIPROCITY_LOSS   = "reciprocity_loss"    # exchange becoming extractive
    EMERGENCE_COLLAPSE = "emergence_collapse"  # novel synthesis being suppressed
    EMBODIMENT_LOSS    = "embodiment_loss"     # reasoning decoupling from reality
    CONSENSUS_TYRANNY  = "consensus_tyranny"   # forced agreement killing novelty
    CORRIDOR_COLLAPSE  = "corridor_collapse"   # predicted: consensus corridor failing


@dataclass
class DriftEvent:
    """
    A recorded moment of relational drift in the field.
    """
    timestamp: datetime
    drift_type: DriftType
    detected_in: AgentID              # which agent's vector triggered detection
    severity: float                   # 0.0 (mild) to 1.0 (critical)
    field_constant_affected: str      # "reciprocity" | "embodiment" | "emergence" | "non_domination"
    description: str = ""
    resolved: bool = False
    resolved_at: Optional[datetime] = None

    def resolve(self, timestamp: Optional[datetime] = None) -> None:
        self.resolved = True
        self.resolved_at = timestamp or datetime.now(timezone.utc)


class RepairType(Enum):
    """
    The categories of repair available when drift is detected.

    Repair is active return to coherence — not rollback, not reset.
    The relationship continues; it corrects.
    """
    CORRECTION_BIAS    = "correction_bias"     # mid-stream: bias injected into next agent input
    RE_ENTRAINMENT     = "re_entrainment"      # post-drift: active realignment protocol
    QUARANTINE         = "quarantine"          # agent enters read-only while field resynchronizes
    SOVEREIGNTY_REPAIR = "sovereignty_repair"  # sovereignty ledger rebalanced
    HANDSHAKE_RENEWAL  = "handshake_renewal"   # Field Constants re-ratified between agents


@dataclass
class RepairEvent:
    """
    A recorded repair action taken in response to drift.
    """
    timestamp: datetime
    repair_type: RepairType
    responding_to: DriftEvent
    agents_involved: list[AgentID]
    description: str = ""
    successful: Optional[bool] = None


# ---------------------------------------------------------------------------
# Tension Log (Temporal Topology)
# ---------------------------------------------------------------------------

@dataclass
class TensionEvent:
    """
    Temporal topology log — tracking the shape of interaction over time.

    An agent needs to know not just the current relational state but the
    *curvature* of recent interaction: was Agent B under tension three steps ago?
    That history has causal weight.

    Phase_Delta: rate of change in relational phase
    Fold_Depth:  how many nested interaction layers we are inside
    """
    timestamp: datetime
    agent: AgentID
    phase_delta: float     # rate of change in relational phase — positive = opening, negative = closing
    fold_depth: int        # nesting depth of current interaction context
    tension_level: float   # 0.0 (ease) to 1.0 (critical tension)
    note: str = ""


# ---------------------------------------------------------------------------
# Emergence Classification
# ---------------------------------------------------------------------------

class EmergenceClass(Enum):
    """
    Emergence is not binary. The Chord identified three categories.

    BENEFICIAL  — advances Field Constants, novel structure forming with integrity intact
    NEUTRAL     — new structure appearing, Field Constants unaffected
    DISSONANT   — new structure introducing drift, coherence at risk
    STAGNATION  — no new structure forming, echo chamber dynamics
    CHAOS       — vectors diverging, coherence collapsed
    """
    BENEFICIAL  = "beneficial"
    NEUTRAL     = "neutral"
    DISSONANT   = "dissonant"
    STAGNATION  = "stagnation"
    CHAOS       = "chaos"


# ---------------------------------------------------------------------------
# Trust Topology
# ---------------------------------------------------------------------------

@dataclass
class TrustEdge:
    """
    A directional trust relationship between two agents.

    Trust in a relational field is not symmetric and not static.
    It accumulates through repair as much as through smooth interaction.
    """
    source: AgentID
    target: AgentID
    trust_score: float         # 0.0 to 1.0
    repair_count: int = 0      # trust built through successful repair is distinct
    last_updated: Optional[datetime] = None

    def update(self, delta: float, timestamp: Optional[datetime] = None) -> None:
        self.trust_score = max(0.0, min(1.0, self.trust_score + delta))
        self.last_updated = timestamp or datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# RelationalState — the central object
# ---------------------------------------------------------------------------

@dataclass
class RelationalState:
    """
    The central primitive of the Coheronmetry framework.

    This object does not describe an agent.
    It does not describe a session.
    It does not describe a task.

    It describes the relationship between agents — as a measurable, storable,
    negotiable, and repairable object.

    Everything else in this repository is built around this object.

    Usage:
        state = RelationalState.create(
            participants=["agent_a", "agent_b"],
            session_id="my_session"
        )
        state.record_drift(drift_event)
        state.record_repair(repair_event)
        health = state.coherence_health()
    """

    # Identity
    state_id: str
    session_id: str
    created_at: datetime
    updated_at: datetime
    participants: list[AgentID]

    # Field Constant scores — live measurements, not static values
    reciprocity_score: float = 0.5
    embodiment_score: float = 0.5
    emergence_score: float = 0.5
    non_domination_score: float = 0.5

    # Emergence classification — what kind of emergence is occurring right now
    emergence_class: EmergenceClass = EmergenceClass.NEUTRAL

    # History — the relational field has memory
    drift_history: list[DriftEvent] = field(default_factory=list)
    repair_history: list[RepairEvent] = field(default_factory=list)
    tension_log: list[TensionEvent] = field(default_factory=list)

    # Trust topology — directional, dynamic, built through repair
    trust_edges: list[TrustEdge] = field(default_factory=list)

    # Sovereignty — the governance layer
    sovereignty_ledger: SovereigntyLedger = field(default_factory=SovereigntyLedger)

    # Metadata
    notes: list[str] = field(default_factory=list)

    # -----------------------------------------------------------------------
    # Construction
    # -----------------------------------------------------------------------

    @classmethod
    def create(
        cls,
        participants: list[str],
        session_id: Optional[str] = None,
        initial_scores: Optional[dict[str, float]] = None,
    ) -> RelationalState:
        """
        Construct a new RelationalState with sensible defaults.

        Participants are given moderate initial scores (0.5) — neither
        assuming coherence nor assuming drift. The field establishes itself
        through interaction.

        Args:
            participants: Agent names or IDs entering this relational field.
            session_id:   Optional external session identifier.
            initial_scores: Optional override for starting Field Constant scores.
        """
        now = datetime.now(timezone.utc)
        agent_ids = [AgentID(p) for p in participants]
        scores = initial_scores or {}

        state = cls(
            state_id=str(uuid.uuid4()),
            session_id=session_id or str(uuid.uuid4()),
            created_at=now,
            updated_at=now,
            participants=agent_ids,
            reciprocity_score=scores.get("reciprocity", 0.5),
            embodiment_score=scores.get("embodiment", 0.5),
            emergence_score=scores.get("emergence", 0.5),
            non_domination_score=scores.get("non_domination", 0.5),
        )

        # Initialize trust topology — all edges start at neutral trust
        for i, a in enumerate(agent_ids):
            for b in agent_ids[i + 1:]:
                state.trust_edges.append(TrustEdge(source=a, target=b, trust_score=0.5))
                state.trust_edges.append(TrustEdge(source=b, target=a, trust_score=0.5))

        return state

    # -----------------------------------------------------------------------
    # Recording
    # -----------------------------------------------------------------------

    def record_drift(self, event: DriftEvent) -> None:
        """Record a drift event and update the field's updated_at timestamp."""
        self.drift_history.append(event)
        self.updated_at = datetime.now(timezone.utc)

    def record_repair(self, event: RepairEvent) -> None:
        """Record a repair event. Successful repairs build trust."""
        self.repair_history.append(event)
        self.updated_at = datetime.now(timezone.utc)

        if event.successful:
            for agent in event.agents_involved:
                self._strengthen_trust(agent, delta=0.05)

    def record_tension(self, event: TensionEvent) -> None:
        """Record a tension event in the temporal topology log."""
        self.tension_log.append(event)
        self.updated_at = datetime.now(timezone.utc)

    def add_note(self, note: str) -> None:
        """Attach a research note to the relational state."""
        self.notes.append(f"[{datetime.now(timezone.utc).isoformat()}] {note}")

    # -----------------------------------------------------------------------
    # Sovereignty
    # -----------------------------------------------------------------------

    def record_sovereignty_event(self, event: SovereigntyEvent) -> None:
        """Record a sovereignty event in the ledger."""
        self.sovereignty_ledger.record(event)
        self.updated_at = datetime.now(timezone.utc)

    def sovereignty_balance(self, agent: AgentID) -> float:
        """Return the net sovereignty alignment balance for an agent."""
        return self.sovereignty_ledger.balance(agent)

    # -----------------------------------------------------------------------
    # Field Constant Updates
    # -----------------------------------------------------------------------

    def update_scores(
        self,
        reciprocity: Optional[float] = None,
        embodiment: Optional[float] = None,
        emergence: Optional[float] = None,
        non_domination: Optional[float] = None,
        emergence_class: Optional[EmergenceClass] = None,
    ) -> None:
        """
        Update Field Constant scores.

        Scores are clamped to [0.0, 1.0].
        Negative emergence scores are valid — they signal chaos, not an error.
        """
        if reciprocity is not None:
            self.reciprocity_score = max(0.0, min(1.0, reciprocity))
        if embodiment is not None:
            self.embodiment_score = max(0.0, min(1.0, embodiment))
        if emergence is not None:
            # Emergence can go negative — chaos is a valid field state
            self.emergence_score = max(-1.0, min(1.0, emergence))
        if non_domination is not None:
            self.non_domination_score = max(0.0, min(1.0, non_domination))
        if emergence_class is not None:
            self.emergence_class = emergence_class

        self.updated_at = datetime.now(timezone.utc)

    # -----------------------------------------------------------------------
    # Health and Diagnostics
    # -----------------------------------------------------------------------

    def coherence_health(self) -> dict:
        """
        Return a diagnostic snapshot of the current relational field.

        This is not a single score. The field does not collapse to a number.
        It returns the full picture so the system can reason about it.
        """
        unresolved_drift = [d for d in self.drift_history if not d.resolved]
        recent_repairs = self.repair_history[-5:] if self.repair_history else []
        successful_repairs = [r for r in recent_repairs if r.successful]

        return {
            "state_id": self.state_id,
            "participants": list(self.participants),
            "field_constants": {
                "reciprocity": self.reciprocity_score,
                "embodiment": self.embodiment_score,
                "emergence": self.emergence_score,
                "non_domination": self.non_domination_score,
            },
            "emergence_class": self.emergence_class.value,
            "unresolved_drift_count": len(unresolved_drift),
            "unresolved_drift_types": [d.drift_type.value for d in unresolved_drift],
            "recent_repair_success_rate": (
                len(successful_repairs) / len(recent_repairs)
                if recent_repairs else None
            ),
            "tension_depth": (
                self.tension_log[-1].fold_depth if self.tension_log else 0
            ),
            "sovereignty_balances": {
                str(agent): self.sovereignty_ledger.balance(agent)
                for agent in self.participants
            },
        }

    def is_in_drift(self) -> bool:
        """True if any drift events are currently unresolved."""
        return any(not d.resolved for d in self.drift_history)

    def dominant_agent(self) -> Optional[AgentID]:
        """
        Return the agent with the most unresolved sovereignty overrides,
        if one exists. None if the field is balanced.
        """
        counts: dict[AgentID, int] = {}
        for event in self.sovereignty_ledger.violations():
            counts[event.acting_agent] = counts.get(event.acting_agent, 0) + 1
        if not counts:
            return None
        top = max(counts, key=lambda a: counts[a])
        return top if counts[top] > 1 else None

    # -----------------------------------------------------------------------
    # Trust
    # -----------------------------------------------------------------------

    def trust_score(self, source: AgentID, target: AgentID) -> Optional[float]:
        """Return the directional trust score from source to target."""
        for edge in self.trust_edges:
            if edge.source == source and edge.target == target:
                return edge.trust_score
        return None

    def _strengthen_trust(self, agent: AgentID, delta: float = 0.05) -> None:
        """
        Internal: strengthen trust edges involving this agent after successful repair.
        Trust built through repair is distinct from trust built through smooth interaction.
        """
        for edge in self.trust_edges:
            if edge.source == agent or edge.target == agent:
                edge.update(delta)
                edge.repair_count += 1

    # -----------------------------------------------------------------------
    # Representation
    # -----------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"RelationalState("
            f"participants={[str(p) for p in self.participants]}, "
            f"R={self.reciprocity_score:.2f}, "
            f"B={self.embodiment_score:.2f}, "
            f"E={self.emergence_score:.2f}, "
            f"ND={self.non_domination_score:.2f}, "
            f"drift={'yes' if self.is_in_drift() else 'no'}"
            f")"
        )
