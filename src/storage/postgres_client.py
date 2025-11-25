"""
Async Postgres client using asyncpg.

Intended to replace infra stubs for production/non-mock use.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional

import asyncpg


class PostgresClient:
    def __init__(self, dsn: str, min_size: int = 1, max_size: int = 10):
        self._dsn = dsn
        self._pool: Optional[asyncpg.Pool] = None
        self._min_size = min_size
        self._max_size = max_size

    async def init(self) -> None:
        self._pool = await asyncpg.create_pool(dsn=self._dsn, min_size=self._min_size, max_size=self._max_size)

    async def close(self) -> None:
        if self._pool:
            await self._pool.close()

    async def insert_proof(self, utid: str, proof_hash: str, payload: Dict[str, Any]) -> None:
        if not self._pool:
            raise RuntimeError("PostgresClient not initialized")
        async with self._pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO proofs(utid, proof_hash, payload) VALUES($1, $2, $3) ON CONFLICT (proof_hash) DO NOTHING",
                utid,
                proof_hash,
                payload,
            )

    async def insert_ledger_entry(self, entry: Dict[str, Any]) -> None:
        if not self._pool:
            raise RuntimeError("PostgresClient not initialized")
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO ledger_entries(utid, uri, delta_credits, proof_hash, credit_root, ts)
                VALUES($1,$2,$3,$4,$5, now())
                ON CONFLICT (utid) DO NOTHING
                """,
                entry["utid"],
                entry["uri"],
                entry["delta_credits"],
                entry.get("proof_hash", ""),
                entry.get("credit_root", ""),
            )
