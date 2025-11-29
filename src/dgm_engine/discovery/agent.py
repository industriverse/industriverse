from typing import Dict, Any, List, Optional
import random
from datetime import datetime

class DGMDiscoveryAgent:
    """
    Discovery V15 Agent: Self-improving hypothesis generator.
    Uses DGM principles to evolve its own prompts and logic.
    """
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.code_repository = {
            'prompt_template': self._load_default_prompt(),
            'validation_rules': ["no_placeholders", "valid_physics"],
            'regeneration_strategy': "retry_twice",
            'obmi_thresholds': {'prin': 0.7, 'aesp': 0.6}
        }
        self.archive = [] # Local archive for this agent instance
        self.score = 0.0
        self.parent_id = None
        self.id = str(random.randint(1000, 9999))

    def _load_default_prompt(self) -> str:
        return """
        Generate a scientific hypothesis about {topic}.
        Ensure it is physically valid and novel.
        Format: OBSERVATION, PREDICTION, MECHANISM.
        """

    def generate_hypothesis(self, topic: str) -> Dict[str, Any]:
        """Generate hypothesis using current configuration"""
        # Mock generation using current prompt
        prompt = self.code_repository['prompt_template'].format(topic=topic)
        # In real implementation, call LLM here
        hypothesis = f"Hypothesis for {topic} using agent {self.id}"
        
        # Heuristic Scoring (No Randomness)
        # Score based on hypothesis length, complexity, and keyword density
        length_score = min(1.0, len(hypothesis) / 100.0)
        
        # Complexity: Ratio of unique words to total words
        words = hypothesis.split()
        unique_words = set(words)
        complexity_score = len(unique_words) / max(1, len(words))
        
        # Keyword density (Physics terms)
        physics_keywords = ["energy", "entropy", "quantum", "force", "mass", "velocity"]
        keyword_count = sum(1 for w in words if w.lower() in physics_keywords)
        relevance_score = min(1.0, keyword_count / 5.0)
        
        # Weighted OBMI Score
        prin_score = (length_score * 0.3) + (complexity_score * 0.3) + (relevance_score * 0.4)
        aesp_score = (complexity_score * 0.5) + (relevance_score * 0.5)
        
        scores = {
            'prin': round(prin_score, 2),
            'aesp': round(aesp_score, 2),
            'valid': prin_score > 0.3
        }
        return {'hypothesis': hypothesis, 'scores': scores}
    
    def propose_improvement(self) -> Dict[str, Any]:
        """Use LLM to propose code/prompt modification"""
        # Deterministic Proposal Logic
        # If score is low, suggest prompt tweak. If high, suggest threshold tightening.
        if self.score < 0.5:
            mod_type = 'prompt_tweak'
            value = "Add constraint: 'Focus on thermodynamic efficiency'"
        else:
            mod_type = 'threshold_adjust'
            value = "Increase PRIN threshold by 0.05"
            
        return {
            'type': mod_type,
            'description': f"Improvement Strategy: {mod_type}",
            'value': value
        }
    
    def apply_modification(self, modification: Dict[str, Any]) -> 'DGMDiscoveryAgent':
        """Create child agent with modification"""
        child = DGMDiscoveryAgent(self.config)
        child.code_repository = self.code_repository.copy()
        child.parent_id = self.id
        
        # Apply mock modification
        if modification['type'] == 'prompt_tweak':
            child.code_repository['prompt_template'] += "\nNOTE: Be extra creative."
        elif modification['type'] == 'threshold_adjust':
            child.code_repository['obmi_thresholds']['prin'] += 0.05
            
        return child
    
    def evaluate_on_benchmark(self, datasets: List[str]) -> float:
        """Test on Discovery V15 datasets"""
        total_score = 0
        for ds in datasets:
            result = self.generate_hypothesis(ds)
            total_score += result['scores']['prin']
        
        self.score = total_score / len(datasets)
        return self.score
