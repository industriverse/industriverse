import torch
import math

def langevin_step(x0: torch.Tensor, energy_fn, steps=10, step_size=0.1, noise_scale=0.01, clip=None):
    """
    Perform Langevin Dynamics sampling to minimize energy.
    x_{t+1} = x_t - step_size * grad(E(x_t)) + noise
    clip: tuple (min, max) or None
    """
    x = x0.clone().detach().requires_grad_(True)
    for _ in range(steps):
        E = energy_fn(x).sum()
        E.backward()
        grad = x.grad
        x = x - step_size * grad + noise_scale * torch.randn_like(x)
        if clip is not None:
            x = torch.clamp(x, clip[0], clip[1])
        x = x.detach()
        x.requires_grad_(True)
    return x
