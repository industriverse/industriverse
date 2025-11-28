import asyncio
import argparse
import sys
import os

# Add root to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.core.orchestration.trifecta_orchestrator import TrifectaOrchestrator

async def main():
    parser = argparse.ArgumentParser(description="Run the Trifecta Conscious Loop")
    parser.add_argument("--goal", type=str, default="Optimize Fusion for Stability", help="High-level goal for the system")
    parser.add_argument("--persona", type=str, default="Operator", help="Persona for UserLM")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f" TRIFECTA CONSCIOUS LOOP")
    print(f"{'='*60}")
    print(f"Goal: {args.goal}")
    print(f"Persona: {args.persona}")
    print(f"{'-'*60}\n")

    orchestrator = TrifectaOrchestrator()
    
    try:
        result = await orchestrator.run_conscious_loop(args.goal, args.persona)
        
        print(f"\n{'-'*60}")
        print(f" LOOP RESULT: {result['status'].upper()}")
        print(f"{'-'*60}")
        
        for entry in result["log"]:
            print(f"\n[{entry['step']}]")
            print(f"  > {entry['output']}")
            
        if result['status'] == 'completed':
            print(f"\nFinal Score: {result['final_score']:.4f}")
            
    except Exception as e:
        print(f"\n[ERROR] Loop Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
