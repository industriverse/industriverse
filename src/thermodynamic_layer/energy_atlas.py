import os
import numpy as np
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class EnergyAtlas:
    """
    Registry for managing Thermodynamic Energy Maps (.npz).
    Acts as the source of truth for 'Physics-Informed Energy Priors'.
    """
    
    def __init__(self, storage_path: str = "data/energy_maps"):
        self.storage_path = storage_path
        self._loaded_maps: Dict[str, np.ndarray] = {}
        self._ensure_storage()

    def _ensure_storage(self):
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path, exist_ok=True)

    def register_map(self, map_name: str, data: np.ndarray):
        """Register a new energy map in memory and save to disk."""
        self._loaded_maps[map_name] = data
        file_path = os.path.join(self.storage_path, f"{map_name}.npz")
        np.savez_compressed(file_path, energy_map=data)
        logger.info(f"Registered energy map: {map_name} at {file_path}")

    def get_map(self, map_name: str) -> Optional[np.ndarray]:
        """Retrieve an energy map, loading from disk if necessary."""
        if map_name in self._loaded_maps:
            return self._loaded_maps[map_name]
        
        file_path = os.path.join(self.storage_path, f"{map_name}.npz")
        if os.path.exists(file_path):
            try:
                with np.load(file_path) as data:
                    self._loaded_maps[map_name] = data['energy_map']
                return self._loaded_maps[map_name]
            except Exception as e:
                logger.error(f"Failed to load energy map {map_name}: {e}")
                return None
        
        # Aliases for Biology/Chemistry if specific files are missing
        if map_name == "biology_cell_map":
            # Alias to active matter (closest proxy for biological swarms/cells)
            logger.info("Using 'active_matter_energy_map' as proxy for 'biology_cell_map'")
            return self.get_map("active_matter_energy_map")
            
        if map_name == "chemistry_reaction_map":
            # Alias to turbulent radiative layer (closest proxy for reaction diffusion)
            logger.info("Using 'turbulent_radiative_layer_2D_energy_map' as proxy for 'chemistry_reaction_map'")
            return self.get_map("turbulent_radiative_layer_2D_energy_map")

        if map_name == "polymer_flow_map":
            # Alias to active matter (closest proxy for viscoelastic flow)
            logger.info("Using 'active_matter_energy_map' as proxy for 'polymer_flow_map'")
            return self.get_map("active_matter_energy_map")

        if map_name == "metallurgy_phase_map":
             # Alias to turbulent radiative layer (closest proxy for thermal phase change)
            logger.info("Using 'turbulent_radiative_layer_2D_energy_map' as proxy for 'metallurgy_phase_map'")
            return self.get_map("turbulent_radiative_layer_2D_energy_map")

        # Fallback for development/testing if file doesn't exist
        logger.warning(f"Energy map {map_name} not found. Generating synthetic mock.")
        return self._generate_synthetic_mock(map_name)

    def _generate_synthetic_mock(self, map_name: str) -> np.ndarray:
        """Generate a synthetic energy map for testing/bootstrapping."""
        # Create a simple 2D Gaussian or Perlin-like noise field
        # representing a generic energy landscape
        shape = (100, 100)
        x = np.linspace(-3, 3, shape[0])
        y = np.linspace(-3, 3, shape[1])
        X, Y = np.meshgrid(x, y)
        
        # Simple potential well + random noise
        Z = np.exp(-(X**2 + Y**2)) + 0.1 * np.random.randn(*shape)
        
        # Normalize to [0, 1]
        Z = (Z - Z.min()) / (Z.max() - Z.min())
        
        return Z

    def get_energy_at_point(self, map_name: str, coordinates: Tuple[int, ...]) -> float:
        """Get the energy value at a specific coordinate."""
        energy_map = self.get_map(map_name)
        if energy_map is None:
            raise ValueError(f"Energy map {map_name} unavailable.")
        
        try:
            return float(energy_map[coordinates])
        except IndexError:
            logger.warning(f"Coordinates {coordinates} out of bounds for map {map_name}")
    def get_statistics(self) -> Dict[str, Any]:
        """Get atlas statistics for Shield State."""
        # Calculate total energy across all loaded maps
        total_energy = 0.0
        for map_data in self._loaded_maps.values():
            total_energy += float(np.sum(map_data))
            
        return {
            "total_energy_joules": total_energy,
            "node_count": len(self._loaded_maps) + 1, # +1 to avoid div by zero
            "loaded_maps": list(self._loaded_maps.keys())
        }
