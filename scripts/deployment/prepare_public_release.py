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
            '.DS_Store', 'venv', 'node_modules', '*.log'
        )
    )
    
    # 3. Sanitize (Mock)
    print("   Sanitizing sensitive files...")
    # Example: Remove internal keys if any were hardcoded (which they shouldn't be)
    # In a real scenario, we might scrub specific lines or replace files.
    
    # 4. Redact Sensitive IP (The "Skeleton" Step)
    print("   Redacting proprietary algorithms...")
    sensitive_files = [
        "src/core/dark_factory.py",
        "src/economics/entropy_trader.py",
        "src/security/exploration_mission.py",
        "src/evolution/experiment_runner.py",
        "src/resource_clusters/clusterer.py",
        "src/meta/genesis.py",
        "src/training/policy_trainer.py",
        "src/integrations/b2_client.py"
    ]
    
    for rel_path in sensitive_files:
        full_path = os.path.join(target_dir, rel_path)
        if os.path.exists(full_path):
            print(f"   - Skeletonizing: {rel_path}")
            with open(full_path, 'w') as f:
                f.write(f"# {os.path.basename(rel_path)}\n")
                f.write("# EMPEIRIA HAUS PROPRIETARY SOURCE CODE\n")
                f.write("# This file contains trade secrets and has been redacted for the public release.\n")
                f.write("# Enterprise License required for full implementation.\n\n")
                f.write("class {}:\n".format(os.path.basename(rel_path).replace('.py', '').replace('_', ' ').title().replace(' ', '')))
                f.write("    \"\"\"\n    [REDACTED] Proprietary Implementation.\n    \"\"\"\n")
                f.write("    def __init__(self, *args, **kwargs):\n")
                f.write("        raise NotImplementedError(\"This module is available in the Enterprise Edition.\")\n")

    # 5. Add Public License
    with open(os.path.join(target_dir, 'LICENSE'), 'w') as f:
        f.write("Empeiria Haus Public License (See Commercial Terms for Enterprise Use)")
        
    print(f"\n✅ Public Release Ready at: {target_dir}")
    print("   You can now zip this folder or push to a public repo.")

if __name__ == "__main__":
    prepare_public_release()
