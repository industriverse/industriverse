import hashlib
import json
import time
import os

class BlackBox:
    """
    The Immutable Audit Log.
    Uses cryptographic chaining (SHA-256) to ensure log integrity.
    """
    def __init__(self, log_path="data/audit_trail.jsonl"):
        self.log_path = log_path
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        self.last_hash = self._get_last_hash()

    def log_event(self, event_type, data):
        """
        Logs an event with a cryptographic signature.
        """
        timestamp = time.time()
        # Create payload to hash
        payload = f"{self.last_hash}{timestamp}{event_type}{json.dumps(data)}"
        current_hash = hashlib.sha256(payload.encode()).hexdigest()
        
        entry = {
            "timestamp": timestamp,
            "prev_hash": self.last_hash,
            "type": event_type,
            "data": data,
            "hash": current_hash
        }
        
        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
            
        self.last_hash = current_hash
        print(f"🔒 [BlackBox] Event Logged: {event_type} (Hash: {current_hash[:8]}...)")
        return current_hash

    def verify_integrity(self):
        """
        Re-calculates all hashes to verify the chain is unbroken.
        """
        print("🕵️  Verifying Black Box Integrity...")
        if not os.path.exists(self.log_path):
            print("   No log file found.")
            return True

        prev_hash = "0" * 64
        valid = True
        
        with open(self.log_path, "r") as f:
            for i, line in enumerate(f):
                try:
                    entry = json.loads(line)
                    # Reconstruct payload
                    payload = f"{prev_hash}{entry['timestamp']}{entry['type']}{json.dumps(entry['data'])}"
                    calculated_hash = hashlib.sha256(payload.encode()).hexdigest()
                    
                    if calculated_hash != entry['hash']:
                        print(f"❌ INTEGRITY FAILURE at Line {i+1}!")
                        print(f"   Expected: {calculated_hash}")
                        print(f"   Found:    {entry['hash']}")
                        valid = False
                        break
                    
                    prev_hash = entry['hash']
                except Exception as e:
                    print(f"❌ Parse Error at Line {i+1}: {e}")
                    valid = False
                    break
        
        if valid:
            print("✅ Integrity Verified. Chain is unbroken.")
        return valid

    def _get_last_hash(self):
        if not os.path.exists(self.log_path):
            return "0" * 64 # Genesis Hash
        
        last_line = ""
        with open(self.log_path, "r") as f:
            for line in f:
                last_line = line
        
        if last_line:
            try:
                return json.loads(last_line)["hash"]
            except:
                return "0" * 64
        return "0" * 64

if __name__ == "__main__":
    box = BlackBox()
    box.log_event("SYSTEM_START", {"user": "admin"})
    box.log_event("DRIFT_CORRECTION", {"vector": [0.1, 0.2]})
    box.verify_integrity()
