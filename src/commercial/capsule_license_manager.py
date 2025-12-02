import time
from dataclasses import dataclass
from typing import List

@dataclass
class License:
    license_id: str
    client_id: str
    capsule_id: str
    tier: str # 'CORE', 'ENTERPRISE', 'SOVEREIGN'
    expires_at: float
    is_active: bool

class CapsuleLicenseManager:
    """
    Manages Rights and Subscriptions for Capsules.
    Supports Offer #4 (Subscriptions) and #6 (DTX).
    """
    
    def __init__(self):
        self.licenses = {} # Mock DB
        
    def issue_license(self, client_id: str, capsule_id: str, tier: str, duration_days: int) -> License:
        """
        Issues a new license.
        """
        license_id = f"LIC_{client_id}_{capsule_id}_{int(time.time())}"
        expires_at = time.time() + (duration_days * 86400)
        
        lic = License(license_id, client_id, capsule_id, tier, expires_at, True)
        self.licenses[license_id] = lic
        return lic
        
    def verify_access(self, license_id: str) -> bool:
        """
        Checks if a license is valid and active.
        """
        if license_id not in self.licenses:
            print(f"❌ Access Denied: License {license_id} not found.")
            return False
            
        lic = self.licenses[license_id]
        
        if not lic.is_active:
            print(f"❌ Access Denied: License {license_id} is inactive.")
            return False
            
        if time.time() > lic.expires_at:
            print(f"❌ Access Denied: License {license_id} expired.")
            return False
            
        print(f"✅ Access Granted: {lic.tier} Tier.")
        return True

# --- Verification ---
if __name__ == "__main__":
    manager = CapsuleLicenseManager()
    
    print("💳 Issuing Enterprise License...")
    lic = manager.issue_license("ACME_CORP", "CAPSULE_SUPPLY_CHAIN", "ENTERPRISE", 365)
    print(f"   License ID: {lic.license_id}")
    
    print("\n🔍 Verifying Access...")
    manager.verify_access(lic.license_id)
    
    print("\n⏳ Simulating Expiration...")
    lic.expires_at = time.time() - 100 # Expire it
    manager.verify_access(lic.license_id)
