import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path.cwd()))

from src.integrations.b2_client import B2Client
from src.economics.dac_capsule import DACCapsule

def demo_infinite_mesh():
    print("🌐 Starting Infinite Service Mesh Demo...")
    print("========================================")
    
    # 1. Initialize the B2 Rehydration Client
    # This will look for B2_KEY_ID and B2_APP_KEY in env vars
    b2_client = B2Client()
    
    # 2. Define our "Services" to be rehydrated
    # In a real scenario, these would be downloaded codebases/models that we then load.
    # Here, we simulate the "Service" as a class that uses the data.
    
    class IndustrialPredictor:
        def __init__(self, model_name):
            self.model_name = model_name
            self.loaded = False
            
        def load_model(self):
            print(f"   [{self.model_name}] Loading weights from disk...")
            self.loaded = True
            
        def predict(self, sensor_data):
            if not self.loaded:
                print(f"   [{self.model_name}] Error: Model not loaded!")
                return None
            print(f"   [{self.model_name}] Analyzing sensor data: {sensor_data}...")
            return {"status": "nominal", "confidence": 0.98}

    # 3. Orchestrate Rehydration & Wrapping
    
    # Service A: Full Export Archive
    print("\n--- Orchestrating Service A: Full Export Archive ---")
    # Rehydrate (Download)
    bucket_name = os.getenv("B2_BUCKET_NAME", "industriverse-backup")
    success_a = b2_client.rehydrate_dataset(bucket_name, "archives/industriverse-export-full-20251120.tar.gz", "./data/archives")
    
    if success_a:
        # Instantiate Service
        service_a = IndustrialPredictor("Export-Archive-2025")
        service_a.load_model()
        
        # Wrap in DAC (Revenue Engine)
        dac_a = DACCapsule(service_a, name="DAC-Archive", price_per_call=0.10)
        
        # Execute (and generate revenue)
        dac_a.predict({"query": "historical_data"})

    # Service B: Packages Archive
    print("\n--- Orchestrating Service B: Packages Archive ---")
    # Rehydrate (Download)
    success_b = b2_client.rehydrate_dataset(bucket_name, "packages/industriverse-packages-20251120.tar.gz", "./data/packages")
    
    if success_b:
        # Instantiate Service
        service_b = IndustrialPredictor("Packages-2025")
        service_b.load_model()
        
        # Wrap in DAC (Revenue Engine)
        dac_b = DACCapsule(service_b, name="DAC-Packages", price_per_call=0.05)
        
        # Execute
        dac_b.predict({"query": "dependency_check"})

    print("\n========================================")
    print("✅ Infinite Service Mesh Demo Complete.")

if __name__ == "__main__":
    demo_infinite_mesh()
