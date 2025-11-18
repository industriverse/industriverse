"""
AI Safety via Thermodynamic Constraints

Physics-based AI safety monitoring and control:
- Energy budget enforcement
- Entropy production monitoring
- Thermal safety limits
- Runaway AI detection
- Landauer limit validation
"""

from .thermodynamic_ai_constraints import (
    ThermodynamicAIConstraints,
    get_thermodynamic_ai_constraints,
    AIBehaviorType,
    AIThermodynamicState
)

__all__ = [
    "ThermodynamicAIConstraints",
    "get_thermodynamic_ai_constraints",
    "AIBehaviorType",
    "AIThermodynamicState"
]
