from typing import Any, Dict
from src.core_ai_layer.ace.ace_service import ACEService
from src.scf.fertilization.cfr_logger import CFRLogger
from src.scf.roots.pulse_connector import PulseConnector

class ContextRoot:
    """
    The Anchor of the SCF.
    Aggregates context from ACE (Memory), CFR (History), and Pulse (Real-time).
    """
    def __init__(self):
        self.ace = ACEService()
        self.cfr = CFRLogger()
        self.pulse = PulseConnector()

    async def get_context_slab(self) -> Dict[str, Any]:
        """
        Produces a 'Context Slab' - the grounded reality for code generation.
        """
        # 1. Get Long-term Memory from ACE
        ace_context = self.ace.get_context()
        
        # 2. Get Real-time Telemetry from Pulse
        pulse_data = await self.pulse.fetch_latest()
        
        # 3. Merge
        slab = {
            "memory": ace_context,
            "telemetry": pulse_data,
            "timestamp": pulse_data.get("timestamp")
        }
        return slab
