import os
import hashlib
import time
import json
from datetime import datetime

class IPArchiver:
    """
    Generates a Cryptographic Manifest of the Codebase.
    Serves as 'Defensive Prior Art' for IP Protection (Checklist Item II.B).
    """
    
    def __init__(self, root_dir=".", output_dir="docs/legal"):
        self.root_dir = root_dir
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
    def _hash_file(self, filepath):
        sha256_hash = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            return f"ERROR: {e}"

    def generate_manifest(self):
        """
        Scans codebase and creates a timestamped JSON manifest.
        """
        manifest = {
            "project": "Industriverse",
            "timestamp_utc": datetime.utcnow().isoformat(),
            "timestamp_unix": time.time(),
            "files": []
        }
        
        print("🛡️ Scanning codebase for IP Archival...")
        
        for root, dirs, files in os.walk(self.root_dir):
            # Ignore hidden/git/venv
            if ".git" in root or "venv" in root or "__pycache__" in root:
                continue
                
            for file in files:
                if file.startswith("."): continue
                
                filepath = os.path.join(root, file)
                file_hash = self._hash_file(filepath)
                
                manifest["files"].append({
                    "path": filepath,
                    "sha256": file_hash,
                    "size_bytes": os.path.getsize(filepath)
                })
                
        # Calculate Root Hash (Merkle Root equivalent)
        all_hashes = "".join(sorted([f["sha256"] for f in manifest["files"]]))
        manifest["root_hash"] = hashlib.sha256(all_hashes.encode()).hexdigest()
        
        # Save
        filename = f"ip_manifest_{int(time.time())}.json"
        output_path = os.path.join(self.output_dir, filename)
        
        with open(output_path, "w") as f:
            json.dump(manifest, f, indent=2)
            
        print(f"✅ IP Manifest generated: {output_path}")
        print(f"🔐 Root Hash: {manifest['root_hash']}")
        return output_path

# --- Verification ---
if __name__ == "__main__":
    archiver = IPArchiver()
    archiver.generate_manifest()
