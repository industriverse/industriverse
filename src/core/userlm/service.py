import asyncio
from typing import AsyncGenerator, Optional
from datetime import datetime, timezone

from src.core_ai_layer.ace.playbook_manager import PlaybookManager
from src.core_ai_layer.ace.memory_logger import ACEMemoryLogger
from src.core_ai_layer.tumix.service import TUMIXService
from src.proof_core.integrity_layer import record_reasoning_edge

class UserLMService:
    """
    Service for the User Language Model (UserLM).
    Simulates the "User" in the loop.
    Supports streaming responses and timeouts.
    Enhanced with ACE (Agentic Context Engineering) and TUMIX (Consensus).
    """
    def __init__(self, timeout_seconds: float = 30.0):
        self.timeout_seconds = timeout_seconds
        self.playbook_manager = PlaybookManager()
        self.memory_logger = ACEMemoryLogger()
        self.tumix_service = TUMIXService()

    async def generate_turn_stream(self, intent: str, history: list, persona: dict, utid: str = "UTID:REAL:unknown") -> AsyncGenerator[str, None]:
        """
        Generates a User turn, streaming the output token by token.
        Uses ACE Playbooks to inform the response.
        Uses TUMIX to validate critical intents.
        """
        # 1. Fetch Context Playbook
        playbook = self.playbook_manager.get_playbook("general")
        strategies = ", ".join(playbook.strategies)
        
        # 2. Log Input
        await self.memory_logger.log_event("user_turn_start", {
            "intent": intent, 
            "persona": persona.get("name"),
            "active_strategies": strategies
        })

        # 3. TUMIX Consensus Check (Simulated for critical intents)
        tumix_note = ""
        if "create" in intent.lower() or "optimize" in intent.lower():
            consensus = await self.tumix_service.request_consensus(
                intent_id="temp-id",
                proposal=intent,
                context={"utid": utid}
            )
            if consensus.final_decision == "rejected":
                tumix_note = f"[TUMIX WARNING: Proposal rejected due to {consensus.synthesis}]"
            else:
                tumix_note = f"[TUMIX APPROVED: Score {consensus.truth_score:.2f}]"

        # Simulate processing delay
        await asyncio.sleep(0.5)
        
        # Mock response generation based on intent and ACE context
        response_text = (
            f"Based on your intent '{intent}' and my persona '{persona.get('name', 'User')}', "
            f"I am applying these strategies: [{strategies}]. "
            f"{tumix_note} "
            f"I need you to run a simulation."
        )
        
        tokens = response_text.split(" ")
        
        start_time = datetime.now(timezone.utc)
        
        try:
            for token in tokens:
                # Check timeout
                if (datetime.now(timezone.utc) - start_time).total_seconds() > self.timeout_seconds:
                    yield " [TIMEOUT]"
                    break
                
                yield token + " "
                await asyncio.sleep(0.1) # Simulate token generation latency
                
            # 3. Log Output
            await self.memory_logger.log_event("user_turn_end", {"response_length": len(response_text)})
            # Emit proof edge
            await record_reasoning_edge(
                utid=utid,
                domain="userlm_turn",
                node_id="userlm_service",
                inputs={"intent": intent, "persona": persona},
                outputs={"response_length": len(response_text), "tumix": tumix_note},
                metadata={"status": "completed"},
            )
                
        except Exception as e:
            yield f" [ERROR: {str(e)}]"

    async def generate_turn(self, intent: str, history: list, persona: dict) -> str:
        """
        Non-streaming wrapper for generate_turn_stream.
        """
        full_response = ""
        async for token in self.generate_turn_stream(intent, history, persona):
            full_response += token
        return full_response.strip()
