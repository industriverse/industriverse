from typing import List, Dict, Any
from src.unification.cross_domain_inference_engine import InferenceResult
from src.unification.unified_substrate_model import USMField
from src.coherence.iacp_v2 import IACPIntent

class StrategicPlanner:
    """
    The Will of the Organism.
    Translates insights into strategic directives.
    """
    
    def formulate_strategy(self, insights: List[InferenceResult], fields: Dict[str, USMField]) -> List[Dict[str, Any]]:
        """
        Decides on the next course of action.
        """
        directives = []
        
        # 1. Handle Critical Insights (Reactive)
        for insight in insights:
            if insight.conclusion == "CYBER_PHYSICAL_ATTACK":
                directives.append({
                    "intent": IACPIntent.ISSUE_WARNING,
                    "urgency": 1.0,
                    "domain": "SECURITY",
                    "payload": {"action": "INITIATE_LOCKDOWN", "reason": "ATTACK_DETECTED"}
                })
            elif insight.conclusion == "MARKET_MANIPULATION":
                directives.append({
                    "intent": IACPIntent.ISSUE_WARNING,
                    "urgency": 0.8,
                    "domain": "ECONOMICS",
                    "payload": {"action": "FREEZE_TRADING", "reason": "MANIPULATION_DETECTED"}
                })
                
        # 2. Handle Entropy Trends (Proactive)
        thermal_entropy = fields.get("THERMAL", USMField("Empty")).get_average_entropy()
        if thermal_entropy > 0.6:
             directives.append({
                "intent": IACPIntent.REQUEST_RESOURCE,
                "urgency": 0.5,
                "domain": "PHYSICS",
                "payload": {"action": "DEPLOY_OPTIMIZERS", "target": "THERMAL_WASTE"}
            })
            
        return directives
