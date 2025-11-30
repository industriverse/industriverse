import json

class FactoryPersonaManager:
    """
    Manages Factory Personalities (e.g., Aggressive, Conservative, Innovative).
    """
    def __init__(self):
        self.personas = {
            "FOXCONN_SPEED": {
                "description": "High Volume, Low Latency, Cost Sensitive",
                "emm_bias": "AGGRESSIVE",
                "bid_multiplier_base": 1.2,
                "risk_tolerance": 0.8
            },
            "TESLA_INNOVATION": {
                "description": "High Tech, High Value, Cost Insensitive",
                "emm_bias": "BALANCED",
                "bid_multiplier_base": 2.0,
                "risk_tolerance": 0.9
            },
            "DEFENSE_PRIME": {
                "description": "Zero Risk, High Security, Slow",
                "emm_bias": "CONSERVATIVE",
                "bid_multiplier_base": 0.8,
                "risk_tolerance": 0.1
            }
        }
        self.current_persona = "FOXCONN_SPEED"

    def set_persona(self, persona_id):
        if persona_id in self.personas:
            self.current_persona = persona_id
            print(f"[Persona] 🎭 Switched to: {persona_id}")
        else:
            print(f"[Persona] ❌ Unknown Persona: {persona_id}")

    def get_config(self):
        return self.personas[self.current_persona]
