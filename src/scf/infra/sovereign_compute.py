import os

class SovereignCompute:
    """
    Manages 'Sovereign Mode' (Air-Gapped / No-Cloud).
    """
    def __init__(self):
        self.sovereign_mode = False

    def enable_sovereign_mode(self):
        self.sovereign_mode = True
        os.environ["SOVEREIGN_MODE"] = "1"
        print("🛡️ SOVEREIGN MODE ENABLED. Cloud connections disabled.")

    def disable_sovereign_mode(self):
        self.sovereign_mode = False
        os.environ.pop("SOVEREIGN_MODE", None)
        print("🌐 Cloud connections re-enabled.")

    def is_sovereign(self) -> bool:
        return self.sovereign_mode or os.environ.get("SOVEREIGN_MODE") == "1"

    def check_connection_policy(self, destination: str) -> bool:
        """
        Returns True if connection is allowed.
        """
        if self.is_sovereign():
            # Block all external IPs/Domains
            if "localhost" in destination or "127.0.0.1" in destination:
                return True
            print(f"🚫 Blocked connection to {destination} (Sovereign Mode)")
            return False
        return True
