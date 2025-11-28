"""
Proof-of-Insight credit ledger with UTID utilities and Merkle proofs.

Production notes:
- Replace in-memory store with durable DB.
- Add signature over reconciliation payloads.
- Add replay protection and auth on append.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from threading import Lock
from typing import Dict, List, Optional, Tuple


def compute_utid(capsule_hash: str, parent_utid: Optional[str], credit_root: str) -> str:
    payload = f"{capsule_hash}|{parent_utid or ''}|{credit_root}".encode("utf-8")
    return hashlib.sha3_512(payload).hexdigest()


@dataclass
class LedgerEntry:
    utid: str
    uri: str
    delta_credits: float
    proof_hash: str
    credit_root: str
    timestamp: float


class CreditLedger:
    def __init__(self) -> None:
        self._entries: List[LedgerEntry] = []
        self._lock = Lock()
        self._seen_utids: set[str] = set()

    def append_execution(self, utid: str, uri: str, telemetry: Optional[Dict] = None) -> LedgerEntry:
        """
        Append execution record. Expects telemetry to carry execution_cost and credit_root.
        """
        proof_hash = (telemetry or {}).get("proof_hash", "")
        credit_root = (telemetry or {}).get("credit_root", "")
        delta_credits = float((telemetry or {}).get("execution_cost", 0.0))
        timestamp = float((telemetry or {}).get("timestamp_epoch", 0.0))
        entry = LedgerEntry(
            utid=utid,
            uri=uri,
            delta_credits=delta_credits,
            proof_hash=proof_hash,
            credit_root=credit_root,
            timestamp=timestamp,
        )
        with self._lock:
            if utid in self._seen_utids:
                raise ValueError(f"Duplicate UTID: {utid}")
            self._entries.append(entry)
            self._seen_utids.add(utid)
        return entry

    def verify_utid(self, utid: str, credit_root: Optional[str]) -> bool:
        return bool(utid) and credit_root is not None

    def merkle_root(self) -> str:
        """
        Compute Merkle root of UTID leaves.
        """
        with self._lock:
            leaves = [hashlib.sha3_512(e.utid.encode("utf-8")).digest() for e in self._entries]
        if not leaves:
            return ""
        return _build_merkle_root(leaves).hex()

    def merkle_proof(self, utid: str) -> Tuple[str, List[Tuple[str, str]]]:
        """
        Return root and proof path for a given utid.
        Proof path is list of (direction, sibling_hex) where direction in {"L","R"}.
        """
        with self._lock:
            leaves = [hashlib.sha3_512(e.utid.encode("utf-8")).digest() for e in self._entries]
        if not leaves:
            return "", []
        root, proof = _merkle_proof(leaves, hashlib.sha3_512(utid.encode("utf-8")).digest())
        return root.hex(), [(d, h.hex()) for d, h in proof]

    def verify_proof(self, utid: str, root_hex: str, proof: List[Tuple[str, str]]) -> bool:
        """
        Verify a Merkle proof path for the given utid against a root.
        """
        node = hashlib.sha3_512(utid.encode("utf-8")).digest()
        for direction, sibling_hex in proof:
            sibling = bytes.fromhex(sibling_hex)
            if direction == "R":
                node = hashlib.sha3_512(node + sibling).digest()
            elif direction == "L":
                node = hashlib.sha3_512(sibling + node).digest()
            else:
                return False
        return node.hex() == root_hex


def _build_merkle_root(leaves: List[bytes]) -> bytes:
    nodes = leaves
    while len(nodes) > 1:
        next_level: List[bytes] = []
        for i in range(0, len(nodes), 2):
            left = nodes[i]
            right = nodes[i + 1] if i + 1 < len(nodes) else left
            next_level.append(hashlib.sha3_512(left + right).digest())
        nodes = next_level
    return nodes[0]


def _merkle_proof(leaves: List[bytes], target: bytes) -> Tuple[bytes, List[Tuple[str, bytes]]]:
    """
    Construct Merkle proof path for target leaf.
    """
    if target not in leaves:
        return b"", []
    proof: List[Tuple[str, bytes]] = []
    level = leaves
    idx = level.index(target)
    while len(level) > 1:
        next_level: List[bytes] = []
        for i in range(0, len(level), 2):
            left = level[i]
            right = level[i + 1] if i + 1 < len(level) else left
            combined = hashlib.sha3_512(left + right).digest()
            next_level.append(combined)
            if i == idx or i + 1 == idx:
                if idx == i:
                    proof.append(("R", right))
                else:
                    proof.append(("L", left))
                idx = len(next_level) - 1
        level = next_level
    return level[0], proof
