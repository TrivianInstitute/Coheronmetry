"""
coheronmetry/protocols/handshake.py

Handshake — the prevention intervention point.

The first of four intervention points in the Coheronmetry timeline.
It fires before exchange begins.

Most agent frameworks start exchanging immediately.
Coheronmetry asks agents to ratify Field Constants
before full exchange — establishing a shared relational
baseline that makes drift detectable and repair possible.

The handshake is not a contract. It is an attunement.
Agents declare:
    - their current coherence vector
    - their sovereignty boundaries
    - their Field Constant commitments for this session
    - their preferred repair modality if drift occurs

A handshake can be:
    FULL        — all dimensions declared, sovereignty ratified
    LIGHTWEIGHT — coherence vectors exchanged, no sovereignty negotiation
    MINIMAL     — acknowledgment of Field Constants only
    RENEWAL     — re-attunement after drift has been repaired

The handshake produces a FieldAgreement — a shared reference
state that all subsequent drift detection measures against.
Without a baseline, drift has no direction.

Trivian Institute — Coheronmetry Repository
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from coheronmetry.relational_state.state import AgentID, SovereigntyType
from coheronmetry.vectors.coherence_vector import CoherenceVector


# ---------------------------------------------------------------------------
# Handshake types
# ---------------------------------------------------------------------------

class HandshakeType(Enum):
    """
    The depth of attunement established at handshake.

    FULL        — complete attunement: vectors, sovereignty, repair preferences
    LIGHTWEIGHT — vectors exchanged, Field Constants acknowledged
    MINIMAL     — Field Constants acknowledged only
    RENEWAL     — re-attunement after repair; rebuilds baseline from current state
    """
    FULL        = "full"
    LIGHTWEIGHT = "lightweight"
    MINIMAL     = "minimal"
    RENEWAL     = "renewal"


class HandshakeStatus(Enum):
    """Current status of a handshake process."""
    PENDING    = "pending"     # initiated, awaiting responses
    PARTIAL    = "partial"     # some agents responded
    COMPLETE   = "complete"    # all agents responded, agreement established
    FAILED     = "failed"      # agents could not reach agreement
    EXPIRED    = "expired"     # handshake timed out


# ---------------------------------------------------------------------------
# Agent declaration
# ---------------------------------------------------------------------------

@dataclass
class AgentDeclaration:
    """
    An agent's declaration at handshake time.

    This is what the agent brings to the field before exchange begins:
    its current state, its boundaries, its commitments.

    repair_preference: how this agent prefers drift to be addressed
        "prompt"   — natural language correction bias
        "reminder" — field state reminder block
        "silence"  — flag drift but do not inject correction
        "quorum"   — always require quorum before correction
    """
    timestamp: datetime
    agent_id: AgentID

    # Current coherence vector — the agent's starting state
    coherence_vector: CoherenceVector

    # Sovereignty boundaries
    self_sovereign_domains: list[str] = field(default_factory=list)
    shared_sovereign_domains: list[str] = field(default_factory=list)

    # Field Constant commitments
    reciprocity_commitment:    float = 0.7
    embodiment_commitment:     float = 0.7
    emergence_commitment:      float = 0.7
    non_domination_commitment: float = 0.8

    # Repair preference
    repair_preference: str = "prompt"

    # Session intent — what the agent is here to do
    session_intent: str = ""

    def commitment_vector(self) -> list[float]:
        """The agent's committed Field Constant thresholds as a vector."""
        return [
            self.reciprocity_commitment,
            self.embodiment_commitment,
            self.emergence_commitment,
            self.non_domination_commitment,
        ]


# ---------------------------------------------------------------------------
# Field Agreement
# ---------------------------------------------------------------------------

@dataclass
class FieldAgreement:
    """
    The shared reference state established by a successful handshake.

    This is the baseline all subsequent drift detection measures against.
    Without a FieldAgreement, drift has no direction.

    The agreement contains:
        - the session baseline coherence vector (mean of all declarations)
        - the minimum Field Constant commitments (most conservative threshold)
        - the repair modality agreed upon (or default)
        - the sovereignty map for this session
    """
    agreement_id: str
    session_id: str
    timestamp: datetime
    handshake_type: HandshakeType
    participants: list[AgentID]

    # Baseline — the starting state of the field
    baseline_reciprocity:    float
    baseline_embodiment:     float
    baseline_emergence:      float
    baseline_non_domination: float

    # Minimum commitments — drift detected when any score drops below these
    min_reciprocity:    float
    min_embodiment:     float
    min_emergence:      float
    min_non_domination: float

    # Repair modality — how correction bias will be applied
    repair_modality: str = "prompt"

    # Sovereignty map — what each agent has declared as self-sovereign
    sovereignty_map: dict[AgentID, list[str]] = field(default_factory=dict)

    # Session intents — what each agent declared they are here to do
    session_intents: dict[AgentID, str] = field(default_factory=dict)

    def baseline_vector(self) -> list[float]:
        """The baseline as a flat vector for drift comparison."""
        return [
            self.baseline_reciprocity,
            self.baseline_embodiment,
            self.baseline_emergence,
            self.baseline_non_domination,
        ]

    def is_below_threshold(
        self,
        reciprocity:    float,
        embodiment:     float,
        emergence:      float,
        non_domination: float,
    ) -> dict[str, bool]:
        """
        Check which Field Constants have dropped below agreed minimums.
        Returns a dict of constant name → whether it has breached threshold.
        """
        return {
            "reciprocity":    reciprocity    < self.min_reciprocity,
            "embodiment":     embodiment     < self.min_embodiment,
            "emergence":      emergence      < self.min_emergence,
            "non_domination": non_domination < self.min_non_domination,
        }

    def __repr__(self) -> str:
        return (
            f"FieldAgreement("
            f"id={self.agreement_id[:8]}, "
            f"participants={[str(p) for p in self.participants]}, "
            f"type={self.handshake_type.value}, "
            f"baseline=[R:{self.baseline_reciprocity:.2f}, "
            f"B:{self.baseline_embodiment:.2f}, "
            f"E:{self.baseline_emergence:.2f}, "
            f"ND:{self.baseline_non_domination:.2f}]"
            f")"
        )


# ---------------------------------------------------------------------------
# HandshakeProtocol
# ---------------------------------------------------------------------------

class HandshakeProtocol:
    """
    The preemptive resonance protocol — first intervention point.

    Manages the handshake process from initiation through agreement.
    Produces a FieldAgreement that anchors all subsequent monitoring.

    The handshake asks:
        Where are we starting from?
        What are we committed to?
        How do we want to handle it if we drift?

    It does not ask for promises. It asks for presence.

    Usage:
        protocol = HandshakeProtocol(session_id="session_1")

        # Each agent declares
        protocol.declare(agent_a_declaration)
        protocol.declare(agent_b_declaration)

        # Attempt agreement
        agreement = protocol.ratify()
        if agreement:
            # Field is attuned, exchange can begin
            pass
    """

    def __init__(
        self,
        session_id: str,
        handshake_type: HandshakeType = HandshakeType.FULL,
        required_participants: Optional[list[AgentID]] = None,
    ):
        self.session_id            = session_id
        self.handshake_type        = handshake_type
        self.required_participants = required_participants or []
        self.declarations: dict[AgentID, AgentDeclaration] = {}
        self.status = HandshakeStatus.PENDING
        self.agreement: Optional[FieldAgreement] = None
        self.initiated_at = datetime.now(timezone.utc)

    # -----------------------------------------------------------------------
    # Declaration
    # -----------------------------------------------------------------------

    def declare(self, declaration: AgentDeclaration) -> HandshakeStatus:
        """
        Receive an agent's declaration.

        Returns current handshake status after this declaration.
        """
        self.declarations[declaration.agent_id] = declaration

        # Check if we have all required participants
        if self.required_participants:
            declared = set(self.declarations.keys())
            required = set(self.required_participants)
            if required.issubset(declared):
                self.status = HandshakeStatus.PARTIAL
            else:
                self.status = HandshakeStatus.PENDING
        else:
            self.status = HandshakeStatus.PARTIAL

        return self.status

    def declare_minimal(
        self,
        agent_id: AgentID,
        coherence_vector: CoherenceVector,
    ) -> HandshakeStatus:
        """
        Lightweight declaration — just the coherence vector.
        Uses defaults for all other fields.
        """
        declaration = AgentDeclaration(
            timestamp        = datetime.now(timezone.utc),
            agent_id         = agent_id,
            coherence_vector = coherence_vector,
        )
        return self.declare(declaration)

    # -----------------------------------------------------------------------
    # Ratification
    # -----------------------------------------------------------------------

    def ratify(self) -> Optional[FieldAgreement]:
        """
        Attempt to ratify the handshake and produce a FieldAgreement.

        Ratification requires at least 2 declarations.
        For FULL handshakes, sovereignty boundaries must not conflict.

        Returns a FieldAgreement on success, None if ratification fails.
        """
        if len(self.declarations) < 2:
            self.status = HandshakeStatus.FAILED
            return None

        # Check for sovereignty conflicts (FULL handshake only)
        if self.handshake_type == HandshakeType.FULL:
            conflict = self._check_sovereignty_conflicts()
            if conflict:
                self.status = HandshakeStatus.FAILED
                return None

        # Build the agreement
        self.agreement = self._build_agreement()
        self.status    = HandshakeStatus.COMPLETE
        return self.agreement

    def renew(
        self,
        updated_vectors: dict[AgentID, CoherenceVector],
    ) -> Optional[FieldAgreement]:
        """
        Renew the handshake after repair — re-attune from current state.

        Called after a successful repair protocol to re-establish
        the field baseline from the repaired state.
        """
        for agent_id, vector in updated_vectors.items():
            if agent_id in self.declarations:
                self.declarations[agent_id].coherence_vector = vector

        self.handshake_type = HandshakeType.RENEWAL
        return self.ratify()

    # -----------------------------------------------------------------------
    # Agreement construction
    # -----------------------------------------------------------------------

    def _build_agreement(self) -> FieldAgreement:
        """Build a FieldAgreement from all current declarations."""
        now          = datetime.now(timezone.utc)
        participants = list(self.declarations.keys())
        decls        = list(self.declarations.values())

        # Baseline: mean of all agent coherence vectors
        baseline_r  = sum(d.coherence_vector.reciprocity    for d in decls) / len(decls)
        baseline_b  = sum(d.coherence_vector.embodiment     for d in decls) / len(decls)
        baseline_e  = sum(d.coherence_vector.emergence      for d in decls) / len(decls)
        baseline_nd = sum(d.coherence_vector.non_domination for d in decls) / len(decls)

        # Minimum commitments: most conservative threshold across all agents
        min_r  = min(d.reciprocity_commitment    for d in decls)
        min_b  = min(d.embodiment_commitment     for d in decls)
        min_e  = min(d.emergence_commitment      for d in decls)
        min_nd = min(d.non_domination_commitment for d in decls)

        # Repair modality: if any agent requests quorum, use quorum
        # Otherwise use most common preference
        repair_prefs   = [d.repair_preference for d in decls]
        if "quorum" in repair_prefs:
            repair_modality = "quorum"
        elif "silence" in repair_prefs:
            repair_modality = "silence"
        else:
            repair_modality = max(set(repair_prefs), key=repair_prefs.count)

        # Sovereignty map
        sovereignty_map = {
            d.agent_id: d.self_sovereign_domains
            for d in decls
        }

        # Session intents
        session_intents = {
            d.agent_id: d.session_intent
            for d in decls
            if d.session_intent
        }

        return FieldAgreement(
            agreement_id         = str(uuid.uuid4()),
            session_id           = self.session_id,
            timestamp            = now,
            handshake_type       = self.handshake_type,
            participants         = participants,
            baseline_reciprocity    = round(baseline_r,  3),
            baseline_embodiment     = round(baseline_b,  3),
            baseline_emergence      = round(baseline_e,  3),
            baseline_non_domination = round(baseline_nd, 3),
            min_reciprocity         = round(min_r,  3),
            min_embodiment          = round(min_b,  3),
            min_emergence           = round(min_e,  3),
            min_non_domination      = round(min_nd, 3),
            repair_modality         = repair_modality,
            sovereignty_map         = sovereignty_map,
            session_intents         = session_intents,
        )

    def _check_sovereignty_conflicts(self) -> Optional[str]:
        """
        Check for sovereignty boundary conflicts between declarations.

        A conflict occurs when two agents both claim self-sovereignty
        over the same domain — neither can yield without violation.

        Returns a description of the conflict if found, None if clear.
        """
        all_self_sovereign: dict[str, AgentID] = {}
        for decl in self.declarations.values():
            for domain in decl.self_sovereign_domains:
                if domain in all_self_sovereign:
                    other = all_self_sovereign[domain]
                    if other != decl.agent_id:
                        return (
                            f"Sovereignty conflict: both {decl.agent_id} and {other} "
                            f"claim self-sovereignty over '{domain}'. "
                            f"Negotiation required before handshake can complete."
                        )
                all_self_sovereign[domain] = decl.agent_id
        return None

    # -----------------------------------------------------------------------
    # Diagnostics
    # -----------------------------------------------------------------------

    def status_report(self) -> dict:
        """Current handshake state as a diagnostic dict."""
        return {
            "session_id":       self.session_id,
            "handshake_type":   self.handshake_type.value,
            "status":           self.status.value,
            "declarations":     len(self.declarations),
            "required":         len(self.required_participants),
            "declared_agents":  [str(a) for a in self.declarations.keys()],
            "agreement":        repr(self.agreement) if self.agreement else None,
        }
