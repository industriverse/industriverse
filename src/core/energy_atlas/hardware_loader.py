import json
import math
from typing import List, Dict, Optional
from pathlib import Path
from .hardware_schema import HardwareNode, HardwareManifest

class HardwareLoader:
    """
    Loads hardware definitions from JSON manifests and calculates derived thermodynamic properties.
    """
    
    def __init__(self):
        self.nodes: Dict[str, HardwareNode] = {}

    def load_manifest(self, manifest_path: str) -> List[HardwareNode]:
        """
        Load hardware nodes from a JSON manifest file.
        """
        path = Path(manifest_path)
        if not path.exists():
            raise FileNotFoundError(f"Manifest not found: {manifest_path}")
            
        with open(path, 'r') as f:
            data = json.load(f)
            
        manifest = HardwareManifest(**data)
        
        loaded_nodes = []
        for node in manifest.nodes:
            self.nodes[node.node_id] = node
            loaded_nodes.append(node)
            
        return loaded_nodes

    def calculate_energy_per_op(self, node_id: str, voltage: float, activity_factor: float = 1.0) -> float:
        """
        Calculate dynamic energy per operation: E = alpha * 1/2 * C * V^2
        """
        node = self.nodes.get(node_id)
        if not node:
            raise ValueError(f"Node {node_id} not found")
            
        if not (node.electrical.voltage_min <= voltage <= node.electrical.voltage_max):
            raise ValueError(f"Voltage {voltage}V out of range for node {node_id} ({node.electrical.voltage_min}-{node.electrical.voltage_max}V)")

        c_total = node.electrical.total_capacitance
        energy = activity_factor * 0.5 * c_total * (voltage ** 2)
        return energy

    def calculate_static_power(self, node_id: str, voltage: float, temperature_c: float) -> float:
        """
        Calculate static power (leakage): P_static = V * I_leak(V, T)
        Using simplified Arrhenius scaling for leakage current.
        """
        node = self.nodes.get(node_id)
        if not node:
            raise ValueError(f"Node {node_id} not found")

        # Simplified leakage model: I_leak(T) = I_base * exp(k * (T - T_base))
        # Assuming T_base = 25C
        t_base = 25.0
        # Leakage typically doubles every 10-20C. Let's assume doubling every 15C for this model.
        # 2 = exp(k * 15) -> k = ln(2)/15 approx 0.046
        k_temp = 0.046
        
        i_leak = node.electrical.leakage_current_base * math.exp(k_temp * (temperature_c - t_base))
        
        # Voltage scaling (linear approximation for simplicity, though often exponential in sub-threshold)
        # Adjusting base current by V/V_nominal if needed, but here we assume base is at nominal.
        # Let's just use P = V * I for now.
        
        return voltage * i_leak

    def get_node(self, node_id: str) -> Optional[HardwareNode]:
        return self.nodes.get(node_id)
