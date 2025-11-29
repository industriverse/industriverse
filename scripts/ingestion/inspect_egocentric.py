import os
from huggingface_hub import list_repo_files, get_hf_file_metadata, hf_hub_url

DATASET_ID = "builddotai/Egocentric-10K"
EVAL_ID = "builddotai/Egocentric-10K-Evaluation"

def inspect_dataset(repo_id):
    print(f"--- Inspecting {repo_id} ---")
    try:
        files = list_repo_files(repo_id=repo_id, repo_type="dataset")
        print(f"Found {len(files)} files.")
        
        # Group by top-level folder
        folders = {}
        for f in files:
            parts = f.split('/')
            if len(parts) > 1:
                root = parts[0]
                folders[root] = folders.get(root, 0) + 1
            else:
                folders['root'] = folders.get('root', 0) + 1
        
        print("\nStructure Summary:")
        for folder, count in folders.items():
            print(f"  - {folder}/: {count} files")
            
        # Print first 20 files to see naming convention
        print("\nSample Files:")
        for f in files[:20]:
            print(f"  {f}")
            
    except Exception as e:
        print(f"Error inspecting {repo_id}: {e}")

if __name__ == "__main__":
    inspect_dataset(DATASET_ID)
    print("\n" + "="*30 + "\n")
    inspect_dataset(EVAL_ID)
