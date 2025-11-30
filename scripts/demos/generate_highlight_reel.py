import json
import time
import random
import sys
import os

class HighlightReelGenerator:
    def __init__(self, config_path="config/demo_scenarios.json"):
        self.config_path = config_path
        self.scenarios = self.load_config()

    def load_config(self):
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def generate(self):
        output_lines = []
        output_lines.append("=== EMPEIRIA HAUS | SYSTEM STARTUP SEQUENCE ===")
        output_lines.append(f"TIMESTAMP: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        output_lines.append("MODE: HYPER-CONVERGENCE")
        output_lines.append("-" * 50)

        for chapter, demos in self.scenarios.items():
            output_lines.append(f"\n>> INITIALIZING MODULE: {chapter.upper()}")
            for demo in demos:
                # Simulate high-speed processing
                improvement = random.uniform(20.0, 99.9)
                line = f"[OK] {demo['id']} :: {demo['name']} >> OPTIMIZED ({improvement:.1f}%)"
                output_lines.append(line)
        
        output_lines.append("-" * 50)
        output_lines.append("ALL SYSTEMS STABILIZED.")
        output_lines.append("ENTROPY REDUCTION: 99.99%")
        output_lines.append("READY.")

        # Save to file
        output_path = "examples/client_deliverables/highlight_reel.txt"
        os.makedirs("examples/client_deliverables", exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write("\n".join(output_lines))
            
        print(f"✅ Highlight Reel Generated: {output_path}")
        print("(This file simulates the 15s scrolling terminal video)")

if __name__ == "__main__":
    gen = HighlightReelGenerator()
    gen.generate()
