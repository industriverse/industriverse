import hashlib
import time
import socket
import secrets
from datetime import datetime

class UTIDGenerator:
    """
    Universal Traceable ID (UTID) Generator.
    Format: UTID:REAL:<host_short>:<capsule_short>:<YYYYMMDDHHMMSS>:<nonce_hex>
    """
    
    def __init__(self, host_secret: str = "dev_secret"):
        self.host_id = self._derive_host_id(host_secret)

    def _derive_host_id(self, secret: str) -> str:
        hostname = socket.gethostname()
        raw = f"{hostname}:{secret}"
        return hashlib.sha256(raw.encode()).hexdigest()[:6]

    def generate(self, capsule_id: str) -> str:
        """
        Generate a new UTID for a given capsule.
        """
        # Extract short capsule name (e.g., capsule:rawmat:v1 -> rawmat)
        try:
            capsule_short = capsule_id.split(":")[1]
        except IndexError:
            capsule_short = "unknown"
            
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        nonce = secrets.token_hex(4) # 8 chars
        
        return f"UTID:REAL:{self.host_id}:{capsule_short}:{timestamp}:{nonce}"

    @staticmethod
    def verify_format(utid: str) -> bool:
        parts = utid.split(":")
        return len(parts) == 6 and parts[0] == "UTID" and parts[1] == "REAL"
