import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.overseer.overseer_stratiform_v2 import OverseerStratiformV2
from src.unification.unified_substrate_model import USMField, USMSignal, USMEntropy
from src.coherence.iacp_v2 import IACPIntent

def verify_overseer_v2():
    print("🧠 INITIALIZING OVERSEER V2 SIMULATION...")
    
    overseer = OverseerStratiformV2()
    
    # 1. Simulate Attack Scenario
    print("\n--- Step 1: Simulating Attack Input ---")
    sec_field = USMField("SECURITY")
    sec_field.add_signal(USMSignal(entropy=USMEntropy(0.95, "SECURITY")))
    
    therm_field = USMField("THERMAL")
    therm_field.add_signal(USMSignal(entropy=USMEntropy(0.90, "THERMAL")))
    
    fields = {"SECURITY": sec_field, "THERMAL": therm_field}
    
    # 2. Run Cycle
    print("\n--- Step 2: Running Overseer Cycle ---")
    commands = overseer.run_cycle(fields)
    
    # 3. Verify Output
    print("\n--- Step 3: Verifying Commands ---")
    lockdown_issued = False
    for cmd in commands:
        if cmd.intent == IACPIntent.ISSUE_WARNING and cmd.payload.get("action") == "INITIATE_LOCKDOWN":
            lockdown_issued = True
            print(f"✅ Correctly issued LOCKDOWN command (Urgency: {cmd.context.urgency})")
            
    if not lockdown_issued:
        print("❌ Failed to issue lockdown.")
        sys.exit(1)
        
    print("\n✅ Overseer V2 Verification Complete. The Organism is Conscious.")

if __name__ == "__main__":
    verify_overseer_v2()
