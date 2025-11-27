import numpy as np
from ebm_lib.base import EnergyPrior

class AmrSafetyPriorV1:
    name = "amrsafety"
    version = "v1"
    required_fields = ["distance_to_human", "speed"]
    metadata = {
        "equations": ["Artificial Potential Fields", "Repulsive Force"],
        "description": "Collision avoidance for autonomous mobile robots.",
    }

    def validate(self, state):
        pass

    def energy(self, state):
        # State vector mapping:
        # 0: Distance to Human (m)
        # 1: Robot Speed (m/s)
        # 2: Heading Error (rad)
        x = state["state_vector"]
        dist = np.clip(x[0], 0.1, 10.0) # Avoid div by zero
        speed = x[1]
        heading = x[2]
        
        # 1. Repulsive Potential (Safety)
        # U_rep = 0.5 * eta * (1/dist - 1/dist_0)^2 if dist < dist_0
        # dist_0 is influence range (e.g., 2.0m)
        dist_0 = 2.0
        e_rep = 0.0
        if dist < dist_0:
            e_rep = 50.0 * (1.0/dist - 1.0/dist_0)**2
            
        # 2. Attractive Potential (Goal Seeking)
        # We want to minimize Heading Error
        e_att = 5.0 * heading**2
        
        # 3. Speed Constraint
        # Speed should be low if distance is small
        # Max safe speed = k * dist
        max_safe_speed = 1.0 * dist
        e_speed = 0.0
        if speed > max_safe_speed:
            e_speed = 10.0 * (speed - max_safe_speed)**2
            
        return float(e_rep + e_att + e_speed)

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

PRIOR = AmrSafetyPriorV1()
