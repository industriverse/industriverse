from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class DemoScenario:
    """
    Defines a single demo scenario for the Industriverse.
    """
    id: str
    name: str
    domain: str
    description: str
    hypothesis: str
    expected_outcome: Dict[str, Any]
    required_priors: List[str] = field(default_factory=list)
    complexity: int = 1 # 1-10
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "domain": self.domain,
            "description": self.description,
            "hypothesis": self.hypothesis,
            "expected_outcome": self.expected_outcome,
            "required_priors": self.required_priors,
            "complexity": self.complexity
        }
