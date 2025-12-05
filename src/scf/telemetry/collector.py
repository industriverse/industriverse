import time
import json
import os
from typing import Dict, Any

class TelemetryCollector:
    """
    Unified Telemetry Collector.
    Aggregates metrics from various subsystems (GPU, Energy, Throughput).
    """
    def __init__(self, log_dir: str = "logs/telemetry"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.current_log_file = os.path.join(log_dir, f"metrics_{int(time.time())}.jsonl")

    def log_metric(self, metric_name: str, value: float, tags: Dict[str, str] = None):
        """
        Log a single metric point.
        """
        entry = {
            "timestamp": time.time(),
            "metric": metric_name,
            "value": value,
            "tags": tags or {}
        }
        self._write_entry(entry)

    def log_batch(self, metrics: Dict[str, Any]):
        """
        Log a batch of metrics.
        """
        entry = {
            "timestamp": time.time(),
            "metrics": metrics
        }
        self._write_entry(entry)

    def _write_entry(self, entry: Dict):
        with open(self.current_log_file, 'a') as f:
            f.write(json.dumps(entry) + "\n")

    def get_recent_metrics(self, limit: int = 10) -> list:
        """
        Retrieve recent logs (for dashboard).
        """
        if not os.path.exists(self.current_log_file):
            return []
            
        with open(self.current_log_file, 'r') as f:
            lines = f.readlines()
            return [json.loads(line) for line in lines[-limit:]]
