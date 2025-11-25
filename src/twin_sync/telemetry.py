"""
Telemetry event helpers for Shadow Twin (Phase 4).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class TelemetryEvent:
    topic: str
    payload: Dict[str, Any]


def capsule_status(uri: str, utid: str, status: str, latency_ms: float, resolution_source: str) -> TelemetryEvent:
    return TelemetryEvent(
        topic="capsule.status",
        payload={
            "uri": uri,
            "utid": utid,
            "status": status,
            "latency_ms": latency_ms,
            "resolution_source": resolution_source,
        },
    )


def capsule_proof(uri: str, utid: str, proof_hash: str, entropy_delta: float, timestamp: str) -> TelemetryEvent:
    return TelemetryEvent(
        topic="capsule.proof",
        payload={
            "uri": uri,
            "utid": utid,
            "proof_hash": proof_hash,
            "entropy_delta": entropy_delta,
            "timestamp": timestamp,
        },
    )


def capsule_credit_flow(
    uri: str,
    utid: str,
    execution_cost: float,
    author_split: float,
    executor_split: float,
    mesh_split: float,
    balance_after: float,
) -> TelemetryEvent:
    return TelemetryEvent(
        topic="capsule.credit_flow",
        payload={
            "uri": uri,
            "utid": utid,
            "execution_cost": execution_cost,
            "author_split": author_split,
            "executor_split": executor_split,
            "mesh_split": mesh_split,
            "balance_after": balance_after,
        },
    )
