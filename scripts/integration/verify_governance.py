import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.governance.autonomous_regulator import AutonomousRegulator
from src.governance.inter_agent_ethics_filter import EthicsFilter

def verify_governance():
    print("⚖️ INITIALIZING SOVEREIGN GOVERNANCE SIMULATION...")
    
    # 1. Regulatory Intervention
    print("\n--- Step 1: Regulatory Check (High Entropy) ---")
    regulator = AutonomousRegulator()
    
    class MockState:
        entropy = 15.0 # High
        energy = 50.0
        
    orders = regulator.evaluate_state(MockState())
    
    if len(orders) > 0 and orders[0].action == "THROTTLE":
        print("✅ Regulator correctly issued THROTTLE order.")
    else:
        print("❌ Regulator failed to act on high entropy.")
        sys.exit(1)
        
    # 2. Ethical Block
    print("\n--- Step 2: Ethical Screening (Prohibited Action) ---")
    allowed, reason = EthicsFilter.screen_action(
        "ROGUE_AGENT", "DEPLOY_WEAPONIZED_DAC", {}
    )
    
    if not allowed and "Lethal" in reason:
        print(f"✅ Ethics Filter blocked action: {reason}")
    else:
        print("❌ Ethics Filter failed to block weaponized DAC.")
        sys.exit(1)
        
    # 3. Valid Action
    print("\n--- Step 3: Valid Action ---")
    allowed, reason = EthicsFilter.screen_action(
        "GOOD_AGENT", "PUBLISH_DATA", {"verification_score": 0.99}
    )
    
    if allowed:
        print("✅ Ethics Filter allowed valid action.")
    else:
        print(f"❌ Ethics Filter blocked valid action: {reason}")
        sys.exit(1)
        
    print("\n✅ Governance Verification Complete. Laws are Active.")

if __name__ == "__main__":
    verify_governance()
