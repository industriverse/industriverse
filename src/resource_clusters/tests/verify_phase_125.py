import random
from src.resource_clusters.engine import ResourceClusterEngine
from src.security.exploration_mission import ExplorationMission

def verify_rce_pipeline():
    print("🧪 Starting Phase 125 Verification: Deep RCE Pipeline")
    
    # 1. Generate Synthetic Telemetry
    # Create two distinct patterns: "Thermal Anomaly" and "Stable Operation"
    telemetry_batch = []
    
    # Pattern A: Thermal Anomaly (High Temp, High Gradient)
    for _ in range(20):
        window = []
        base_temp = 60 + random.random() * 10
        for i in range(10):
            window.append({
                "temperature": base_temp + (i * 2), # Rising temp
                "vibration": 0.1
            })
        telemetry_batch.append(window)
        
    # Pattern B: Stable Operation (Low Temp, Low Gradient)
    for _ in range(20):
        window = []
        base_temp = 30 + random.random()
        for i in range(10):
            window.append({
                "temperature": base_temp + random.random() * 0.5,
                "vibration": 0.05
            })
        telemetry_batch.append(window)

    # 2. Run RCE Engine
    engine = ResourceClusterEngine()
    zones = engine.process_telemetry(telemetry_batch)
    
    assert len(zones) >= 1, "Failed to create zones"
    
    # 3. Verify Scoring & Classification
    high_value_zone = None
    for zone in zones:
        print(f"📍 Zone {zone.id}: Score={zone.aggregated_opportunity_score:.2f}, Risk={zone.aggregated_risk:.2f}, Tags={zone.dominant_tag}")
        if zone.aggregated_opportunity_score > 0.7:
            high_value_zone = zone
            
    assert high_value_zone is not None, "Failed to identify high-value zone"
    
    # 4. Trigger AI Shield Mission
    print(f"🎯 Triggering Mission for High Value Zone: {high_value_zone.id}")
    mission = ExplorationMission(high_value_zone.id)
    result = mission.run()
    
    assert result is not None, "Mission failed to produce discovery"
    assert result.validated, "Discovery not validated"
    
    print("✅ Phase 125 Verification Complete: RCE -> Zones -> Mission -> Discovery")

if __name__ == "__main__":
    verify_rce_pipeline()
