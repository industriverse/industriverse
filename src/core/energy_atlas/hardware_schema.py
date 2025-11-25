from pydantic import BaseModel, Field
from typing import Dict, Optional, List

class ElectricalProperties(BaseModel):
    """
    Electrical properties of a hardware node for thermodynamic modeling.
    E = 1/2 * C * V^2
    """
    capacitance_gate: float = Field(..., description="Gate capacitance (Farads)")
    capacitance_wire: float = Field(..., description="Wire capacitance (Farads)")
    capacitance_fringe: float = Field(0.0, description="Fringing capacitance (Farads)")
    voltage_min: float = Field(..., description="Minimum operating voltage (Volts)")
    voltage_max: float = Field(..., description="Maximum operating voltage (Volts)")
    leakage_current_base: float = Field(..., description="Base leakage current at 25C (Amps)")
    thermal_resistance: float = Field(..., description="Thermal resistance (K/W)")
    
    @property
    def total_capacitance(self) -> float:
        return self.capacitance_gate + self.capacitance_wire + self.capacitance_fringe

class HardwareNode(BaseModel):
    """
    Represents a physical hardware unit (GPU, TPU, Core) in the Energy Atlas.
    """
    node_id: str = Field(..., description="Unique identifier for the hardware node")
    node_type: str = Field(..., description="Type of node (e.g., 'gpu', 'cpu_core', 'tpu_slice')")
    electrical: ElectricalProperties
    location: Dict[str, float] = Field(default_factory=dict, description="Physical or logical coordinates")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Additional metadata")

class HardwareManifest(BaseModel):
    """
    Collection of hardware nodes to be loaded into the Energy Atlas.
    """
    nodes: List[HardwareNode]
    version: str = "1.0"
