import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.infrastructure.ipfs_storage_node import IPFSStorageNode
from src.infrastructure.decentralized_artifact_manager import DecentralizedArtifactManager

def print_header(text):
    print(f"\n{'='*60}")
    print(f"   {text}")
    print(f"{'='*60}")

def demo_ipfs_integration():
    print_header("DEMO: INTER-PLANETARY FILE SYSTEM (IPFS) INTEGRATION")
    print("Scenario: Immutable Storage of Scientific Truth")
    
    # 1. Initialize Infrastructure
    node = IPFSStorageNode()
    mgr = DecentralizedArtifactManager(node)
    
    # 2. Generate Discovery
    print("\n>> STEP 1: Generating Scientific Discovery...")
    discovery_data = {
        "title": "Superconductor_Type_II",
        "formula": "H3S",
        "critical_temp_kelvin": 203,
        "author": "Agent_Curie"
    }
    print(f"   Data: {discovery_data}")
    
    # 3. Pin to IPFS
    print("\n>> STEP 2: Pinning to Decentralized Network...")
    cid = mgr.pin_artifact("Superconductor Discovery V1", discovery_data)
    print(f"   ✅ Content Pinned. CID: {cid}")
    
    # 4. Retrieval (Simulation of Peer Access)
    print("\n>> STEP 3: Peer Retrieval via CID...")
    retrieved_data = mgr.retrieve_artifact(cid)
    
    if retrieved_data == discovery_data:
        print("   ✅ Data Integrity Verified. Content Matches.")
    else:
        print("   ❌ Data Corruption Detected.")
        
    # 5. Immutability Demonstration
    print("\n>> STEP 4: Immutability Check...")
    print("   Attempting to modify data but keep same CID...")
    modified_data = discovery_data.copy()
    modified_data["critical_temp_kelvin"] = 999 # Fake data
    
    cid_modified = node.add(modified_data)
    print(f"   Original CID: {cid}")
    print(f"   Modified CID: {cid_modified}")
    
    if cid != cid_modified:
        print("   ✅ Immutability Confirmed. Different Content = Different CID.")
    else:
        print("   ❌ Immutability Failed.")
        
    print_header("DEMO COMPLETE: TRUTH IS IMMUTABLE")

if __name__ == "__main__":
    demo_ipfs_integration()
