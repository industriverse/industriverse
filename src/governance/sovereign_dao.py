import sys
import os
import hashlib
import json
import time
from typing import Dict, Any, Optional

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.proof_core.utid.utid_registry import UTIDRegistry
from src.white_label.i3.shadow_twin_backend import get_shadow_twin, NodeType, EdgeType
from src.economics.dac_capsule import DACCapsule

class SovereignDAO:
    """
    The Sovereign Governance Orchestrator.
    Manages the lifecycle of Sovereign DACs:
    1. Minting UTIDs (Identity)
    2. Generating Genesis Proofs (Verifiability)
    3. Injecting into Shadow Twin (Presence)
    """
    def __init__(self):
        self.utid_registry = UTIDRegistry()
        self.shadow_twin = get_shadow_twin()
        print("🏛️  Sovereign DAO Online.")

    def commission_dac(self, service_instance, name: str, price_per_call: float = 0.01) -> DACCapsule:
        """
        Commissions a new Sovereign DAC.
        """
        print(f"\n📜 Commissioning Sovereign DAC: '{name}'...")
        
        # 1. Generate Genesis Proof (Mock ZK)
        genesis_proof = self._generate_genesis_proof(name, service_instance)
        print(f"   ✨ Genesis Proof Generated: {genesis_proof['proof_hash'][:16]}...")
        
        # 2. Mint UTID
        utid = self._mint_utid(name, genesis_proof)
        print(f"   🆔 UTID Minted: {utid}")
        
        # 3. Inject into Shadow Twin
        self._inject_into_twin(utid, name, "Active")
        print(f"   👻 Injected into Shadow Twin.")
        
        # 4. Instantiate Capsule with Sovereignty
        dac = DACCapsule(
            service_instance, 
            name=name, 
            price_per_call=price_per_call,
            utid=utid,
            proof=genesis_proof
        )
        
        return dac

    def _generate_genesis_proof(self, name: str, service) -> Dict[str, Any]:
        """
        Simulates generating a ZK-proof of the service's codebase/config.
        """
        # In reality, this would hash the bytecode and generate a ZK-SNARK
        payload = f"{name}:{str(service)}:{time.time()}"
        proof_hash = hashlib.sha256(payload.encode()).hexdigest()
        
        return {
            "proof_type": "zk-genesis-v1",
            "proof_hash": proof_hash,
            "timestamp": time.time(),
            "verifier": "SovereignDAO"
        }

    def _mint_utid(self, name: str, proof: Dict[str, Any]) -> str:
        """
        Mints a Universal Unique Token ID (UTID).
        """
        # Generate a deterministic but unique ID
        raw_id = f"{name}-{proof['proof_hash']}"
        utid = f"utid:dac:{hashlib.sha256(raw_id.encode()).hexdigest()[:16]}"
        
        # Register in Registry
        self.utid_registry.add(utid, proof['proof_hash'], {"name": name, "type": "DAC"})
        return utid

    def _inject_into_twin(self, utid: str, label: str, status: str):
        """
        Adds the DAC as a node in the Shadow Twin graph.
        """
        # Add Node
        self.shadow_twin.add_node(
            node_id=utid,
            node_type=NodeType.CONCEPT, # Using CONCEPT as proxy for Agent/DAC
            label=label,
            metadata={"status": status, "type": "SovereignDAC"}
        )
        
        # Link to DAO (Central Hub)
        dao_node_id = "node:SovereignDAO"
        if dao_node_id not in self.shadow_twin.nodes:
             self.shadow_twin.add_node(dao_node_id, NodeType.CLUSTER, "Sovereign DAO")
             
        self.shadow_twin.add_edge(dao_node_id, utid, EdgeType.CONTAINS)

if __name__ == "__main__":
    # Test
    class MockService:
        pass
    
    dao = SovereignDAO()
    dac = dao.commission_dac(MockService(), "Test-Bot-Alpha")
