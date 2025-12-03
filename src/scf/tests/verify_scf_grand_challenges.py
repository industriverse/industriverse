import asyncio
from src.scf.trunk.trifecta_master_loop import TrifectaMasterLoop

# Mock Dependencies
class MockContextRoot:
    async def get_context_slab(self): return {"context": "mock"}

class MockIntentEngine:
    def generate(self): return "Optimize Grid"
    def expand(self, intent): return {"goal": intent}

class MockBuilder:
    def build(self, spec): return "print('Optimized')"

class MockReviewer:
    def review(self, code): return {"verdict": "APPROVE", "score": 0.9, "critique": "None"}

class MockDeployer:
    def deploy(self, code, context): return "Deployed"

async def verify_integration():
    print("🧪 Starting SCF Grand Challenge Integration Verification")
    
    # 1. Initialize Loop with Mocks
    loop = TrifectaMasterLoop(
        MockContextRoot(),
        MockIntentEngine(),
        MockBuilder(),
        MockReviewer(),
        MockDeployer()
    )
    
    # 2. Verify Component Initialization
    assert loop.telos_classifier is not None, "Telos missing"
    assert loop.energy_api is not None, "EnergyAPI missing"
    assert loop.negentropy_ledger is not None, "NegentropyLedger missing"
    
    # Quadrality Checks
    assert loop.chronos is not None, "Chronos missing"
    assert loop.aletheia is not None, "Aletheia missing"
    assert loop.persona_manager is not None, "PersonaManager missing"
    assert loop.hydrator is not None, "Hydrator missing"
    
    # Empeiria Haus Checks
    assert loop.research_controller is not None, "ResearchController missing"
    assert loop.entropy_oracle is not None, "EntropyOracle missing"
    assert loop.value_vault is not None, "ValueVault missing"
    
    print("✅ Components Initialized (Grand Challenges + Quadrality + Empeiria)")
    
    # 3. Run a Cycle
    print("🔄 Running Cycle...")
    result = await loop.cycle()
    
    # 4. Verify Integrations
    # Energy Check happened (implicit if we got here)
    # Negentropy recorded
    assert len(loop.negentropy_ledger.ledger) > 0, "Negentropy Ledger failed to record"
    last_tx = loop.negentropy_ledger.ledger[-1]
    print(f"✅ Negentropy Transaction Recorded: {last_tx['hash'][:8]}... Value: {last_tx['value_credits']}")
    
    print("✅ SCF Grand Challenge Integration Verified")

if __name__ == "__main__":
    asyncio.run(verify_integration())
