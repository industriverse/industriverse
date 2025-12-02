import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.social.social_orchestrator import SocialOrchestrator

def print_header(text):
    print(f"\n{'='*60}")
    print(f"   {text}")
    print(f"{'='*60}")

def demo_social_mesh():
    print_header("DEMO: THE SOVEREIGN SOCIAL NETWORK")
    print("Scenario: Vicarious Discovery & The Proof Economy")
    
    orch = SocialOrchestrator()
    
    # 1. Topic Launch
    print("\n>> STEP 1: Launching Reasoning Capsule...")
    cid = orch.launch_capsule("Optimize Graphene for Mars Habitats", "Elon_M")
    
    # 2. Social Interaction
    print("\n>> STEP 2: Community Engagement...")
    orch.subscribe("Fan_1", cid)
    orch.subscribe("Investor_VC", cid)
    
    # 3. Reasoning Cycle 1 (Standard)
    print("\n>> STEP 3: Initial Reasoning Cycle...")
    orch.capsules[cid].run_cycle()
    time.sleep(0.5)
    
    # 4. Funding / Boost
    print("\n>> STEP 4: Funding Injection...")
    orch.boost_capsule(cid, 1000.0)
    
    # 5. Reasoning Cycle 2 (Accelerated)
    print("\n>> STEP 5: Accelerated Reasoning Cycle...")
    # Simulate a breakthrough
    orch.capsules[cid]._emit_update("BREAKTHROUGH: 30% Weight Reduction Achieved!", "PROOF", {"hash": "0xABC123", "confidence": 0.99})
    orch.capsules[cid].user_lm.narrate("We have confirmed the simulation results. This is a viable candidate.")
    
    # 6. The Feed Experience
    print_header("USER FEED: DYNAMIC ISLAND VIEW")
    feed = orch.get_user_feed("Fan_1")
    for item in feed:
        icon = "📝"
        if item.type == "PROOF": icon = "🏆"
        elif item.type == "FUNDING": icon = "🚀"
        elif item.type == "EXPERIMENT": icon = "🧪"
        
        print(f"   {icon} [{item.type}] {item.message}")
        
    print_header("DEMO COMPLETE: REASONING SOCIALIZED")

if __name__ == "__main__":
    demo_social_mesh()
