from typing import Dict, List, Optional
from datetime import datetime
from .schema import ContextPlaybook

class PlaybookManager:
    """
    Manages Context Playbooks.
    Retrieves the most relevant strategies for a given domain/intent.
    """
    
    def __init__(self):
        self.playbooks: Dict[str, ContextPlaybook] = {}
        self._seed_playbooks()

    def _seed_playbooks(self):
        """Seed with default playbooks"""
        self.playbooks["default"] = ContextPlaybook(
            playbook_id="pb-default",
            domain="general",
            strategies=["Break down complex tasks", "Verify assumptions"],
            anti_patterns=["Infinite loops", "Hallucination"],
            success_rate=0.8,
            last_updated=datetime.now()
        )

    def get_playbook(self, domain: str) -> ContextPlaybook:
        """Get playbook for a domain, falling back to default"""
        return self.playbooks.get(domain, self.playbooks["default"])

    def update_playbook(self, playbook_id: str, new_strategy: str):
        """Add a new strategy to a playbook"""
        if playbook_id in self.playbooks:
            self.playbooks[playbook_id].strategies.append(new_strategy)
            self.playbooks[playbook_id].last_updated = datetime.now()
