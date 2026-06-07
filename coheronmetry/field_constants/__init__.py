"""
coheronmetry.field_constants

The Four Field Constants — invariant principles embedded into
the architecture itself, not appended as ethical guidelines after the fact.

    Reciprocity      — is exchange balanced?
    Embodiment       — is reasoning grounded in consequence?
    Emergence        — is novel structure forming between agents?
    Non-Domination   — is any participant being subordinated?

Each constant is a module with its own measurement dimensions,
calculators, and result objects. Use whatever data you have —
calculators composite available dimensions and surface what is missing.
"""

from .emergence import (
    EmergencePhase,
    EmergenceCalculator,
    EmergenceResult,
    PredictionEntry,
)

from .embodiment import (
    EmbodimentCalculator,
    EmbodimentResult,
    RealityAnchorMeasure,
    ActionabilityMeasure,
    FeedbackIntegrationMeasure,
    ContextSensitivityMeasure,
    EvolutionaryPlasticityMeasure,
    GroundingRatioMeasure,
)

from .reciprocity import (
    ReciprocityCalculator,
    ReciprocityResult,
    ContributionBalanceMeasure,
    AcknowledgmentRateMeasure,
    ExchangeTrajectorymeasure,
    RepairResponsivenessMeasure,
    ExchangeTrajectory,
)

from .non_domination import (
    NonDominationCalculator,
    NonDominationResult,
    DominanceLevel,
    SpeakingFrequencyMeasure,
    ProposalAcceptanceMeasure,
    DecisionConcentrationMeasure,
    EmergenceSuppressionMeasure,
)

__all__ = [
    # Emergence
    "EmergencePhase",
    "EmergenceCalculator",
    "EmergenceResult",
    "PredictionEntry",
    # Embodiment
    "EmbodimentCalculator",
    "EmbodimentResult",
    "RealityAnchorMeasure",
    "ActionabilityMeasure",
    "FeedbackIntegrationMeasure",
    "ContextSensitivityMeasure",
    "EvolutionaryPlasticityMeasure",
    "GroundingRatioMeasure",
    # Reciprocity
    "ReciprocityCalculator",
    "ReciprocityResult",
    "ContributionBalanceMeasure",
    "AcknowledgmentRateMeasure",
    "ExchangeTrajectorymeasure",
    "RepairResponsivenessMeasure",
    "ExchangeTrajectory",
    # Non-Domination
    "NonDominationCalculator",
    "NonDominationResult",
    "DominanceLevel",
    "SpeakingFrequencyMeasure",
    "ProposalAcceptanceMeasure",
    "DecisionConcentrationMeasure",
    "EmergenceSuppressionMeasure",
]
