import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class DocGenerator:
    def __init__(self):
        pass

    def generate_manual(self, capsule_manifest):
        logger.info(f"Generating documentation for {capsule_manifest['name']}...")
        
        # In a real system, this would use an LLM to generate text based on the manifest.
        # Here we use a template.
        
        template = """
# Operator Manual: {name}
**Version:** {version}
**UTID:** {utid}

## 1. Overview
The **{name}** is a sovereign industrial capsule designed for **{domain}**. 
It operates at Intelligence Level **{intelligence_level}**.

## 2. Capabilities
This capsule is equipped with the following capabilities:
{capabilities_list}

## 3. Safety Protocols
**Max Temperature:** {max_temp} K
**Max Pressure:** {max_pressure} Bar
**Emergency Stop Latency:** {estop_ms} ms

## 4. Maintenance
Recommended maintenance interval: Every 500 operational hours.
        """
        
        capabilities_list = "\n".join([f"- {cap}" for cap in capsule_manifest['capabilities']])
        
        doc = template.format(
            name=capsule_manifest['name'],
            version=capsule_manifest['version'],
            utid=capsule_manifest['utid'],
            domain=capsule_manifest['prin']['domain'],
            intelligence_level=capsule_manifest['prin']['intelligence_level'],
            capabilities_list=capabilities_list,
            max_temp=capsule_manifest['safety']['max_temp'],
            max_pressure=capsule_manifest['safety']['max_pressure'],
            estop_ms=capsule_manifest['safety']['emergency_stop_latency_ms']
        )
        
        return doc

def run():
    print("\n" + "="*60)
    print(" DEMO 9: GENERATIVE DOCUMENTATION")
    print("="*60 + "\n")

    generator = DocGenerator()

    # Mock Capsule Manifest
    capsule = {
        "name": "Fusion Injector V4",
        "version": "4.2.0",
        "utid": "capsule_fusion_inj_v4_9988",
        "prin": {
            "domain": "Plasma Fusion",
            "intelligence_level": "L3_Optimization"
        },
        "capabilities": [
            "Precision Fuel Injection",
            "Plasma Density Monitoring",
            "Magnetic Field Stabilization"
        ],
        "safety": {
            "max_temp": 5000,
            "max_pressure": 200,
            "emergency_stop_latency_ms": 5
        }
    }

    print("--- Input Manifest ---")
    print(json.dumps(capsule, indent=2))

    print("\n--- Generating Manual ---")
    manual = generator.generate_manual(capsule)

    print("\n--- Generated Output (Markdown) ---")
    print(manual)

    print("\n" + "="*60)
    print(" DEMO COMPLETE: DOCS GENERATED")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
