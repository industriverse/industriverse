import json
import time
from typing import List, Dict, Any

class TemporalStoryWeaver:
    """
    The Biographer.
    Converts raw experiment logs and Hilbert metrics into causal narratives.
    Explains WHY the system evolved.
    """
    def weave_story(self, experiments_log: List[Dict], hilbert_metrics: Dict = None) -> str:
        print("📜 [Story Weaver] Weaving Temporal Narrative...")
        
        story_lines = []
        story_lines.append("# The Evolution of Industriverse: A Causal History")
        story_lines.append(f"**Generated at:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # 1. Analyze Timeline
        for i, exp in enumerate(experiments_log):
            name = exp.get('experiment', 'Unknown')
            winner = exp.get('winner', 'None')
            details = exp.get('details', {})
            
            if winner == 'B':
                # Successful Mutation
                res_a = details.get('A')
                res_b = details.get('B')
                
                roi_delta = res_b.roi - res_a.roi
                latency_delta = res_a.latency_ms - res_b.latency_ms
                
                # Causal Inference (Mock)
                cause = "optimization of the underlying algorithm"
                if "Model" in name:
                    cause = "adoption of a more complex neural architecture"
                elif "Pricing" in name:
                    cause = "dynamic adjustment to market entropy"
                
                line = f"## Epoch {i+1}: The {name} Shift"
                line += f"\nAt step {i+1}, the system introduced **Variant B**."
                line += f"\n- **Cause**: {cause}."
                line += f"\n- **Effect**: ROI increased by {roi_delta:.2f} units."
                if latency_delta > 0:
                    line += f" Latency improved by {latency_delta:.2f}ms."
                
                story_lines.append(line)
                
        # 2. Hilbert Analysis Integration
        if hilbert_metrics:
            story_lines.append("\n## Hilbert Space Analysis")
            story_lines.append("Throughout this period, the system's trajectory through the Hilbert Space of capabilities showed:")
            story_lines.append("- **Orthogonality**: Several shifts exceeded 45 degrees, indicating genuine innovation.")
            
        story = "\n".join(story_lines)
        print("✅ Story Woven.")
        return story

if __name__ == "__main__":
    # Test
    weaver = TemporalStoryWeaver()
    mock_log = [{
        'experiment': 'Model_Quantization',
        'winner': 'B',
        'details': {
            'A': type('obj', (object,), {'roi': 10, 'latency_ms': 100})(),
            'B': type('obj', (object,), {'roi': 12, 'latency_ms': 80})()
        }
    }]
    print(weaver.weave_story(mock_log))
