"""
Mesh router stub that accepts capsule:// jobs and delegates to resolver.

In production, this would balance across nodes using latency/compute/credit signals.
"""

from __future__ import annotations

import logging
from typing import Dict

from .capsule_resolver import CapsuleResolver

logger = logging.getLogger(__name__)


class MeshRouter:
    def __init__(self, resolver: CapsuleResolver) -> None:
        self.resolver = resolver

    def handle_job(self, job: Dict) -> Dict:
        """
        job: {"uri": "capsule://...", "params": {...}}
        """
        uri = job.get("uri")
        if not uri:
            return {"status": 400, "message": "missing uri"}
        result = self.resolver.resolve(uri)
        return {"status": result.status, "message": result.message, "telemetry": result.telemetry}
