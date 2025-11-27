import numpy as np
from ebm_lib.base import EnergyPrior

class WorkforcePriorV1:
    name = "workforce"
    version = "v1"
    required_fields = ["fatigue", "productivity", "shift_length"]
    metadata = {
        "equations": ["Circadian Rhythm Model", "Fatigue Accumulation"],
        "description": "Worker fatigue dynamics and productivity optimization.",
    }

    def validate(self, state):
        pass

    def energy(self, state):
        # State vector mapping:
        # 0: Fatigue Level (0-100)
        # 1: Productivity (0-100)
        # 2: Shift Length (hours)
        x = state["state_vector"]
        fatigue = np.clip(x[0], 0.0, 100.0)
        prod = x[1]
        shift = x[2]
        
        # 1. Fatigue Accumulation
        # Fatigue ~ exp(k * ShiftLength)
        # We want the observed fatigue to match the physical prediction
        pred_fatigue = 10.0 * np.exp(0.2 * shift)
        e_fatigue = (fatigue - pred_fatigue)**2
        
        # 2. Productivity vs Fatigue
        # Prod = Base - k * Fatigue
        pred_prod = 100.0 - 0.8 * fatigue
        e_prod = (prod - pred_prod)**2
        
        # 3. Shift Limit (Soft Constraint)
        # Shift shouldn't exceed 12 hours
        e_limit = 0.0
        if shift > 12.0:
            e_limit = 100.0 * (shift - 12.0)**2
            
        return float(e_fatigue + e_prod + e_limit)

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

PRIOR = WorkforcePriorV1()
