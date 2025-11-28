"""
Consensus service skeleton for Merkle root signing/finalization.

Replace signature stubs with real Ed25519/BLS implementations and secure key storage.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class ConsensusService:
    def __init__(self, trusted_pubkeys: Dict[str, str], quorum: int):
        self.trusted_pubkeys = trusted_pubkeys
        self.quorum = quorum

    def sign_root(self, merkle_root_hex: str, private_key: str) -> str:
        """
        Placeholder: replace with real signature (Ed25519/BLS).
        """
        payload = (merkle_root_hex + private_key).encode("utf-8")
        return hashlib.sha3_256(payload).hexdigest()

    def verify_signature(self, merkle_root_hex: str, signature_hex: str, node_id: str) -> bool:
        """
        Placeholder verification: replace with real crypto.
        """
        pubkey = self.trusted_pubkeys.get(node_id)
        if not pubkey:
            return False
        expected = hashlib.sha3_256((merkle_root_hex + pubkey).encode("utf-8")).hexdigest()
        return expected == signature_hex

    def finalize(self, merkle_root_hex: str, signatures: List[Dict[str, str]]) -> bool:
        valid = [s for s in signatures if self.verify_signature(merkle_root_hex, s["signature"], s["node_id"])]
        if len(valid) >= self.quorum:
            logger.info("Merkle root finalized with %d signatures", len(valid))
            return True
        logger.warning("Not enough valid signatures: %d/%d", len(valid), self.quorum)
        return False
