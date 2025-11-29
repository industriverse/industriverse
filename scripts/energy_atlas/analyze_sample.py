import sys
import os

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.energy_atlas.gcode_parser import GCodeEnergyParser

def analyze_file(filepath: str):
    print(f"Analyzing: {filepath}")
    
    # Check if binary G-code (bgcode)
    if filepath.endswith('.bgcode'):
        print("WARNING: This is a binary G-code file (.bgcode).")
        print("The current parser expects ASCII G-code (.gcode).")
        print("We need to decode it or find ASCII samples.")
        return

    parser = GCodeEnergyParser()
    try:
        metrics = parser.parse_file(filepath)
        print("\n--- Energy Metrics ---")
        print(f"Total Energy: {metrics['total_energy_joules']:.2f} J")
        print(f"Total Time:   {metrics['total_time_seconds']:.2f} s")
        print(f"Avg Power:    {metrics['average_power_watts']:.2f} W")
        print(f"Layers:       {metrics['layers']}")
    except Exception as e:
        print(f"Error parsing file: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_sample.py <gcode_file>")
        sys.exit(1)
        
    analyze_file(sys.argv[1])
