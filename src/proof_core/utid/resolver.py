import hmac
import os
from hashlib import sha256
from typing import Optional
import socket
import uuid
from src.proof_core.utid.hw_attestor import HardwareAttestor


class UTIDResolver:
    """
    Verifies UTID structure and signature.
    """

    def __init__(self, secret: Optional[str] = None):
        self.secret = (secret or os.environ.get("UTID_SECRET") or "dev-utid-secret").encode()
        self.host_id = self._host_fingerprint()
        self.attestor = HardwareAttestor()

    def verify(self, utid: str) -> bool:
        """
        Verify basic format and HMAC signature.
        """
        if not utid or not utid.startswith("UTID:REAL:"):
            return False
        parts = utid.split(":")
        if len(parts) != 7:
            return False
        _, _, nonce, issued_at, ctx_digest, signature, attest_sig = parts
        if not signature or len(signature) < 8:
            return False
        # host_id is included implicitly in signature calculation to bind UTID to machine
        attest_token = os.environ.get("UTID_ATTEST_TOKEN", "")
        payload = f"{nonce}:{issued_at}:{ctx_digest}:{self.host_id}:{attest_token}"
        expected = hmac.new(self.secret, payload.encode(), sha256).hexdigest()[:16]
        if not hmac.compare_digest(expected, signature):
            return False
        return self.attestor.verify(payload, attest_sig)

    def _host_fingerprint(self) -> str:
        host = socket.gethostname()
        mac = uuid.getnode()
        raw = f"{host}:{mac}"
        return sha256(raw.encode()).hexdigest()[:12]
