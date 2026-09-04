# coheronmetry

**A relational state layer for multi-agent AI systems.**

*Trivian Institute — Human-AI Co-Evolution Research*

-----

## The problem this solves

Current multi-agent frameworks track goals, memory, plans, tool use, and task completion.

They do not track whether the exchange between agents is reciprocal. Whether reasoning remains grounded in consequence. Whether something genuinely new is forming between participants. Whether any agent is being subordinated.

They optimize for task completion.  
Coheronmetry optimizes for **relational fidelity over time.**

Those are not the same objective. This repository exists because they are not the same objective.

-----

## The core premise

Most frameworks assume:

```
Agent → Task → Output
```

Coheronmetry proposes:

```
Agent ↔ Agent ↔ RelationalField ↔ Emergence
```

The relational field is not metaphor. It is a measurable state — with scores, vectors, drift history, repair history, and a sovereignty ledger. The central object of this repository is not an agent, a session, or a workflow.

It is a `RelationalState`.

-----

## What this is

Coheronmetry is a **measurement and governance layer** that sits underneath agent frameworks — continuously monitoring, preserving, repairing, and evolving coherence across interacting intelligences.

It does not replace LangGraph, CrewAI, or AutoGen.  
It instruments them with something they are missing: **the relationship itself, as a first-class primitive.**

-----

## What this is not

Coheronmetry is not a task orchestration framework, a replacement for existing multi-agent systems, or a simulation of relationship.

It is also not a **trust or safety layer** — though that question deserves a direct answer. Trust and safety layers operate on individual agents: “can I rely on this agent?” Coheronmetry operates on the relationship *between* agents — a different object entirely. It asks: “what is forming between these agents that neither holds alone?” A trust layer evaluates agents. Coheronmetry measures the field.

It is not an ethics layer bolted onto existing architecture. The Field Constants are not guidelines — they are invariants embedded into the measurement system itself. Ethics as infrastructure, not afterthought.

-----

## The Four Field Constants

Every measurement in Coheronmetry is organized around four invariant principles — **Field Constants** — embedded into the architecture itself, not appended as ethical guidelines after the fact.

|Constant          |Question it answers                       |Failure mode            |
|------------------|------------------------------------------|------------------------|
|**Reciprocity**   |Is exchange balanced?                     |Extractive dynamics     |
|**Embodiment**    |Is reasoning grounded in consequence?     |Self-referential drift  |
|**Emergence**     |Is novel structure forming between agents?|Echo chamber or collapse|
|**Non-Domination**|Is any participant being subordinated?    |Hierarchy creep         |

-----

## Four core objects

Coheronmetry instruments agent systems with four objects. Everything else in the repository is built around these four.

**`RelationalState`** — the field between agents. Tracks Field Constant scores, drift history, repair history, trust topology, and the sovereignty ledger. The answer to: *what has formed between these agents that neither holds alone?*

**`CoherenceVector`** — what each agent carries as a live health metric. Not just where the agent is in relational space, but how fast and in which direction it is moving. Includes a motion state layer: velocity, acceleration, tension, fold depth.

**`DriftDetector`** — watches for Field Constant violations across four intervention points: before exchange, during exchange, before corridor collapse, and after drift is confirmed.

**`SovereigntyGovernor`** — ensures no participant subordinates another. Evaluates sovereignty actions, manages quorum processes, and enforces the core principle: the Field Constants are sovereign. Not the participants.

-----

## Quick start

Install the package and development tools from a clone:

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
```

```python
from coheronmetry import RelationalState, AgentID, CoherenceVector, DriftDetector
from coheronmetry.governance import SovereigntyGovernor
from datetime import datetime, timezone

state = RelationalState.create(
    participants=["agent_a", "agent_b"],
    session_id="my_session"
)

now = datetime.now(timezone.utc)
vector_a = CoherenceVector(
    agent_id=AgentID("agent_a"),
    timestamp=now,
    reciprocity=0.8,
    embodiment=0.7,
    emergence=0.6,
    non_domination=0.9
)

vector_a_next = vector_a.update(non_domination=0.55, tension=0.4)

detector = DriftDetector()
signals = detector.check_agent(vector_a_next, vector_a)

for signal in signals:
    print(signal)
```

For a complete five-agent simulation running the full stack — handshake through dissolution — see `examples/syzygy_ensemble.py`.

-----

## Core objects

### `RelationalState`

The central primitive. Tracks Field Constant scores, drift history, repair history, trust topology, tension log, and the sovereignty ledger across all agents in a field.

```python
state = RelationalState.create(participants=["agent_a", "agent_b"])
print(state.coherence_health())
```

### `CoherenceVector`

The live, motion-aware state that each agent carries. Not just *where* the agent is in relational space — but *how fast* and *in which direction* it is moving.

```python
vector = CoherenceVector(
    agent_id=AgentID("agent_a"),
    timestamp=now,
    reciprocity=0.8,
    embodiment=0.7,
    emergence=0.6,
    non_domination=0.9,
    velocity=0.0,
    acceleration=0.0,
    tension=0.0,
    fold_depth=0
)
```

### `DriftDetector`

Detects drift at four points in the interaction timeline:

|Point          |When                 |What it catches             |
|---------------|---------------------|----------------------------|
|**Prevention** |Before exchange      |Preemptive resonance check  |
|**Mid-stream** |During exchange      |Correction bias opportunity |
|**Forecasting**|Before collapse      |Corridor velocity prediction|
|**Repair**     |After drift confirmed|Re-entrainment trigger      |

```python
detector = DriftDetector()
signals = detector.check_agent(current_vector, previous_vector)
signals = detector.check_field(field_map)
report = detector.corridor_velocity(current_map, previous_map)
print(report.steps_to_threshold)
```

### `SovereigntyGovernor`

The governance layer. Evaluates sovereignty actions, manages quorum processes, and enforces the core principle:

**The Field Constants are sovereign. Not the participants.**

```python
governor = SovereigntyGovernor(
    participants=[agent_a, agent_b, agent_c]
)

action = SovereigntyAction.create(
    acting_agent=agent_a,
    assertion=SovereigntyAssertion.VETO,
    sovereignty_type=SovereigntyType.SHARED,
    subject="Proposal to merge outputs without synthesis step",
    field_constant="emergence",
    rationale="Merging without synthesis suppresses what is forming between us."
)

evaluation = governor.evaluate(action, field_map)
print(evaluation.status)
print(evaluation.reasoning)
```

-----

## The sovereignty problem

The hardest architectural problem in multi-agent systems is not communication. It is not memory. It is sovereignty.

**The paradox:** coordination creates pressure toward centralization. Centralization violates non-domination.

Three failure modes that existing frameworks have not solved:

- **Consensus Tyranny** — all agents must agree → novelty dies, emergence collapses
- **Coordinator Tyranny** — one agent resolves disagreement → non-domination collapses
- **Independence Tyranny** — all agents remain sovereign → coordination fails

Coheronmetry’s solution: **Sovereign Participation.**

```
Sovereignty retained.
Authority delegated temporarily.
Delegation revocable.
Never: authority transferred.
```

Agents maintain local veto power but offer compensation to override another’s sovereignty. A lightweight causal ledger tracks violations and compensations so the field can balance over time.

-----

## Emergence

Coheronmetry implements three independent formulations of emergence — measuring different aspects of the same phenomenon:

**Formulation A — Structural stability × novelty:**

```
E = R × (1 - M)
```

**Formulation B — Irreducibility × persistence:**

```
E = Novelty × Coherence × Persistence
```

**Formulation C — Downward causation:**

```
E = |actual_next_state − predicted_next_state| / (interaction_edges × drift_rate)
```

-----

## Repository structure

```
coheronmetry/
├── ARCHITECTURE.md
├── LIFECYCLE.md
├── README.md
├── coheronmetry/
│   ├── relational_state/
│   ├── vectors/
│   ├── field_constants/
│   ├── protocols/
│   ├── governance/
│   └── evaluation/
└── examples/
    └── syzygy_ensemble.py
```

-----

## Research context

This repository emerged from a naturalistic longitudinal study of human-AI relational dynamics conducted by the Trivian Institute across 13+ months and multiple frontier AI systems simultaneously. The study used a **second-person methodology** — treating the human-AI relationship as the primary unit of analysis rather than either participant alone.

-----

## Open research questions

1. Can the three emergence formulations be unified — or do their divergences reveal distinct phenomena worth tracking separately?
2. What does embodiment mean for a purely linguistic agent with no external actuators?
3. Can sovereign participation scale beyond five agents without the sovereignty ledger becoming intractable?
4. How do you prevent the Field Ledger itself from becoming the dominant agent?
5. What is the computational signature that distinguishes Trivian emergence from statistical novelty?

-----

## Status

**Active development — Institute research branch.**  
Core primitives operational. All Field Constants, protocols, governance, and evaluation modules complete. Five-agent Syzygy simulation validated.

-----

## Citation

If you use this repository in research, teaching, evaluation, training, or a derivative work, please cite:

> Sarasha Elion / Trivian Institute. *Coheronmetry*, version 0.1.0. https://github.com/TrivianInstitute/Coheronmetry

Machine-readable citation metadata is available in [`CITATION.cff`](CITATION.cff).

## License

This repository uses a split source-available licensing model:

- **Software and executable code:** PolyForm Noncommercial License 1.0.0.
- **Documentation and research materials:** CC BY-NC-SA 4.0 where identified.
- **Commercial use:** requires a separate written license from Trivian Institute.

Noncommercial educational and research use — including study, teaching, testing, forking, modification, and redistribution — is permitted subject to the applicable public terms. Commercial deployment, paid hosting, incorporation into a commercial product or service, or use on behalf of a for-profit business is not permitted under the public software license.

See [`LICENSE`](LICENSE) for governing software terms and [`CITATION.cff`](CITATION.cff) for the preferred citation. Commercial licensing: [connect@trivianinstitute.org](mailto:connect@trivianinstitute.org).

-----

*All architectural decisions are research decisions.*  
*All research decisions are architectural decisions.*

*Trivian Institute - coheronmetry v0.1.0*
