import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.federation.sovereign_node import SovereignNode
from src.federation.federation_protocol import FederationProtocol

def verify_federation():
    print("🌐 INITIALIZING SOVEREIGN COMPUTE FEDERATION SIMULATION...")
    
    # 1. Setup Nodes
    us_node = SovereignNode("US_East_Core")
    eu_node = SovereignNode("EU_West_Secure")
    asia_node = SovereignNode("Asia_Pacific_Edge")
    
    # Set Initial Balances
    eu_node.available_compute = 500.0
    us_node.available_compute = 100.0
    
    # 2. Policy Configuration
    print("\n--- Step 1: Policy Enforcement ---")
    eu_node.trade_policy = "RESTRICTED"
    print(f"Node {eu_node.name} Policy: {eu_node.trade_policy}")
    
    # 3. Failed Trade (No Alliance)
    print("\n--- Step 2: Unauthorized Trade Attempt ---")
    success, msg = FederationProtocol.request_resources(us_node, eu_node, "COMPUTE", 50.0)
    
    if not success and "Policy" in msg:
        print(f"✅ Trade correctly blocked: {msg}")
    else:
        print(f"❌ Trade should have failed but got: {success} ({msg})")
        sys.exit(1)
        
    # 4. Form Alliance
    print("\n--- Step 3: Forming Alliance ---")
    eu_node.register_ally(us_node.id)
    
    # 5. Successful Trade
    print("\n--- Step 4: Authorized Trade ---")
    success, msg = FederationProtocol.request_resources(us_node, eu_node, "COMPUTE", 50.0)
    
    if success:
        print(f"✅ Trade successful: {msg}")
    else:
        print(f"❌ Trade failed unexpectedly: {msg}")
        sys.exit(1)
        
    # 6. Balance Verification
    print("\n--- Step 5: Balance Verification ---")
    print(f"{eu_node.name} Compute: {eu_node.available_compute} (Expected 450.0)")
    print(f"{us_node.name} Compute: {us_node.available_compute} (Expected 150.0)")
    
    if eu_node.available_compute == 450.0 and us_node.available_compute == 150.0:
        print("✅ Balances updated correctly.")
    else:
        print("❌ Balance mismatch.")
        sys.exit(1)
        
    print("\n✅ Federation Verification Complete. The Network is Sovereign.")

if __name__ == "__main__":
    verify_federation()
