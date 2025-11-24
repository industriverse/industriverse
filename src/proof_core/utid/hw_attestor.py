import hmac
import os
from hashlib import sha256
from typing import Optional


class HardwareAttestor:
    """
    Lightweight attestor stub. In production, this would integrate with TPM/PUF.
    """

    def __init__(self, secret: Optional[str] = None):
        self.secret = (secret or os.environ.get("UTID_ATTEST_SECRET") or "dev-attest-secret").encode()

    def sign(self, payload: str) -> str:
        return hmac.new(self.secret, payload.encode(), sha256).hexdigest()[:16]

    def verify(self, payload: str, signature: str) -> bool:
        expected = hmac.new(self.secret, payload.encode(), sha256).hexdigest()[:16]
        return hmac.compare_digest(expected, signature)
