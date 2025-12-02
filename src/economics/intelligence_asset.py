from dataclasses import dataclass
import time
import uuid

@dataclass
class IntelligenceAsset:
    """
    A cryptographic asset backed by verified intelligence (Proof or Fossil).
    """
    id: str
    owner_id: str # Sovereign Node ID
    asset_type: str # PROOF_OF_COMPLIANCE, DISCOVERY_LICENSE, INFLUENCE_FINGERPRINT
    backing_reference: str # ID of the ZK Proof or Fossil
    value_negentropy: float # Value in Negentropy Credits (J)
    timestamp: float = time.time()
    
    def transfer(self, new_owner_id: str):
        """
        Transfers ownership of the asset.
        """
        print(f"   💎 [ASSET] Transferring {self.id} ({self.asset_type})")
        print(f"     -> From: {self.owner_id}")
        print(f"     -> To:   {new_owner_id}")
        self.owner_id = new_owner_id

# --- Verification ---
if __name__ == "__main__":
    asset = IntelligenceAsset(
        id=str(uuid.uuid4()),
        owner_id="Node_A",
        asset_type="DISCOVERY_LICENSE",
        backing_reference="FOSSIL_123",
        value_negentropy=1000.0
    )
    asset.transfer("Node_B")
