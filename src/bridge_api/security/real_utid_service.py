import os
from typing import Any, Dict, Optional

from src.proof_core.utid.generator import UTIDGenerator
from src.proof_core.utid.resolver import UTIDResolver
from src.proof_core.utid.utid_registry import UTIDRegistry


class RealUTIDService:
    """
    Lightweight UTID service that signs and verifies UTIDs.

    This is intended as a drop-in for stricter, hardware-backed UTID implementations.
    """

    def __init__(self, secret: Optional[str] = None):
        secret = secret or os.environ.get("UTID_SECRET")
        self.generator = UTIDGenerator(secret=secret)
        self.resolver = UTIDResolver(secret=secret)
        self.registry = UTIDRegistry()

    def issue(self, context: Optional[Dict[str, Any]] = None) -> str:
        utid = self.generator.generate(context=context)
        ctx_digest = utid.split(":")[4] if utid else "none"
        self.registry.add(utid=utid, context_digest=ctx_digest, context=context)
        return utid

    def verify(self, utid: str) -> bool:
        return self.resolver.verify(utid)
