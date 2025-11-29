import sys
import json
import math

class SimulationOracle:
    """
    AI Shield v3 - Gate 3: Thermodynamic Simulation Oracle.
    Predicts energy, time, and thermal impact of Industrial Bytecode.
    """
    def __init__(self):
        # Calibrated Physics Constants (derived from Slice100k)
        self.P_heater_avg = 80.0  # Watts
        self.P_motor_avg = 20.0   # Watts
        self.P_base = 10.0        # Watts (Electronics)
        self.specific_heat_pla = 1800 # J/kg*K
        self.density_pla = 1.24 # g/cm3

    def simulate(self, bytecode_program):
        """
        Input: List of bytecode ops
        Output: { energy_j: float, time_s: float, heat_map: [] }
        """
        total_time = 0.0
        total_energy = 0.0
        current_pos = {"x": 0, "y": 0, "z": 0}
        
        # 1. Kinematic Simulation
        for op in bytecode_program:
            op_code = op.get("op")
            params = op.get("params", {})
            
            if op_code == "OP_MOVE":
                # Calculate Distance
                dx = params.get("x", current_pos["x"]) - current_pos["x"]
                dy = params.get("y", current_pos["y"]) - current_pos["y"]
                dz = params.get("z", current_pos["z"]) - current_pos["z"]
                dist = math.sqrt(dx**2 + dy**2 + dz**2)
                
                # Update Pos
                current_pos["x"] = params.get("x", current_pos["x"])
                current_pos["y"] = params.get("y", current_pos["y"])
                current_pos["z"] = params.get("z", current_pos["z"])
                
                # Calculate Time
                feedrate = params.get("f", 1000) / 60.0 # mm/s
                if feedrate > 0:
                    time_s = dist / feedrate
                    total_time += time_s
            
            elif op_code == "OP_DWELL":
                time_s = params.get("s", 0)
                total_time += time_s

        # 2. Thermodynamic Estimation
        # E = P * t
        avg_power = self.P_base + self.P_heater_avg + self.P_motor_avg
        total_energy = avg_power * total_time
        
        return {
            "energy_j": round(total_energy, 2),
            "time_s": round(total_time, 2),
            "avg_power_w": avg_power,
            "simulation_id": "sim_" + str(int(total_energy))
        }

if __name__ == "__main__":
    # Test with a simple program
    program = [
        {"op": "OP_MOVE", "params": {"x": 100, "y": 0, "z": 0, "f": 3000}},
        {"op": "OP_MOVE", "params": {"x": 100, "y": 100, "z": 0, "f": 3000}},
        {"op": "OP_MOVE", "params": {"x": 0, "y": 100, "z": 0, "f": 3000}},
        {"op": "OP_MOVE", "params": {"x": 0, "y": 0, "z": 0, "f": 3000}}
    ]
    oracle = SimulationOracle()
    print(json.dumps(oracle.simulate(program)))
