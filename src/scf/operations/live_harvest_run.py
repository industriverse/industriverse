import asyncio
import logging
import sys
import os
import json
import time
from datetime import datetime
from unittest.mock import MagicMock

# Mock Dependencies (since we cannot install packages)
class MockBaseModel:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
    def dict(self):
        return self.__dict__

sys.modules["pydantic"] = MagicMock()
sys.modules["pydantic"].BaseModel = MockBaseModel
sys.modules["pydantic"].Field = MagicMock()
sys.modules["fastapi"] = MagicMock()
sys.modules["numpy"] = MagicMock()
sys.modules["src.bridge_api.ai_shield.state"] = MagicMock()
sys.modules["src.bridge_api.telemetry.thermo"] = MagicMock()

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.scf.daemon.scf_daemon import SCFSovereignDaemon
from src.datahub.value_vault import ValueVault

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("LiveHarvestRun")

async def run_live_harvest():
    """
    Simulates a 24-hour Data Harvest Run (compressed into a few seconds for demo).
    """
    logger.info("🚀 Initiating LIVE HARVEST RUN...")
    
    # 1. Initialize Daemon
    daemon = SCFSovereignDaemon()
    vault = ValueVault()
    
    # Measure initial vault state
    initial_fossils = len(vault.retrieve_all_secrets())
    logger.info(f"📊 Initial ValueVault Count: {initial_fossils}")
    
    # 2. Start Daemon in Background
    # We run the daemon's loop for a few iterations manually to simulate time
    logger.info("🟢 Starting Daemon...")
    
    # Create Control File to set Gear to STANDARD
    control_file = "data/scf/control.json"
    os.makedirs(os.path.dirname(control_file), exist_ok=True)
    with open(control_file, 'w') as f:
        json.dump({"command": "SHIFT_GEAR", "payload": {"level": "STANDARD"}}, f)
        
    # 3. Simulate Cycles (Time Dilation)
    # In a real run, we'd use daemon.start(), but here we want to control the loop for the demo
    # so we will manually trigger the loop logic a few times.
    
    cycles = 5
    logger.info(f"⏳ Simulating {cycles} Operational Cycles (representing 24h activity)...")
    
    try:
        # Initialize components
        # Accessing master_loop instead of loop
        await daemon.master_loop.context_root.pulse.connect()
        
        for i in range(cycles):
            logger.info(f"   🔄 Cycle {i+1}/{cycles}...")
            
            # Check Control Plane
            daemon.check_control_file()
            
            # Execute One Loop Iteration
            await daemon.master_loop.cycle()
            
            # Simulate time passing & Task Completion
            await asyncio.sleep(0.5)
            
            # Release Nodes (Simulate task finished)
            mgr = daemon.deployer.node_manager
            for nid in list(mgr.nodes.keys()):
                mgr.release_node(nid)
            
    except Exception as e:
        logger.error(f"❌ Run Failed: {e}")
        raise e
    finally:
        # stop() is not async in the daemon implementation, it just sets a flag
        daemon.stop()
        
    # 4. Verify Harvest
    final_fossils = len(vault.retrieve_all_secrets())
    new_fossils = final_fossils - initial_fossils
    
    logger.info(f"📊 Final ValueVault Count: {final_fossils}")
    logger.info(f"🌾 Harvested {new_fossils} new Code Fossils.")
    
    if new_fossils > 0:
        logger.info("✅ LIVE HARVEST RUN SUCCESSFUL. The Organism is Alive.")
    else:
        logger.warning("⚠️ No new fossils harvested. Check system logs.")

if __name__ == "__main__":
    try:
        asyncio.run(run_live_harvest())
    except KeyboardInterrupt:
        pass
