
import torch
from torch import nn

class MatflowTNN(nn.Module):
    def forward(self, x, t):
        # Placeholder dynamics for matflow
        # dx/dt = -x (decay)
        return -0.1 * x
