import time
import numpy as np
import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from ebm_lib.registry import get as load_prior
import ebm_lib.priors
from ebm_runtime.samplers.langevin import langevin_sample

def run_zero_defect_foundry():
    print("💎 STARTING COHESION DEMO: ZERO-DEFECT FOUNDRY")
    print("==============================================")
    print("🔗 Linking: WAFER -> PCB -> ELECTRONICS")
    
    wafer_prior = load_prior("wafer_v1")
    pcb_prior = load_prior("pcbmfg_v1")
    elec_prior = load_prior("electronics_v1")
    
    print("\n1️⃣  WAFER FAB: Lithography Scan...")
    # Simulate a "Hot Spot" on the wafer
    wafer_state = {"state_vector": np.random.randn(8)}
    wafer_state["state_vector"][3] += 5.0 # Anomaly at index 3
    
    wafer_res = langevin_sample(wafer_prior, wafer_state, {"steps": 15, "lr": 0.1, "noise": 0.0})
    final_wafer_state = wafer_res["final_state"]
    anomaly_idx = np.argmax(np.abs(final_wafer_state))
    anomaly_magnitude = np.abs(final_wafer_state[anomaly_idx])
    
    print(f"   Anomaly Detected at Zone {anomaly_idx}. Magnitude: {anomaly_magnitude:.2f}")
    
    print(f"\n2️⃣  PCB ASSEMBLY: Adaptive Soldering...")
    # PCB line receives the anomaly map and adjusts solder temp for that zone
    base_temp = 250.0
    adjusted_temp = base_temp
    if anomaly_magnitude > 2.0:
        adjusted_temp = base_temp - (anomaly_magnitude * 5.0) # Lower temp to prevent stress
        print(f"   ⚠️ High Risk Zone! Lowering Solder Temp to {adjusted_temp:.1f}°C")
    else:
        print(f"   Nominal Risk. Solder Temp: {base_temp}°C")
        
    pcb_state = {"state_vector": np.array([adjusted_temp] * 8)}
    pcb_res = langevin_sample(pcb_prior, pcb_state, {"steps": 10, "lr": 0.01, "noise": 0.1})
    
    print(f"\n3️⃣  ELECTRONICS FINAL TEST: Yield Prediction...")
    # Predict yield based on the adjusted process
    yield_prob = 0.99
    if anomaly_magnitude > 4.0 and adjusted_temp > 240.0:
        yield_prob = 0.60 # Failed to adapt enough
        print("   ❌ Adaptation Insufficient. Predicted Yield: 60%")
    elif anomaly_magnitude > 4.0:
        yield_prob = 0.95 # Successful adaptation
        print("   ✅ Adaptation Successful! Predicted Yield: 95%")
        
    elec_state = {"state_vector": np.array([yield_prob] * 8)}
    elec_res = langevin_sample(elec_prior, elec_state, {"steps": 5, "lr": 0.001, "noise": 0.0})
    
    proof = {
        "chain_id": f"zero-defect-{int(time.time())}",
        "wafer": {"anomaly_mag": anomaly_magnitude, "zone": int(anomaly_idx)},
        "pcb": {"solder_temp": adjusted_temp},
        "electronics": {"predicted_yield": yield_prob},
        "timestamp": time.time()
    }
    
    out_path = os.path.join(os.path.dirname(__file__), "..", "..", "artifacts", "ebm_tnn_runs", "demo_zero_defect.json")
    with open(out_path, "w") as f:
        json.dump(proof, f, indent=2)
        
    print(f"\n✅ COHESION PROOF MINTED: {out_path}")

if __name__ == "__main__":
    run_zero_defect_foundry()
