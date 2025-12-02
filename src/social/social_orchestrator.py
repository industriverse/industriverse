from typing import Dict, List
from src.social.reasoning_capsule import ReasoningCapsule, CapsuleUpdate

class SocialOrchestrator:
    """
    The Platform Manager for the Social Industriverse.
    Orchestrates capsules, subscriptions, and funding.
    """
    
    def __init__(self):
        self.capsules: Dict[str, ReasoningCapsule] = {}
        
    def launch_capsule(self, topic: str, owner_id: str) -> str:
        capsule = ReasoningCapsule(topic, owner_id)
        self.capsules[capsule.id] = capsule
        return capsule.id
        
    def subscribe(self, user_id: str, capsule_id: str):
        if capsule_id in self.capsules:
            self.capsules[capsule_id].add_subscriber(user_id)
            
    def boost_capsule(self, capsule_id: str, amount: float):
        """
        Injects funding to accelerate reasoning (e.g., buy more GPU time).
        """
        if capsule_id in self.capsules:
            print(f"   🚀 [BOOST] Capsule {capsule_id} received {amount} Credits!")
            # In a real system, this would trigger RND1 to allocate more resources
            self.capsules[capsule_id]._emit_update(f"Boosted by {amount} Credits!", "FUNDING", {"amount": amount})
            
    def get_user_feed(self, user_id: str) -> List[CapsuleUpdate]:
        """
        Aggregates updates from all subscribed capsules.
        """
        feed = []
        for cap in self.capsules.values():
            if user_id in cap.subscribers:
                feed.extend(cap.updates)
        return sorted(feed, key=lambda x: x.timestamp, reverse=True)

    def process_updates(self):
        """
        Simulates the processing of the social feed.
        """
        # In a real system, this would push updates to WebSocket clients
        # For simulation, we just iterate through capsules and run a cycle occasionally
        for cid, capsule in self.capsules.items():
            # Randomly trigger a cycle for liveliness
            import random
            if random.random() < 0.3:
                capsule.run_cycle()


# --- Verification ---
if __name__ == "__main__":
    orch = SocialOrchestrator()
    cid = orch.launch_capsule("Quantum Materials", "Scientist_X")
    orch.subscribe("Viewer_Y", cid)
    orch.boost_capsule(cid, 500.0)
    orch.capsules[cid].run_cycle()
    print(f"Feed Items: {len(orch.get_user_feed('Viewer_Y'))}")
