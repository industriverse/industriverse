from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import threading
import time
import os


@dataclass
class UTIDRecord:
    utid: str
    issued_at_ms: int
    context_digest: str
    context: Optional[Dict[str, Any]]


class UTIDRegistry:
    """
    Simple registry for issued UTIDs.
    Thread-safe; persists to disk for auditability.
    """

    def __init__(self, store_path: Optional[str] = None):
        self._lock = threading.Lock()
        self._records: List[UTIDRecord] = []
        self.store_path = store_path or os.environ.get("UTID_STORE_PATH", "data/utids.jsonl")
        self._ensure_store()
        self._load_existing()

    def add(self, utid: str, context_digest: str, context: Optional[Dict[str, Any]]) -> None:
        issued_at = int(time.time() * 1000)
        record = UTIDRecord(utid=utid, issued_at_ms=issued_at, context_digest=context_digest, context=context)
        with self._lock:
            self._records.append(record)
            self._append_to_disk(record)

    def list(self, limit: int = 50, offset: int = 0, context_digest: Optional[str] = None, context_contains: Optional[str] = None) -> List[UTIDRecord]:
        with self._lock:
            filtered = [
                r
                for r in self._records
                if (context_digest is None or r.context_digest == context_digest)
                and (context_contains is None or (r.context and context_contains in json.dumps(r.context)))
            ]
            start = max(len(filtered) - offset - limit, 0)
            end = len(filtered) - offset if offset == 0 else len(filtered) - offset
            return list(filtered[start:end])

    def _ensure_store(self):
        os.makedirs(os.path.dirname(self.store_path), exist_ok=True) if os.path.dirname(self.store_path) else None
        if not os.path.exists(self.store_path):
            open(self.store_path, "a").close()

    def _append_to_disk(self, record: UTIDRecord):
        try:
            with open(self.store_path, "a") as f:
                f.write(json.dumps(record.__dict__) + "\n")
        except Exception:
            pass

    def _load_existing(self):
        if not os.path.exists(self.store_path):
            return
        try:
            with open(self.store_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    data = json.loads(line)
                    self._records.append(
                        UTIDRecord(
                            utid=data.get("utid"),
                            issued_at_ms=data.get("issued_at_ms"),
                            context_digest=data.get("context_digest"),
                            context=data.get("context"),
                        )
                    )
        except Exception:
            self._records = []
