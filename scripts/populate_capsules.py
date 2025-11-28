"""
Capsule population scaffold.

Steps this script should perform (fill in with real registry/object store clients):
- Read capsules manifest (JSON/YAML) describing capsule metadata, manifests, and credit info.
- Upload artifacts to object store (e.g., MinIO/S3).
- Register capsule with Registry API (URI, UTID, credit metadata, locations).
- Optionally seed ledger entries and emit registration events.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)


def load_manifest(path: Path) -> List[Dict]:
    with path.open() as f:
        return json.load(f)


def upload_artifact(path: Path) -> str:
    """
    Placeholder: implement upload to object store and return URL.
    """
    logger.info("Uploading %s (stub)", path)
    return f"file://{path}"


def register_capsule(entry: Dict) -> None:
    """
    Placeholder: POST to registry service.
    """
    logger.info("Registering capsule %s (stub)", entry.get("uri"))


def populate(manifest_path: str) -> None:
    capsules = load_manifest(Path(manifest_path))
    for capsule in capsules:
        artifacts = capsule.get("artifacts", [])
        uploaded = [upload_artifact(Path(a)) for a in artifacts]
        capsule["artifact_urls"] = uploaded
        register_capsule(capsule)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import sys

    if len(sys.argv) < 2:
        print("Usage: python scripts/populate_capsules.py <manifest.json>")
        sys.exit(1)
    populate(sys.argv[1])
