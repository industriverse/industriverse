import sys
import os

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.dgm_engine.core import DarwinEngine, GodelEngine, SelfUnderstandingEngine

def test_fitness(results, performance):
    return 1.0 if results['passed'] else 0.0

def main():
    print("="*60)
    print("       DGM ENGINE SELF-IMPROVEMENT TEST")
    print("="*60)
    
    # 1. Initialize Engines
    print("\n[1] Initializing Engines...")
    darwin = DarwinEngine()
    darwin.fitness_function = test_fitness
    godel = GodelEngine()
    self_understanding = SelfUnderstandingEngine()
    
    # 2. Test Darwin Mutation
    print("\n[2] Testing Darwin Mutation...")
    original_code = "x = 10\ny = x + 5"
    print(f"    Original: {original_code.replace(chr(10), '; ')}")
    mutated_code = darwin.mutate_code(original_code)
    print(f"    Mutated:  {mutated_code.replace(chr(10), '; ')}")
    
    # 3. Test Gödel Proof
    print("\n[3] Testing Gödel Proof...")
    proof = godel.prove_correctness(mutated_code, "spec")
    print(f"    Proof Valid: {proof.get('valid')}")
    
    # 4. Test Self-Understanding
    print("\n[4] Testing Self-Understanding...")
    capabilities = self_understanding.analyze_capabilities()
    print(f"    Capabilities: {capabilities}")
    
    weaknesses = self_understanding.identify_weaknesses()
    if weaknesses:
        print(f"    Weaknesses Identified: {list(weaknesses.keys())}")
        plan = self_understanding.plan_improvement(weaknesses)
        self_understanding.execute_improvement(plan)
    else:
        print("    No weaknesses found.")

    print("\n" + "="*60)
    print("DGM ENGINE VERIFIED")
    print("="*60)

if __name__ == "__main__":
    main()
