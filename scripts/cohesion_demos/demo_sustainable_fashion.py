import time
import numpy as np
import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from ebm_lib.registry import get as load_prior
import ebm_lib.priors
from ebm_runtime.samplers.langevin import langevin_sample

def run_sustainable_fashion():
    print("👗 STARTING COHESION DEMO: SUSTAINABLE FASHION CYCLE")
    print("===================================================")
    print("🔗 Linking: CHEM -> POLYMER -> APPAREL")
    
    chem_prior = load_prior("chem_v1")
    poly_prior = load_prior("polymer_v1")
    apparel_prior = load_prior("apparel_v1")
    
    print("\n1️⃣  GREEN CHEMISTRY: Dye Synthesis Optimization...")
    # State: [pH, Temp, Toxicity, Yield]
    # Initialize with non-optimal conditions
    chem_state = {"state_vector": np.array([5.0, 300.0, 50.0, 0.0])}
    
    # EBM finds the low-energy (stable) state for reaction
    chem_res = langevin_sample(chem_prior, chem_state, {"steps": 30, "lr": 0.1, "noise": 0.1})
    final_chem = chem_res["final_state"]
    ph = final_chem[0]
    temp = final_chem[1]
    toxicity = final_chem[2]
    
    print(f"   Optimized pH: {ph:.2f} | Temp: {temp:.1f}K | Toxicity Index: {toxicity:.2f}")
    
    # Logic: Low toxicity allows for higher quality polymer extrusion
    draw_potential = 2.0
    if toxicity < 10.0:
        draw_potential = 5.0 # Can draw fibers more aggressively without breaking
        print("   ✅ Low Toxicity! Enabling High-Draw Extrusion.")
        
    print(f"\n2️⃣  POLYMER EXTRUSION: Fiber Alignment...")
    # State: [Alignment, Draw Ratio, Strength]
    # We set the Draw Ratio based on Chem step
    poly_state = {"state_vector": np.array([0.5, draw_potential, 100.0])}
    
    # EBM solves for physical properties
    poly_res = langevin_sample(poly_prior, poly_state, {"steps": 20, "lr": 0.05, "noise": 0.01})
    final_poly = poly_res["final_state"]
    alignment = final_poly[0]
    strength = final_poly[2]
    
    print(f"   Chain Alignment: {alignment:.2f} | Tensile Strength: {strength:.1f} MPa")
    
    print(f"\n3️⃣  APPAREL DESIGN: Durability Prediction...")
    # State: [Stress, Strain, Drape, Wear Life]
    # We simulate a specific strain (e.g., stretching during wear)
    # And see what Stress/Wear results based on the material Strength
    # Note: The Apparel prior models generic fabric. 
    # We inject the specific strength from Polymer step as a constraint/modifier?
    # For this demo, we assume the prior adapts or we interpret the result.
    
    # Let's simulate a high strain event (running)
    strain_event = 5.0 # %
    apparel_state = {"state_vector": np.array([0.0, strain_event, 0.5, 0.0])}
    
    apparel_res = langevin_sample(apparel_prior, apparel_state, {"steps": 20, "lr": 0.1, "noise": 0.0})
    final_apparel = apparel_res["final_state"]
    stress = final_apparel[0]
    wear_life = final_apparel[3]
    
    # Adjust wear life based on material strength from step 2
    # If strength is high, wear life improves
    adjusted_wear = wear_life * (strength / 100.0)
    
    print(f"   Stress at 5% Strain: {stress:.1f} MPa")
    print(f"   Predicted Wear Life: {adjusted_wear:.1f} Years (Material Strength Boost: {strength/100.0:.2f}x)")
    
    proof = {
        "chain_id": f"fashion-{int(time.time())}",
        "chem": {"ph": ph, "toxicity": toxicity},
        "polymer": {"alignment": alignment, "strength": strength},
        "apparel": {"strain": strain_event, "wear_life_years": adjusted_wear},
        "timestamp": time.time()
    }
    
    out_path = os.path.join(os.path.dirname(__file__), "..", "..", "artifacts", "ebm_tnn_runs", "demo_sustainable_fashion.json")
    with open(out_path, "w") as f:
        json.dump(proof, f, indent=2)
        
    print(f"\n✅ COHESION PROOF MINTED: {out_path}")

if __name__ == "__main__":
    run_sustainable_fashion()
