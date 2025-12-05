import torch
import torch.nn as nn

class SimpleModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(4, 4)

    def forward(self, x):
        return self.linear(x)

model = SimpleModel()
dummy_input = torch.randn(1, 4)
torch.onnx.export(model, dummy_input, "simple.onnx", opset_version=11)
print("✅ Simple Export Successful")
