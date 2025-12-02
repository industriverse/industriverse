from typing import Dict, Any
from src.anthropology.cognitive_fossil_record import CognitiveFossil

class IdeaGenealogy:
    """
    The Family Tree Manager.
    Enriches fossils with causal metadata to explain 'Why' and 'How'.
    """
    
    @staticmethod
    def create_discovery_fossil(
        description: str,
        creator_id: str,
        parent_id: str = None,
        trigger_event: str = "UNKNOWN",
        mechanism_used: str = "UNKNOWN",
        context_snapshot: Dict[str, Any] = None
    ) -> CognitiveFossil:
        """
        Factory method to create a fully contextualized fossil.
        """
        fossil = CognitiveFossil(
            description=description,
            creator_id=creator_id,
            parent_fossil_id=parent_id,
            daemon_level=context_snapshot.get("daemon_level", "UNKNOWN") if context_snapshot else "UNKNOWN",
            narrative_context=context_snapshot.get("narrative_mode", "UNKNOWN") if context_snapshot else "UNKNOWN"
        )
        
        # Embed Causal Metadata into description or a separate field (simulated here via description for simplicity)
        # In a real DB, this would be a JSON field.
        fossil.description += f" | Trigger: {trigger_event} | Tool: {mechanism_used}"
        
        return fossil

    @staticmethod
    def map_lineage(fossil_record, root_id: str):
        """
        Visualizes the tree of ideas starting from a root.
        """
        print(f"\n🌳 [GENEALOGY] Lineage Map for Root: {root_id[:8]}")
        # Simple BFS/DFS to print tree (Mock implementation for now)
        # In reality, would traverse self.lineages
        descendants = fossil_record.lineages.get(root_id, [])
        for fossil_id in descendants:
            f = fossil_record.fossils.get(fossil_id)
            indent = "  " if f.parent_fossil_id == root_id else "    "
            print(f"{indent}↳ {f.description}")

# --- Verification ---
if __name__ == "__main__":
    from src.anthropology.cognitive_fossil_record import FossilRecord
    
    cfr = FossilRecord()
    
    # Context
    ctx = {"daemon_level": "SINGULARITY", "narrative_mode": "GOLDEN_AGE"}
    
    # 1. Root
    f1 = IdeaGenealogy.create_discovery_fossil(
        "Theory of Everything", "DAEMON_01", 
        trigger_event="User Query", mechanism_used="Trifecta", context_snapshot=ctx
    )
    cfr.preserve_fossil(f1)
    
    # 2. Child
    f2 = IdeaGenealogy.create_discovery_fossil(
        "Quantum Gravity", "LITHOS", 
        parent_id=f1.id, 
        trigger_event="Math Inconsistency", mechanism_used="DGM_Recursive", context_snapshot=ctx
    )
    cfr.preserve_fossil(f2)
    
    # Map
    IdeaGenealogy.map_lineage(cfr, f1.id)
