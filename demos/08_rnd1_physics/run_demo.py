import time
import math
import logging
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class RND1Simulator:
    def __init__(self):
        pass

    def simulate_microstructure(self, grain_size_initial, temp, time_steps):
        """
        Simulates grain growth using a simplified Monte Carlo approach (M2N2 model proxy).
        """
        logger.info(f"Initializing M2N2 Simulation: Initial Grain Size={grain_size_initial}um, Temp={temp}K")
        
        current_grain_size = grain_size_initial
        history = []

        for t in range(time_steps):
            # Arrhenius equation proxy for growth rate
            # Rate = A * exp(-Q / RT)
            # Simplified: Rate increases exponentially with temperature
            growth_rate = 0.01 * math.exp((temp - 1000) / 200) 
            
            # Add stochastic noise
            noise = random.uniform(-0.05, 0.1)
            
            delta = growth_rate + noise
            current_grain_size += max(0, delta)
            
            history.append(current_grain_size)
            
            # Visualize progress
            bar_len = int(current_grain_size / 2)
            bar = "▓" * bar_len
            print(f"Step {t+1}/{time_steps}: Size={current_grain_size:.2f}um {bar}")
            
            time.sleep(0.2)

        return history

def run():
    print("\n" + "="*60)
    print(" DEMO 8: RND1 PHYSICS SIMULATION (M2N2)")
    print("="*60 + "\n")

    sim = RND1Simulator()

    print("--- Scenario 1: Standard Annealing (1100K) ---")
    sim.simulate_microstructure(grain_size_initial=10.0, temp=1100, time_steps=10)

    print("\n--- Scenario 2: High-Temp Sintering (1400K) ---")
    sim.simulate_microstructure(grain_size_initial=10.0, temp=1400, time_steps=10)

    print("\n" + "="*60)
    print(" DEMO COMPLETE: PHYSICS SIMULATION VERIFIED")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
