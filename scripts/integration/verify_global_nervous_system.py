import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.integration.sovereign_runtime import SovereignRuntime
from src.overseer.overseer_stratiform import StrategicMode

def verify_global_nervous_system():
    print("🌍 INITIALIZING GLOBAL NERVOUS SYSTEM SIMULATION...")
    
    runtime = SovereignRuntime("Industriverse_Omega")
    
    # 1. Morning: Peace
    print("\n--- 🌅 Phase 1: Morning (Peace) ---")
    runtime.run_cycle()
    if runtime.overseer.current_mode != StrategicMode.PEACE:
        print("❌ Failed to start in PEACE.")
        sys.exit(1)
        
    # 2. Noon: Crisis (War)
    print("\n--- ⚔️ Phase 2: Noon (Crisis) ---")
    signals = {
        "INTEL": {"value": 0.9, "desc": "Cyber-Physical Attack Detected"}
    }
    # Force tension up for simulation
    runtime.organism.narrative.world_state.global_tension = 0.9
    
    runtime.run_cycle(signals)
    
    if runtime.overseer.current_mode != StrategicMode.WAR:
        print(f"❌ Failed to shift to WAR. Current: {runtime.overseer.current_mode}")
        sys.exit(1)
    if "defense" not in runtime.institution.get_public_statement().lower():
        print("❌ Public statement did not reflect WAR.")
        sys.exit(1)
        
    # 3. Evening: Breakthrough (Singularity)
    print("\n--- 🚀 Phase 3: Evening (Singularity) ---")
    # Reset tension, boost science
    runtime.organism.narrative.world_state.global_tension = 0.1
    runtime.organism.narrative.world_state.scientific_consensus = 0.95
    
    runtime.run_cycle()
    
    if runtime.overseer.current_mode != StrategicMode.SINGULARITY:
        print(f"❌ Failed to shift to SINGULARITY. Current: {runtime.overseer.current_mode}")
        sys.exit(1)
        
    # Verify Auto-Publication happened (checked via logs in run_cycle, but we can check CFR)
    if not runtime.cfr.fossils:
        print("❌ No fossils recorded during Singularity.")
        sys.exit(1)
        
    print("\n✅ Global Nervous System Verification Complete. The Organism is Alive.")

if __name__ == "__main__":
    verify_global_nervous_system()
