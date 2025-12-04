import logging
from typing import Set

LOG = logging.getLogger("SCF.FossilDedupe")

class FossilDedupeEngine:
    def __init__(self):
        self.seen_hashes: Set[str] = set()

    def is_duplicate(self, fossil_hash: str) -> bool:
        if fossil_hash in self.seen_hashes:
            return True
        self.seen_hashes.add(fossil_hash)
        return False

    def clear(self):
        self.seen_hashes.clear()
