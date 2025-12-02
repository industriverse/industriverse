import sys
import os
import time
import random
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.consensus.raft_protocol import RaftNode
from src.consensus.mace_engine import MACEEngine

def print_header(text):
    print(f"\n{'='*60}")
    print(f"   {text}")
    print(f"{'='*60}")

def demo_mace_consensus():
    print_header("DEMO: MULTI-AGENT CONSENSUS ENGINE (MACE)")
    print("Scenario: The Council of Truth (Leader Election & Ratification)")
    
    # 1. Initialize Cluster
    print("\n>> STEP 1: Assembling the Council...")
    agents = []
    names = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"]
    for name in names:
        agents.append(RaftNode(f"Agent_{name}", []))
        
    # Link Peers (Full Mesh)
    for agent in agents:
        agent.peers = [p for p in agents if p != agent]
        
    # 2. Leader Election
    print("\n>> STEP 2: Electing a Leader...")
    # Simulate random timeouts
    time.sleep(0.1)
    agents[0].start_election() # Force Alpha to start for demo stability
    
    # 3. Propose Truth
    print("\n>> STEP 3: Proposing a Discovery...")
    mace = MACEEngine(agents)
    truth = "Discovery: Room_Temp_Superconductor_Confirmed"
    
    success = mace.propose_truth(truth)
    
    if success:
        print("\n   🎉 THE COUNCIL HAS SPOKEN.")
        print(f"   '{truth}' is ratified as OBJECTIVE REALITY.")
    else:
        print("\n   🚫 THE COUNCIL DISSENTS.")
        
    print_header("DEMO COMPLETE: CONSENSUS ACHIEVED")

if __name__ == "__main__":
    demo_mace_consensus()
