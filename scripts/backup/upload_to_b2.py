import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
import b2sdk.v2 as b2

# Load Credentials
load_dotenv()
B2_KEY_ID = os.getenv("B2_KEY_ID")
B2_APP_KEY = os.getenv("B2_APP_KEY")
BUCKET_NAME = os.getenv("B2_BUCKET_NAME", "industriverse-data-lake")

if not B2_KEY_ID or not B2_APP_KEY:
    print("❌ Error: B2_KEY_ID or B2_APP_KEY not found in .env")
    sys.exit(1)


def auto_caffeinate():
    """
    Spawns a background 'caffeinate' process to prevent sleep while this script runs.
    """
    try:
        import subprocess
        # -i: Prevent idle sleep
        # -w <pid>: Wait for this process to exit
        subprocess.Popen(['caffeinate', '-i', '-w', str(os.getpid())])
        print("☕️  Auto-Caffeinate: System sleep disabled for this session.")
    except Exception as e:
        print(f"⚠️  Could not start caffeinate: {e}")

class B2Uploader:
    def __init__(self):
        auto_caffeinate()
        print("🔌 Connecting to Backblaze B2...")
        self.info = b2.InMemoryAccountInfo()
        self.b2_api = b2.B2Api(self.info)
        self.b2_api.authorize_account("production", B2_KEY_ID, B2_APP_KEY)
        self.bucket = self.b2_api.get_bucket_by_name(BUCKET_NAME)
        print(f"✅ Connected to Bucket: {BUCKET_NAME}")
        
        self.history_file = Path("upload_history.log")
        self.uploaded_files = set()
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                self.uploaded_files = set(line.strip() for line in f)
            print(f"📜 Loaded history: {len(self.uploaded_files)} files already uploaded.")

    def upload_directory(self, local_dir: str, remote_prefix: str):
        local_path = Path(local_dir)
        if not local_path.exists():
            print(f"⚠️  Directory not found: {local_dir}")
            return

        print(f"🚀 Uploading {local_dir} -> b2://{BUCKET_NAME}/{remote_prefix}")
        
        from concurrent.futures import ThreadPoolExecutor
        
        files_to_upload = []
        for root, dirs, files in os.walk(local_path):
            for file in files:
                if file.startswith('.'): continue
                local_file = Path(root) / file
                
                # Check history
                if str(local_file) in self.uploaded_files:
                    continue
                    
                relative_path = local_file.relative_to(local_path)
                remote_file_name = f"{remote_prefix}/{relative_path}"
                files_to_upload.append((local_file, remote_file_name))
                
        print(f"   Found {len(files_to_upload)} new files to upload.")
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            for local_file, remote_name in files_to_upload:
                executor.submit(self._upload_file, local_file, remote_name)

    def _upload_file(self, local_file, remote_name):
        import gzip
        import shutil
        
        try:
            # Simple approach: Gzip to .gz and upload
            compressed_path = local_file.with_suffix(local_file.suffix + '.gz')
            remote_name_gz = remote_name + '.gz'
            
            print(f"   📦 Compressing {local_file.name}...", end="\r")
            with open(local_file, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            print(f"   ⬆️  Uploading {compressed_path.name}...", end="\r")
            self.bucket.upload_local_file(
                local_file=str(compressed_path),
                file_name=str(remote_name_gz)
            )
            
            # Log success
            with open(self.history_file, 'a') as f:
                f.write(f"{local_file}\n")
            
            # Cleanup compressed file
            os.remove(compressed_path)
            print(f"   ✅ {local_file.name} compressed & uploaded.")
            
        except Exception as e:
            print(f"   ❌ Failed to upload {local_file.name}: {e}")
            if os.path.exists(compressed_path):
                os.remove(compressed_path)

if __name__ == "__main__":
    uploader = B2Uploader()
    
    # Priority 1: Fossil Vault (The Processed Data)
    uploader.upload_directory("/Volumes/Expansion/fossil_vault", "fossil_vault")
    
    # Priority 2: Energy Atlas (The Index)
    uploader.upload_directory("/Volumes/Expansion/energy_atlas", "energy_atlas")
    
    # Priority 3: Raw Ingest (The Source - Only specific high-value ones if needed)
    # uploader.upload_directory("/Volumes/Expansion/raw_ingest", "raw_ingest")
    
    print("\n🎉 Upload Session Complete.")
