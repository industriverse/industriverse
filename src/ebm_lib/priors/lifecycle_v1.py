import numpy as np
from ebm_lib.base import EnergyPrior

class LifecyclePriorV1:
    name = "lifecycle"
    version = "v1"
    required_fields = ["retention_prob", "burnout_risk"]
    metadata = {
        "equations": ["Survival Analysis", "Hazard Function"],
        "description": "Employee retention and burnout prediction.",
    }

    def validate(self, state):
        pass

    def energy(self, state):
        # State vector mapping:
        # 0: Retention Probability (0-1)
        # 1: Burnout Risk (0-1)
        # 2: Tenure (Months)
        x = state["state_vector"]
        retention = np.clip(x[0], 0.0, 1.0)
        burnout = np.clip(x[1], 0.0, 1.0)
        tenure = x[2]
        
        # 1. Burnout vs Retention
        # Retention ~ 1 - Burnout
        e_consistency = 100.0 * (retention - (1.0 - burnout))**2
        
        # 2. Burnout vs Tenure (Hazard Function)
        # Risk increases if tenure is high without breaks (simplified)
        # Let's say Burnout ~ 1 - exp(-k * Tenure)
        # But we want to MINIMIZE burnout.
        # The prior defines the relationship.
        # If tenure is high, burnout IS high physically unless mitigated.
        # We assume unmitigated state.
        pred_burnout = 1.0 - np.exp(-0.05 * tenure)
        e_hazard = 10.0 * (burnout - pred_burnout)**2
        
        return float(e_consistency + e_hazard)

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

PRIOR = LifecyclePriorV1()
