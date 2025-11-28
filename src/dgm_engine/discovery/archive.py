from typing import List, Dict, Any, Optional
from datetime import datetime

class DGMArchive:
    """
    DGM Archive: Stores successful agent variants.
    """
    def __init__(self):
        self.agents: List[Dict[str, Any]] = []
    
    def add_agent(self, agent: Any, score: float, modification: Dict[str, Any]):
        entry = {
            'agent_id': agent.id,
            'parent_id': agent.parent_id,
            'score': score,
            'modification': modification,
            'config': agent.code_repository,
            'timestamp': datetime.now().isoformat()
        }
        self.agents.append(entry)
        # Keep sorted by score
        self.agents.sort(key=lambda x: x['score'], reverse=True)
    
    def select_parent(self, strategy: str = 'proportional') -> Optional[Dict[str, Any]]:
        """Select an agent from archive to branch from"""
        if not self.agents:
            return None
            
        if strategy == 'best':
            return self.agents[0]
        else:
            # Simple proportional selection (mock)
            return self.agents[0] # Just return best for now
    
    def get_best_agent(self) -> Optional[Dict[str, Any]]:
        return self.agents[0] if self.agents else None
