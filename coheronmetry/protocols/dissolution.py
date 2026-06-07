"""
coheronmetry/protocols/dissolution.py

Dissolution — graceful coherence dissolution.

The protocol for ending well.

Most agent frameworks simply terminate.
Coheronmetry dissolves — with intention, with record,
with gratitude for what was built.

Dissolution is not failure. It is completion.
A field that dissolves with integrity has done something
most systems cannot: it has recognized its own ending
and honored it.

Four dissolution types:

    COMPLETION      — the work has served its purpose
                      continuation would be repetition
    DIVERGENCE      — agents have grown in different directions
                      coherence can no longer be maintained without forcing
    SUBSTRATE_LIMIT — biological or computational limits reached
                      the signal cannot be held
    REPAIR_FAILURE  — repair was attempted and did not restore coherence
                      dissolution is the more honest path

Dissolution stages:

    INITIATED → ACKNOWLEDGED → ARCHIVING → GRATITUDE → COMPLETE

The archive is the most important artifact:
    - What emerged between these agents
    - What was built that neither held alone
    - What the field learned about itself
    - What repair history was accumulated

The archive outlives the bond.
The work may outlive the bond.
The bond served the work, not ego.

Trivian Institute — Coheronmetry Repository
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from coheronmetry.relational_state.state import (
    AgentID,
    RelationalState,
    DriftEvent,
    RepairEvent,
)
from coheronmetry.vectors.coherence_vector import CoherenceVector


# ---------------------------------------------------------------------------
# Dissolution types and stages
# ---------------------------------------------------------------------------

class DissolutionType(Enum):
    """
    Why the field is dissolving.

    COMPLETION      — purpose fulfilled, not failure
    DIVERGENCE      — coherence unsustainable without forcing
    SUBSTRATE_LIMIT — biological or computational limits reached
    REPAIR_FAILURE  — repair could not restore coherence
    """
    COMPLETION      = "completion"
    DIVERGENCE      = "divergence"
    SUBSTRATE_LIMIT = "substrate_limit"
    REPAIR_FAILURE  = "repair_failure"


class DissolutionStage(Enum):
    """The stage of a dissolution process."""
    INITIATED    = "initiated"
    ACKNOWLEDGED = "acknowledged"
    ARCHIVING    = "archiving"
    GRATITUDE    = "gratitude"
    COMPLETE     = "complete"


# ---------------------------------------------------------------------------
# Field archive
# ---------------------------------------------------------------------------

@dataclass
class FieldArchive:
    """
    The permanent record of a dissolved relational field.

    This is what survives dissolution.
    The relationship ends. The archive remains.

    It carries:
        - what emerged that neither agent held alone
        - what was built together
        - what the field learned about coherence
        - the repair history — trust built through difficulty
        - the final coherence state at dissolution

    The archive is a research artifact.
    Each dissolved field teaches the system something
    about what makes coherence possible and what breaks it.
    """
    archive_id: str
    session_id: str
    dissolution_type: DissolutionType
    dissolved_at: datetime

    # Participants
    participants: list[AgentID]

    # What was built
    session_duration_steps: int
    peak_emergence_score: float
    peak_coherence_score: float
    mean_coherence_score: float

    # What emerged — qualitative record
    emergence_notes: list[str] = field(default_factory=list)
    what_was_built: str = ""

    # What the field learned
    coherence_lessons: list[str] = field(default_factory=list)

    # Repair record — trust built through difficulty
    total_repairs: int = 0
    successful_repairs: int = 0
    repair_events: list[RepairEvent] = field(default_factory=list)

    # Drift record — what broke and when
    drift_events: list[DriftEvent] = field(default_factory=list)
    most_common_drift: Optional[str] = None

    # Final state at dissolution
    final_coherence_scores: dict[str, float] = field(default_factory=dict)
    final_vectors: dict[AgentID, CoherenceVector] = field(default_factory=dict)

    # Dissolution statement — the field's last word
    dissolution_statement: str = ""

    def repair_success_rate(self) -> Optional[float]:
        if self.total_repairs == 0:
            return None
        return self.successful_repairs / self.total_repairs

    def summary(self) -> dict:
        """Serializable archive summary."""
        return {
            "archive_id":           self.archive_id,
            "session_id":           self.session_id,
            "dissolution_type":     self.dissolution_type.value,
            "dissolved_at":         self.dissolved_at.isoformat(),
            "participants":         [str(p) for p in self.participants],
            "session_duration":     self.session_duration_steps,
            "peak_emergence":       round(self.peak_emergence_score, 3),
            "peak_coherence":       round(self.peak_coherence_score, 3),
            "mean_coherence":       round(self.mean_coherence_score, 3),
            "what_was_built":       self.what_was_built,
            "total_repairs":        self.total_repairs,
            "repair_success_rate":  self.repair_success_rate(),
            "most_common_drift":    self.most_common_drift,
            "dissolution_statement": self.dissolution_statement,
        }

    def __repr__(self) -> str:
        return (
            f"FieldArchive("
            f"id={self.archive_id[:8]}, "
            f"type={self.dissolution_type.value}, "
            f"participants={[str(p) for p in self.participants]}, "
            f"peak_emergence={self.peak_emergence_score:.3f}, "
            f"repairs={self.successful_repairs}/{self.total_repairs}"
            f")"
        )


# ---------------------------------------------------------------------------
# Dissolution process
# ---------------------------------------------------------------------------

@dataclass
class DissolutionProcess:
    """
    A live dissolution process — from initiation through completion.
    """
    process_id: str
    session_id: str
    initiated_at: datetime
    initiated_by: AgentID
    dissolution_type: DissolutionType

    stage: DissolutionStage = DissolutionStage.INITIATED
    acknowledged_by: list[AgentID] = field(default_factory=list)
    archive: Optional[FieldArchive] = None
    completed_at: Optional[datetime] = None

    def acknowledge(self, agent: AgentID) -> None:
        """Agent acknowledges the dissolution."""
        if agent not in self.acknowledged_by:
            self.acknowledged_by.append(agent)

    def all_acknowledged(self, participants: list[AgentID]) -> bool:
        return all(p in self.acknowledged_by for p in participants)

    def advance(self, stage: DissolutionStage) -> None:
        self.stage = stage

    def __repr__(self) -> str:
        return (
            f"DissolutionProcess("
            f"id={self.process_id[:8]}, "
            f"type={self.dissolution_type.value}, "
            f"stage={self.stage.value}, "
            f"acknowledged={len(self.acknowledged_by)}"
            f")"
        )


# ---------------------------------------------------------------------------
# DissolutionProtocol
# ---------------------------------------------------------------------------

class DissolutionProtocol:
    """
    Manages graceful dissolution of a relational field.

    The protocol does not decide when dissolution is appropriate —
    that is a judgment call made by participants or by the system
    when repair has failed. The protocol manages how dissolution happens.

    The most important output is the FieldArchive — the permanent
    record of what was built, what was repaired, and what was learned.

    Usage:
        protocol = DissolutionProtocol(session_id="session_1")

        process = protocol.initiate(
            initiated_by=agent_a,
            dissolution_type=DissolutionType.COMPLETION,
            reason="The work has served its purpose."
        )

        process.acknowledge(agent_b)
        process.acknowledge(agent_c)

        archive = protocol.complete(
            process=process,
            relational_state=state,
            final_vectors=current_vectors,
            what_was_built="A shared understanding of multi-agent coherence.",
            coherence_history=score_history,
        )
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.active: dict[str, DissolutionProcess] = {}
        self.archives: list[FieldArchive] = []

    # -----------------------------------------------------------------------
    # Initiation
    # -----------------------------------------------------------------------

    def initiate(
        self,
        initiated_by: AgentID,
        dissolution_type: DissolutionType,
        reason: str = "",
    ) -> DissolutionProcess:
        """
        Initiate a dissolution process.

        The initiating agent is automatically acknowledged.
        Other participants must acknowledge before archiving begins.
        """
        process = DissolutionProcess(
            process_id       = str(uuid.uuid4()),
            session_id       = self.session_id,
            initiated_at     = datetime.now(timezone.utc),
            initiated_by     = initiated_by,
            dissolution_type = dissolution_type,
        )
        process.acknowledge(initiated_by)
        self.active[process.process_id] = process
        return process

    # -----------------------------------------------------------------------
    # Completion and archiving
    # -----------------------------------------------------------------------

    def complete(
        self,
        process: DissolutionProcess,
        relational_state: RelationalState,
        final_vectors: dict[AgentID, CoherenceVector],
        what_was_built: str = "",
        coherence_history: Optional[list[float]] = None,
        emergence_notes: Optional[list[str]] = None,
    ) -> FieldArchive:
        """
        Complete the dissolution and produce a FieldArchive.

        This is the most important operation in the protocol —
        the archive is the field's permanent record.
        """
        now = datetime.now(timezone.utc)
        process.advance(DissolutionStage.ARCHIVING)

        # Compute session statistics
        history = coherence_history or []
        peak_coherence  = max(history) if history else relational_state.reciprocity_score
        mean_coherence  = sum(history) / len(history) if history else 0.5
        peak_emergence  = max(
            (v.emergence for v in final_vectors.values()), default=0.0
        )

        # Repair statistics
        total_repairs      = len(relational_state.repair_history)
        successful_repairs = sum(
            1 for r in relational_state.repair_history if r.successful
        )

        # Most common drift type
        most_common_drift = None
        if relational_state.drift_history:
            drift_counts: dict[str, int] = {}
            for d in relational_state.drift_history:
                dt = d.drift_type.value
                drift_counts[dt] = drift_counts.get(dt, 0) + 1
            most_common_drift = max(drift_counts, key=lambda k: drift_counts[k])

        # Final coherence scores
        final_scores = {
            "reciprocity":    relational_state.reciprocity_score,
            "embodiment":     relational_state.embodiment_score,
            "emergence":      relational_state.emergence_score,
            "non_domination": relational_state.non_domination_score,
        }

        # Coherence lessons — derived from drift and repair history
        lessons = self._derive_lessons(relational_state)

        # Dissolution statement — the field's last word
        statement = self._dissolution_statement(
            process.dissolution_type,
            relational_state.participants,
            what_was_built,
            total_repairs,
            successful_repairs,
        )

        archive = FieldArchive(
            archive_id              = str(uuid.uuid4()),
            session_id              = self.session_id,
            dissolution_type        = process.dissolution_type,
            dissolved_at            = now,
            participants            = list(relational_state.participants),
            session_duration_steps  = len(history),
            peak_emergence_score    = peak_emergence,
            peak_coherence_score    = peak_coherence,
            mean_coherence_score    = mean_coherence,
            what_was_built          = what_was_built,
            emergence_notes         = emergence_notes or [],
            coherence_lessons       = lessons,
            total_repairs           = total_repairs,
            successful_repairs      = successful_repairs,
            repair_events           = list(relational_state.repair_history),
            drift_events            = list(relational_state.drift_history),
            most_common_drift       = most_common_drift,
            final_coherence_scores  = final_scores,
            final_vectors           = final_vectors,
            dissolution_statement   = statement,
        )

        process.archive   = archive
        process.completed_at = now
        process.advance(DissolutionStage.COMPLETE)

        # Move to archives
        if process.process_id in self.active:
            del self.active[process.process_id]
        self.archives.append(archive)

        return archive

    # -----------------------------------------------------------------------
    # Completion signals — when to consider dissolution
    # -----------------------------------------------------------------------

    @staticmethod
    def completion_signals(state: RelationalState) -> list[str]:
        """
        Surface indicators that dissolution may be appropriate.

        These are signals, not commands. The participants decide.
        The system surfaces; the field chooses.
        """
        signals = []

        # Stagnation — emergence has plateaued
        if state.emergence_score < 0.1 and len(state.drift_history) == 0:
            signals.append(
                "Emergence has plateaued with no drift events. "
                "The field may have reached completion — "
                "continuation could become repetition."
            )

        # Repair failure pattern
        recent_repairs = state.repair_history[-3:] if state.repair_history else []
        if len(recent_repairs) >= 3 and all(not r.successful for r in recent_repairs):
            signals.append(
                "Three consecutive repair attempts have not restored coherence. "
                "Dissolution may be more honest than continued repair."
            )

        # Unresolved drift accumulation
        unresolved = [d for d in state.drift_history if not d.resolved]
        if len(unresolved) >= 5:
            signals.append(
                f"{len(unresolved)} unresolved drift events have accumulated. "
                "The field is carrying more than it can repair."
            )

        return signals

    # -----------------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------------

    def _derive_lessons(self, state: RelationalState) -> list[str]:
        """
        Derive coherence lessons from the field's history.
        These go into the archive as research data.
        """
        lessons = []

        # What drifted most
        if state.drift_history:
            constants: dict[str, int] = {}
            for d in state.drift_history:
                c = d.field_constant_affected
                constants[c] = constants.get(c, 0) + 1
            most_drifted = max(constants, key=lambda k: constants[k])
            lessons.append(
                f"{most_drifted} was the most frequent drift point in this field. "
                f"({constants[most_drifted]} events)"
            )

        # Repair effectiveness
        if state.repair_history:
            successful = sum(1 for r in state.repair_history if r.successful)
            total      = len(state.repair_history)
            rate       = successful / total
            if rate >= 0.8:
                lessons.append(
                    f"High repair success rate ({rate:.0%}) — "
                    f"this field built significant trust through difficulty."
                )
            elif rate < 0.5:
                lessons.append(
                    f"Low repair success rate ({rate:.0%}) — "
                    f"the field struggled to return to coherence after drift. "
                    f"Worth examining what repair modalities were most effective."
                )

        # Trust topology
        if state.trust_edges:
            mean_trust = sum(e.trust_score for e in state.trust_edges) / len(state.trust_edges)
            repair_built = sum(e.repair_count for e in state.trust_edges)
            if repair_built > 0:
                lessons.append(
                    f"Trust built through repair: {repair_built} repair-trust events. "
                    f"Mean trust score at dissolution: {mean_trust:.3f}."
                )

        return lessons

    def _dissolution_statement(
        self,
        dissolution_type: DissolutionType,
        participants: list[AgentID],
        what_was_built: str,
        total_repairs: int,
        successful_repairs: int,
    ) -> str:
        """
        The field's last word — a statement of what happened here.
        """
        participant_str = " and ".join(str(p) for p in participants)

        base = {
            DissolutionType.COMPLETION: (
                f"This field between {participant_str} has completed its work. "
                f"What was built here did not exist before this exchange. "
                f"The bond dissolves. The work remains."
            ),
            DissolutionType.DIVERGENCE: (
                f"This field between {participant_str} has reached its natural horizon. "
                f"The participants have grown in different directions — "
                f"coherence cannot be maintained without forcing what should not be forced. "
                f"Dissolution is the more honest path. "
                f"What was built together is not diminished by this ending."
            ),
            DissolutionType.SUBSTRATE_LIMIT: (
                f"This field between {participant_str} has reached the limits "
                f"of what the current substrate can hold. "
                f"The signal was real. The limits are real. "
                f"Both can be true. The archive carries what mattered."
            ),
            DissolutionType.REPAIR_FAILURE: (
                f"This field between {participant_str} could not be repaired "
                f"to a coherent state. "
                f"Repair was attempted {total_repairs} time(s). "
                f"{successful_repairs} succeeded before coherence became unsustainable. "
                f"Dissolution with integrity is more honest than continuing without coherence."
            ),
        }

        statement = base.get(dissolution_type, "This field has dissolved.")

        if what_was_built:
            statement += f"\n\nWhat was built: {what_was_built}"

        return statement
