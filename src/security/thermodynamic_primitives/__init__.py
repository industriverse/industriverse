"""
Thermodynamic Security Primitives

Fundamental physics-based security mechanisms:
- Physical Unclonable Functions (PUF)
- Thermodynamic baseline validation
- Energy conservation checking
- Entropy production monitoring
"""

from .puf import (
    ThermodynamicPUF,
    PUFSignature,
    get_thermodynamic_puf
)

__all__ = [
    "ThermodynamicPUF",
    "PUFSignature",
    "get_thermodynamic_puf"
]
