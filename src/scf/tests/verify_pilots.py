import os
from src.edge.pilots.mobile_telemetry_agent import MobileTelemetryAgent

def verify_mobile_agent():
    print("📱 Verifying Mobile Telemetry Agent...")
    agent = MobileTelemetryAgent(device_id="TEST_DEVICE_001")
    
    # Run a few cycles
    data = agent.run_cycle()
    
    # Assertions
    assert data["device_id"] == "TEST_DEVICE_001"
    assert "sensors" in data
    assert "physics_metrics" in data
    assert data["physics_metrics"]["entropy_score"] >= 0.0
    
    print(f"✅ Agent Cycle Successful. Entropy: {data['physics_metrics']['entropy_score']:.2f}")

def verify_ingestion_script_exists():
    print("💾 Verifying Ingestion Script...")
    script_path = "scripts/operations/ingest_external_drive.py"
    assert os.path.exists(script_path), "Ingestion script not found"
    print("✅ Ingestion script exists.")

if __name__ == "__main__":
    verify_mobile_agent()
    verify_ingestion_script_exists()
    print("\n🎉 PILOT DEPLOYMENTS VERIFIED")
