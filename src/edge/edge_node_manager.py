from dataclasses import dataclass, field
from typing import Dict, List, Optional
import time
import uuid

@dataclass
class EdgeNode:
    id: str
    hostname: str
    arch: str # arm64, amd64
    status: str # ONLINE, OFFLINE, BUSY
    resources: Dict[str, float] # cpu_cores, ram_gb
    last_heartbeat: float

class EdgeNodeManager:
    """
    The K3s Fleet Commander.
    Manages lightweight edge nodes.
    """
    
    def __init__(self):
        self.nodes: Dict[str, EdgeNode] = {}
        print("   🕸️ [K3S] Edge Manager Initialized.")
        
    def register_node(self, hostname: str, arch: str, cpu: int, ram: int) -> str:
        node = EdgeNode(
            id=str(uuid.uuid4()),
            hostname=hostname,
            arch=arch,
            status="ONLINE",
            resources={"cpu": cpu, "ram": ram},
            last_heartbeat=time.time()
        )
        self.nodes[node.id] = node
        print(f"     -> Registered Node: {hostname} ({arch})")
        return node.id
        
    def deploy_pod(self, image: str, node_id: str):
        """
        Deploys a container to a specific node.
        """
        if node_id in self.nodes:
            node = self.nodes[node_id]
            if node.status == "ONLINE":
                print(f"     -> 🚀 [DEPLOY] Pod '{image}' -> {node.hostname}")
                node.status = "BUSY"
            else:
                print(f"     -> ❌ Node {node.hostname} is {node.status}")
        else:
            print(f"     -> ❌ Node ID {node_id} not found.")

    def release_node(self, node_id: str):
        """
        Simulates a node finishing its task.
        """
        if node_id in self.nodes:
            self.nodes[node_id].status = "ONLINE"
            print(f"     -> ✅ Node {self.nodes[node_id].hostname} is now ONLINE.")
            
    def check_health(self):
        print("\n   🏥 [HEALTH CHECK]")
        for node in self.nodes.values():
            age = time.time() - node.last_heartbeat
            status = "ONLINE" if age < 60 else "OFFLINE"
            print(f"     -> {node.hostname}: {status} (Last seen {age:.1f}s ago)")

# --- Verification ---
if __name__ == "__main__":
    mgr = EdgeNodeManager()
    nid = mgr.register_node("pi-cluster-01", "arm64", 4, 8)
    mgr.deploy_pod("nginx:alpine", nid)
    mgr.check_health()
