from typing import List, Dict
from .extractor import FeatureExtractor
from .clusterer import Clusterer
from ..opportunity_zones.zone_builder import ZoneBuilder
from ..opportunity_zones.scoring import OpportunityScorer

class ResourceClusterEngine:
    """
    Orchestrates the full RCE pipeline:
    Telemetry -> Features -> Clusters -> Zones -> Scores
    """
    def __init__(self):
        self.extractor = FeatureExtractor()
        self.clusterer = Clusterer()
        self.zone_builder = ZoneBuilder()
        self.scorer = OpportunityScorer()

    def process_telemetry(self, telemetry_windows: List[List[Dict[str, float]]]):
        """
        Runs the full pipeline on a batch of telemetry windows.
        """
        print("⚙️  RCE: Processing Telemetry Batch...")
        
        # 1. Extract Features
        feature_vectors = []
        for window in telemetry_windows:
            feats = self.extractor.extract_features(window)
            if feats:
                feature_vectors.append(feats)
        
        # 2. Mine Clusters (RCOs)
        rcos = self.clusterer.mine_clusters(feature_vectors)
        
        # 3. Score RCOs
        for rco in rcos:
            self.scorer.score_rco(rco)
            
        # 4. Build Zones
        zones = self.zone_builder.build_zones(rcos)
        
        print(f"✅ RCE: Created {len(zones)} Opportunity Zones from {len(rcos)} Clusters.")
        return zones
