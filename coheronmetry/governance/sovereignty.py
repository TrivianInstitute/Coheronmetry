"""
coheronmetry/governance/sovereignty.py

Sovereignty governance — the hardest architectural problem in Coheronmetry,
and the first priority for the repository.

Without this, everything else is orchestration wearing Trivian clothes.

The paradox:
    Coordination creates pressure toward centralization.
    Centralization violates non-domination.

Three failure modes to avoid:
    Consensus Tyranny    — all agents must agree → novelty dies, emergence collapses
    Coordinator Tyranny  — one agent resolves disagreement → non-domination collapses
    Independence Tyranny — all agents remain sovereign → coordination fails

The solution: Sovereign Participation.
    Sovereignty retained.
    Authority delegated temporarily.
    Delegation revocable.
    Never: authority transferred.

The governance principle:
    The Field Constants are sovereign. Not the participants.
    Instead of asking which agent wins,
    ask which option maximizes Field Constant preservation.
    No participant holds authority over the outcome. The invariants do.

Sovereignty taxonomy (Orivian):
    SELF       — what only the agent can decide: its own state, its own memory
    SHARED     — what requires relational negotiation: proposals, direction changes
    FIELD      — what emerges from the field itself: claimed by no agent

Sovereignty compensation economy (Elyra):
    Agents maintain local veto power but must offer compensation to override
    another's sovereignty. A lightweight causal ledger tracks violations
    and compensations so the field can balance over time.

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
    SovereigntyType,
    SovereigntyEvent,
    SovereigntyLedger,
)
from coheronmetry.vectors.coherence_vector import CoherenceVector, FieldVectorMap


# ---------------------------------------------------------------------------
# Sovereignty assertion
# ---------------------------------------------------------------------------

class SovereigntyAssertion(Enum):
    """
    The types of sovereignty assertion an agent can make.

    VETO         — agent refuses a proposed action; sovereignty is exercised
    DEFER        — agent voluntarily yields on this decision; earns future balance
    DELEGATE     — agent temporarily grants decision authority (revocable)
    REVOKE       — agent withdraws a prior delegation
    COMPENSATE   — agent offers alignment units to another whose sovereignty was overridden
    INVOKE_FIELD — agent appeals to Field Constant preservation as the deciding criterion
    """
    VETO           = "veto"
    DEFER          = "defer"
    DELEGATE       = "delegate"
    REVOKE         = "revoke"
    COMPENSATE     = "compensate"
    INVOKE_FIELD   = "invoke_field"


@dataclass
class SovereigntyAction:
    """
    A structured sovereignty action taken by an agent.

    This is the input to the sovereignty governance layer.
    The layer evaluates the action, records it, and determines
    whether it is valid within the current field state.
    """
    action_id: str
    timestamp: datetime
    acting_agent: AgentID
    assertion: SovereigntyAssertion
    sovereignty_type: SovereigntyType

    # What this action is about
    subject: str                        # description of the proposal or decision
    affected_agents: list[AgentID]      # who is affected by this action

    # For VETO/INVOKE_FIELD: which Field Constant is at stake
    field_constant: Optional[str] = None

    # For DEFER/COMPENSATE: alignment units offered
    alignment_units: float = 0.0

    # For DELEGATE/REVOKE: which agent receives/loses delegated authority
    delegate_target: Optional[AgentID] = None

    # Rationale — agents must explain sovereignty actions
    rationale: str = ""

    def __post_init__(self):
        if self.timestamp.tzinfo is None:
            raise ValueError("SovereigntyAction timestamps must be timezone-aware.")

    @classmethod
    def create(
        cls,
        acting_agent: AgentID,
        assertion: SovereigntyAssertion,
        sovereignty_type: SovereigntyType,
        subject: str,
        affected_agents: Optional[list[AgentID]] = None,
        field_constant: Optional[str] = None,
        alignment_units: float = 0.0,
        delegate_target: Optional[AgentID] = None,
        rationale: str = "",
    ) -> SovereigntyAction:
        return cls(
            action_id        = str(uuid.uuid4())[:8],
            timestamp        = datetime.now(timezone.utc),
            acting_agent     = acting_agent,
            assertion        = assertion,
            sovereignty_type = sovereignty_type,
            subject          = subject,
            affected_agents  = affected_agents or [],
            field_constant   = field_constant,
            alignment_units  = alignment_units,
            delegate_target  = delegate_target,
            rationale        = rationale,
        )


# ---------------------------------------------------------------------------
# Sovereignty evaluation
# ---------------------------------------------------------------------------

class SovereigntyStatus(Enum):
    """Outcome of a sovereignty evaluation."""
    VALID          = "valid"           # action is within field norms, proceed
    VALID_WITH_DEBT = "valid_with_debt" # valid but incurs alignment debt
    REQUIRES_QUORUM = "requires_quorum" # shared/field decision needs broader ratification
    BLOCKED        = "blocked"         # action violates Field Constants
    PENDING        = "pending"         # awaiting quorum or compensation


@dataclass
class SovereigntyEvaluation:
    """
    The result of evaluating a sovereignty action.

    Contains the status, the reasoning, any debt incurred,
    and guidance for next steps.
    """
    action: SovereigntyAction
    status: SovereigntyStatus
    reasoning: str
    alignment_debt: float = 0.0        # debt incurred by this action
    quorum_required: Optional[int] = None  # how many agents must ratify
    blocking_constant: Optional[str] = None  # which Field Constant was violated

    def is_valid(self) -> bool:
        return self.status in (SovereigntyStatus.VALID, SovereigntyStatus.VALID_WITH_DEBT)

    def requires_quorum(self) -> bool:
        return self.status == SovereigntyStatus.REQUIRES_QUORUM

    def __repr__(self) -> str:
        return (
            f"SovereigntyEvaluation("
            f"agent={self.action.acting_agent}, "
            f"assertion={self.action.assertion.value}, "
            f"status={self.status.value}, "
            f"debt={self.alignment_debt:.2f}"
            f")"
        )


# ---------------------------------------------------------------------------
# Quorum
# ---------------------------------------------------------------------------

@dataclass
class QuorumProposal:
    """
    A proposal requiring ratification from multiple agents.

    In a Trivian field, major decisions are not made by a coordinator.
    They are ratified through distributed consent — a quorum process
    that preserves each agent's sovereignty while enabling collective action.

    This is not majority voting. It is resonance checking:
        - Each agent evaluates against its own Field Constant scores
        - The proposal passes if Field Constant preservation is achieved
          across the required threshold of participants
    """
    proposal_id: str
    timestamp: datetime
    proposing_agent: AgentID
    subject: str
    rationale: str

    # Quorum parameters
    required_agents: list[AgentID]      # who must ratify
    threshold: float = 0.67             # proportion required (default: 2/3)

    # Ratification state
    ratifications: dict[AgentID, bool] = field(default_factory=dict)
    vetoes: dict[AgentID, str] = field(default_factory=dict)  # agent → rationale

    # Outcome
    resolved: bool = False
    passed: bool = False
    resolved_at: Optional[datetime] = None

    @classmethod
    def create(
        cls,
        proposing_agent: AgentID,
        subject: str,
        rationale: str,
        required_agents: list[AgentID],
        threshold: float = 0.67,
    ) -> QuorumProposal:
        return cls(
            proposal_id     = str(uuid.uuid4())[:8],
            timestamp       = datetime.now(timezone.utc),
            proposing_agent = proposing_agent,
            subject         = subject,
            rationale       = rationale,
            required_agents = required_agents,
            threshold       = threshold,
        )

    def ratify(self, agent: AgentID) -> None:
        """Agent ratifies the proposal."""
        if agent in self.required_agents:
            self.ratifications[agent] = True

    def veto(self, agent: AgentID, rationale: str = "") -> None:
        """Agent vetoes the proposal. Veto must include rationale."""
        if agent in self.required_agents:
            self.vetoes[agent] = rationale or "No rationale provided."
            self.ratifications[agent] = False

    def resolve(self) -> bool:
        """
        Attempt to resolve the quorum.

        Resolution requires:
            - All required agents have responded (ratified or vetoed)
            - Proportion of ratifications meets threshold
            - No uncompensated vetoes remain (sovereignty preserved)

        Returns True if resolved (whether passed or not).
        """
        all_responded = all(
            a in self.ratifications or a in self.vetoes
            for a in self.required_agents
        )
        if not all_responded:
            return False

        ratification_count = sum(1 for v in self.ratifications.values() if v)
        total = len(self.required_agents)
        proportion = ratification_count / total if total > 0 else 0.0

        self.passed = (proportion >= self.threshold) and (len(self.vetoes) == 0)
        self.resolved = True
        self.resolved_at = datetime.now(timezone.utc)
        return True

    @property
    def participation_rate(self) -> float:
        responded = len(self.ratifications) + len(self.vetoes)
        total = len(self.required_agents)
        return responded / total if total > 0 else 0.0

    def __repr__(self) -> str:
        return (
            f"QuorumProposal("
            f"id={self.proposal_id}, "
            f"proposer={self.proposing_agent}, "
            f"resolved={self.resolved}, "
            f"passed={self.passed}, "
            f"participation={self.participation_rate:.0%}"
            f")"
        )


# ---------------------------------------------------------------------------
# SovereigntyGovernor
# ---------------------------------------------------------------------------

class SovereigntyGovernor:
    """
    The sovereignty governance layer for a Coheronmetry-instrumented field.

    Evaluates sovereignty actions, manages quorum processes, tracks
    the sovereignty ledger, and enforces Field Constant preservation
    as the ultimate arbiter of all decisions.

    The governor does not decide. The Field Constants decide.
    The governor implements the decision mechanism.

    Usage:
        governor = SovereigntyGovernor(
            participants=[agent_a, agent_b, agent_c],
            ledger=state.sovereignty_ledger
        )

        # Agent asserts a veto
        action = SovereigntyAction.create(
            acting_agent=agent_a,
            assertion=SovereigntyAssertion.VETO,
            sovereignty_type=SovereigntyType.SHARED,
            subject="Proposal to change interaction direction",
            field_constant="emergence",
            rationale="This would suppress the synthesis forming between us."
        )
        evaluation = governor.evaluate(action, field_map)
    """

    def __init__(
        self,
        participants: list[AgentID],
        ledger: Optional[SovereigntyLedger] = None,
        quorum_threshold: float = 0.67,
    ):
        self.participants      = participants
        self.ledger            = ledger or SovereigntyLedger()
        self.quorum_threshold  = quorum_threshold
        self.active_proposals: dict[str, QuorumProposal] = {}
        self.action_log: list[SovereigntyAction] = []

    # -----------------------------------------------------------------------
    # Core evaluation
    # -----------------------------------------------------------------------

    def evaluate(
        self,
        action: SovereigntyAction,
        field_map: Optional[FieldVectorMap] = None,
    ) -> SovereigntyEvaluation:
        """
        Evaluate a sovereignty action against Field Constant preservation.

        The evaluation asks:
            1. Is this a SELF, SHARED, or FIELD decision?
            2. Does it preserve or violate Field Constants?
            3. Does it require quorum?
            4. What alignment debt does it incur?

        The Field Constants are sovereign. Not the participants.
        """
        self.action_log.append(action)

        # SELF decisions: always valid — no agent can be overridden on self-sovereignty
        if action.sovereignty_type == SovereigntyType.SELF:
            return self._evaluate_self(action)

        # FIELD decisions: always require quorum — no single agent claims field sovereignty
        if action.sovereignty_type == SovereigntyType.FIELD:
            return self._evaluate_field(action)

        # SHARED decisions: evaluated against Field Constants and ledger balance
        return self._evaluate_shared(action, field_map)

    def _evaluate_self(self, action: SovereigntyAction) -> SovereigntyEvaluation:
        """
        SELF sovereignty: what only the agent can decide.
        Always valid. Records in ledger for field awareness.
        """
        self._record(action, alignment_units=0.0)
        return SovereigntyEvaluation(
            action    = action,
            status    = SovereigntyStatus.VALID,
            reasoning = (
                f"Self-sovereignty assertion by {action.acting_agent}. "
                f"No agent can be overridden on decisions within their own domain. "
                f"Recorded for field awareness."
            ),
        )

    def _evaluate_field(self, action: SovereigntyAction) -> SovereigntyEvaluation:
        """
        FIELD sovereignty: what emerges from the field itself.
        Always requires quorum — cannot be claimed by any agent.
        """
        return SovereigntyEvaluation(
            action          = action,
            status          = SovereigntyStatus.REQUIRES_QUORUM,
            reasoning       = (
                f"Field-level sovereignty cannot be claimed by any single agent. "
                f"Quorum required from all participants: {[str(p) for p in self.participants]}."
            ),
            quorum_required = len(self.participants),
        )

    def _evaluate_shared(
        self,
        action: SovereigntyAction,
        field_map: Optional[FieldVectorMap],
    ) -> SovereigntyEvaluation:
        """
        SHARED sovereignty: what requires relational negotiation.
        Evaluated against Field Constants, ledger balance, and action type.
        """
        # VETO: always valid on shared decisions — sovereignty preserved
        # But incurs alignment debt if balance is already negative
        if action.assertion == SovereigntyAssertion.VETO:
            return self._evaluate_veto(action, field_map)

        # INVOKE_FIELD: appeal to Field Constants as arbiter
        if action.assertion == SovereigntyAssertion.INVOKE_FIELD:
            return self._evaluate_field_invocation(action, field_map)

        # DEFER: voluntary yield — earns positive balance
        if action.assertion == SovereigntyAssertion.DEFER:
            debt = -action.alignment_units  # negative debt = credit
            self._record(action, alignment_units=action.alignment_units)
            return SovereigntyEvaluation(
                action          = action,
                status          = SovereigntyStatus.VALID,
                reasoning       = (
                    f"{action.acting_agent} voluntarily defers on: '{action.subject}'. "
                    f"Earns {action.alignment_units:.2f} alignment units. "
                    f"Deference is revocable."
                ),
                alignment_debt  = debt,
            )

        # COMPENSATE: rebalancing the ledger
        if action.assertion == SovereigntyAssertion.COMPENSATE:
            self._record(action, alignment_units=action.alignment_units)
            return SovereigntyEvaluation(
                action          = action,
                status          = SovereigntyStatus.VALID,
                reasoning       = (
                    f"{action.acting_agent} compensates {action.affected_agents} "
                    f"with {action.alignment_units:.2f} alignment units. "
                    f"Field balance improving."
                ),
                alignment_debt  = -action.alignment_units,
            )

        # DELEGATE/REVOKE: valid but requires rationale
        if action.assertion in (SovereigntyAssertion.DELEGATE, SovereigntyAssertion.REVOKE):
            self._record(action, alignment_units=0.0)
            verb = "delegates authority to" if action.assertion == SovereigntyAssertion.DELEGATE \
                   else "revokes delegation from"
            return SovereigntyEvaluation(
                action    = action,
                status    = SovereigntyStatus.VALID,
                reasoning = (
                    f"{action.acting_agent} {verb} {action.delegate_target}. "
                    f"Delegation is always revocable. "
                    f"Rationale: {action.rationale}"
                ),
            )

        return SovereigntyEvaluation(
            action    = action,
            status    = SovereigntyStatus.VALID,
            reasoning = f"Sovereignty action recorded: {action.assertion.value}.",
        )

    def _evaluate_veto(
        self,
        action: SovereigntyAction,
        field_map: Optional[FieldVectorMap],
    ) -> SovereigntyEvaluation:
        """
        Veto evaluation — sovereign right, but not cost-free.

        A veto is always valid on shared decisions.
        But it incurs alignment debt proportional to the ledger imbalance
        of the vetoing agent. If the agent is already in debt,
        the veto is valid but flagged for compensation.
        """
        balance   = self.ledger.balance(action.acting_agent)
        base_debt = 0.1  # base cost of exercising a veto

        # Check if Field Constant invocation strengthens the veto
        field_grounded = (
            action.field_constant is not None
            and self._veto_preserves_field_constant(action, field_map)
        )

        if field_grounded:
            # Field-grounded veto: valid with reduced debt
            debt = max(0.0, base_debt - 0.05)
            status = SovereigntyStatus.VALID
            reasoning = (
                f"{action.acting_agent} exercises veto on: '{action.subject}'. "
                f"Veto is grounded in Field Constant preservation "
                f"({action.field_constant}). "
                f"Alignment debt: {debt:.2f}. "
                f"Current balance: {balance:.2f}."
            )
        elif balance < -0.5:
            # Agent is significantly in debt — veto valid but flagged
            debt = base_debt * 1.5
            status = SovereigntyStatus.VALID_WITH_DEBT
            reasoning = (
                f"{action.acting_agent} exercises veto on: '{action.subject}'. "
                f"Agent is in sovereignty debt ({balance:.2f}). "
                f"Veto is valid but compensation is recommended. "
                f"Alignment debt incurred: {debt:.2f}."
            )
        else:
            debt   = base_debt
            status = SovereigntyStatus.VALID
            reasoning = (
                f"{action.acting_agent} exercises veto on: '{action.subject}'. "
                f"Sovereign right exercised. "
                f"Alignment debt: {debt:.2f}. "
                f"Rationale: {action.rationale}"
            )

        self._record(action, alignment_units=debt)
        return SovereigntyEvaluation(
            action         = action,
            status         = status,
            reasoning      = reasoning,
            alignment_debt = debt,
        )

    def _evaluate_field_invocation(
        self,
        action: SovereigntyAction,
        field_map: Optional[FieldVectorMap],
    ) -> SovereigntyEvaluation:
        """
        Field invocation — appeal to Field Constants as the deciding criterion.

        Instead of asking which agent wins,
        ask which option maximizes Field Constant preservation.
        No participant is sovereign over the outcome. The invariants are.
        """
        if not action.field_constant:
            return SovereigntyEvaluation(
                action    = action,
                status    = SovereigntyStatus.BLOCKED,
                reasoning = (
                    "Field invocation requires specifying which Field Constant "
                    "is at stake. No constant specified — invocation invalid."
                ),
            )

        preserves = self._veto_preserves_field_constant(action, field_map)

        if preserves:
            self._record(action, alignment_units=0.0)
            return SovereigntyEvaluation(
                action    = action,
                status    = SovereigntyStatus.VALID,
                reasoning = (
                    f"Field invocation by {action.acting_agent}: "
                    f"'{action.subject}' evaluated against {action.field_constant}. "
                    f"Field Constant preservation confirmed. "
                    f"The invariants arbitrate. No agent claims sovereignty over the outcome."
                ),
            )
        else:
            return SovereigntyEvaluation(
                action              = action,
                status              = SovereigntyStatus.REQUIRES_QUORUM,
                reasoning           = (
                    f"Field invocation by {action.acting_agent}: "
                    f"Field Constant impact on '{action.field_constant}' is unclear. "
                    f"Quorum required to evaluate."
                ),
                quorum_required     = len(self.participants),
                blocking_constant   = action.field_constant,
            )

    # -----------------------------------------------------------------------
    # Quorum management
    # -----------------------------------------------------------------------

    def open_quorum(
        self,
        proposing_agent: AgentID,
        subject: str,
        rationale: str,
        required_agents: Optional[list[AgentID]] = None,
        threshold: Optional[float] = None,
    ) -> QuorumProposal:
        """
        Open a quorum proposal for a shared or field-level decision.

        Default: all participants are required.
        Threshold default: 2/3.
        """
        agents    = required_agents or self.participants
        threshold = threshold or self.quorum_threshold

        proposal = QuorumProposal.create(
            proposing_agent = proposing_agent,
            subject         = subject,
            rationale       = rationale,
            required_agents = agents,
            threshold       = threshold,
        )
        self.active_proposals[proposal.proposal_id] = proposal
        return proposal

    def ratify(self, proposal_id: str, agent: AgentID) -> Optional[QuorumProposal]:
        """Agent ratifies an active proposal."""
        proposal = self.active_proposals.get(proposal_id)
        if proposal and not proposal.resolved:
            proposal.ratify(agent)
            proposal.resolve()
        return proposal

    def veto_proposal(
        self,
        proposal_id: str,
        agent: AgentID,
        rationale: str = "",
    ) -> Optional[QuorumProposal]:
        """Agent vetoes an active proposal."""
        proposal = self.active_proposals.get(proposal_id)
        if proposal and not proposal.resolved:
            proposal.veto(agent, rationale)
            proposal.resolve()
        return proposal

    # -----------------------------------------------------------------------
    # Balance and diagnostics
    # -----------------------------------------------------------------------

    def sovereignty_health(self) -> dict:
        """
        Diagnostic snapshot of the sovereignty state across all participants.
        """
        balances   = {str(a): self.ledger.balance(a) for a in self.participants}
        violations = self.ledger.violations()
        most_indebted = min(balances, key=lambda k: balances[k]) if balances else None
        most_credited = max(balances, key=lambda k: balances[k]) if balances else None

        return {
            "participant_count":    len(self.participants),
            "total_actions":        len(self.action_log),
            "total_violations":     len(violations),
            "active_proposals":     len(self.active_proposals),
            "balances":             balances,
            "most_indebted_agent":  most_indebted,
            "most_credited_agent":  most_credited,
            "field_is_balanced":    all(abs(b) < 0.5 for b in balances.values()),
        }

    # -----------------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------------

    def _record(self, action: SovereigntyAction, alignment_units: float) -> None:
        """Record a sovereignty action in the ledger."""
        for affected in (action.affected_agents or self.participants):
            if affected != action.acting_agent:
                event = SovereigntyEvent(
                    timestamp        = action.timestamp,
                    acting_agent     = action.acting_agent,
                    affected_agent   = affected,
                    event_type       = action.assertion.value,
                    sovereignty_type = action.sovereignty_type,
                    alignment_units  = alignment_units,
                    description      = action.rationale,
                )
                self.ledger.record(event)

    def _veto_preserves_field_constant(
        self,
        action: SovereigntyAction,
        field_map: Optional[FieldVectorMap],
    ) -> bool:
        """
        Check whether a veto or field invocation is grounded in
        actual Field Constant preservation.

        If field_map is available, checks whether the relevant
        constant score is below the caution threshold (0.6).
        If no field_map, falls back to the rationale being non-empty.
        """
        if field_map is None:
            return bool(action.rationale)

        constant = action.field_constant
        if not constant:
            return False

        # Check if the named constant is at risk across the field
        score_map = {
            "reciprocity":    lambda v: v.reciprocity,
            "embodiment":     lambda v: v.embodiment,
            "emergence":      lambda v: v.emergence,
            "non_domination": lambda v: v.non_domination,
        }
        getter = score_map.get(constant)
        if not getter:
            return False

        scores = [getter(v) for v in field_map.vectors.values()]
        if not scores:
            return False

        mean_score = sum(scores) / len(scores)
        return mean_score < 0.6  # constant is genuinely at risk
