import numpy as np
from ebm_lib.base import EnergyPrior

class BatteryPriorV1:
    name = "battery"
    version = "v1"
    required_fields = ["soc", "voltage", "temperature"]
    metadata = {
        "equations": ["Nernst Equation", "Arrhenius Law"],
        "description": "Electrochemical potential energy based on Nernst equation.",
    }

    def validate(self, state):
        for f in self.required_fields:
            if f not in state:
                raise ValueError(f"Missing required field: {f}")

    def energy(self, state):
        # State vector mapping:
        # 0: SoC (0.0 - 1.0)
        # 1: Voltage (V)
        # 2: Temperature (K)
        # 3: Current (A)
        x = state["state_vector"]
        soc = np.clip(x[0], 0.01, 0.99) # Avoid log(0)
        voltage = x[1]
        temp = x[2]
        
        # Nernst Equation Approximation for OCV (Open Circuit Voltage)
        # E = E0 - (RT/nF) * ln(Q)
        # Simplified: V_ocv = 3.7 + 0.5 * soc + 0.1 * ln(soc / (1-soc))
        v_ocv = 3.7 + 0.5 * soc + 0.05 * np.log(soc / (1.0 - soc))
        
        # Energy is the squared error from the physical ideal (Voltage - OCV)^2
        # Plus a penalty for extreme temperatures (Arrhenius-like degradation risk)
        voltage_energy = 10.0 * (voltage - v_ocv)**2
        
        # Temperature penalty: Optimal is 298K (25C). 
        # Energy rises exponentially as we deviate, especially high heat.
        temp_dev = (temp - 298.0) / 10.0
        temp_energy = np.exp(temp_dev**2 / 2.0) - 1.0
        
        return float(voltage_energy + temp_energy)

    def grad(self, state):
        # Numerical gradient approximation for simplicity and robustness
        x = state["state_vector"]
        epsilon = 1e-4
        grad_v = np.zeros_like(x)
        
        base_energy = self.energy(state)
        
        for i in range(len(x)):
            x_perturb = x.copy()
            x_perturb[i] += epsilon
            e_perturb = self.energy({"state_vector": x_perturb})
            grad_v[i] = (e_perturb - base_energy) / epsilon
            
        return {"state_vector": grad_v}

PRIOR = BatteryPriorV1()
