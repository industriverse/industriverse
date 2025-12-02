from typing import Dict, Any
import uuid
from src.economics.intelligence_asset import IntelligenceAsset

class MockXRPL:
    """
    Simulates the XRP Ledger for instant settlement.
    """
    def __init__(self):
        self.ledger: Dict[str, float] = {} # Account -> Balance (XRP/Credits)
        
    def set_balance(self, account: str, amount: float):
        self.ledger[account] = amount
        
    def transfer(self, sender: str, receiver: str, amount: float) -> bool:
        if self.ledger.get(sender, 0.0) >= amount:
            self.ledger[sender] -= amount
            self.ledger[receiver] = self.ledger.get(receiver, 0.0) + amount
            return True
        return False

class NovaVialLiquidity:
    """
    Simulates NOVA VIAL liquidity pools for instant conversion.
    """
    @staticmethod
    def get_conversion_rate(asset_type: str) -> float:
        # Mock rates
        if asset_type == "DISCOVERY_LICENSE": return 1.0
        if asset_type == "PROOF_OF_COMPLIANCE": return 0.5
        return 0.1

class M2MPaymentRail:
    """
    The Instant Payment Machine.
    Orchestrates atomic swaps of Assets for Credits via XRPL.
    """
    
    def __init__(self):
        self.xrpl = MockXRPL()
        
    def execute_atomic_swap(self, buyer_id: str, seller_id: str, asset: IntelligenceAsset) -> bool:
        """
        Atomically transfers payment and asset ownership.
        """
        print(f"   💸 [M2M] Initiating Atomic Swap for {asset.id}...")
        
        # 1. Calculate Price
        rate = NovaVialLiquidity.get_conversion_rate(asset.asset_type)
        price = asset.value_negentropy * rate
        print(f"     -> Price: {price:.2f} Credits (Rate: {rate})")
        
        # 2. Execute Payment (Ripple Settlement)
        payment_success = self.xrpl.transfer(buyer_id, seller_id, price)
        
        if payment_success:
            print(f"     -> ✅ Payment Settled on XRPL.")
            # 3. Transfer Asset
            asset.transfer(buyer_id)
            print(f"     -> ✅ Asset Transferred.")
            return True
        else:
            print(f"     -> ❌ Payment Failed (Insufficient Funds).")
            return False

# --- Verification ---
if __name__ == "__main__":
    rail = M2MPaymentRail()
    
    # Setup Accounts
    rail.xrpl.set_balance("Buyer_Node", 5000.0)
    rail.xrpl.set_balance("Seller_Node", 0.0)
    
    # Asset
    asset = IntelligenceAsset("A1", "Seller_Node", "DISCOVERY_LICENSE", "REF", 1000.0)
    
    # Execute
    rail.execute_atomic_swap("Buyer_Node", "Seller_Node", asset)
