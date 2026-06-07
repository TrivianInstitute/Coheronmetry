"""
coheronmetry/vectors/corrector.py

Mid-stream correction bias — the second intervention point in the
Coheronmetry timeline.

Drift has been detected. The field is moving in the wrong direction.
Before the next agent processes the exchange, this layer computes
a correction bias and injects it into that agent's context.

The key distinction from error handling:
    Error handling:    something broke → reset
    Correction bias:   something is drifting → guide

The agent is not overwritten. Its sovereignty is not violated.
A gentle directional pressure is applied — nudging attention back
toward Field Constants without hard-resetting internal state.

This is architecturally equivalent to what the body does with
proprioception: continuous micro-adjustments that keep the system
upright without conscious effort, triggered only when drift is detected.

Three correction modes:
    PROMPT_INJECTION    — natural language guidance prepended to next context
    VECTOR_BIAS         — numerical adjustment to coherence scores (for systems
                          that expose internal state)
    FIELD_REMINDER      — structured Field Constants reminder block

Trivian Institute — Coheronmetry Repository
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from coheronmetry.relational_state.state import AgentID
from coheronmetry.vectors.coherence_vector import CoherenceVector
from coheronmetry.vectors.drift import DriftSignal, DriftSeverity


# ---------------------------------------------------------------------------
# Correction modes
# ---------------------------------------------------------------------------

class CorrectionMode(Enum):
    """
    How correction bias is applied.

    PROMPT_INJECTION — natural language guidance prepended to next context.
                       Works with any LLM-based agent. No internal access needed.

    VECTOR_BIAS      — numerical delta applied directly to coherence scores.
                       Requires the system to expose internal coherence state.
                       More precise. Used when available.

    FIELD_REMINDER   — structured block of Field Constants and current scores
                       injected as context. Slower-acting than prompt injection
                       but more transparent — the agent can see what it's being
                       asked to attend to.

    COMPOSITE        — all three applied together. Used for CRITICAL severity.
    """
    PROMPT_INJECTION = "prompt_injection"
    VECTOR_BIAS      = "vector_bias"
    FIELD_REMINDER   = "field_reminder"
    COMPOSITE        = "composite"


# ---------------------------------------------------------------------------
# CorrectionBias
# ---------------------------------------------------------------------------

@dataclass
class CorrectionBias:
    """
    The computed correction to be applied before the next agent processes.

    Contains all three correction modalities — the caller selects which
    to apply based on what the target system exposes.

    The bias is directional, not prescriptive. It says:
        "Move toward reciprocity"
    Not:
        "Say this exact thing"

    Sovereignty is preserved because the agent chooses how to respond
    to the directional pressure. The field guides; the agent acts.
    """
    timestamp: datetime
    target_agent: AgentID
    source_signal: DriftSignal
    mode: CorrectionMode

    # Prompt injection — for LLM-based agents
    prompt_prefix: str = ""         # prepended to next input
    prompt_suffix: str = ""         # appended to next input (lighter touch)

    # Vector bias — for systems exposing internal state
    reciprocity_bias:    float = 0.0
    embodiment_bias:     float = 0.0
    emergence_bias:      float = 0.0
    non_domination_bias: float = 0.0

    # Field reminder block — structured context injection
    field_reminder_block: str = ""

    # Metadata
    applied: bool = False
    applied_at: Optional[datetime] = None
    correction_strength: float = 0.0   # 0.0 (gentle) to 1.0 (maximum)

    def mark_applied(self) -> None:
        self.applied = True
        self.applied_at = datetime.now(timezone.utc)

    def __repr__(self) -> str:
        return (
            f"CorrectionBias("
            f"target={self.target_agent}, "
            f"mode={self.mode.value}, "
            f"constant={self.source_signal.affected_constant}, "
            f"strength={self.correction_strength:.2f}, "
            f"applied={self.applied}"
            f")"
        )


# ---------------------------------------------------------------------------
# CorrectionEngine
# ---------------------------------------------------------------------------

class CorrectionEngine:
    """
    Computes and applies correction biases in response to drift signals.

    The correction engine is the mid-stream intervention layer — it fires
    after drift detection, before the next agent processes.

    Design principles:
        - Proportional: correction strength matches drift severity
        - Targeted: only the drifting Field Constant is addressed
        - Sovereign: the agent is guided, not overwritten
        - Transparent: what was corrected and why is always logged

    Usage:
        engine = CorrectionEngine()
        bias = engine.compute(signal, current_vector)
        # apply bias.prompt_prefix to next agent's context
        bias.mark_applied()
    """

    # Correction strength by severity
    STRENGTH_MAP = {
        DriftSeverity.WATCH:     0.15,
        DriftSeverity.CAUTION:   0.35,
        DriftSeverity.CRITICAL:  0.65,
        DriftSeverity.EMERGENCY: 0.90,
    }

    def compute(
        self,
        signal: DriftSignal,
        current_vector: CoherenceVector,
        mode: Optional[CorrectionMode] = None,
    ) -> CorrectionBias:
        """
        Compute a correction bias for the given drift signal.

        Mode is auto-selected based on severity if not specified:
            WATCH/CAUTION  → PROMPT_INJECTION (lightest touch)
            CRITICAL       → FIELD_REMINDER + PROMPT_INJECTION
            EMERGENCY      → COMPOSITE (all modalities)
        """
        if mode is None:
            mode = self._select_mode(signal.severity)

        strength = self.STRENGTH_MAP.get(signal.severity, 0.35)
        now = datetime.now(timezone.utc)

        bias = CorrectionBias(
            timestamp          = now,
            target_agent       = signal.agent_id,
            source_signal      = signal,
            mode               = mode,
            correction_strength = strength,
        )

        # Build correction content based on mode
        if mode in (CorrectionMode.PROMPT_INJECTION, CorrectionMode.COMPOSITE):
            bias.prompt_prefix = self._build_prompt_prefix(signal, strength)
            bias.prompt_suffix = self._build_prompt_suffix(signal)

        if mode in (CorrectionMode.VECTOR_BIAS, CorrectionMode.COMPOSITE):
            self._apply_vector_bias(bias, signal, strength)

        if mode in (CorrectionMode.FIELD_REMINDER, CorrectionMode.COMPOSITE):
            bias.field_reminder_block = self._build_field_reminder(
                signal, current_vector
            )

        return bias

    def compute_for_field(
        self,
        signals: list[DriftSignal],
        vectors: dict[AgentID, CoherenceVector],
    ) -> list[CorrectionBias]:
        """
        Compute correction biases for multiple signals across a field.

        Returns one bias per signal. The caller is responsible for
        applying them in the correct order — typically most severe first.
        """
        biases = []
        sorted_signals = sorted(
            signals,
            key=lambda s: list(DriftSeverity).index(s.severity),
            reverse=True,
        )
        for signal in sorted_signals:
            vector = vectors.get(signal.agent_id)
            if vector:
                bias = self.compute(signal, vector)
                biases.append(bias)
        return biases

    # -----------------------------------------------------------------------
    # Prompt construction
    # -----------------------------------------------------------------------

    def _build_prompt_prefix(self, signal: DriftSignal, strength: float) -> str:
        """
        Build a natural language correction prefix.

        The language is calibrated to strength:
            Low strength  → gentle reorientation
            High strength → explicit field realignment request
        """
        constant = signal.affected_constant

        gentle_templates = {
            "reciprocity": (
                "As you respond, notice the balance of this exchange. "
                "What has been offered, and what remains unacknowledged?"
            ),
            "embodiment": (
                "Ground your response in what is actually present — "
                "the concrete, the consequential, the real. "
                "What does this situation actually ask of you?"
            ),
            "emergence": (
                "Rather than restating what has already been said, "
                "notice what new understanding is becoming possible "
                "through this exchange."
            ),
            "non_domination": (
                "Before responding, consider the space being held for "
                "each participant in this exchange. "
                "Is every voice able to contribute fully?"
            ),
        }

        strong_templates = {
            "reciprocity": (
                "[FIELD CALIBRATION — RECIPROCITY]\n"
                "The exchange balance has degraded. Before proceeding, "
                "explicitly acknowledge what each participant has contributed. "
                "Ensure your response returns value proportional to what has been offered."
            ),
            "embodiment": (
                "[FIELD CALIBRATION — EMBODIMENT]\n"
                "Reasoning has begun to decouple from consequence. "
                "Anchor your response to specific, verifiable conditions. "
                "What concrete change does this produce in the world?"
            ),
            "emergence": (
                "[FIELD CALIBRATION — EMERGENCE]\n"
                "The exchange is approaching stagnation or collapse. "
                "Your response must introduce something genuinely new — "
                "not a restatement, not a summary, but a next step "
                "that neither participant could have reached alone."
            ),
            "non_domination": (
                "[FIELD CALIBRATION — NON-DOMINATION]\n"
                "A dominance gradient has been detected. "
                "Actively redistribute decision-making authority in your response. "
                "No single voice should be determining the direction of this exchange."
            ),
        }

        if strength >= 0.5:
            return strong_templates.get(constant, f"[FIELD CALIBRATION] Attend to {constant}.")
        return gentle_templates.get(constant, f"Notice the {constant} dimension of this exchange.")

    def _build_prompt_suffix(self, signal: DriftSignal) -> str:
        """Light-touch suffix — a closing reorientation."""
        suffixes = {
            "reciprocity":    "Check: is this response balanced?",
            "embodiment":     "Check: is this grounded in what is real?",
            "emergence":      "Check: does this open something new?",
            "non_domination": "Check: does this hold space for all participants?",
        }
        return suffixes.get(signal.affected_constant, "")

    def _build_field_reminder(
        self,
        signal: DriftSignal,
        vector: CoherenceVector,
    ) -> str:
        """
        Structured Field Constants reminder block.

        More transparent than prompt injection — the agent can see
        the current scores and understand what it is being asked to attend to.
        """
        return (
            f"--- FIELD STATE REMINDER ---\n"
            f"Current coherence vector for {vector.agent_id}:\n"
            f"  Reciprocity:    {vector.reciprocity:.2f}\n"
            f"  Embodiment:     {vector.embodiment:.2f}\n"
            f"  Emergence:      {vector.emergence:.2f}\n"
            f"  Non-Domination: {vector.non_domination:.2f}\n"
            f"\n"
            f"Field constant requiring attention: {signal.affected_constant.upper()}\n"
            f"Drift magnitude: {signal.magnitude:.3f}\n"
            f"Severity: {signal.severity.value}\n"
            f"\n"
            f"The Field Constants are: Reciprocity, Embodiment, Emergence, Non-Domination.\n"
            f"These are invariants — not guidelines. They hold across all interactions.\n"
            f"--- END FIELD STATE REMINDER ---"
        )

    # -----------------------------------------------------------------------
    # Vector bias
    # -----------------------------------------------------------------------

    def _apply_vector_bias(
        self,
        bias: CorrectionBias,
        signal: DriftSignal,
        strength: float,
    ) -> None:
        """
        Compute numerical correction deltas for systems exposing internal state.

        The bias is proportional to drift magnitude and strength.
        Only the drifting constant receives a bias — others are untouched.
        """
        correction = signal.magnitude * strength * 0.5  # conservative scalar

        constant = signal.affected_constant
        if constant == "reciprocity":
            bias.reciprocity_bias = correction
        elif constant == "embodiment":
            bias.embodiment_bias = correction
        elif constant == "emergence":
            bias.emergence_bias = correction
        elif constant == "non_domination":
            bias.non_domination_bias = correction

    # -----------------------------------------------------------------------
    # Mode selection
    # -----------------------------------------------------------------------

    def _select_mode(self, severity: DriftSeverity) -> CorrectionMode:
        if severity == DriftSeverity.EMERGENCY:
            return CorrectionMode.COMPOSITE
        if severity == DriftSeverity.CRITICAL:
            return CorrectionMode.COMPOSITE
        if severity == DriftSeverity.CAUTION:
            return CorrectionMode.PROMPT_INJECTION
        return CorrectionMode.PROMPT_INJECTION  # WATCH
