import torch
import torch.nn as nn

class KineticMemory(nn.Module):
    """
    Short-term temporal memory for the Sovereign Model.
    Uses a GRU to process a sequence of past states (e.g., entropy history).
    """
    def __init__(self, input_dim: int, hidden_dim: int = 32, num_layers: int = 1):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        
        # GRU for temporal processing
        # batch_first=True expects input: (batch, seq_len, input_dim)
        self.gru = nn.GRU(input_dim, hidden_dim, num_layers, batch_first=True)
        
        # Projection to output (optional, if we want to predict next state directly)
        # For now, we just return the hidden state as the "memory context"
        self.projection = nn.Linear(hidden_dim, input_dim)

    def forward(self, x: torch.Tensor, h: torch.Tensor = None):
        """
        Args:
            x: Input sequence (batch, seq_len, input_dim)
            h: Initial hidden state (num_layers, batch, hidden_dim)
            
        Returns:
            output: (batch, seq_len, input_dim) - Projected output (e.g. prediction)
            h_n: (num_layers, batch, hidden_dim) - Final hidden state (context)
        """
        # GRU Forward
        out, h_n = self.gru(x, h)
        
        # Project output
        output = self.projection(out)
        
        return output, h_n

    def init_hidden(self, batch_size: int, device: torch.device = torch.device('cpu')):
        """
        Initialize hidden state with zeros.
        """
        return torch.zeros(self.num_layers, batch_size, self.hidden_dim).to(device)
