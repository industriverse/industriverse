import numpy as np
from ebm_lib.base import EnergyPrior

class FailurePriorV1:
    name = "failure"
    version = "v1"
    required_fields = ["state_vector"]
    metadata = {
        "equations": ["Generic ODE"],
        "description": "Physics-informed energy function for failure",
    }

    def validate(self, state):
        for f in self.required_fields:
            if f not in state:
                raise ValueError(f"Missing required field: {f}")

    def energy(self, state):
        x = state["state_vector"]
        # Placeholder energy function: simple quadratic well
        return float(np.sum(x**2))

    def grad(self, state):
        x = state["state_vector"]
        return {"state_vector": 2 * x}

PRIOR = FailurePriorV1()
