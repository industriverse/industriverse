import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.unification.unified_substrate_model import USMField, USMSignal, USMEntropy
from src.unification.cross_domain_inference_engine import CrossDomainInferenceEngine

def verify_usm():
    print("⚛️ INITIALIZING UNIFIED SUBSTRATE MODEL SIMULATION...")
    
    engine = CrossDomainInferenceEngine()
    
    # --- Scenario 1: Cyber-Physical Attack ---
    print("\n--- Scenario 1: Stuxnet-style Event ---")
    sec_field = USMField("SECURITY")
    sec_field.add_signal(USMSignal(entropy=USMEntropy(0.95, "SECURITY"))) # Intrusion
    
    therm_field = USMField("THERMAL")
    therm_field.add_signal(USMSignal(entropy=USMEntropy(0.85, "THERMAL"))) # Overheating
    
    results = engine.analyze({"SECURITY": sec_field, "THERMAL": therm_field})
    
    if any(r.conclusion == "CYBER_PHYSICAL_ATTACK" for r in results):
        print("✅ Correctly inferred Cyber-Physical Attack.")
    else:
        print("❌ Failed to infer attack.")
        sys.exit(1)
        
    # --- Scenario 2: Pump and Dump ---
    print("\n--- Scenario 2: Social Engineering Event ---")
    social_field = USMField("SOCIAL")
    social_field.add_signal(USMSignal(entropy=USMEntropy(0.9, "SOCIAL"))) # Hype
    
    therm_field_quiet = USMField("THERMAL")
    therm_field_quiet.add_signal(USMSignal(entropy=USMEntropy(0.1, "THERMAL"))) # No production
    
    results = engine.analyze({"SOCIAL": social_field, "THERMAL": therm_field_quiet})
    
    if any(r.conclusion == "MARKET_MANIPULATION" for r in results):
        print("✅ Correctly inferred Market Manipulation.")
    else:
        print("❌ Failed to infer manipulation.")
        sys.exit(1)
        
    print("\n✅ USM Verification Complete. The Organism has Insight.")

if __name__ == "__main__":
    verify_usm()
