import time
import numpy as np
import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from ebm_lib.registry import get as load_prior
import ebm_lib.priors
from ebm_runtime.samplers.langevin import langevin_sample

def run_perfect_powertrain():
    print("🏎️  STARTING COHESION DEMO: PERFECT POWERTRAIN")
    print("==============================================")
    print("🔗 Linking: BATTERY -> MOTOR -> CHASSIS")
    
    batt_prior = load_prior("battery_v1")
    motor_prior = load_prior("motor_v1")
    chassis_prior = load_prior("chassis_v1")
    
    print("\n1️⃣  BATTERY MANAGEMENT: State of Health Check...")
    # Simulate a battery under load
    # State: [SoC, Voltage, Temp, Current]
    batt_state = {"state_vector": np.array([0.8, 3.9, 310.0, 50.0])} # 310K is hot (~37C)
    
    # EBM finds the most physically probable voltage for this SoC/Temp
    batt_res = langevin_sample(batt_prior, batt_state, {"steps": 20, "lr": 0.01, "noise": 0.001})
    final_batt = batt_res["final_state"]
    soc = final_batt[0]
    voltage = final_batt[1]
    temp = final_batt[2]
    
    print(f"   SoC: {soc*100:.1f}% | Voltage: {voltage:.2f}V | Temp: {temp:.1f}K")
    
    # Logic: If temp is high, limit current to motor
    max_current = 100.0
    if temp > 305.0:
        max_current = 40.0
        print(f"   ⚠️ High Temp Detected! Limiting Motor Current to {max_current}A")
        
    print(f"\n2️⃣  MOTOR CONTROL: Torque Optimization...")
    # Motor tries to maximize torque within current limit
    # State: [RPM, Torque, Current, Voltage]
    # We fix current to max_current and see what torque we get
    motor_state = {"state_vector": np.array([3000.0, 0.0, max_current, 48.0])} 
    
    # EBM solves for consistent Torque/RPM
    motor_res = langevin_sample(motor_prior, motor_state, {"steps": 20, "lr": 0.1, "noise": 0.1})
    final_motor = motor_res["final_state"]
    torque = final_motor[1]
    rpm = final_motor[0]
    
    print(f"   RPM: {rpm:.0f} | Optimized Torque: {torque:.2f} Nm (limited by current)")
    
    print(f"\n3️⃣  ACTIVE CHASSIS: Suspension Tuning...")
    # Chassis reacts to the torque (acceleration)
    # F = ma -> a = F/m. Approx accel from torque: a = Torque / (WheelRadius * Mass)
    # Assume WheelRadius=0.3m, Mass=1500kg
    accel_demand = torque / (0.3 * 1500.0)
    print(f"   Predicted Acceleration: {accel_demand:.2f} m/s^2")
    
    # State: [Travel, Velocity, Accel]
    # We want to find the suspension travel that minimizes energy for this accel
    chassis_state = {"state_vector": np.array([0.0, 0.0, accel_demand])}
    chassis_res = langevin_sample(chassis_prior, chassis_state, {"steps": 20, "lr": 0.001, "noise": 0.0})
    final_chassis = chassis_res["final_state"]
    travel = final_chassis[0] * 1000.0 # mm
    
    print(f"   Suspension Compression: {travel:.2f} mm to absorb launch.")
    
    proof = {
        "chain_id": f"powertrain-{int(time.time())}",
        "battery": {"soc": soc, "temp": temp, "limit": max_current},
        "motor": {"torque": torque, "rpm": rpm},
        "chassis": {"accel": accel_demand, "compression_mm": travel},
        "timestamp": time.time()
    }
    
    out_path = os.path.join(os.path.dirname(__file__), "..", "..", "artifacts", "ebm_tnn_runs", "demo_perfect_powertrain.json")
    with open(out_path, "w") as f:
        json.dump(proof, f, indent=2)
        
    print(f"\n✅ COHESION PROOF MINTED: {out_path}")

if __name__ == "__main__":
    run_perfect_powertrain()
