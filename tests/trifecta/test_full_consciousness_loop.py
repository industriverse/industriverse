import asyncio
import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.core.userlm.service import UserLMService
from src.core_ai_layer.ace.reflection_engine import ReflectionEngine
from src.core_ai_layer.ace.playbook_manager import PlaybookManager
from src.core_ai_layer.ace.schema import UserIntent, IntentType

class TestFullConsciousnessLoop(unittest.IsolatedAsyncioTestCase):
    """
    Verify the Full Consciousness Loop:
    UserLM (Intent) -> ACE (Context) -> TUMIX (Consensus) -> Reflection
    """
    
    async def asyncSetUp(self):
        self.userlm = UserLMService()
        self.playbook_manager = PlaybookManager()
        self.reflection_engine = ReflectionEngine(self.playbook_manager)

    async def test_full_loop_execution(self):
        print("\n--- Testing Full Consciousness Loop ---")
        
        # 1. UserLM Generates Turn (Triggering ACE & TUMIX)
        intent = "Create a new optimization strategy for lithium."
        persona = {"name": "System Architect"}
        
        print(f"User Intent: {intent}")
        
        response = ""
        async for chunk in self.userlm.generate_turn_stream(intent, [], persona):
            response += chunk
            
        print(f"UserLM Response: {response}")
        
        # Verify TUMIX involvement in response
        self.assertIn("TUMIX", response)
        print("✅ TUMIX validated the intent.")
        
        # 2. Simulate Reflection on the Outcome
        user_intent = UserIntent(
            intent_id="intent-loop-001",
            raw_input=intent,
            intent_type=IntentType.CREATION,
            goal="Optimize lithium"
        )
        
        reflection = self.reflection_engine.reflect(
            intent=user_intent,
            outcome="success",
            notes="TUMIX approved, execution successful.",
            consensus_score=0.9
        )
        
        self.assertIn("Consensus: 0.9", reflection.reflection_notes)
        print("✅ ACE reflected on the outcome with consensus score.")

if __name__ == "__main__":
    unittest.main()
