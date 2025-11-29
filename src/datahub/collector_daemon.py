import time
import json
import os
import random
import logging
import signal
import sys
from typing import Dict, Any

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data/datahub/collector.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("CollectorDaemon")

class CollectorDaemon:
    """
    Industriverse Data Hub: Collector Daemon (Production Ready).
    
    Purpose:
    Runs 24/7 to collect system telemetry and generate data shards.
    Robustness: Logging, Error Handling, Graceful Shutdown.
    """
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {
            "output_dir": "data/datahub/raw",
            "interval_seconds": 0.5,
            "max_shards_per_run": 1000 # Safety limit for demo
        }
        self.output_dir = self.config["output_dir"]
        os.makedirs(self.output_dir, exist_ok=True)
        self.is_running = False
        
        # Handle Signals
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)

    def handle_signal(self, signum, frame):
        logger.info(f"Received signal {signum}. Shutting down...")
        self.stop()

    def start(self):
        self.is_running = True
        logger.info("📡 Data Hub Collector Daemon Started.")
        logger.info(f"   Target: {self.output_dir}")
        logger.info(f"   Interval: {self.config['interval_seconds']}s")
        
        try:
            self.run_loop()
        except Exception as e:
            logger.critical(f"🔥 Critical Failure: {e}", exc_info=True)
        finally:
            self.stop()
        
    def stop(self):
        self.is_running = False
        logger.info("🛑 Data Hub Collector Daemon Stopped.")

    def run_loop(self):
        """
        Continuous collection loop.
        """
        count = 0
        while self.is_running:
            if count >= self.config["max_shards_per_run"]:
                logger.info("Reached max shards limit. Stopping.")
                break
                
            try:
                data_packet = self.collect_system_state()
                self.save_packet(data_packet)
                count += 1
            except Exception as e:
                logger.error(f"Error in collection loop: {e}")
                
            time.sleep(self.config["interval_seconds"])

    def collect_system_state(self) -> Dict[str, Any]:
        """
        Gather data from subsystems.
        """
        # Mock Data Sources
        return {
            "timestamp": time.time(),
            "source": random.choice(["SIMULATOR", "AI_SHIELD", "CAPSULE_A2A", "ROBOTICS"]),
            "energy_state": {
                "joules": random.uniform(100, 500),
                "entropy": random.uniform(0.1, 0.9)
            },
            "event_type": "OPTIMIZATION_STEP",
            "payload": {
                "action_vector": [random.random() for _ in range(3)],
                "safety_score": random.uniform(0.8, 1.0)
            }
        }

    def save_packet(self, packet: Dict[str, Any]):
        """
        Saves the data packet as a JSON shard.
        """
        filename = f"shard_{int(packet['timestamp']*1000)}_{packet['source']}.json"
        path = os.path.join(self.output_dir, filename)
        
        try:
            with open(path, 'w') as f:
                json.dump(packet, f)
            logger.debug(f"Saved shard: {filename}")
        except IOError as e:
            logger.error(f"Failed to write shard {filename}: {e}")

if __name__ == "__main__":
    # Example Config
    config = {
        "output_dir": "data/datahub/raw",
        "interval_seconds": 0.2,
        "max_shards_per_run": 10
    }
    daemon = CollectorDaemon(config)
    daemon.start()
