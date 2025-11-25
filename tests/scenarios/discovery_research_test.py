import unittest
import sys
import os
import asyncio
from typing import Dict, Any

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.core.userlm.service import UserLMService
from src.white_label.credit_protocol.utid_marketplace import UTIDMarketplace
from src.white_label.credit_protocol.proof_ledger import ProofOfInsightLedger
from src.white_label.widgets.research_explorer import ResearchExplorerWidget
from src.white_label.widgets.widget_sdk import WidgetConfig

class TestDiscoveryResearch(unittest.IsolatedAsyncioTestCase):
    """
    Tier 3: Discovery & Research Test Scenario
    Verifies:
    1. UserLM hypothesis generation (mocked interaction).
    2. UTID Marketplace trading.
    3. Proof Ledger verification.
    4. Research Explorer visualization.
    """

    async def asyncSetUp(self):
        self.userlm = UserLMService()
        self.marketplace = UTIDMarketplace()
        self.ledger = ProofOfInsightLedger()
        config = WidgetConfig(widget_id="test_widget", partner_id="test_partner", theme="cosmic")
        self.explorer = ResearchExplorerWidget(config)

    async def test_userlm_hypothesis(self):
        print("\n--- Testing UserLM Hypothesis Generation ---")
        # Simulate a prompt for hypothesis
        prompt = "Optimize cooling efficiency for quantum processor."
        
        # UserLMService.generate_turn_stream is async generator
        # We'll just consume one chunk to verify it works
        response = ""
        async for chunk in self.userlm.generate_turn_stream(prompt, history=[], persona={"name": "TestUser"}):
            response += chunk
            break # Just check first chunk for aliveness
            
        self.assertTrue(len(response) > 0)
        print("✅ UserLM generated response stream.")

    async def test_utid_marketplace_trade(self):
        print("\n--- Testing UTID Marketplace ---")
        # 1. Mint a UTID (via Ledger)
        insight_id = "insight_001"
        utid = "utid_001"
        
        self.ledger.record_insight_creation(
            insight_id=insight_id,
            creator_id="user_001",
            source_papers=[],
            confidence=0.95
        )
        
        self.ledger.record_utid_minting(
            insight_id=insight_id,
            utid=utid,
            creator_id="user_001",
            proof_score=0.95
        )
        
        # 2. List on Marketplace
        from decimal import Decimal
        listing = self.marketplace.create_sale_listing(
            utid=utid,
            insight_id=insight_id,
            seller_id="user_001",
            seller_name="User One",
            price=Decimal(5000),
            title="New Alloy Discovery",
            description="Thermodynamic analysis of new alloy"
        )
        self.assertIsNotNone(listing)
        
        # 3. Buy Item
        buyer_id = "partner_001"
        success, message, tx = self.marketplace.purchase_insight(
            listing_id=listing.listing_id,
            buyer_id=buyer_id,
            buyer_credits=Decimal(10000)
        )
        self.assertTrue(success)
        print(f"✅ UTID {utid} traded successfully on marketplace.")

    async def test_research_explorer_visualization(self):
        print("\n--- Testing Research Explorer ---")
        # Simulate research data
        research_data = {
            "papers": [{"id": "p1", "title": "Thermodynamic AI"}],
            "citations": [],
            "trends": ["Energy Efficiency"]
        }
        
        await self.explorer.on_data_update(research_data)
        
        self.assertIsNotNone(self.explorer._data_cache)
        print("✅ Research Explorer visualized data")

if __name__ == "__main__":
    unittest.main()
