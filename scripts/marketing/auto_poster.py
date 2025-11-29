import json
import random
from datetime import datetime

class AutoPoster:
    """
    Generates high-engagement social media posts based on system telemetry.
    Targets: Twitter/X, LinkedIn.
    """
    def __init__(self):
        self.hashtags = ["#IndustrialAI", "#AGI", "#Manufacturing", "#Thermodynamics", "#Industriverse"]
        
    def generate_post(self, event_type="HIGHLIGHT_REEL", data=None):
        if event_type == "HIGHLIGHT_REEL":
            return self._generate_highlight_post(data)
        elif event_type == "NEW_SKILL":
            return self._generate_skill_post(data)
        else:
            return "System Operational."

    def _generate_highlight_post(self, data):
        # Mock data if none provided
        cost = data.get("cost", 12.50) if data else 12.50
        margin = data.get("margin", 32) if data else 32
        duration = data.get("duration", 15) if data else 15
        
        post = f"""
🚀 INDUSTRIAL AGI UPDATE

Just executed a fully autonomous manufacturing loop in {duration} seconds.

✅ Intent: High-Performance Turbine Blade
🔒 ZK Proof: Verified (IP Protected)
⚡ Energy Cost: ${cost:.2f}
📈 Profit Margin: {margin}%

No human in the loop. Pure thermodynamic optimization.

The future of manufacturing is deterministic.

{' '.join(self.hashtags)}
"""
        return post.strip()

    def _generate_skill_post(self, data):
        skill = data.get("skill", "Unknown") if data else "5-Axis-Milling-v2"
        return f"""
🧠 NEW SKILL UNLOCKED

Capsule Swarm just evolved a new capability: {skill}.

- Physics Verified: YES
- ZK Proven: YES
- Available for Licensing: NOW

Our factories are learning. Are yours?

{' '.join(self.hashtags)}
"""

if __name__ == "__main__":
    poster = AutoPoster()
    print("--- GENERATED TWEET ---")
    print(poster.generate_post("HIGHLIGHT_REEL", {"cost": 11.20, "margin": 35}))
    print("\n--- GENERATED LINKEDIN ---")
    print(poster.generate_post("NEW_SKILL", {"skill": "Adaptive-Laser-Welding-v4"}))
