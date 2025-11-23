import asyncio
import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.core_ai_layer.t2l.service import TextToLoRAService
from src.core_ai_layer.t2l.schema import T2LRequest, LoRAStatus
from src.core_ai_layer.dgm.dgm_engine import DGMEngine

class TestT2LPipeline(unittest.IsolatedAsyncioTestCase):
    """
    Verify the Text-to-LoRA pipeline:
    DGM (Prompt) -> T2L Service -> LoRA Generator -> Metadata
    """
    
    async def asyncSetUp(self):
        self.t2l_service = TextToLoRAService()
        self.dgm = DGMEngine()

    async def test_dgm_to_lora_flow(self):
        print("\n--- Testing DGM -> T2L Flow ---")
        
        # 1. DGM Generates Prompt
        context = {"intent": "optimize lithium extraction", "constraints": ["low power"]}
        prompt = self.dgm.generate_t2l_prompt(context)
        print(f"DGM Generated Prompt: {prompt}")
        self.assertIn("lithium extraction", prompt)
        
        # 2. Request LoRA Creation
        request = T2LRequest(
            request_id="req-123",
            prompt=prompt,
            base_model="llama-3-8b"
        )
        
        response = await self.t2l_service.create_lora(request)
        print(f"T2L Response: {response.message}")
        
        self.assertEqual(response.status, LoRAStatus.READY)
        self.assertTrue(response.lora_id.startswith("lora-"))
        
        # 3. Verify Registry
        lora = self.t2l_service.get_lora(response.lora_id)
        self.assertIsNotNone(lora)
        self.assertEqual(lora.generation_prompt, prompt)
        print(f"✅ LoRA {lora.name} registered successfully.")

if __name__ == "__main__":
    unittest.main()
