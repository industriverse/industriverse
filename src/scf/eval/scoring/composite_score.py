class CompositeScore:
    def __init__(self):
        self.weights = {
            "heldout": 0.25,
            "energy": 0.30,
            "stability": 0.15,
            "negentropy": 0.15,
            "novelty": 0.10,
            "tnn_error": 0.10
        }

    def calculate(self, metrics):
        # w1*heldout + w2*(1-violation) + w3*stability + w4*negentropy + w5*novelty - w6*tnn_error
        
        score = (
            self.weights["heldout"] * metrics.get("heldout_pass_rate", 0) +
            self.weights["energy"] * (1.0 - metrics.get("energy_violation_rate", 1.0)) +
            self.weights["stability"] * metrics.get("stability_score", 0) +
            self.weights["negentropy"] * min(1.0, metrics.get("median_negentropy_yield", 0) / 2.0) + # Norm to 2.0J
            self.weights["novelty"] * metrics.get("novelty_score", 0) -
            self.weights["tnn_error"] * metrics.get("tnn_error_pct", 0)
        )
        
        return max(0, min(100, score * 100))
