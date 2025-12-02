import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.security.uzkl_ledger import UnifiedZKLedger
from src.security.proof_adapters import ProofAdapters

def verify_automated_compliance():
    print("🏛️ INITIALIZING AUTOMATED COMPLIANCE AUDIT (UZKL)...")
    
    ledger = UnifiedZKLedger()
    adapters = ProofAdapters(ledger)
    
    # 1. Reality Anchor (Mobile)
    print("\n--- Step 1: Proof of Reality ---")
    reality_data = {"device_id": "DEV_001", "entropy_signature": "SIG_XYZ"}
    reality_proof = adapters.prove_reality(reality_data)
    
    # 2. Influence Fingerprint (SPI)
    print("\n--- Step 2: Proof of Influence ---")
    influence_data = {"post_id": "POST_999", "bot_prob": 0.05, "origin": "ORGANIC"}
    influence_proof = adapters.prove_influence(influence_data)
    
    # 3. Physics Law (LithOS)
    print("\n--- Step 3: Proof of Physics ---")
    physics_data = {"formula": "E=mc^2", "stability": 0.999}
    physics_proof = adapters.prove_physics_law(physics_data)
    
    # 4. The Audit (Verification)
    print("\n--- Step 4: The Audit ---")
    print("   Auditor verifying proofs against Ledger...")
    
    valid_1 = ledger.verify_proof(reality_proof.id, reality_data)
    valid_2 = ledger.verify_proof(influence_proof.id, influence_data)
    valid_3 = ledger.verify_proof(physics_proof.id, physics_data)
    
    # 5. Tamper Test
    print("\n--- Step 5: Tamper Detection ---")
    fake_physics = {"formula": "E=mc^3", "stability": 0.999} # Modified Formula
    valid_4 = ledger.verify_proof(physics_proof.id, fake_physics)
    
    if valid_1 and valid_2 and valid_3 and not valid_4:
        print("\n✅ UZKL Verification Complete. Compliance Assured.")
    else:
        print("\n❌ UZKL Verification Failed.")
        sys.exit(1)

if __name__ == "__main__":
    verify_automated_compliance()
