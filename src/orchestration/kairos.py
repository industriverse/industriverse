import random
from src.integrations.energy_api import EnergyAPI

class KairosOptimizer:
    """
    The Economic Optimizer.
    Decides 'When' to run based on Value vs Cost.
    """
    def __init__(self):
        self.energy_api = EnergyAPI()
        self.min_profit_margin = 0.10

    def get_grid_price(self):
        """
        Gets the real-time electricity price from the Energy API.
        """
        return self.energy_api.get_current_price()

    def evaluate(self, task):
        """
        Decides EXECUTE or DEFER based on thermodynamic economics.
        """
        if task['priority'] == 'CRITICAL':
            return "EXECUTE"

        current_price = self.get_grid_price()
        max_bid = task['max_bid_price']
        value = task['negentropy_value']

        # Economic Logic:
        # If price is low, run everything.
        # If price is high, only run High Value tasks.
        
        # Adjusted Bid: We pay more for high value tasks.
        effective_bid = max_bid * (1 + value) 

        # Check Hydration Cost (if applicable)
        hydration_cost = task.get('hydration_cost_est', 0.0)
        if hydration_cost > 0.05 and task['priority'] != 'CRITICAL':
             # If hydration is expensive, be stricter
             effective_bid *= 0.8

        if current_price <= effective_bid:
            return "EXECUTE"
        else:
            return f"DEFER (Price {current_price:.2f} > Bid {effective_bid:.2f})"
