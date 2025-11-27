
import torch
from torch import nn

class ConveyorTNN(nn.Module):
    def forward(self, x, t):
        # Placeholder dynamics for conveyor
        # dx/dt = -x (decay)
        return -0.1 * x
