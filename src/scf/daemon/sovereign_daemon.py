import time
import logging
import subprocess
import os
from pathlib import Path

# Configuration
LOG_FILE = "sovereign_daemon.log"
INGEST_INTERVAL = 3600  # 1 Hour
TRAIN_INTERVAL = 86400  # 24 Hours
RELEASE_INTERVAL = 604800 # 7 Days

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class SovereignDaemon:
    def __init__(self):
        self.running = True
        self.last_ingest = 0
        self.last_train = 0
        self.last_release = 0
        
    def run_command(self, cmd, description):
        logging.info(f"Starting: {description}")
        try:
            subprocess.run(cmd, shell=True, check=True)
            logging.info(f"Completed: {description}")
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed: {description} - {e}")
            return False

    def ingest_loop(self):
        if time.time() - self.last_ingest > INGEST_INTERVAL:
            logging.info("Triggering Ingest Loop...")
            # Call fossilizer logic here (or script)
            # self.run_command("python3 scripts/ingest_fossils.py", "Fossil Ingestion")
            self.last_ingest = time.time()

    def train_loop(self):
        if time.time() - self.last_train > TRAIN_INTERVAL:
            logging.info("Triggering Training Loop...")
            # self.run_command("python3 scripts/train_incremental.py", "Incremental Training")
            self.last_train = time.time()

    def release_loop(self):
        if time.time() - self.last_release > RELEASE_INTERVAL:
            logging.info("Triggering Weekly Release...")
            self.run_command("./scripts/release/weekly_release.sh", "Weekly Release")
            self.last_release = time.time()

    def start(self):
        logging.info("🔥 Sovereign Daemon Started")
        print("🔥 Sovereign Daemon Started (Check sovereign_daemon.log)")
        
        while self.running:
            try:
                self.ingest_loop()
                self.train_loop()
                self.release_loop()
                
                # Heartbeat
                time.sleep(60) 
                
            except KeyboardInterrupt:
                logging.info("Daemon Stopping...")
                self.running = False
            except Exception as e:
                logging.error(f"Daemon Error: {e}")
                time.sleep(60)

if __name__ == "__main__":
    daemon = SovereignDaemon()
    daemon.start()
