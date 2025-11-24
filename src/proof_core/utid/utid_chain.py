from dataclasses import dataclass, field
from typing import List


@dataclass
class UTIDChain:
    """
    Represents a lineage chain of UTIDs across actions.
    """

    root: str
    hops: List[str] = field(default_factory=list)

    def append(self, utid: str) -> None:
        self.hops.append(utid)

    def as_list(self) -> List[str]:
        return [self.root, *self.hops]
