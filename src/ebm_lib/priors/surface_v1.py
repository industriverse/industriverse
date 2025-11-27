import numpy as np
from ebm_lib.base import EnergyPrior

class SurfacePriorV1:
    name = "surface"
    version = "v1"
    required_fields = ["roughness", "defect_probability"]
    metadata = {
        "equations": ["Shannon Entropy", "Texture Analysis"],
        "description": "Surface anomaly detection via entropy.",
    }

    def validate(self, state):
        pass

    def energy(self, state):
        # State vector mapping:
        # 0: Surface Roughness (Ra)
        # 1: Texture Entropy (bits)
        # 2: Defect Probability (0-1)
        x = state["state_vector"]
        ra = x[0]
        entropy = x[1]
        prob = x[2]
        
        # 1. Texture Entropy Model
        # Smooth surface -> Low entropy. Rough/Defective -> High entropy.
        # Expected Entropy ~ k * Ra
        pred_entropy = 2.0 * ra
        e_entropy = 5.0 * (entropy - pred_entropy)**2
        
        # 2. Defect Probability
        # If Entropy > Threshold, Prob -> 1
        # Sigmoid function
        threshold = 5.0
        # Sigmoid function with stability check
        # 1 / (1 + exp(-x))
        x_val = entropy - threshold
        if x_val < -500:
            pred_prob = 0.0
        elif x_val > 500:
            pred_prob = 1.0
        else:
            pred_prob = 1.0 / (1.0 + np.exp(-x_val))
        e_prob = 10.0 * (prob - pred_prob)**2
        
        return float(e_entropy + e_prob)

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

PRIOR = SurfacePriorV1()
