import time
import json
import random
from pathlib import Path
from typing import Dict, Any
from src.scf.ingestion.atlas_builder import AtlasBuilder

class DarkFactoryLite:
    """
    The First Sovereign Agent.
    Optimizes industrial parameters by recalling physics baselines from the Energy Atlas.
    """
    def __init__(self, atlas_db: str = "energy_atlas.db"):
        self.atlas = AtlasBuilder("mock_vault", db_path=atlas_db)
        self.decision_log = Path("dark_factory_decisions.jsonl")
        print("🏭 Dark Factory Lite Agent Online.")

    def run_loop(self, steps: int = 10):
        """
        Main Control Loop: Observe -> Recall -> Act -> Audit.
        """
        print(f"   Starting {steps}-step optimization loop...")
        
        for i in range(steps):
            # 1. Observe (Simulated Plant State)
            current_state = self._observe_plant()
            print(f"   [{i+1}/{steps}] Observed Entropy: {current_state['entropy_rate']:.4f} | Power: {current_state['power_w']:.2f}W")
            
            # 2. Recall (Query Atlas for better states)
            # We look for states with LOWER entropy than current (more ordered/efficient)
            target_entropy = current_state['entropy_rate'] * 0.95
            recommendations = self.atlas.query(max_entropy=target_entropy, limit=1)
            
            # 3. Act (Make Decision)
            decision = self._make_decision(current_state, recommendations)
            
            # 4. Audit (Log to immutable chain - stubbed as JSONL)
            self._log_decision(decision)
            
            # Simulate time step
            time.sleep(0.5)
            
        print(f"✅ Optimization Loop Complete. Log: {self.decision_log}")

    def _observe_plant(self) -> Dict[str, float]:
        """Simulate reading sensors from a chaotic system."""
        # High entropy state (inefficient)
        return {
            "timestamp": time.time(),
            "power_w": 1000.0 + random.uniform(-50, 50),
            "temp_c": 65.0 + random.uniform(-2, 2),
            "entropy_rate": 2.5 + random.uniform(-0.1, 0.1) # Arbitrary units
        }

    def _make_decision(self, current: Dict[str, Any], memory: list) -> Dict[str, Any]:
        """Decide on control action based on memory."""
        action = "MAINTAIN"
        reason = "No better state found in Atlas."
        
        if memory:
            best_past = memory[0]
            # If we found a historical state with higher entropy (wait, we want LOWER entropy for order, 
            # OR we want to match a high-efficiency flow which might have specific entropy signature).
            # Let's assume we want to MINIMIZE entropy production (waste).
            # But the query asked for min_entropy >= target.
            # Let's refine: We want to find a state that had LOWER entropy rate than current.
            
            # Actually, let's flip it: We query for states with *lower* entropy.
            # But the Atlas query `min_entropy` filters for >=. 
            # We might need to update Atlas query logic or just use what we get.
            
            # For this PoV, let's assume we found a "Reference State"
            ref_entropy = best_past['entropy_rate']
            
            if ref_entropy < current['entropy_rate']:
                action = "OPTIMIZE"
                reason = f"Found lower entropy baseline ({ref_entropy:.4f}) from {best_past['source']}"
            else:
                action = "OBSERVE"
                reason = f"Current state is similar to baseline ({ref_entropy:.4f})"
                
        return {
            "timestamp": time.time(),
            "current_entropy": current['entropy_rate'],
            "action": action,
            "reason": reason,
            "ref_id": memory[0]['fossil_id'] if memory else None
        }

    def _log_decision(self, decision: Dict[str, Any]):
        with open(self.decision_log, 'a') as f:
            f.write(json.dumps(decision) + "\n")
        
        if decision['action'] == "OPTIMIZE":
            print(f"      ⚡ ACTION: {decision['action']} -> {decision['reason']}")

if __name__ == "__main__":
    agent = DarkFactoryLite()
    agent.run_loop()
