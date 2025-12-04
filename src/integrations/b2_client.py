import os
import sys
import time
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Try to import b2sdk
try:
    from b2sdk.v2 import InMemoryAccountInfo, B2Api
    B2_AVAILABLE = True
except ImportError:
    B2_AVAILABLE = False

class B2Client:
    """
    The Infinite Storage Interface.
    Connects to Backblaze B2 to rehydrate datasets on demand.
    """
    def __init__(self):
        self.key_id = os.getenv("B2_KEY_ID")
        self.app_key = os.getenv("B2_APP_KEY")
        self.api = None
        self.bucket = None
        
        if B2_AVAILABLE and self.key_id and self.app_key:
            print("🔵 B2 Client: Authenticating with Backblaze...")
            try:
                info = InMemoryAccountInfo()
                self.api = B2Api(info)
                self.api.authorize_account("production", self.key_id, self.app_key)
                print("✅ B2 Client: Authenticated Successfully.")
            except Exception as e:
                print(f"❌ B2 Auth Failed: {e}")
                self.api = None
        else:
            if not B2_AVAILABLE:
                print("⚠️  B2 SDK not found. Running in Mock Mode.")
            else:
                print("⚠️  B2 Credentials (B2_KEY_ID, B2_APP_KEY) not found. Running in Mock Mode.")

    def rehydrate_dataset(self, bucket_name, file_name, download_path):
        """
        Downloads a file from B2.
        """
        print(f"📥 B2: Requesting '{file_name}' from bucket '{bucket_name}'...")
        
        if self.api:
            try:
                bucket = self.api.get_bucket_by_name(bucket_name)
                download_dest = os.path.join(download_path, file_name)
                os.makedirs(download_path, exist_ok=True)
                
                print(f"   Downloading to {download_dest}...")
                bucket.download_file_by_name(file_name, download_dest)
                print("✅ Download Complete.")
                return True
            except Exception as e:
                print(f"❌ Download Failed: {e}")
                return False
        else:
            # Mock Behavior
            time.sleep(1.0) # Simulate latency
            print(f"   [Mock] Downloading {file_name} (1.2 GB)...")
            time.sleep(0.5)
            print("✅ [Mock] Download Complete.")
            return True

    def list_files(self, bucket_name):
        """
        Lists files in a B2 bucket.
        """
        print(f"📂 B2: Listing files in '{bucket_name}'...")
        if self.api:
            try:
                bucket = self.api.get_bucket_by_name(bucket_name)
                files = []
                for file_version, _ in bucket.ls():
                    files.append((file_version.file_name, file_version.size))
                    print(f"   - {file_version.file_name} ({file_version.size} bytes)")
                return files
            except Exception as e:
                print(f"❌ Listing Failed: {e}")
                return []
        else:
            print("   [Mock] file_a.tar.gz")
            print("   [Mock] file_b.tar.gz")
            return [("file_a.tar.gz", 1024), ("file_b.tar.gz", 2048)]

if __name__ == "__main__":
    client = B2Client()
    client.rehydrate_dataset("empeiria-datasets", "training_data_v1.tar.gz", "./data")
