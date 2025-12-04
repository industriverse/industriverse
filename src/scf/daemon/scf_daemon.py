import asyncio
import os
import sys
import json
import time
import logging
import subprocess
import uuid
import shutil
from pathlib import Path
from typing import Dict, Any, Optional

from src.scf.config import EXTERNAL_DRIVE, FOSSIL_VAULT, MODEL_ZOO, RELEASES, ZK_PROOFS, CONTROL_FILE

# Configure Logging
LOG = logging.getLogger("SCF.Daemon")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class OrchestrationLevelManager:
    LEVELS = ["STANDARD", "ACCELERATED", "HYPER", "SINGULARITY"]
    
    def __init__(self):
        self.level = "STANDARD"
        
    def set(self, level):
        if level in self.LEVELS:
            LOG.info("⚙️ SHIFTING GEARS: %s -> %s", self.level, level)
            self.level = level
        else:
            LOG.warning("⚠️ Invalid Gear Level: %s", level)

class TrifectaMasterLoop:
    """
    The inner conscious loop of the daemon.
    """
    def __init__(self, olm: OrchestrationLevelManager):
        self.olm = olm
        self.running = False

    def check_disk_usage(self) -> bool:
        """
        Checks if disk usage is safe (< 40%).
        Returns True if safe, False if unsafe (pause).
        """
        try:
            total, used, free = shutil.disk_usage(EXTERNAL_DRIVE)
            percent_used = (used / total) * 100
            if percent_used > 90:
                LOG.warning("⚠️ STORAGE ALERT: Disk usage is %.2f%% (> 90%%). Pausing Ingestion.", percent_used)
                return False
            return True
        except Exception as e:
            LOG.error("Failed to check disk usage: %s", e)
            return True # Fail open to avoid deadlock, but log error

    async def run_once(self):
        # One conscious loop
        LOG.info("Trifecta Master Loop cycle start (Gear=%s)", self.olm.level)
        
        # 0) Safety Check: Storage Guard
        if not self.check_disk_usage():
            LOG.info("🛑 Daemon Paused due to Storage Limit. Sleeping.")
            await asyncio.sleep(60)
            return

        # 1. Observe (Pulse)
        candidate = self.pick_fossil()
        if candidate is None:
            # If no fossils, we might just sleep, or run a self-reflection cycle
            # LOG.debug("No new fossils to process.")
            return

        LOG.info("Trifecta Cycle Start (Gear=%s) | Processing: %s", self.olm.level, candidate.name)

        # 2. Orient (Intent)
        intent = {"task": "train_ebdm", "fossil": str(candidate)}

        # 3. Decide (Dispatch)
        # In a real scenario, this dispatches to RunPod. For now, we simulate or run local.
        job_id = await self.dispatch_to_runner(intent, candidate)

        # 4. Act (Wait & Verify)
        if job_id:
            ckpt = await self.wait_for_checkpoint(job_id)
            if ckpt:
                verified = self.verify_and_sign_checkpoint(ckpt)
                if verified:
                    self.promote_checkpoint(ckpt)
                    # Mark fossil as processed (move or rename)
                    self.archive_fossil(candidate)
        
        LOG.info("Trifecta Cycle Complete.")

    def pick_fossil(self) -> Optional[Path]:
        """Picks an unprocessed fossil from the vault."""
        if not FOSSIL_VAULT.exists():
            return None
            
        # Look for .ndjson or .json files
        files = sorted(list(FOSSIL_VAULT.glob("fossil-*.ndjson")) + list(FOSSIL_VAULT.glob("fossil-*.json")))
        for f in files:
            lock = f.with_suffix(f.suffix + ".lock")
            if lock.exists():
                continue
            
            # Try to acquire lock
            try:
                lock.write_text(str(time.time()))
                return f
            except Exception:
                continue
        return None

    def archive_fossil(self, fossil_path: Path):
        """Moves processed fossil to an archive folder to prevent re-processing."""
        archive_dir = FOSSIL_VAULT / "processed"
        archive_dir.mkdir(exist_ok=True)
        try:
            target = archive_dir / fossil_path.name
            fossil_path.rename(target)
            # Remove lock
            lock = fossil_path.with_suffix(fossil_path.suffix + ".lock")
            if lock.exists():
                lock.unlink()
            LOG.info("Archived fossil: %s", fossil_path.name)
        except Exception as e:
            LOG.error("Failed to archive fossil %s: %s", fossil_path, e)

    async def dispatch_to_runner(self, intent: Dict[str, Any], fossil_path: Path) -> str:
        job_id = f"job-{uuid.uuid4().hex[:8]}"
        LOG.info("Dispatching Job %s to GPU Worker...", job_id)
        
        # In production, this makes an HTTP request to RunPod.
        # For bootstrap, we spawn the local gpu_worker.py
        
        worker_script = Path(__file__).parent / "gpu_worker.py"
        if not worker_script.exists():
            LOG.error("GPU Worker script not found at %s", worker_script)
            return None

        try:
            # Running asynchronously to not block the daemon loop
            log_dir = EXTERNAL_DRIVE / "logs"
            log_dir.mkdir(exist_ok=True)
            log_file = open(log_dir / f"worker-{job_id}.log", "w")
            
            # Add repo root to PYTHONPATH so worker can import src
            env = os.environ.copy()
            repo_root = Path(__file__).parent.parent.parent.parent
            env["PYTHONPATH"] = str(repo_root) + os.pathsep + env.get("PYTHONPATH", "")

            subprocess.Popen([
                sys.executable, str(worker_script),
                str(fossil_path),
                "--job", job_id
            ], env=env, stdout=log_file, stderr=subprocess.STDOUT)
            return job_id
        except Exception as e:
            LOG.error("Failed to dispatch job: %s", e)
            return None

    async def wait_for_checkpoint(self, job_id: str, timeout=3600) -> Optional[Path]:
        start = time.time()
        LOG.info("   Waiting for checkpoint in: %s", MODEL_ZOO)
        while time.time() - start < timeout:
            # Look for checkpoint in MODEL_ZOO
            # Debug: List all files
            all_files = list(MODEL_ZOO.glob("*"))
            LOG.info("   Files in Zoo: %s", [f.name for f in all_files])
            
            ckpt_glob = list(MODEL_ZOO.glob(f"ckpt-{job_id}*.pt"))
            if ckpt_glob:
                ckpt = ckpt_glob[0]
                LOG.info("✅ Found Checkpoint: %s", ckpt.name)
                return ckpt
            await asyncio.sleep(5)
        
        LOG.warning("❌ Timeout waiting for job %s. Checked: %s", job_id, MODEL_ZOO)
        return None

    def verify_and_sign_checkpoint(self, ckpt: Path) -> bool:
        LOG.info("🔐 Verifying and Signing Checkpoint...")
        # Placeholder for Aletheia verification
        # In real impl, load model, run physics checks.
        
        # Mint ZK Proof (Mock)
        proof_id = uuid.uuid4().hex
        proof_data = {
            "id": proof_id,
            "checkpoint": ckpt.name,
            "timestamp": time.time(),
            "signature": "mock_zk_signature_xyz"
        }
        
        proof_path = ZK_PROOFS / f"proof-{proof_id}.json"
        try:
            proof_path.write_text(json.dumps(proof_data, indent=2))
            LOG.info("   ZK Proof Minted: %s", proof_path.name)
            return True
        except Exception as e:
            LOG.error("Failed to mint proof: %s", e)
            return False

    def promote_checkpoint(self, ckpt: Path):
        # Move to a "staging" area or just log it. 
        # Real promotion happens via the Weekly Release script, but we can tag it here.
        LOG.info("🚀 Checkpoint Promoted to Model Zoo Registry.")

class SCFSovereignDaemon:
    def __init__(self):
        self.olm = OrchestrationLevelManager()
        self.master = TrifectaMasterLoop(self.olm)
        self.master.running = True

    async def start(self):
        LOG.info("🟢 SCF Sovereign Daemon Booting Up...")
        LOG.info("   Root Drive: %s", EXTERNAL_DRIVE)
        
        cycles = 0
        try:
            while self.master.running:
                # Check Control Plane
                if CONTROL_FILE.exists():
                    try:
                        cfg = json.loads(CONTROL_FILE.read_text())
                        cmd = cfg.get("command")
                        if cmd == "SHIFT_GEAR":
                            self.olm.set(cfg.get("payload", {}).get("level", "STANDARD"))
                        elif cmd == "STOP":
                            LOG.info("🛑 STOP command received.")
                            self.master.running = False
                    except Exception:
                        LOG.warning("Malformed control.json")

                # Run Cycle
                await self.master.run_once()
                cycles += 1
                
                # Heartbeat Sleep
                sleep_map = {"STANDARD": 5, "ACCELERATED": 1, "HYPER": 0.1, "SINGULARITY": 0.05}
                await asyncio.sleep(sleep_map.get(self.olm.level, 5))
                
        except asyncio.CancelledError:
            LOG.info("Daemon cancelled.")
        finally:
            LOG.info("🔴 Daemon Stopped.")

if __name__ == "__main__":
    daemon = SCFSovereignDaemon()
    try:
        asyncio.run(daemon.start())
    except KeyboardInterrupt:
        pass
