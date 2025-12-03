import json
import time
import logging
from typing import Dict, Any

logger = logging.getLogger("DashboardExporter")

class DashboardExporter:
    """
    Exposes Sovereign Intelligence metrics for monitoring (e.g., Prometheus/Grafana).
    Writes metrics to a JSON file that can be scraped or polled.
    """
    def __init__(self, metrics_file="data/datahub/dashboard_metrics.json"):
        self.metrics_file = metrics_file
        self.metrics = {
            "system_status": "ONLINE",
            "last_update": time.time(),
            "models": {
                "ebdm_loss": 0.0,
                "tnn_residual": 0.0,
                "gen_n_perplexity": 0.0
            },
            "operations": {
                "cfr_fossils_count": 0,
                "negentropy_minted_total": 0.0,
                "deployments_24h": 0
            }
        }
        self._flush()

    def update_model_metrics(self, ebdm_loss: float, tnn_residual: float, gen_n_ppx: float):
        self.metrics["models"]["ebdm_loss"] = ebdm_loss
        self.metrics["models"]["tnn_residual"] = tnn_residual
        self.metrics["models"]["gen_n_perplexity"] = gen_n_ppx
        self.metrics["last_update"] = time.time()
        self._flush()

    def update_operational_metrics(self, fossils_added: int, negentropy_added: float):
        self.metrics["operations"]["cfr_fossils_count"] += fossils_added
        self.metrics["operations"]["negentropy_minted_total"] += negentropy_added
        self.metrics["operations"]["deployments_24h"] += 1
        self.metrics["last_update"] = time.time()
        self._flush()

    def _flush(self):
        try:
            with open(self.metrics_file, 'w') as f:
                json.dump(self.metrics, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to write dashboard metrics: {e}")

    def get_metrics(self) -> Dict[str, Any]:
        return self.metrics
