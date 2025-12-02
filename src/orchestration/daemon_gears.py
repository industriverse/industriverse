from enum import Enum
from dataclasses import dataclass
import time

class DaemonLevel(Enum):
    PEACE = 1
    VIGILANCE = 2
    EXPANSION = 3
    WAR = 4 # Code Red

@dataclass
class DaemonState:
    level: DaemonLevel
    active_features: list
    resource_allocation: dict # CPU/RAM split

class OrchestrationLevelManager:
    """
    The Gear Shifter. Manages the Daemon's operational level.
    """
    
    def __init__(self):
        self.current_level = DaemonLevel.PEACE
        self.state = self._get_peace_state()
        
    def set_level(self, level: DaemonLevel):
        """
        Shifts the Daemon to a new level.
        """
        print(f"⚙️ SHIFTING GEARS: {self.current_level.name} -> {level.name}")
        self.current_level = level
        
        if level == DaemonLevel.PEACE:
            self.state = self._get_peace_state()
        elif level == DaemonLevel.VIGILANCE:
            self.state = self._get_vigilance_state()
        elif level == DaemonLevel.EXPANSION:
            self.state = self._get_expansion_state()
        elif level == DaemonLevel.WAR:
            self.state = self._get_war_state()
            self._activate_code_red()
            
        return self.state

    def _get_peace_state(self):
        return DaemonState(
            level=DaemonLevel.PEACE,
            active_features=["StandardDiscovery", "BasicSCDS"],
            resource_allocation={"Discovery": 0.4, "Optimization": 0.4, "Reserve": 0.2}
        )

    def _get_vigilance_state(self):
        return DaemonState(
            level=DaemonLevel.VIGILANCE,
            active_features=["DeepSCDS", "SentimentAnalysis", "TrustScoring"],
            resource_allocation={"Security": 0.6, "Discovery": 0.2, "Reserve": 0.2}
        )

    def _get_expansion_state(self):
        return DaemonState(
            level=DaemonLevel.EXPANSION,
            active_features=["AggressiveDAC", "RCOExtraction", "MarketMaker"],
            resource_allocation={"Growth": 0.7, "Security": 0.2, "Reserve": 0.1}
        )

    def _get_war_state(self):
        return DaemonState(
            level=DaemonLevel.WAR,
            active_features=[
                "ScorchedEarth", "WarDAC", "OffensiveSPI", "ThermalOverride",
                "SovereignLockdown", "LiquidityDrain", "HyperLoop", "PhoenixProtocol"
            ],
            resource_allocation={"WAR": 1.0, "Reserve": 0.0}
        )

    def _activate_code_red(self):
        print("🚨 CODE RED ACTIVATED 🚨")
        print("   - Engaging Scorched Earth Protocols...")
        print("   - Unlocking Safety Limits...")
        print("   - Spawning War DACs...")

# --- Verification ---
if __name__ == "__main__":
    manager = OrchestrationLevelManager()
    
    # Simulate Escalation
    manager.set_level(DaemonLevel.VIGILANCE)
    time.sleep(0.5)
    manager.set_level(DaemonLevel.WAR)
    
    print(f"\nCurrent State: {manager.state.level.name}")
    print(f"Active Features: {len(manager.state.active_features)}")
