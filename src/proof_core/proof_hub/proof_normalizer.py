from typing import Any, Dict


class ProofNormalizer:
    """
    Canonicalizes proof payloads so downstream components operate on a stable schema.
    """

    REQUIRED_FIELDS = ["proof_id", "utid", "domain", "inputs", "outputs"]

    def normalize(self, proof: Dict[str, Any]) -> Dict[str, Any]:
        normalized = {
            "proof_id": proof.get("proof_id"),
            "utid": proof.get("utid"),
            "domain": proof.get("domain", "general"),
            "inputs": proof.get("inputs", {}),
            "outputs": proof.get("outputs", {}),
            "metadata": proof.get("metadata", {}),
        }
        # Promote common fields
        for key in ["proof_hash", "status", "anchors"]:
            if key in proof:
                normalized["metadata"][key] = proof.get(key)
        # Promote common physics metadata if present
        if "energy_joules" in proof:
            normalized["metadata"]["energy_joules"] = proof.get("energy_joules")
        if "entropy" in proof:
            normalized["metadata"]["entropy"] = proof.get("entropy")
        return normalized
