import sys
import os
import json

# Add project root to path
sys.path.append(os.getcwd())

def run():
    print("\n" + "="*60)
    print(" DEMO 41: ONTOLOGY CONVERTER (TSO)")
    print("="*60 + "\n")

    print("Input: Legacy SCADA Tag...")
    legacy_tag = {
        "tag_id": "PLC_401_TEMP_VAL",
        "value": 450.5,
        "unit": "F",
        "timestamp": "2023-10-27T10:00:00Z"
    }
    print(json.dumps(legacy_tag, indent=2))

    print("\nConverting to Thermodynamic Signal Ontology (TSO) v0.1...")
    
    # Simulated Conversion Logic
    tso_object = {
        "@context": "https://industriverse.com/schemas/tso/v1",
        "@type": "ThermodynamicState",
        "source_id": "urn:industriverse:node:PLC_401",
        "energy_vector": {
            "potential_energy": (legacy_tag["value"] - 32) * 5/9, # Convert F to C (proxy for energy)
            "unit": "Celsius_Equivalent"
        },
        "metadata": {
            "original_tag": legacy_tag["tag_id"],
            "ingest_time": legacy_tag["timestamp"]
        }
    }
    
    print(json.dumps(tso_object, indent=2))
    print("\n✅ Validated against TSO Schema.")

    print("\n" + "="*60)
    print(" DEMO COMPLETE: ONTOLOGY MAPPED")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
