import numpy as np
from ebm_lib.base import EnergyPrior

class MetalPriorV1:
    name = "metal"
    version = "v1"
    required_fields = ["atomic_spacing", "impurity_concentration"]
    metadata = {
        "equations": ["Lennard-Jones Potential"],
        "description": "Interatomic potential energy for alloy lattice structure.",
    }

    def validate(self, state):
        pass

    def energy(self, state):
        # State vector mapping:
        # 0: Atomic Spacing (Angstroms) - r
        # 1: Impurity Concentration (%)
        # 2: Lattice Strain (%)
        x = state["state_vector"]
        r = np.clip(x[0], 2.0, 5.0) # Constrain to realistic range
        impurity = x[1]
        strain = x[2]
        
        # Lennard-Jones Parameters for generic metal (e.g., Aluminum)
        epsilon = 1.0 # Depth of potential well
        sigma = 2.86  # Finite distance at which inter-particle potential is zero
        
        # V_LJ = 4 * epsilon * [(sigma/r)^12 - (sigma/r)^6]
        # We want to minimize this energy (find equilibrium spacing)
        term12 = (sigma / r) ** 12
        term6 = (sigma / r) ** 6
        v_lj = 4.0 * epsilon * (term12 - term6)
        
        # Impurity Penalty: High impurities distort lattice energy
        # E_impurity = k * (impurity)^2
        e_impurity = 0.1 * impurity**2
        
        # Strain Energy: E = 0.5 * YoungsModulus * strain^2
        # Normalized Young's Modulus
        e_strain = 5.0 * strain**2
        
        return float(v_lj + e_impurity + e_strain)

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

PRIOR = MetalPriorV1()
