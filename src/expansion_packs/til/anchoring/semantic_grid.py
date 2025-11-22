from typing import List, Dict, Set

class SemanticGrid:
    def __init__(self):
        # Load a mock industrial ontology
        self.ontology: Set[str] = {
            "pump", "valve", "pressure", "temperature", "flow_rate", 
            "rpm", "vibration", "cavitation", "efficiency", "power"
        }

    def validate_term(self, term: str) -> bool:
        """
        Check if a term exists in the semantic grid.
        """
        return term.lower() in self.ontology

    def anchor_output(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter/Tag output based on semantic validity.
        """
        anchored = {}
        for k, v in output.items():
            if self.validate_term(k):
                anchored[k] = {"value": v, "verified": True}
            else:
                anchored[k] = {"value": v, "verified": False, "warning": "Unknown semantic term"}
        return anchored
