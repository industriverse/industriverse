import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

@dataclass
class CognitiveFossil:
    """
    A snapshot of a cognitive event (idea, discovery, decision) preserved in time.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    
    # The "DNA" of the Idea
    content_hash: str = "" # Hash of the idea/discovery
    description: str = ""
    
    # Ancestry
    parent_fossil_id: Optional[str] = None # The idea this mutated from
    
    # Context (The Environment)
    creator_id: str = "UNKNOWN" # Agent/Daemon ID
    daemon_level: str = "STANDARD" # e.g., SINGULARITY
    narrative_context: str = "PEACE" # e.g., WAR_FOOTING
    
    # Outcome
    outcome: str = "PENDING" # SUCCESS, FAILURE, MUTATED, DISCARDED

class FossilRecord:
    """
    The Anthropological Archive.
    Maintains the lineage and history of all cognitive artifacts.
    """
    
    def __init__(self):
        self.fossils: Dict[str, CognitiveFossil] = {}
        self.lineages: Dict[str, List[str]] = {} # RootID -> List[FossilID]
        
    def preserve_fossil(self, fossil: CognitiveFossil):
        """
        Archives a new fossil.
        """
        print(f"   🦕 [CFR] Preserving Fossil: {fossil.description} ({fossil.id[:8]})")
        self.fossils[fossil.id] = fossil
        
        # Track Lineage
        if fossil.parent_fossil_id:
            # Find root of the parent
            root_id = self._find_root(fossil.parent_fossil_id)
            if root_id not in self.lineages:
                self.lineages[root_id] = []
            self.lineages[root_id].append(fossil.id)
        else:
            # This is a new root
            self.lineages[fossil.id] = [fossil.id]
            
    def _find_root(self, fossil_id: str) -> str:
        """
        Traces back to the original ancestor.
        """
        current = self.fossils.get(fossil_id)
        while current and current.parent_fossil_id:
            current = self.fossils.get(current.parent_fossil_id)
        return current.id if current else fossil_id

    def get_evolutionary_trail(self, fossil_id: str) -> List[CognitiveFossil]:
        """
        Reconstructs the full history chain leading to this fossil.
        """
        trail = []
        current = self.fossils.get(fossil_id)
        while current:
            trail.insert(0, current)
            current = self.fossils.get(current.parent_fossil_id)
        return trail

# --- Verification ---
if __name__ == "__main__":
    cfr = FossilRecord()
    
    # 1. Original Idea
    f1 = CognitiveFossil(description="Hypothesis A: Energy is Mass", creator_id="DAEMON_01")
    cfr.preserve_fossil(f1)
    
    # 2. Mutation
    f2 = CognitiveFossil(description="Hypothesis A.1: E=mc^2", parent_fossil_id=f1.id, creator_id="LITHOS_KERNEL")
    cfr.preserve_fossil(f2)
    
    # 3. Trace
    trail = cfr.get_evolutionary_trail(f2.id)
    print("\n--- Evolutionary Trail ---")
    for f in trail:
        print(f" -> {f.description} [{f.creator_id}]")
