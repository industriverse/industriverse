from dataclasses import dataclass
from typing import Dict, List, Optional
import time

@dataclass
class DaemonReward:
    reward_type: str # 'FOSSIL_BONUS', 'ENTROPY_BONUS', 'EFFICIENCY_BONUS', 'PENALTY'
    amount: float
    timestamp: float
    reason: str

class IncentiveEngine:
    """
    The "North Star" Engine.
    Calculates rewards for the Daemon to incentivize optimal behavior.
    """
    def __init__(self):
        self.total_score = 0.0
        self.reward_history: List[DaemonReward] = []
        
        # Incentive Configuration
        self.points_per_fossil = 0.1
        self.points_per_mj_saved = 1.0
        self.points_per_kwh_efficiency = 5.0 # Bonus for low energy/inference

    def calculate_rewards(self, metrics: Dict[str, float]) -> List[DaemonReward]:
        """
        Evaluate metrics and award points.
        Metrics expected:
        - fossils_processed_count
        - energy_saved_mj
        - inference_efficiency_kwh
        """
        new_rewards = []
        
        # 1. Fossil Processing Reward
        fossils = metrics.get('fossils_processed_count', 0)
        if fossils > 0:
            amount = fossils * self.points_per_fossil
            new_rewards.append(DaemonReward(
                reward_type='FOSSIL_BONUS',
                amount=amount,
                timestamp=time.time(),
                reason=f"Processed {fossils} fossils"
            ))

        # 2. Entropy/Energy Savings Reward
        mj_saved = metrics.get('energy_saved_mj', 0)
        if mj_saved > 0:
            amount = mj_saved * self.points_per_mj_saved
            new_rewards.append(DaemonReward(
                reward_type='ENTROPY_BONUS',
                amount=amount,
                timestamp=time.time(),
                reason=f"Saved {mj_saved:.2f} MJ of energy"
            ))
            
        # 3. Efficiency Bonus (if efficiency is better than baseline, say 0.01 kWh/inf)
        efficiency = metrics.get('inference_efficiency_kwh', 1.0)
        baseline = 0.01
        if efficiency < baseline:
            # Lower is better. Bonus proportional to improvement.
            improvement = (baseline - efficiency) / baseline
            amount = improvement * self.points_per_kwh_efficiency
            new_rewards.append(DaemonReward(
                reward_type='EFFICIENCY_BONUS',
                amount=amount,
                timestamp=time.time(),
                reason=f"High Efficiency: {efficiency:.4f} kWh/inf"
            ))

        # Apply Rewards
        for reward in new_rewards:
            self.total_score += reward.amount
            self.reward_history.append(reward)
            print(f"🌟 DAEMON REWARD: +{reward.amount:.2f} ({reward.reason})")
            
        return new_rewards

    def get_score(self) -> float:
        return self.total_score
