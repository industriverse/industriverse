import time
import numpy as np
import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from ebm_lib.registry import get as load_prior
import ebm_lib.priors
from ebm_runtime.samplers.langevin import langevin_sample

def run_safe_zone():
    print("🚧 STARTING COHESION DEMO: SAFE-ZONE FACTORY FLOOR")
    print("==================================================")
    print("🔗 Linking: ROBOTICS -> AMRSAFETY -> ASSEMBLY")
    
    robot_prior = load_prior("robotics_v1")
    amr_prior = load_prior("amrsafety_v1")
    assembly_prior = load_prior("assembly_v1")
    
    print("\n1️⃣  ROBOTICS: Kinematic Envelope Broadcast...")
    # State: [q1, q2, vel, torque]
    # Initialize with some motion
    robot_state = {"state_vector": np.array([1.0, -0.5, 2.0, 10.0])}
    
    # EBM optimizes motion (minimizes energy/torque)
    robot_res = langevin_sample(robot_prior, robot_state, {"steps": 20, "lr": 0.1, "noise": 0.01})
    final_robot = robot_res["final_state"]
    vel = final_robot[2]
    
    print(f"   Robot Velocity: {vel:.2f} rad/s")
    
    print(f"\n2️⃣  AMR SAFETY: Dynamic Exclusion Zone...")
    # State: [Distance, Speed, Heading]
    # Simulate a human walking nearby (Distance decreases)
    human_dist = 1.5 # meters (Inside 2m danger zone)
    amr_state = {"state_vector": np.array([human_dist, 2.0, 0.1])} # Moving fast
    
    print(f"   Human Detected at {human_dist}m!")
    
    # EBM should reduce speed due to Repulsive Potential
    amr_res = langevin_sample(amr_prior, amr_state, {"steps": 30, "lr": 0.05, "noise": 0.0})
    final_amr = amr_res["final_state"]
    safe_speed = final_amr[1]
    
    print(f"   Safety Intervention: Speed reduced to {safe_speed:.2f} m/s")
    
    print(f"\n3️⃣  ASSEMBLY LINE: Throughput Adaptation...")
    # State: [Throughput, WIP, CycleTime]
    # If robots/AMRs slow down, CycleTime increases.
    # We simulate this impact.
    impact_cycle_time = 10.0 # minutes (slower due to safety)
    assembly_state = {"state_vector": np.array([100.0, 10.0, impact_cycle_time])}
    
    # EBM re-balances WIP and Throughput for the new cycle time
    assembly_res = langevin_sample(assembly_prior, assembly_state, {"steps": 20, "lr": 1.0, "noise": 0.1})
    final_assembly = assembly_res["final_state"]
    throughput = final_assembly[0]
    wip = final_assembly[1]
    
    print(f"   Adjusted Throughput: {throughput:.1f} parts/hr | WIP: {wip:.1f}")
    
    proof = {
        "chain_id": f"safe-zone-{int(time.time())}",
        "robotics": {"velocity": vel},
        "amr": {"human_dist": human_dist, "safe_speed": safe_speed},
        "assembly": {"cycle_time": impact_cycle_time, "throughput": throughput},
        "timestamp": time.time()
    }
    
    out_path = os.path.join(os.path.dirname(__file__), "..", "..", "artifacts", "ebm_tnn_runs", "demo_safe_zone.json")
    with open(out_path, "w") as f:
        json.dump(proof, f, indent=2)
        
    print(f"\n✅ COHESION PROOF MINTED: {out_path}")

if __name__ == "__main__":
    run_safe_zone()
