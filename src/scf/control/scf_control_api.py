import asyncio
import json
import logging
from pathlib import Path
from typing import Any

LOG = logging.getLogger("SCF.ControlAPI")

class SCFControlAPI:
    def __init__(self, control_file_path: str):
        self.control_file = Path(control_file_path)
        self.control_file.parent.mkdir(parents=True, exist_ok=True)

    async def start_listener(self, daemon_instance: Any):
        """
        Polls the control file for commands.
        In a real implementation, this might be a FastAPI server or a more robust queue.
        """
        LOG.info("Control API listening on %s", self.control_file)
        while True:
            if self.control_file.exists():
                try:
                    content = self.control_file.read_text()
                    if content.strip():
                        cmd = json.loads(content)
                        await self._process_command(daemon_instance, cmd)
                        # Clear file after processing to acknowledge
                        self.control_file.unlink()
                except Exception as e:
                    LOG.error("Error processing control file: %s", e)
            
            await asyncio.sleep(1) # Poll interval

    async def _process_command(self, daemon, cmd_dict):
        command = cmd_dict.get("command")
        payload = cmd_dict.get("payload", {})
        
        LOG.info("Received Control Command: %s", command)
        
        if command == "SHIFT_GEAR":
            daemon.set_gear(payload.get("level", "STANDARD"))
        elif command == "STOP":
            await daemon.stop()
        elif command == "RUN_ONCE":
            # Force a cycle immediately
            await daemon.loop_once()
        elif command == "RELEASE_MODEL":
            daemon.releaser.attempt_release()
        else:
            LOG.warning("Unknown command: %s", command)
