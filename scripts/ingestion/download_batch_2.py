import os
import sys
from huggingface_hub import snapshot_download

# Configuration
DATASET_ID = "builddotai/Egocentric-10K"
TARGET_DIR = "/Volumes/Expansion/Egocentric-10K"

# Filter: Batch 2 - Workers 006-010 of Factory 001
# Expanding the dataset to support EAPM and MFEM training.
ALLOW_PATTERNS = [
    "factory_001/workers/worker_006*",
    "factory_001/workers/worker_007*",
    "factory_001/workers/worker_008*",
    "factory_001/workers/worker_009*",
    "factory_001/workers/worker_010*"
]

def ensure_drive_mounted():
    if not os.path.exists("/Volumes/Expansion"):
        print("❌ Error: External drive '/Volumes/Expansion' not found.")
        print("Please connect the drive and try again.")
        sys.exit(1)
    print(f"✅ External drive found at /Volumes/Expansion")

def download_batch_2():
    print(f"🚀 Starting Batch 2 Download to {TARGET_DIR}...")
    print(f"🎯 Target: {DATASET_ID}")
    print(f"🔍 Filters: {ALLOW_PATTERNS}")
    
    try:
        path = snapshot_download(
            repo_id=DATASET_ID,
            repo_type="dataset",
            local_dir=TARGET_DIR,
            allow_patterns=ALLOW_PATTERNS,
            resume_download=True,
            max_workers=8
        )
        print(f"✅ Batch 2 downloaded to: {path}")
    except Exception as e:
        print(f"❌ Error downloading Batch 2: {e}")

if __name__ == "__main__":
    ensure_drive_mounted()
    download_batch_2()
    print("\n🎉 Batch 2 Download Process Complete.")
