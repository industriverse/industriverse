import hashlib
import json
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class AuditLog:
    def __init__(self):
        self.chain = []
        self.genesis_block()

    def genesis_block(self):
        genesis = {
            "index": 0,
            "timestamp": time.time(),
            "action": "GENESIS",
            "actor": "SYSTEM",
            "prev_hash": "0" * 64
        }
        genesis["hash"] = self.calculate_hash(genesis)
        self.chain.append(genesis)

    def calculate_hash(self, block):
        # Create a string representation of the block content (excluding the hash itself if present)
        block_content = json.dumps({k: v for k, v in block.items() if k != "hash"}, sort_keys=True)
        return hashlib.sha256(block_content.encode()).hexdigest()

    def log_action(self, actor, action, details):
        prev_block = self.chain[-1]
        new_block = {
            "index": len(self.chain),
            "timestamp": time.time(),
            "actor": actor,
            "action": action,
            "details": details,
            "prev_hash": prev_block["hash"]
        }
        new_block["hash"] = self.calculate_hash(new_block)
        self.chain.append(new_block)
        logger.info(f"Logged Action: {action} by {actor} -> Hash: {new_block['hash'][:8]}...")
        return new_block

    def verify_integrity(self):
        logger.info("Verifying Log Integrity...")
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            prev = self.chain[i-1]
            
            # 1. Check if current hash is valid
            if current["hash"] != self.calculate_hash(current):
                logger.error(f"Integrity Failure at Block {i}: Invalid Hash")
                return False
            
            # 2. Check if prev_hash matches
            if current["prev_hash"] != prev["hash"]:
                logger.error(f"Integrity Failure at Block {i}: Broken Chain")
                return False
                
        logger.info("Integrity Verified: Chain is valid.")
        return True

def run():
    print("\n" + "="*60)
    print(" DEMO 4: IMMUTABLE AUDIT LOG")
    print("="*60 + "\n")

    log = AuditLog()

    print("--- Phase 1: Logging Actions ---")
    log.log_action("Operator_Dave", "START_CAPSULE", {"capsule_id": "furnace_v1"})
    time.sleep(0.1)
    log.log_action("System_AI", "ADJUST_TEMP", {"capsule_id": "furnace_v1", "delta": +50})
    time.sleep(0.1)
    log.log_action("Operator_Dave", "STOP_CAPSULE", {"capsule_id": "furnace_v1"})

    print("\n--- Phase 2: Verifying Integrity ---")
    if log.verify_integrity():
        print("SUCCESS: Log is immutable and verified.")

    print("\n--- Phase 3: Attempting Tampering ---")
    # Simulate an attack: changing a past record
    target_block_index = 2
    print(f"Attacker modifying Block {target_block_index} (ADJUST_TEMP)...")
    log.chain[target_block_index]["details"]["delta"] = +500 # Malicious change
    # Note: Hash is now invalid for this block, and next block's prev_hash won't match re-calculated hash

    if not log.verify_integrity():
        print("SUCCESS: Tampering detected.")

    print("\n" + "="*60)
    print(" DEMO COMPLETE: AUDIT LOG SECURE")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
