import sys
import os
import time

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.core.a2a_protocol import A2AProtocol
from src.core.negotiation_engine import NegotiationEngine

def verify_phase_111():
    print("==================================================")
    print("🧪 Phase 111 Verification: Challenges 5 & 8")
    print("==================================================")

    # Setup Agents
    requester = A2AProtocol("Agent_Requester")
    provider = NegotiationEngine("Agent_Provider", capabilities=["WELDING_V1", "INSPECTION_V2"])

    # 1. Requester Broadcasts ASK
    print("\n📡 1. Broadcasting ASK for 'WELDING_V1'...")
    ask_payload = {
        "task_type": "WELDING_V1",
        "max_price": 0.50,
        "deadline": time.time() + 3600
    }
    ask_msg = requester.broadcast("ASK", ask_payload)

    # 2. Provider Receives ASK
    print("\n📥 2. Provider Receiving Message...")
    # Manually inject for simulation (since no real network)
    provider.a2a.receive(ask_msg)
    
    # 3. Provider Processes ASK and Bids
    print("\n🤖 3. Provider Evaluating ASK...")
    bid_msg = provider.process_ask(ask_msg)

    if bid_msg:
        # 4. Requester Receives BID
        print("\n📬 4. Requester Receiving BID...")
        requester.receive(bid_msg)
        
        last_msg = requester.inbox[-1]
        print(f"   Requester Inbox: Received {last_msg['type']} from {last_msg['sender']}")
        print(f"   Bid Price: ${last_msg['payload']['price']}")
        print(f"   ZK Proof: {last_msg['payload']['zk_proof']}")
    else:
        print("❌ Provider did not bid (Price too high or capability missing).")

    print("\n==================================================")
    print("✅ Verification Complete.")
    print("==================================================")

if __name__ == "__main__":
    verify_phase_111()
