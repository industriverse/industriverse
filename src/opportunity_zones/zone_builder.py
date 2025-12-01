from typing import List
from src.resource_clusters.rco import ResourceClusterObject, OpportunityZone
from .scoring import OpportunityScorer

class ZoneBuilder:
    """
    The Map Maker.
    Groups RCOs into Opportunity Zones.
    """
    def __init__(self):
        self.scorer = OpportunityScorer()

    def build_zones(self, rcos: List[ResourceClusterObject]) -> List[OpportunityZone]:
        """
        Scores RCOs and groups them.
        For simplicity, we group by dominant tag in this iteration.
        """
        zones = {}
        
        for rco in rcos:
            # 1. Score the RCO
            self.scorer.score_rco(rco)
            
            # 2. Group by Tag
            tag = rco.classification_tags[0] if rco.classification_tags else "uncategorized"
            
            if tag not in zones:
                zones[tag] = OpportunityZone(name=f"{tag.capitalize()} Zone", dominant_tag=tag)
            
            zone = zones[tag]
            zone.rco_ids.append(rco.id)
            
            # Update Aggregates (Simple Average)
            n = len(zone.rco_ids)
            prev_score = zone.aggregated_opportunity_score * (n-1)
            prev_risk = zone.aggregated_risk * (n-1)
            
            zone.aggregated_opportunity_score = (prev_score + rco.opportunity_score) / n
            zone.aggregated_risk = (prev_risk + rco.risk_score) / n

        return list(zones.values())
