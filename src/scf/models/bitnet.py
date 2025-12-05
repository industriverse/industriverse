import torch
import torch.nn as nn
import torch.nn.functional as F

def activation_quant(x):
    """
    Per-token quantization to 8 bits.
    Range: [-127, 127]
    """
    scale = 127.0 / x.abs().max(dim=-1, keepdim=True).values.clamp_(min=1e-5)
    y = (x * scale).round().clamp_(-128, 127) / scale
    return y + (x - x.detach()) # STE

def weight_quant(w):
    """
    Ternary weight quantization to {-1, 0, 1}.
    Scale is the mean absolute value of the weights.
    """
    scale = 1.0 / w.abs().mean().clamp_(min=1e-5)
    y = (w * scale).round().clamp_(-1, 1) / scale
    return y + (w - w.detach()) # STE

class BitLinear(nn.Linear):
    """
    Linear layer with 1.58-bit weights (Ternary).
    """
    def __init__(self, in_features, out_features, bias=False):
        super(BitLinear, self).__init__(in_features, out_features, bias=bias)

    def forward(self, x):
        # 1. Quantize Weights (Ternary)
        w_quant = weight_quant(self.weight)
        
        # 2. Quantize Activations (8-bit)
        x_quant = activation_quant(x)
        
        # 3. Linear Operation
        # Note: In a real kernel, this would be an integer GEMM.
        # Here we simulate it with FP32 but using quantized values.
        return F.linear(x_quant, w_quant, self.bias)

class BitNet_Student(nn.Module):
    """
    The 'Sovereign Chip' compatible model.
    Uses BitLinear layers for extreme efficiency.
    """
    def __init__(self, input_dim: int = 4, hidden_dim: int = 16, output_dim: int = 4):
        super().__init__()
        self.net = nn.Sequential(
            BitLinear(input_dim, hidden_dim),
            nn.SiLU(),
            BitLinear(hidden_dim, hidden_dim),
            nn.SiLU(),
            BitLinear(hidden_dim, output_dim)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)
