import numpy as np
from ebm_lib.base import EnergyPrior

class ChassisPriorV1:
    name = "chassis"
    version = "v1"
    required_fields = ["suspension_travel", "velocity"]
    metadata = {
        "equations": ["Hooke's Law", "Damping Force"],
        "description": "Mechanical energy of vehicle suspension system.",
    }

    def validate(self, state):
        pass

    def energy(self, state):
        # State vector mapping:
        # 0: Suspension Travel (m) - deviation from equilibrium
        # 1: Vertical Velocity (m/s)
        # 2: Acceleration (m/s^2)
        x = state["state_vector"]
        travel = x[0]
        velocity = x[1]
        accel = x[2]
        
        # Constants
        k = 50000.0 # Spring constant (N/m)
        c = 5000.0  # Damping coefficient (Ns/m)
        m = 1500.0  # Quarter car mass (kg) approx
        
        # 1. Potential Energy (Spring): 0.5 * k * x^2
        # We want to minimize excessive travel (bottoming out)
        e_potential = 0.5 * k * travel**2
        
        # 2. Damping Energy Dissipation
        # Force balance: F_spring + F_damper = m * a
        # k*x + c*v = m*a
        # Energy penalty for force imbalance (Newton's 2nd Law violation)
        force_imbalance = (k * travel + c * velocity) - (m * accel)
        e_dynamics = 0.001 * force_imbalance**2
        
        # 3. Comfort Penalty: Minimize acceleration (Jerk/G-force)
        e_comfort = 100.0 * accel**2
        
        # Normalize for EBM scale
        return float((e_potential + e_dynamics + e_comfort) * 1e-4)

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

PRIOR = ChassisPriorV1()
