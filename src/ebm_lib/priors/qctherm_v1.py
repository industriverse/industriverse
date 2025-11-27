import numpy as np
from ebm_lib.base import EnergyPrior

class QcThermPriorV1:
    name = "qctherm"
    version = "v1"
    required_fields = ["thermal_gradient", "internal_stress"]
    metadata = {
        "equations": ["Fourier's Law", "Thermal Stress"],
        "description": "Internal defect detection via thermal imaging.",
    }

    def validate(self, state):
        pass

    def energy(self, state):
        # State vector mapping:
        # 0: Thermal Gradient (K/m)
        # 1: Internal Stress (MPa)
        # 2: Defect Depth (mm)
        x = state["state_vector"]
        grad = x[0]
        stress = x[1]
        depth = x[2]
        
        # 1. Thermal Gradient Anomaly
        # Uniform material -> Low gradient. Defect -> High gradient spike.
        # Gradient ~ 1 / Depth (closer to surface = sharper spike)
        # If depth is small (near surface), gradient is high.
        depth_safe = np.maximum(depth, 0.1)
        pred_grad = 10.0 / depth_safe
        e_grad = 0.1 * (grad - pred_grad)**2
        
        # 2. Thermal Stress
        # Stress = Alpha * E * DeltaT
        # DeltaT is proportional to Gradient * LengthScale
        # Simplified: Stress ~ k * Gradient
        pred_stress = 5.0 * grad
        e_stress = 0.01 * (stress - pred_stress)**2
        
        return float(e_grad + e_stress)

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

PRIOR = QcThermPriorV1()
