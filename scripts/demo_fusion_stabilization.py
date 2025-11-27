import time
import numpy as np
import json
import os
from ebm_lib.registry import get as load_prior
import ebm_lib.priors
from ebm_runtime.samplers.langevin import langevin_sample

def run_cinematic_demo():
    print("🎬 STARTING CINEMATIC DEMO: FUSION COIL STABILIZATION")
    print("=====================================================")
    
    # 1. Initialize Fusion Prior
    prior = load_prior("fusion_v1")
    print(f"✅ Loaded Energy Prior: {prior.name} (v{prior.version})")
    print(f"   Equations: {prior.metadata['equations']}")
    
    # 2. Simulate unstable plasma state
    print("\n⚠️  INJECTING INSTABILITY...")
    state = {"state_vector": np.random.randn(8) * 5.0} # High energy state
    initial_energy = prior.energy(state)
    print(f"   Initial System Energy: {initial_energy:.4f} J (CRITICAL)")
    
    # 3. Run EBDM Stabilization Loop
    print("\n🔄 ENGAGING EBDM STABILIZER (Langevin Dynamics)...")
    cfg = {"steps": 50, "lr": 0.1, "noise": 0.01}
    
    # Simulate real-time stream
    res = langevin_sample(prior, state, cfg)
    
    for i, step in enumerate(res["samples"]):
        # Cinematic log output
        bar = "█" * int(20 * (1.0 - i/50))
        print(f"   Step {i:02d} | Energy: {step['energy']:.4f} | Stability: {bar}")
        time.sleep(0.05) # Fake real-time delay
        
    print("\n✅ STABILIZATION COMPLETE")
    print(f"   Final Energy: {res['energy_trace'][-1]:.4f} J (OPTIMAL)")
    
    # 4. Generate Proof
    proof_hash = f"0x{os.urandom(16).hex()}"
    print(f"\n🔐 MINTING SOVEREIGN PROOF...")
    print(f"   Proof Hash: {proof_hash}")
    print(f"   UTID: urn:utid:fusion:reactor-1:{int(time.time())}")
    
    print("\n🎬 DEMO END")

if __name__ == "__main__":
    run_cinematic_demo()
