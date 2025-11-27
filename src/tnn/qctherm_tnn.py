
import torch
from torch import nn

class QcthermTNN(nn.Module):
    def forward(self, x, t):
        # Placeholder dynamics for qctherm
        # dx/dt = -x (decay)
        return -0.1 * x
