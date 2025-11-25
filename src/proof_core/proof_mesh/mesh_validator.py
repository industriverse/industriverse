from typing import Any, Dict, List
import hashlib


class ProofMeshValidator:
    """
    Mesh-level validation logic.
    Computes a deterministic hash of proofs and assigns a simple ProofScore.
    """

    async def validate(self, proof: Dict[str, Any]) -> Dict[str, Any]:
        payload = str(proof).encode()
        validation_hash = hashlib.sha256(payload).hexdigest()
        score = self._compute_score(proof)
        return {"status": "validated", "proof_id": proof.get("proof_id"), "proof_hash": validation_hash, "proof_score": score}

    def _compute_score(self, proof: Dict[str, Any]) -> float:
        base = 0.5
        meta = proof.get("metadata", {})
        if proof.get("utid"):
            base += 0.2
        if meta.get("anchors"):
            base += 0.2
        if meta.get("proof_hash"):
            base += 0.05
        return min(base, 1.0)
