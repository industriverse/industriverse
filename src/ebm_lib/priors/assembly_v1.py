import numpy as np
from ebm_lib.base import EnergyPrior

class AssemblyPriorV1:
    name = "assembly"
    version = "v1"
    required_fields = ["throughput", "wip", "cycle_time"]
    metadata = {
        "equations": ["Little's Law", "Queueing Theory"],
        "description": "Production line flow optimization.",
    }

    def validate(self, state):
        pass

    def energy(self, state):
        # State vector mapping:
        # 0: Throughput (parts/hour)
        # 1: WIP (Work In Progress count)
        # 2: Cycle Time (minutes)
        x = state["state_vector"]
        throughput = x[0]
        wip = x[1]
        cycle_time = x[2]
        
        # 1. Little's Law Consistency
        # WIP = Throughput * CycleTime
        # Note units: Throughput (parts/min) = Throughput/60
        # WIP = (Throughput/60) * CycleTime
        pred_wip = (throughput / 60.0) * cycle_time
        e_little = 1.0 * (wip - pred_wip)**2
        
        # 2. Maximize Throughput (Minimize -Throughput)
        # But constrained by capacity (e.g., max 100 parts/hr)
        max_cap = 100.0
        e_cap = 0.0
        if throughput > max_cap:
            e_cap = 100.0 * (throughput - max_cap)**2 # Stronger penalty
        
        # Soft maximization
        e_max_thru = -0.1 * throughput
        
        # Safety bound to prevent explosion
        if throughput > 1000.0:
             e_cap += 1000.0 * (throughput - 1000.0)**2
        
        # 3. Minimize WIP (Inventory cost)
        e_wip = 0.5 * wip**2
        
        return float(e_little + e_cap + e_max_thru + e_wip)

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

PRIOR = AssemblyPriorV1()
