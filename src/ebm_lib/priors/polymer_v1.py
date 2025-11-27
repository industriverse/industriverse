import numpy as np
from ebm_lib.base import EnergyPrior

class PolymerPriorV1:
    name = "polymer"
    version = "v1"
    required_fields = ["chain_alignment", "tensile_strength"]
    metadata = {
        "equations": ["Flory-Huggins Solution Theory", "Rubber Elasticity"],
        "description": "Polymer chain dynamics and fiber extrusion.",
    }

    def validate(self, state):
        pass

    def energy(self, state):
        # State vector mapping:
        # 0: Chain Alignment (Order Parameter 0-1)
        # 1: Draw Ratio (Extension)
        # 2: Tensile Strength (MPa)
        x = state["state_vector"]
        alignment = np.clip(x[0], 0.0, 1.0)
        draw_ratio = x[1]
        strength = x[2]
        
        # 1. Entropic Elasticity
        # Aligning chains reduces entropy (increases free energy).
        # Nature wants random coils (alignment = 0).
        # We apply work (draw_ratio) to align them.
        # E_entropy = -T * S. S ~ ln(Omega).
        # Simplified: Energy cost to align
        e_entropy = 10.0 * alignment**2
        
        # 2. Draw Ratio vs Alignment
        # Higher draw ratio forces alignment.
        # Alignment ~ 1 - exp(-DrawRatio)
        pred_alignment = 1.0 - np.exp(-0.5 * draw_ratio)
        e_consistency = 100.0 * (alignment - pred_alignment)**2
        
        # 3. Strength vs Alignment
        # Strength scales linearly with alignment.
        # Strength = Base + k * Alignment
        pred_strength = 50.0 + 200.0 * alignment
        e_strength = (strength - pred_strength)**2
        
        # We want to maximize strength (minimize -strength) for the product,
        # but the physics prior describes the material behavior.
        # The "Controller" (TNN) would drive the state to high strength.
        # Here, the EBM ensures the state is PHYSICALLY CONSISTENT.
        
        return float(e_entropy + e_consistency + e_strength)

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

PRIOR = PolymerPriorV1()
