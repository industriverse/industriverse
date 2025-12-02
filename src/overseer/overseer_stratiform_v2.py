from typing import List, Dict
from src.unification.unified_substrate_model import USMField
from src.unification.cross_domain_inference_engine import CrossDomainInferenceEngine
from src.coherence.iacp_v2 import IACPMessage, IACPIntent, IACPContext
from src.overseer.strategic_planner import StrategicPlanner

class OverseerStratiformV2:
    """
    The Sovereign Mind.
    Orchestrates the organism using USM perception and IACP command.
    """
    
    def __init__(self):
        self.inference_engine = CrossDomainInferenceEngine()
        self.planner = StrategicPlanner()
        
    def run_cycle(self, fields: Dict[str, USMField]) -> List[IACPMessage]:
        """
        The OODA Loop: Observe (USM) -> Orient (Inference) -> Decide (Plan) -> Act (IACP).
        """
        print("   👁️ [OVERSEER] Observing Substrate...")
        
        # 1. Orient: Cross-Domain Inference
        insights = self.inference_engine.analyze(fields)
        
        # 2. Decide: Strategic Planning
        directives = self.planner.formulate_strategy(insights, fields)
        
        # 3. Act: Generate Commands
        commands = []
        for directive in directives:
            cmd = IACPMessage(
                sender_id="OVERSEER_PRIME",
                intent=directive["intent"],
                context=IACPContext(urgency=directive["urgency"], domain=directive["domain"]),
                payload=directive["payload"]
            )
            commands.append(cmd)
            print(f"     -> 🗣️ COMMAND: {cmd.intent.name} ({cmd.payload})")
            
        return commands

# --- Verification ---
if __name__ == "__main__":
    # Mock Dependencies for standalone run
    pass
