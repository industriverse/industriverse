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

class B2Downloader:
    def __init__(self):
        print("🔌 Connecting to Backblaze B2...")
        self.info = b2.InMemoryAccountInfo()
        self.b2_api = b2.B2Api(self.info)
        self.b2_api.authorize_account("production", B2_KEY_ID, B2_APP_KEY)
        self.bucket = self.b2_api.get_bucket_by_name(BUCKET_NAME)
        print(f"✅ Connected to Bucket: {BUCKET_NAME}")

    def download_directory(self, remote_prefix: str, local_dir: str):
        local_path = Path(local_dir)
        local_path.mkdir(parents=True, exist_ok=True)
        
        print(f"🚀 Downloading b2://{BUCKET_NAME}/{remote_prefix} -> {local_dir}")
        
        # List files with prefix
        for file_version, folder_name in self.bucket.ls(folder_to_list=remote_prefix, recursive=True):
            if file_version.action == 'upload':
                file_name = file_version.file_name
                relative_name = file_name[len(remote_prefix):].lstrip('/')
                local_file = local_path / relative_name
                
                print(f"   ⬇️  {relative_name}...", end="\r")
                try:
                    self.bucket.download_file_by_name(file_name).save(b2.DownloadDestLocalFile(str(local_file)))
                    print(f"   ✅ {relative_name} downloaded.")
                except Exception as e:
                    print(f"   ❌ Failed to download {relative_name}: {e}")

if __name__ == "__main__":
    downloader = B2Downloader()
    
    # Download Fossil Vault
    downloader.download_directory("fossil_vault", "fossil_vault")
    
    print("\n🎉 Download Session Complete.")
