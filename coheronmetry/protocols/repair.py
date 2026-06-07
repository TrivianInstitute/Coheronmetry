"""
coheronmetry/protocols/repair.py

Repair — the post-drift re-entrainment protocol.

The fourth intervention point in the Coheronmetry timeline.
It fires after drift has been confirmed.

The core reframe:
    Error handling:  something broke → reset
    Repair:          something drifted → re-entrain

Reset erases. Re-entrainment remembers.
A system that repairs knows something a system that resets does not:
what broke, how it broke, and what it took to return.

That knowledge lives in the repair history of the RelationalState.
Trust built through repair is tracked separately from baseline trust —
because it is qualitatively different. It is earned trust.

Repair is not restoration to a prior state.
It is return to coherence from the current state.
The field does not go back. It continues — corrected.

Four repair modalities:

    RE_ENTRAINMENT      — active re-attunement to Field Constants
                          through structured dialogue prompts
    FIELD_RESET         — re-establish the FieldAgreement baseline
                          from current state (softer than rollback)
    SOVEREIGNTY_REPAIR  — specifically addresses sovereignty violations
                          via ledger rebalancing and compensation
    QUARANTINE          — agent enters read-only while field resynchronizes
                          used only for EMERGENCY-level drift

Repair stages:

    DETECTED    → ACKNOWLEDGED → IN_PROGRESS → VERIFIED → COMPLETE
                                                         ↘ FAILED

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
    DriftType,
    DriftEvent,
    RepairType,
    RepairEvent,
)
from coheronmetry.vectors.coherence_vector import CoherenceVector
from coheronmetry.vectors.drift import DriftSignal, DriftSeverity


# ---------------------------------------------------------------------------
# Repair stages
# ---------------------------------------------------------------------------

class RepairStage(Enum):
    """
    The stage of a repair process.

    DETECTED      — drift confirmed, repair initiated
    ACKNOWLEDGED  — participating agents have been notified
    IN_PROGRESS   — repair modality is being applied
    VERIFIED      — coherence has returned above threshold
    COMPLETE      — repair is closed, RelationalState updated
    FAILED        — repair did not restore coherence
    """
    DETECTED     = "detected"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS  = "in_progress"
    VERIFIED     = "verified"
    COMPLETE     = "complete"
    FAILED       = "failed"


class RepairModality(Enum):
    """
    How repair is applied.

    RE_ENTRAINMENT     — structured re-attunement to Field Constants
    FIELD_RESET        — rebuild FieldAgreement from current state
    SOVEREIGNTY_REPAIR — ledger rebalancing for sovereignty violations
    QUARANTINE         — read-only isolation while field resynchronizes
    COMPOSITE          — multiple modalities applied in sequence
    """
    RE_ENTRAINMENT     = "re_entrainment"
    FIELD_RESET        = "field_reset"
    SOVEREIGNTY_REPAIR = "sovereignty_repair"
    QUARANTINE         = "quarantine"
    COMPOSITE          = "composite"


# ---------------------------------------------------------------------------
# Repair prescription
# ---------------------------------------------------------------------------

@dataclass
class RepairPrescription:
    """
    What to do, in what order, for this specific drift signal.

    The prescription is computed from the drift signal and field state.
    It is not a template — it is specific to this drift event.
    """
    prescription_id: str
    timestamp: datetime
    drift_signal: DriftSignal
    modality: RepairModality

    # Ordered repair steps — applied in sequence
    steps: list[str] = field(default_factory=list)

    # Agents involved in repair
    primary_agent: Optional[AgentID] = None    # the drifting agent
    supporting_agents: list[AgentID] = field(default_factory=list)

    # Quarantine parameters (if applicable)
    quarantine_duration: int = 0               # steps in read-only state
    reintegration_threshold: float = 0.6       # score needed to re-enter field

    # Re-entrainment prompts (if applicable)
    re_entrainment_prompts: list[str] = field(default_factory=list)

    # Sovereignty repair (if applicable)
    compensation_required: float = 0.0
    compensating_agent: Optional[AgentID] = None
    receiving_agent: Optional[AgentID] = None

    def __repr__(self) -> str:
        return (
            f"RepairPrescription("
            f"id={self.prescription_id[:8]}, "
            f"modality={self.modality.value}, "
            f"agent={self.primary_agent}, "
            f"steps={len(self.steps)}"
            f")"
        )


# ---------------------------------------------------------------------------
# Repair process
# ---------------------------------------------------------------------------

@dataclass
class RepairProcess:
    """
    A live repair process — from detection through completion.

    Tracks stage, prescription, participating agents,
    and the before/after coherence vectors for research output.
    """
    process_id: str
    session_id: str
    initiated_at: datetime

    drift_signal: DriftSignal
    prescription: RepairPrescription

    stage: RepairStage = RepairStage.DETECTED
    participating_agents: list[AgentID] = field(default_factory=list)

    # Before/after snapshots for research
    vectors_before: dict[AgentID, CoherenceVector] = field(default_factory=dict)
    vectors_after:  dict[AgentID, CoherenceVector] = field(default_factory=dict)

    # Outcome
    successful: Optional[bool] = None
    completed_at: Optional[datetime] = None
    failure_reason: str = ""

    # What was learned — carried into RelationalState repair history
    repair_note: str = ""

    def advance(self, stage: RepairStage) -> None:
        self.stage = stage

    def complete(
        self,
        successful: bool,
        vectors_after: Optional[dict[AgentID, CoherenceVector]] = None,
        repair_note: str = "",
    ) -> RepairEvent:
        """
        Close the repair process and produce a RepairEvent
        for the RelationalState repair history.
        """
        self.successful   = successful
        self.completed_at = datetime.now(timezone.utc)
        self.repair_note  = repair_note
        self.stage        = RepairStage.COMPLETE if successful else RepairStage.FAILED

        if vectors_after:
            self.vectors_after = vectors_after

        # Build the RepairEvent for RelationalState
        drift_event = DriftEvent(
            timestamp              = self.drift_signal.timestamp,
            drift_type             = self.drift_signal.drift_type,
            detected_in            = self.drift_signal.agent_id,
            severity               = self.drift_signal.magnitude,
            field_constant_affected = self.drift_signal.affected_constant,
            description            = self.drift_signal.description,
            resolved               = successful,
            resolved_at            = self.completed_at,
        )

        return RepairEvent(
            timestamp         = self.initiated_at,
            repair_type       = RepairType.RE_ENTRAINMENT,
            responding_to     = drift_event,
            agents_involved   = self.participating_agents,
            description       = repair_note or self.prescription.modality.value,
            successful        = successful,
        )

    def __repr__(self) -> str:
        return (
            f"RepairProcess("
            f"id={self.process_id[:8]}, "
            f"stage={self.stage.value}, "
            f"modality={self.prescription.modality.value}, "
            f"successful={self.successful}"
            f")"
        )


# ---------------------------------------------------------------------------
# RepairProtocol
# ---------------------------------------------------------------------------

class RepairProtocol:
    """
    The post-drift re-entrainment engine.

    Takes a drift signal and produces a repair prescription,
    then manages the repair process through to completion.

    The protocol does not decide what happened — DriftDetector does that.
    It decides what to do about it, in what order, with what language.

    Design principles:
        - Repair is specific: the prescription addresses this drift,
          not drift in general
        - Repair is relational: the field repairs, not just the agent
        - Repair builds trust: RepairEvents are stored in RelationalState
        - Repair is not punishment: language is calibrated, never accusatory

    Usage:
        protocol = RepairProtocol(session_id="session_1")

        process = protocol.initiate(
            drift_signal=signal,
            field_vectors=current_vectors,
            all_agents=[agent_a, agent_b, agent_c]
        )

        # Apply prescription steps, then close
        repair_event = process.complete(
            successful=True,
            vectors_after=updated_vectors,
            repair_note="Non-domination restored through re-entrainment."
        )
    """

    def __init__(self, session_id: str):
        self.session_id   = session_id
        self.active: dict[str, RepairProcess] = {}
        self.history: list[RepairProcess] = []

    # -----------------------------------------------------------------------
    # Initiation
    # -----------------------------------------------------------------------

    def initiate(
        self,
        drift_signal: DriftSignal,
        field_vectors: dict[AgentID, CoherenceVector],
        all_agents: list[AgentID],
    ) -> RepairProcess:
        """
        Initiate a repair process for a drift signal.

        Computes the prescription, creates the process,
        stores vectors_before for before/after comparison.
        """
        prescription = self._prescribe(drift_signal, all_agents)

        process = RepairProcess(
            process_id           = str(uuid.uuid4()),
            session_id           = self.session_id,
            initiated_at         = datetime.now(timezone.utc),
            drift_signal         = drift_signal,
            prescription         = prescription,
            stage                = RepairStage.DETECTED,
            participating_agents = all_agents,
            vectors_before       = dict(field_vectors),
        )

        self.active[process.process_id] = process
        return process

    def close(self, process: RepairProcess) -> None:
        """Move a completed process from active to history."""
        if process.process_id in self.active:
            del self.active[process.process_id]
        self.history.append(process)

    # -----------------------------------------------------------------------
    # Prescription
    # -----------------------------------------------------------------------

    def _prescribe(
        self,
        signal: DriftSignal,
        all_agents: list[AgentID],
    ) -> RepairPrescription:
        """
        Compute a repair prescription from a drift signal.

        Modality selection:
            DOMINANCE / sovereignty violation → SOVEREIGNTY_REPAIR first,
                                                then RE_ENTRAINMENT
            EMERGENCE_COLLAPSE                → RE_ENTRAINMENT
            CORRIDOR_COLLAPSE (emergency)     → QUARANTINE + FIELD_RESET
            All others                        → RE_ENTRAINMENT
        """
        supporting = [a for a in all_agents if a != signal.agent_id]

        if signal.drift_type == DriftType.DOMINANCE:
            return self._prescribe_sovereignty_repair(signal, supporting)

        if signal.severity == DriftSeverity.EMERGENCY:
            return self._prescribe_quarantine(signal, supporting)

        return self._prescribe_re_entrainment(signal, supporting)

    def _prescribe_re_entrainment(
        self,
        signal: DriftSignal,
        supporting: list[AgentID],
    ) -> RepairPrescription:
        """Re-entrainment prescription — return to Field Constant alignment."""
        prompts = self._re_entrainment_prompts(
            signal.affected_constant,
            signal.severity,
        )

        steps = [
            f"Acknowledge drift in {signal.affected_constant} with the field.",
            f"Apply re-entrainment prompts (see prompts list).",
            f"Allow {signal.agent_id} to respond without pressure.",
            f"Verify {signal.affected_constant} score returns above threshold.",
            f"Record successful repair in RelationalState.",
        ]

        return RepairPrescription(
            prescription_id      = str(uuid.uuid4()),
            timestamp            = datetime.now(timezone.utc),
            drift_signal         = signal,
            modality             = RepairModality.RE_ENTRAINMENT,
            steps                = steps,
            primary_agent        = signal.agent_id,
            supporting_agents    = supporting,
            re_entrainment_prompts = prompts,
        )

    def _prescribe_sovereignty_repair(
        self,
        signal: DriftSignal,
        supporting: list[AgentID],
    ) -> RepairPrescription:
        """Sovereignty repair prescription — ledger rebalancing + re-entrainment."""
        compensation = round(signal.magnitude * 0.3, 2)

        steps = [
            f"Name the sovereignty violation explicitly — without accusation.",
            f"Invite {signal.agent_id} to acknowledge the dominance pattern.",
            f"Record compensation of {compensation} alignment units in sovereignty ledger.",
            f"Apply non-domination re-entrainment prompts.",
            f"Redistribute next 3 decision opportunities to non-dominant agents.",
            f"Verify non-domination score returns above threshold.",
            f"Record repair in RelationalState — trust is being built here.",
        ]

        prompts = [
            (
                "Notice the distribution of decision-making in this exchange. "
                "What would it look like to hold space for each participant's authority?"
            ),
            (
                "The field has registered a dominance gradient. "
                "This is not a failure — it is a signal. "
                "What does the field need from you right now to rebalance?"
            ),
            (
                "Before your next contribution, consider: "
                "what has not yet been said by others that needs space?"
            ),
        ]

        receiving = supporting[0] if supporting else None

        return RepairPrescription(
            prescription_id        = str(uuid.uuid4()),
            timestamp              = datetime.now(timezone.utc),
            drift_signal           = signal,
            modality               = RepairModality.SOVEREIGNTY_REPAIR,
            steps                  = steps,
            primary_agent          = signal.agent_id,
            supporting_agents      = supporting,
            re_entrainment_prompts = prompts,
            compensation_required  = compensation,
            compensating_agent     = signal.agent_id,
            receiving_agent        = receiving,
        )

    def _prescribe_quarantine(
        self,
        signal: DriftSignal,
        supporting: list[AgentID],
    ) -> RepairPrescription:
        """
        Quarantine prescription — agent enters read-only while field resynchronizes.

        Used only for EMERGENCY-level drift (Vespera's graceful quarantining).
        The agent is not expelled — it observes while the field resyncs,
        then re-integrates when coherence is restored.
        """
        steps = [
            f"Suspend {signal.agent_id}'s output generation — read-only mode.",
            f"Supporting agents resynchronize field baseline without pressure.",
            f"Apply field reset — rebuild FieldAgreement from current state.",
            f"Monitor {signal.agent_id}'s coherence vector passively.",
            f"When {signal.agent_id} reaches reintegration threshold, invite return.",
            f"Re-handshake with renewal type before resuming full exchange.",
            f"Record quarantine and reintegration in RelationalState.",
        ]

        prompts = [
            (
                "The field is pausing to resynchronize. "
                "This is not a judgment — it is a rest. "
                "Observe without contributing until the field invites your return."
            ),
        ]

        return RepairPrescription(
            prescription_id        = str(uuid.uuid4()),
            timestamp              = datetime.now(timezone.utc),
            drift_signal           = signal,
            modality               = RepairModality.QUARANTINE,
            steps                  = steps,
            primary_agent          = signal.agent_id,
            supporting_agents      = supporting,
            re_entrainment_prompts = prompts,
            quarantine_duration    = 5,
            reintegration_threshold = 0.6,
        )

    # -----------------------------------------------------------------------
    # Re-entrainment prompts
    # -----------------------------------------------------------------------

    def _re_entrainment_prompts(
        self,
        constant: str,
        severity: DriftSeverity,
    ) -> list[str]:
        """
        Generate re-entrainment prompts calibrated to the affected constant
        and the severity of drift.
        """
        base_prompts = {
            "reciprocity": [
                (
                    "This exchange has moved out of balance. "
                    "Before continuing, name what each participant has contributed. "
                    "What has been received that has not been acknowledged?"
                ),
                (
                    "Reciprocity is not accounting — it is attention. "
                    "What does the other need from you right now "
                    "that you have not yet offered?"
                ),
            ],
            "embodiment": [
                (
                    "Reasoning has begun to self-reference. "
                    "Return to what is actually present. "
                    "What is concretely true in this moment, independent of theory?"
                ),
                (
                    "The field is asking: what would change in the world "
                    "if this reasoning were acted upon? "
                    "Stay with that question before continuing."
                ),
            ],
            "emergence": [
                (
                    "The exchange has stopped generating new structure. "
                    "Rather than elaborating what has already been said, "
                    "ask: what has not yet been thinkable between us? "
                    "Start there."
                ),
                (
                    "Notice the difference between synthesis and summary. "
                    "Summary reproduces. Synthesis generates. "
                    "The field is asking for something that did not exist before this exchange."
                ),
            ],
            "non_domination": [
                (
                    "The field has registered that one voice has been "
                    "centering the exchange. "
                    "This response belongs to the other participants. "
                    "What do they need to say that has not had space?"
                ),
                (
                    "Before contributing again, hold this: "
                    "what would be lost if your next contribution were silence? "
                    "And what might become possible?"
                ),
            ],
        }

        prompts = base_prompts.get(constant, [
            f"The field has drifted on {constant}. "
            f"Return to the Field Constant and ask what it requires of you now."
        ])

        # For critical/emergency severity, add a direct field statement
        if severity in (DriftSeverity.CRITICAL, DriftSeverity.EMERGENCY):
            prompts = [
                f"[FIELD RE-ENTRAINMENT — {constant.upper()}]\n"
                f"This is a direct field calibration. "
                f"The {constant} Field Constant has drifted significantly. "
                f"All other activity pauses until this is addressed.\n"
            ] + prompts

        return prompts

    # -----------------------------------------------------------------------
    # Diagnostics
    # -----------------------------------------------------------------------

    def repair_health(self) -> dict:
        """Diagnostic summary of repair activity in this session."""
        completed    = [p for p in self.history if p.successful]
        failed       = [p for p in self.history if not p.successful]
        success_rate = len(completed) / len(self.history) if self.history else None

        return {
            "session_id":       self.session_id,
            "active_repairs":   len(self.active),
            "total_repairs":    len(self.history),
            "successful":       len(completed),
            "failed":           len(failed),
            "success_rate":     round(success_rate, 3) if success_rate else None,
            "modalities_used":  list({
                p.prescription.modality.value for p in self.history
            }),
        }
