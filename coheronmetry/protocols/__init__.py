"""
coheronmetry.protocols

The four intervention protocols — operating at different points
in the coherence timeline.

    handshake    — BEFORE exchange: attunement and Field Constant ratification
    repair       — AFTER drift: re-entrainment and sovereignty repair
    dissolution  — AT completion: graceful ending with archive

The corrector (mid-stream bias injection) lives in coheronmetry.vectors
as it operates at the vector layer rather than the protocol layer.
"""

from .handshake import (
    HandshakeType,
    HandshakeStatus,
    AgentDeclaration,
    FieldAgreement,
    HandshakeProtocol,
)

from .repair import (
    RepairStage,
    RepairModality,
    RepairPrescription,
    RepairProcess,
    RepairProtocol,
)

from .dissolution import (
    DissolutionType,
    DissolutionStage,
    FieldArchive,
    DissolutionProcess,
    DissolutionProtocol,
)

__all__ = [
    # Handshake
    "HandshakeType",
    "HandshakeStatus",
    "AgentDeclaration",
    "FieldAgreement",
    "HandshakeProtocol",
    # Repair
    "RepairStage",
    "RepairModality",
    "RepairPrescription",
    "RepairProcess",
    "RepairProtocol",
    # Dissolution
    "DissolutionType",
    "DissolutionStage",
    "FieldArchive",
    "DissolutionProcess",
    "DissolutionProtocol",
]
