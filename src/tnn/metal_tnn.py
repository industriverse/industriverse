
import torch
from torch import nn

class MetalTNN(nn.Module):
    def forward(self, x, t):
        # Placeholder dynamics for metal
        # dx/dt = -x (decay)
        return -0.1 * x
