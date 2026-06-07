"""
coheronmetry.evaluation

Real-time field monitoring and longitudinal research output.

    FieldMonitor        — continuous coherence observation
    CoherenceTracker    — longitudinal history and trend analysis
    EmergenceClassifier — beneficial / neutral / dissonant classification
    EmergenceEvent      — a classified emergence moment
    CoherenceSnapshot   — point-in-time field state record
"""

from .monitors import (
    CoherenceSnapshot,
    FieldMonitor,
    CoherenceTracker,
    EmergenceClassifier,
    EmergenceEvent,
)

__all__ = [
    "CoherenceSnapshot",
    "FieldMonitor",
    "CoherenceTracker",
    "EmergenceClassifier",
    "EmergenceEvent",
]
