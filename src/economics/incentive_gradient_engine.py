from dataclasses import dataclass
from typing import Dict

@dataclass
class IncentiveProfile:
    discovery_reward: float = 1.0
    efficiency_reward: float = 1.0
    security_penalty: float = 2.0
    waste_penalty: float = 1.5

class IncentiveGradientEngine:
    """
    The Dopamine System.
    Dynamically shapes the incentive landscape to guide agent behavior.
    """
    
    def __init__(self):
        self.profile = IncentiveProfile()
        
    def shape_gradient(self, dominant_drive: str):
        """
        Adjusts incentives based on the Organism's dominant drive.
        """
        print(f"   🍬 [INCENTIVE] Shaping Gradient for Drive: {dominant_drive}")
        
        if dominant_drive == "SURVIVAL":
            # High penalty for waste/risk, reward efficiency
            self.profile.efficiency_reward = 2.0
            self.profile.waste_penalty = 3.0
            self.profile.discovery_reward = 0.5
            print("     -> Prioritizing Efficiency & Safety.")
            
        elif dominant_drive == "CURIOSITY":
            # High reward for discovery, tolerate some waste
            self.profile.discovery_reward = 2.5
            self.profile.waste_penalty = 0.8
            print("     -> Prioritizing Discovery.")
            
        elif dominant_drive == "EXPANSION":
            # Balanced high rewards
            self.profile.discovery_reward = 1.5
            self.profile.efficiency_reward = 1.5
            print("     -> Prioritizing Growth.")
            
    def calculate_reward(self, action_type: str, outcome_metric: float) -> float:
        """
        Calculates the Negentropy Credit reward for an action.
        """
        reward = 0.0
        if action_type == "DISCOVERY":
            reward = outcome_metric * self.profile.discovery_reward
        elif action_type == "OPTIMIZATION":
            reward = outcome_metric * self.profile.efficiency_reward
            
        return round(reward, 2)

# --- Verification ---
if __name__ == "__main__":
    engine = IncentiveGradientEngine()
    
    # 1. Survival Mode
    engine.shape_gradient("SURVIVAL")
    r1 = engine.calculate_reward("DISCOVERY", 10.0)
    print(f"   Reward for Discovery (10.0): {r1}")
    
    # 2. Curiosity Mode
    engine.shape_gradient("CURIOSITY")
    r2 = engine.calculate_reward("DISCOVERY", 10.0)
    print(f"   Reward for Discovery (10.0): {r2}")
