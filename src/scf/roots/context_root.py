import asyncio
from typing import Dict, Any
from src.scf.roots.pulse_connector import PulseConnector
from src.scf.roots.memory_stem import MemoryStem
from src.core_ai_layer.ace.ace_service import ACEService, ACERequest

class ContextRoot:
    """
    The Anchor of the SCF.
    Absorbs real-time data (Pulse) and historical wisdom (Memory) to form the Context Slab.
    Now powered by ACE (Agentic Context Engineering).
    """
    def __init__(self):
        self.pulse = PulseConnector()
        self.memory = MemoryStem()
        self.ace = ACEService() # Real ACE Service

    async def get_context_slab(self) -> Dict[str, Any]:
        """
        Synthesizes the Context Slab using ACE.
        """
        # 1. Gather Raw Inputs
        telemetry = await self.pulse.fetch_latest()
        memories = self.memory.recall(query="current_state")
        
        # 2. Construct ACE Request
        # In a real scenario, 'intent' might come from an upstream trigger, 
        # but here we are forming the *base* context for intent generation.
        request = ACERequest(
            request_id="scf_context_gen",
            intent="Synthesize Operational Context",
            context=[str(telemetry), str(memories)]
        )
        
        # 3. Process with ACE
        try:
            ace_response = await self.ace.process_request(request)
            reflection = ace_response.reflection
            
            return {
                "telemetry": telemetry,
                "memory": memories,
                "ace_reflection": reflection.dict() if reflection else {},
                "timestamp": telemetry.get("timestamp")
            }
        except Exception as e:
            print(f"⚠️ ContextRoot: ACE processing failed, falling back to raw data: {e}")
            return {
                "telemetry": telemetry,
                "memory": memories,
                "error": str(e)
            }
