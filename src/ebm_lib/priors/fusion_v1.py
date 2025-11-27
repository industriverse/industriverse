import numpy as np
from ebm_lib.base import EnergyPrior

class FusionPriorV1:
    name = "fusion"
    version = "v1"
    required_fields = ["state_vector"]
    metadata = {
        "equations": ["MHD"],
        "description": "Physics-informed energy function for fusion",
    }

    def validate(self, state):
        for f in self.required_fields:
            if f not in state:
                raise ValueError(f"Missing required field: {f}")

    def energy(self, state):
        x = state["state_vector"]
        # placeholder: domain-specific physics equation goes here
        # Simple quadratic potential for demo purposes: E = sum(x^2)
        return float(np.sum(x**2))

    def grad(self, state):
        x = state["state_vector"]
        # Gradient of sum(x^2) is 2*x
        return {"state_vector": 2 * x}

PRIOR = FusionPriorV1()
