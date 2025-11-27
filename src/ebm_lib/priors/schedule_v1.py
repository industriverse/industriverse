import numpy as np
from ebm_lib.base import EnergyPrior

class SchedulePriorV1:
    name = "schedule"
    version = "v1"
    required_fields = ["fairness_entropy", "coverage"]
    metadata = {
        "equations": ["Shannon Entropy (Fairness)", "Coverage Optimization"],
        "description": "Shift scheduling fairness and coverage.",
    }

    def validate(self, state):
        pass

    def energy(self, state):
        # State vector mapping:
        # 0: Fairness Entropy (Higher is fairer)
        # 1: Coverage (%)
        # 2: Overtime Hours
        x = state["state_vector"]
        entropy = x[0]
        coverage = x[1]
        overtime = x[2]
        
        # 1. Maximize Fairness Entropy (Minimize -Entropy)
        # Ideally Entropy should be high (uniform distribution of bad shifts)
        # Target Entropy = 5.0 bits (mock max)
        e_fairness = 10.0 * (entropy - 5.0)**2
        
        # 2. Maximize Coverage
        # Target = 100%
        e_coverage = 10.0 * (coverage - 100.0)**2
        
        # 3. Minimize Overtime
        e_overtime = 1.0 * overtime**2
        
        return float(e_fairness + e_coverage + e_overtime)

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

PRIOR = SchedulePriorV1()
