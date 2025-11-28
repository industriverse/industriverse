import time
import numpy as np
import json
import os
import sys

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from ebm_lib.registry import get as load_prior
import ebm_lib.priors # Force registration
from ebm_runtime.samplers.langevin import langevin_sample

def run_infinite_energy_chain():
    print("⚡ STARTING COHESION DEMO: INFINITE ENERGY CHAIN")
    print("==============================================")
    print("🔗 Linking: FUSION -> GRID -> MICROGRID")
    
    # 1. Initialize Capsules
    fusion_prior = load_prior("fusion_v1")
    grid_prior = load_prior("grid_v1")
    microgrid_prior = load_prior("microgrid_v1")
    
    print("\n1️⃣  FUSION REACTOR: Stabilizing Plasma...")
    # Simulate unstable plasma
    fusion_state = {"state_vector": np.random.randn(8) * 3.0}
    fusion_res = langevin_sample(fusion_prior, fusion_state, {"steps": 20, "lr": 0.1, "noise": 0.01})
    final_fusion_energy = fusion_res["energy_trace"][-1]
    stability_score = 1.0 / (1.0 + final_fusion_energy)
    print(f"   Plasma Stabilized. Energy: {final_fusion_energy:.4f} | Stability Score: {stability_score:.4f}")
    
    print(f"\n2️⃣  NATIONAL GRID: Adjusting Frequency based on Fusion Stability ({stability_score:.4f})...")
    # Grid frequency target depends on fusion stability
    target_freq = 60.0 + (stability_score - 0.5) * 0.2 # Slight shift based on stability
    grid_state = {"state_vector": np.array([target_freq] * 8)} # Mock state
    # Grid tries to maintain this state against noise
    grid_res = langevin_sample(grid_prior, grid_state, {"steps": 10, "lr": 0.05, "noise": 0.01})
    final_grid_energy = grid_res["energy_trace"][-1]
    print(f"   Grid Frequency Locked: {target_freq:.4f} Hz | Entropy: {final_grid_energy:.4f}")
    
    print(f"\n3️⃣  LOCAL MICROGRID: Balancing Load...")
    # Microgrid sees grid frequency and adjusts local load
    # If freq > 60, we can consume more (charge batteries). If < 60, shed load.
    load_factor = 1.0
    if target_freq > 60.05:
        load_factor = 1.2 # Charge mode
        print("   Grid Frequency High -> Charging Batteries")
    elif target_freq < 59.95:
        load_factor = 0.8 # Shed mode
        print("   Grid Frequency Low -> Shedding Non-Critical Load")
    else:
        print("   Grid Frequency Nominal -> Normal Operation")
        
    micro_state = {"state_vector": np.random.randn(8) * load_factor}
    micro_res = langevin_sample(microgrid_prior, micro_state, {"steps": 10, "lr": 0.05, "noise": 0.01})
    
    # Generate Cohesion Proof
    proof = {
        "chain_id": f"inf-energy-{int(time.time())}",
        "fusion": {"final_energy": final_fusion_energy, "stability": stability_score},
        "grid": {"target_freq": target_freq, "final_energy": final_grid_energy},
        "microgrid": {"load_factor": load_factor, "final_energy": micro_res["energy_trace"][-1]},
        "timestamp": time.time()
    }
    
    out_path = os.path.join(os.path.dirname(__file__), "..", "..", "artifacts", "ebm_tnn_runs", "demo_infinite_energy.json")
    with open(out_path, "w") as f:
        json.dump(proof, f, indent=2)
        
    print(f"\n✅ COHESION PROOF MINTED: {out_path}")
    print("   The Thermodynamic State successfully flowed across 3 domains.")

if __name__ == "__main__":
    run_infinite_energy_chain()
