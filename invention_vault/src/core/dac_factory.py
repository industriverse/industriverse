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

class LoRAFactory:
    """
    Text-to-LoRA (T2L) Factory.
    Generates specialized adapters on-the-fly from natural language descriptions.
    """
    def __init__(self):
        self.adapters = {}
        
    def generate_adapter(self, task_description: str) -> Dict[str, Any]:
        """
        Generate a LoRA adapter configuration for the given task.
        """
        adapter_id = f"lora_{uuid.uuid4().hex[:8]}"
        
        # Mock T2L Hypernetwork Logic
        # In reality, this would run a hypernetwork to predict weights
        rank = 8
        alpha = 16
        if "math" in task_description.lower() or "calculus" in task_description.lower():
            rank = 16
            alpha = 32
        elif "creative" in task_description.lower() or "poem" in task_description.lower():
            rank = 4
            alpha = 8
            
        adapter_config = {
            "id": adapter_id,
            "task": task_description,
            "rank": rank,
            "alpha": alpha,
            "target_modules": ["q_proj", "v_proj"],
            "status": "generated"
        }
        
        self.adapters[adapter_id] = adapter_config
        return adapter_config
