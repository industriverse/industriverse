import sys
import os
import uuid
import hashlib
import json
from typing import Dict, Any, Optional

# Attempt to import from security layer, else use mock
try:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
    from src.security_compliance_layer.core.zk_attestation.zk_attestation_service import ProofGenerator
    ZK_AVAILABLE = True
except ImportError:
    ZK_AVAILABLE = False
    print("Warning: ZK Attestation Service not found. Using internal mock.")

class ProofClient:
    """
    Client for generating Zero-Knowledge Proofs for loaded models.
    Integrates with the Security & Compliance Layer's ProofGenerator.
    """
    def __init__(self):
        if ZK_AVAILABLE:
            self.generator = ProofGenerator()
        else:
            self.generator = None

    async def generate_proof(self, model_hash: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a ZK proof attesting to the integrity of the loaded model.
        """
        claim_data = {
            "model_hash": model_hash,
            "context_hash": self._hash_context(context),
            "timestamp": context.get("timestamp", 0)
        }

        if self.generator:
            # Use real (mocked) generator from security layer
            result = self.generator.generate_proof(
                subject_id=f"loader-{uuid.uuid4()}",
                claim_type="model_integrity",
                claim_data=claim_data,
                proof_scheme="groth16"
            )
            if result["success"]:
                return result["proof"]
            else:
                print(f"Proof generation failed: {result.get('error')}")
                return self._mock_proof(model_hash)
        else:
            return self._mock_proof(model_hash)

    def _hash_context(self, context: Dict[str, Any]) -> str:
        return hashlib.sha256(json.dumps(context, sort_keys=True, default=str).encode()).hexdigest()

    def _mock_proof(self, model_hash: str) -> Dict[str, Any]:
        return {
            "id": str(uuid.uuid4()),
            "type": "mock_groth16",
            "public_inputs": [model_hash],
            "proof": "0xMOCK_PROOF_DATA"
        }
