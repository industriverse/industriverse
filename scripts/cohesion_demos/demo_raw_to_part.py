import time
import numpy as np
import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from ebm_lib.registry import get as load_prior
import ebm_lib.priors
from ebm_runtime.samplers.langevin import langevin_sample

def run_raw_to_part():
    print("🔩 STARTING COHESION DEMO: RAW-TO-PART TRACEABILITY")
    print("==================================================")
    print("🔗 Linking: METAL -> CASTING -> CNC")
    
    metal_prior = load_prior("metal_v1")
    cast_prior = load_prior("casting_v1")
    cnc_prior = load_prior("cnc_v1")
    
    print("\n1️⃣  ALLOY COMPOSITION: Lattice Optimization...")
    # State: [Atomic Spacing, Impurity, Strain]
    # Initial state: Strained, impure alloy
    metal_state = {"state_vector": np.array([3.5, 5.0, 0.1])}
    
    # EBM relaxes the lattice structure
    metal_res = langevin_sample(metal_prior, metal_state, {"steps": 20, "lr": 0.05, "noise": 0.01})
    final_metal = metal_res["final_state"]
    spacing = final_metal[0]
    impurity = final_metal[1]
    
    print(f"   Equilibrium Spacing: {spacing:.3f} Å | Impurity: {impurity:.2f}%")
    
    # Logic: High impurity affects casting cooling requirements
    target_cooling = 10.0
    if impurity > 2.0:
        target_cooling = 15.0 # Need faster cooling to freeze impurities
        print(f"   ⚠️ High Impurity! Increasing Target Cooling Rate to {target_cooling} C/s")
        
    print(f"\n2️⃣  SMART CASTING: Microstructure Control...")
    # State: [Cooling Rate, Nucleation, Porosity]
    # We initialize with the target cooling rate derived from Metal step
    cast_state = {"state_vector": np.array([target_cooling, 50.0, 5.0])}
    
    # EBM optimizes for grain structure
    cast_res = langevin_sample(cast_prior, cast_state, {"steps": 20, "lr": 0.1, "noise": 0.1})
    final_cast = cast_res["final_state"]
    nucleation = final_cast[1]
    porosity = final_cast[2]
    
    print(f"   Nucleation Density: {nucleation:.1f} grains/mm^2 | Porosity: {porosity:.2f}%")
    
    # Logic: Hardness proxy based on nucleation (Hall-Petch)
    hardness = 100.0 + 0.5 * nucleation
    print(f"   Estimated Hardness: {hardness:.1f} HB")
    
    print(f"\n3️⃣  ADAPTIVE CNC: Toolpath Generation...")
    # State: [Feed, Speed, Force, Roughness]
    # Harder material requires slower feed/speed to maintain force limits
    # We initialize with aggressive params and let EBM throttle them
    cnc_state = {"state_vector": np.array([500.0, 2000.0, 100.0, 1.0])}
    
    # EBM balances efficiency vs force/quality
    cnc_res = langevin_sample(cnc_prior, cnc_state, {"steps": 20, "lr": 10.0, "noise": 1.0}) # High LR for large scale params
    final_cnc = cnc_res["final_state"]
    feed = final_cnc[0]
    speed = final_cnc[1]
    force = final_cnc[2]
    
    print(f"   Optimized Feed: {feed:.1f} mm/min | Speed: {speed:.0f} RPM | Force: {force:.1f} N")
    
    proof = {
        "chain_id": f"raw-to-part-{int(time.time())}",
        "metal": {"spacing": spacing, "impurity": impurity},
        "casting": {"cooling_rate": final_cast[0], "hardness": hardness},
        "cnc": {"feed": feed, "speed": speed},
        "timestamp": time.time()
    }
    
    out_path = os.path.join(os.path.dirname(__file__), "..", "..", "artifacts", "ebm_tnn_runs", "demo_raw_to_part.json")
    with open(out_path, "w") as f:
        json.dump(proof, f, indent=2)
        
    print(f"\n✅ COHESION PROOF MINTED: {out_path}")

if __name__ == "__main__":
    run_raw_to_part()
