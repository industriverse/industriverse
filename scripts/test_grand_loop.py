import asyncio
import sys
import os
import logging

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.unified_loop.grand_orchestrator import get_grand_orchestrator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def main():
    print("="*60)
    print("       GRAND UNIFIED LOOP TEST")
    print("="*60)
    
    orchestrator = get_grand_orchestrator()
    
    client_id = "tester_001"
    task = "Design a high-temperature superconductor for fusion magnets"
    domain = "material_science"
    
    print(f"\nRunning Task: {task}")
    print(f"Domain: {domain}")
    print("-" * 40)
    
    try:
        result = await orchestrator.run_grand_loop(client_id, task, domain)
        
        print("\n" + "="*60)
        print("RESULT:")
        print(f"Status: {result['status']}")
        if result['status'] == 'success':
            print(f"Capsule ID: {result['capsule_id']}")
            print(f"Hypothesis: {result['hypothesis']}")
            print(f"Reward: {result['reward']} Negentropy Credits")
            print(f"LoRA: {result['lora_used'].get('domain', 'N/A')}")
        else:
            print(f"Reason: {result.get('reason')}")
            
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
