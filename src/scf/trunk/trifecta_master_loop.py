from typing import Any
import asyncio
from src.scf.fertilization.cfr_logger import CFRLogger
from src.integrations.voice_engine import VoiceEngine
from src.security.uzkl_ledger import UnifiedZKLedger

class TrifectaMasterLoop:
    """
    The Central Conscious Loop of the Sovereign Code Foundry.
    Orchestrates the cycle: Observe -> Orient -> Decide -> Build -> Verify -> Reward -> Store.
    """
    def __init__(self, context_root: Any, intent_engine: Any, builder_engine: Any, reviewer: Any, deployer: Any):
        self.context_root = context_root
        self.intent_engine = intent_engine
        self.builder = builder_engine
        self.reviewer = reviewer
        self.deployer = deployer
        self.cfr = CFRLogger() # The Scribe
        self.voice = VoiceEngine() # The Voice
        self.ledger = UnifiedZKLedger() # The Conscience
        self.parameters = {}

    def set_parameters(self, params: dict):
        """
        Dynamically updates loop parameters (e.g., from Daemon Level).
        """
        self.parameters.update(params)

    async def cycle(self) -> Any:
        """
        Executes one full iteration of the conscious code generation loop.
        Includes Auto-Heal retry logic.
        """
        max_retries = 3
        attempt = 0
        
        while attempt < max_retries:
            try:
                # 1. Observe: Get Context Slab (Pulse + Memory)
                context_slab = await self.context_root.get_context_slab()
                
                # 2. Orient: Generate Intent based on Context
                intent = self.intent_engine.generate()
                spec = self.intent_engine.expand(intent)
                
                # Announce Intent
                self.voice.speak(f"I understand. Proceeding to {intent}.")
                
                # 3. Build: Generate Code (GenN)
                code = self.builder.build(spec)
                
                # 4. Verify: Review (PRIN + EBDM) & Simulate (TNN)
                review_result = self.reviewer.review(code)
                
                if review_result["verdict"] == "REJECT":
                    # Record failure to CFR
                    self.cfr.record(intent, code, review_result)
                    self.voice.speak("Optimization rejected. Refining approach.")
                    return {"status": "rejected", "reason": review_result["critique"]}

                # 5. Deploy
                result = self.deployer.deploy(code, context=context_slab)
                
                # 6. Fertilize (Record Success)
                self.cfr.record(intent, code, review_result)
                
                # 7. Conscience (Mint ZK Proof)
                proof = self.ledger.generate_proof(
                    domain="CODE_GENERATION",
                    data={"intent": intent, "code_hash": str(hash(code))},
                    metadata={"verdict": "APPROVE", "score": review_result.get("score")}
                )
                
                self.voice.speak("Deployment successful. Optimization active.")
                
                return {
                    "status": "deployed",
                    "result": result,
                    "intent": intent,
                    "review": review_result,
                    "proof_id": proof.id
                }
            except Exception as e:
                attempt += 1
                print(f"⚠️ Cycle Error (Attempt {attempt}/{max_retries}): {e}")
                if attempt >= max_retries:
                    return {"status": "error", "error": str(e)}
                await asyncio.sleep(0.1 * attempt) # Backoff
