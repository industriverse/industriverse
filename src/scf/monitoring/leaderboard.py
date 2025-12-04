import json
import logging
from pathlib import Path
from typing import List, Dict

LOG = logging.getLogger("SCF.Leaderboard")

class Leaderboard:
    def __init__(self, db_path="data/scf/leaderboard.json"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.entries = self._load()

    def _load(self) -> List[Dict]:
        if self.db_path.exists():
            return json.loads(self.db_path.read_text())
        return []

    def update(self, eval_report_path: str):
        report = json.loads(Path(eval_report_path).read_text())
        entry = {
            "model_id": report["model_id"],
            "score": report["metrics"]["composite_score"],
            "metrics": report["metrics"],
            "timestamp": report.get("timestamp", "")
        }
        self.entries.append(entry)
        # Sort by score desc
        self.entries.sort(key=lambda x: x["score"], reverse=True)
        self._save()
        LOG.info("Leaderboard updated. Top model: %s (%.1f)", self.entries[0]["model_id"], self.entries[0]["score"])

    def _save(self):
        self.db_path.write_text(json.dumps(self.entries, indent=2))
