import time
from typing import Any
from src.datahub.value_vault import ValueVault
from src.research.research_controller import ResearchController

class CFRLogger:
    """
    Logs code evolution events to the Cognitive Fossil Record (CFR).
    Integrates with ValueVault for storage and ResearchController for analysis.
    """
    def __init__(self):
        self.value_vault = ValueVault()
        self.research_controller = ResearchController()

    def record(self, intent: Any, code: Any, feedback: Any) -> None:
        """
        Records a complete evolution step (Intent -> Code -> Feedback) to the CFR.
        """
        # Construct the fossil record
        fossil = {
            "timestamp": time.time(),
            "type": "CODE_EVOLUTION",
            "intent": intent,
            "code_snippet": code[:1000] if isinstance(code, str) else str(code)[:1000], # Truncate for summary
            "feedback": feedback,
            "verdict": feedback.get("verdict", "UNKNOWN")
        }

        # 1. Store in Value Vault (The "Fossil Layer")
        try:
            self.value_vault.store_secret(fossil)
        except Exception as e:
            print(f"⚠️ CFRLogger: Failed to store in ValueVault: {e}")

        # 2. Trigger Research Analysis (The "Paleontologist")
        # Only analyze if it was a successful mutation or interesting failure
        if feedback.get("verdict") == "APPROVE" or feedback.get("score", 0) > 0.8:
            try:
                self.research_controller.analyze_packet(fossil)
            except Exception as e:
                print(f"⚠️ CFRLogger: Failed to trigger ResearchController: {e}")
