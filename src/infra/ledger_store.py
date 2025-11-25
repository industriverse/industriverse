"""
Postgres-backed ledger store (skeleton).

Production:
- Use parameterized queries and connection pooling.
- Add migrations for tables:
  ledger_entries(utid PRIMARY KEY, uri, delta_credits, proof_hash, credit_root, timestamp)
- Add indexes on timestamp, credit_root.
"""

from __future__ import annotations

import logging
from typing import Dict, Optional

from .db import PostgresClient

logger = logging.getLogger(__name__)


class LedgerStore:
    def __init__(self, pg: PostgresClient):
        self.pg = pg

    def append(self, entry: Dict) -> None:
        """
        Persist ledger entry. Placeholder: wire to psycopg execute.
        """
        logger.info("Persisting ledger entry utid=%s (stub)", entry.get("utid"))

    def fetch(self, utid: str) -> Optional[Dict]:
        logger.info("Fetching ledger entry utid=%s (stub)", utid)
        return None
