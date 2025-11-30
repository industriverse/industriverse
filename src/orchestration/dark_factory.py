import time
import random
from src.orchestration.chronos import Chronos
from src.orchestration.emm import EntropyMarketMaker
from src.orchestration.aletheia import AletheiaTruthLayer

class DarkFactoryController:
    """
    The Autopilot. Manages the Quadrality (Chronos-Kairos-Telos-Aletheia).
    """
    def __init__(self):
        self.chronos = Chronos()
        self.emm = EntropyMarketMaker()
        self.aletheia = AletheiaTruthLayer()
        self.running = False

    def run_cycle(self):
        """
        Single 'Lights-Out' Cycle.
        """
        # 1. Sense Market
        energy_price = self.chronos.kairos.get_grid_price()
        stance = self.emm.get_market_stance(energy_price)
        bid_mult = self.emm.get_bid_multiplier(stance)
        
        print(f"\n[DarkFactory] 🌑 Cycle Start. Price: ${energy_price:.2f} | Stance: {stance} | Bid Mult: {bid_mult}x")

        # 2. Configure Kairos (Inject Market Logic)
        # In a real system, we'd update Kairos config. 
        # For MVP, we just print the intent.
        
        # 3. Run Chronos (Dispatch Tasks)
        # We manually tick Chronos for one cycle
        self.chronos.tick()

        # 4. Validate Reality (Aletheia)
        # Mock: Let's assume the last executed task needs validation
        # In prod, Chronos would return executed tasks.
        
        # 5. Profit Calculation (Mock)
        profit = random.uniform(-5, 20)
        self.emm.record_trade({"name": "Cycle_Trade"}, profit)

    def run(self):
        self.running = True
        print("🏭 Dark Factory Autopilot ENGAGED.")
        while self.running:
            self.run_cycle()
            time.sleep(5)

if __name__ == "__main__":
    df = DarkFactoryController()
    df.run()
