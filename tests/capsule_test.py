import sys
import os
import json

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.capsules.capsule_manager import CapsuleManager

def test_capsule_network():
    print("\n--- Testing Capsule Network ---")
    
    manager = CapsuleManager()
    
    # 1. Verify Loading
    if len(manager.capsules) > 0:
        print(f"✅ Loaded {len(manager.capsules)} capsules.")
    else:
        print("❌ No capsules loaded.")
        
    # 2. Verify Bidding
    # Intent: Needs precision
    intent_vector = [0.1, 0.2, 0.3] # Mock
    bids = manager.request_bids(intent_vector)
    
    if len(bids) > 0:
        print(f"✅ Received {len(bids)} bids.")
        best_bid = bids[0]
        print(f"Best Bid: {best_bid['name']} (Score: {best_bid['score']})")
        
        if best_bid['score'] >= 1.0: # 0.8 (precision) + 0.2 (idle)
            print("✅ Bid score calculation correct.")
        else:
            print(f"❌ Bid score too low: {best_bid['score']}")
    else:
        print("❌ No bids received.")

if __name__ == "__main__":
    test_capsule_network()
