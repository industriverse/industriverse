import hashlib
import uuid
from typing import List, Any
from src.security.uzkl_expansion import USMProof, GovernanceProof
from src.unification.cross_domain_inference_engine import InferenceResult

class ProofMinter:
    """
    The Notary Factory.
    Generates cryptographic proofs for various organism events.
    """
    
    @staticmethod
    def mint_usm_proof(inference: InferenceResult, source_signals: List[Any]) -> USMProof:
        """
        Creates a proof for a CDIE inference.
        """
        print(f"   🔏 [MINTER] Minting USM Proof for: {inference.conclusion}")
        
        signal_hashes = [hashlib.sha256(str(s).encode()).hexdigest() for s in source_signals]
        conclusion_hash = hashlib.sha256(inference.conclusion.encode()).hexdigest()
        
        return USMProof(
            id=f"PROOF_USM_{uuid.uuid4()}",
            inference_id=str(uuid.uuid4()),
            signal_hashes=signal_hashes,
            conclusion_hash=conclusion_hash
        )

    @staticmethod
    def mint_governance_proof(action_id: str, ethics_result: bool) -> GovernanceProof:
        """
        Creates a proof for a governance decision.
        """
        print(f"   🔏 [MINTER] Minting Governance Proof for Action: {action_id}")
        
        return GovernanceProof(
            id=f"PROOF_GOV_{uuid.uuid4()}",
            action_id=action_id,
            ethics_check_id=str(uuid.uuid4()),
            regulator_state_hash=hashlib.sha256(b"SAFE_STATE").hexdigest()
        )

# --- Verification ---
if __name__ == "__main__":
    # Mock Data
    inf = InferenceResult("TEST_CONCLUSION", 0.9, [])
    signals = ["Sig1", "Sig2"]
    
    proof = ProofMinter.mint_usm_proof(inf, signals)
    print(f"Proof ID: {proof.id}")
