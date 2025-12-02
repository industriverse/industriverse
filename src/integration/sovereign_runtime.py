import time
from src.sok.organism_kernel import SovereignOrganism
from src.sok.goal_homeostasis import GoalHomeostasis
from src.sok.autopoeisis_engine import AutopoeisisEngine
from src.overseer.overseer_stratiform import OverseerStratiform, StrategicMode
from src.anthropology.cognitive_fossil_record import FossilRecord
from src.anthropology.idea_genealogy import IdeaGenealogy
from src.institution.public_interface import InstituteInterface
from src.institution.publication_engine import PublicationEngine
from src.security.uzkl_ledger import UnifiedZKLedger
from src.security.proof_adapters import ProofAdapters

class SovereignRuntime:
    """
    The Global Nervous System.
    Integrates all layers of the Sovereign Organism into a single runtime.
    """
    
    def __init__(self, name="Industriverse_Prime"):
        print(f"🌍 [RUNTIME] Booting {name}...")
        
        # 1. The Body (SOK)
        self.organism = SovereignOrganism(name)
        self.organism.drives = GoalHomeostasis()
        self.organism.immune_system = AutopoeisisEngine()
        
        # 2. The Brain (Overseer) - Already in SOK, but we reference it
        self.overseer = self.organism.overseer
        
        # 3. The Memory (CFR)
        self.cfr = FossilRecord()
        
        # 4. The Voice (Institution)
        self.institution = InstituteInterface(self.organism)
        
        # 5. The Conscience (UZKL)
        self.ledger = UnifiedZKLedger()
        self.proof_adapters = ProofAdapters(self.ledger)
        
        print("   ✅ All Systems Integrated.")
        
    def run_cycle(self, external_signals: dict = None):
        """
        Executes one full "Life Cycle" of the Organism.
        """
        print(f"\n⚡ [RUNTIME] Cycle Start (Age: {self.organism.state.age_cycles})")
        
        # 1. Ingest Signals (Perception)
        if external_signals:
            for source, data in external_signals.items():
                self.organism.narrative.ingest_signal(source, data.get('value'), data.get('desc'))
                
        # 2. Metabolic Pulse (Body + Brain)
        # This triggers Overseer -> Drives -> Incentives -> Autopoeisis
        self.organism.pulse()
        
        # 3. Cognitive Fossilization (Memory)
        # Check if the Daemon produced a discovery (Mock check)
        if self.organism.narrative.world_state.scientific_consensus > 0.8:
            self._record_discovery()
            
        # 4. Institutional Update (Voice)
        statement = self.institution.get_public_statement()
        print(f"   📢 [PUBLIC] {statement}")
        
        # 5. Compliance Check (Conscience)
        # Prove that the organism is safe
        safety_data = {"energy": self.organism.state.energy, "entropy": self.organism.state.entropy}
        proof = self.proof_adapters.prove_compliance(safety_data)
        self.ledger.verify_proof(proof.id, safety_data)
        
    def _record_discovery(self):
        """
        Captures a discovery in the CFR and potentially publishes it.
        """
        # Mock Discovery Event
        ctx = {
            "daemon_level": self.organism.nervous_system.current_level.name,
            "narrative_mode": self.overseer.current_mode.name
        }
        fossil = IdeaGenealogy.create_discovery_fossil(
            "Automated Insight", "SOVEREIGN_RUNTIME", 
            trigger_event="High Consensus", mechanism_used="Daemon_Pulse", context_snapshot=ctx
        )
        self.cfr.preserve_fossil(fossil)
        
        # Auto-Publish if significant
        if self.overseer.current_mode == StrategicMode.SINGULARITY:
            trail = self.cfr.get_evolutionary_trail(fossil.id)
            paper = PublicationEngine.generate_paper(fossil, trail)
            print(f"   📄 [PUBLISH] Auto-Generated Paper: {fossil.description}")

# --- Verification ---
if __name__ == "__main__":
    runtime = SovereignRuntime()
    runtime.run_cycle()
