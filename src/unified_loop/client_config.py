from typing import Dict, Any, List

class ClientConfiguration:
    """
    Manages client-specific configuration for the Unified Loop.
    Defines Optimization Targets (what to improve) and Guardrails (safety limits).
    """
    
    def __init__(self, config_dict: Dict[str, Any]):
        self.config = config_dict
        self.validate()
        
    def validate(self):
        """Ensure required fields are present"""
        required = ['client_id', 'targets', 'guardrails']
        for r in required:
            if r not in self.config:
                raise ValueError(f"Missing required config field: {r}")

    def get_guardrails(self) -> Dict[str, Any]:
        """Return safety guardrails"""
        return self.config.get('guardrails', {})

    def get_targets(self) -> List[str]:
        """Return optimization targets"""
        return self.config.get('targets', [])

    @classmethod
    def default_config(cls, client_id: str) -> 'ClientConfiguration':
        """Create a default configuration"""
        return cls({
            "client_id": client_id,
            "targets": ["Minimize Energy", "Maximize Stability"],
            "guardrails": {
                "max_energy": 10.0,
                "min_efficiency": 0.8,
                "safety_mode": "strict"
            }
        })
