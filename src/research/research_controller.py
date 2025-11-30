import time
import json
import os
import random
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("ResearchController")

class ResearchController:
    """
    The Brain of the Autonomous Research Engine.
    Monitors data streams for 'Research-Worthy' events.
    """
    def __init__(self, output_dir="data/research/raw"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.active = False
        self.entropy_threshold = 0.3 # Trigger if entropy drops below this
        self.anomaly_threshold = 0.9 # Trigger if safety score drops below this (high risk)

    def determine_mastery_stage(self, entropy: float, confidence: float) -> str:
        """
        Classifies the event into the Framework of Mastery (Bible).
        """
        if confidence < 0.5:
            return "STAGE_1_OBSERVATION" # Still learning, low confidence
        elif confidence < 0.8:
            return "STAGE_2_IMITATION" # Simulating, medium confidence
        elif entropy < self.entropy_threshold:
            return "STAGE_3_INNOVATION" # High confidence + Low Entropy = Innovation
        else:
            return "STAGE_4_MASTERY" # High confidence, stable state

    def set_active(self, active: bool):
        self.active = active
        state = "ENABLED" if active else "DISABLED"
        logger.info(f"🔬 Research Mode {state}")

    def analyze_packet(self, packet: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analyzes a data packet. If interesting, returns a Research Snapshot.
        """
        if not self.active:
            return None

        # Extract Metrics
        energy_state = packet.get("energy_state", {})
        entropy = energy_state.get("entropy", 1.0)
        payload = packet.get("payload", {})
        safety_score = payload.get("safety_score", 1.0)
        confidence = payload.get("confidence", 0.5) # Default to 0.5 if missing
        source = packet.get("source", "UNKNOWN")

        # 1. Determine Mastery Stage
        mastery_stage = self.determine_mastery_stage(entropy, confidence)

        # 2. Detection Logic
        event_type = None
        hypothesis = None

        # Case A: Significant Entropy Reduction (Optimization Discovery)
        if entropy < self.entropy_threshold:
            event_type = "ENTROPY_MINIMIZATION"
            hypothesis = f"System found low-entropy state ({entropy:.4f}) in {source}."

        # Case B: High-Risk Anomaly (Safety Research)
        elif safety_score < self.anomaly_threshold:
            event_type = "ANOMALY_DETECTED"
            hypothesis = f"Safety degradation ({safety_score:.4f}) detected in {source}. Investigation required."

        # 2. Snapshot Generation
        if event_type:
            logger.info(f"💡 Research Event Detected: {event_type}")
            snapshot = {
                "timestamp": time.time(),
                "event_id": f"res-{int(time.time()*1000)}",
                "event_type": event_type,
                "mastery_stage": mastery_stage,
                "hypothesis": hypothesis,
                "source_packet": packet,
                "metrics": {
                    "entropy": entropy,
                    "safety_score": safety_score
                }
            }
            self.save_snapshot(snapshot)
            return snapshot
        
        return None

    def save_snapshot(self, snapshot: Dict[str, Any]):
        filename = f"{snapshot['event_id']}_{snapshot['event_type']}.json"
        path = os.path.join(self.output_dir, filename)
        try:
            with open(path, 'w') as f:
                json.dump(snapshot, f, indent=2)
            logger.info(f"   📄 Saved Research Snapshot: {filename}")
        except Exception as e:
            logger.error(f"Failed to save snapshot: {e}")
