import torch
import torch.nn as nn

class EBDM(nn.Module):
    def __init__(self, input_dim=128, hidden_dim=512, num_layers=6):
        super().__init__()

        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.SiLU(),
        )

        self.score_network = nn.ModuleList([
            nn.Sequential(
                nn.Linear(hidden_dim, hidden_dim),
                nn.SiLU(),
                nn.Linear(hidden_dim, hidden_dim),
                nn.SiLU(),
            ) for _ in range(num_layers)
        ])

        self.output = nn.Linear(hidden_dim, input_dim)

    def forward(self, x, noise_level):
        # Embed noise level
        # Simple broadcasting for now, in prod use sinusoidal embeddings
        h = self.encoder(x)
        
        # Add noise info (simplified)
        h = h + noise_level 
        
        for layer in self.score_network:
            h = h + layer(h)
        h = self.output(h)
        return h * noise_level

def ebdm_loss(model, x0):
    noise = torch.randn_like(x0)
    noise_level = torch.rand(x0.size(0), 1).to(x0.device)
    x_noisy = x0 + noise * noise_level
    score = model(x_noisy, noise_level)
    # Denoising score matching loss
    return ((score - noise)**2).mean()
