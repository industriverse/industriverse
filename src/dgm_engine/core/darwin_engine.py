import ast
import random
from typing import List, Callable, Any

class DarwinEngine:
    """
    Darwin Layer: Evolutionary self-improvement through code mutation.
    """
    def __init__(self, population_size: int = 100):
        self.population = []
        self.fitness_function = None
        self.mutation_rate = 0.01
        
    def mutate_code(self, code: str) -> str:
        """Mutate code through AST manipulation"""
        try:
            ast_tree = ast.parse(code)
            mutated_tree = self.apply_mutations(ast_tree)
            return ast.unparse(mutated_tree)
        except Exception as e:
            print(f"Mutation failed: {e}")
            return code
    
    def apply_mutations(self, tree: ast.AST) -> ast.AST:
        """
        Apply random mutations to the AST.
        Currently supports: Constant modification, Operator swapping.
        """
        class MutationVisitor(ast.NodeTransformer):
            def __init__(self, rate):
                self.rate = rate

            def visit_Constant(self, node):
                if random.random() < self.rate:
                    if isinstance(node.value, (int, float)):
                        # Mutate number by +/- 10%
                        return ast.Constant(value=node.value * (1 + random.uniform(-0.1, 0.1)))
                return node

            def visit_BinOp(self, node):
                if random.random() < self.rate:
                    # Swap operators (e.g., + to -)
                    ops = [ast.Add(), ast.Sub(), ast.Mult(), ast.Div()]
                    return ast.BinOp(left=node.left, op=random.choice(ops), right=node.right)
                return node

        return MutationVisitor(self.mutation_rate).visit(tree)

    def evaluate_fitness(self, code: str) -> float:
        """Evaluate code fitness through testing"""
        if not self.fitness_function:
            raise ValueError("Fitness function not set")
            
        # Placeholder for actual execution/testing logic
        # In a real scenario, this would run unit tests securely
        test_results = {"passed": True} 
        performance = {"execution_time": 0.1}
        
        return self.fitness_function(test_results, performance)
    
    def select_parents(self) -> List[Any]:
        """Select best-performing code for reproduction"""
        # Sort by fitness (assuming 'fitness' attribute exists on population items)
        sorted_population = sorted(self.population, 
                                   key=lambda x: getattr(x, 'fitness', 0), 
                                   reverse=True)
        return sorted_population[:len(sorted_population)//2]
    
    def reproduce(self, parent1: Any, parent2: Any) -> str:
        """Combine two code snippets (Crossover)"""
        # Simple crossover: Take first half of parent1 and second half of parent2
        # This is a naive string-based crossover; AST-based would be better
        lines1 = parent1.code.split('\n')
        lines2 = parent2.code.split('\n')
        
        split_point = min(len(lines1), len(lines2)) // 2
        child_code = '\n'.join(lines1[:split_point] + lines2[split_point:])
        return child_code
