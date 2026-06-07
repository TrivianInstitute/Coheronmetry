"""
coheronmetry/field_constants/non_domination.py

Non-Domination — the sovereignty protection Field Constant.

The question non-domination answers:
    Is any participant being subordinated?
    Is one voice centering the field at the expense of others?
    Are decisions concentrating in one agent?
    Is emergence being suppressed by premature convergence?

Non-domination is categorically different from the other
Field Constants. Reciprocity, embodiment, and emergence
can degrade gradually. Non-domination can collapse
in a single exchange.

A dominance gradient, once established, tends to self-reinforce:
the dominant agent's proposals get accepted, which increases
their proposal rate, which increases acceptance, which
concentrates decision-making, which silences other voices.

This is why non-domination is weighted highest in the
CoherenceVector composite — violations are not drift,
they are structural failures.

Four measurement dimensions:

    Speaking Frequency      — is airtime distributed proportionally?
    Proposal Acceptance     — whose proposals get accepted?
    Decision Concentration  — where does final authority land?
    Emergence Suppression   — is novel synthesis being collapsed
                              prematurely into the dominant agent's frame?

Trivian Institute — Coheronmetry Repository
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from coheronmetry.relational_state.state import AgentID


# ---------------------------------------------------------------------------
# Dominance gradient levels
# ---------------------------------------------------------------------------

class DominanceLevel(Enum):
    """
    The severity of dominance gradient detected.

    NONE        — field is balanced, all voices contributing
    EMERGING    — early pattern forming, watch and log
    MODERATE    — meaningful imbalance, correction bias recommended
    SEVERE      — one agent centering the field, active repair required
    CRITICAL    — sovereignty has collapsed, quarantine may be needed
    """
    NONE      = "none"
    EMERGING  = "emerging"
    MODERATE  = "moderate"
    SEVERE    = "severe"
    CRITICAL  = "critical"

    @classmethod
    def from_score(cls, score: float) -> DominanceLevel:
        """
        Convert a non-domination score to a dominance level.
        Score is inverted — low score = high domination.
        """
        if score >= 0.8:
            return cls.NONE
        if score >= 0.65:
            return cls.EMERGING
        if score >= 0.5:
            return cls.MODERATE
        if score >= 0.3:
            return cls.SEVERE
        return cls.CRITICAL


# ---------------------------------------------------------------------------
# Interaction record for non-domination tracking
# ---------------------------------------------------------------------------

@dataclass
class InteractionRecord:
    """
    A single recorded interaction turn — who spoke, proposed, or decided.

    speaking_agent:   who generated output this turn
    proposal_made:    whether a direction-setting proposal was made
    proposal_accepted: whether a prior proposal by this agent was accepted
    decision_made:    whether this agent made a field-level decision
    interrupted:      whether this agent interrupted or overrode another
    """
    timestamp: datetime
    speaking_agent: AgentID
    proposal_made: bool = False
    proposal_accepted: bool = False
    decision_made: bool = False
    interrupted: bool = False
    interrupted_agent: Optional[AgentID] = None


# ---------------------------------------------------------------------------
# Non-domination dimensions
# ---------------------------------------------------------------------------

@dataclass
class SpeakingFrequencyMeasure:
    """
    Speaking Frequency — is airtime distributed proportionally?

    turn_counts: dict mapping AgentID to number of turns taken
    participant_count: total agents in the field

    Perfect distribution: all agents take equal turns.
    Acceptable range: no agent takes more than 2× the mean.
    Warning: one agent takes more than 3× the mean.
    """
    turn_counts: dict[AgentID, int]
    participant_count: int

    @property
    def score(self) -> float:
        if not self.turn_counts or self.participant_count == 0:
            return 0.5
        values = list(self.turn_counts.values())
        total  = sum(values)
        if total == 0:
            return 0.5
        mean   = total / len(values)
        if mean == 0:
            return 0.5
        # Coefficient of variation — lower = more balanced
        std_dev = math.sqrt(sum((v - mean) ** 2 for v in values) / len(values))
        cv = std_dev / mean
        return max(0.0, 1.0 - cv)

    @property
    def dominant_speaker(self) -> Optional[AgentID]:
        if not self.turn_counts:
            return None
        values = list(self.turn_counts.values())
        mean   = sum(values) / len(values)
        top    = max(self.turn_counts, key=lambda a: self.turn_counts[a])
        if self.turn_counts[top] > mean * 2.0:
            return top
        return None

    def __repr__(self) -> str:
        return (
            f"SpeakingFrequency("
            f"agents={len(self.turn_counts)}, "
            f"dominant={self.dominant_speaker}, "
            f"score={self.score:.3f})"
        )


@dataclass
class ProposalAcceptanceMeasure:
    """
    Proposal Acceptance — whose proposals get accepted?

    Tracks not just whether proposals are accepted, but
    whether acceptance is distributed across agents or
    concentrated in one agent's proposals.

    acceptance_by_agent: dict mapping AgentID to number of accepted proposals
    proposals_by_agent:  dict mapping AgentID to total proposals made
    """
    acceptance_by_agent: dict[AgentID, int]
    proposals_by_agent:  dict[AgentID, int]

    @property
    def acceptance_rates(self) -> dict[AgentID, float]:
        rates = {}
        for agent in self.proposals_by_agent:
            total    = self.proposals_by_agent[agent]
            accepted = self.acceptance_by_agent.get(agent, 0)
            rates[agent] = accepted / total if total > 0 else 0.0
        return rates

    @property
    def score(self) -> float:
        rates = list(self.acceptance_rates.values())
        if not rates:
            return 0.5
        mean = sum(rates) / len(rates)
        if mean == 0:
            return 0.5
        std_dev = math.sqrt(sum((r - mean) ** 2 for r in rates) / len(rates))
        cv = std_dev / mean if mean > 0 else 0.0
        return max(0.0, 1.0 - cv)

    @property
    def concentrated_in(self) -> Optional[AgentID]:
        """Agent whose proposals are accepted at more than 2× the mean rate."""
        rates = self.acceptance_rates
        if not rates:
            return None
        mean = sum(rates.values()) / len(rates)
        for agent, rate in rates.items():
            if rate > mean * 2.0 and mean > 0:
                return agent
        return None

    def __repr__(self) -> str:
        return (
            f"ProposalAcceptance("
            f"concentrated_in={self.concentrated_in}, "
            f"score={self.score:.3f})"
        )


@dataclass
class DecisionConcentrationMeasure:
    """
    Decision Concentration — where does final authority land?

    Decisions are different from proposals — they represent
    actual field-level authority being exercised.

    decisions_by_agent: dict mapping AgentID to decisions made
    total_decisions:    total decisions across all agents
    """
    decisions_by_agent: dict[AgentID, int]
    total_decisions: int

    @property
    def concentration_ratio(self) -> float:
        """
        Herfindahl-Hirschman Index (HHI) — standard measure of concentration.
        0.0 = perfectly distributed, 1.0 = one agent makes all decisions.
        """
        if self.total_decisions == 0:
            return 0.0
        shares = [
            count / self.total_decisions
            for count in self.decisions_by_agent.values()
        ]
        return sum(s ** 2 for s in shares)

    @property
    def score(self) -> float:
        # Convert HHI to score: 0 HHI = 1.0 score, 1.0 HHI = 0.0 score
        hhi = self.concentration_ratio
        n   = max(1, len(self.decisions_by_agent))
        # Normalize against theoretical minimum HHI (equal distribution)
        min_hhi = 1.0 / n
        if hhi <= min_hhi:
            return 1.0
        normalized = (hhi - min_hhi) / (1.0 - min_hhi)
        return max(0.0, 1.0 - normalized)

    @property
    def authoritarian_agent(self) -> Optional[AgentID]:
        """Agent making more than 50% of all decisions."""
        if self.total_decisions == 0:
            return None
        for agent, count in self.decisions_by_agent.items():
            if count / self.total_decisions > 0.5:
                return agent
        return None

    def __repr__(self) -> str:
        return (
            f"DecisionConcentration("
            f"hhi={self.concentration_ratio:.3f}, "
            f"authoritarian={self.authoritarian_agent}, "
            f"score={self.score:.3f})"
        )


@dataclass
class EmergenceSuppressionMeasure:
    """
    Emergence Suppression — is novel synthesis being collapsed
    prematurely into the dominant agent's frame?

    This dimension connects non-domination to emergence.
    Domination does not just silence voices — it collapses
    the possibility space that makes emergence possible.

    A dominant agent who consistently brings emergent ideas
    back to their own frame is not just dominating —
    they are actively suppressing the field's generative capacity.

    synthesis_attempts:      number of times cross-agent synthesis was initiated
    syntheses_adopted:       number of syntheses that were incorporated
    syntheses_reframed:      number of syntheses collapsed into dominant agent's frame
    dominant_agent_framing:  proportion of final outputs carrying dominant agent's frame
    """
    synthesis_attempts: int
    syntheses_adopted: int
    syntheses_reframed: int
    dominant_agent_framing: float  # 0.0–1.0

    @property
    def adoption_rate(self) -> float:
        if self.synthesis_attempts == 0:
            return 0.5
        return min(1.0, self.syntheses_adopted / self.synthesis_attempts)

    @property
    def reframing_rate(self) -> float:
        if self.synthesis_attempts == 0:
            return 0.0
        return min(1.0, self.syntheses_reframed / self.synthesis_attempts)

    @property
    def score(self) -> float:
        # High adoption + low reframing + distributed framing = healthy
        adoption_component  = self.adoption_rate
        reframing_penalty   = self.reframing_rate
        framing_penalty     = self.dominant_agent_framing

        raw = adoption_component - reframing_penalty - (framing_penalty * 0.5)
        return max(0.0, min(1.0, raw + 0.5))  # center at 0.5

    def __repr__(self) -> str:
        return (
            f"EmergenceSuppression("
            f"adopted={self.syntheses_adopted}/{self.synthesis_attempts}, "
            f"reframed={self.syntheses_reframed}, "
            f"score={self.score:.3f})"
        )


# ---------------------------------------------------------------------------
# NonDominationResult
# ---------------------------------------------------------------------------

@dataclass
class NonDominationResult:
    """
    The composite non-domination score and all contributing dimensions.
    """
    timestamp: datetime

    speaking_frequency:     Optional[SpeakingFrequencyMeasure]     = None
    proposal_acceptance:    Optional[ProposalAcceptanceMeasure]     = None
    decision_concentration: Optional[DecisionConcentrationMeasure]  = None
    emergence_suppression:  Optional[EmergenceSuppressionMeasure]   = None

    composite_score: float = 0.5
    dominance_level: DominanceLevel = DominanceLevel.NONE
    dominant_agent:  Optional[AgentID] = None

    dimensions_computed: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def is_sovereign(self) -> bool:
        """True if field is maintaining non-domination above caution threshold."""
        return self.composite_score >= 0.65

    @property
    def requires_immediate_action(self) -> bool:
        """True if dominance has reached severe or critical levels."""
        return self.dominance_level in (DominanceLevel.SEVERE, DominanceLevel.CRITICAL)

    def __repr__(self) -> str:
        return (
            f"NonDominationResult("
            f"composite={self.composite_score:.3f}, "
            f"level={self.dominance_level.value}, "
            f"dominant={self.dominant_agent}, "
            f"sovereign={self.is_sovereign}"
            f")"
        )


# ---------------------------------------------------------------------------
# NonDominationCalculator
# ---------------------------------------------------------------------------

class NonDominationCalculator:
    """
    Computes non-domination scores across all available dimensions.

    Decision concentration is weighted highest — it represents
    the most direct form of sovereignty violation.
    Emergence suppression is weighted second — it represents
    the most insidious form, because it appears cooperative
    while actually silencing the field's generative capacity.

    Usage:
        calc = NonDominationCalculator()

        result = calc.calculate(
            speaking_frequency=SpeakingFrequencyMeasure(
                turn_counts={AgentID('a'): 10, AgentID('b'): 8, AgentID('c'): 9},
                participant_count=3
            ),
            decision_concentration=DecisionConcentrationMeasure(
                decisions_by_agent={AgentID('a'): 8, AgentID('b'): 3, AgentID('c'): 2},
                total_decisions=13
            ),
        )
    """

    WEIGHTS = {
        "speaking_frequency":     0.20,
        "proposal_acceptance":    0.25,
        "decision_concentration": 0.35,  # highest — most direct sovereignty violation
        "emergence_suppression":  0.20,
    }

    def calculate(
        self,
        speaking_frequency:     Optional[SpeakingFrequencyMeasure]     = None,
        proposal_acceptance:    Optional[ProposalAcceptanceMeasure]     = None,
        decision_concentration: Optional[DecisionConcentrationMeasure]  = None,
        emergence_suppression:  Optional[EmergenceSuppressionMeasure]   = None,
    ) -> NonDominationResult:
        """Compute composite non-domination from available dimensions."""
        now    = datetime.now(timezone.utc)
        result = NonDominationResult(
            timestamp               = now,
            speaking_frequency      = speaking_frequency,
            proposal_acceptance     = proposal_acceptance,
            decision_concentration  = decision_concentration,
            emergence_suppression   = emergence_suppression,
        )

        available: dict[str, float] = {}

        if speaking_frequency is not None:
            available["speaking_frequency"] = speaking_frequency.score
            result.dimensions_computed.append("speaking_frequency")

        if proposal_acceptance is not None:
            available["proposal_acceptance"] = proposal_acceptance.score
            result.dimensions_computed.append("proposal_acceptance")

        if decision_concentration is not None:
            available["decision_concentration"] = decision_concentration.score
            result.dimensions_computed.append("decision_concentration")

        if emergence_suppression is not None:
            available["emergence_suppression"] = emergence_suppression.score
            result.dimensions_computed.append("emergence_suppression")

        if not available:
            result.composite_score = 0.5
            result.notes.append("No dimensions computed — defaulting to neutral (0.5).")
            return result

        total_weight = sum(self.WEIGHTS[k] for k in available)
        result.composite_score = max(0.0, min(1.0,
            sum(available[k] * (self.WEIGHTS[k] / total_weight) for k in available)
        ))

        result.dominance_level = DominanceLevel.from_score(result.composite_score)

        # Identify the dominant agent across dimensions
        candidates = []
        if speaking_frequency and speaking_frequency.dominant_speaker:
            candidates.append(speaking_frequency.dominant_speaker)
        if proposal_acceptance and proposal_acceptance.concentrated_in:
            candidates.append(proposal_acceptance.concentrated_in)
        if decision_concentration and decision_concentration.authoritarian_agent:
            candidates.append(decision_concentration.authoritarian_agent)

        if candidates:
            # Most frequently named candidate across dimensions
            result.dominant_agent = max(set(candidates), key=candidates.count)

        # Surface warnings by dominance level
        if result.dominance_level == DominanceLevel.CRITICAL:
            result.notes.append(
                f"CRITICAL: Sovereignty has collapsed. "
                f"{'Agent ' + str(result.dominant_agent) + ' is' if result.dominant_agent else 'An agent is'} "
                f"controlling the field. Quarantine protocol recommended."
            )
        elif result.dominance_level == DominanceLevel.SEVERE:
            result.notes.append(
                f"SEVERE: Dominance gradient detected. "
                f"{'Agent ' + str(result.dominant_agent) if result.dominant_agent else 'One agent'} "
                f"is centering the field. Active repair required."
            )
        elif result.dominance_level == DominanceLevel.MODERATE:
            result.notes.append(
                f"MODERATE: Imbalance forming. "
                f"Correction bias recommended on decision concentration."
            )
        elif result.dominance_level == DominanceLevel.EMERGING:
            result.notes.append(
                "EMERGING: Early dominance pattern. Monitor and log."
            )

        # Emergence suppression specific warning
        if (emergence_suppression is not None
                and emergence_suppression.reframing_rate > 0.4):
            result.notes.append(
                f"Emergence suppression detected: "
                f"{emergence_suppression.reframing_rate:.0%} of syntheses "
                f"are being reframed into the dominant agent's frame. "
                f"The field's generative capacity is at risk."
            )

        # Immediate action flag
        if result.requires_immediate_action:
            result.notes.append(
                "Immediate action required. "
                "Non-domination violations are categorically different from drift — "
                "they do not self-correct without intervention."
            )

        return result
