import json
from typing import Dict, Any, List

class PhysicsContentReasoning:
    def __init__(self, llm_model):
        self.llm = llm_model
        self.perspectives = ['Observable', 'Phenomenon', 'Mechanism', 'Scale', 'Method', 'Application']
    
    def extract_perspectives(self, paper: Dict[str, Any]) -> Dict[str, Any]:
        """Extract 6 physics perspectives from paper"""
        prompt = f"""
        Can you analyze the paper contents according to the following physics perspectives:
        
        (1) Observable: What physical quantities are measured or simulated?
        (2) Phenomenon: What physical event or process is being studied?
        (3) Mechanism: What is the underlying physical law or causal process?
        (4) Scale: What are the spatial, temporal, and energy scales involved?
        (5) Method: What computational or experimental technique is used?
        (6) Application: What is the industrial or commercial use case?
        
        Paper Title: {paper['title']}
        Paper Abstract: {paper['abstract']}
        
        Return JSON format with all 6 perspectives.
        """
        
        # Mock LLM response if model is a dummy
        if hasattr(self.llm, 'generate'):
            response = self.llm.generate(prompt)
        else:
            # Mock response
            response = json.dumps({
                "Observable": "Magnetic field, Density",
                "Phenomenon": "MHD Instability",
                "Mechanism": "Magnetic Reconnection",
                "Scale": "Microscopic to Macroscopic",
                "Method": "Particle-in-Cell Simulation",
                "Application": "Fusion Energy"
            })
            
        try:
            perspectives = json.loads(response)
        except:
            perspectives = {}
        
        return {
            'paper_id': paper['id'],
            'perspectives': perspectives
        }
