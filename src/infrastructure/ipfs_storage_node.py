import hashlib
import json
from typing import Dict, Any, Optional

class IPFSStorageNode:
    """
    A Mock Inter-Planetary File System (IPFS) Node.
    Provides content-addressable storage logic.
    """
    
    def __init__(self):
        self.storage: Dict[str, bytes] = {}
        print("   🌌 [IPFS] Node Initialized (Gateway: Localhost)")
        
    def add(self, content: Any) -> str:
        """
        Adds content to IPFS and returns the CID (Content Identifier).
        """
        # Serialize content
        if isinstance(content, dict) or isinstance(content, list):
            data_bytes = json.dumps(content, sort_keys=True).encode('utf-8')
        elif isinstance(content, str):
            data_bytes = content.encode('utf-8')
        else:
            data_bytes = str(content).encode('utf-8')
            
        # Generate CID (SHA-256 Hash)
        cid = "Qm" + hashlib.sha256(data_bytes).hexdigest()[:44]
        
        # Store
        self.storage[cid] = data_bytes
        print(f"     -> 📌 [PIN] Added Content. CID: {cid}")
        return cid
        
    def get(self, cid: str) -> Optional[Any]:
        """
        Retrieves content by CID.
        """
        if cid in self.storage:
            data_bytes = self.storage[cid]
            try:
                return json.loads(data_bytes.decode('utf-8'))
            except:
                return data_bytes.decode('utf-8')
        else:
            print(f"     -> ❌ [404] CID Not Found: {cid}")
            return None

# --- Verification ---
if __name__ == "__main__":
    node = IPFSStorageNode()
    cid = node.add({"proof": "valid", "value": 42})
    print(f"Retrieved: {node.get(cid)}")
