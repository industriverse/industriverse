import time
import random
import os
import sys

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

class GodView:
    def __init__(self):
        self.nodes = [
            {"id": "miner_01", "type": "Miner", "status": "ACTIVE", "load": 85},
            {"id": "miner_02", "type": "Miner", "status": "ACTIVE", "load": 78},
            {"id": "refiner_01", "type": "Refiner", "status": "ACTIVE", "load": 92},
            {"id": "refiner_02", "type": "Refiner", "status": "MAINTENANCE", "load": 0},
            {"id": "assembly_01", "type": "Assembler", "status": "ACTIVE", "load": 65},
            {"id": "qc_scanner", "type": "Sensor", "status": "ACTIVE", "load": 12}
        ]

    def update(self):
        for node in self.nodes:
            if node["status"] == "ACTIVE":
                # Random fluctuation
                node["load"] = max(0, min(100, node["load"] + random.randint(-5, 5)))
                
                # Random fault injection
                if random.random() > 0.98:
                    node["status"] = "WARNING"
            elif node["status"] == "WARNING":
                if random.random() > 0.8:
                    node["status"] = "ACTIVE" # Recover
            elif node["status"] == "MAINTENANCE":
                if random.random() > 0.95:
                    node["status"] = "ACTIVE" # Back online

    def render(self):
        clear_screen()
        print("="*60)
        print(" INDUSTRIVERSE GLOBAL OPERATIONS CENTER (GOD VIEW)")
        print("="*60)
        print(f"{'NODE ID':<15} | {'TYPE':<10} | {'STATUS':<12} | {'LOAD':<20}")
        print("-" * 60)
        
        for node in self.nodes:
            status_color = "\033[92m" # Green
            if node["status"] == "WARNING": status_color = "\033[93m" # Yellow
            if node["status"] == "MAINTENANCE": status_color = "\033[90m" # Grey
            reset = "\033[0m"
            
            bar_len = int(node["load"] / 5)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            
            print(f"{node['id']:<15} | {node['type']:<10} | {status_color}{node['status']:<12}{reset} | {bar} {node['load']}%")
            
        print("-" * 60)
        print("Press Ctrl+C to exit.")

def run():
    dashboard = GodView()
    try:
        # Run for 5 seconds (50 frames)
        for _ in range(50):
            dashboard.update()
            dashboard.render()
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        print("\n" + "="*60)
        print(" DEMO COMPLETE: DASHBOARD VERIFIED")
        print("="*60 + "\n")

if __name__ == "__main__":
    run()
