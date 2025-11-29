import os
import requests
import sys
import time

# Configuration
DOWNLOAD_URL = "https://figshare.com/ndownloader/articles/25954399?private_link=9d084ff84f3822d2bf17"
TARGET_DIR = "/Volumes/Expansion/industriverse_datasets/slice100k"
FILENAME = "slice100k_all.zip"
FILE_PATH = os.path.join(TARGET_DIR, FILENAME)

def download_file():
    # 1. Create Directory
    if not os.path.exists(TARGET_DIR):
        try:
            os.makedirs(TARGET_DIR)
            print(f"Created directory: {TARGET_DIR}")
        except PermissionError:
            print(f"ERROR: Permission denied creating {TARGET_DIR}.")
            print("Please ensure the drive is mounted and writable.")
            return

    # 2. Check for existing file (Resume capability)
    current_size = 0
    if os.path.exists(FILE_PATH):
        current_size = os.path.getsize(FILE_PATH)
        print(f"Found existing file. Current size: {current_size / (1024**3):.2f} GB")

    # 3. Start Download
    headers = {}
    if current_size > 0:
        headers['Range'] = f"bytes={current_size}-"
        print(f"Resuming download from byte {current_size}...")
    else:
        print("Starting new download...")

    try:
        # Stream download
        with requests.get(DOWNLOAD_URL, headers=headers, stream=True) as r:
            r.raise_for_status()
            
            total_size = int(r.headers.get('content-length', 0)) + current_size
            print(f"Total File Size: {total_size / (1024**3):.2f} GB")
            
            with open(FILE_PATH, 'ab') as f:
                start_time = time.time()
                downloaded_this_session = 0
                
                for chunk in r.iter_content(chunk_size=8192 * 16): # 128KB chunks
                    if chunk:
                        f.write(chunk)
                        downloaded_this_session += len(chunk)
                        
                        # Progress report every 100MB
                        if downloaded_this_session % (100 * 1024 * 1024) < (128 * 1024):
                            current_total = current_size + downloaded_this_session
                            percent = (current_total / total_size) * 100 if total_size else 0
                            elapsed = time.time() - start_time
                            speed = downloaded_this_session / elapsed / (1024**2) if elapsed > 0 else 0
                            print(f"Progress: {percent:.2f}% | {current_total / (1024**3):.2f} GB | Speed: {speed:.2f} MB/s")
                            
        print("\nDownload Complete!")
        print(f"File saved to: {FILE_PATH}")

    except KeyboardInterrupt:
        print("\nDownload paused by user.")
    except Exception as e:
        print(f"\nError during download: {e}")

if __name__ == "__main__":
    print("============================================================")
    print("       SLICE100K DATASET DOWNLOADER")
    print("============================================================")
    download_file()
