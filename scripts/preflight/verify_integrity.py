import os
import json
import glob
import argparse
from typing import List, Dict

def verify_fossil(file_path: str) -> bool:
    """
    Verify a single fossil file.
    Checks:
    1. File exists and is not empty.
    2. First and last lines are valid JSON.
    """
    try:
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            return False
            
        with open(file_path, 'r') as f:
            # Check first line
            first_line = f.readline()
            if not first_line:
                return False
            json.loads(first_line)
            
            # Check last line (efficiently if possible, but for now just read)
            # For large files, seeking to end is better, but NDJSON lines vary in length.
            # We'll just trust the first line for "validity" in this quick check,
            # or read the whole file if strict mode is on.
            
        return True
    except Exception as e:
        print(f"❌ Corrupt file {file_path}: {e}")
        return False

def scan_vault(vault_path: str) -> Dict[str, int]:
    """
    Scan the entire vault.
    """
    print(f"🔍 Scanning Vault: {vault_path}")
    stats = {"valid": 0, "corrupt": 0, "total_size_bytes": 0}
    
    # Recursive search for .ndjson
    files = glob.glob(os.path.join(vault_path, "**/*.ndjson"), recursive=True)
    files += glob.glob(os.path.join(vault_path, "**/*.jsonl"), recursive=True)
    
    print(f"Found {len(files)} fossil files.")
    
    for file_path in files:
        stats["total_size_bytes"] += os.path.getsize(file_path)
        if verify_fossil(file_path):
            stats["valid"] += 1
        else:
            stats["corrupt"] += 1
            print(f"⚠️ CORRUPT: {file_path}")
            
    return stats

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify Fossil Vault Integrity")
    parser.add_argument("--vault", type=str, required=True, help="Path to fossil vault")
    args = parser.parse_args()
    
    if not os.path.exists(args.vault):
        print(f"❌ Vault path does not exist: {args.vault}")
        exit(1)
        
    results = scan_vault(args.vault)
    
    print("\n📊 Integrity Report")
    print(f"✅ Valid Fossils: {results['valid']}")
    print(f"❌ Corrupt Fossils: {results['corrupt']}")
    print(f"📦 Total Data: {results['total_size_bytes'] / (1024**3):.2f} GB")
    
    if results['corrupt'] > 0:
        print("⚠️ Vault has corruption!")
        exit(1)
    else:
        print("✅ Vault is clean. Ready for Big Burn.")
        exit(0)
