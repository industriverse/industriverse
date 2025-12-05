class ThermodynamicSafetyGuard:
    """
    Enforces physics constraints on model outputs and control actions.
    """
    def __init__(self, max_temp_c: float = 100.0, max_pressure_bar: float = 10.0):
        self.max_temp = max_temp_c
        self.max_pressure = max_pressure_bar

    def check_energy_conservation(self, energy_in: float, energy_out: float, tolerance: float = 0.05) -> bool:
        """
        Energy cannot be created or destroyed (First Law).
        Allows for some measurement noise/tolerance.
        """
        delta = abs(energy_in - energy_out)
        # In a closed system, delta should be 0.
        # In an open system, delta = accumulation.
        # For this check, we assume we are checking a balance where they should match.
        return delta <= (energy_in * tolerance)

    def check_entropy_increase(self, ds_dt: float) -> bool:
        """
        Entropy of an isolated system must increase or stay constant (Second Law).
        dS/dt >= 0.
        Note: Local entropy can decrease if heat is exported, but for the total system it increases.
        Here we check if the predicted entropy rate is physically plausible.
        """
        # We allow small negative values due to numerical noise, but generally should be >= 0
        return ds_dt >= -1e-5

    def check_safety_limits(self, temp_c: float, pressure_bar: float) -> bool:
        """
        Operational safety limits.
        """
        if temp_c > self.max_temp:
            return False
        if pressure_bar > self.max_pressure:
            return False
        return True

    def validate_action(self, action_vector: list) -> bool:
        """
        Validate a control action before execution.
        """
        # Mock validation logic
        # Assume action_vector = [setpoint_temp, setpoint_pressure]
        if len(action_vector) != 2:
            return False
        return self.check_safety_limits(action_vector[0], action_vector[1])
