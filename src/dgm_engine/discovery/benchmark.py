from typing import List

class DGMBenchmark:
    """
    Evaluation framework for Discovery Agents.
    """
    def __init__(self):
        self.datasets = [
            "plasma_physics",
            "molecular_biology",
            "material_science",
            "quantum_chemistry"
        ]
        
    def run_benchmark(self, agent) -> float:
        """Run agent against all datasets and return aggregate score"""
        print(f"Benchmarking Agent {agent.id}...")
        score = agent.evaluate_on_benchmark(self.datasets)
        print(f"  > Score: {score:.4f}")
        return score
