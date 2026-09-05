from datetime import datetime, timezone

import pytest

from coheronmetry.relational_state.state import AgentID, EmergenceClass
from coheronmetry.vectors.coherence_vector import CoherenceVector, FieldVectorMap
from coheronmetry.evaluation.monitors import FieldMonitor


def vector(r=1.0, b=1.0, e=1.0, n=1.0):
    return CoherenceVector(AgentID("agent"), datetime.now(timezone.utc), r, b, e, n)


def test_relational_condition_is_multiplicative():
    state = vector(0.8, 0.5, 1.0, 0.25)
    assert state.relational_condition == pytest.approx(0.1)
    assert state.qualified_emergence == pytest.approx(0.1)


@pytest.mark.parametrize("scores", [(0, 1, 1), (1, 0, 1), (1, 1, 0)])
def test_constitutive_collapse_cannot_be_compensated(scores):
    r, b, n = scores
    assert vector(r, b, 1.0, n).relational_condition == 0.0


def test_emergence_is_not_an_input_to_relational_condition():
    low = vector(0.8, 0.8, 0.0, 0.8)
    high = vector(0.8, 0.8, 1.0, 0.8)
    assert low.relational_condition == high.relational_condition
    assert low.qualified_emergence == 0.0
    assert high.qualified_emergence == pytest.approx(0.512)


def test_corridor_requires_every_constitutive_dependency():
    assert vector(1.0, 0.69, 1.0, 1.0).is_in_corridor is False
    assert vector(0.7, 0.7, 0.1, 0.7).is_in_corridor is True


def test_monitor_marks_high_emergence_with_collapsed_dependency_dissonant():
    field = FieldVectorMap()
    field.add(vector(1.0, 0.1, 1.0, 1.0))
    snapshot = FieldMonitor("test").observe(field, 1)
    assert snapshot.mean_composite == pytest.approx(0.1)
    assert snapshot.emergence_class is EmergenceClass.DISSONANT
