from datetime import datetime, timezone

import pytest

from coheronmetry.vectors.coherence_vector import CoherenceVector


@pytest.mark.parametrize("name", [
    "reciprocity", "embodiment", "emergence", "non_domination",
    "tension", "velocity", "acceleration", "fold_depth",
])
@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf"), None, True])
def test_rejects_invalid_numeric_state(name, value):
    with pytest.raises(ValueError, match="finite number"):
        CoherenceVector("test", datetime.now(timezone.utc), **{name: value})


def test_mutation_cannot_promote_nan_to_perfect_score():
    vector = CoherenceVector("test", datetime.now(timezone.utc))
    vector.reciprocity = float("nan")
    with pytest.raises(ValueError, match="finite number"):
        _ = vector.relational_condition


def test_finite_clamping_and_negative_emergence_are_preserved():
    vector = CoherenceVector("test", datetime.now(timezone.utc),
                             reciprocity=2, embodiment=-1, emergence=-0.5)
    assert vector.reciprocity == 1
    assert vector.embodiment == 0
    assert vector.emergence == -0.5
    assert vector.qualified_emergence == 0


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_update_rejects_nonfinite_measurement(value):
    vector = CoherenceVector("test", datetime.now(timezone.utc))
    with pytest.raises(ValueError, match="finite number"):
        vector.update(reciprocity=value)
