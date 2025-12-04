import torch
from src.scf.discovery.novelty.novelty_search import NoveltySearchEngine

def test_novelty(output_tensor: torch.Tensor, novelty_engine: NoveltySearchEngine) -> float:
    """
    Scores the novelty of the output using the NoveltySearchEngine.
    Returns novelty score [0.0, 1.0].
    """
    # Flatten if needed
    embedding = output_tensor.view(output_tensor.size(0), -1)
    
    # Use the engine to score
    score = novelty_engine.score_novelty(embedding)
    
    return score
