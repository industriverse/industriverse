import os
import torch
import torch.multiprocessing as mp
import logging

LOG = logging.getLogger("SCF.DDPLauncher")

class DDPLauncher:
    def run(self, fn, world_size, *args):
        """
        Launches the training function `fn` on `world_size` processes.
        fn signature: fn(rank, world_size, *args)
        """
        if world_size < 1:
            LOG.warning("World size < 1, defaulting to 1 (Single GPU/CPU)")
            fn(0, 1, *args)
            return

        os.environ['MASTER_ADDR'] = 'localhost'
        os.environ['MASTER_PORT'] = '12355'
        
        LOG.info(f"Spawning {world_size} processes for DDP...")
        mp.spawn(fn, args=(world_size, *args), nprocs=world_size, join=True)
