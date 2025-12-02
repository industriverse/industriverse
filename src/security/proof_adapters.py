from typing import Dict, Any
from src.security.uzkl_ledger import UnifiedZKLedger, ZKProof

class ProofAdapters:
    """
    Connects domain-specific systems to the Unified ZK Ledger.
    """
    
    def __init__(self, ledger: UnifiedZKLedger):
        self.ledger = ledger
        
    def prove_reality(self, anchor_data: Dict[str, Any]) -> ZKProof:
        """
        Generates a 'Proof of Reality' for mobile sensor data.
        """
        # anchor_data comes from src.mobile.advanced.reality_anchor
        return self.ledger.generate_proof(
            domain="REALITY",
            data=anchor_data,
            metadata={"sensor_count": len(anchor_data.get("sensors", []))}
        )

    def prove_influence(self, fingerprint_data: Dict[str, Any]) -> ZKProof:
        """
        Generates a 'Proof of Influence' for social physics.
        """
        # fingerprint_data comes from src.security.zk_influence_fingerprint
        return self.ledger.generate_proof(
            domain="SOCIAL",
            data=fingerprint_data,
            metadata={"bot_probability": fingerprint_data.get("bot_prob", 0.0)}
        )

    def prove_physics_law(self, capsule_data: Dict[str, Any]) -> ZKProof:
        """
        Generates a 'Proof of Law' for a LithOS Physics Capsule.
        """
        return self.ledger.generate_proof(
            domain="PHYSICS",
            data=capsule_data,
            metadata={"stability": capsule_data.get("stability", 0.0)}
        )

    def prove_compliance(self, audit_data: Dict[str, Any]) -> ZKProof:
        """
        Generates a 'Proof of Compliance' for regulatory reporting.
        """
        return self.ledger.generate_proof(
            domain="COMPLIANCE",
            data=audit_data,
            metadata={"regulation": "GDPR_AI_ACT"}
        )

# --- Verification ---
if __name__ == "__main__":
    ledger = UnifiedZKLedger()
    adapters = ProofAdapters(ledger)
    
    # Test Reality Proof
    reality_data = {"gps": "40.7128,-74.0060", "wifi_entropy": 0.85}
    adapters.prove_reality(reality_data)
    
    # Test Compliance Proof
    audit_data = {"user_consent": True, "data_retention": "30_days"}
    adapters.prove_compliance(audit_data)
