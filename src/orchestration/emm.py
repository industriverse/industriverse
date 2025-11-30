import random

class EntropyMarketMaker:
    """
    The Economist Agent. Optimizes Global Factory Parameters.
    """
    def __init__(self):
        self.balance = 1000.0 # Starting Capital
        self.history = []

    def get_market_stance(self, energy_price):
        """
        Decides the Factory Persona based on market conditions.
        """
        if energy_price > 0.20:
            return "CONSERVATIVE"
        elif energy_price < 0.10:
            return "AGGRESSIVE"
        else:
            return "BALANCED"

    def get_bid_multiplier(self, stance):
        """
        Returns the bid multiplier based on stance.
        """
        if stance == "AGGRESSIVE":
            return 1.5 # Pay 50% more to win execution
        elif stance == "CONSERVATIVE":
            return 0.8 # Undercut
        return 1.0

    def record_trade(self, task, profit):
        """
        Updates internal model (RL Step).
        """
        self.balance += profit
        self.history.append({
            "task": task['name'],
            "profit": profit,
            "balance": self.balance
        })
        print(f"[EMM] 💰 Trade Recorded. Profit: ${profit:.2f} | Balance: ${self.balance:.2f}")
