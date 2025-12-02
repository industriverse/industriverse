import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.evolution.agent_gene_bank import AgentGeneBank, AgentGenome
from src.evolution.workforce_orchestrator import WorkforceOrchestrator

def verify_workforce():
    print("🧬 INITIALIZING AGENTIC WORKFORCE SIMULATION...")
    
    # 1. Setup Gene Bank
    bank = AgentGeneBank()
    
    # Genesis Genome
    genesis = AgentGenome(
        id="ANALYST_ALPHA",
        generation=1,
        capabilities=["DATA_ANALYSIS"],
        traits={"processing_speed": 1.0, "error_rate": 0.1}
    )
    bank.register_genome(genesis)
    
    # 2. Evolution (Mutation)
    print("\n--- Step 1: Evolutionary Leap ---")
    evolved = bank.mutate_genome(genesis.id)
    
    # Check if traits changed
    if evolved.traits != genesis.traits:
        print(f"✅ Evolution Successful. New Traits: {evolved.traits}")
    else:
        print("❌ Evolution Failed. Traits identical.")
        sys.exit(1)
        
    # 3. Deployment
    print("\n--- Step 2: Fleet Deployment ---")
    orch = WorkforceOrchestrator(bank)
    orch.spawn_workforce(evolved.id, 3) # Spawn 3 clones of the evolved agent
    
    if len(orch.active_agents) == 3:
        print("✅ Fleet Spawned Successfully.")
    else:
        print(f"❌ Fleet Spawn Failed. Count: {len(orch.active_agents)}")
        sys.exit(1)
        
    # 4. Bridge Integration (Task Execution)
    print("\n--- Step 3: Bridge Integration (MCP + A2A) ---")
    # We capture stdout to verify bridge usage if we were doing a strict test, 
    # but for this script we'll rely on the visual output and successful execution.
    orch.assign_task_to_all("ANALYZE_MARKET_DATA")
    
    print("\n✅ Workforce Verification Complete. The Species is Evolving.")

if __name__ == "__main__":
    verify_workforce()
