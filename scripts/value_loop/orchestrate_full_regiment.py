#!/usr/bin/env python3
"""
Script 7: orchestrate_full_regiment.py
Purpose: Continuous Integration / Continuous Value. Runs the Strike Loop for all active contracts.
Usage: python orchestrate_full_regiment.py
"""

import sys
import os
import time
import logging
import subprocess
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Active Contracts (Domains to optimize)
CONTRACTS = [
    "fusion",
    "grid",
    "wafer",
    "battery",
    "robotics"
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_strike(domain):
    logger.info(f"🚀 Launching Strike Loop for: {domain}")
    cmd = f"python {os.path.join(BASE_DIR, 'run_client_strike_loop.py')} --domain {domain}"
    try:
        subprocess.run(cmd, shell=True, check=True)
        logger.info(f"✅ Strike Loop Successful: {domain}")
    except subprocess.CalledProcessError:
        logger.error(f"❌ Strike Loop Failed: {domain}")

def main():
    logger.info("🏭 STARTING INDUSTRIVERSE REGIMENT ORCHESTRATOR")
    logger.info("===============================================")
    
    while True:
        # Pick a random contract to "service"
        domain = random.choice(CONTRACTS)
        
        run_strike(domain)
        
        # Wait before next job
        delay = 5
        logger.info(f"💤 Sleeping for {delay}s...")
        time.sleep(delay)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Orchestrator stopped by user.")
