import os
import sys
from huggingface_hub import snapshot_download

# Configuration
DATASET_ID = "builddotai/Egocentric-10K"
EVAL_ID = "builddotai/Egocentric-10K-Evaluation"
TARGET_DIR = "/Volumes/Expansion/Egocentric-10K"

# Filter: Download only Factory 001, Workers 001-005 to start (Conservative 1TB limit)
# We can expand this later.
ALLOW_PATTERNS = [
    "factory_001/workers/worker_001*",
    "factory_001/workers/worker_002*",
    "factory_001/workers/worker_003*",
    "factory_001/workers/worker_004*",
    "factory_001/workers/worker_005*",
    "README.md",
    ".gitattributes"
]

def ensure_drive_mounted():
    if not os.path.exists("/Volumes/Expansion"):
        print("❌ Error: External drive '/Volumes/Expansion' not found.")
        print("Please connect the drive and try again.")
        sys.exit(1)
    print(f"✅ External drive found at /Volumes/Expansion")

def download_dataset():
    print(f"🚀 Starting Download to {TARGET_DIR}...")
    print(f"🎯 Target: {DATASET_ID}")
    print(f"🔍 Filters: {ALLOW_PATTERNS}")
    
    # 1. Main Dataset (Filtered)
    try:
        path = snapshot_download(
            repo_id=DATASET_ID,
            repo_type="dataset",
            local_dir=TARGET_DIR,
            allow_patterns=ALLOW_PATTERNS,
            resume_download=True,
            max_workers=8
        )
        print(f"✅ Main Dataset downloaded to: {path}")
    except Exception as e:
        print(f"❌ Error downloading Main Dataset: {e}")

    # 2. Evaluation Dataset (Full)
    print(f"🎯 Target: {EVAL_ID}")
    try:
        path_eval = snapshot_download(
            repo_id=EVAL_ID,
            repo_type="dataset",
            local_dir=os.path.join(TARGET_DIR, "Evaluation"),
            resume_download=True
        )
        print(f"✅ Evaluation Dataset downloaded to: {path_eval}")
    except Exception as e:
        print(f"❌ Error downloading Evaluation Dataset: {e}")

if __name__ == "__main__":
    ensure_drive_mounted()
    download_dataset()
    print("\n🎉 Download Process Complete.")
