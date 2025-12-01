import sys
import os
import time

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.evolution.experiment_runner import ExperimentRunner
from src.evolution.hilbert_metrics import HilbertMetrics

def run_verification():
    print("############################################################")
    print("#   PHASE 126: EVOLUTION ENGINE VERIFICATION               #")
    print("############################################################")

    # 1. Verify Hilbert Metrics
    print("🔵 Testing Hilbert Metrics...")
    hm = HilbertMetrics()
    s1 = {'roi': 1.0, 'latency': 0.5, 'stability': 0.9}
    s2 = {'roi': 1.2, 'latency': 0.4, 'stability': 0.9} # Optimization
    s3 = {'roi': 1.5, 'latency': 0.6, 'stability': 0.8, 'entropy': 0.8} # Innovation
    
    res_opt = hm.analyze_evolution(s1, s2)
    res_inn = hm.analyze_evolution(s1, s3)
    
    print(f"   Optimization Angle: {res_opt['orthogonality']:.4f} ({res_opt['interpretation']})")
    print(f"   Innovation Angle:   {res_inn['orthogonality']:.4f} ({res_inn['interpretation']})")
    
    if res_inn['orthogonality'] < res_opt['orthogonality']:
        print("✅ Hilbert Metrics correctly identified structural shift.")
    else:
        print("❌ Hilbert Metrics Failed.")

    # 2. Verify Experiment Runner
    print("\n🔵 Testing Experiment Runner...")
    runner = ExperimentRunner()
    
    def variant_a(ctx):
        return {"value": 10}
        
    def variant_b(ctx):
        return {"value": 20} # Should win ROI
        
    result = runner.run_experiment("Verification_Test", variant_a, variant_b, {})
    
    if result['winner'] == "B":
        print("✅ Experiment Runner correctly picked Variant B (Higher ROI).")
    else:
        print("❌ Experiment Runner Failed.")

if __name__ == "__main__":
    run_verification()
