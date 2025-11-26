import logging

logger = logging.getLogger(__name__)

class EnergyGovernor:
    """
    Throttles or approves actions based on a thermodynamic cost function and budget.
    """
    def __init__(self, max_joules_budget=1000.0):
        self.budget = max_joules_budget
        self.consumed = 0.0

    def request_action(self, action_name, estimated_cost_joules):
        """
        Returns True if action is approved, False if rejected due to budget.
        """
        if self.consumed + estimated_cost_joules > self.budget:
            logger.warning(f"Action '{action_name}' REJECTED. Cost {estimated_cost_joules}J exceeds remaining budget ({self.budget - self.consumed:.2f}J).")
            return False
        
        self.consumed += estimated_cost_joules
        logger.info(f"Action '{action_name}' APPROVED. Cost: {estimated_cost_joules}J. Remaining: {self.budget - self.consumed:.2f}J")
        return True

    def reset_budget(self):
        self.consumed = 0.0
        logger.info("Energy budget reset.")

class MetaGovernor:
    """
    Adjusts system sensitivity thresholds based on 'Meta-Entropy' (volatility of the environment).
    """
    def __init__(self, base_sensitivity=0.5):
        self.sensitivity = base_sensitivity # 0.0 to 1.0

    def update(self, environment_volatility):
        """
        Args:
            environment_volatility (float): 0.0 (calm) to 1.0 (chaos).
        """
        # If environment is chaotic, lower sensitivity to avoid false alarms.
        # If environment is calm, raise sensitivity to catch subtle anomalies.
        
        # Simple inverse relationship
        target_sensitivity = 1.0 - (environment_volatility * 0.8)
        
        # Smooth update (EMA)
        self.sensitivity = (self.sensitivity * 0.7) + (target_sensitivity * 0.3)
        
        logger.info(f"Meta-Governor: Env Volatility {environment_volatility:.2f} -> Adjusted Sensitivity to {self.sensitivity:.2f}")
        return self.sensitivity
