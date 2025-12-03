import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger("FossilValidator")

class FossilValidator:
    """
    The Gatekeeper of the Fossil Record.
    Ensures only high-quality, rich-metadata fossils enter the training lake.
    """
    def __init__(self):
        self.required_fields = [
            "intent_id", 
            "context_slab_ref", 
            "negentropy_score", 
            "energy_trace_summary",
            "artifact_cid",
            "verifier_result"
        ]

    def validate(self, fossil: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validates a fossil against the 'Sovereign Schema'.
        Returns (is_valid, reason).
        """
        # 1. Check Required Fields
        for field in self.required_fields:
            if field not in fossil:
                return False, f"Missing required field: {field}"

        # 2. Check Negentropy (Must be > 0)
        negentropy = fossil.get("negentropy_score", 0.0)
        if negentropy <= 0.0:
            # Fallback check: Did we at least calculate a Joule delta?
            joules_saved = fossil.get("energy_trace_summary", {}).get("joules_saved", 0.0)
            if joules_saved <= 0.0:
                return False, "Zero Negentropy & Zero Joule Savings (Low Value)"

        # 3. Check Provenance (UZKL Proof)
        if "proof_id" not in fossil:
             return False, "Missing UZKL Proof ID (Unverified)"

        return True, "Valid"
