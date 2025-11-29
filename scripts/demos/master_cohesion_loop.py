import sys
import os
import time
import subprocess
import logging
import json

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data/cohesion_loop.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("CohesionLoop")

class MasterCohesionLoop:
    """
    Orchestrates the Full Loop: AI Shield -> HRAE -> Data Hub.
    """
    def __init__(self):
        self.root_dir = os.getcwd()
        self.daemon_process = None
        
    def start_daemon(self):
        logger.info("Step 1: Starting Data Hub Collector Daemon...")
        cmd = ["python3", "src/datahub/collector_daemon.py"]
        self.daemon_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(2) # Warmup
        if self.daemon_process.poll() is None:
            logger.info("   ✅ Daemon Running (PID: {})".format(self.daemon_process.pid))
        else:
            logger.error("   ❌ Daemon Failed to Start")

    def run_hrae_autopilot(self):
        logger.info("Step 2: Engaging HRAE Autopilot (The 'Action')...")
        # We run the HRAE core script
        cmd = ["node", "src/models/hrae_core.js"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            logger.info("   HRAE Output:\n" + result.stdout)
            if result.returncode == 0:
                logger.info("   ✅ HRAE Sequence Complete.")
            else:
                logger.error("   ❌ HRAE Failed.")
        except Exception as e:
            logger.error(f"   ❌ HRAE Execution Error: {e}")

    def verify_data_hub(self):
        logger.info("Step 3: Verifying Data Hub Ingestion...")
        # Check if shards were created
        raw_dir = "data/datahub/raw"
        shards = [f for f in os.listdir(raw_dir) if f.endswith(".json")]
        if len(shards) > 0:
            logger.info(f"   ✅ Data Hub captured {len(shards)} shards during operation.")
            logger.info(f"   Sample Shard: {shards[0]}")
        else:
            logger.warning("   ⚠️ No shards found. Daemon might not have captured HRAE events.")

    def stop_daemon(self):
        if self.daemon_process:
            logger.info("Step 4: Stopping Daemon...")
            self.daemon_process.terminate()
            self.daemon_process.wait()
            logger.info("   ✅ Daemon Stopped.")

    def run_full_loop(self):
        logger.info("========================================")
        logger.info("🔄 STARTING MASTER COHESION LOOP")
        logger.info("========================================")
        
        try:
            self.start_daemon()
            self.run_hrae_autopilot()
            time.sleep(2) # Allow daemon to catch up
            self.verify_data_hub()
        finally:
            self.stop_daemon()
            
        logger.info("========================================")
        logger.info("✅ COHESION LOOP COMPLETE")
        logger.info("========================================")

if __name__ == "__main__":
    loop = MasterCohesionLoop()
    loop.run_full_loop()
