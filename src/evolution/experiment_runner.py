import time
import uuid
import json
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from .hilbert_metrics import HilbertMetrics

# Mock Quadrality Components for this implementation
class Chronos:
    def measure_latency(self, func, *args):
        start = time.time()
        result = func(*args)
        latency = (time.time() - start) * 1000
        return result, latency

class Kairos:
    def calculate_roi(self, output: Any) -> float:
        # Mock ROI calculation based on output "value"
        if isinstance(output, dict):
            return output.get("value", 0.0) * 1.5 - 0.1 # Revenue - Cost
        return 0.0

class Telos:
    def score_stability(self, output: Any) -> float:
        # Mock stability score (0.0 - 1.0)
        return 0.95

class Aletheia:
    def validate_truth(self, output: Any) -> bool:
        # Mock truth validation
        return True

@dataclass
class ExperimentResult:
    variant_id: str
    output: Any
    latency_ms: float
    roi: float
    stability: float
    truth_valid: bool

class ExperimentRunner:
    """
    The Evolution Engine Core.
    Runs AB tests using Quadrality for evaluation.
    """
    def __init__(self):
        self.chronos = Chronos()
        self.kairos = Kairos()
        self.telos = Telos()
        self.aletheia = Aletheia()
        self.hilbert = HilbertMetrics()
        self.results = []

    def run_experiment(self, name: str, variant_a_func, variant_b_func, context: Dict = None):
        print(f"🧬 [Evolution Engine] Running Experiment: {name}")
        
        # Run Variant A
        res_a = self._evaluate_variant("A", variant_a_func, context)
        print(f"   Variant A: ROI=${res_a.roi:.2f}, Latency={res_a.latency_ms:.2f}ms, Stable={res_a.stability}")

        # Run Variant B
        res_b = self._evaluate_variant("B", variant_b_func, context)
        print(f"   Variant B: ROI=${res_b.roi:.2f}, Latency={res_b.latency_ms:.2f}ms, Stable={res_b.stability}")

        # Determine Winner
        winner = "A" if res_a.roi >= res_b.roi else "B"
        print(f"🏆 Winner: Variant {winner}")

        # Calculate Hilbert Metrics (Evolutionary Angle)
        # Construct state dicts from results
        state_a = {'roi': res_a.roi, 'latency': res_a.latency_ms, 'stability': res_a.stability}
        state_b = {'roi': res_b.roi, 'latency': res_b.latency_ms, 'stability': res_b.stability}
        
        evolution_analysis = self.hilbert.analyze_evolution(state_a, state_b)
        print(f"📐 Hilbert Analysis: {evolution_analysis['interpretation']} (Angle: {evolution_analysis['orthogonality']:.2f})")
        
        return {
            "experiment": name,
            "winner": winner,
            "details": {
                "A": res_a,
                "B": res_b
            }
        }

    def _evaluate_variant(self, variant_id: str, func, context) -> ExperimentResult:
        # 1. Chronos (Latency)
        try:
            output, latency = self.chronos.measure_latency(func, context)
        except Exception as e:
            print(f"   ❌ Variant {variant_id} Failed: {e}")
            return ExperimentResult(variant_id, None, 0, -1.0, 0.0, False)

        # 2. Aletheia (Truth)
        truth_valid = self.aletheia.validate_truth(output)
        if not truth_valid:
            return ExperimentResult(variant_id, output, latency, -1.0, 0.0, False)

        # 3. Telos (Stability)
        stability = self.telos.score_stability(output)

        # 4. Kairos (ROI)
        roi = self.kairos.calculate_roi(output)

        return ExperimentResult(variant_id, output, latency, roi, stability, truth_valid)

if __name__ == "__main__":
    # Test
    runner = ExperimentRunner()
    
    def func_a(ctx):
        time.sleep(0.1)
        return {"value": 10}
        
    def func_b(ctx):
        time.sleep(0.05) # Faster
        return {"value": 12} # Higher Value
        
    runner.run_experiment("Test_Optimization", func_a, func_b, {})
