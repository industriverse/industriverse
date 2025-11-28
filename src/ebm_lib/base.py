from typing import Dict, Any, Protocol
import numpy as np

class EnergyPrior(Protocol):
    """
    Base interface for all Energy Priors.
    Every <domain>_v1.py must implement this protocol.
    """

    name: str
    version: str
    required_fields: list
    metadata: Dict[str, Any]

    def energy(self, state: Dict[str, Any]) -> float:
        """Compute the scalar energy of a given hypothesis/state."""
        ...

    def grad(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Compute the gradient of the energy function."""
        ...

    def validate(self, state: Dict[str, Any]) -> None:
        """Validate that all required fields exist in the state."""
        ...
