from pydantic import BaseModel, Field
from typing import List, Optional

class AxisConstraint(BaseModel):
    axis: str
    min_pos_mm: float
    max_pos_mm: float
    max_velocity_mm_s: float
    max_acceleration_mm_s2: float

class ThermalEnvelope(BaseModel):
    max_temp_c: float
    optimal_temp_c: float
    cooling_rate_c_s: float

class MachineCapabilityModel(BaseModel):
    """
    Defines the physical constraints and capabilities of a manufacturing machine.
    This acts as the 'Hardware Abstraction Layer' for the AGI Loop.
    """
    machine_id: str
    machine_type: str  # e.g., "FDM_PRINTER", "CNC_MILL"
    
    # Kinematics
    axes: List[AxisConstraint]
    max_jerk_mm_s3: Optional[float] = None
    
    # Thermodynamics
    thermal_envelope: ThermalEnvelope
    power_consumption_watts: float
    
    # Capabilities
    supported_materials: List[str]
    min_layer_height_mm: Optional[float] = None
    spindle_max_rpm: Optional[float] = None
    
    def validate_intent(self, intent_plan: dict) -> bool:
        """
        Validates if a high-level intent plan is physically executable on this machine.
        """
        # 1. Material Check
        if 'material' in intent_plan and intent_plan['material'] not in self.supported_materials:
            return False
            
        # 2. Thermal Check (Mock logic for now)
        if 'temp_c' in intent_plan and intent_plan['temp_c'] > self.thermal_envelope.max_temp_c:
            return False
            
        return True
