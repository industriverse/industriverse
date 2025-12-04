import torch

class TNNConstraints:
    @staticmethod
    def energy_conservation(state_t0, state_t1):
        """
        Enforce that energy change matches work done/heat flow.
        For closed system: E(t0) == E(t1)
        Returns scalar penalty.
        """
        return torch.abs(state_t1.sum() - state_t0.sum())

    @staticmethod
    def boundary_condition(state, min_val=0.0, max_val=1.0):
        """
        Penalize values outside physical bounds.
        """
        violation = torch.relu(min_val - state) + torch.relu(state - max_val)
        return violation.mean()
