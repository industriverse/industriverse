from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import hashlib
import uuid
import random
import json
import requests
from datetime import datetime
from typing import Optional

app = FastAPI(title="AI Ripple Phase 0 Kernel", version="0.1.0")

class ArbitrageRequest(BaseModel):
    amount_usd: float
    target_machine_id: str
    source_service: str = "capsule_deployment"

class ArbitrageResult(BaseModel):
    trade_id: str
    input_amount: float
    profit_usd: float
    profit_percentage: float
    spa_id: str
    spa_hash: str
    proof_credits_minted: int
    settlement_status: str
    execution_time_ms: int

class ArbitrageEngine:
    """Phase 0: Simulation kernel with future extensibility"""
    
    def simulate(self, amount: float) -> dict:
        """Simulate arbitrage with realistic variations"""
        # Base 18% profit with ±1% variation
        profit_rate = 0.18 + random.uniform(-0.01, 0.01)
        
        # Simulate gas fees (0.5-1% deduction)
        gas_fee_rate = random.uniform(0.005, 0.01)
        
        gross_profit = amount * profit_rate
        gas_fee = amount * gas_fee_rate
        net_profit = gross_profit - gas_fee
        
        return {
            "gross_profit": round(gross_profit, 2),
            "gas_fee": round(gas_fee, 2),
            "net_profit": round(net_profit, 2),
            "profit_percentage": round((net_profit / amount) * 100, 2)
        }

class SPAGenerator:
    """Stability Proof Artifact generator"""
    
    def create_spa(self, trade_data: dict) -> dict:
        """Generate Phase 0 SPA with future-compatible schema"""
        trade_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Create SPA content
        spa_content = {
            "trade_id": trade_id,
            "timestamp": timestamp,
            "input_amount": trade_data["amount"],
            "profit": trade_data["profit"],
            "asset_type": "simulated_fiat",  # Future: USD, EUR, gold, energy_kwh
            "token_id": None,  # Future: stablecoin contract addresses
            "source_service": trade_data.get("source_service", "ai_ripple"),
            "target_machine": trade_data.get("target_machine_id", "unknown")
        }
        
        # Generate proof hash
        spa_json = json.dumps(spa_content, sort_keys=True)
        proof_hash = hashlib.sha256(spa_json.encode()).hexdigest()
        
        spa_content["proof_hash"] = proof_hash
        
        return {
            "spa_id": trade_id,
            "spa_content": spa_content,
            "proof_hash": proof_hash
        }

class ProofHubStub:
    """Phase 0: Stub for future Merkle anchoring"""
    
    def anchor_spa(self, spa: dict) -> bool:
        """Phase 0: Log SPA, Phase 1+: Merkle tree anchoring"""
        try:
            # Console logging for immediate visibility
            print(f"[PROOF HUB] SPA Anchored: {spa['spa_id']}")
            print(f"[PROOF HUB] Hash: {spa['proof_hash']}")
            
            # File logging for persistence (simulated)
            # with open("/tmp/spa_proofs.jsonl", "a") as f:
            #     f.write(json.dumps(spa) + "\n")
            
            return True
        except Exception as e:
            print(f"[PROOF HUB ERROR] {e}")
            return False

class CreditMinter:
    """Interface to Proof Credit Registry and NOVA VIAL"""
    
    def __init__(self):
        # In a real K8s env, these would be service URLs.
        # For local dev/demo, we might mock them or point to localhost if running.
        self.proof_credit_url = "http://proof-credit-registry-service:8130"
        self.nova_vial_url = "http://nova-vial-m2m-nodeport:8110"
    
    async def mint_credits(self, amount: float, spa_id: str) -> dict:
        """Mint Proof Credits via Registry API"""
        # Mocking for Phase 0 local execution if services aren't reachable
        return {"status": "success", "credits_minted": int(amount)}
    
    async def settle_via_nova_vial(self, credits: int, target_machine: str, spa_id: str) -> dict:
        """Settle credits via NOVA VIAL M2M"""
        # Mocking for Phase 0 local execution
        return {"status": "success", "settlement_id": f"settle_{uuid.uuid4()}"}

# Initialize components
arbitrage_engine = ArbitrageEngine()
spa_generator = SPAGenerator()
proof_hub = ProofHubStub()
credit_minter = CreditMinter()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai-ripple-phase0-kernel",
        "version": "0.1.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/arbitrage/simulate", response_model=ArbitrageResult)
async def simulate_arbitrage(request: ArbitrageRequest):
    """Core Phase 0 endpoint: Simulate arbitrage and complete economic loop"""
    start_time = datetime.utcnow()
    
    try:
        # Step 1: Simulate arbitrage
        arbitrage_result = arbitrage_engine.simulate(request.amount_usd)
        
        # Step 2: Generate SPA
        spa_data = spa_generator.create_spa({
            "amount": request.amount_usd,
            "profit": arbitrage_result["net_profit"],
            "source_service": request.source_service,
            "target_machine_id": request.target_machine_id
        })
        
        # Step 3: Anchor SPA to Proof Hub
        anchor_success = proof_hub.anchor_spa(spa_data)
        if not anchor_success:
            raise HTTPException(status_code=500, detail="SPA anchoring failed")
        
        # Step 4: Mint Proof Credits
        credit_result = await credit_minter.mint_credits(
            arbitrage_result["net_profit"], 
            spa_data["spa_id"]
        )
        
        # Step 5: Settle via NOVA VIAL
        settlement_result = await credit_minter.settle_via_nova_vial(
            int(arbitrage_result["net_profit"]),
            request.target_machine_id,
            spa_data["spa_id"]
        )
        
        # Calculate execution time
        execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return ArbitrageResult(
            trade_id=spa_data["spa_id"],
            input_amount=request.amount_usd,
            profit_usd=arbitrage_result["net_profit"],
            profit_percentage=arbitrage_result["profit_percentage"],
            spa_id=spa_data["spa_id"],
            spa_hash=spa_data["proof_hash"],
            proof_credits_minted=int(arbitrage_result["net_profit"]),
            settlement_status=settlement_result["status"],
            execution_time_ms=int(execution_time)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Arbitrage simulation failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
