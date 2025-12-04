import torch
import logging
from typing import Any, Tuple

LOG = logging.getLogger("SCF.ResumeExecutor")

class ResumeExecutor:
    def __init__(self, checkpoint_manager):
        self.ckpt_manager = checkpoint_manager

    def restore_state(self, 
                      model: torch.nn.Module, 
                      optimizer: torch.optim.Optimizer, 
                      scheduler: Any) -> Tuple[int, int]:
        """
        Restores model, optimizer, scheduler, and RNG states.
        Returns (start_step, fossil_offset).
        """
        state = self.ckpt_manager.load_latest()
        if not state:
            LOG.info("No checkpoint found. Starting from scratch.")
            return 0, 0

        try:
            model.load_state_dict(state["model_state_dict"])
            optimizer.load_state_dict(state["optimizer_state_dict"])
            if scheduler and state.get("scheduler_state_dict"):
                scheduler.load_state_dict(state["scheduler_state_dict"])
            
            if state.get("rng_state_torch") is not None:
                torch.set_rng_state(state["rng_state_torch"])
            if state.get("rng_state_cuda") is not None and torch.cuda.is_available():
                torch.cuda.set_rng_state_all(state["rng_state_cuda"])
            
            step = state.get("step", 0)
            offset = state.get("fossil_offset", 0)
            
            LOG.info("Restored state at step %d, offset %d", step, offset)
            return step, offset

        except Exception as e:
            LOG.error("Failed to restore checkpoint: %s", e)
            LOG.warning("Starting from scratch due to corruption.")
            return 0, 0
