import pytest

from coheronmetry.evaluation.generative_coherence import (
    GenerativeCoherenceObservation,
    GenerativeCondition,
)


def observation(coherence, differentiation):
    return GenerativeCoherenceObservation(
        coherence=coherence,
        differentiation_floor=differentiation,
        coherence_floor=0.6,
        required_differentiation_floor=0.4,
        provenance=("orthogonal-signal:test",),
    )


def test_high_high_is_generative_coherence():
    assert observation(0.8, 0.8).condition is GenerativeCondition.GENERATIVE_COHERENCE


def test_high_coherence_low_difference_is_crystallization():
    obs = observation(0.9, 0.2)
    assert obs.condition is GenerativeCondition.CRYSTALLIZATION_RISK
    assert obs.homogenization_detected


def test_low_coherence_high_difference_is_fragmentation():
    assert observation(0.2, 0.8).condition is GenerativeCondition.FRAGMENTATION_RISK


def test_low_low_is_collapse_or_stagnation():
    assert observation(0.2, 0.2).condition is GenerativeCondition.COLLAPSE_OR_STAGNATION_RISK


def test_out_of_range_values_fail_closed():
    with pytest.raises(ValueError):
        observation(1.1, 0.8)
