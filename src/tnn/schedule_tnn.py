
import torch
from torch import nn

class ScheduleTNN(nn.Module):
    def forward(self, x, t):
        # Placeholder dynamics for schedule
        # dx/dt = -x (decay)
        return -0.1 * x
