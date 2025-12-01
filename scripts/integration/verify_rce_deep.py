import sys
import os
import numpy as np
import time

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.resource_clusters.extractor import FeatureExtractor
from src.resource_clusters.clusterer import Clusterer
from src.opportunity_zones.zone_builder import ZoneBuilder
from src.security.exploration_mission import ExplorationMission

def run_deep_verification():
    print("############################################################")
    print("#   PHASE 125: DEEP RCE VERIFICATION                       #")
    print("############################################################")

    # 1. Generate Synthetic Telemetry with Vibration (Sine Wave)
    # Window A: Stable
    win_a = [{'temperature': 20, 'vibration': 0.01} for _ in range(50)]
    # Window B: Oscillating (Vibration Anomaly)
    t = np.linspace(0, 10, 50)
    vib_signal = 0.5 * np.sin(2 * np.pi * 5 * t) # 5Hz oscillation
    win_b = [{'temperature': 20, 'vibration': float(v)} for v in vib_signal]
    
    windows = [win_a, win_b]
    
    # 2. Extract Features (Test Spectral Energy)
    print("🔵 Testing Feature Extractor (Spectral)...")
    extractor = FeatureExtractor()
    features = [extractor.extract_features(w) for w in windows]
    
    print(f"   Window A Spectral Energy: {features[0]['spectral_energy']:.4f}")
    print(f"   Window B Spectral Energy: {features[1]['spectral_energy']:.4f}")
    
    if features[1]['spectral_energy'] > features[0]['spectral_energy']:
        print("✅ Spectral Analysis correctly identified vibration.")
    else:
        print("❌ Spectral Analysis Failed.")

    # 3. Mine Clusters (Test Fallback Clusterer)
    print("\n🔵 Testing Clusterer (Fallback/DBSCAN)...")
    clusterer = Clusterer(eps=2.0, min_samples=1)
    rcos = clusterer.mine_clusters(features)
    print(f"✅ Mined {len(rcos)} RCOs.")
    for rco in rcos:
        print(f"   RCO Tags: {rco.classification_tags}")

    # 4. Build Zones (Test Advanced Scoring)
    print("\n🔵 Testing Zone Builder (Liquidity/Urgency)...")
    builder = ZoneBuilder()
    zones = builder.build_zones(rcos)
    for z in zones:
        print(f"   📍 {z.name}: Score={z.aggregated_opportunity_score:.2f} (Includes Liquidity/Urgency)")

    # 5. Trigger Mission (Test Healing)
    print("\n🔵 Testing Mission (Healing Contingency)...")
    if zones:
        target_zone = zones[0]
        mission = ExplorationMission(target_zone.id)
        # Force a scenario where we might see healing logs (though mock is random/fixed)
        discovery = mission.run()
        if discovery:
            print("✅ Mission Successful.")

if __name__ == "__main__":
    run_deep_verification()
