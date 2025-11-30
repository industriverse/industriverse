import argparse
import sys
import os

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
from src.core.trifecta_orchestrator import TrifectaOrchestrator

def main():
    parser = argparse.ArgumentParser(description="Run Empeiria Haus Factory Orchestration")
    parser.add_argument("--persona", type=str, required=True, help="Persona ID (e.g., research_lead, safety_officer)")
    
    args = parser.parse_args()
    
    orchestrator = TrifectaOrchestrator(args.persona)
    if orchestrator.persona:
        orchestrator.run_loop()
    else:
        print("Failed to initialize orchestrator.")

if __name__ == "__main__":
    main()
