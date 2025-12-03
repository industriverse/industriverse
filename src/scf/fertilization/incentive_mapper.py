from typing import Any

class IncentiveMapper:
    """
    Maps code performance and outcomes to economic incentives.
    """
    def map_incentives(self, code_result: Any) -> Any:
        """
        Calculates the reward (Joules/Value) for a given code result.
        """
        # Extract metrics
        review = code_result.get("review", {})
        score = review.get("score", 0.0)
        verdict = review.get("verdict", "REJECT")
        
        # Base Reward
        base_reward = 0.0
        if verdict == "APPROVE":
            base_reward = 100.0
        
        # Multipliers
        quality_multiplier = score * 2.0 # Higher score = double reward
        
        # Total Calculation
        total_reward = base_reward * quality_multiplier
        
        return {
            "reward": total_reward,
            "currency": "JouleToken",
            "breakdown": {
                "base": base_reward,
                "quality_multiplier": quality_multiplier
            }
        }
