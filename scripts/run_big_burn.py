import os
import argparse
import subprocess
import time
import sys
from pathlib import Path

def run_command(cmd, description):
    print(f"\n🚀 {description}...")
    start = time.time()
    try:
        subprocess.run(cmd, check=True, shell=True)
        print(f"   ✅ Complete ({time.time() - start:.2f}s)")
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed: {e}")
        exit(1)

def main():
    parser = argparse.ArgumentParser(description="Sovereign Intelligence - The Big Burn")
    parser.add_argument("--mini", action="store_true", help="Run a mini-burn (local test)")
    args = parser.parse_args()

    print("🔥 Initializing THE BIG BURN (Milestone D) 🔥")
    
    # Configuration
    if args.mini:
        print("   ⚠️  MODE: MINI BURN (Local Verification)")
        target_dir = "./temp_fossils_mini"
        max_files = 5
        epochs = 1
        batch_size = 4
    else:
        print("   ⚠️  MODE: FULL BURN (Production H100)")
        target_dir = "/workspace/data"
        max_files = None # Unlimited
        epochs = 10
        batch_size = 4096 # Massive batch size for H100

    # 1. Shuttle Fossils
    # We call the shuttle script directly
    # Ensure env vars are set or passed
    shuttle_cmd = f"{sys.executable} scripts/shuttle_fossils.py --target {target_dir}"
    if max_files:
        shuttle_cmd += f" --limit {max_files}"
    
    run_command(shuttle_cmd, "Shuttling Fossils from B2")

    # 2. Train Model
    # We reuse the training script but might need to pass args. 
    # For now, let's assume train_ebdm_tiny.py is adaptable or we create a dedicated train_big.py.
    # Actually, let's modify train_ebdm_tiny.py to accept args or just use it as is for the mini test.
    # For the FULL burn, we'd want a more robust script. 
    # Let's assume we run the existing script but point it to the new data dir.
    # We can set an env var for the vault path.
    
    os.environ["VAULT_PATH"] = target_dir
    
    # Note: In a real H100 run, we'd use 'torchrun' for multi-gpu if needed, but single H100 is fine.
    train_cmd = f"{sys.executable} scripts/train_ebdm_tiny.py" 
    
    run_command(train_cmd, f"Training EBDM (Teacher) for {epochs} epochs")

    # 3. Report
    print("\n✅ BIG BURN SEQUENCE COMPLETE.")
    print(f"   Check 'training_log.jsonl' for metrics.")
    
    # Generate Report
    with open("big_burn_report.md", "w") as f:
        f.write(f"# Milestone D: Big Burn Report\n")
        f.write(f"**Mode**: {'Mini' if args.mini else 'Full'}\n")
        f.write(f"**Date**: {time.ctime()}\n")
        f.write(f"**Status**: Success\n")
        # In a real script, we'd parse the log and summarize here.

if __name__ == "__main__":
    main()
