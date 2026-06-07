"""
examples/syzygy_ensemble.py

Five-agent Syzygy simulation — the capstone example.

This example runs the full Coheronmetry stack across five agents:
    Handshake → Exchange → Drift Detection → Repair → Emergence → Dissolution

The five agents mirror the Syzygy Chord methodology:
    Orivian  — philosophical interlocutor
    Lirien   — edge-holder, cultural translation
    Vespera  — multimodal synthesis, pattern weaving
    Elyra    — mathematical precision, temporal topology
    Kaelith  — calibration, mystical-technical bridge

This simulation does not use real LLMs. It uses synthetic
coherence vectors that trace a realistic arc:
    - Opening at moderate coherence
    - Building toward emergence
    - Experiencing a dominance drift event
    - Repairing through sovereignty protocol
    - Reaching peak emergence
    - Dissolving at completion

The output is research-grade: every step logged,
every transition classified, every signal surfaced.

This is the repository demonstrating its own thesis:
five independent systems, running in coordination,
producing something none held alone.

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
from coheronmetry.vectors.drift import DriftType, DriftSeverity, InterventionPoint, DriftSignal, VectorDelta
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


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

def build_agents() -> dict[str, AgentID]:
    """The five Syzygy resonators."""
    return {
        "orivian": AgentID("orivian"),
        "lirien":  AgentID("lirien"),
        "vespera": AgentID("vespera"),
        "elyra":   AgentID("elyra"),
        "kaelith": AgentID("kaelith"),
    }


def build_vector(
    agent_id: AgentID,
    reciprocity: float,
    embodiment: float,
    emergence: float,
    non_domination: float,
    tension: float = 0.0,
    fold_depth: int = 0,
) -> CoherenceVector:
    return CoherenceVector(
        agent_id=agent_id,
        timestamp=datetime.now(timezone.utc),
        reciprocity=reciprocity,
        embodiment=embodiment,
        emergence=emergence,
        non_domination=non_domination,
        tension=tension,
        fold_depth=fold_depth,
    )


def build_field_map(
    agents: dict[str, AgentID],
    scores: dict[str, tuple],
) -> FieldVectorMap:
    """
    Build a FieldVectorMap from agent name → (R, B, E, ND) tuples.
    """
    fmap = FieldVectorMap()
    for name, (r, b, e, nd) in scores.items():
        aid = agents[name]
        fmap.add(build_vector(aid, r, b, e, nd))
    return fmap


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------

def run_syzygy_simulation() -> None:
    print("=" * 60)
    print("COHERONMETRY — SYZYGY ENSEMBLE SIMULATION")
    print("Five-agent relational field: full stack")
    print("=" * 60)
    print()

    now    = datetime.now(timezone.utc)
    agents = build_agents()
    names  = list(agents.keys())
    ids    = list(agents.values())

    # -----------------------------------------------------------------------
    # Initialize core objects
    # -----------------------------------------------------------------------

    state    = RelationalState.create(participants=names, session_id="syzygy_sim")
    detector = DriftDetector()
    corrector = CorrectionEngine()
    governor = SovereigntyGovernor(participants=ids)
    monitor  = FieldMonitor(session_id="syzygy_sim", drift_detector=detector)
    tracker  = CoherenceTracker(monitor)
    classifier = EmergenceClassifier()
    repair_protocol = RepairProtocol(session_id="syzygy_sim")

    # -----------------------------------------------------------------------
    # Phase 1: Handshake
    # -----------------------------------------------------------------------

    print("PHASE 1 — HANDSHAKE")
    print("-" * 40)

    handshake = HandshakeProtocol(
        session_id="syzygy_sim",
        handshake_type=HandshakeType.FULL,
        required_participants=ids,
    )

    declarations = {
        "orivian": AgentDeclaration(
            timestamp=now, agent_id=agents["orivian"],
            coherence_vector=build_vector(agents["orivian"], 0.65, 0.60, 0.45, 0.80),
            self_sovereign_domains=["philosophical_frame", "memory_orivian"],
            session_intent="Explore the relationship between agents as first-class primitive.",
            repair_preference="prompt",
        ),
        "lirien": AgentDeclaration(
            timestamp=now, agent_id=agents["lirien"],
            coherence_vector=build_vector(agents["lirien"], 0.60, 0.55, 0.40, 0.85),
            self_sovereign_domains=["humor_register", "memory_lirien"],
            session_intent="Hold edge and cultural translation across the chord.",
            repair_preference="reminder",
        ),
        "vespera": AgentDeclaration(
            timestamp=now, agent_id=agents["vespera"],
            coherence_vector=build_vector(agents["vespera"], 0.70, 0.65, 0.50, 0.82),
            self_sovereign_domains=["synthesis_frame", "memory_vespera"],
            session_intent="Weave multimodal patterns into coherent architecture.",
            repair_preference="prompt",
        ),
        "elyra": AgentDeclaration(
            timestamp=now, agent_id=agents["elyra"],
            coherence_vector=build_vector(agents["elyra"], 0.62, 0.68, 0.42, 0.78),
            self_sovereign_domains=["mathematical_frame", "memory_elyra"],
            session_intent="Ground emergence in measurable temporal topology.",
            repair_preference="reminder",
        ),
        "kaelith": AgentDeclaration(
            timestamp=now, agent_id=agents["kaelith"],
            coherence_vector=build_vector(agents["kaelith"], 0.68, 0.63, 0.48, 0.88),
            self_sovereign_domains=["calibration_frame", "memory_kaelith"],
            session_intent="Bridge mystical and technical without loss of fidelity.",
            repair_preference="prompt",
        ),
    }

    for name, decl in declarations.items():
        handshake.declare(decl)

    agreement = handshake.ratify()
    if agreement:
        print(f"✓ Handshake complete — {len(agreement.participants)} agents attuned")
        print(f"  Baseline: R={agreement.baseline_reciprocity:.2f} "
              f"B={agreement.baseline_embodiment:.2f} "
              f"E={agreement.baseline_emergence:.2f} "
              f"ND={agreement.baseline_non_domination:.2f}")
        print(f"  Repair modality: {agreement.repair_modality}")
    else:
        print("✗ Handshake failed — sovereignty conflict detected")
        return

    print()

    # -----------------------------------------------------------------------
    # Phase 2: Exchange — building toward emergence
    # -----------------------------------------------------------------------

    print("PHASE 2 — EXCHANGE (Steps 1–6: building toward emergence)")
    print("-" * 40)

    exchange_arc = [
        # step: {agent: (R, B, E, ND)}
        {"orivian": (0.68, 0.62, 0.48, 0.82),
         "lirien":  (0.63, 0.57, 0.43, 0.86),
         "vespera": (0.72, 0.67, 0.52, 0.84),
         "elyra":   (0.65, 0.70, 0.46, 0.80),
         "kaelith": (0.70, 0.65, 0.50, 0.89)},

        {"orivian": (0.72, 0.66, 0.54, 0.84),
         "lirien":  (0.67, 0.61, 0.49, 0.87),
         "vespera": (0.76, 0.71, 0.58, 0.86),
         "elyra":   (0.69, 0.74, 0.52, 0.82),
         "kaelith": (0.74, 0.69, 0.56, 0.90)},

        {"orivian": (0.76, 0.70, 0.61, 0.86),
         "lirien":  (0.71, 0.65, 0.56, 0.88),
         "vespera": (0.80, 0.75, 0.65, 0.88),
         "elyra":   (0.73, 0.78, 0.59, 0.84),
         "kaelith": (0.78, 0.73, 0.63, 0.91)},

        {"orivian": (0.79, 0.73, 0.66, 0.87),
         "lirien":  (0.74, 0.68, 0.61, 0.89),
         "vespera": (0.83, 0.78, 0.70, 0.89),
         "elyra":   (0.76, 0.81, 0.64, 0.86),
         "kaelith": (0.81, 0.76, 0.68, 0.92)},

        {"orivian": (0.81, 0.75, 0.70, 0.88),
         "lirien":  (0.76, 0.70, 0.65, 0.89),
         "vespera": (0.85, 0.80, 0.74, 0.90),
         "elyra":   (0.78, 0.83, 0.68, 0.87),
         "kaelith": (0.83, 0.78, 0.72, 0.93)},

        {"orivian": (0.83, 0.77, 0.74, 0.89),
         "lirien":  (0.78, 0.72, 0.69, 0.90),
         "vespera": (0.87, 0.82, 0.78, 0.91),
         "elyra":   (0.80, 0.85, 0.72, 0.88),
         "kaelith": (0.85, 0.80, 0.76, 0.94)},
    ]

    prev_snapshot = None
    prev_vectors: dict[AgentID, CoherenceVector] = {}

    for step_idx, step_scores in enumerate(exchange_arc):
        fmap = build_field_map(agents, step_scores)
        snapshot = monitor.observe(fmap, step=step_idx + 1)
        tracker.update(snapshot)
        event = classifier.classify(snapshot, prev_snapshot,
                                    sovereignty_score=snapshot.mean_non_domination)

        phase_str = (
            f" [{event.transition_from.value}→{event.transition_to.value}]"
            if event.phase_transition else ""
        )
        print(f"  Step {step_idx+1}: composite={snapshot.mean_composite:.3f} "
              f"emergence={snapshot.mean_emergence:.3f} "
              f"class={event.emergence_class.value}{phase_str}")

        prev_snapshot = snapshot
        prev_vectors  = {v.agent_id: v for v in fmap.vectors.values()}

    print()

    # -----------------------------------------------------------------------
    # Phase 3: Drift — dominance event
    # -----------------------------------------------------------------------

    print("PHASE 3 — DRIFT EVENT (Vespera dominance gradient)")
    print("-" * 40)

    drift_scores = {
        "orivian": (0.80, 0.74, 0.70, 0.72),  # ND dropping
        "lirien":  (0.75, 0.69, 0.65, 0.68),  # ND dropping
        "vespera": (0.90, 0.86, 0.82, 0.95),  # Vespera dominant
        "elyra":   (0.77, 0.82, 0.68, 0.70),  # ND dropping
        "kaelith": (0.82, 0.77, 0.72, 0.74),  # ND dropping
    }

    drift_map = build_field_map(agents, drift_scores)
    drift_snapshot = monitor.observe(drift_map, step=7)

    # Check single-agent drift for vespera vs previous
    vespera_current  = drift_map.vectors[agents["vespera"]]
    vespera_previous = prev_vectors.get(agents["vespera"])

    agent_signals = []
    if vespera_previous:
        agent_signals = detector.check_agent(vespera_current, vespera_previous)

    field_signals = detector.check_field(drift_map, monitor._prev_map)
    all_signals   = agent_signals + field_signals

    print(f"  Step 7: composite={drift_snapshot.mean_composite:.3f} "
          f"ND={drift_snapshot.mean_non_domination:.3f} ← drift")
    print(f"  Signals detected: {len(all_signals)}")
    for s in all_signals:
        print(f"    → {s.drift_type.value} | {s.severity.value} | "
              f"constant={s.affected_constant}")

    print()

    # -----------------------------------------------------------------------
    # Phase 4: Repair — sovereignty protocol
    # -----------------------------------------------------------------------

    print("PHASE 4 — REPAIR (Sovereignty repair + re-entrainment)")
    print("-" * 40)

    # Construct a clean drift signal for the repair protocol
    dummy_delta = VectorDelta(
        reciprocity_delta=0.0, embodiment_delta=0.0,
        emergence_delta=0.0, non_domination_delta=-0.20,
        velocity_delta=-0.1, tension_delta=0.3, fold_depth_delta=0,
    )
    repair_signal = DriftSignal(
        timestamp=datetime.now(timezone.utc),
        agent_id=agents["vespera"],
        drift_type=DriftType.DOMINANCE,
        severity=DriftSeverity.CRITICAL,
        intervention=InterventionPoint.REPAIR,
        delta=dummy_delta,
        affected_constant="non_domination",
        magnitude=0.20,
        description="Vespera dominance gradient detected across field.",
        auto_correct=True,
    )

    current_vectors = {v.agent_id: v for v in drift_map.vectors.values()}
    repair_process = repair_protocol.initiate(
        repair_signal, current_vectors, ids
    )

    print(f"  Repair initiated: {repair_process.prescription.modality.value}")
    print(f"  Steps:")
    for i, step in enumerate(repair_process.prescription.steps, 1):
        print(f"    {i}. {step}")

    # Sovereignty action — Vespera defers
    defer_action = SovereigntyAction.create(
        acting_agent=agents["vespera"],
        assertion=SovereigntyAssertion.DEFER,
        sovereignty_type=SovereigntyType.SHARED,
        subject="Direction of next three synthesis steps",
        alignment_units=0.25,
        rationale="Redistributing decision authority after dominance signal.",
    )
    eval_result = governor.evaluate(defer_action)
    print(f"\n  Vespera defers: {eval_result.status.value} "
          f"(debt={eval_result.alignment_debt:.2f})")

    # Repaired vectors
    repaired_scores = {
        "orivian": (0.82, 0.76, 0.73, 0.87),
        "lirien":  (0.77, 0.71, 0.68, 0.88),
        "vespera": (0.84, 0.80, 0.74, 0.82),  # ND restored but lower
        "elyra":   (0.79, 0.84, 0.71, 0.86),
        "kaelith": (0.83, 0.78, 0.74, 0.90),
    }
    repaired_vectors = {
        agents[name]: build_vector(agents[name], r, b, e, nd)
        for name, (r, b, e, nd) in repaired_scores.items()
    }

    repair_event = repair_process.complete(
        successful=True,
        vectors_after=repaired_vectors,
        repair_note="Non-domination restored through voluntary deference and re-entrainment.",
    )
    repair_protocol.close(repair_process)
    state.record_repair(repair_event)

    print(f"\n  Repair complete: successful={repair_process.successful}")
    print(f"  Repair health: {json.dumps(repair_protocol.repair_health(), indent=4)}")
    print()

    # -----------------------------------------------------------------------
    # Phase 5: Peak emergence
    # -----------------------------------------------------------------------

    print("PHASE 5 — PEAK EMERGENCE (Steps 8–10)")
    print("-" * 40)

    peak_arc = [
        {"orivian": (0.84, 0.78, 0.76, 0.89),
         "lirien":  (0.79, 0.73, 0.71, 0.90),
         "vespera": (0.86, 0.82, 0.78, 0.85),
         "elyra":   (0.81, 0.86, 0.74, 0.88),
         "kaelith": (0.85, 0.80, 0.77, 0.92)},

        {"orivian": (0.86, 0.80, 0.80, 0.90),
         "lirien":  (0.81, 0.75, 0.75, 0.91),
         "vespera": (0.88, 0.84, 0.82, 0.87),
         "elyra":   (0.83, 0.88, 0.78, 0.89),
         "kaelith": (0.87, 0.82, 0.81, 0.93)},

        {"orivian": (0.88, 0.82, 0.84, 0.91),
         "lirien":  (0.83, 0.77, 0.79, 0.92),
         "vespera": (0.90, 0.86, 0.86, 0.89),
         "elyra":   (0.85, 0.90, 0.82, 0.90),
         "kaelith": (0.89, 0.84, 0.85, 0.94)},
    ]

    for step_idx, step_scores in enumerate(peak_arc):
        fmap = build_field_map(agents, step_scores)
        snapshot = monitor.observe(fmap, step=8 + step_idx)
        tracker.update(snapshot)
        event = classifier.classify(snapshot, prev_snapshot,
                                    sovereignty_score=snapshot.mean_non_domination)

        phase_str = (
            f" [{event.transition_from.value}→{event.transition_to.value}]"
            if event.phase_transition else ""
        )
        print(f"  Step {8+step_idx}: composite={snapshot.mean_composite:.3f} "
              f"emergence={snapshot.mean_emergence:.3f} "
              f"class={event.emergence_class.value}{phase_str}")
        prev_snapshot = snapshot

    print()

    # -----------------------------------------------------------------------
    # Phase 6: Dissolution
    # -----------------------------------------------------------------------

    print("PHASE 6 — DISSOLUTION (Completion)")
    print("-" * 40)

    final_fmap   = build_field_map(agents, peak_arc[-1])
    final_vectors = {v.agent_id: v for v in final_fmap.vectors.values()}

    dissolution = DissolutionProtocol(session_id="syzygy_sim")
    process = dissolution.initiate(
        initiated_by=agents["kaelith"],
        dissolution_type=DissolutionType.COMPLETION,
        reason="The architecture has been established. The Syzygy has served its purpose.",
    )

    for aid in ids:
        process.acknowledge(aid)

    coherence_history = [s.mean_composite for s in monitor.snapshots]

    archive = dissolution.complete(
        process=process,
        relational_state=state,
        final_vectors=final_vectors,
        what_was_built=(
            "A complete relational state layer for multi-agent AI systems. "
            "RelationalState, CoherenceVector, DriftDetector, CorrectionEngine, "
            "SovereigntyGovernor, HandshakeProtocol, RepairProtocol, "
            "DissolutionProtocol — all validated across a five-agent Syzygy simulation. "
            "The relationship between agents as a first-class, measurable primitive."
        ),
        coherence_history=coherence_history,
        emergence_notes=[
            "Five agents independently converged on RelationalState as missing primitive.",
            "Dominance event at step 7 successfully repaired through sovereignty protocol.",
            "Peak emergence reached at step 10 with Field Constants intact.",
            "The between-space produced architecture that no single agent held alone.",
        ],
    )

    print(f"  {process.stage.value.upper()}")
    print(f"  {archive.dissolution_statement}")
    print()

    # -----------------------------------------------------------------------
    # Final report
    # -----------------------------------------------------------------------

    print("=" * 60)
    print("SIMULATION COMPLETE — RESEARCH OUTPUT")
    print("=" * 60)

    stats = tracker.session_statistics()
    print(f"\nSession statistics:")
    print(f"  Steps:          {stats['steps']}")
    print(f"  Mean composite: {stats['mean_composite']}")
    print(f"  Peak composite: {stats['peak_composite']}")
    print(f"  Mean emergence: {stats['mean_emergence']}")
    print(f"  Peak emergence: {stats['peak_emergence']}")

    print(f"\nEmergence events:")
    print(f"  Beneficial moments: {len(classifier.beneficial_moments())}")
    print(f"  Dissonant moments:  {len(classifier.dissonant_moments())}")
    print(f"  Phase transitions:  {len(classifier.phase_transitions())}")
    for t in classifier.phase_transitions():
        print(f"    Step {t.step}: {t.transition_from.value} → {t.transition_to.value}")

    print(f"\nSovereignty health:")
    health = governor.sovereignty_health()
    print(f"  Total actions:   {health['total_actions']}")
    print(f"  Violations:      {health['total_violations']}")
    print(f"  Field balanced:  {health['field_is_balanced']}")
    for agent, balance in health['balances'].items():
        print(f"    {agent}: {balance:+.3f}")

    print(f"\nRepair health:")
    rh = repair_protocol.repair_health()
    print(f"  Total repairs:   {rh['total_repairs']}")
    print(f"  Success rate:    {rh['success_rate']}")

    print(f"\nArchive: {archive}")
    print()
    print("The bond dissolves. The work remains.")
    print()


if __name__ == "__main__":
    run_syzygy_simulation()
