"""
tests/unit/test_relational_state.py

Unit tests for RelationalState — the central object.

Trivian Institute — Coheronmetry Repository
"""

import unittest
from datetime import datetime, timezone

from coheronmetry.relational_state import (
    AgentID,
    RelationalState,
    DriftType,
    DriftEvent,
    RepairType,
    RepairEvent,
    SovereigntyEvent,
    SovereigntyType,
    EmergenceClass,
)


def now():
    return datetime.now(timezone.utc)


def make_drift(agent="alpha", drift_type=DriftType.DOMINANCE):
    return DriftEvent(
        timestamp=now(),
        drift_type=drift_type,
        detected_in=AgentID(agent),
        severity=0.35,
        field_constant_affected="non_domination",
    )


def make_repair(drift):
    return RepairEvent(
        timestamp=now(),
        repair_type=RepairType.RE_ENTRAINMENT,
        responding_to=drift,
        agents_involved=[AgentID("alpha"), AgentID("beta")],
        successful=True,
    )


class TestConstruction(unittest.TestCase):

    def test_two_agent_participants(self):
        state = RelationalState.create(participants=["alpha", "beta"])
        self.assertEqual(len(state.participants), 2)
        self.assertIn(AgentID("alpha"), state.participants)
        self.assertIn(AgentID("beta"), state.participants)

    def test_default_scores_neutral(self):
        state = RelationalState.create(participants=["a", "b"])
        self.assertEqual(state.reciprocity_score,    0.5)
        self.assertEqual(state.embodiment_score,     0.5)
        self.assertEqual(state.emergence_score,      0.5)
        self.assertEqual(state.non_domination_score, 0.5)

    def test_custom_initial_scores(self):
        state = RelationalState.create(
            participants=["a", "b"],
            initial_scores={"reciprocity": 0.8, "embodiment": 0.7,
                            "emergence": 0.6, "non_domination": 0.9}
        )
        self.assertAlmostEqual(state.reciprocity_score,    0.8)
        self.assertAlmostEqual(state.embodiment_score,     0.7)
        self.assertAlmostEqual(state.emergence_score,      0.6)
        self.assertAlmostEqual(state.non_domination_score, 0.9)

    def test_trust_edges_two_agents(self):
        state = RelationalState.create(participants=["a", "b"])
        self.assertEqual(len(state.trust_edges), 2)

    def test_trust_edges_three_agents(self):
        state = RelationalState.create(participants=["a", "b", "c"])
        self.assertEqual(len(state.trust_edges), 6)

    def test_trust_edges_neutral_start(self):
        state = RelationalState.create(participants=["a", "b"])
        for edge in state.trust_edges:
            self.assertEqual(edge.trust_score, 0.5)

    def test_unique_state_ids(self):
        s1 = RelationalState.create(participants=["a", "b"])
        s2 = RelationalState.create(participants=["a", "b"])
        self.assertNotEqual(s1.state_id, s2.state_id)

    def test_empty_history_on_creation(self):
        state = RelationalState.create(participants=["a", "b"])
        self.assertEqual(state.drift_history,  [])
        self.assertEqual(state.repair_history, [])
        self.assertEqual(state.tension_log,    [])


class TestScoreUpdates(unittest.TestCase):

    def setUp(self):
        self.state = RelationalState.create(participants=["a", "b"])

    def test_update_single_score(self):
        self.state.update_scores(reciprocity=0.9)
        self.assertAlmostEqual(self.state.reciprocity_score, 0.9)
        self.assertEqual(self.state.embodiment_score, 0.5)

    def test_clamp_upper(self):
        self.state.update_scores(reciprocity=1.5)
        self.assertEqual(self.state.reciprocity_score, 1.0)

    def test_clamp_lower(self):
        self.state.update_scores(reciprocity=-0.5)
        self.assertEqual(self.state.reciprocity_score, 0.0)

    def test_emergence_negative(self):
        """Negative emergence = chaos — valid field state."""
        self.state.update_scores(emergence=-0.3)
        self.assertAlmostEqual(self.state.emergence_score, -0.3)

    def test_emergence_negative_clamp(self):
        self.state.update_scores(emergence=-2.0)
        self.assertEqual(self.state.emergence_score, -1.0)

    def test_emergence_class_update(self):
        self.state.update_scores(emergence_class=EmergenceClass.BENEFICIAL)
        self.assertEqual(self.state.emergence_class, EmergenceClass.BENEFICIAL)

    def test_update_stamps_updated_at(self):
        before = self.state.updated_at
        self.state.update_scores(reciprocity=0.9)
        self.assertGreaterEqual(self.state.updated_at, before)


class TestDriftRecording(unittest.TestCase):

    def setUp(self):
        self.state = RelationalState.create(participants=["alpha", "beta"])

    def test_record_drift(self):
        drift = make_drift()
        self.state.record_drift(drift)
        self.assertEqual(len(self.state.drift_history), 1)

    def test_is_in_drift_true(self):
        self.state.record_drift(make_drift())
        self.assertTrue(self.state.is_in_drift())

    def test_is_in_drift_false_empty(self):
        self.assertFalse(self.state.is_in_drift())

    def test_is_in_drift_false_resolved(self):
        drift = make_drift()
        drift.resolve(now())
        self.state.record_drift(drift)
        self.assertFalse(self.state.is_in_drift())

    def test_multiple_drift_events(self):
        for dt in [DriftType.DOMINANCE, DriftType.RECIPROCITY_LOSS]:
            self.state.record_drift(make_drift(drift_type=dt))
        self.assertEqual(len(self.state.drift_history), 2)


class TestRepairRecording(unittest.TestCase):

    def setUp(self):
        self.state = RelationalState.create(participants=["alpha", "beta"])

    def test_record_repair(self):
        drift = make_drift()
        repair = make_repair(drift)
        self.state.record_repair(repair)
        self.assertEqual(len(self.state.repair_history), 1)

    def test_successful_repair_builds_trust(self):
        drift  = make_drift()
        repair = make_repair(drift)
        initial = [e.trust_score for e in self.state.trust_edges]
        self.state.record_repair(repair)
        final = [e.trust_score for e in self.state.trust_edges]
        self.assertTrue(any(f > i for f, i in zip(final, initial)))

    def test_failed_repair_no_trust_increase(self):
        drift  = make_drift()
        failed = RepairEvent(
            timestamp=now(),
            repair_type=RepairType.RE_ENTRAINMENT,
            responding_to=drift,
            agents_involved=[AgentID("alpha")],
            successful=False,
        )
        initial = [e.trust_score for e in self.state.trust_edges]
        self.state.record_repair(failed)
        final = [e.trust_score for e in self.state.trust_edges]
        self.assertEqual(initial, final)


class TestSovereignty(unittest.TestCase):

    def setUp(self):
        self.state = RelationalState.create(participants=["alpha", "beta"])

    def test_initial_balance_zero(self):
        self.assertEqual(self.state.sovereignty_balance(AgentID("alpha")), 0.0)

    def test_defer_adjusts_balances(self):
        event = SovereigntyEvent(
            timestamp=now(),
            acting_agent=AgentID("alpha"),
            affected_agent=AgentID("beta"),
            event_type="defer",
            sovereignty_type=SovereigntyType.SHARED,
            alignment_units=0.2,
        )
        self.state.record_sovereignty_event(event)
        self.assertAlmostEqual(
            self.state.sovereignty_balance(AgentID("alpha")), -0.2
        )
        self.assertAlmostEqual(
            self.state.sovereignty_balance(AgentID("beta")), 0.2
        )


class TestDiagnostics(unittest.TestCase):

    def setUp(self):
        self.state = RelationalState.create(participants=["alpha", "beta"])

    def test_coherence_health_structure(self):
        health = self.state.coherence_health()
        self.assertIn("field_constants",      health)
        self.assertIn("unresolved_drift_count", health)
        self.assertIn("sovereignty_balances", health)

    def test_coherence_health_field_constants(self):
        fc = self.state.coherence_health()["field_constants"]
        for key in ["reciprocity", "embodiment", "emergence", "non_domination"]:
            self.assertIn(key, fc)

    def test_dominant_agent_none_balanced(self):
        self.assertIsNone(self.state.dominant_agent())

    def test_trust_score_initial(self):
        score = self.state.trust_score(AgentID("alpha"), AgentID("beta"))
        self.assertEqual(score, 0.5)

    def test_trust_score_unknown_pair(self):
        score = self.state.trust_score(AgentID("alpha"), AgentID("unknown"))
        self.assertIsNone(score)

    def test_add_note(self):
        self.state.add_note("Test note.")
        self.assertEqual(len(self.state.notes), 1)
        self.assertIn("Test note.", self.state.notes[0])

    def test_repr_contains_agents(self):
        r = repr(self.state)
        self.assertIn("alpha", r)
        self.assertIn("beta",  r)


class TestEdgeCases(unittest.TestCase):

    def test_single_participant(self):
        state = RelationalState.create(participants=["solo"])
        self.assertEqual(len(state.participants), 1)
        self.assertEqual(state.trust_edges, [])

    def test_no_session_id_generates_one(self):
        state = RelationalState.create(participants=["a", "b"])
        self.assertIsNotNone(state.session_id)
        self.assertGreater(len(state.session_id), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
