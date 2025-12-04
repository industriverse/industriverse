import sys
import os
from pathlib import Path
from dotenv import load_dotenv

sys.path.append(str(Path.cwd()))
load_dotenv()

from src.integrations.b2_client import B2Client

def list_b2_files():
    client = B2Client()
    bucket_name = os.getenv("B2_BUCKET_NAME", "industriverse-backup")
    client.list_files(bucket_name)

if __name__ == "__main__":
    list_b2_files()
