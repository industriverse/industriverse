import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.sok.organism_kernel import SovereignOrganism
from src.sok.goal_homeostasis import GoalHomeostasis
from src.sok.autopoeisis_engine import AutopoeisisEngine
from src.overseer.overseer_stratiform import StrategicMode

def verify_overseer_autonomy():
    print("🧠 INITIALIZING OVERSEER STRATIFORM SIMULATION...")
    
    # 1. Birth
    organism = SovereignOrganism("Industriverse_Strategos")
    organism.drives = GoalHomeostasis()
    organism.immune_system = AutopoeisisEngine()
    
    print("\n--- Pulse 1: Normal Operation (PEACE) ---")
    organism.pulse()
    # Assert Peace
    if organism.overseer.current_mode != StrategicMode.PEACE:
        print("❌ Failed to start in PEACE mode")
        
    print("\n--- Pulse 2: Threat Detected (WAR) ---")
    # Inject War Narrative
    organism.narrative.world_state.global_tension = 0.9
    organism.narrative.ingest_signal("INTEL", 0.9, "Hostile Troop Movements")
    organism.pulse()
    
    # Assert War
    if organism.overseer.current_mode != StrategicMode.WAR:
        print(f"❌ Failed to shift to WAR. Current: {organism.overseer.current_mode}")
    else:
        print("✅ Successfully shifted to WAR Mode.")
        
    print("\n--- Pulse 3: Scientific Breakthrough (SINGULARITY) ---")
    # Inject Golden Age Narrative
    organism.narrative.world_state.global_tension = 0.1
    organism.narrative.world_state.scientific_consensus = 0.95
    organism.pulse()
    
    # Assert Singularity
    if organism.overseer.current_mode != StrategicMode.SINGULARITY:
        print(f"❌ Failed to shift to SINGULARITY. Current: {organism.overseer.current_mode}")
    else:
        print("✅ Successfully shifted to SINGULARITY Mode.")
        
    print("\n--- Pulse 4: Energy Crisis (HIBERNATION) ---")
    # Inject Safety Critical
    organism.state.energy = 4.0 # Below 5.0 threshold
    organism.pulse()
    
    # Assert Hibernation
    if organism.overseer.current_mode != StrategicMode.HIBERNATION:
        print(f"❌ Failed to shift to HIBERNATION. Current: {organism.overseer.current_mode}")
    else:
        print("✅ Successfully shifted to HIBERNATION Mode (Safety Override).")
        
    print("\n✅ Overseer Verification Complete.")

if __name__ == "__main__":
    verify_overseer_autonomy()
