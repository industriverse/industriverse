import numpy as np
from ebm_lib.base import EnergyPrior

class MotorPriorV1:
    name = "motor"
    version = "v1"
    required_fields = ["rpm", "torque", "current"]
    metadata = {
        "equations": ["Lorentz Force Law", "Back-EMF"],
        "description": "Electromechanical energy balance for DC brushless motors.",
    }

    def validate(self, state):
        pass # Using state_vector index mapping

    def energy(self, state):
        # State vector mapping:
        # 0: RPM (rad/s approx)
        # 1: Torque (Nm)
        # 2: Current (A)
        # 3: Voltage (V)
        x = state["state_vector"]
        rpm = x[0]
        torque = x[1]
        current = x[2]
        voltage = x[3]
        
        # Motor Constants (Simulated)
        Kt = 0.1 # Torque constant (Nm/A)
        Kv = 0.1 # Back-EMF constant (V/(rad/s))
        R = 0.5  # Winding resistance (Ohms)
        
        # 1. Torque Physics: Torque should equal Kt * Current
        # E_torque = (Torque - Kt * I)^2
        e_torque = (torque - Kt * current)**2
        
        # 2. Electrical Physics: V = I*R + Back-EMF (Kv * RPM)
        # E_elec = (V - (I*R + Kv*RPM))^2
        back_emf = Kv * rpm
        e_elec = (voltage - (current * R + back_emf))**2
        
        # 3. Efficiency/Heat Penalty: I^2 * R loss should be minimized (soft constraint)
        e_heat = 0.01 * (current**2 * R)
        
        return float(10.0 * e_torque + 10.0 * e_elec + e_heat)

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

PRIOR = MotorPriorV1()
