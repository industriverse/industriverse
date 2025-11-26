import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from src.core_ai_layer.semantic_translator import NarrativeEngine

def run():
    print("\n" + "="*60)
    print(" DEMO 27: INCIDENT NARRATIVE GENERATOR")
    print("="*60 + "\n")

    narrator = NarrativeEngine()

    print("--- Scenario: Critical Failure ---")
    tags = [
        {"tag": "Rapid_Flux", "severity": "CRITICAL"},
        {"tag": "High_Disorder", "severity": "WARNING"}
    ]
    
    report = narrator.generate_report("TURBINE_04", tags)
    print(report)

    print("\n--- Scenario: Nominal Operations ---")
    tags = [{"tag": "High_Efficiency", "severity": "INFO"}]
    
    report = narrator.generate_report("SOLAR_ARRAY_01", tags)
    print(report)

    print("\n" + "="*60)
    print(" DEMO COMPLETE: NARRATIVE GENERATED")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
