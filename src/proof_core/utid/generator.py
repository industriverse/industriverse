import hmac
import os
import time
import uuid
from hashlib import sha256
from typing import Any, Dict, Optional
import socket
import json


class UTIDGenerator:
    """
    Generates hardware- and context-bound UTIDs with an HMAC signature.

    This is a lightweight, production-ready starting point that can later
    incorporate hardware attestation (TPM, PUF) without changing callers.
    """

    def __init__(self, secret: Optional[str] = None):
        self.secret = (secret or os.environ.get("UTID_SECRET") or "dev-utid-secret").encode()
        self.host_id = self._host_fingerprint()
        self.attest_token = os.environ.get("UTID_ATTEST_TOKEN", "")

    def generate(self, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a UTID string with embedded signature.

        Format: UTID:REAL:{nonce}:{issued_at_ms}:{ctx_digest}:{sig}
        """
        nonce = uuid.uuid4().hex
        issued_at = int(time.time() * 1000)
        ctx_digest = self._context_digest(context) if context else "none"
        payload = f"{nonce}:{issued_at}:{ctx_digest}:{self.host_id}:{self.attest_token}"
        signature = hmac.new(self.secret, payload.encode(), sha256).hexdigest()[:16]
        return f"UTID:REAL:{nonce}:{issued_at}:{ctx_digest}:{signature}"

    def _context_digest(self, context: Dict[str, Any]) -> str:
        """
        Produce a deterministic, hashed context digest for privacy.
        """
        if not context:
            return "none"
        parts = []
        for key in sorted(context.keys()):
            parts.append(f"{key}={context[key]}")
        raw = "|".join(parts)
        return sha256(raw.encode()).hexdigest()[:12]

    def _host_fingerprint(self) -> str:
        host = socket.gethostname()
        mac = uuid.getnode()
        raw = f"{host}:{mac}"
        return sha256(raw.encode()).hexdigest()[:12]
