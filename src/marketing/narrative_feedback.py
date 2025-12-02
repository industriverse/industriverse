import random
from typing import Dict

class NarrativeFeedbackLoop:
    """
    The Ear.
    Closes the loop between market sentiment and evolution direction.
    """
    def ingest_market_signals(self) -> Dict[str, float]:
        print("👂 [Narrative Feedback] Listening to Market Signals...")
        
        # Mock Sentiment Analysis from "Social Media"
        signals = {
            "physics_grounding": 0.8, # Investors love physics
            "autonomous_agents": 0.9, # High hype
            "sustainability": 0.7,
            "cost_reduction": 0.95    # Clients love this
        }
        
        print(f"   Detected Sentiment: {signals}")
        return signals

    def adjust_evolution_plan(self, current_plan: Dict, signals: Dict[str, float]) -> Dict:
        print("⚖️ [Narrative Feedback] Adjusting Evolution Weights...")
        
        # Adjust weights based on sentiment
        new_plan = current_plan.copy()
        
        if signals.get("cost_reduction", 0) > 0.9:
            print("   -> Boosting 'Optimization' experiments due to client demand.")
            new_plan['weights']['optimization'] += 0.2
            
        if signals.get("autonomous_agents", 0) > 0.8:
            print("   -> Boosting 'Agent' experiments due to investor hype.")
            new_plan['weights']['agents'] += 0.1
            
        return new_plan

if __name__ == "__main__":
    # Test
    loop = NarrativeFeedbackLoop()
    signals = loop.ingest_market_signals()
    plan = {'weights': {'optimization': 0.5, 'agents': 0.5}}
    new_plan = loop.adjust_evolution_plan(plan, signals)
    print(f"Old Plan: {plan}")
    print(f"New Plan: {new_plan}")
