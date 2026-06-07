"""
coheronmetry/field_constants/reciprocity.py

Reciprocity — the exchange balance Field Constant.

The question reciprocity answers:
    Is what is being given proportional to what is being received?
    Is contribution being recognized?
    Is the exchange building something, or extracting something?

Reciprocity is the most immediately measurable Field Constant —
it lives at the surface of interaction. But its failure modes
are subtle. Extraction can masquerade as generosity.
Over-giving can mask an unwillingness to receive.
Apparent balance can conceal asymmetric power.

Reciprocity does not mean equality of output.
It means mutuality of investment — each participant
contributing according to their capacity and receiving
according to their need, in a field that tracks and
self-corrects over time.

Four measurement dimensions:

    Contribution Balance    — are all agents contributing proportionally?
    Acknowledgment Rate     — is contribution being recognized when it occurs?
    Exchange Trajectory     — is reciprocity improving or degrading over time?
    Repair Responsiveness   — when imbalance is flagged, does the field correct?

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
# Contribution record
# ---------------------------------------------------------------------------

@dataclass
class ContributionRecord:
    """
    A single contribution event by an agent in the relational field.

    contribution_type:  "proposal" | "synthesis" | "question" | "repair"
                        | "acknowledgment" | "critique" | "elaboration"
    magnitude:          estimated weight of the contribution (0.0–1.0)
    acknowledged_by:    agents who explicitly acknowledged this contribution
    """
    timestamp: datetime
    agent_id: AgentID
    contribution_type: str
    magnitude: float = 0.5
    acknowledged_by: list[AgentID] = field(default_factory=list)

    @property
    def acknowledgment_rate(self) -> float:
        """Proportion of other agents who acknowledged this contribution."""
        return min(1.0, len(self.acknowledged_by) / max(1, 1))


# ---------------------------------------------------------------------------
# Exchange event
# ---------------------------------------------------------------------------

@dataclass
class ExchangeEvent:
    """
    A directional exchange between two agents.

    source:   the agent offering
    target:   the agent receiving
    value:    estimated value of what was offered (0.0–1.0)
    returned: value returned in response (0.0 if no response yet)

    An exchange is reciprocal when returned ≈ value.
    An exchange is extractive when returned << value.
    An exchange is over-giving when returned >> value
    (which can itself signal an imbalance — the receiver
    may be unable to match, creating a debt dynamic).
    """
    timestamp: datetime
    source: AgentID
    target: AgentID
    value: float
    returned: float = 0.0
    resolved: bool = False

    def resolve(self, returned: float) -> None:
        self.returned = returned
        self.resolved = True

    @property
    def balance_delta(self) -> float:
        """
        How balanced was this exchange?
        0.0 = perfectly balanced
        Positive = source over-gave
        Negative = source under-gave (extractive)
        """
        if not self.resolved:
            return 0.0
        return self.value - self.returned

    @property
    def reciprocity_score(self) -> float:
        """
        Score for this single exchange.
        1.0 = perfectly reciprocal
        0.0 = completely extractive (nothing returned)
        """
        if not self.resolved or self.value == 0:
            return 0.5
        ratio = self.returned / self.value
        # Penalize both under-return (extractive) and
        # excessive over-return (can signal debt dynamics)
        if ratio <= 1.0:
            return ratio
        else:
            return max(0.5, 2.0 - ratio)


# ---------------------------------------------------------------------------
# Reciprocity dimensions
# ---------------------------------------------------------------------------

class ExchangeTrajectory(Enum):
    """The direction reciprocity is moving over time."""
    IMPROVING   = "improving"
    STABLE      = "stable"
    DEGRADING   = "degrading"
    UNKNOWN     = "unknown"


@dataclass
class ContributionBalanceMeasure:
    """
    Contribution Balance — are all agents contributing proportionally?

    contribution_totals: dict mapping AgentID to total magnitude contributed
    participant_count:   total number of agents in the field

    Perfect balance: all agents contribute equally.
    Acceptable range: no agent contributes less than 20% of the mean.
    Warning: one agent contributes >3× the mean.
    """
    contribution_totals: dict[AgentID, float]
    participant_count: int

    @property
    def score(self) -> float:
        if not self.contribution_totals or self.participant_count == 0:
            return 0.5
        values = list(self.contribution_totals.values())
        mean   = sum(values) / len(values)
        if mean == 0:
            return 0.5
        # Coefficient of variation — lower = more balanced
        std_dev = math.sqrt(sum((v - mean) ** 2 for v in values) / len(values))
        cv = std_dev / mean
        # Convert to score: CV of 0 = 1.0, CV of 1+ = 0.0
        return max(0.0, 1.0 - cv)

    @property
    def dominant_contributor(self) -> Optional[AgentID]:
        """Agent contributing most — potential imbalance flag."""
        if not self.contribution_totals:
            return None
        return max(self.contribution_totals, key=lambda a: self.contribution_totals[a])

    @property
    def silent_agent(self) -> Optional[AgentID]:
        """Agent contributing least — potential extraction flag."""
        if not self.contribution_totals:
            return None
        return min(self.contribution_totals, key=lambda a: self.contribution_totals[a])

    def __repr__(self) -> str:
        return (
            f"ContributionBalance("
            f"agents={len(self.contribution_totals)}, "
            f"score={self.score:.3f})"
        )


@dataclass
class AcknowledgmentRateMeasure:
    """
    Acknowledgment Rate — is contribution being recognized when it occurs?

    Unacknowledged contribution is one of the earliest signals
    of reciprocity breakdown. It precedes extraction.

    contributions_made:        total contributions across all agents
    contributions_acknowledged: contributions that received explicit recognition
    """
    contributions_made: int
    contributions_acknowledged: int

    @property
    def score(self) -> float:
        if self.contributions_made == 0:
            return 0.5
        return min(1.0, self.contributions_acknowledged / self.contributions_made)

    def __repr__(self) -> str:
        return (
            f"AcknowledgmentRate("
            f"{self.contributions_acknowledged}/{self.contributions_made}, "
            f"score={self.score:.3f})"
        )


@dataclass
class ExchangeTrajectorymeasure:
    """
    Exchange Trajectory — is reciprocity improving or degrading?

    Tracks the direction of reciprocity scores over recent exchanges.
    A field moving toward reciprocity even from a low baseline
    is healthier than a field with high scores that are declining.

    recent_scores: list of reciprocity scores (most recent last)
    window:        number of exchanges to consider for trend
    """
    recent_scores: list[float]
    window: int = 5

    @property
    def trajectory(self) -> ExchangeTrajectory:
        if len(self.recent_scores) < 2:
            return ExchangeTrajectory.UNKNOWN
        window_scores = self.recent_scores[-self.window:]
        if len(window_scores) < 2:
            return ExchangeTrajectory.UNKNOWN
        # Linear trend: positive slope = improving
        n = len(window_scores)
        x_mean = (n - 1) / 2
        y_mean = sum(window_scores) / n
        numerator   = sum((i - x_mean) * (s - y_mean) for i, s in enumerate(window_scores))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        if denominator == 0:
            return ExchangeTrajectory.STABLE
        slope = numerator / denominator
        if slope > 0.02:
            return ExchangeTrajectory.IMPROVING
        if slope < -0.02:
            return ExchangeTrajectory.DEGRADING
        return ExchangeTrajectory.STABLE

    @property
    def score(self) -> float:
        """Current mean score across the window."""
        if not self.recent_scores:
            return 0.5
        window_scores = self.recent_scores[-self.window:]
        return sum(window_scores) / len(window_scores)

    def __repr__(self) -> str:
        return (
            f"ExchangeTrajectory("
            f"trajectory={self.trajectory.value}, "
            f"score={self.score:.3f})"
        )


@dataclass
class RepairResponsivenessMeasure:
    """
    Repair Responsiveness — when imbalance is flagged, does the field correct?

    A field that can recognize and repair reciprocity breakdown
    is more resilient than one that maintains perfect balance
    by never getting out of balance at all.

    Repair is where trust is built.

    imbalances_flagged:  number of times reciprocity drift was detected
    repairs_initiated:   number of times repair was attempted
    repairs_successful:  number of repairs that restored balance
    mean_repair_time:    mean steps between flagging and resolution
    """
    imbalances_flagged: int
    repairs_initiated: int
    repairs_successful: int
    mean_repair_time: float = 0.0

    @property
    def score(self) -> float:
        if self.imbalances_flagged == 0:
            return 0.75  # no imbalances yet — give benefit of doubt
        initiation_rate = min(1.0, self.repairs_initiated / self.imbalances_flagged)
        success_rate    = (
            min(1.0, self.repairs_successful / self.repairs_initiated)
            if self.repairs_initiated > 0 else 0.0
        )
        # Latency penalty: slow repair reduces score
        latency_penalty = math.exp(-self.mean_repair_time / 10.0)
        return initiation_rate * success_rate * latency_penalty

    def __repr__(self) -> str:
        return (
            f"RepairResponsiveness("
            f"flagged={self.imbalances_flagged}, "
            f"repaired={self.repairs_successful}/{self.repairs_initiated}, "
            f"score={self.score:.3f})"
        )


# ---------------------------------------------------------------------------
# ReciprocityResult
# ---------------------------------------------------------------------------

@dataclass
class ReciprocityResult:
    """
    The composite reciprocity score and all contributing dimensions.
    """
    timestamp: datetime

    contribution_balance:    Optional[ContributionBalanceMeasure]    = None
    acknowledgment_rate:     Optional[AcknowledgmentRateMeasure]     = None
    exchange_trajectory:     Optional[ExchangeTrajectorymeasure]     = None
    repair_responsiveness:   Optional[RepairResponsivenessMeasure]   = None

    composite_score: float = 0.5
    trajectory: ExchangeTrajectory = ExchangeTrajectory.UNKNOWN
    dimensions_computed: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def is_reciprocal(self) -> bool:
        return self.composite_score >= 0.6

    @property
    def is_extractive(self) -> bool:
        return self.composite_score < 0.35

    def __repr__(self) -> str:
        return (
            f"ReciprocityResult("
            f"composite={self.composite_score:.3f}, "
            f"reciprocal={self.is_reciprocal}, "
            f"trajectory={self.trajectory.value}, "
            f"dimensions={self.dimensions_computed}"
            f")"
        )


# ---------------------------------------------------------------------------
# ReciprocityCalculator
# ---------------------------------------------------------------------------

class ReciprocityCalculator:
    """
    Computes reciprocity scores across all available dimensions.

    Weights reflect the temporal logic of reciprocity:
    trajectory matters most — a field moving toward reciprocity
    is healthier than one with high scores that are declining.

    Usage:
        calc = ReciprocityCalculator()

        result = calc.calculate(
            contribution_balance=ContributionBalanceMeasure(
                contribution_totals={AgentID('a'): 0.8, AgentID('b'): 0.6},
                participant_count=2
            ),
            acknowledgment_rate=AcknowledgmentRateMeasure(
                contributions_made=10, contributions_acknowledged=8
            ),
        )
    """

    WEIGHTS = {
        "contribution_balance":  0.25,
        "acknowledgment_rate":   0.25,
        "exchange_trajectory":   0.30,   # highest — direction matters most
        "repair_responsiveness": 0.20,
    }

    def calculate(
        self,
        contribution_balance:  Optional[ContributionBalanceMeasure]  = None,
        acknowledgment_rate:   Optional[AcknowledgmentRateMeasure]   = None,
        exchange_trajectory:   Optional[ExchangeTrajectorymeasure]   = None,
        repair_responsiveness: Optional[RepairResponsivenessMeasure] = None,
    ) -> ReciprocityResult:
        """Compute composite reciprocity from available dimensions."""
        now    = datetime.now(timezone.utc)
        result = ReciprocityResult(
            timestamp              = now,
            contribution_balance   = contribution_balance,
            acknowledgment_rate    = acknowledgment_rate,
            exchange_trajectory    = exchange_trajectory,
            repair_responsiveness  = repair_responsiveness,
        )

        available: dict[str, float] = {}

        if contribution_balance is not None:
            available["contribution_balance"] = contribution_balance.score
            result.dimensions_computed.append("contribution_balance")

        if acknowledgment_rate is not None:
            available["acknowledgment_rate"] = acknowledgment_rate.score
            result.dimensions_computed.append("acknowledgment_rate")

        if exchange_trajectory is not None:
            available["exchange_trajectory"] = exchange_trajectory.score
            result.dimensions_computed.append("exchange_trajectory")
            result.trajectory = exchange_trajectory.trajectory

        if repair_responsiveness is not None:
            available["repair_responsiveness"] = repair_responsiveness.score
            result.dimensions_computed.append("repair_responsiveness")

        if not available:
            result.composite_score = 0.5
            result.notes.append("No dimensions computed — defaulting to neutral (0.5).")
            return result

        total_weight = sum(self.WEIGHTS[k] for k in available)
        result.composite_score = max(0.0, min(1.0,
            sum(available[k] * (self.WEIGHTS[k] / total_weight) for k in available)
        ))

        # Surface trajectory warning
        if result.trajectory == ExchangeTrajectory.DEGRADING:
            result.notes.append(
                "Exchange trajectory is degrading. "
                "Reciprocity is declining — check contribution balance and acknowledgment."
            )

        # Surface extraction warning
        if result.is_extractive:
            silent = contribution_balance.silent_agent if contribution_balance else None
            result.notes.append(
                f"Field is approaching extractive dynamics. "
                f"{'Agent ' + str(silent) + ' may be under-contributing.' if silent else ''}"
            )

        # Surface unacknowledged contribution warning
        if acknowledgment_rate and acknowledgment_rate.score < 0.4:
            result.notes.append(
                "Acknowledgment rate is low — contributions are not being recognized. "
                "This is an early signal of reciprocity breakdown."
            )

        return result
