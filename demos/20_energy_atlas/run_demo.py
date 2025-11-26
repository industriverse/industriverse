import time
import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class EnergyAtlas:
    def __init__(self):
        self.total_joules = 0.0
        self.logs = []

    def log_consumption(self, source, joules, task_type):
        self.total_joules += joules
        entry = {
            "timestamp": time.time(),
            "source": source,
            "joules": joules,
            "task": task_type
        }
        self.logs.append(entry)
        logger.info(f"[Energy Atlas] Logged: {joules:.2f}J from {source} for {task_type}")

    def report(self):
        print("\n--- Energy Atlas Report ---")
        print(f"Total Consumption: {self.total_joules:.2f} Joules")
        print(f"Total Events: {len(self.logs)}")
        print("-" * 30)

class ComputeNode:
    def __init__(self, node_id, atlas):
        self.node_id = node_id
        self.atlas = atlas

    def perform_task(self, task_name, complexity):
        logger.info(f"[{self.node_id}] Starting task: {task_name} (Complexity: {complexity})")
        
        # Simulate work
        duration = complexity * 0.1
        time.sleep(duration)
        
        # Calculate Energy Cost (Simulated)
        # E.g., 10 Watts * duration
        power_watts = 10 + random.random() * 5
        energy_joules = power_watts * duration
        
        self.atlas.log_consumption(self.node_id, energy_joules, task_name)

def run():
    print("\n" + "="*60)
    print(" DEMO 20: ENERGY ATLAS VISUALIZATION")
    print("="*60 + "\n")

    atlas = EnergyAtlas()
    node_a = ComputeNode("gpu_cluster_01", atlas)
    node_b = ComputeNode("edge_device_04", atlas)

    print("--- Phase 1: Workload Execution ---")
    node_a.perform_task("Train_RND1_Model", complexity=5)
    node_b.perform_task("Inference_UserLM", complexity=2)
    node_a.perform_task("Verify_ZKP_Proof", complexity=3)
    
    # Visualize "Graph" (ASCII)
    print("\n--- Phase 2: Visualization ---")
    atlas.report()
    
    print("Consumption by Source:")
    sources = {}
    for log in atlas.logs:
        sources[log['source']] = sources.get(log['source'], 0) + log['joules']
    
    for source, joules in sources.items():
        bar_len = int(joules / 5)
        bar = "⚡" * bar_len
        print(f"{source:<15} | {bar} {joules:.2f}J")

    print("\n" + "="*60)
    print(" DEMO COMPLETE: ENERGY TRACKED")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
