import numpy as np
from ebm_lib.base import EnergyPrior

class SensorIntPriorV1:
    name = "sensorint"
    version = "v1"
    required_fields = ["lidar_dist", "camera_dist", "fused_dist"]
    metadata = {
        "equations": ["Kalman Filter Update", "Gaussian Likelihood"],
        "description": "Sensor fusion energy minimization.",
    }

    def validate(self, state):
        pass

    def energy(self, state):
        # State vector mapping:
        # 0: Lidar Distance (m)
        # 1: Camera Distance (m)
        # 2: Fused Distance (m)
        # 3: Confidence (0-1)
        x = state["state_vector"]
        z_lidar = x[0]
        z_cam = x[1]
        x_est = x[2]
        conf = x[3]
        
        # Variances (Assumed)
        R_lidar = 0.01 # Lidar is precise
        R_cam = 0.1    # Camera is noisy
        
        # Kalman Energy: Weighted squared error
        # E = (z1 - x)^2 / R1 + (z2 - x)^2 / R2
        e_fusion = (z_lidar - x_est)**2 / R_lidar + (z_cam - x_est)**2 / R_cam
        
        # Confidence should be high if residuals are low
        # Residual = |z1 - x| + |z2 - x|
        residual = abs(z_lidar - x_est) + abs(z_cam - x_est)
        pred_conf = np.exp(-residual)
        e_conf = 10.0 * (conf - pred_conf)**2
        
        return float(e_fusion + e_conf)

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

PRIOR = SensorIntPriorV1()
