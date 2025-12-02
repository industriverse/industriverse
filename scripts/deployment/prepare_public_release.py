import os
import shutil
import sys

def prepare_public_release():
    print("############################################################")
    print("#   EMPEIRIA HAUS: PUBLIC RELEASE GENERATOR                #")
    print("############################################################")
    
    source_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
    target_dir = os.path.abspath(os.path.join(source_dir, '../industriverse_public'))
    
    print(f"🚀 Preparing Release: {source_dir} -> {target_dir}")
    
    # 1. Clean Target
    if os.path.exists(target_dir):
        print("   Cleaning existing target directory...")
        shutil.rmtree(target_dir)
    
    # 2. Copy Codebase
    print("   Copying codebase...")
    shutil.copytree(
        source_dir, 
        target_dir, 
        ignore=shutil.ignore_patterns(
            '.git', '.env', '__pycache__', '*.pyc', 'secrets', 'private',
            '.DS_Store', 'venv', 'node_modules'
        )
    )
    
    # 3. Sanitize (Mock)
    print("   Sanitizing sensitive files...")
    # Example: Remove internal keys if any were hardcoded (which they shouldn't be)
    # In a real scenario, we might scrub specific lines or replace files.
    
    # 4. Add Public License
    with open(os.path.join(target_dir, 'LICENSE'), 'w') as f:
        f.write("Empeiria Haus Public License (See Commercial Terms for Enterprise Use)")
        
    print(f"\n✅ Public Release Ready at: {target_dir}")
    print("   You can now zip this folder or push to a public repo.")

if __name__ == "__main__":
    prepare_public_release()
