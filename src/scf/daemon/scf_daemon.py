import asyncio
import logging
import time
from datetime import datetime
from src.scf.trunk.trifecta_master_loop import TrifectaMasterLoop
from src.scf.control.operator_auth import OperatorAuth
from src.scf.control.scf_control_api import SCFControlAPI
from src.scf.batcher.fossil_batcher import FossilBatcher
from src.scf.training.training_orchestrator import TrainingOrchestrator
from src.scf.release.release_manager import ReleaseManager
from src.scf.safety.emergency_stop import EmergencyStop
from src.scf.audit.audit_logger import AuditLogger

logger = logging.getLogger("SCF_Daemon")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class SCFSovereignDaemon:
    def __init__(self, control_json_path="data/scf/control.json"):
        self.master_loop = TrifectaMasterLoop()
        self.control_api = SCFControlAPI(control_json_path)
        self.auth = OperatorAuth()
        self.batcher = FossilBatcher()
        self.trainer = TrainingOrchestrator()
        self.releaser = ReleaseManager()
        self.emergency = EmergencyStop()
        self.audit = AuditLogger()
        self.gear = "STANDARD"  # STANDARD | ACCELERATED | HYPER | SINGULARITY
        self.heartbeat = 5  # seconds, overridden by gears
        self._running = False

    def set_gear(self, gear):
        logger.info("⚙️ SHIFTING GEARS: %s -> %s", self.gear, gear)
        self.audit.record("SHIFT_GEAR", {"from": self.gear, "to": gear})
        self.gear = gear
        if gear == "STANDARD":
            self.heartbeat = 5
        elif gear == "ACCELERATED":
            self.heartbeat = 1
        elif gear == "HYPER":
            self.heartbeat = 0.1
        elif gear == "SINGULARITY":
            self.heartbeat = 0.01

    async def loop_once(self):
        # Pre-flight safety check
        if self.emergency.is_active():
            logger.critical("Emergency stop active — halting loop.")
            self.audit.record("LOOP_HALTED", {"reason":"emergency_stop"})
            return

        # 1) ingest small batch of fossils (non-blocking)
        # In a real run, we might limit this to avoid IO blocking the loop too long
        new = self.batcher.ingest_stream(batch_target_count=10)
        if new:
            logger.info("Ingested %d fossils", new)
            self.audit.record("FOSSIL_INGEST", {"count": new})

        # 2) check if training should run
        if self.batcher.ready_for_training():
            batch = self.batcher.build_batch()
            if batch:
                logger.info("Built batch with %d fossils", len(batch["samples"]))
                self.audit.record("BATCH_CREATED", {"size": len(batch["samples"])})
                # schedule training asynchronously
                asyncio.create_task(self.trainer.train_on_batch(batch))

        # 3) run one master loop cycle (orchestrates intent->build->verify->deploy)
        await self.master_loop.cycle()

        # 4) evaluate for release (run daily gate)
        if self.releaser.should_try_release():
            self.releaser.attempt_release()

    async def start(self):
        logger.info("🟢 Starting SCF Sovereign Daemon")
        self._running = True
        self.audit.record("DAEMON_START", {"time": str(datetime.utcnow())})
        
        # Start Control API listener
        control_task = asyncio.create_task(self.control_api.start_listener(self))
        
        try:
            while self._running:
                start = time.time()
                await self.loop_once()
                elapsed = time.time() - start
                wait = max(self.heartbeat - elapsed, 0)
                await asyncio.sleep(wait)
        except asyncio.CancelledError:
            logger.info("Daemon cancelled.")
        finally:
            logger.info("🛑 SCF Sovereign Daemon Stopped.")
            self.audit.record("DAEMON_STOP", {"time": str(datetime.utcnow())})
            control_task.cancel()

    async def stop(self):
        logger.info("Received stop; shutting down after current cycle.")
        self._running = False

if __name__ == "__main__":
    daemon = SCFSovereignDaemon()
    try:
        asyncio.run(daemon.start())
    except KeyboardInterrupt:
        pass
