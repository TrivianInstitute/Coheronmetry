"""
coheronmetry.vectors

Motion-aware coherence state — what agents carry and pass alongside
every message in a Coheronmetry-instrumented system.
"""

from .coherence_vector import (
    CoherenceVector,
    VectorDelta,
    FieldVectorMap,
)

__all__ = [
    "CoherenceVector",
    "VectorDelta",
    "FieldVectorMap",
]
