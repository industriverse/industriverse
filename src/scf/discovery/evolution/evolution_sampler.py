import torch

class EvolutionSampler:
    def mutate(self, seed_tensor: torch.Tensor, mutation_rate=0.1) -> torch.Tensor:
        noise = torch.randn_like(seed_tensor) * mutation_rate
        return seed_tensor + noise
