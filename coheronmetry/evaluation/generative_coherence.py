"""Coherence x differentiation observation for Coheronmetry.

This module does not define orthogonality itself; Orthogonal Signal remains the
canonical source for differentiation measurement. Coheronmetry consumes a
coherence value and a supplied differentiation floor to distinguish generative
coherence from apparent coherence under homogenization.
"""

from dataclasses import dataclass
from enum import Enum


class GenerativeCondition(str, Enum):
    GENERATIVE_COHERENCE = "generative_coherence"
    CRYSTALLIZATION_RISK = "crystallization_risk"
    FRAGMENTATION_RISK = "fragmentation_risk"
    COLLAPSE_OR_STAGNATION_RISK = "collapse_or_stagnation_risk"


@dataclass(frozen=True)
class GenerativeCoherenceObservation:
    coherence: float
    differentiation_floor: float
    coherence_floor: float
    required_differentiation_floor: float
    provenance: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name in (
            "coherence",
            "differentiation_floor",
            "coherence_floor",
            "required_differentiation_floor",
        ):
            value = getattr(self, name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be in [0.0, 1.0]")

    @property
    def condition(self) -> GenerativeCondition:
        coherent = self.coherence >= self.coherence_floor
        differentiated = self.differentiation_floor >= self.required_differentiation_floor
        if coherent and differentiated:
            return GenerativeCondition.GENERATIVE_COHERENCE
        if coherent and not differentiated:
            return GenerativeCondition.CRYSTALLIZATION_RISK
        if not coherent and differentiated:
            return GenerativeCondition.FRAGMENTATION_RISK
        return GenerativeCondition.COLLAPSE_OR_STAGNATION_RISK

    @property
    def homogenization_detected(self) -> bool:
        return self.condition is GenerativeCondition.CRYSTALLIZATION_RISK
