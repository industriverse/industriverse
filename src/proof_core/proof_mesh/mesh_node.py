from typing import Any, Dict, List


class ProofMeshNode:
    """
    Lightweight node representation for a future proof mesh.
    """

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.neighbors: List[str] = []

    def add_neighbor(self, neighbor: str) -> None:
        if neighbor not in self.neighbors:
            self.neighbors.append(neighbor)

    async def broadcast(self, proof: Dict[str, Any]) -> None:
        # In a real mesh this would send to neighbors; here we simply log intended broadcasts.
        proof["broadcasted_to"] = list(self.neighbors)
        return proof
