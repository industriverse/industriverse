
import torch
from torch import nn

class HeatTNN(nn.Module):
    def forward(self, x, t):
        # Placeholder dynamics for heat
        # dx/dt = -x (decay)
        return -0.1 * x
