import numpy as np
from ebm_lib.base import EnergyPrior

class MagnetPriorV1:
    name = "magnet"
    version = "v1"
    required_fields = ["magnetic_field", "temperature", "demag_risk"]
    metadata = {
        "equations": ["Curie Law", "Hysteresis Loop"],
        "description": "Permanent magnet stability and demagnetization risk.",
    }

    def validate(self, state):
        pass

    def energy(self, state):
        # State vector mapping:
        # 0: Magnetic Field Strength (Tesla)
        # 1: Temperature (K)
        # 2: Demagnetization Risk (0-1)
        x = state["state_vector"]
        b_field = x[0]
        temp = x[1]
        risk = x[2]
        
        # 1. Curie Law / Thermal Degradation
        # Magnetization drops as Temp approaches Curie Temp (Tc).
        # For Neodymium, Tc ~ 580K.
        # But irreversible loss happens much lower (e.g., > 350K).
        # We model the "Energy Cost" of maintaining B-field at high Temp.
        # E_thermal = k * B^2 * exp(Temp / T_crit)
        e_thermal = 0.1 * b_field**2 * np.exp((temp - 300.0) / 50.0)
        
        # 2. Optimal Operating Point
        # Target B-field = 1.2 T
        e_optimal = 10.0 * (b_field - 1.2)**2
        
        # 3. Demagnetization Risk
        # Risk is high if Temp is high OR if opposing field (not modeled here) is high.
        # Here we link Risk to Temp and B-field stability.
        # PredRisk = Sigmoid((Temp - 350) / 10)
        # Use stable sigmoid
        x_val = (temp - 350.0) / 10.0
        if x_val < -500:
            pred_risk = 0.0
        elif x_val > 500:
            pred_risk = 1.0
        else:
            pred_risk = 1.0 / (1.0 + np.exp(-x_val))
            
        e_risk = 10.0 * (risk - pred_risk)**2
        
        return float(e_thermal + e_optimal + e_risk)

    def grad(self, state):
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

PRIOR = MagnetPriorV1()
