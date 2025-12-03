from typing import Dict, Any
from src.sok.organism_kernel import SovereignOrganism
from src.scf.daemon.scf_daemon import SCFSovereignDaemon
from src.coherence.iacp_v2 import IACPMessage, IACPIntent

class SovereignFoundryAdapter:
    """
    The Bridge between the Sovereign Organism (SOK) and the Code Foundry (SCF).
    Allows the Organism to 'wield' the Foundry as an organ for self-improvement.
    """
    def __init__(self, organism: SovereignOrganism):
        self.organism = organism
        self.daemon = SCFSovereignDaemon()
        print("🔌 [SCF BRIDGE] Connected Foundry to Sovereign Organism")
        
    def process_iacp_command(self, message: IACPMessage):
        """
        Translates IACP messages from the Overseer into Foundry actions.
        """
        if message.intent == IACPIntent.OPTIMIZE_SYSTEM: # Assuming this intent exists or we map it
            print(f"   🔨 [SCF BRIDGE] Received Optimization Order: {message.payload}")
            # Trigger a focused cycle
            # In a real async system, we'd await this or schedule it
            # self.daemon.master_loop.cycle() # This is async, need handling
            pass
            
    def sync_state(self):
        """
        Syncs Organism state (Energy, Narrative) to Foundry Context.
        """
        # Push SOK energy level to SCF context
        # self.daemon.context_root.update_energy(self.organism.state.energy)
        pass
