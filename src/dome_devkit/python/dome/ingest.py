import logging
import random
import time
from typing import Iterator, Dict, Any

logger = logging.getLogger(__name__)

class CSIIngestor:
    """
    Ingests Channel State Information (CSI) frames.
    Supports simulation mode for dev/test.
    """
    def __init__(self, source: str = "simulation"):
        self.source = source
        logger.info(f"CSIIngestor initialized with source: {source}")

    def stream(self) -> Iterator[Dict[str, Any]]:
        """
        Yields simulated CSI frames.
        """
        while True:
            # Simulate a frame
            frame = {
                "timestamp": time.time(),
                "source_id": "sim_router_01",
                "amplitude": [random.uniform(0, 1) for _ in range(64)],
                "phase": [random.uniform(-3.14, 3.14) for _ in range(64)],
                "num_subcarriers": 64,
                "num_antennas": 2,
                "sampling_rate": 100.0
            }
            yield frame
            time.sleep(0.1) # 10Hz simulation
