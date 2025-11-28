"""
In-memory capsule registry for resolver development/testing.
"""

from __future__ import annotations

from typing import Dict, Optional

from .capsule_uri import CapsuleURI


class InMemoryRegistry:
    def __init__(self) -> None:
        self._store: Dict[str, Dict] = {}

    def register(self, uri: CapsuleURI, metadata: Dict) -> None:
        self._store[uri.to_uri()] = metadata | {"local": True}

    def get_capsule(self, uri: CapsuleURI) -> Optional[Dict]:
        return self._store.get(uri.to_uri())
