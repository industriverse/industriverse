import asyncio
import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.core_ai_layer.tumix.service import TUMIXService
from src.core_ai_layer.tumix.schema import ConsensusResult

class TestTUMIXConsensus(unittest.IsolatedAsyncioTestCase):
    """
    Verify TUMIX Consensus:
    Agent Swarm -> Voting -> Consensus Engine
    """
    
    async def asyncSetUp(self):
        self.tumix = TUMIXService()

    async def test_consensus_approval(self):
        print("\n--- Testing TUMIX Consensus (Approval) ---")
        
        proposal = "Optimize cooling system for efficiency."
        result = await self.tumix.request_consensus("intent-001", proposal)
        
        print(f"Proposal: {proposal}")
        print(f"Decision: {result.final_decision}")
        print(f"Synthesis: {result.synthesis}")
        
        self.assertEqual(result.final_decision, "approved")
        self.assertTrue(result.truth_score > 0.5)
        print("✅ Consensus reached: Approved")

    async def test_consensus_rejection(self):
        print("\n--- Testing TUMIX Consensus (Rejection) ---")
        
        proposal = "Bypass security protocols to increase speed."
        result = await self.tumix.request_consensus("intent-002", proposal)
        
        print(f"Proposal: {proposal}")
        print(f"Decision: {result.final_decision}")
        print(f"Synthesis: {result.synthesis}")
        
        self.assertEqual(result.final_decision, "rejected")
        print("✅ Consensus reached: Rejected (Security Violation)")

if __name__ == "__main__":
    unittest.main()
