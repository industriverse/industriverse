import sys
import os
import shutil
import time

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.loop.intent_queue import IntentQueue
from src.dgm_engine.core.self_understanding_engine import SelfUnderstandingEngine
from src.dgm_engine.discovery.agent import DGMDiscoveryAgent

def test_hardening():
    print("\n--- Testing No-Mock Hardening ---")
    
    # 1. Test Intent Queue Persistence
    print("\n[1] Testing Intent Queue Persistence...")
    db_path = "test_queue.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        
    q1 = IntentQueue(db_path)
    q1.add("Test Intent 1", {"priority": "high"})
    q1.add("Test Intent 2", {"priority": "low"})
    
    # Simulate restart
    del q1
    q2 = IntentQueue(db_path)
    
    if len(q2) == 2:
        print("✅ Persistence Verified (Count: 2).")
    else:
        print(f"❌ Persistence Failed (Count: {len(q2)}).")
        
    item = q2.get_next()
    if item and item['text'] == "Test Intent 1":
        print("✅ Retrieval Verified.")
    else:
        print("❌ Retrieval Failed.")
        
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)

    # 2. Test Self-Understanding Metrics
    print("\n[2] Testing Self-Understanding Metrics...")
    engine = SelfUnderstandingEngine()
    caps = engine.analyze_capabilities()
    
    print(f"  Capabilities: {caps}")
    
    if caps['code_generation'] != 0.85: # Should not be mock value
        print("✅ Code Generation Metric is Real.")
    else:
        print("❌ Code Generation Metric is still Mock (0.85).")
        
    if caps['proof_generation'] != 0.92:
        print("✅ Proof Success Metric is Real.")
    else:
        print("❌ Proof Success Metric is still Mock (0.92).")

    # 3. Test Discovery Agent Heuristics
    print("\n[3] Testing Discovery Agent Heuristics...")
    agent = DGMDiscoveryAgent()
    
    # Test with physics keywords
    res1 = agent.generate_hypothesis("quantum energy entropy")
    score1 = res1['scores']['prin']
    
    # Test with nonsense
    res2 = agent.generate_hypothesis("foo bar baz")
    score2 = res2['scores']['prin']
    
    print(f"  Score (Physics): {score1}")
    print(f"  Score (Nonsense): {score2}")
    
    if score1 > score2:
        print("✅ Heuristic Scoring Verified (Physics > Nonsense).")
    else:
        print("❌ Heuristic Scoring Failed.")

if __name__ == "__main__":
    test_hardening()
