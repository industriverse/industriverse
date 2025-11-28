import sys
import os
import json

# Add project root to path
sys.path.append(os.getcwd())

from src.core_ai_layer.semantic_translator import ThermodynamicTranslator

def run():
    print("\n" + "="*60)
    print(" DEMO 44: SEMANTIC TRANSLATION API")
    print("="*60 + "\n")

    translator = ThermodynamicTranslator()

    print("Simulating API Request (POST /api/v1/translate)...")
    request_body = {
        "energy_vector": {
            "E_total": 0.0,
            "Entropy": 0.0,
            "dE_dt_volatility": 0.0
        }
    }
    print(f"Request: {json.dumps(request_body)}")

    print("\nProcessing...")
    tags = translator.translate(request_body["energy_vector"])
    
    response = {
        "status": "success",
        "semantic_tags": [t["tag"] for t in tags],
        "severity": max([t["severity"] for t in tags], key=lambda x: len(x)) # Simple heuristic
    }
    
    print(f"Response: {json.dumps(response, indent=2)}")
    
    if "Dead_Signal" in response["semantic_tags"]:
        print("✅ API correctly identified Dead Signal.")

    print("\n" + "="*60)
    print(" DEMO COMPLETE: API RESPONSE SENT")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
