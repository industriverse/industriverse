import logging
import json
from datetime import datetime
from typing import Dict, Any
from src.bridge_api.event_bus import GlobalEventBus

logger = logging.getLogger(__name__)

class BehavioralTracker:
    """
    Tracks user behavior and system events for ASAL (Automated Sovereign Alignment Layer).
    
    Logs events to a structured audit trail for Week 9 integration.
    """
    
    def __init__(self, log_path: str = "data/asal_behavior_log.jsonl"):
        self.log_path = log_path
        
        # Subscribe to relevant events
        GlobalEventBus.subscribe(self._on_event)
        
        logger.info("BehavioralTracker initialized - Watching for ASAL signals")

    async def _on_event(self, event: Dict[str, Any]):
        """Handle global events"""
        event_type = event.get("type") or event.get("event_type")
        
        # Handle Enum
        if hasattr(event_type, "value"):
            event_type = event_type.value
            
        if not event_type:
            return
        
        # Filter for governance-relevant events
        relevant_types = [
            "snapshot_created",
            "remix_committed",
            "utid_minted",
            "deployment_complete",
            "proof_generated",
            "capsule_update"
        ]
        
        if event_type in relevant_types or event_type.startswith("remix_"):
            await self._log_behavior(event)

    async def _log_behavior(self, event: Dict[str, Any]):
        """Log behavior to ASAL audit trail"""
        try:
            event_type = event.get("type") or event.get("event_type")
            if hasattr(event_type, "value"):
                event_type = event_type.value

            entry = {
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "actor": event.get("user_id") or event.get("committed_by") or "system",
                "context": {
                    "utid": event.get("utid"),
                    "proof_id": event.get("proof_id") or event.get("proof_ref"),
                    "snapshot_id": event.get("snapshot_id"),
                    "deployment_id": event.get("deployment_id")
                },
                "asal_vector": self._calculate_asal_vector(event)
            }
            
            # Append to log file
            with open(self.log_path, "a") as f:
                f.write(json.dumps(entry) + "\n")
                
            logger.debug(f"ASAL Logged: {event.get('type')}")
            
        except Exception as e:
            logger.error(f"Failed to log behavior: {e}")

    def _calculate_asal_vector(self, event: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate alignment vector for ASAL.
        
        This is a stub for the Week 9 AI governance model.
        """
        # Placeholder logic
        vector = {
            "coherence": 0.5,
            "safety": 0.5,
            "novelty": 0.5
        }
        
        if event.get("type") == "proof_generated":
            vector["coherence"] = 0.9
            vector["safety"] = 0.8
            
        if event.get("type") == "remix_committed":
            vector["novelty"] = 0.9
            
        return vector

# Global instance
_tracker = None

def get_behavioral_tracker() -> BehavioralTracker:
    global _tracker
    if _tracker is None:
        _tracker = BehavioralTracker()
    return _tracker
