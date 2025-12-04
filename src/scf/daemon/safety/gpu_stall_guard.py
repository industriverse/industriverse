import time
import logging
from typing import Optional

LOG = logging.getLogger("SCF.GPUStallGuard")

class GPUStallGuard:
    def __init__(self, stall_threshold_seconds: int = 120, min_gpu_util: float = 10.0):
        self.stall_threshold = stall_threshold_seconds
        self.min_gpu_util = min_gpu_util
        self.last_activity = time.time()
        self.last_loss = None
        self.stagnant_steps = 0

    def tick(self, current_loss: Optional[float] = None):
        """Call this every training step."""
        now = time.time()
        self.last_activity = now
        
        if current_loss is not None:
            if self.last_loss is not None and abs(current_loss - self.last_loss) < 1e-6:
                self.stagnant_steps += 1
            else:
                self.stagnant_steps = 0
            self.last_loss = current_loss

    def check_health(self) -> bool:
        """Returns False if stalled."""
        # 1. Check time since last tick
        if time.time() - self.last_activity > self.stall_threshold:
            LOG.error("GPU STALL DETECTED: No activity for %d seconds", time.time() - self.last_activity)
            return False
        
        # 2. Check loss stagnation
        if self.stagnant_steps > 200:
            LOG.error("TRAINING STAGNATION: Loss unchanged for 200 steps")
            return False
            
        # 3. GPU Util check (requires pynvml or similar, stubbed here)
        # util = get_gpu_util() 
        # if util < self.min_gpu_util: return False
        
        return True
