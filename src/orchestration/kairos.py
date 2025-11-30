import random

class KairosOptimizer:
    """
    The Economist. Optimizes execution based on Energy Price vs. Value.
    """
    def __init__(self):
        pass

    def get_grid_price(self):
        """Simulates real-time energy price ($/kWh)."""
        # In prod, this would hit an API.
        return random.uniform(0.05, 0.25)

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
