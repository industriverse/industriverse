"""
Directive 05: Agent Behavior
Grid Immunity Agent: Detects anomalies and balances load.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class GridAgent:
    def __init__(self, manifest):
        self.manifest = manifest
        self.nominal_freq = 60.0
        
    def observe(self, sensor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Directive 05: Observation Function"""
        return {
            "frequency": sensor_data.get("frequency", 60.0),
            "voltage": sensor_data.get("voltage", 1.0),
            "load_demand": sensor_data.get("load_demand", 0.0)
        }

    def policy(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """Directive 05: Policy Function"""
        freq = observation.get("frequency", 60.0)
        
        if abs(freq - self.nominal_freq) > 0.1:
            # Frequency deviation detected
            action = {
                "type": "dispatch_reserves",
                "amount_mw": (self.nominal_freq - freq) * 100, # Droop control
                "reason": f"Frequency deviation: {freq}Hz"
            }
        else:
            action = {
                "type": "monitor",
                "reason": "Grid stable"
            }
            
        logger.info(f"Grid Agent Action: {action['reason']}")
        return action
