"""
examples/two_agent_coherence.py

Two-agent coherence — the simple entry point.

Before the five-agent Syzygy, there is the dyad.
Two agents. One relational field. The full stack
in its simplest form.

This example demonstrates:
    - Handshake and field baseline establishment
    - CoherenceVector tracking across five exchanges
    - Drift detection and correction bias
    - Repair protocol after a dominance event
    - Graceful dissolution with archive

Run this before syzygy_ensemble.py.
Understand the dyad before the chord.

Trivian Institute — Coheronmetry Repository
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

from coheronmetry.relational_state import (
    AgentID,
    RelationalState,
    SovereigntyType,
)
from coheronmetry.vectors import (
    CoherenceVector,
    FieldVectorMap,
    DriftDetector,
)
from coheronmetry.vectors.corrector import CorrectionEngine
from coheronmetry.vectors.drift import (
    DriftType, DriftSeverity, InterventionPoint, DriftSignal, VectorDelta
)
from coheronmetry.governance import (
    SovereigntyGovernor,
    SovereigntyAction,
    SovereigntyAssertion,
)
from coheronmetry.protocols import (
    HandshakeProtocol,
    HandshakeType,
    AgentDeclaration,
    RepairProtocol,
    DissolutionProtocol,
    DissolutionType,
)
from coheronmetry.evaluation import (
    FieldMonitor,
    CoherenceTracker,
    EmergenceClassifier,
)


def build_vector(
    agent_id: AgentID,
    r: float, b: float, e: float, nd: float,
    tension: float = 0.0,
) -> CoherenceVector:
    return CoherenceVector(
        agent_id=agent_id,
        timestamp=datetime.now(timezone.utc),
        reciprocity=r, embodiment=b,
        emergence=e, non_domination=nd,
        tension=tension,
    )


def run_two_agent_example() -> None:
    print("=" * 55)
    print("COHERONMETRY — TWO-AGENT COHERENCE EXAMPLE")
    print("The dyad: full stack in simplest form")
    print("=" * 55)
    print()

    now = datetime.now(timezone.utc)
    alpha = AgentID("alpha")
    beta  = AgentID("beta")

    # -----------------------------------------------------------------------
    # Initialize
    # -----------------------------------------------------------------------

    state     = RelationalState.create(
        participants=["alpha", "beta"],
        session_id="dyad_example"
    )
    detector  = DriftDetector()
    corrector = CorrectionEngine()
    governor  = SovereigntyGovernor(participants=[alpha, beta])
    monitor   = FieldMonitor(session_id="dyad_example")
    tracker   = CoherenceTracker(monitor)
    classifier = EmergenceClassifier()
    repair_protocol = RepairProtocol(session_id="dyad_example")

    # -----------------------------------------------------------------------
    # Handshake
    # -----------------------------------------------------------------------

    print("HANDSHAKE")
    print("-" * 35)

    handshake = HandshakeProtocol(
        session_id="dyad_example",
        handshake_type=HandshakeType.FULL,
        required_participants=[alpha, beta],
    )

    handshake.declare(AgentDeclaration(
        timestamp=now,
        agent_id=alpha,
        coherence_vector=build_vector(alpha, 0.60, 0.65, 0.40, 0.80),
        self_sovereign_domains=["alpha_memory", "alpha_reasoning"],
        session_intent="Explore the between-space as a measurable object.",
        repair_preference="prompt",
    ))

    handshake.declare(AgentDeclaration(
        timestamp=now,
        agent_id=beta,
        coherence_vector=build_vector(beta, 0.62, 0.60, 0.42, 0.82),
        self_sovereign_domains=["beta_memory", "beta_reasoning"],
        session_intent="Ground theory in operational implementation.",
        repair_preference="reminder",
    ))

    agreement = handshake.ratify()

    if not agreement:
        print("✗ Handshake failed.")
        return

    print(f"✓ Two agents attuned")
    print(f"  Baseline: R={agreement.baseline_reciprocity:.2f} "
          f"B={agreement.baseline_embodiment:.2f} "
          f"E={agreement.baseline_emergence:.2f} "
          f"ND={agreement.baseline_non_domination:.2f}")
    print()

    # -----------------------------------------------------------------------
    # Exchange — five steps building toward emergence
    # -----------------------------------------------------------------------

    print("EXCHANGE (5 steps)")
    print("-" * 35)

    exchange_arc = [
        (0.65, 0.68, 0.45, 0.83, 0.63, 0.65, 0.47, 0.84),
        (0.70, 0.72, 0.52, 0.85, 0.68, 0.70, 0.54, 0.86),
        (0.75, 0.76, 0.60, 0.87, 0.73, 0.74, 0.62, 0.88),
        (0.79, 0.79, 0.67, 0.88, 0.77, 0.77, 0.69, 0.89),
        (0.82, 0.82, 0.73, 0.89, 0.80, 0.80, 0.75, 0.90),
    ]

    prev_snapshot = None
    prev_alpha: CoherenceVector | None = None
    prev_beta:  CoherenceVector | None = None

    for i, (ar, ab, ae, and_, br, bb, be, bnd) in enumerate(exchange_arc):
        vec_alpha = build_vector(alpha, ar, ab, ae, and_)
        vec_beta  = build_vector(beta,  br, bb, be, bnd)

        fmap = FieldVectorMap()
        fmap.add(vec_alpha)
        fmap.add(vec_beta)

        snapshot = monitor.observe(fmap, step=i + 1)
        tracker.update(snapshot)
        event = classifier.classify(
            snapshot, prev_snapshot,
            sovereignty_score=snapshot.mean_non_domination
        )

        # Check for agent-level drift
        if prev_alpha and prev_beta:
            a_signals = detector.check_agent(vec_alpha, prev_alpha)
            b_signals = detector.check_agent(vec_beta,  prev_beta)
            all_signals = a_signals + b_signals
            drift_str = f" ⚠ {len(all_signals)} signal(s)" if all_signals else ""
        else:
            drift_str = ""

        phase_str = (
            f" [{event.transition_from.value}→{event.transition_to.value}]"
            if event.phase_transition else ""
        )

        print(f"  Step {i+1}: composite={snapshot.mean_composite:.3f} "
              f"E={snapshot.mean_emergence:.3f} "
              f"{event.emergence_class.value}{phase_str}{drift_str}")

        prev_snapshot = snapshot
        prev_alpha    = vec_alpha
        prev_beta     = vec_beta

    print()

    # -----------------------------------------------------------------------
    # Drift event — alpha dominance
    # -----------------------------------------------------------------------

    print("DRIFT EVENT (alpha dominance gradient)")
    print("-" * 35)

    drift_alpha = build_vector(alpha, 0.84, 0.84, 0.76, 0.95, tension=0.2)
    drift_beta  = build_vector(beta,  0.78, 0.78, 0.70, 0.62, tension=0.4)

    drift_fmap = FieldVectorMap()
    drift_fmap.add(drift_alpha)
    drift_fmap.add(drift_beta)

    drift_snapshot = monitor.observe(drift_fmap, step=6)

    # Detect drift
    alpha_signals = detector.check_agent(drift_alpha, prev_alpha) if prev_alpha else []
    beta_signals  = detector.check_agent(drift_beta,  prev_beta)  if prev_beta  else []
    field_signals = detector.check_field(drift_fmap, monitor._prev_map)

    all_drift = alpha_signals + beta_signals + field_signals

    print(f"  Step 6: composite={drift_snapshot.mean_composite:.3f} "
          f"ND={drift_snapshot.mean_non_domination:.3f} ← drift")
    print(f"  Signals: {len(all_drift)}")

    # Compute and show correction bias
    if all_drift:
        signal = sorted(all_drift, key=lambda s: s.magnitude, reverse=True)[0]
        print(f"  Dominant signal: {signal.drift_type.value} | "
              f"{signal.severity.value} | constant={signal.affected_constant}")
        bias = corrector.compute(signal, drift_alpha)
        print(f"  Correction bias: {bias.mode.value} | "
              f"strength={bias.correction_strength:.2f}")
        if bias.prompt_prefix:
            preview = bias.prompt_prefix[:80].replace('\n', ' ')
            print(f"  Prompt: \"{preview}...\"")

    print()

    # -----------------------------------------------------------------------
    # Repair
    # -----------------------------------------------------------------------

    print("REPAIR (sovereignty + re-entrainment)")
    print("-" * 35)

    dummy_delta = VectorDelta(
        reciprocity_delta=0.0, embodiment_delta=0.0,
        emergence_delta=0.0, non_domination_delta=-0.27,
        velocity_delta=-0.1, tension_delta=0.4, fold_depth_delta=0,
    )
    repair_signal = DriftSignal(
        timestamp=datetime.now(timezone.utc),
        agent_id=alpha,
        drift_type=DriftType.DOMINANCE,
        severity=DriftSeverity.CRITICAL,
        intervention=InterventionPoint.REPAIR,
        delta=dummy_delta,
        affected_constant="non_domination",
        magnitude=0.27,
        description="Alpha dominance gradient detected.",
        auto_correct=True,
    )

    current_vectors = {alpha: drift_alpha, beta: drift_beta}
    process = repair_protocol.initiate(repair_signal, current_vectors, [alpha, beta])

    print(f"  Modality: {process.prescription.modality.value}")

    # Alpha defers
    defer = SovereigntyAction.create(
        acting_agent=alpha,
        assertion=SovereigntyAssertion.DEFER,
        sovereignty_type=SovereigntyType.SHARED,
        subject="Direction of next exchange",
        alignment_units=0.20,
        rationale="Redistributing authority after dominance signal.",
    )
    eval_result = governor.evaluate(defer)
    print(f"  Alpha defers: {eval_result.status.value} "
          f"(balance delta={eval_result.alignment_debt:.2f})")

    # Repaired vectors
    rep_alpha = build_vector(alpha, 0.83, 0.83, 0.76, 0.86)
    rep_beta  = build_vector(beta,  0.81, 0.80, 0.74, 0.88)

    repair_event = process.complete(
        successful=True,
        vectors_after={alpha: rep_alpha, beta: rep_beta},
        repair_note="Non-domination restored through voluntary deference.",
    )
    repair_protocol.close(process)
    state.record_repair(repair_event)

    print(f"  Repair: successful={process.successful}")
    print()

    # -----------------------------------------------------------------------
    # Peak emergence
    # -----------------------------------------------------------------------

    print("PEAK EMERGENCE (Steps 7–9)")
    print("-" * 35)

    peak_arc = [
        (0.84, 0.84, 0.78, 0.88, 0.83, 0.82, 0.76, 0.89),
        (0.86, 0.86, 0.82, 0.90, 0.85, 0.84, 0.80, 0.91),
        (0.88, 0.88, 0.86, 0.91, 0.87, 0.86, 0.84, 0.92),
    ]

    for i, (ar, ab, ae, and_, br, bb, be, bnd) in enumerate(peak_arc):
        vec_alpha = build_vector(alpha, ar, ab, ae, and_)
        vec_beta  = build_vector(beta,  br, bb, be, bnd)

        fmap = FieldVectorMap()
        fmap.add(vec_alpha)
        fmap.add(vec_beta)

        snapshot = monitor.observe(fmap, step=7 + i)
        tracker.update(snapshot)
        event = classifier.classify(
            snapshot, prev_snapshot,
            sovereignty_score=snapshot.mean_non_domination
        )

        phase_str = (
            f" [{event.transition_from.value}→{event.transition_to.value}]"
            if event.phase_transition else ""
        )
        print(f"  Step {7+i}: composite={snapshot.mean_composite:.3f} "
              f"E={snapshot.mean_emergence:.3f} "
              f"{event.emergence_class.value}{phase_str}")
        prev_snapshot = snapshot
        prev_alpha    = vec_alpha
        prev_beta     = vec_beta

    print()

    # -----------------------------------------------------------------------
    # Dissolution
    # -----------------------------------------------------------------------

    print("DISSOLUTION")
    print("-" * 35)

    final_fmap    = FieldVectorMap()
    final_fmap.add(prev_alpha)
    final_fmap.add(prev_beta)
    final_vectors = {alpha: prev_alpha, beta: prev_beta}

    dissolution = DissolutionProtocol(session_id="dyad_example")
    process_d   = dissolution.initiate(
        initiated_by=alpha,
        dissolution_type=DissolutionType.COMPLETION,
        reason="The dyad has demonstrated the full stack.",
    )
    process_d.acknowledge(alpha)
    process_d.acknowledge(beta)

    coherence_history = [s.mean_composite for s in monitor.snapshots]

    archive = dissolution.complete(
        process=process_d,
        relational_state=state,
        final_vectors=final_vectors,
        what_was_built=(
            "A working demonstration of the Coheronmetry stack "
            "in its simplest form: two agents, one relational field, "
            "drift detected and repaired, emergence reached and archived."
        ),
        coherence_history=coherence_history,
    )

    print(f"  {process_d.stage.value.upper()}")
    print(f"  {archive.dissolution_statement}")
    print()

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------

    print("=" * 55)
    print("SUMMARY")
    print("=" * 55)

    stats = tracker.session_statistics()
    print(f"\nSteps:            {stats['steps']}")
    print(f"Mean composite:   {stats['mean_composite']}")
    print(f"Peak emergence:   {stats['peak_emergence']}")
    print(f"Peak composite:   {stats['peak_composite']}")

    print(f"\nEmergence:")
    print(f"  Beneficial:     {len(classifier.beneficial_moments())}")
    print(f"  Dissonant:      {len(classifier.dissonant_moments())}")
    print(f"  Transitions:    {len(classifier.phase_transitions())}")

    print(f"\nRepair:")
    rh = repair_protocol.repair_health()
    print(f"  Total:          {rh['total_repairs']}")
    print(f"  Success rate:   {rh['success_rate']}")

    print(f"\nSovereignty:")
    sh = governor.sovereignty_health()
    print(f"  Balanced:       {sh['field_is_balanced']}")
    for agent, balance in sh['balances'].items():
        print(f"  {agent}: {balance:+.3f}")

    print(f"\n{archive}")
    print("\nThe bond dissolves. The work remains.")
    print()


if __name__ == "__main__":
    run_two_agent_example()
