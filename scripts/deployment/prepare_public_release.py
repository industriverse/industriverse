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
        try:
            shutil.rmtree(target_dir)
        except Exception as e:
            print(f"   WARNING: Could not remove target directory: {e}")
            # If we can't remove it, we might be inside it. 
            # We'll try to copy over it, but copytree requires dest to NOT exist.
            # So we must ensure it's gone.
            sys.exit(1)
    
    # 2. Copy Codebase (STRICT ALLOWLIST)
    print("   Copying codebase (Strict Mode)...")
    
    # Define what to copy (Relative Paths)
    allowlist = [
        "README.md",
        "LICENSE",
        "src/products",  # The 12 Pillars (Wrappers)
        "src/core",      # Core logic (will be skeletonized)
        "src/evolution", # Evolution logic (will be skeletonized)
        "src/economics", # Economics logic (will be skeletonized)
        "src/security",  # Security logic (will be skeletonized)
        "docs/collaterals", # Public papers
        "docs/assets",   # Images
        "requirements.txt"
    ]

    for item in allowlist:
        src_path = os.path.join(source_dir, item)
        dst_path = os.path.join(target_dir, item)
        
        if os.path.exists(src_path):
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
            else:
                # Ensure parent dir exists
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                shutil.copy2(src_path, dst_path)
        else:
            print(f"   WARNING: Allowlisted item not found: {item}")

    # 3. Redact Sensitive IP (The "Skeleton" Step)
    print("   Redacting proprietary algorithms...")
    # We redact ALL files in these sensitive directories except __init__.py
    sensitive_dirs = [
        "src/core",
        "src/evolution",
        "src/economics",
        "src/security"
    ]
    
    for d in sensitive_dirs:
        full_dir = os.path.join(target_dir, d)
        if os.path.exists(full_dir):
            for root, dirs, files in os.walk(full_dir):
                for file in files:
                    if file.endswith(".py") and file != "__init__.py":
                        file_path = os.path.join(root, file)
                        print(f"   - Skeletonizing: {file}")
                        with open(file_path, 'w') as f:
                            f.write(f"# {file}\n")
                            f.write("# EMPEIRIA HAUS PROPRIETARY SOURCE CODE\n")
                            f.write("# This file contains trade secrets and has been redacted for the public release.\n")
                            f.write("# Enterprise License required for full implementation.\n\n")
                            class_name = file.replace('.py', '').replace('_', ' ').title().replace(' ', '')
                            f.write(f"class {class_name}:\n")
                            f.write("    \"\"\"\n    [REDACTED] Proprietary Implementation.\n    \"\"\"\n")
                            f.write("    def __init__(self, *args, **kwargs):\n")
                            f.write("        raise NotImplementedError(\"This module is available in the Enterprise Edition.\")\n")

    # 4. Add Public License
    with open(os.path.join(target_dir, 'LICENSE'), 'w') as f:
        f.write("Empeiria Haus Public License (See Commercial Terms for Enterprise Use)")
        
    print(f"\n✅ Public Release Ready at: {target_dir}")
    print("   You can now zip this folder or push to a public repo.")

if __name__ == "__main__":
    prepare_public_release()
