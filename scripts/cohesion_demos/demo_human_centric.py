import time
import numpy as np
import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from ebm_lib.registry import get as load_prior
import ebm_lib.priors
from ebm_runtime.samplers.langevin import langevin_sample

def run_human_centric():
    print("👥 STARTING COHESION DEMO: HUMAN-CENTRIC SHIFT")
    print("==============================================")
    print("🔗 Linking: WORKFORCE -> SCHEDULE -> LIFECYCLE")
    
    work_prior = load_prior("workforce_v1")
    sched_prior = load_prior("schedule_v1")
    life_prior = load_prior("lifecycle_v1")
    
    print("\n1️⃣  WORKFORCE MONITOR: Fatigue Analysis...")
    # State: [Fatigue, Prod, ShiftLength]
    # Simulate a long shift (10 hours)
    shift_len = 10.0
    work_state = {"state_vector": np.array([50.0, 80.0, shift_len])}
    
    # EBM predicts fatigue and productivity
    work_res = langevin_sample(work_prior, work_state, {"steps": 20, "lr": 0.1, "noise": 0.1})
    final_work = work_res["final_state"]
    fatigue = final_work[0]
    prod = final_work[1]
    
    print(f"   Shift Length: {shift_len}h -> Fatigue: {fatigue:.1f}% | Productivity: {prod:.1f}%")
    
    # Logic: If fatigue > 70%, trigger schedule rotation
    rotate_schedule = False
    if fatigue > 70.0:
        rotate_schedule = True
        print("   ⚠️ High Fatigue! Triggering Schedule Rotation...")
        
    print(f"\n2️⃣  SMART SCHEDULING: Fairness Optimization...")
    # State: [Entropy, Coverage, Overtime]
    # If rotation triggered, we accept some overtime to relieve the tired worker
    overtime_init = 0.0
    if rotate_schedule:
        overtime_init = 2.0 # Need coverage
        
    sched_state = {"state_vector": np.array([3.0, 90.0, overtime_init])}
    
    # EBM optimizes fairness
    sched_res = langevin_sample(sched_prior, sched_state, {"steps": 20, "lr": 0.1, "noise": 0.0})
    final_sched = sched_res["final_state"]
    entropy = final_sched[0]
    coverage = final_sched[1]
    
    print(f"   Fairness Entropy: {entropy:.2f} bits | Coverage: {coverage:.1f}%")
    
    print(f"\n3️⃣  LIFECYCLE PREDICTION: Retention Forecast...")
    # State: [Retention, Burnout, Tenure]
    # Simulate a worker with 24 months tenure
    tenure = 24.0
    life_state = {"state_vector": np.array([0.8, 0.2, tenure])}
    
    # EBM predicts burnout risk
    life_res = langevin_sample(life_prior, life_state, {"steps": 20, "lr": 0.01, "noise": 0.0})
    final_life = life_res["final_state"]
    retention = final_life[0]
    burnout = final_life[1]
    
    # Impact of intervention: If we rotated schedule, burnout drops
    if rotate_schedule:
        burnout *= 0.8
        retention = 1.0 - burnout
        print(f"   ✅ Intervention Applied. Burnout Risk Reduced by 20%.")
        
    print(f"   Tenure: {tenure} months -> Retention Prob: {retention:.2f} | Burnout Risk: {burnout:.2f}")
    
    proof = {
        "chain_id": f"human-centric-{int(time.time())}",
        "workforce": {"fatigue": fatigue, "productivity": prod},
        "schedule": {"fairness": entropy, "rotated": rotate_schedule},
        "lifecycle": {"retention": retention, "burnout": burnout},
        "timestamp": time.time()
    }
    
    out_path = os.path.join(os.path.dirname(__file__), "..", "..", "artifacts", "ebm_tnn_runs", "demo_human_centric.json")
    with open(out_path, "w") as f:
        json.dump(proof, f, indent=2)
        
    print(f"\n✅ COHESION PROOF MINTED: {out_path}")

if __name__ == "__main__":
    run_human_centric()
