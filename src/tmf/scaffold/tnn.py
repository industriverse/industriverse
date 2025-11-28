import torch
import torch.nn as nn
import abc

class BaseTNN(nn.Module, abc.ABC):
    """
    Base class for Thermodynamic Neural Networks (TNN).
    Implements Hamiltonian dynamics: H_total = H_physics + H_learned.
    """
    def __init__(self):
        super().__init__()

    @abc.abstractmethod
    def H_learned(self, state):
        """The learned component of the Hamiltonian (correction)."""
        pass

    @abc.abstractmethod
    def H_physics(self, state):
        """The analytic physical Hamiltonian (e.g. 0.5*mv^2)."""
        pass

    def H_total(self, state):
        """Total Hamiltonian."""
        return self.H_physics(state) + self.H_learned(state)

    def vector_field(self, state):
        """
        Computes the symplectic vector field F = J * grad(H).
        For canonical coordinates (q, p):
        dq/dt = dH/dp
        dp/dt = -dH/dq
        """
        with torch.enable_grad():
            if not state.requires_grad:
                state.requires_grad_(True)
            
            H = self.H_total(state)
            grads = torch.autograd.grad(H, state, create_graph=True)[0]
            
            # Assuming state is [q, p] concatenated
            dim = state.shape[-1] // 2
            dH_dq = grads[..., :dim]
            dH_dp = grads[..., dim:]
            
            dq_dt = dH_dp
            dp_dt = -dH_dq
            
            return torch.cat([dq_dt, dp_dt], dim=-1)

    def step(self, state, dt):
        """
        Simple symplectic Euler step (placeholder).
        In production, use a higher-order integrator.
        """
        F = self.vector_field(state)
        return state + F * dt
