import time
import random
import json
from typing import List, Dict
from .experiment_runner import ExperimentRunner

class TimeCompressor:
    """
    Simulates 30 days of evolution in minutes.
    Generates synthetic experiments and runs them through the Evolution Engine.
    """
    def __init__(self):
        self.runner = ExperimentRunner()
        self.experiments_log = []

    def compress_time(self, days=30, experiments_per_day=4):
        print(f"⏳ [Time Compressor] Initiating {days}-Day Simulation...")
        
        start_time = time.time()
        
        for day in range(1, days + 1):
            print(f"\n📅 Day {day}/{days}")
            
            for i in range(experiments_per_day):
                exp_name = f"Day{day}_Exp{i+1}_{self._generate_exp_name()}"
                
                # Generate Synthetic Variants
                # Variant A (Baseline)
                def variant_a(ctx):
                    return {
                        "value": 10.0 + random.uniform(-1, 1),
                        "latency": 50.0 + random.uniform(-5, 5),
                        "stability": 0.9
                    }
                
                # Variant B (Innovation - Probabilistic Improvement)
                # 60% chance of improvement, 10% chance of breakthrough
                def variant_b(ctx):
                    improvement = random.random()
                    val = 10.0
                    lat = 50.0
                    
                    if improvement > 0.4: # 60% success
                        val += random.uniform(1, 5)
                        lat -= random.uniform(1, 10)
                    
                    if improvement > 0.9: # 10% breakthrough
                        val += random.uniform(10, 20)
                        lat -= random.uniform(10, 20)
                        
                    return {
                        "value": val,
                        "latency": lat,
                        "stability": 0.85 + random.uniform(-0.1, 0.1)
                    }

                # Run Experiment
                result = self.runner.run_experiment(exp_name, variant_a, variant_b, {})
                self.experiments_log.append(result)
                
                # Simulate "Thinking Time"
                time.sleep(0.05)

        duration = time.time() - start_time
        print(f"\n✅ Simulation Complete. {len(self.experiments_log)} Experiments run in {duration:.2f}s.")
        return self.experiments_log

    def _generate_exp_name(self):
        types = ["Optimization", "Refactor", "NewFeature", "ModelUpdate", "UX_Tweak"]
        return random.choice(types)

if __name__ == "__main__":
    compressor = TimeCompressor()
    compressor.compress_time(days=5) # Short test
