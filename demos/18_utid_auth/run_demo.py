import logging
import hashlib
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class UTIDAuthority:
    def __init__(self):
        self.revoked_list = ["utid_compromised_001"]

    def issue_certificate(self, device_id, public_key):
        logger.info(f"Issuing certificate for {device_id}...")
        # Mock certificate
        cert = {
            "utid": device_id,
            "public_key": public_key,
            "issuer": "Industriverse_Root_CA",
            "expiry": time.time() + 3600,
            "signature": hashlib.sha256(f"{device_id}:{public_key}".encode()).hexdigest()
        }
        return cert

    def authenticate(self, cert, challenge, signature):
        logger.info(f"Authenticating {cert['utid']}...")
        
        # 1. Check Revocation
        if cert['utid'] in self.revoked_list:
            logger.warning("❌ Authentication Failed: UTID Revoked")
            return False
            
        # 2. Check Expiry
        if time.time() > cert['expiry']:
            logger.warning("❌ Authentication Failed: Certificate Expired")
            return False
            
        # 3. Verify Signature (Mock)
        # In reality, verify signature using cert['public_key'] against challenge
        expected_sig = hashlib.sha256(f"{challenge}:{cert['utid']}".encode()).hexdigest()
        
        if signature == expected_sig:
            logger.info("✅ Authentication Successful")
            return True
        else:
            logger.warning("❌ Authentication Failed: Invalid Signature")
            return False

def run():
    print("\n" + "="*60)
    print(" DEMO 18: ACCESS CONTROL & IDENTITY (UTID)")
    print("="*60 + "\n")

    auth = UTIDAuthority()

    # Scenario 1: Valid Device
    print("--- Scenario 1: Valid Device Login ---")
    device_id = "utid_sensor_v1_999"
    cert = auth.issue_certificate(device_id, "pub_key_123")
    
    challenge = "random_nonce_555"
    # Device signs challenge
    signature = hashlib.sha256(f"{challenge}:{device_id}".encode()).hexdigest()
    
    auth.authenticate(cert, challenge, signature)

    # Scenario 2: Revoked Device
    print("\n--- Scenario 2: Revoked Device Login ---")
    bad_device_id = "utid_compromised_001"
    bad_cert = auth.issue_certificate(bad_device_id, "pub_key_666")
    
    bad_signature = hashlib.sha256(f"{challenge}:{bad_device_id}".encode()).hexdigest()
    auth.authenticate(bad_cert, challenge, bad_signature)

    # Scenario 3: Invalid Signature (Impersonation)
    print("\n--- Scenario 3: Impersonation Attempt ---")
    # Attacker tries to use Valid Device's cert but can't sign correctly
    fake_signature = "invalid_signature_block"
    auth.authenticate(cert, challenge, fake_signature)

    print("\n" + "="*60)
    print(" DEMO COMPLETE: AUTHENTICATION VERIFIED")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
