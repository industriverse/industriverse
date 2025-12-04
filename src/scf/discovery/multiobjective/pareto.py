from typing import List, Dict, Any

class ParetoOptimizer:
    def find_pareto_front(self, candidates: List[Dict[str, Any]], objectives: List[str]) -> List[Dict[str, Any]]:
        """
        Returns the subset of candidates that are Pareto efficient.
        Assumes we want to MAXIMIZE all objectives.
        """
        pareto_front = []
        for candidate in candidates:
            is_dominated = False
            for other in candidates:
                if candidate == other: continue
                
                # Check if 'other' dominates 'candidate'
                # Dominated if: other >= candidate in ALL objs AND other > candidate in AT LEAST ONE
                better_or_equal = all(other[obj] >= candidate[obj] for obj in objectives)
                strictly_better = any(other[obj] > candidate[obj] for obj in objectives)
                
                if better_or_equal and strictly_better:
                    is_dominated = True
                    break
            
            if not is_dominated:
                pareto_front.append(candidate)
                
        return pareto_front
