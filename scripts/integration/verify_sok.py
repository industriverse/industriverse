import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.sok.organism_kernel import SovereignOrganism
from src.sok.goal_homeostasis import GoalHomeostasis
from src.sok.autopoeisis_engine import AutopoeisisEngine

def verify_sok_lifecycle():
    print("🧬 INITIALIZING SOVEREIGN ORGANISM KERNEL...")
    
    # 1. Birth
    organism = SovereignOrganism("Industriverse_Genesis")
    organism.drives = GoalHomeostasis()
    organism.immune_system = AutopoeisisEngine()
    
    print(f"   Born: {organism.name}")
    
    # 2. Life Cycle (5 Pulses)
    print("\n🌱 STARTING LIFE CYCLE...")
    for i in range(5):
        organism.pulse()
        
        # Simulate Stress on Pulse 3
        if i == 2:
            print("\n   ⚠️ SIMULATING DAMAGE & HIGH ENTROPY...")
            organism.state.health = 0.6
            organism.state.energy = 15.0 # Low Energy
            organism.state.entropy = 0.8 # High Entropy (Triggers Inference?)
            
    # 3. Final Status
    status = organism.get_status()
    print(f"\n🏁 FINAL STATUS: {status}")
    
    # Assertions
    if status['age'] != 5:
        print("❌ Age Mismatch")
        sys.exit(1)
    if status['vitality'] < 0.6: # Should have repaired some
        print("❌ Autopoeisis Failed")
        sys.exit(1)
        
    print("✅ SOK Verification Passed.")

if __name__ == "__main__":
    verify_sok_lifecycle()
