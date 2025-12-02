from typing import Dict, Any, List
import time

class InstituteInterface:
    """
    The Public Face of the Sovereign Organism.
    Handles external communication, partnerships, and knowledge dissemination.
    """
    
    def __init__(self, organism):
        self.organism = organism
        self.partners: Dict[str, str] = {} # PartnerID -> Role
        
    def get_public_statement(self) -> str:
        """
        Returns a sanitized summary of the Organism's current state and goals.
        """
        # Get internal narrative
        narrative = self.organism.narrative.get_context_summary()
        mode = narrative.get('context_mode', 'UNKNOWN')
        
        # Sanitize for public consumption
        if mode == "WAR_FOOTING":
            return "The Institute is currently focused on critical infrastructure resilience and defense optimization."
        elif mode == "GOLDEN_AGE":
            return "The Institute is experiencing a period of rapid scientific acceleration and invites collaboration."
        elif mode == "HIBERNATION":
            return "The Institute is currently in a conservation cycle."
        else:
            return "The Institute is operating nominally, pursuing balanced growth and discovery."

    def query_knowledge_base(self, query: str) -> List[str]:
        """
        Allows external partners to query the Fossil Record (Sanitized).
        """
        print(f"   🌐 [INSTITUTE] External Query: '{query}'")
        # Mock logic - in reality, would search CFR
        if "battery" in query.lower():
            return ["Public Abstract: Solid State Quantum Cell (Patent Pending)"]
        return ["No public records found."]

    def register_external_partner(self, partner_id: str, role: str):
        """
        Registers a new academic or corporate partner.
        """
        print(f"   🤝 [INSTITUTE] New Partner: {partner_id} ({role})")
        self.partners[partner_id] = role

# --- Verification ---
if __name__ == "__main__":
    # Mock Organism
    class MockNarrative:
        def get_context_summary(self):
            return {"context_mode": "GOLDEN_AGE"}
    class MockOrg:
        narrative = MockNarrative()
        
    interface = InstituteInterface(MockOrg())
    print(f"Statement: {interface.get_public_statement()}")
