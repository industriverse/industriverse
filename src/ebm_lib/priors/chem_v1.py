import numpy as np
from ebm_lib.base import EnergyPrior

class ChemPriorV1:
    name = "chem"
    version = "v1"
    required_fields = ["ph", "temperature", "toxicity"]
    metadata = {
        "equations": ["Gibbs Free Energy", "Arrhenius Equation"],
        "description": "Chemical reaction dynamics and toxicity minimization.",
    }

    def validate(self, state):
        pass

    def energy(self, state):
        # State vector mapping:
        # 0: pH (0-14)
        # 1: Temperature (K)
        # 2: Toxicity Index (0-100)
        # 3: Reaction Yield (%)
        x = state["state_vector"]
        ph = x[0]
        temp = x[1]
        toxicity = x[2]
        yield_pct = x[3]
        
        # 1. Optimal pH for Dye Synthesis (e.g., pH 7.0 neutral)
        e_ph = 5.0 * (ph - 7.0)**2
        
        # 2. Reaction Yield vs Temperature (Arrhenius)
        # Higher temp -> Higher yield, but also higher risk of side reactions (toxicity)
        # Optimal temp for this reaction is 350K
        e_temp = (temp - 350.0)**2
        
        # 3. Toxicity Penalty
        # We want to MINIMIZE toxicity.
        # Toxicity increases exponentially with temp > 360K
        tox_penalty = 0.0
        if temp > 360.0:
            # Clip temp to avoid overflow
            safe_temp = min(temp, 500.0)
            tox_penalty = np.exp((safe_temp - 360.0) / 5.0)
            
        # We also want high yield.
        # E_yield = -Yield (Maximize yield)
        # But yield is coupled to temp/pH physically.
        # Here we model the "Energy Landscape" where the minimum energy state IS the high yield state.
        # So we don't just force yield, we find the conditions that allow it.
        # Let's say Yield = 100 - (pH_error + Temp_error)
        pred_yield = 100.0 - (abs(ph - 7.0)*10.0 + abs(temp - 350.0)*0.5)
        e_yield_consistency = (yield_pct - pred_yield)**2
        
        # Explicit toxicity minimization
        e_tox = 10.0 * toxicity**2 + tox_penalty
        
        return float(e_ph + 0.1 * e_temp + e_yield_consistency + e_tox)

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

PRIOR = ChemPriorV1()
