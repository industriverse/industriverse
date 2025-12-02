import sys
import os
import time
import random
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.energy.neural_battery import NeuralBattery
from src.energy.grid_stabilizer import GridStabilizer

def print_header(text):
    print(f"\n{'='*60}")
    print(f"   {text}")
    print(f"{'='*60}")

def demo_neural_battery():
    print_header("DEMO: THE NEURAL BATTERY")
    print("Scenario: ERCOT (Texas) Frequency Response")
    
    # 1. Initialize Asset
    battery = NeuralBattery("ERCOT_Node_1", max_mw=500.0, min_mw=50.0)
    stabilizer = GridStabilizer(battery)
    
    # 2. Simulation Loop
    print_header("LIVE GRID TELEMETRY")
    
    scenarios = [
        (60.00, "Normal Operation"),
        (59.95, "Minor Dip"),
        (59.85, "Wind Drop (Stress)"),
        (59.70, "GENERATOR TRIP (CRITICAL)"),
        (60.00, "Recovery"),
        (60.10, "Solar Peak (Surplus)"),
        (60.25, "Negative Pricing Event")
    ]
    
    for freq, desc in scenarios:
        print(f"\n>> EVENT: {desc}")
        stabilizer.on_frequency_change(freq)
        battery.get_status()
        time.sleep(0.5)
        
    print_header("DEMO COMPLETE: GRID STABILIZED")

if __name__ == "__main__":
    demo_neural_battery()
