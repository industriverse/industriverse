from typing import Dict, Any


def compute_proof_score(proof: Dict[str, Any]) -> float:
    """
    Compute a simple ProofScore based on presence of UTID, anchors, and energy metadata.
    """
    score = 0.3
    if proof.get("utid"):
        score += 0.2
    anchors = proof.get("metadata", {}).get("anchors", [])
    if anchors:
        score += 0.3
    if proof.get("metadata", {}).get("energy_joules") is not None:
        score += 0.1
    return min(score, 1.0)
