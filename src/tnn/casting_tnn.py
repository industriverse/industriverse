
import torch
from torch import nn

class CastingTNN(nn.Module):
    def forward(self, x, t):
        # Placeholder dynamics for casting
        # dx/dt = -x (decay)
        return -0.1 * x
