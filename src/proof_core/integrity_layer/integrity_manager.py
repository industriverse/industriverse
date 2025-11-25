import uuid
import os
from typing import Any, Dict, Optional

from src.proof_core.proof_hub.proof_normalizer import ProofNormalizer
from src.proof_core.proof_hub.proof_repository import ProofRepository
from src.proof_core.proof_hub.sqlite_repository import SQLiteProofRepository
from src.proof_core.proof_hub.postgres_repository import PostgresProofRepository
from src.proof_core.proof_hub.unified_hub_adapter import UnifiedProofHubAdapter
from src.proof_core.proof_hub.proof_router import ProofRouter


def _build_repository():
    backend = os.environ.get("PROOF_BACKEND", "sqlite").lower()
    if backend == "sqlite":
        return SQLiteProofRepository()
    if backend == "postgres":
        try:
            return PostgresProofRepository()
        except Exception as e:
            import logging
            logging.warning(f"Postgres backend unavailable, falling back to SQLite: {e}")
            return SQLiteProofRepository()
    return ProofRepository()


_proof_repository = _build_repository()


class IntegrityManager:
    """
    Coordinates proof normalization and routing for the Integrity Loop.
    """

    def __init__(self):
        self.normalizer = ProofNormalizer()
        self.repository = _proof_repository
        self.router = ProofRouter(adapter=UnifiedProofHubAdapter())

    async def record_action(
        self,
        utid: str,
        domain: str,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        proof_id = uuid.uuid4().hex
        proof = self.normalizer.normalize(
            {
                "proof_id": proof_id,
                "utid": utid,
                "domain": domain,
                "inputs": inputs,
                "outputs": outputs,
                "metadata": metadata or {},
            }
        )
        self.repository.store(proof)
        return await self.router.route(proof)
