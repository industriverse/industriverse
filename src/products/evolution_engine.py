from src.evolution.experiment_runner import ExperimentRunner

class EvolutionEngine:
    """
    Product 5: Evolution Engine
    Automated R&D Lab.
    """
    def __init__(self):
        self.name = "Evolution Engine"
        self.runner = ExperimentRunner()

    def get_status(self):
        return {
            "product": self.name,
            "status": "EVOLVING",
            "experiments_run": len(self.runner.results)
        }

    def run_ab_test(self, name, var_a, var_b):
        print(f"[{self.name}] Running A/B Test: {name}")
        return self.runner.run_experiment(name, var_a, var_b, {})
