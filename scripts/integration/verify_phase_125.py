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

def run_verification():
    print("############################################################")
    print("#   PHASE 125: RCE PIPELINE VERIFICATION                   #")
    print("############################################################")

    # 1. Generate Synthetic Telemetry (3 Windows)
    # Window A: Stable, Low Entropy
    win_a = [{'temperature': 20+np.random.normal(0, 0.1), 'vibration': 0.01} for _ in range(50)]
    # Window B: High Temp, High Entropy (Thermal Anomaly)
    win_b = [{'temperature': 80+np.random.normal(0, 5.0), 'vibration': 0.05} for _ in range(50)]
    # Window C: Stable, Low Entropy (Similar to A)
    win_c = [{'temperature': 21+np.random.normal(0, 0.1), 'vibration': 0.01} for _ in range(50)]
    
    windows = [win_a, win_b, win_c]
    
    # 2. Extract Features
    extractor = FeatureExtractor()
    features = [extractor.extract_features(w) for w in windows]
    print(f"✅ Extracted {len(features)} feature vectors.")
    print(f"   Sample: {features[0]}")

    # 3. Mine Clusters (RCOs)
    clusterer = Clusterer(eps=2.0, min_samples=1) # Loose params for small data
    rcos = clusterer.mine_clusters(features)
    print(f"✅ Mined {len(rcos)} RCOs.")
    
    # 4. Build Opportunity Zones
    builder = ZoneBuilder()
    zones = builder.build_zones(rcos)
    print(f"✅ Built {len(zones)} Opportunity Zones.")
    for z in zones:
        print(f"   📍 {z.name}: Score={z.aggregated_opportunity_score:.2f}, Risk={z.aggregated_risk:.2f}")

    # 5. Trigger Exploration Mission
    if zones:
        target_zone = zones[0]
        mission = ExplorationMission(target_zone.id)
        discovery = mission.run()
        if discovery:
            print("✅ Mission Successful. Discovery Object Created.")
        else:
            print("❌ Mission Failed.")

if __name__ == "__main__":
    run_verification()
