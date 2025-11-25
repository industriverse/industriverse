import os
from typing import Optional

ENERGY_BUDGET = float(os.environ.get("ENERGY_BUDGET_J", "1000000"))  # default high
THREAT_THRESHOLD = float(os.environ.get("THREAT_THRESHOLD", "0.9"))
ENTROPY_BUDGET = float(os.environ.get("ENTROPY_BUDGET", "5.0"))


def should_throttle(energy_joules: Optional[float]) -> bool:
    if energy_joules is None:
        return False
    try:
        energy = float(energy_joules)
    except (TypeError, ValueError):
        return False
    return energy > ENERGY_BUDGET


def should_quarantine(threat_score: Optional[float]) -> bool:
    if threat_score is None:
        return False
    try:
        score = float(threat_score)
    except (TypeError, ValueError):
        return False
    return score >= THREAT_THRESHOLD


def entropy_alert(entropy: Optional[float]) -> bool:
    if entropy is None:
        return False
    try:
        ent = float(entropy)
    except (TypeError, ValueError):
        return False
    return ent > ENTROPY_BUDGET
