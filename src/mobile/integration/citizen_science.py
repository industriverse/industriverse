import random
from dataclasses import dataclass

@dataclass
class Mission:
    id: str
    title: str
    reward_credits: float
    data_type: str

class CitizenScience:
    """
    The Research Bridge: Distributes scientific data collection missions to users.
    """
    def __init__(self):
        self.available_missions = [
            Mission("M001", "Map WiFi Entropy in CBD", 10.0, "WIFI_MAP"),
            Mission("M002", "Record Urban Noise Floor", 5.0, "AUDIO_SAMPLE"),
            Mission("M003", "Verify Satellite Signal Strength", 15.0, "GPS_SNR")
        ]
        
    def list_missions(self):
        print("🔬 [Science] Available Missions:")
        for m in self.available_missions:
            print(f"   - [{m.id}] {m.title} (Reward: {m.reward_credits} Credits)")
            
    def accept_mission(self, mission_id: str, wallet):
        """
        User accepts and completes a mission.
        """
        mission = next((m for m in self.available_missions if m.id == mission_id), None)
        if mission:
            print(f"🚀 [Science] Mission '{mission.title}' Started...")
            # Simulate data collection
            print("   📡 Collecting Data...")
            
            # Reward
            print(f"   ✅ Mission Complete! Uploading Data.")
            wallet.credit_earnings(mission.reward_credits, "Citizen Science")
            return True
        return False
