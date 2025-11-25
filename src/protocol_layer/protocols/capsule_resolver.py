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
import time
import os
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
    def resolve(self, uri_str: str) -> ResolutionResult:
        """
        Resolve a capsule URI to an executable payload.
        Phase 5 Update: Support for Sovereign Capsules (capsule://sovereign/...)
        """
        try:
            uri = parse_capsule_uri(uri_str)
        except ValueError as e:
            return ResolutionResult(
                status=STATUS_CODES["BAD_URI"], # Changed from INVALID_URI to BAD_URI as INVALID_URI is not defined
                message=str(e),
                uri=CapsuleURI(authority="", domain="", subdomains=[], operation="", version=None, params={}) # uri_str is a string, not CapsuleURI
            )

        # 1. Check Registry (for legacy/mock capsules)
        registry_entry = None
        if self.registry:
            registry_entry = self.registry.get_capsule(uri) # Pass CapsuleURI object

        # 2. Phase 5: Sovereign Capsule Resolution
        if uri.domain == "sovereign":
            # Map capsule://sovereign/<id>/v1 -> src/capsules/sovereign/<id>_v1
            # Example: capsule://sovereign/fusion/v1 -> src/capsules/sovereign/fusion_v1
            capsule_id = uri.operation.strip("/") # operation is the path part after domain
            version = uri.version or "v1"
            
            # Construct local path (assuming running from project root)
            # In production, this would be a dynamic loader or k8s lookup
            sovereign_dir = f"src/capsules/sovereign/{capsule_id}_{version}"
            
            if os.path.isdir(sovereign_dir):
                try:
                    # Dynamically load specific capsule class if needed, or use generic SovereignCapsule
                    # For now, we instantiate the base class which loads the manifest
                    capsule = SovereignCapsule(sovereign_dir)
                    
                    # Ignite (Directive 10)
                    capsule.ignite(uri.params)
                    
                    # Emit Telemetry (Directive 11)
                    self._emit("capsule.status", {"uri": uri.to_uri(), "status": "resolving", "resolution_source": "local"})
                    
                    return ResolutionResult(
                        status=STATUS_CODES["EXECUTED"], # Changed from SUCCESS to EXECUTED
                        message=f"Sovereign Capsule {capsule.capsule_id} ignited.",
                        uri=uri, # uri_str is a string, not CapsuleURI
                        utid=f"utid:{capsule_id}:{version}:sovereign", # Mock UTID for now
                        payload_location=sovereign_dir,
                        telemetry={"prin": capsule.manifest.prin.dict()}
                    )
                except Exception as e:
                    logger.exception("Failed to ignite sovereign capsule: %s", uri_str)
                    return ResolutionResult(
                        status=STATUS_CODES["EXECUTION_ERROR"],
                        message=f"Failed to ignite sovereign capsule: {e}",
                        uri=uri # uri_str is a string, not CapsuleURI
                    )

        if not registry_entry:
            # Fallback to Mesh (Phase 2)
            remote = None
            if self.mesh_client:
                remote = self.mesh_client.find_replica(uri) # Pass CapsuleURI object
            if remote:
                self._emit("capsule.status", {"uri": uri.to_uri(), "status": "resolving", "resolution_source": "mesh"})
                return ResolutionResult(
                    status=STATUS_CODES["RESOLVED"], # Changed from SUCCESS to RESOLVED
                    message="Resolved via Mesh",
                    uri=uri, # uri_str is a string, not CapsuleURI
                    payload_location=remote,
                    telemetry={"source": "mesh"}
                )
            
            return ResolutionResult(
                status=STATUS_CODES["NOT_FOUND"],
                message="Capsule not found in Registry or Mesh",
                uri=uri # uri_str is a string, not CapsuleURI
            )

        # 3. Verify UTID (Phase 2)
        utid = registry_entry.get("utid")
        if self.ledger and utid:
            if not self.ledger.verify_utid(utid, registry_entry.get("credit_root")):
                return ResolutionResult(
                    status=STATUS_CODES["SIGNATURE_MISMATCH"], # Changed from PERMISSION_DENIED to SIGNATURE_MISMATCH
                    message="UTID Verification Failed",
                    uri=uri # uri_str is a string, not CapsuleURI
                )

        # 4. Execute/Sandbox (Phase 1/2)
        # For now, just return success with metadata
        self._emit("capsule.status", {"uri": uri.to_uri(), "status": "resolving", "resolution_source": "local"})
        
        # Simulate execution delay
        time.sleep(0.1)
        
        telemetry = {"resolution_source": "local"}
        payload_location = registry_entry.get("location")

        if not self.sandbox:
            return ResolutionResult(
                status=STATUS_CODES["NOT_IMPLEMENTED"],
                message="Sandbox executor not configured",
                uri=uri,
                utid=utid,
                payload_location=payload_location,
                telemetry=telemetry,
            )

        try:
            exec_result = self.sandbox.run(registry_entry, uri.params)
            telemetry.update(exec_result.telemetry if hasattr(exec_result, "telemetry") else {})
            if self.ledger and utid:
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
