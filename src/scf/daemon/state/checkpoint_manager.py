import torch
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional

LOG = logging.getLogger("SCF.CheckpointManager")

class CheckpointManager:
    def __init__(self, checkpoint_dir: str = "data/model_zoo/checkpoints"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.latest_checkpoint = None

    def save_state(self, 
                   model: torch.nn.Module, 
                   optimizer: torch.optim.Optimizer, 
                   scheduler: Any, 
                   step: int, 
                   fossil_offset: int, 
                   metadata: Dict[str, Any] = None):
        """
        Saves full training state including RNG states.
        """
        state = {
            "step": step,
            "fossil_offset": fossil_offset,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "scheduler_state_dict": scheduler.state_dict() if scheduler else None,
            "rng_state_torch": torch.get_rng_state(),
            "rng_state_cuda": torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None,
            "metadata": metadata or {}
        }
        
        filename = f"ckpt_step_{step}.pt"
        path = self.checkpoint_dir / filename
        
        # Atomic save
        tmp_path = path.with_suffix(".tmp")
        torch.save(state, tmp_path)
        os.rename(tmp_path, path)
        
        self.latest_checkpoint = path
        LOG.info("Saved checkpoint to %s", path)
        
        # Update 'latest' pointer
        latest_link = self.checkpoint_dir / "latest.pt"
        if latest_link.exists():
            latest_link.unlink()
        try:
            latest_link.symlink_to(filename)
        except OSError:
            # Fallback for systems without symlinks
            torch.save(state, latest_link)

    def load_latest(self) -> Optional[Dict[str, Any]]:
        latest_link = self.checkpoint_dir / "latest.pt"
        if latest_link.exists():
            LOG.info("Loading latest checkpoint from %s", latest_link)
            return torch.load(latest_link, map_location="cpu")
        return None
