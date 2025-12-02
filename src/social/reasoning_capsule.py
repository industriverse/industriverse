from dataclasses import dataclass, field
from typing import List, Dict, Any
import uuid
import time

# Mocking Trifecta Components for the Capsule
class MockUserLM:
    def narrate(self, event: str) -> str:
        return f"UserLM: Analyzing '{event}'... Here is the narrative context."

class MockRND1:
    def optimize(self, goal: str) -> str:
        return f"RND1: Optimization path found for '{goal}'. Efficiency +15%."

class MockACE:
    def log_lesson(self, outcome: str):
        pass

@dataclass
class CapsuleUpdate:
    timestamp: float
    message: str
    type: str # NARRATIVE, PROOF, EXPERIMENT
    data: Dict[str, Any]

class ReasoningCapsule:
    """
    The Atomic Unit of the Social Industriverse.
    Encapsulates a Topic, a Team of Agents, and a Reasoning State.
    """
    
    def __init__(self, topic: str, owner_id: str):
        self.id = str(uuid.uuid4())
        self.topic = topic
        self.owner_id = owner_id
        self.subscribers: List[str] = []
        self.updates: List[CapsuleUpdate] = []
        self.state = "INITIALIZING"
        
        # The Trifecta Team
        self.user_lm = MockUserLM()
        self.rnd1 = MockRND1()
        self.ace = MockACE()
        
        print(f"   💊 [CAPSULE] Created: '{self.topic}' (Owner: {self.owner_id})")
        
    def add_subscriber(self, user_id: str):
        self.subscribers.append(user_id)
        print(f"     -> New Subscriber: {user_id}")
        
    def run_cycle(self):
        """
        Simulates one 'tick' of reasoning.
        """
        print(f"   ⚙️ [CAPSULE] Running Cycle for '{self.topic}'...")
        
        # 1. RND1 Optimizes
        opt_result = self.rnd1.optimize(self.topic)
        self._emit_update(opt_result, "EXPERIMENT", {"efficiency": 0.85})
        
        # 2. UserLM Narrates
        narrative = self.user_lm.narrate(opt_result)
        self._emit_update(narrative, "NARRATIVE", {})
        
        # 3. ACE Learns
        self.ace.log_lesson("Cycle Complete")
        
    def _emit_update(self, message: str, msg_type: str, data: Dict[str, Any]):
        update = CapsuleUpdate(time.time(), message, msg_type, data)
        self.updates.append(update)
        # In a real system, this would push to a WebSocket/Event Bus
        print(f"     -> 📢 [FEED] {msg_type}: {message}")

# --- Verification ---
if __name__ == "__main__":
    cap = ReasoningCapsule("Sustainable Hydrogen", "User_001")
    cap.add_subscriber("Investor_A")
    cap.run_cycle()
