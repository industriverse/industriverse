import time
import json
import os
import random
from typing import Dict, Any

class CollectorDaemon:
    """
    Industriverse Data Hub: Collector Daemon.
    
    Purpose:
    Runs 24/7 to collect:
    - Simulator runs
    - Energy minimization trajectories
    - AI Shield rejects
    - Operator overrides
    - A2A capsule negotiations
    
    Output:
    Raw data shards in 'data/datahub/raw/'.
    """
    def __init__(self, output_dir="data/datahub/raw"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.is_running = False
        
    def start(self):
        self.is_running = True
        print("📡 Data Hub Collector Daemon Started.")
        print(f"   Target: {self.output_dir}")
        self.run_loop()
        
    def stop(self):
        self.is_running = False
        print("🛑 Data Hub Collector Daemon Stopped.")

    def run_loop(self):
        """
        Simulates the continuous collection loop.
        """
        count = 0
        while self.is_running and count < 5: # Limit for demo
            data_packet = self.collect_system_state()
            self.save_packet(data_packet)
            count += 1
            time.sleep(0.5)

    def collect_system_state(self) -> Dict[str, Any]:
        """
        Simulates gathering data from various subsystems.
        """
        # Mock Data Sources
        return {
            "timestamp": time.time(),
            "source": random.choice(["SIMULATOR", "AI_SHIELD", "CAPSULE_A2A", "ROBOTICS"]),
            "energy_state": {
                "joules": random.uniform(100, 500),
                "entropy": random.uniform(0.1, 0.9)
            },
            "event_type": "OPTIMIZATION_STEP",
            "payload": {
                "action_vector": [random.random() for _ in range(3)],
                "safety_score": random.uniform(0.8, 1.0)
            }
        }

    def save_packet(self, packet: Dict[str, Any]):
        """
        Saves the data packet as a JSON shard.
        """
        filename = f"shard_{int(packet['timestamp']*1000)}_{packet['source']}.json"
        path = os.path.join(self.output_dir, filename)
        with open(path, 'w') as f:
            json.dump(packet, f)
        print(f"   Saved shard: {filename}")

if __name__ == "__main__":
    daemon = CollectorDaemon()
    daemon.start()
