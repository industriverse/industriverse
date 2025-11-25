import asyncio
from typing import List, Dict, Any

from .mesh_node import ProofMeshNode
from .mesh_validator import ProofMeshValidator


class MeshGossip:
    """
    Minimal gossip stub for proof dissemination and validation.
    """

    def __init__(self, node_id: str):
        self.node = ProofMeshNode(node_id=node_id)
        self.validator = ProofMeshValidator()

    async def add_peer(self, peer_id: str):
        self.node.add_neighbor(peer_id)

    async def disseminate(self, proof: Dict[str, Any]) -> Dict[str, Any]:
        validated = await self.validator.validate(proof)
        await self.node.broadcast(validated)
        return validated
