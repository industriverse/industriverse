import hashlib
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class UpdateManager:
    def __init__(self):
        self.public_key = "pub_key_industriverse_root"

    def create_update_package(self, version, content):
        logger.info(f"Creating update package {version}...")
        package = {
            "version": version,
            "content": content,
            "timestamp": time.time()
        }
        # Sign the package (Simulated)
        # In reality, this would use a private key to sign the hash of the content
        package_hash = hashlib.sha256(f"{version}:{content}".encode()).hexdigest()
        signature = f"sig_{package_hash}_signed_by_root"
        
        return {
            "package": package,
            "signature": signature
        }

class IndustrialNode:
    def __init__(self, node_id):
        self.node_id = node_id
        self.current_version = "1.0.0"
        self.root_public_key = "pub_key_industriverse_root"

    def receive_update(self, update_bundle):
        logger.info(f"[{self.node_id}] Receiving update...")
        package = update_bundle["package"]
        signature = update_bundle["signature"]
        
        # 1. Verify Signature
        logger.info(f"[{self.node_id}] Verifying signature...")
        package_hash = hashlib.sha256(f"{package['version']}:{package['content']}".encode()).hexdigest()
        expected_signature = f"sig_{package_hash}_signed_by_root"
        
        if signature == expected_signature:
            logger.info(f"[{self.node_id}] ✅ Signature Verified.")
            self.install_update(package)
        else:
            logger.error(f"[{self.node_id}] ❌ Signature Verification Failed! Discarding update.")

    def install_update(self, package):
        logger.info(f"[{self.node_id}] Installing version {package['version']}...")
        time.sleep(1)
        self.current_version = package["version"]
        logger.info(f"[{self.node_id}] Update Complete. Running version {self.current_version}.")

def run():
    print("\n" + "="*60)
    print(" DEMO 19: SECURE FIRMWARE UPDATE")
    print("="*60 + "\n")

    manager = UpdateManager()
    node = IndustrialNode("sensor_node_01")

    # Scenario 1: Valid Update
    print("--- Scenario 1: Valid Update Push ---")
    update_v2 = manager.create_update_package("2.0.0", "binary_blob_v2")
    node.receive_update(update_v2)

    # Scenario 2: Tampered Update
    print("\n--- Scenario 2: Man-in-the-Middle Attack ---")
    update_v3 = manager.create_update_package("3.0.0", "binary_blob_v3")
    
    # Attacker modifies content but cannot generate valid signature
    print("Attacker injecting malicious code...")
    update_v3["package"]["content"] = "malicious_binary_blob" 
    
    node.receive_update(update_v3)

    print("\n" + "="*60)
    print(" DEMO COMPLETE: UPDATE SECURITY VERIFIED")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
