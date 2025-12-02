from dataclasses import dataclass
from typing import List, Dict

@dataclass
class InferenceEvent:
    id: str
    description: str
    confidence: float
    implication: str

class CrossDomainInferenceEngine:
    """
    The Association Cortex.
    Correlates signals across Security, Energy, and Social domains to find hidden patterns.
    """
    
    def __init__(self):
        self.active_inferences = []
        
    def analyze_signals(self, signals: Dict[str, float]) -> List[InferenceEvent]:
        """
        Analyzes a set of cross-domain signals for correlations.
        Signals dict example: {"SPI_SENTIMENT": 0.2, "GRID_LOAD": 0.9, "THREAT_LEVEL": 0.1}
        """
        inferences = []
        
        # 1. Correlation: High Load + Low Sentiment (Boycott/Unrest Risk)
        if signals.get("GRID_LOAD", 0) > 0.8 and signals.get("SPI_SENTIMENT", 1) < 0.3:
            inferences.append(InferenceEvent(
                "INF_01", "Strain-Induced Unrest", 0.85, 
                "High Grid Load coinciding with Negative Sentiment suggests potential infrastructure protests."
            ))
            
        # 2. Correlation: High Threat + High Entropy (Cyber-Physical Attack)
        if signals.get("THREAT_LEVEL", 0) > 0.7 and signals.get("SYSTEM_ENTROPY", 0) > 0.7:
             inferences.append(InferenceEvent(
                "INF_02", "Cyber-Physical Destabilization", 0.92, 
                "Simultaneous Security Threats and System Entropy indicate coordinated attack."
            ))
            
        self.active_inferences = inferences
        if inferences:
            print(f"   🧠 [INFERENCE] Generated {len(inferences)} Cross-Domain Insights.")
            for inf in inferences:
                print(f"     -> {inf.description} ({inf.confidence*100}%)")
                
        return inferences

# --- Verification ---
if __name__ == "__main__":
    engine = CrossDomainInferenceEngine()
    
    # Scenario: Strained Grid & Angry Populace
    signals = {
        "SPI_SENTIMENT": 0.2,
        "GRID_LOAD": 0.95,
        "THREAT_LEVEL": 0.1
    }
    
    engine.analyze_signals(signals)
