import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.anthropology.cognitive_fossil_record import FossilRecord
from src.anthropology.idea_genealogy import IdeaGenealogy

def verify_cognitive_fossil_record():
    print("📜 INITIALIZING COGNITIVE FOSSIL RECORD (CFR)...")
    cfr = FossilRecord()
    
    # 1. Genesis (Standard Mode)
    print("\n--- Step 1: Genesis ---")
    ctx_1 = {"daemon_level": "STANDARD", "narrative_mode": "PEACE"}
    f1 = IdeaGenealogy.create_discovery_fossil(
        "Concept: Better Batteries", "USER_LM", 
        trigger_event="User Request", mechanism_used="Brainstorm", context_snapshot=ctx_1
    )
    cfr.preserve_fossil(f1)
    
    # 2. Mutation 1 (Accelerated Mode)
    print("\n--- Step 2: Mutation (Optimization) ---")
    ctx_2 = {"daemon_level": "ACCELERATED", "narrative_mode": "WAR_FOOTING"}
    f2 = IdeaGenealogy.create_discovery_fossil(
        "Design: Lithium-Sulfur Matrix", "RND1_ENGINE", 
        parent_id=f1.id,
        trigger_event="Efficiency Goal", mechanism_used="Foundry_Optimizer", context_snapshot=ctx_2
    )
    cfr.preserve_fossil(f2)
    
    # 3. Mutation 2 (Singularity Mode)
    print("\n--- Step 3: Mutation (Breakthrough) ---")
    ctx_3 = {"daemon_level": "SINGULARITY", "narrative_mode": "GOLDEN_AGE"}
    f3 = IdeaGenealogy.create_discovery_fossil(
        "Invention: Solid State Quantum Cell", "DGM_CORE", 
        parent_id=f2.id,
        trigger_event="Recursive Improvement", mechanism_used="T2L_FlashForge", context_snapshot=ctx_3
    )
    cfr.preserve_fossil(f3)
    
    # 4. Trace the Lineage
    print("\n--- 🧬 Reconstructing Evolutionary Trail ---")
    trail = cfr.get_evolutionary_trail(f3.id)
    
    for i, fossil in enumerate(trail):
        print(f"[{i}] {fossil.description}")
        print(f"    Context: {fossil.daemon_level} | {fossil.narrative_context}")
        
    # Assertions
    if len(trail) != 3:
        print("❌ Trail length mismatch.")
        sys.exit(1)
    if trail[0].daemon_level != "STANDARD":
        print("❌ Genesis context mismatch.")
        sys.exit(1)
    if trail[2].daemon_level != "SINGULARITY":
        print("❌ Singularity context mismatch.")
        sys.exit(1)
        
    print("\n✅ CFR Verification Complete. History is Preserved.")

if __name__ == "__main__":
    verify_cognitive_fossil_record()
