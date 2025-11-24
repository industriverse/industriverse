import os
from typing import Dict, Any

from src.core.energy_atlas.atlas_core import EnergyAtlas


class ThermoMetrics:
    """
    Provides thermodynamic metrics derived from EnergyAtlas manifests.
    """

    def __init__(self, manifest_path: str = "src/core/energy_atlas/sample_manifest.json"):
        self.manifest_path = os.environ.get("ENERGY_ATLAS_MANIFEST", manifest_path)
        self.atlas = EnergyAtlas(use_mock=True)
        try:
            self.atlas.load_manifest(self.manifest_path)
        except Exception:
            pass

    def current_metrics(self) -> Dict[str, Any]:
        try:
            energy_map = self.atlas.get_energy_map()
            node_count = energy_map.get("node_count", 0)
            nodes = energy_map.get("nodes", {})
            total_cap = sum([n.get("electrical", {}).get("total_capacitance", 0) for n in nodes.values()])
            avg_temp = sum([n.get("electrical", {}).get("thermal_resistance", 0) for n in nodes.values()]) / node_count if node_count else 0
            total_power = total_cap * 1e9  # rough heuristic
            entropy = 0.4 + (node_count * 0.01)
            return {
                "total_power_watts": total_power,
                "avg_temperature_c": avg_temp,
                "system_entropy": entropy,
                "node_count": node_count,
            }
        except Exception:
            return {
                "total_power_watts": 0.0,
                "avg_temperature_c": 0.0,
                "system_entropy": 0.0,
                "node_count": 0,
            }


thermo_metrics = ThermoMetrics()
