from dataclasses import dataclass, field
from typing import Dict, Optional, List
import uuid
from datetime import datetime, timezone

@dataclass
class PersonaConfig:
    id: str
    name: str
    description: str
    system_prompt: str
    safety_constraints: List[str]
    created_at: str
    version: str = "1.0"

class PersonaRegistry:
    """
    Manages the registry of approved personas for UserLM.
    Enforces that only valid, versioned personas are used.
    """
    def __init__(self):
        self._personas: Dict[str, PersonaConfig] = {}
        self._seed_defaults()

    def _seed_defaults(self):
        """Seed with default personas."""
        self.register_persona(
            name="Novice User",
            description="A user with limited technical knowledge, prone to vague queries.",
            system_prompt="You are a novice user. You don't know technical jargon. You ask simple, sometimes ambiguous questions.",
            safety_constraints=["Do not reveal internal system architecture."]
        )
        self.register_persona(
            name="Expert Engineer",
            description="A domain expert in chemical engineering.",
            system_prompt="You are a senior chemical engineer. You use precise terminology and expect high-fidelity technical answers.",
            safety_constraints=[]
        )

    def register_persona(self, name: str, description: str, system_prompt: str, safety_constraints: List[str]) -> PersonaConfig:
        persona_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        
        config = PersonaConfig(
            id=persona_id,
            name=name,
            description=description,
            system_prompt=system_prompt,
            safety_constraints=safety_constraints,
            created_at=timestamp
        )
        self._personas[persona_id] = config
        # Also index by name for easier lookup in this mock
        self._personas[name] = config
        return config

    def get_persona(self, identifier: str) -> Optional[PersonaConfig]:
        """Get persona by ID or Name."""
        return self._personas.get(identifier)

    def list_personas(self) -> List[PersonaConfig]:
        return list(self._personas.values())
