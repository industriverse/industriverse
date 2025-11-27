import numpy as np
from ebm_lib.base import EnergyPrior

class CastingPriorV1:
    name = "casting"
    version = "v1"
    required_fields = ["cooling_rate", "nucleation_density"]
    metadata = {
        "equations": ["Newton's Law of Cooling", "Hall-Petch Relation"],
        "description": "Thermodynamics of solidification and grain structure.",
    }

    def validate(self, state):
        pass

    def energy(self, state):
        # State vector mapping:
        # 0: Cooling Rate (C/s)
        # 1: Nucleation Density (grains/mm^2)
        # 2: Porosity (%)
        x = state["state_vector"]
        rate = x[0]
        nucleation = x[1]
        porosity = x[2]
        
        # Optimal Cooling Rate for specific alloy (e.g., 10 C/s)
        # Too slow -> coarse grains (weak). Too fast -> thermal shock/cracking.
        target_rate = 10.0
        e_rate = (rate - target_rate)**2
        
        # Hall-Petch: Strength scales with 1/sqrt(grain_size). 
        # Higher nucleation -> smaller grains -> higher strength.
        # We want to MAXIMIZE nucleation (Minimize -nucleation), but within limits.
        # Let's say optimal is 100 grains/mm^2
        e_structure = (nucleation - 100.0)**2
        
        # Porosity is strictly bad. Minimize it.
        # Porosity often increases if cooling rate is too low (shrinkage) or too high (gas entrapment)
        # Modeled as a direct penalty here.
        e_porosity = 10.0 * porosity**2
        
        return float(e_rate + 0.1 * e_structure + e_porosity)

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

PRIOR = CastingPriorV1()
