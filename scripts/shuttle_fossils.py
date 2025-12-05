import os
import time
import argparse
from b2sdk.v2 import InMemoryAccountInfo, B2Api
from pathlib import Path

# Configuration (Env vars should be set in the container)
B2_KEY_ID = os.environ.get("B2_KEY_ID")
B2_APP_KEY = os.environ.get("B2_APP_KEY")
B2_BUCKET_NAME = os.environ.get("B2_BUCKET_NAME", "industriverse-fossil-vault")

def shuttle_fossils(target_dir: str, max_files: int = None):
    """
    Downloads fossils from B2 to the target directory.
    """
    print(f"🚀 Starting Fossil Shuttle to {target_dir}...")
    
    if not B2_KEY_ID or not B2_APP_KEY:
        print("❌ Error: B2_KEY_ID and B2_APP_KEY environment variables must be set.")
        return

    info = InMemoryAccountInfo()
    b2_api = B2Api(info)
    
    try:
        b2_api.authorize_account("production", B2_KEY_ID, B2_APP_KEY)
        bucket = b2_api.get_bucket_by_name(B2_BUCKET_NAME)
        print(f"   ✅ Connected to B2 Bucket: {B2_BUCKET_NAME}")
    except Exception as e:
        print(f"   ❌ Connection Failed: {e}")
        return

    target_path = Path(target_dir)
    target_path.mkdir(parents=True, exist_ok=True)
    
    print("   Scanning remote files...")
    count = 0
    downloaded_bytes = 0
    start_time = time.time()
    
    # List files in the bucket
    for file_version, folder_name in bucket.ls(recursive=True):
        if max_files and count >= max_files:
            break
            
        file_name = file_version.file_name
        if not file_name.endswith('.ndjson'):
            continue
            
        local_file = target_path / file_name
        
        # Skip if already exists (Idempotency)
        if local_file.exists() and local_file.stat().st_size == file_version.content_length:
            print(f"   Using cached: {file_name}")
            count += 1
            continue
            
        print(f"   ⬇️  Downloading: {file_name} ({file_version.content_length / 1024 / 1024:.2f} MB)")
        
        try:
            bucket.download_file_by_name(file_name).save(str(local_file))
            downloaded_bytes += file_version.content_length
            count += 1
        except Exception as e:
            print(f"   ⚠️ Failed to download {file_name}: {e}")

    duration = time.time() - start_time
    speed_mbps = (downloaded_bytes * 8) / (duration * 1000 * 1000) if duration > 0 else 0
    
    print(f"\n✅ Shuttle Complete.")
    print(f"   Files: {count}")
    print(f"   Total Size: {downloaded_bytes / 1024 / 1024:.2f} MB")
    print(f"   Speed: {speed_mbps:.2f} Mbps")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=str, default="/workspace/data", help="Target directory for fossils")
    parser.add_argument("--limit", type=int, default=None, help="Max files to download")
    args = parser.parse_args()
    
    shuttle_fossils(args.target, args.limit)
