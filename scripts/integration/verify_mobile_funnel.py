import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.mobile.integration.negentropy_wallet import NegentropyWallet
from src.mobile.integration.pocket_scanner import PocketScanner
from src.mobile.integration.citizen_science import CitizenScience

def verify_funnel():
    print("🌪️ Starting Mobile Ecosystem Funnel Verification...")
    
    # 1. Setup
    wallet = NegentropyWallet("DEVICE_USER_01")
    scanner = PocketScanner("DEVICE_USER_01")
    science = CitizenScience()
    
    # 2. Earn Initial Credits (Neural Battery Simulation)
    print("\n--- Step 1: Earning (Neural Battery) ---")
    wallet.credit_earnings(20.0, "Neural Battery (Nightly)")
    
    # 3. Participate in Science
    print("\n--- Step 2: Contributing (Citizen Science) ---")
    science.list_missions()
    science.accept_mission("M003", wallet) # Earns 15.0
    
    # 4. Production & Spending
    print("\n--- Step 3: Production (Scan & Fabricate) ---")
    scan = scanner.scan_object("Broken Coffee Handle")
    
    # Attempt to buy (Cost 50.0). Balance should be 20 + 15 = 35. Fail.
    print("   (Attempting purchase with insufficient funds...)")
    scanner.request_fabrication(scan["scan_id"], wallet)
    
    # Earn more to afford it
    print("   (Earning more...)")
    wallet.credit_earnings(20.0, "Referral Bonus")
    
    # Retry purchase. Balance 55. Cost 50. Success.
    print("   (Retrying purchase...)")
    scanner.request_fabrication(scan["scan_id"], wallet)
    
    print("\n✅ FUNNEL VERIFICATION COMPLETE.")

if __name__ == "__main__":
    verify_funnel()
