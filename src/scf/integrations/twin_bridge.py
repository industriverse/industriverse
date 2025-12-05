import time
import math
import random
from typing import Dict, Any

class TwinBridge:
    """
    Simulates a connection to an Industrial Digital Twin (or real PLC).
    Models a simple thermal system (e.g., Server Cooling) with power/entropy dynamics.
    """
    def __init__(self, asset_id: str = "TWIN-001"):
        self.asset_id = asset_id
        # System State
        self.temperature = 65.0  # Celsius
        self.setpoint = 65.0
        self.load_factor = 0.8   # 0-1 (Compute Load)
        self.fan_speed = 0.5     # 0-1
        self.last_update = time.time()

    def read_sensors(self) -> Dict[str, float]:
        """
        Reads current state from the 'Twin'.
        """
        self._update_physics()
        
        # Calculate Power (Fan Power + Leakage)
        # Power scales cubically with fan speed (Physics Law)
        power_w = 200.0 + (800.0 * (self.fan_speed ** 3)) + (self.load_factor * 500.0)
        
        # Calculate Entropy Rate (Heat production / Temperature)
        # dS/dt = Q_dot / T
        heat_production = power_w * 0.9 # 90% of power becomes heat
        entropy_rate = heat_production / (self.temperature + 273.15)
        
        return {
            "timestamp": time.time(),
            "asset_id": self.asset_id,
            "temperature_c": self.temperature,
            "power_w": power_w,
            "entropy_rate": entropy_rate,
            "fan_speed": self.fan_speed,
            "load_factor": self.load_factor
        }

    def write_setpoint(self, parameter: str, value: float):
        """
        Sends a control command to the Twin.
        """
        if parameter == "fan_speed":
            self.fan_speed = max(0.1, min(1.0, value))
        elif parameter == "setpoint":
            self.setpoint = value
        print(f"   ⚙️ Twin Actuator: Set {parameter} to {value:.2f}")

    def _update_physics(self):
        """
        Evolves the simulation state based on simple thermodynamics.
        """
        now = time.time()
        dt = now - self.last_update
        self.last_update = now
        
        # Heat Source (Compute Load)
        q_in = self.load_factor * 1000.0 # Watts
        
        # Cooling (Fan)
        cooling_capacity = self.fan_speed * 1500.0 # Watts
        
        # Net Heat Flow
        q_net = q_in - cooling_capacity
        
        # Thermal Inertia (Mass * Specific Heat)
        thermal_mass = 5000.0 # J/K
        
        # Temp Change
        delta_T = (q_net * dt) / thermal_mass
        self.temperature += delta_T
        
        # Add some sensor noise
        self.temperature += random.uniform(-0.05, 0.05)
