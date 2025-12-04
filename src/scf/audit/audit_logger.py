import logging
import json
import time
from pathlib import Path

class AuditLogger:
    def __init__(self, log_dir="data/scf/audit_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger("SCF.Audit")

    def record(self, event_type: str, details: dict):
        entry = {
            "timestamp": time.time(),
            "event": event_type,
            "details": details
        }
        # Log to file
        log_file = self.log_dir / f"audit-{time.strftime('%Y-%m-%d')}.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
        
        self.logger.info("AUDIT: %s %s", event_type, details)
