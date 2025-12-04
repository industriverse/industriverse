import time
import torch
import logging

LOG = logging.getLogger("SCF.Eval.Performance")

def test_performance(model, input_tensor: torch.Tensor) -> float:
    """
    Measures inference time in milliseconds.
    """
    model.eval()
    noise_level = torch.zeros(input_tensor.size(0), 1).to(input_tensor.device)
    
    start = time.perf_counter()
    with torch.no_grad():
        _ = model(input_tensor, noise_level)
    end = time.perf_counter()
    
    duration_ms = (end - start) * 1000.0
    return duration_ms
