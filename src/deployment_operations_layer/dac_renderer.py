import logging
import json
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

class DACRenderer:
    """
    Renders the internal state of a Sovereign DAC.
    Can output to Console, JSON, or (in future) a Web Interface/AR Overlay.
    """
    def __init__(self, dac_id: str):
        self.dac_id = dac_id
        logger.info(f"DACRenderer initialized for {dac_id}")

    def render_state(self, state: Dict[str, Any], format: str = "console"):
        """
        Render the current state.
        """
        if format == "console":
            self._render_console(state)
        elif format == "json":
            return self._render_json(state)
        else:
            logger.warning(f"Unknown render format: {format}")

    def _render_console(self, state: Dict[str, Any]):
        """
        Print a futuristic status block to the console.
        """
        timestamp = datetime.now().isoformat()
        status = state.get("status", "UNKNOWN")
        energy = state.get("energy_level", 0.0)
        utid = state.get("utid", "N/A")
        
        print(f"\n╔════════════════════════════════════════════════════╗")
        print(f"║ SOVEREIGN DAC: {self.dac_id:<31} ║")
        print(f"╠════════════════════════════════════════════════════╣")
        print(f"║ TIME   : {timestamp:<33} ║")
        print(f"║ UTID   : {utid:<33} ║")
        print(f"║ STATUS : {status:<33} ║")
        print(f"║ EXERGY : {energy:<33.2f} ║")
        print(f"╠════════════════════════════════════════════════════╣")
        
        if "active_loop" in state and state["active_loop"] is not None:
            loop = state["active_loop"]
            print(f"║ ACTIVE LOOP: {loop.get('loop_id', 'N/A')[:28]:<30} ║")
            print(f"║ > STAGE: {loop.get('stage', 'PROCESSING'):<32} ║")
            if "bitnet_advice" in loop:
                print(f"║ > BITNET: {loop['bitnet_advice'][:31]:<31} ║")
                
        print(f"╚════════════════════════════════════════════════════╝\n")

    def _render_json(self, state: Dict[str, Any]) -> str:
        return json.dumps(state, indent=2)
