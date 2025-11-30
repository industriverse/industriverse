import random
import time

class EnergyAPI:
    """
    Challenge #3: Thermodynamic Scheduling.
    Mocks a real-time connection to an energy grid (e.g., ERCOT, PJM).
    """
    def __init__(self, region="ERCOT"):
        self.region = region
        self.base_price = 0.12 # $/kWh

    def get_current_price(self):
        """
        Returns the current electricity price in $/kWh.
        Simulates volatility based on time of day and random fluctuations.
        """
        # Simulate time-of-day pricing (Peak: 14:00-18:00)
        current_hour = time.localtime().tm_hour
        is_peak = 14 <= current_hour <= 18
        
        volatility = random.uniform(-0.02, 0.05)
        peak_multiplier = 2.5 if is_peak else 1.0
        
        price = (self.base_price + volatility) * peak_multiplier
        return max(0.01, round(price, 4))

    def get_carbon_intensity(self):
        """
        Returns gCO2/kWh.
        """
        return random.randint(200, 500)
