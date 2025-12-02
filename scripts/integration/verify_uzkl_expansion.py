import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.security.proof_minter import ProofMinter
from src.unification.cross_domain_inference_engine import InferenceResult

def verify_uzkl_expansion():
    print("🔐 INITIALIZING UZKL EXPANSION SIMULATION...")
    
    # 1. Generate Insight
    print("\n--- Step 1: Generating Insight ---")
    signals = ["Signal_Security_High", "Signal_Thermal_High"]
    inference = InferenceResult("CYBER_PHYSICAL_ATTACK", 0.99, [])
    
    # 2. Mint Proof
    print("\n--- Step 2: Minting Proof ---")
    proof = ProofMinter.mint_usm_proof(inference, signals)
    print(f"   Proof ID: {proof.id}")
    
    # 3. Verify (Success)
    print("\n--- Step 3: Verifying (Valid Data) ---")
    is_valid = proof.verify(signals, "CYBER_PHYSICAL_ATTACK")
    
    if is_valid:
        print("✅ Proof Verified Successfully.")
    else:
        print("❌ Proof Verification Failed (Expected Success).")
        sys.exit(1)
        
    # 4. Verify (Tampered)
    print("\n--- Step 4: Verifying (Tampered Data) ---")
    tampered_signals = ["Signal_Security_LOW", "Signal_Thermal_High"] # Modified
    is_valid_tampered = proof.verify(tampered_signals, "CYBER_PHYSICAL_ATTACK")
    
    if not is_valid_tampered:
        print("✅ Tamper Detection Successful.")
    else:
        print("❌ Tamper Detection Failed (Proof accepted invalid data).")
        sys.exit(1)
        
    print("\n✅ UZKL Expansion Verification Complete. Truth is Secured.")

if __name__ == "__main__":
    verify_uzkl_expansion()
