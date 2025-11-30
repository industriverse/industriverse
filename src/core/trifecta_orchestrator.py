import os
import json
import time
import logging
import random
from typing import Dict, Any, Optional

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TrifectaOrchestrator")

class TrifectaOrchestrator:
    """
    The Brain of Brains.
    Orchestrates the Daemon based on a specific Persona (UserLM/ACE).
    """
    def __init__(self, persona_id: str, config_dir="config/trifecta_personas"):
        self.persona_id = persona_id
        self.config_dir = config_dir
        self.persona = self.load_persona(persona_id)
        self.control_file = "data/datahub/control.json"
        self.research_dir = "data/research/raw"
        self.active = True

    def load_persona(self, persona_id: str) -> Dict[str, Any]:
        path = os.path.join(self.config_dir, f"{persona_id}.json")
        try:
            with open(path, 'r') as f:
                persona = json.load(f)
            logger.info(f"🎭 Loaded Persona: {persona['name']} ({persona['role']})")
            return persona
        except FileNotFoundError:
            logger.error(f"Persona {persona_id} not found.")
            return {}

    def send_daemon_command(self, command: str, payload: Dict[str, Any] = None):
        """
        Sends a command to the Collector Daemon via IPC.
        """
        cmd_data = {
            "command": command,
            "payload": payload or {},
            "timestamp": time.time(),
            "issuer": f"Trifecta-{self.persona_id}"
        }
        try:
            with open(self.control_file, 'w') as f:
                json.dump(cmd_data, f)
            logger.info(f"📡 Sent Command: {command}")
        except Exception as e:
            logger.error(f"Failed to send command: {e}")

    def analyze_context(self):
        """
        Reads the latest research snapshots to build 'ACE Context'.
        Decides on actions based on Persona goals.
        """
        # Get latest snapshot
        try:
            files = sorted(os.listdir(self.research_dir), reverse=True)
            if not files:
                return
            
            latest_file = files[0]
            if not latest_file.endswith(".json"):
                return

            with open(os.path.join(self.research_dir, latest_file), 'r') as f:
                snapshot = json.load(f)
            
            self.make_decision(snapshot)
            
        except Exception as e:
            logger.error(f"Context analysis failed: {e}")

    def make_decision(self, snapshot: Dict[str, Any]):
        """
        The Core Logic: Persona-driven decision making.
        """
        metrics = snapshot.get("metrics", {})
        entropy = float(metrics.get("entropy", 1.0))
        safety = float(metrics.get("safety_score", 1.0))
        
        thresholds = self.persona.get("thresholds", {})
        strategy = self.persona.get("strategy", "BALANCED")

        logger.info(f"🧠 Analyzing Snapshot: Entropy={entropy:.2f}, Safety={safety:.2f}")

        # Strategy: CONSERVATIVE_PROTECTION (Safety Officer)
        if strategy == "CONSERVATIVE_PROTECTION":
            if safety < thresholds.get("safety_tolerance", 0.99):
                logger.warning(f"🚨 SAFETY VIOLATION ({safety} < {thresholds['safety_tolerance']}). HALTING DAEMON.")
                self.send_daemon_command("PAUSE")
                self.send_daemon_command("RESEARCH_MODE", {"active": False})
                return

        # Strategy: AGGRESSIVE_OPTIMIZATION (Research Lead)
        elif strategy == "AGGRESSIVE_OPTIMIZATION":
            if entropy > thresholds.get("entropy_target", 0.2):
                logger.info(f"⚡ Entropy too high ({entropy}). Increasing sampling rate.")
                self.send_daemon_command("UPDATE_CONFIG", {"sampling_rate": 0.01}) # Faster sampling
            
            if safety > 0.8: # If safe enough, push harder
                 self.send_daemon_command("RESEARCH_MODE", {"active": True})

        # Strategy: COST_MINIMIZATION (Financial Auditor)
        elif strategy == "COST_MINIMIZATION":
            if entropy < 0.5: # Good enough
                logger.info("💰 Efficiency target met. Reducing sampling to save energy.")
                self.send_daemon_command("UPDATE_CONFIG", {"sampling_rate": 0.5}) # Slower sampling

    def run_loop(self):
        logger.info("🚀 Trifecta Orchestrator Started.")
        try:
            while self.active:
                self.analyze_context()
                time.sleep(2) # Orchestrate every 2 seconds
        except KeyboardInterrupt:
            logger.info("Orchestrator Stopped.")
