import time
import numpy as np
import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from ebm_lib.registry import get as load_prior
import ebm_lib.priors
from ebm_runtime.samplers.langevin import langevin_sample

def run_quantum_quality():
    print("👁️  STARTING COHESION DEMO: QUANTUM QUALITY EYE")
    print("==============================================")
    print("🔗 Linking: SENSORINT -> SURFACE -> QCTHERM")
    
    sensor_prior = load_prior("sensorint_v1")
    surface_prior = load_prior("surface_v1")
    qc_prior = load_prior("qctherm_v1")
    
    print("\n1️⃣  SENSOR FUSION: Lidar/Camera Alignment...")
    # State: [Lidar, Cam, Fused, Conf]
    # Simulate noisy inputs
    lidar_val = 1.05 # m
    cam_val = 0.95   # m
    sensor_state = {"state_vector": np.array([lidar_val, cam_val, 1.0, 0.5])}
    
    # EBM fuses the data
    sensor_res = langevin_sample(sensor_prior, sensor_state, {"steps": 20, "lr": 0.01, "noise": 0.001})
    final_sensor = sensor_res["final_state"]
    fused_dist = final_sensor[2]
    conf = final_sensor[3]
    
    print(f"   Lidar: {lidar_val}m | Cam: {cam_val}m -> Fused: {fused_dist:.3f}m (Conf: {conf:.2f})")
    
    print(f"\n2️⃣  SURFACE SCAN: Texture Entropy Analysis...")
    # State: [Ra, Entropy, Prob]
    # Simulate a rough surface (potential scratch)
    ra_val = 3.5 # High roughness
    surface_state = {"state_vector": np.array([ra_val, 0.0, 0.0])}
    
    # EBM predicts entropy and defect probability
    surface_res = langevin_sample(surface_prior, surface_state, {"steps": 20, "lr": 0.1, "noise": 0.0})
    final_surface = surface_res["final_state"]
    entropy = final_surface[1]
    prob = final_surface[2]
    
    print(f"   Roughness: {ra_val} -> Entropy: {entropy:.2f} bits | Defect Prob: {prob:.2f}")
    
    # Logic: If defect prob is high, trigger thermal scan
    trigger_thermal = False
    if prob > 0.8:
        trigger_thermal = True
        print("   ⚠️ High Defect Probability! Triggering Thermal Depth Scan...")
        
    print(f"\n3️⃣  THERMAL DEPTH: Internal Stress Correlation...")
    # State: [Gradient, Stress, Depth]
    # If triggered, we look for a shallow defect
    depth_init = 1.0
    if trigger_thermal:
        depth_init = 0.5 # Suspect shallow
        
    qc_state = {"state_vector": np.array([0.0, 0.0, depth_init])}
    
    # EBM correlates gradient to stress
    qc_res = langevin_sample(qc_prior, qc_state, {"steps": 20, "lr": 0.1, "noise": 0.1})
    final_qc = qc_res["final_state"]
    grad = final_qc[0]
    stress = final_qc[1]
    
    print(f"   Thermal Gradient: {grad:.1f} K/m | Internal Stress: {stress:.1f} MPa")
    
    proof = {
        "chain_id": f"quantum-quality-{int(time.time())}",
        "sensor": {"fused_dist": fused_dist, "conf": conf},
        "surface": {"entropy": entropy, "defect_prob": prob},
        "qc": {"stress": stress, "depth": final_qc[2]},
        "timestamp": time.time()
    }
    
    out_path = os.path.join(os.path.dirname(__file__), "..", "..", "artifacts", "ebm_tnn_runs", "demo_quantum_quality.json")
    with open(out_path, "w") as f:
        json.dump(proof, f, indent=2)
        
    print(f"\n✅ COHESION PROOF MINTED: {out_path}")

if __name__ == "__main__":
    run_quantum_quality()
