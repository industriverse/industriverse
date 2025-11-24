import hmac
import os
from hashlib import sha256
from typing import Optional


class HardwareAttestor:
    """
    Lightweight attestor. Uses HMAC over a keyfile or env secret.
    In production, integrate with TPM/PUF secure key storage.
    """

    def __init__(self, secret: Optional[str] = None, key_path: Optional[str] = None):
        key_path = key_path or os.environ.get("UTID_ATTEST_KEY_PATH")
        if key_path and os.path.exists(key_path):
            with open(key_path, "rb") as f:
                key = f.read().strip()
        else:
            key = (secret or os.environ.get("UTID_ATTEST_SECRET") or "dev-attest-secret").encode()
        self.secret = key

    def sign(self, payload: str) -> str:
        return hmac.new(self.secret, payload.encode(), sha256).hexdigest()[:16]

    def verify(self, payload: str, signature: str) -> bool:
        expected = hmac.new(self.secret, payload.encode(), sha256).hexdigest()[:16]
        return hmac.compare_digest(expected, signature)
