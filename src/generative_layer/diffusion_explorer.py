import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class DiffusionExplorer:
    """
    Diffusion Explorer.
    Visualizes the geometric intuition and generation path of diffusion models.
    """
    def __init__(self):
        self.history = []
        
    def track_step(self, step: int, latent_state: List[float], energy: float):
        """
        Track a single step in the diffusion process.
        """
        self.history.append({
            "step": step,
            "latent_norm": sum([x**2 for x in latent_state])**0.5 if latent_state else 0,
            "energy": energy
        })
        
    def visualize_path(self) -> str:
        """
        Generate a text-based visualization of the generation path.
        """
        if not self.history:
            return "No history to visualize."
            
        viz = "Diffusion Path Visualization:\n"
        viz += "Step | Energy | Latent Norm\n"
        viz += "-----|--------|------------\n"
        
        for entry in self.history:
            viz += f"{entry['step']:4d} | {entry['energy']:.4f} | {entry['latent_norm']:.4f}\n"
            
        return viz
