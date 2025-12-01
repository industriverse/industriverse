import random

class Oracle:
    """
    The First-Principles Knowledge Base.
    Uses a simulated Vector DB to cite Physics Laws for industrial phenomena.
    """
    def __init__(self):
        # Simulated Vector Store (Embeddings would go here)
        self.knowledge_base = {
            "thermal_expansion": {
                "principle": "Linear Thermal Expansion",
                "equation": "ΔL = αLΔT",
                "citation": "Shigley's Mechanical Engineering Design, Ch. 3",
                "explanation": "Materials expand when heated due to increased molecular vibration."
            },
            "friction_wear": {
                "principle": "Tribological Wear (Archard's Equation)",
                "equation": "V = K * (W * L) / H",
                "citation": "Tribology Handbook, Section 4.2",
                "explanation": "Material removal rate is proportional to normal load and sliding distance."
            },
            "vibration_resonance": {
                "principle": "Mechanical Resonance",
                "equation": "f = (1/2π) * √(k/m)",
                "citation": "Vibration Analysis Fundamentals, Ch. 2",
                "explanation": "System amplitude maximizes when forcing frequency matches natural frequency."
            },
            "entropy_increase": {
                "principle": "Second Law of Thermodynamics",
                "equation": "ΔS ≥ 0",
                "citation": "Thermodynamics: An Engineering Approach, Ch. 7",
                "explanation": "Entropy of an isolated system always increases over time (degradation)."
            }
        }

    def query(self, context_string):
        """
        Returns the most relevant physics principle for the given context.
        """
        context_lower = context_string.lower()
        
        # Semantic Matching Logic (Simulated)
        if "heat" in context_lower or "temp" in context_lower or "expand" in context_lower:
            return self.knowledge_base["thermal_expansion"]
        elif "grind" in context_lower or "wear" in context_lower or "friction" in context_lower:
            return self.knowledge_base["friction_wear"]
        elif "shake" in context_lower or "vibrat" in context_lower or "oscillat" in context_lower:
            return self.knowledge_base["vibration_resonance"]
        elif "decay" in context_lower or "rot" in context_lower or "chaos" in context_lower or "entropy" in context_lower:
            return self.knowledge_base["entropy_increase"]
        else:
            return {
                "principle": "Unknown Phenomenon",
                "equation": "N/A",
                "citation": "Empeiria Haus Research Database",
                "explanation": "Insufficient data to correlate with known physical laws."
            }

if __name__ == "__main__":
    oracle = Oracle()
    print(oracle.query("Why is the spindle getting longer when hot?"))
    print(oracle.query("The machine is shaking violently."))
