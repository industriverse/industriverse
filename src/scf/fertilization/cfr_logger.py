import time
from typing import Dict, Any
from src.datahub.value_vault import ValueVault
from src.research.research_controller import ResearchController
from src.anthropology.cognitive_fossil_record import FossilRecord, CognitiveFossil
from src.scf.fertilization.fossil_validator import FossilValidator

class CFRLogger:
    """
    The Scribe of the Sovereign Code Foundry.
    Records 'Code Fossils' into the Anthropological Layer (CFR).
    Also syncs high-value insights to the ValueVault.
    """
    def __init__(self):
        self.value_vault = ValueVault()
        self.research_controller = ResearchController()
        self.fossil_record = FossilRecord()
        self.validator = FossilValidator()
        print("📜 CFR Logger Initialized (Connected to Anthropological Layer)")

    def record(self, intent: str, code: str, review_result: Dict[str, Any]):
        """
        Logs the event as a Cognitive Fossil.
        """
        # 1. Create Fossil
        fossil = CognitiveFossil(
            description=f"SCF Generation: {intent}",
            creator_id="SOVEREIGN_CODE_FOUNDRY",
            content_hash=str(hash(code)),
            narrative_context="OPTIMIZATION_CYCLE", # Could be dynamic
            outcome="SUCCESS" if review_result.get("verdict") == "APPROVE" else "FAILURE"
        )
        
        # 2. Validate Fossil (Quality Control)
        # Construct a validation packet
        validation_packet = {
            "intent_id": str(hash(intent)),
            "context_slab_ref": "LATEST_CONTEXT", # Mock
            "negentropy_score": review_result.get("score", 0.0),
            "energy_trace_summary": {"joules_saved": 0.0}, # Mock
            "proof_id": "PENDING", # Mock
            "artifact_cid": f"ipfs://{str(hash(code))}", # Mock IPFS CID
            "verifier_result": review_result.get("verdict", "UNKNOWN")
        }
        
        is_valid, reason = self.validator.validate(validation_packet)
        if not is_valid:
            print(f"⚠️ [CFR] Fossil Validation Failed: {reason}. Marking as LOW_QUALITY.")
            fossil.metadata = {"quality": "LOW", "validation_error": reason}
        else:
            fossil.metadata = {"quality": "HIGH"}

        # 3. Preserve in Global History
        self.fossil_record.preserve_fossil(fossil)
        
        # 4. Store in Value Vault (if valuable)
        # We calculate a 'negentropy' score based on the review
        score = review_result.get("score", 0.5)
        if score > 0.7:
            insight = {
                "intent": intent,
                "code": code,
                "fossil_id": fossil.id,
                "thermodynamics": {
                    "negentropy_score": score
                }
            }
            self.value_vault.store_secret(insight)
            
            # 5. Trigger Research if Breakthrough
            if score > 0.9:
                packet = {
                    "source": "SOVEREIGN_CODE_FOUNDRY",
                    "energy_state": {
                        "entropy": 0.1 # Low entropy = high order/quality
                    },
                    "payload": {
                        "intent": intent,
                        "code_hash": str(hash(code)),
                        "confidence": score,
                        "safety_score": 1.0
                    }
                }
                self.research_controller.set_active(True)
                self.research_controller.analyze_packet(packet)
