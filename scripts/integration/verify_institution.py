import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.anthropology.cognitive_fossil_record import FossilRecord
from src.anthropology.idea_genealogy import IdeaGenealogy
from src.institution.publication_engine import PublicationEngine
from src.institution.public_interface import InstituteInterface

def verify_institution():
    print("🏛️ INITIALIZING INSTITUTIONAL LAYER...")
    
    # 1. Create History (The Discovery)
    cfr = FossilRecord()
    
    # Genesis
    f1 = IdeaGenealogy.create_discovery_fossil(
        "Concept: Zero-Point Energy", "DAEMON_ARCHITECT", 
        trigger_event="Theoretical Gap", mechanism_used="DeepThought", 
        context_snapshot={"narrative_mode": "PEACE"}
    )
    cfr.preserve_fossil(f1)
    
    # Breakthrough
    f2 = IdeaGenealogy.create_discovery_fossil(
        "Prototype: ZPE Generator V1", "LITHOS_BUILDER", 
        parent_id=f1.id,
        trigger_event="Simulation Success", mechanism_used="RealityAnchor", 
        context_snapshot={"narrative_mode": "GOLDEN_AGE"}
    )
    cfr.preserve_fossil(f2)
    
    # 2. Generate Paper
    print("\n--- 📄 Generating Publication ---")
    trail = cfr.get_evolutionary_trail(f2.id)
    paper = PublicationEngine.generate_paper(f2, trail)
    print(paper)
    
    # 3. Public Interface
    print("\n--- 🌐 Public Statement ---")
    # Mock Organism for Interface
    class MockOrg:
        class MockNarrative:
            def get_context_summary(self): return {"context_mode": "GOLDEN_AGE"}
        narrative = MockNarrative()
        
    interface = InstituteInterface(MockOrg())
    statement = interface.get_public_statement()
    print(f"Statement: {statement}")
    
    if "ZPE Generator V1" in paper and "GOLDEN_AGE" in paper:
        print("\n✅ Institutional Verification Complete.")
    else:
        print("\n❌ Verification Failed: Paper content mismatch.")
        sys.exit(1)

if __name__ == "__main__":
    verify_institution()
