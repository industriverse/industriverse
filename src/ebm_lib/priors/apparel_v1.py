import numpy as np
from ebm_lib.base import EnergyPrior

class ApparelPriorV1:
    name = "apparel"
    version = "v1"
    required_fields = ["stress", "strain", "drape"]
    metadata = {
        "equations": ["Hooke's Law (2D)", "Kawabata Evaluation System"],
        "description": "Fabric mechanics and drape simulation.",
    }

    def validate(self, state):
        pass

    def energy(self, state):
        # State vector mapping:
        # 0: Stress (MPa)
        # 1: Strain (%)
        # 2: Drape Coefficient (0-1, 1=stiff, 0=fluid)
        # 3: Wear Cycle Predicted (Years)
        x = state["state_vector"]
        stress = x[0]
        strain = x[1]
        drape = x[2]
        wear = x[3]
        
        # 1. Stress-Strain Relationship (Non-linear for fabrics)
        # Stress = k * Strain + non_linear_term
        # Fabrics stiffen at high strain (J-curve)
        pred_stress = 0.1 * strain + 0.01 * strain**3
        e_mechanics = (stress - pred_stress)**2
        
        # 2. Drape vs Stiffness (Stress/Strain modulus)
        # Stiffer fabric (higher stress for same strain) -> Higher drape coeff (stiffer)
        modulus = stress / (strain + 0.1)
        pred_drape = np.tanh(modulus / 10.0) # Sigmoid to 0-1
        e_drape = 10.0 * (drape - pred_drape)**2
        
        # 3. Wear Prediction
        # High stress/strain cycles reduce life.
        # Wear ~ 1 / (Stress * Strain)
        # We want to maximize Wear (minimize -Wear).
        # But physically, Wear is a consequence.
        # Let's say Predicted Wear = 10.0 / (Stress * Strain + 0.1)
        pred_wear = 10.0 / (abs(stress * strain) + 0.1)
        e_wear = (wear - pred_wear)**2
        
        return float(e_mechanics + e_drape + e_wear)

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

PRIOR = ApparelPriorV1()
