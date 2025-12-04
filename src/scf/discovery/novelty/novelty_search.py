import torch

class NoveltySearchEngine:
    def __init__(self):
        self.archive = []

    def score_novelty(self, embedding: torch.Tensor) -> float:
        if not self.archive:
            return 1.0
            
        # Compute cosine distance to nearest neighbor in archive
        # embedding: [1, D], archive: [N, D]
        archive_tensor = torch.stack(self.archive).to(embedding.device)
        
        # Cosine similarity: (A . B) / (|A| |B|)
        sim = torch.nn.functional.cosine_similarity(embedding, archive_tensor, dim=1)
        max_sim = sim.max().item()
        
        # Novelty = 1 - max_similarity
        return 1.0 - max_sim

    def add_to_archive(self, embedding: torch.Tensor):
        self.archive.append(embedding.detach().cpu())
