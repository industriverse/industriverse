import torch
import pytest
from src.scf.models.kinetic_memory import KineticMemory

def test_kinetic_memory_shapes():
    batch_size = 4
    seq_len = 10
    input_dim = 5
    hidden_dim = 16
    
    model = KineticMemory(input_dim, hidden_dim)
    
    # Random input: (batch, seq_len, input_dim)
    x = torch.randn(batch_size, seq_len, input_dim)
    
    # Forward pass
    output, h_n = model(x)
    
    # Check Output Shape: (batch, seq_len, input_dim)
    assert output.shape == (batch_size, seq_len, input_dim)
    
    # Check Hidden State Shape: (num_layers, batch, hidden_dim)
    assert h_n.shape == (1, batch_size, hidden_dim)

def test_hidden_init():
    model = KineticMemory(input_dim=5, hidden_dim=16)
    h = model.init_hidden(batch_size=8)
    assert h.shape == (1, 8, 16)
    assert torch.all(h == 0)
