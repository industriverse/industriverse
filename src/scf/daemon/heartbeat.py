import json
import time
from pathlib import Path

class DaemonHeartbeat:
    def __init__(self, status_file="data/scf/status.json"):
        self.status_file = Path(status_file)
        self.status_file.parent.mkdir(parents=True, exist_ok=True)

    def pulse(self, state: dict):
        state["timestamp"] = time.time()
        self.status_file.write_text(json.dumps(state))
