import sys
import os
import time
import random
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.edge.edge_node_manager import EdgeNodeManager
from src.edge.bitnet_deployer import BitNetDeployer

def print_header(text):
    print(f"\n{'='*60}")
    print(f"   {text}")
    print(f"{'='*60}")

def demo_edge_compute():
    print_header("DEMO: THE EDGE COMPUTE FABRIC")
    print("Scenario: Distributed BitNet Deployment (Swarm Intelligence)")
    
    # 1. Initialize Fleet
    mgr = EdgeNodeManager()
    print("\n>> STEP 1: Booting Edge Cluster...")
    nodes = []
    for i in range(5):
        nid = mgr.register_node(f"pi-worker-{i+1:02d}", "arm64", 4, 8)
        nodes.append(nid)
    
    # 2. Deploy Intelligence
    deployer = BitNetDeployer(mgr)
    print("\n>> STEP 2: Deploying 1-Bit LLM (BitNet b1.58)...")
    deployer.deploy_model("BitNet_3B_Quantized", "arm64")
    
    # 3. Simulate Inference
    print("\n>> STEP 3: Running Distributed Inference...")
    print("   Task: Analyze Local Video Feed for Anomalies")
    
    for nid in nodes:
        node = mgr.nodes[nid]
        latency = random.uniform(15, 45) # ms
        confidence = random.uniform(0.8, 0.99)
        print(f"     -> {node.hostname}: Inference Complete ({latency:.1f}ms) | Confidence: {confidence:.2f}")
        
    print_header("DEMO COMPLETE: EDGE INTELLIGENCE ONLINE")

if __name__ == "__main__":
    demo_edge_compute()
