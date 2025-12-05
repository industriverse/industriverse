import random
import json
import time
from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class ExperimentResult:
    experiment_id: str
    hyperparameters: Dict
    validation_entropy: float
    status: str # 'promoted', 'rejected', 'failed'

class ExperimentLoop:
    """
    The Self-Improvement Engine.
    Autonomously forks the current best model, applies variations, and tests them.
    """
    def __init__(self, baseline_entropy: float = 1.0):
        self.current_best_entropy = baseline_entropy
        self.history = []

    def propose_experiment(self) -> Dict:
        """
        Propose a new set of hyperparameters based on simple mutation.
        """
        # Base config (mock)
        base_config = {"lr": 0.001, "hidden_dim": 64, "layers": 3}
        
        # Mutation logic
        mutation_type = random.choice(["lr", "hidden_dim"])
        new_config = base_config.copy()
        
        if mutation_type == "lr":
            # Mutate Learning Rate (0.5x to 1.5x)
            factor = random.uniform(0.5, 1.5)
            new_config["lr"] *= factor
        elif mutation_type == "hidden_dim":
            # Mutate Hidden Dim (Small adjustment)
            delta = random.choice([-8, 8])
            new_config["hidden_dim"] = max(16, new_config["hidden_dim"] + delta)
            
        return new_config

    def run_experiment(self, config: Dict) -> ExperimentResult:
        """
        Simulate running an experiment.
        In a real system, this would trigger a training job.
        """
        experiment_id = f"exp_{int(time.time())}_{random.randint(1000,9999)}"
        print(f"🧪 Starting Experiment {experiment_id} with config: {config}")
        
        # Simulate training outcome (Mock)
        # Assume 20% chance of improvement
        improvement = random.random() < 0.2
        
        if improvement:
            # Better entropy (lower is better)
            new_entropy = self.current_best_entropy * random.uniform(0.90, 0.99)
        else:
            # Worse or same
            new_entropy = self.current_best_entropy * random.uniform(1.00, 1.10)
            
        status = "rejected"
        if new_entropy < self.current_best_entropy:
            status = "promoted"
            self.current_best_entropy = new_entropy
            print(f"   🚀 SUCCESS! New Best Entropy: {self.current_best_entropy:.4f}")
        else:
            print(f"   ❌ Failed. Entropy: {new_entropy:.4f} (vs {self.current_best_entropy:.4f})")
            
        result = ExperimentResult(
            experiment_id=experiment_id,
            hyperparameters=config,
            validation_entropy=new_entropy,
            status=status
        )
        self.history.append(result)
        return result

    def get_best_config(self) -> Dict:
        # In a real system, this would return the config associated with the best entropy
        # For this mock, we just return the last promoted one or default
        return {"entropy": self.current_best_entropy}
