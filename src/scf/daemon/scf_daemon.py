import time
import json
import os
import signal
import sys
import asyncio
import logging
from typing import Dict, Any

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.orchestration.daemon_gears import OrchestrationLevelManager, DaemonLevel
from src.scf.trunk.trifecta_master_loop import TrifectaMasterLoop
from src.scf.roots.context_root import ContextRoot
from src.scf.branches.intent.intent_engine import IntentEngine
from src.scf.branches.build.builder_engine import BuilderEngine
from src.scf.branches.verify.review_engine import ReviewEngine
from src.scf.canopy.deploy.bitnet_autodeploy import BitNetAutoDeploy

# Ensure log directory exists
os.makedirs("data/scf", exist_ok=True)

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data/scf/daemon.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("SCFSovereignDaemon")

class SCFSovereignDaemon:
    """
    The Sovereign Code Foundry Daemon.
    A continuous process that orchestrates the Trifecta Master Loop.
    Managed by the DaemonController via 'Daemon Levels'.
    """
    def __init__(self):
        self.config_dir = "data/scf"
        os.makedirs(self.config_dir, exist_ok=True)
        self.control_file = os.path.join(self.config_dir, "control.json")
        self.heartbeat_file = os.path.join(self.config_dir, "heartbeat.json")
        
        self.is_running = False
        self.is_paused = False
        self.cycles_completed = 0
        
        # Orchestration Manager (Gears)
        self.level_manager = OrchestrationLevelManager()
        self.current_state = self.level_manager.state
        
        # Initialize SCF Components
        self.context_root = ContextRoot()
        self.intent_engine = IntentEngine(None, None) # Placeholder args
        self.builder_engine = BuilderEngine(None, None) # Placeholder args
        self.reviewer = ReviewEngine()
        self.deployer = BitNetAutoDeploy()
        
        self.master_loop = TrifectaMasterLoop(
            self.context_root, 
            self.intent_engine, 
            self.builder_engine, 
            self.reviewer, 
            self.deployer
        )
        
        # Handle Signals
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)

    def handle_signal(self, signum, frame):
        logger.info(f"Received signal {signum}. Shutting down...")
        self.stop()

    def start(self):
        self.is_running = True
        logger.info("🚀 SCF Sovereign Daemon Started.")
        logger.info(f"   Initial Level: {self.current_state.level.name}")
        
        try:
            asyncio.run(self.run_loop())
        except Exception as e:
            logger.critical(f"🔥 Critical Failure: {e}", exc_info=True)
        finally:
            self.stop()

    def stop(self):
        self.is_running = False
        if os.path.exists(self.heartbeat_file):
            try:
                os.remove(self.heartbeat_file)
            except:
                pass
        logger.info("🛑 SCF Sovereign Daemon Stopped.")

    async def run_loop(self):
        """
        Main Event Loop.
        """
        while self.is_running:
            # 1. Check Control Plane
            self.check_control_file()
            
            # 2. Update Heartbeat
            self.write_heartbeat()
            
            # 3. Execute Conscious Cycle
            if not self.is_paused:
                # Apply Daemon Level Parameters to Loop
                self.apply_level_parameters()
                
                logger.info(f"🔄 Starting Cycle {self.cycles_completed + 1} (Level: {self.current_state.level.name})")
                result = await self.master_loop.cycle()
                
                if result.get("status") == "deployed":
                    self.cycles_completed += 1
                    logger.info(f"✅ Cycle Completed. Intent: {result.get('intent')}")
                elif result.get("status") == "error":
                    logger.error(f"❌ Cycle Failed: {result.get('error')}")
                
                # Sleep based on level (Velocity control)
                await asyncio.sleep(self.get_interval_for_level())
            else:
                await asyncio.sleep(1.0)

    def check_control_file(self):
        """
        Reads commands from control.json.
        """
        if not os.path.exists(self.control_file):
            return

        try:
            with open(self.control_file, 'r') as f:
                command_data = json.load(f)
            
            cmd = command_data.get("command")
            logger.info(f"📥 Received Command: {cmd}")
            
            if cmd == "SHIFT_GEAR":
                level_name = command_data.get("payload", {}).get("level", "STANDARD")
                try:
                    level = DaemonLevel[level_name]
                    self.current_state = self.level_manager.set_level(level)
                except KeyError:
                    logger.error(f"Invalid Daemon Level: {level_name}")
            elif cmd == "PAUSE":
                self.is_paused = True
                logger.info("⏸️ Daemon PAUSED.")
            elif cmd == "RESUME":
                self.is_paused = False
                logger.info("▶️ Daemon RESUMED.")
            elif cmd == "STOP":
                self.stop()
                
            os.remove(self.control_file)
            
        except Exception as e:
            logger.error(f"Failed to process control file: {e}")

    def write_heartbeat(self):
        status = {
            "timestamp": time.time(),
            "pid": os.getpid(),
            "status": "PAUSED" if self.is_paused else "RUNNING",
            "level": self.current_state.level.name,
            "cycles_completed": self.cycles_completed,
            "metrics": self.current_state.discovery_metrics
        }
        try:
            with open(self.heartbeat_file, 'w') as f:
                json.dump(status, f)
        except Exception as e:
            logger.error(f"Failed to write heartbeat: {e}")

    def apply_level_parameters(self):
        """
        Propagates current Daemon Level settings to the Master Loop components.
        """
        # Example: Adjust mutation rate in Builder Engine based on level
        mutation_rate = self.current_state.discovery_metrics.get("Mutation_Rate", "Low")
        # In a real impl, we would call: self.builder_engine.set_mutation_rate(mutation_rate)
        pass

    def get_interval_for_level(self) -> float:
        """
        Determines loop interval based on velocity.
        """
        level = self.current_state.level
        if level == DaemonLevel.STANDARD:
            return 5.0
        elif level == DaemonLevel.ACCELERATED:
            return 1.0
        elif level == DaemonLevel.HYPER:
            return 0.1
        elif level == DaemonLevel.SINGULARITY:
            return 0.0 # Max speed
        return 5.0

if __name__ == "__main__":
    daemon = SCFSovereignDaemon()
    daemon.start()
