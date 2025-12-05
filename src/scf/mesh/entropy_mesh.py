from dataclasses import dataclass
from typing import Dict, List
import time

@dataclass
class MeshNode:
    node_id: str
    node_type: str # 'EDGE', 'CLOUD', 'FACTORY'
    status: str
    last_heartbeat: float

class EntropyMesh:
    """
    Manages the cross-device mesh network.
    """
    def __init__(self):
        self.nodes: Dict[str, MeshNode] = {}

    def register_node(self, node_id: str, node_type: str):
        self.nodes[node_id] = MeshNode(
            node_id=node_id,
            node_type=node_type,
            status='ONLINE',
            last_heartbeat=time.time()
        )
        print(f"🕸️ Node Joined Mesh: {node_id} ({node_type})")

    def heartbeat(self, node_id: str):
        if node_id in self.nodes:
            self.nodes[node_id].last_heartbeat = time.time()
            self.nodes[node_id].status = 'ONLINE'

    def get_active_nodes(self) -> List[str]:
        # Simple check: active if heartbeat within last 60s
        now = time.time()
        active = []
        for node in self.nodes.values():
            if now - node.last_heartbeat < 60:
                active.append(node.node_id)
            else:
                node.status = 'OFFLINE'
        return active
