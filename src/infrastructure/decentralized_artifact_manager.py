from typing import Dict, List, Any
from src.infrastructure.ipfs_storage_node import IPFSStorageNode

class DecentralizedArtifactManager:
    """
    The Librarian of the Decentralized Web.
    Manages the pinning and retrieval of Truth Artifacts.
    """
    
    def __init__(self, ipfs_node: IPFSStorageNode):
        self.ipfs = ipfs_node
        self.my_artifacts: Dict[str, str] = {} # CID -> Description
        
    def pin_artifact(self, description: str, content: Any) -> str:
        """
        Stores an artifact on IPFS and tracks it.
        """
        print(f"   📦 [MANAGER] Pinning Artifact: '{description}'...")
        cid = self.ipfs.add(content)
        self.my_artifacts[cid] = description
        return cid
        
    def retrieve_artifact(self, cid: str) -> Any:
        """
        Fetches an artifact from IPFS.
        """
        print(f"   📥 [MANAGER] Retrieving CID: {cid}...")
        return self.ipfs.get(cid)
        
    def list_artifacts(self):
        print("\n   🗂️ [ARTIFACT INDEX]")
        for cid, desc in self.my_artifacts.items():
            print(f"     -> {cid[:10]}... : {desc}")

# --- Verification ---
if __name__ == "__main__":
    node = IPFSStorageNode()
    mgr = DecentralizedArtifactManager(node)
    cid = mgr.pin_artifact("Genesis Proof", {"id": 1, "data": "Genesis"})
    mgr.list_artifacts()
