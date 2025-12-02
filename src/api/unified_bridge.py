import json
from src.orchestration.daemon_gears import OrchestrationLevelManager, DaemonLevel
from src.science.lithos_kernel import LithOSKernel
from src.academy.certification_engine import CertificationEngine, UserProfile

class UnifiedBridge:
    """
    The Bridge between Backend Engines and Frontend UI.
    Exposes core logic as simple API methods.
    """
    
    def __init__(self):
        self.daemon = OrchestrationLevelManager()
        self.lithos = LithOSKernel()
        self.academy = CertificationEngine()
        # Mock User for Session
        self.current_user = UserProfile("USER_ADMIN", "ARCHITECT", ["ICDE", "ICCD"])

    # --- Daemon API ---
    def get_daemon_status(self):
        state = self.daemon.state
        return {
            "level": state.level.name,
            "features": state.active_features,
            "metrics": state.discovery_metrics
        }

    def set_daemon_level(self, level_name: str):
        try:
            level = DaemonLevel[level_name.upper()]
            self.daemon.set_level(level)
            return {"status": "SUCCESS", "new_level": level.name}
        except KeyError:
            return {"status": "ERROR", "message": "Invalid Level"}

    # --- LithOS API ---
    def get_universe_snapshot(self):
        # Mocking a snapshot from the Kernel
        return {
            "universe_id": "UNI_ALPHA",
            "stability": "STABLE",
            "capsules": [
                {"id": "CAP_01", "state": "0.99"},
                {"id": "CAP_02", "state": "0.45"}
            ]
        }

    # --- Academy API ---
    def get_user_profile(self):
        return {
            "user_id": self.current_user.user_id,
            "tier": self.current_user.avatar_tier,
            "certs": self.current_user.completed_certs
        }

# --- Verification ---
if __name__ == "__main__":
    bridge = UnifiedBridge()
    
    print("🌉 Testing Unified Bridge...")
    print(f"Daemon: {bridge.get_daemon_status()['level']}")
    
    print("⚙️ Shifting to SINGULARITY...")
    bridge.set_daemon_level("SINGULARITY")
    print(f"Daemon: {bridge.get_daemon_status()['level']}")
    
    print(f"Profile: {bridge.get_user_profile()['tier']}")
