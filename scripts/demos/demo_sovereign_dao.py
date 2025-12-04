import sys
import os
from pathlib import Path
import time

# Add project root to path
sys.path.append(str(Path.cwd()))

from src.governance.sovereign_dao import SovereignDAO
from src.white_label.i3.shadow_twin_backend import get_shadow_twin

def demo_sovereign_dao():
    print("🏛️  Starting Sovereign DAO Demo...")
    print("===================================")
    
    # 1. Initialize DAO
    dao = SovereignDAO()
    
    # 2. Define a Service
    class ResearchAgent:
        def analyze(self, topic):
            print(f"   [Agent] Analyzing '{topic}'...")
            return "Analysis Complete"

    # 3. Commission the DAC (The "Birth" of a Sovereign Entity)
    print("\n--- Commissioning Process ---")
    dac = dao.commission_dac(ResearchAgent(), "Sovereign-Researcher-V1", price_per_call=0.50)
    
    # 4. Verify Identity
    print("\n--- Identity Verification ---")
    print(f"Name: {dac.name}")
    print(f"UTID: {dac.utid}")
    print(f"Proof: {dac.proof['proof_hash'][:16]}...")
    
    if dac.utid and dac.proof:
        print("✅ Identity Verified (UTID + Proof present).")
    else:
        print("❌ Identity Verification Failed.")
        return

    # 5. Verify Shadow Twin Presence
    print("\n--- Shadow Twin Verification ---")
    twin = get_shadow_twin()
    if dac.utid in twin.nodes:
        node = twin.nodes[dac.utid]
        print(f"✅ Found in Shadow Twin: {node.label} ({node.node_type})")
        print(f"   Status: {node.metadata.get('status')}")
    else:
        print("❌ Not found in Shadow Twin.")
        return

    # 6. Execute & Ledger Sign
    print("\n--- Execution & Ledger Signing ---")
    dac.analyze("Quantum Thermodynamics")
    
    # Check Ledger (Mock check, relying on console output from DAC)
    print("\n===================================")
    print("✅ Sovereign DAO Demo Complete.")

if __name__ == "__main__":
    demo_sovereign_dao()
