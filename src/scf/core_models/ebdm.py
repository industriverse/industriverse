from typing import Any, Dict, Protocol
from src.thermodynamic_layer.energy_atlas import EnergyAtlas

class EBDM(Protocol):
    """
    Protocol for Energy-Based Diffusion Models in the SCF.
    """
    def energy(self, state: Dict[str, Any]) -> float:
        ...
    
    def grad(self, state: Dict[str, Any]) -> Dict[str, Any]:
        ...

class EBDMAdapter:
    """
    Adapts the EnergyAtlas to the SCF EBDM interface.
    Uses real physics-informed energy maps as priors.
    """
    def __init__(self):
        self.atlas = EnergyAtlas()

    def energy(self, state: Dict[str, Any]) -> float:
        """
        Computes energy using the Energy Atlas.
        Expects state to contain 'map_name' and 'coordinates'.
        """
        map_name = state.get("map_name", "generic_map")
        coords = state.get("coordinates", (0, 0))
        try:
            return self.atlas.get_energy_at_point(map_name, coords)
        except Exception:
            return 1.0 # Default high energy if lookup fails

    def grad(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Computes gradient (mocked for now as Atlas is discrete).
        """
        return {"grad": 0.0}
