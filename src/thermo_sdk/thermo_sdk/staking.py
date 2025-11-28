from dataclasses import dataclass
from typing import Dict

@dataclass
class StakeRecord:
    utid: str
    exergy: float

class StakingManager:
    def __init__(self):
        self.stakes: Dict[str, StakeRecord] = {}

    def stake(self, utid: str, exergy: float):
        self.stakes[utid] = StakeRecord(utid, exergy)

    def reward(self, utid: str, negentropy: float):
        # Simplistic: add negentropy to stake
        if utid in self.stakes:
            self.stakes[utid].exergy += negentropy
