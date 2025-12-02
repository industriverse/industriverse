import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.economics.intelligence_asset import IntelligenceAsset
from src.economics.m2m_payment_rail import M2MPaymentRail

def verify_cryptoeconomy():
    print("💎 INITIALIZING INTELLIGENCE CRYPTOECONOMY SIMULATION...")
    
    rail = M2MPaymentRail()
    
    # 1. Setup Participants
    seller = "Node_Scientific_Core"
    buyer = "Node_Commercial_Hub"
    
    # Fund Buyer
    initial_balance = 2000.0
    rail.xrpl.set_balance(buyer, initial_balance)
    rail.xrpl.set_balance(seller, 0.0)
    print(f"   💰 Buyer Balance: {initial_balance}")
    
    # 2. Mint Asset
    print("\n--- Step 1: Minting Intelligence Asset ---")
    asset = IntelligenceAsset(
        id="ASSET_GENESIS_01",
        owner_id=seller,
        asset_type="DISCOVERY_LICENSE",
        backing_reference="FOSSIL_ZPE_V1",
        value_negentropy=1500.0 # High value
    )
    print(f"   Created Asset: {asset.id} (Value: {asset.value_negentropy})")
    
    # 3. Execute Trade
    print("\n--- Step 2: Executing M2M Trade ---")
    success = rail.execute_atomic_swap(buyer, seller, asset)
    
    if not success:
        print("❌ Trade failed.")
        sys.exit(1)
        
    # 4. Verify Settlement
    print("\n--- Step 3: Verifying Settlement ---")
    
    # Check Asset Ownership
    if asset.owner_id == buyer:
        print("✅ Asset Ownership Transferred to Buyer.")
    else:
        print(f"❌ Asset ownership mismatch: {asset.owner_id}")
        sys.exit(1)
        
    # Check Balances (Price = 1500 * 1.0 = 1500)
    seller_balance = rail.xrpl.ledger[seller]
    buyer_balance = rail.xrpl.ledger[buyer]
    
    print(f"   Seller Balance: {seller_balance} (Expected 1500.0)")
    print(f"   Buyer Balance: {buyer_balance} (Expected 500.0)")
    
    if seller_balance == 1500.0 and buyer_balance == 500.0:
        print("✅ Financial Settlement Correct.")
    else:
        print("❌ Financial Settlement Failed.")
        sys.exit(1)
        
    print("\n✅ Cryptoeconomy Verification Complete. Value is Liquid.")

if __name__ == "__main__":
    verify_cryptoeconomy()
