import json
import os

class SolutionArchitect:
    """
    The 'Sales Engineer' AI.
    Maps natural language client requests to technical module combinations.
    """
    def __init__(self, matrix_path="src/marketing/solution_matrix.json"):
        # Resolve path relative to this file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # If running from root, adjust path
        if not os.path.exists(os.path.join(base_dir, "solution_matrix.json")):
             # Fallback for when running from root
             matrix_path = os.path.abspath(matrix_path)
        else:
             matrix_path = os.path.join(base_dir, "solution_matrix.json")
             
        with open(matrix_path, 'r') as f:
            self.matrix = json.load(f)

    def map_request_to_solution(self, user_query):
        """
        Analyzes the query and returns the best matching solution.
        """
        query_lower = user_query.lower()
        best_match = None
        max_score = 0

        for pattern in self.matrix['patterns']:
            score = 0
            for keyword in pattern['keywords']:
                if keyword in query_lower:
                    score += 1
            
            if score > max_score:
                max_score = score
                best_match = pattern

        if best_match:
            return {
                "modules": best_match['modules'],
                "pitch": best_match['pitch'],
                "confidence": "HIGH" if max_score > 1 else "MEDIUM"
            }
        else:
            # Fallback / Default
            return {
                "modules": ["Consultation_Required"],
                "pitch": "Custom Engineering Solution Required.",
                "confidence": "LOW"
            }

if __name__ == "__main__":
    # Quick Test
    architect = SolutionArchitect()
    print(architect.map_request_to_solution("Can you fix thermal drift in my CNC?"))
    print(architect.map_request_to_solution("I need robots to learn from video."))
