from typing import List
from src.supply_chain.cognitive_supply_chain import CognitiveSupplyChain
from src.unification.unified_substrate_model import USMSignal

class PredictiveLogistics:
    """
    The Oracle of Operations.
    Predicts supply chain disruptions using USM signals.
    """
    
    def __init__(self, chain: CognitiveSupplyChain):
        self.chain = chain
        
    def analyze_signals(self, signals: List[USMSignal]):
        """
        Scans for threats to the supply chain.
        """
        print("   🔮 [PREDICTOR] Scanning USM Signals for Logistics Threats...")
        
        for sig in signals:
            # Rule 1: Weather Event (High Thermal Entropy)
            if sig.entropy.type == "THERMAL" and sig.entropy.value > 0.8:
                print("     -> 🌪️ STORM DETECTED (High Thermal Entropy).")
                self._trigger_reroute("WEATHER_EVENT")
                
            # Rule 2: Labor Strike (High Social Entropy)
            elif sig.entropy.type == "SOCIAL" and sig.entropy.value > 0.8:
                print("     -> 🪧 STRIKE RISK (High Social Entropy).")
                self._trigger_reroute("LABOR_EVENT")
                
    def _trigger_reroute(self, reason: str):
        """
        Simulates proactive rerouting logic.
        """
        # In a real system, we'd map the signal location to specific routes.
        # Here, we mock closing the first active route.
        if self.chain.routes:
            target_route = list(self.chain.routes.values())[0]
            print(f"     -> 🛡️ PROACTIVE ACTION: Closing Route {target_route.id} due to {reason}.")
            self.chain.update_route_status(target_route.id, "BLOCKED")

# --- Verification ---
if __name__ == "__main__":
    from src.unification.unified_substrate_model import USMEntropy
    chain = CognitiveSupplyChain()
    chain.add_route("A", "B", 10.0)
    
    pred = PredictiveLogistics(chain)
    sig = USMSignal(entropy=USMEntropy(0.9, "THERMAL"))
    pred.analyze_signals([sig])
