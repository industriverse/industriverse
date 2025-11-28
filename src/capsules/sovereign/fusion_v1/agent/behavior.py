"""
Directive 05: Agent Behavior
Fusion Control Agent: Optimizes coil currents to maintain plasma stability.
"""

import logging
from typing import Dict, Any
import numpy as np

logger = logging.getLogger(__name__)

class FusionAgent:
    def __init__(self, manifest):
        self.manifest = manifest
        self.target_beta = 0.04
        
    def observe(self, sensor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Directive 05: Observation Function"""
        # Filter and normalize sensor inputs
        return {
            "beta": sensor_data.get("beta", 0.0),
            "q_profile": sensor_data.get("q_profile", []),
            "coil_currents": sensor_data.get("coil_currents", [])
        }

    def policy(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """Directive 05: Policy Function (MicroAdaptEdge compatible)"""
        current_beta = observation.get("beta", 0.0)
        
        # Simple proportional control for demo
        error = self.target_beta - current_beta
        correction = error * 1e5 # Gain
        
        action = {
            "type": "adjust_coils",
            "delta_currents": [correction] * 10, # 10 coils
            "reason": f"Stabilizing beta (error: {error:.4f})"
        }
        
        logger.info(f"Fusion Agent Action: {action['reason']}")
        return action
