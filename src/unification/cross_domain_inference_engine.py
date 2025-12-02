from typing import List, Dict
from src.unification.unified_substrate_model import USMField, USMSignal

class InferenceResult:
    def __init__(self, conclusion: str, confidence: float, evidence: List[str]):
        self.conclusion = conclusion
        self.confidence = confidence
        self.evidence = evidence

class CrossDomainInferenceEngine:
    """
    The Synapse.
    Finds hidden correlations between disparate fields (Security, Physics, Social).
    """
    
    def analyze(self, fields: Dict[str, USMField]) -> List[InferenceResult]:
        """
        Analyzes a set of fields for cross-domain patterns.
        """
        results = []
        print(f"   🧠 [CDIE] Analyzing {len(fields)} Fields...")
        
        # Extract Entropies
        security_entropy = fields.get("SECURITY", USMField("Empty")).get_average_entropy()
        thermal_entropy = fields.get("THERMAL", USMField("Empty")).get_average_entropy()
        social_entropy = fields.get("SOCIAL", USMField("Empty")).get_average_entropy()
        
        print(f"     -> Entropies: Sec={security_entropy:.2f}, Therm={thermal_entropy:.2f}, Soc={social_entropy:.2f}")
        
        # Rule 1: Cyber-Physical Attack (High Security + High Thermal)
        if security_entropy > 0.7 and thermal_entropy > 0.7:
            res = InferenceResult(
                conclusion="CYBER_PHYSICAL_ATTACK",
                confidence=0.95,
                evidence=["High Security Entropy", "High Thermal Entropy"]
            )
            results.append(res)
            print(f"     -> 🚨 INFERENCE: {res.conclusion} ({res.confidence*100:.0f}%)")
            
        # Rule 2: Market Manipulation (High Social + Low Thermal)
        # Lots of noise, but no physical work being done
        elif social_entropy > 0.8 and thermal_entropy < 0.2:
            res = InferenceResult(
                conclusion="MARKET_MANIPULATION",
                confidence=0.85,
                evidence=["High Social Entropy", "Low Physical Work"]
            )
            results.append(res)
            print(f"     -> ⚠️ INFERENCE: {res.conclusion} ({res.confidence*100:.0f}%)")
            
        return results

# --- Verification ---
if __name__ == "__main__":
    from src.unification.unified_substrate_model import USMSignal, USMEntropy
    
    # Mock Data
    sec_field = USMField("SECURITY")
    sec_field.add_signal(USMSignal(entropy=USMEntropy(0.9, "SECURITY")))
    
    therm_field = USMField("THERMAL")
    therm_field.add_signal(USMSignal(entropy=USMEntropy(0.8, "THERMAL")))
    
    engine = CrossDomainInferenceEngine()
    engine.analyze({"SECURITY": sec_field, "THERMAL": therm_field})
