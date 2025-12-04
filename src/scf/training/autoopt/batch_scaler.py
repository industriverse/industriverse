import logging
import torch

LOG = logging.getLogger("SCF.BatchScaler")

class BatchScaler:
    def __init__(self, start_batch=32, max_batch=512):
        self.current_batch = start_batch
        self.max_batch = max_batch

    def scale_up(self):
        if self.current_batch * 2 <= self.max_batch:
            self.current_batch *= 2
            LOG.info("Scaling batch size UP to %d", self.current_batch)
            return self.current_batch
        return self.current_batch

    def scale_down(self):
        if self.current_batch > 1:
            self.current_batch //= 2
            LOG.info("Scaling batch size DOWN to %d", self.current_batch)
            return self.current_batch
        return self.current_batch
