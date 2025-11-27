import numpy as np
from ebm_lib.base import EnergyPrior

class CncPriorV1:
    name = "cnc"
    version = "v1"
    required_fields = ["feed_rate", "spindle_speed", "cutting_force"]
    metadata = {
        "equations": ["Merchant's Circle Diagram", "Taylor's Tool Life"],
        "description": "Machining dynamics and tool wear optimization.",
    }

    def validate(self, state):
        pass

    def energy(self, state):
        # State vector mapping:
        # 0: Feed Rate (mm/min)
        # 1: Spindle Speed (RPM)
        # 2: Cutting Force (N)
        # 3: Surface Roughness (um)
        x = state["state_vector"]
        feed = x[0]
        speed = x[1]
        force = x[2]
        roughness = x[3]
        
        # 1. Cutting Force Model (Simplified Kienzle Force Model)
        # F = k * f^a * d^b
        # We want the observed Force to match the physical prediction based on feed/speed
        # Assume depth of cut is constant.
        # Predicted Force increases with feed rate.
        # Clip feed to avoid negative values in power operation
        safe_feed = np.maximum(feed, 1.0)
        pred_force = 10.0 * safe_feed**0.8
        e_force = 0.01 * (force - pred_force)**2
        
        # 2. Surface Roughness Model
        # R = f^2 / (8 * ToolRadius)
        # We want to minimize roughness.
        # Also, roughness increases if speed is too low (built-up edge).
        e_quality = 10.0 * roughness**2
        
        # 3. Efficiency (MRR - Material Removal Rate)
        # We want to MAXIMIZE Feed * Speed (Minimize -Feed*Speed)
        # But limited by Force and Roughness constraints.
        # We add a term that penalizes LOW removal rates.
        e_efficiency = 10000.0 / (feed * speed + 1.0)
        
        return float(e_force + e_quality + e_efficiency)

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

PRIOR = CncPriorV1()
