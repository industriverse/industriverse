import os
from b2sdk.v2 import InMemoryAccountInfo, B2Api

def download_logs():
    print("⬇️ Downloading logs from B2...")
    
    # Credentials (Hardcoded for this session based on user input)
    key_id = "00538e1a3d29f220000000001"
    app_key = "K005BtVUhuATVeto2sYgy5vZnz3pKS4"
    bucket_name = "industriverse-backup"
    
    info = InMemoryAccountInfo()
    b2_api = B2Api(info)
    
    try:
        b2_api.authorize_account("production", key_id, app_key)
        bucket = b2_api.get_bucket_by_name(bucket_name)
        
        local_file = "training_log.jsonl"
        remote_file = "big_burn_logs/training_log.jsonl"
        
        with open(local_file, 'wb') as f:
            bucket.download_file_by_name(remote_file).save(f)
            
        print(f"✅ Successfully downloaded {local_file}")
        
    except Exception as e:
        print(f"❌ Download failed: {e}")

if __name__ == "__main__":
    download_logs()
