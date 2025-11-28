"""
Simple mesh client stub for resolver development.
"""

from __future__ import annotations

from typing import Dict, Optional

from .capsule_uri import CapsuleURI


class MockMeshClient:
    def __init__(self) -> None:
        self._store: Dict[str, Dict] = {}

    def register_remote(self, uri: CapsuleURI, metadata: Dict) -> None:
        self._store[uri.to_uri()] = metadata | {"local": False}

    def find_replica(self, uri: CapsuleURI) -> Optional[Dict]:
        return self._store.get(uri.to_uri())
