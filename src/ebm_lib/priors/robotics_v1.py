import numpy as np
from ebm_lib.base import EnergyPrior

class RoboticsPriorV1:
    name = "robotics"
    version = "v1"
    required_fields = ["joint_angles", "velocity", "torque"]
    metadata = {
        "equations": ["Lagrangian Dynamics", "Kinetic Energy"],
        "description": "Robot arm dynamics and joint limit avoidance.",
    }

    def validate(self, state):
        pass

    def energy(self, state):
        # State vector mapping:
        # 0: Joint 1 Angle (rad)
        # 1: Joint 2 Angle (rad)
        # 2: Velocity (rad/s)
        # 3: Torque (Nm)
        x = state["state_vector"]
        q1 = x[0]
        q2 = x[1]
        vel = x[2]
        torque = x[3]
        
        # 1. Joint Limits (Soft Constraints)
        # Limits: -pi to pi
        e_limit = 0.0
        if abs(q1) > np.pi:
            e_limit += 10.0 * (abs(q1) - np.pi)**2
        if abs(q2) > np.pi:
            e_limit += 10.0 * (abs(q2) - np.pi)**2
            
        # 2. Kinetic Energy Minimization (Efficiency)
        # KE = 0.5 * Inertia * vel^2
        e_kinetic = 0.5 * 1.0 * vel**2
        
        # 3. Torque Efficiency
        # Minimize torque usage
        e_torque = 0.01 * torque**2
        
        # 4. Target Tracking (Mock)
        # Assume target is at q1=0, q2=0
        e_target = 5.0 * (q1**2 + q2**2)
        
        return float(e_limit + e_kinetic + e_torque + e_target)

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

PRIOR = RoboticsPriorV1()
