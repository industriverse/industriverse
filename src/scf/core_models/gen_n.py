import torch
import torch.nn as nn

class GenN(nn.Module):
    def __init__(self, input_dim=1024, hidden=2048, vocab_size=32000):
        super().__init__()
        # minimal code generator head; in prod replace with transformer encoder-decoder
        self.encoder = nn.Sequential(nn.Linear(input_dim, hidden), nn.GELU())
        self.decoder = nn.Sequential(nn.Linear(hidden, hidden), nn.GELU(), nn.Linear(hidden, vocab_size))
    def forward(self, x):
        h = self.encoder(x)
        logits = self.decoder(h)
        return logits
