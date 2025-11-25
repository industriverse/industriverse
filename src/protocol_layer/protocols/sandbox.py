"""
Deterministic sandbox stub for resolver development.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict


@dataclass
class SandboxResult:
    telemetry: Dict


class DeterministicSandbox:
    def run(self, metadata: Dict, params: Dict) -> SandboxResult:
        # Simulate execution latency
        start = time.time()
        time.sleep(0.01)
        latency_ms = (time.time() - start) * 1000
        telemetry = {
            "latency_ms": latency_ms,
            "proof_hash": metadata.get("proof_hash", ""),
            "entropy_delta": metadata.get("entropy_delta", 0),
            "timestamp": metadata.get("timestamp", ""),
            "execution_cost": metadata.get("execution_cost", 0),
            "author_split": metadata.get("author_split", 0.7),
            "executor_split": metadata.get("executor_split", 0.2),
            "mesh_split": metadata.get("mesh_split", 0.1),
            "balance_after": metadata.get("balance_after", 0),
        }
        return SandboxResult(telemetry=telemetry)
