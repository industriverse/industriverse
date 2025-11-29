import json
import os
import sys

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.economy.pricing_engine import ExergyPricingEngine

class CapsuleManager:
    """
    AI Shield v3 - Gate 10: Capsule Manager.
    Orchestrates the 'Distributed Intelligence' of the factory.
    Capsules bid on tasks based on their capabilities and current load.
    """
    def __init__(self, definitions_dir="src/capsules/definitions"):
        self.definitions_dir = definitions_dir
        self.capsules = []
        self.pricing_engine = ExergyPricingEngine()
        self.load_capsules()

    def load_capsules(self):
        """Loads all capsule definitions from JSON files."""
        if not os.path.exists(self.definitions_dir):
            print(f"Warning: Definitions dir {self.definitions_dir} not found.")
            return

        for filename in os.listdir(self.definitions_dir):
            if filename.endswith(".json"):
                path = os.path.join(self.definitions_dir, filename)
                try:
                    with open(path, 'r') as f:
                        capsule_def = json.load(f)
                        self.capsules.append(capsule_def)
                        print(f"Loaded Capsule: {capsule_def.get('name')} ({capsule_def.get('id')})")
                except Exception as e:
                    print(f"Failed to load {filename}: {e}")

    def request_bids(self, intent_vector):
        """
        Broadcasts an intent to all capsules and collects bids.
        Input: intent_vector (list)
        Output: List of bids sorted by score.
        """
        bids = []
        for cap in self.capsules:
            bid = self._calculate_bid(cap, intent_vector)
            if bid:
                bids.append(bid)
        
        # Sort by score (descending)
        bids.sort(key=lambda x: x['score'], reverse=True)
        return bids

    def _calculate_bid(self, capsule, intent_vector):
        """
        Internal logic to determine if a capsule wants this job.
        In a real system, this would be an Agentic decision.
        Here, we use a heuristic based on capabilities.
        """
        capabilities = capsule.get("capabilities", [])
        
        # Simple Match: Do capabilities overlap with intent keywords?
        # (Mocking intent vector as keywords for simplicity here, 
        # or assuming intent_vector has metadata attached)
        
        # For this mock, we assume intent_vector has a 'keywords' field attached 
        # or we just match blindly for the test.
        
        score = 0.0
        
        # Heuristic: Specialized capsules get higher score
        if "precision" in capabilities:
            score += 0.8
        if "speed" in capabilities:
            score += 0.5
            
        # Availability Check (Mock)
        if capsule.get("status") == "IDLE":
            score += 0.2
            
        if score > 0:
            return {
                "capsule_id": capsule.get("id"),
                "name": capsule.get("name"),
                "score": round(score, 2),
                "price_estimate": 10.0 * score # Mock price
            }
        return None

if __name__ == "__main__":
    manager = CapsuleManager()
    print("--- Requesting Bids ---")
    bids = manager.request_bids([0.1, 0.2, 0.3])
    print(json.dumps(bids, indent=2))
