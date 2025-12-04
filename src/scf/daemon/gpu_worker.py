import argparse
import logging
import time
import os
import subprocess
import json
import uuid
from pathlib import Path

from src.scf.config import EXTERNAL_DRIVE, MODEL_ZOO

LOG = logging.getLogger("SCF.GPUWorker")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def run_training(fossil_file: Path, job_id: str):
    LOG.info("👷 GPU Worker Started | Job: %s | Fossil: %s", job_id, fossil_file.name)
    
    # Ensure output directory exists
    MODEL_ZOO.mkdir(parents=True, exist_ok=True)
    
    ckpt_out = MODEL_ZOO / f"ckpt-{job_id}-{int(time.time())}.pt"
    
    # Construct command to run train_ebdm.py as a module
    # We assume the worker is running in the root of the repo
    
    import sys
    cmd = [
        sys.executable, "-m", "src.scf.training.train_ebdm",
        "--fossil", str(fossil_file),
        "--out", str(ckpt_out),
        "--epochs", "1",
        "--batch_size", "32", # Smaller batch for local testing
        "--fossils", "1"      # Just process this one fossil file (or small set)
    ]
    
    LOG.info("   Executing: %s", " ".join(cmd))
    
    try:
        subprocess.run(cmd, check=True)
        LOG.info("✅ Training Job Complete. Checkpoint: %s", ckpt_out.name)
        return ckpt_out
    except subprocess.CalledProcessError as e:
        LOG.error("❌ Training Failed: %s", e)
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("fossil", help="Path to the fossil file")
    parser.add_argument("--job", required=True, help="Job ID")
    
    args = parser.parse_args()
    
    fossil_path = Path(args.fossil)
    if not fossil_path.exists():
        LOG.error("Fossil file not found: %s", fossil_path)
        exit(1)
        
    run_training(fossil_path, args.job)
