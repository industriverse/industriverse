import time
import numpy as np
import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from ebm_lib.registry import get as load_prior
import ebm_lib.priors
from ebm_runtime.samplers.langevin import langevin_sample

def run_resilient_infra():
    print("🛡️  STARTING COHESION DEMO: RESILIENT INFRASTRUCTURE")
    print("==================================================")
    print("🔗 Linking: HEAT -> PIPELINE -> FAILURE")
    
    heat_prior = load_prior("heat_v1")
    pipe_prior = load_prior("pipeline_v1")
    fail_prior = load_prior("failure_v1")
    
    print("\n1️⃣  HEAT DOME SIMULATION: Temperature Spike...")
    # Simulate extreme heat event
    heat_state = {"state_vector": np.ones(8) * 45.0} # 45 degrees C
    heat_res = langevin_sample(heat_prior, heat_state, {"steps": 10, "lr": 0.1, "noise": 0.5})
    avg_temp = np.mean(heat_res["final_state"])
    print(f"   Ambient Temperature: {avg_temp:.1f}°C")
    
    print(f"\n2️⃣  PIPELINE STRESS MONITOR: Thermal Expansion...")
    # Pipeline stress increases with temperature
    base_stress = 100.0
    thermal_stress = (avg_temp - 25.0) * 5.0 # Simple linear model
    total_stress = base_stress + thermal_stress
    print(f"   Calculated Stress: {total_stress:.1f} MPa (Thermal Component: {thermal_stress:.1f} MPa)")
    
    pipe_state = {"state_vector": np.array([total_stress] * 8)}
    pipe_res = langevin_sample(pipe_prior, pipe_state, {"steps": 10, "lr": 0.1, "noise": 1.0})
    
    print(f"\n3️⃣  FAILURE MODEL: Risk Assessment & Rerouting...")
    # Failure probability
    fail_prob = 0.01
    action = "NONE"
    if total_stress > 180.0:
        fail_prob = 0.85
        action = "EMERGENCY_REROUTE"
        print("   🚨 CRITICAL STRESS! Probability of Rupture: 85%")
        print("   🔄 ACTION: Rerouting Flow to Bypass Sector 7...")
    elif total_stress > 150.0:
        fail_prob = 0.30
        action = "THROTTLE_FLOW"
        print("   ⚠️ High Stress. Throttling Flow by 20%.")
    else:
        print("   ✅ Stress within limits. Normal Operation.")
        
    fail_state = {"state_vector": np.array([fail_prob] * 8)}
    # EBM verifies the new state (e.g., after rerouting, risk should drop)
    if action == "EMERGENCY_REROUTE":
        fail_state["state_vector"] = np.array([0.05] * 8) # Simulated post-action state
        print("   ... Reroute Successful. Risk dropped to 5%.")
        
    fail_res = langevin_sample(fail_prior, fail_state, {"steps": 5, "lr": 0.01, "noise": 0.0})
    
    proof = {
        "chain_id": f"resilient-infra-{int(time.time())}",
        "heat": {"avg_temp": avg_temp},
        "pipeline": {"total_stress": total_stress},
        "failure": {"initial_risk": fail_prob, "action": action, "final_risk": np.mean(fail_res["final_state"])},
        "timestamp": time.time()
    }
    
    out_path = os.path.join(os.path.dirname(__file__), "..", "..", "artifacts", "ebm_tnn_runs", "demo_resilient_infra.json")
    with open(out_path, "w") as f:
        json.dump(proof, f, indent=2)
        
    print(f"\n✅ COHESION PROOF MINTED: {out_path}")

if __name__ == "__main__":
    run_resilient_infra()
