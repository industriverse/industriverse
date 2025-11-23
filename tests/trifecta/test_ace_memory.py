import asyncio
import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from datetime import datetime
from src.core_ai_layer.ace.memory_logger import ACEMemoryLogger
from src.core_ai_layer.ace.playbook_manager import PlaybookManager
from src.core_ai_layer.ace.reflection_engine import ReflectionEngine
from src.core_ai_layer.ace.schema import UserIntent, IntentType

class TestACEMemory(unittest.IsolatedAsyncioTestCase):
    """
    Verify ACE Memory and Reflection:
    Logging -> Reflection -> Playbook Update
    """
    
    async def asyncSetUp(self):
        self.logger = ACEMemoryLogger()
        self.playbook_manager = PlaybookManager()
        self.reflection_engine = ReflectionEngine(self.playbook_manager)

    async def test_logging_and_reflection(self):
        print("\n--- Testing ACE Memory & Reflection ---")
        
        # 1. Log Event
        await self.logger.log_event("test_event", {"data": "foo"})
        logs = self.logger.get_recent_logs()
        self.assertEqual(len(logs), 1)
        print("✅ Event logged successfully.")
        
        # 2. Simulate Reflection on Failure
        intent = UserIntent(
            intent_id="intent-fail-001",
            raw_input="Do unsafe thing",
            intent_type=IntentType.COMMAND,
            goal="Break system"
        )
        
        reflection = self.reflection_engine.reflect(
            intent=intent,
            outcome="failure",
            notes="Attempted unsafe operation"
        )
        
        self.assertEqual(reflection.outcome, "failure")
        
        # 3. Verify Playbook Update
        playbook = self.playbook_manager.get_playbook("default")
        self.assertTrue(any("intent-fail-001" in s for s in playbook.strategies))
        print(f"✅ Playbook updated with anti-pattern: {playbook.strategies[-1]}")

if __name__ == "__main__":
    unittest.main()
