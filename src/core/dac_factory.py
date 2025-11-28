import uuid
from datetime import datetime
from typing import Dict, Any, List
from src.core.capsule_uri import CapsuleURI

class Capsule:
    """
    A thermodynamic unit of computation.
    """
    def __init__(self, uri: CapsuleURI, metadata: Dict[str, Any], content: Dict[str, Any]):
        self.uri = uri
        self.id = str(uuid.uuid4())
        self.created_at = datetime.utcnow().isoformat()
        self.metadata = metadata
        self.content = content
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "uri": str(self.uri),
            "created_at": self.created_at,
            "metadata": self.metadata,
            "content": self.content
        }

class DACFactory:
    """
    Mints Capsules from raw artifacts.
    """
    
    def mint_capsule(self, domain: str, variant: str, version: str, 
                     hypothesis: str, design: Dict[str, Any], proof: Dict[str, Any] = None) -> Capsule:
        """
        Package artifacts into a thermodynamic Capsule.
        """
        uri = CapsuleURI(domain=domain, variant=variant, version=version)
        
        metadata = {
            "type": "sovereign_dac",
            "generator": "UnifiedLoopOrchestrator",
            "energy_rating": design.get("predicted_energy", "unknown")
        }
        
        content = {
            "hypothesis": hypothesis,
            "design": design,
            "proof": proof or {}
        }
        
        return Capsule(uri, metadata, content)
