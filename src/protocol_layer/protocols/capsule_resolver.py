"""
Capsule resolver skeleton.

Responsibilities (per docs/capsule-uri-spec.md):
- Parse capsule:// URIs.
- Look up capsule metadata in local registry; fall back to mesh DNS.
- Verify UTID/Merkle proof and integrity.
- Execute in deterministic sandbox.
- Emit telemetry and credit ledger events.

This module provides a lightweight scaffold so engineers can wire in the
actual registry, mesh, sandbox, and ledger implementations.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from .capsule_uri import CapsuleURI, STATUS_CODES, parse_capsule_uri

logger = logging.getLogger(__name__)


@dataclass
class ResolutionResult:
    status: int
    message: str
    uri: CapsuleURI
    utid: Optional[str] = None
    payload_location: Optional[str] = None
    telemetry: Dict[str, Any] = field(default_factory=dict)


class CapsuleResolver:
    def __init__(self, registry=None, mesh_client=None, ledger=None, sandbox=None, emitter=None):
        """
        registry: interface exposing get_capsule(uri: CapsuleURI) -> metadata/payload
        mesh_client: interface exposing find_replica(uri: CapsuleURI) -> location/metadata
        ledger: credit ledger interface for UTID/credit recording
        sandbox: deterministic execution adapter
        emitter: telemetry emitter with emit(event) -> None
        """
        self.registry = registry
        self.mesh_client = mesh_client
        self.ledger = ledger
        self.sandbox = sandbox
        self.emitter = emitter
        self._cache: Dict[str, Dict] = {}

    def resolve(self, uri: str) -> ResolutionResult:
        try:
            parsed = parse_capsule_uri(uri)
        except ValueError as exc:
            return ResolutionResult(
                status=STATUS_CODES["BAD_URI"],
                message=str(exc),
                uri=CapsuleURI(authority="", domain="", subdomains=[], operation="", version=None, params={}),
            )

        metadata = self._cache.get(uri.strip())
        if self.registry:
            metadata = metadata or self.registry.get_capsule(parsed)
            if metadata:
                logger.debug("Resolved locally: %s", parsed)
                self._emit("capsule.status", {"uri": parsed.to_uri(), "utid": metadata.get("utid"), "status": "resolving", "resolution_source": "local"})

        if not metadata and self.mesh_client:
            metadata = self.mesh_client.find_replica(parsed)
            if metadata:
                logger.debug("Resolved via mesh: %s", parsed)
                self._emit("capsule.status", {"uri": parsed.to_uri(), "utid": metadata.get("utid"), "status": "resolving", "resolution_source": "mesh"})
                self._cache[parsed.to_uri()] = metadata

        if not metadata:
            return ResolutionResult(
                status=STATUS_CODES["NOT_FOUND"],
                message="Capsule not found in local registry or mesh",
                uri=parsed,
            )

        utid = metadata.get("utid")
        if self.ledger and utid:
            if not self.ledger.verify_utid(utid, metadata.get("credit_root")):
                return ResolutionResult(
                    status=STATUS_CODES["SIGNATURE_MISMATCH"],
                    message="UTID verification failed",
                    uri=parsed,
                )

        payload_location = metadata.get("location")
        telemetry = {"resolution_source": "local" if metadata.get("local") else "mesh"}

        # Placeholder execution path; implement sandbox wiring in infra layer.
        if not self.sandbox:
            return ResolutionResult(
                status=STATUS_CODES["NOT_IMPLEMENTED"],
                message="Sandbox executor not configured",
                uri=parsed,
                utid=utid,
                payload_location=payload_location,
                telemetry=telemetry,
            )

        try:
            exec_result = self.sandbox.run(metadata, parsed.params)
            telemetry.update(exec_result.telemetry if hasattr(exec_result, "telemetry") else {})
            if self.ledger and utid:
                self.ledger.append_execution(utid=utid, uri=parsed.to_uri(), telemetry=telemetry)
            self._emit("capsule.status", {"uri": parsed.to_uri(), "utid": utid, "status": "executed", "latency_ms": telemetry.get("latency_ms", 0), "resolution_source": telemetry.get("resolution_source", "")})
            if telemetry.get("proof_hash"):
                self._emit("capsule.proof", {"uri": parsed.to_uri(), "utid": utid, "proof_hash": telemetry["proof_hash"], "entropy_delta": telemetry.get("entropy_delta", 0), "timestamp": telemetry.get("timestamp", "")})
            if "execution_cost" in telemetry:
                self._emit(
                    "capsule.credit_flow",
                    {
                        "uri": parsed.to_uri(),
                        "utid": utid,
                        "execution_cost": telemetry.get("execution_cost", 0),
                        "author_split": telemetry.get("author_split", 0),
                        "executor_split": telemetry.get("executor_split", 0),
                        "mesh_split": telemetry.get("mesh_split", 0),
                        "balance_after": telemetry.get("balance_after", 0),
                    },
                )
            return ResolutionResult(
                status=STATUS_CODES["EXECUTED"],
                message="Executed",
                uri=parsed,
                utid=utid,
                payload_location=payload_location,
                telemetry=telemetry,
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Execution error for %s", uri)
            self._emit("capsule.status", {"uri": parsed.to_uri(), "utid": utid, "status": "error", "error": str(exc)})
            return ResolutionResult(
                status=STATUS_CODES["EXECUTION_ERROR"],
                message=str(exc),
                uri=parsed,
                utid=utid,
                payload_location=payload_location,
                telemetry=telemetry,
            )

    def _emit(self, topic: str, payload: dict) -> None:
        if self.emitter:
            try:
                self.emitter.emit({"topic": topic, "payload": payload})
            except Exception:  # noqa: BLE001
                logger.debug("Telemetry emit failed for topic %s", topic, exc_info=True)
