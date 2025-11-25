from typing import Any, Dict


class ProofRouter:
    """
    Simple placeholder router that can be extended with policy-based routing.
    """

    def __init__(self, adapter):
        self.adapter = adapter

    async def route(self, proof: Dict[str, Any]) -> Dict[str, Any]:
        return await self.adapter.submit(proof)
