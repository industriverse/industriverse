from typing import Dict, List, Any
import time

# Core Systems
from src.unification.unified_substrate_model import USMField, USMSignal, USMEntropy
from src.overseer.overseer_stratiform_v2 import OverseerStratiformV2
from src.coherence.iacp_v2 import IACPMessage, IACPIntent
from src.coherence.intent_parser import IntentParser
from src.evolution.workforce_orchestrator import WorkforceOrchestrator
from src.evolution.agent_gene_bank import AgentGeneBank, AgentGenome
from src.economics.m2m_payment_rail import M2MPaymentRail
from src.security.proof_minter import ProofMinter

class SovereignOrganismV2:
    """
    The Fully Integrated Sovereign Cognitive Organism (V2).
    Unifies Physics (USM), Mind (Overseer), Speech (IACP), Labor (Workforce), and Value (Economy).
    """
    
    def __init__(self, name: str):
        self.name = name
        print(f"🌟 [ORGANISM] Birthing {self.name}...")
        
        # 1. Initialize Senses (USM)
        self.usm_fields: Dict[str, USMField] = {
            "SECURITY": USMField("SECURITY"),
            "THERMAL": USMField("THERMAL"),
            "SOCIAL": USMField("SOCIAL"),
            "ECONOMIC": USMField("ECONOMIC")
        }
        
        # 2. Initialize Brain (Overseer)
        self.overseer = OverseerStratiformV2()
        
        # 3. Initialize Nervous System (IACP)
        self.intent_parser = IntentParser()
        self._setup_reflexes()
        
        # 4. Initialize Muscles (Workforce)
        self.gene_bank = AgentGeneBank()
        self._seed_gene_bank()
        self.workforce = WorkforceOrchestrator(self.gene_bank)
        
        # 5. Initialize Circulatory System (Economy)
        self.economy = M2MPaymentRail()
        
        # 6. Initialize Conscience (Proof Minter)
        self.notary = ProofMinter()
        
        print(f"   ✅ {self.name} is ALIVE.")
        
    def _seed_gene_bank(self):
        """Creates initial agent genomes."""
        g1 = AgentGenome("DEFENDER_V1", 1, ["SECURITY_OPS"], {"vigilance": 0.9})
        g2 = AgentGenome("TRADER_V1", 1, ["HFT"], {"speed": 0.95})
        self.gene_bank.register_genome(g1)
        self.gene_bank.register_genome(g2)
        
    def _setup_reflexes(self):
        """Registers handlers for IACP messages."""
        self.intent_parser.register_handler(IACPIntent.ISSUE_WARNING, self._handle_warning)
        self.intent_parser.register_handler(IACPIntent.REQUEST_RESOURCE, self._handle_resource_request)
        
    def _handle_warning(self, msg: IACPMessage):
        print(f"   🛡️ [REFLEX] Handling Warning: {msg.payload}")
        if msg.payload.get("action") == "INITIATE_LOCKDOWN":
            print("     -> 🔒 LOCKDOWN PROTOCOL ENGAGED.")
            # Spawn Defenders
            self.workforce.spawn_workforce("DEFENDER_V1", 5)
            self.workforce.assign_task_to_all("SECURE_PERIMETER")
            
    def _handle_resource_request(self, msg: IACPMessage):
        print(f"   💰 [REFLEX] Handling Resource Request: {msg.payload}")
        # Logic to allocate funds via M2M Rail would go here
        
    def ingest_signal(self, domain: str, signal: USMSignal):
        """
        Feeds external data into the USM fields.
        """
        if domain in self.usm_fields:
            self.usm_fields[domain].add_signal(signal)
            
    def heartbeat(self):
        """
        Runs one full cycle of life.
        """
        print(f"\n💓 [HEARTBEAT] Cycle Start ({time.strftime('%H:%M:%S')})")
        
        # 1. Brain Process (Observe -> Orient -> Decide -> Act)
        commands = self.overseer.run_cycle(self.usm_fields)
        
        # 2. Nervous System Process (Route Commands)
        for cmd in commands:
            self.intent_parser.process(cmd)
            
        # 3. Conscience Process (Mint Proofs for Insights)
        # (Simplified: In a real loop, we'd capture the insights from the Overseer first)
        
        print("💓 [HEARTBEAT] Cycle Complete.")

# --- Verification ---
if __name__ == "__main__":
    organism = SovereignOrganismV2("Gaia_Prime")
    organism.heartbeat()
