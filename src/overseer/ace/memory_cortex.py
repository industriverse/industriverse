from typing import List, Dict, Any
import json
import os

class MemoryCortex:
    def __init__(self, storage_path: str = "ace_memory.json"):
        self.storage_path = storage_path
        self.episodes = []
        self.playbooks = {}

    def add_episode(self, episode: Dict[str, Any]):
        self.episodes.append(episode)
        # In reality, we would persist this to disk/DB
        
    def get_playbook(self, threat_type: str) -> List[str]:
        return self.playbooks.get(threat_type, ["default_containment", "alert_human"])

    def update_playbook(self, threat_type: str, actions: List[str]):
        self.playbooks[threat_type] = actions

    def retrieve_context(self, query: str) -> Dict[str, Any]:
        # Mock retrieval
        return {"relevant_episodes": len(self.episodes), "suggested_strategy": "monitor"}
