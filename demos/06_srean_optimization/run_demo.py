import time
import json
import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class SupplyChainAgent:
    def __init__(self, name, role, params):
        self.name = name
        self.role = role
        self.params = params
        self.constraints = {}

    def receive_constraint(self, constraint):
        logger.info(f"[{self.name}] Received constraint: {constraint}")
        self.constraints.update(constraint)

    def optimize(self):
        logger.info(f"[{self.name}] Running optimization loop...")
        time.sleep(0.5) # Simulate compute
        
        # Logic: If Dysprosium is short, increase Refining Purity to compensate
        if "dysprosium_availability" in self.constraints:
            avail = self.constraints["dysprosium_availability"]
            if avail < 0.8:
                if self.role == "Refiner":
                    logger.info(f"[{self.name}] Detected shortage. Increasing purity target.")
                    self.params["purity_target"] = 0.9999 # Increase purity
                    self.params["energy_consumption"] *= 1.2 # Cost increases
                elif self.role == "Assembler":
                    logger.info(f"[{self.name}] Detected shortage. Adjusting magnetic alignment.")
                    self.params["alignment_field_strength"] *= 1.1

        return self.params

    def report(self):
        return {
            "agent": self.name,
            "params": self.params,
            "status": "OPTIMAL"
        }

def run():
    print("\n" + "="*60)
    print(" DEMO 6: S-REAN SUPPLY CHAIN OPTIMIZATION")
    print("="*60 + "\n")

    # Initialize Agents
    miner = SupplyChainAgent("Miner_01", "Miner", {"output_rate": 100, "dysprosium_grade": 0.05})
    refiner = SupplyChainAgent("Refiner_01", "Refiner", {"purity_target": 0.99, "energy_consumption": 500})
    assembler = SupplyChainAgent("Assembler_01", "Assembler", {"alignment_field_strength": 2.0, "magnet_coercivity": 1.5})

    agents = [miner, refiner, assembler]

    print("--- Phase 1: Baseline Operation ---")
    for agent in agents:
        print(f"  -> {agent.name}: {agent.params}")

    print("\n--- Phase 2: Injecting Supply Shock ---")
    print("ALERT: Global Dysprosium Shortage detected (-40% supply)")
    constraint = {"dysprosium_availability": 0.6}
    
    # Propagate constraint
    for agent in agents:
        agent.receive_constraint(constraint)

    print("\n--- Phase 3: S-REAN Orchestration ---")
    print("Initiating multi-agent negotiation...")
    
    # Run optimization
    for agent in agents:
        new_params = agent.optimize()
        print(f"  -> {agent.name} New Params: {new_params}")

    print("\n--- Phase 4: Verification ---")
    # Verify that the system compensated
    if refiner.params["purity_target"] > 0.99:
        print("SUCCESS: Refiner increased purity to compensate for lower raw material grade.")
    
    if assembler.params["alignment_field_strength"] > 2.0:
        print("SUCCESS: Assembler increased field strength to maintain coercivity.")

    print("\n" + "="*60)
    print(" DEMO COMPLETE: OPTIMIZATION SUCCESSFUL")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
