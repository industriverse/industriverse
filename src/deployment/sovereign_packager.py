import os
import shutil
import time
from dataclasses import dataclass

@dataclass
class SovereignConfig:
    client_name: str
    include_source: bool
    include_models: bool
    encryption_level: str # 'STANDARD', 'MILITARY', 'QUANTUM'

class SovereignPackager:
    """
    Bundles Industriverse for Sovereign/Air-Gapped Deployment.
    Supports Offer #1: Sovereign Stack.
    """
    
    def __init__(self, output_dir="dist/sovereign"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
    def create_package(self, config: SovereignConfig):
        """
        Creates the deployment bundle.
        """
        timestamp = int(time.time())
        package_name = f"industriverse_sovereign_{config.client_name}_{timestamp}"
        package_path = os.path.join(self.output_dir, package_name)
        
        print(f"📦 Packaging for {config.client_name}...")
        os.makedirs(package_path)
        
        # 1. Manifest Generation
        with open(os.path.join(package_path, "MANIFEST.txt"), "w") as f:
            f.write(f"Client: {config.client_name}\n")
            f.write(f"Date: {time.ctime()}\n")
            f.write(f"Encryption: {config.encryption_level}\n")
            f.write("Status: AIR-GAP READY\n")
            
        # 2. Config Injection (Mock)
        with open(os.path.join(package_path, "sovereign_config.yaml"), "w") as f:
            f.write("network:\n  mode: offline\n  allow_external: false\n")
            f.write(f"security:\n  encryption: {config.encryption_level}\n")
            
        # 3. Source Code Bundling (Mock - would copy actual src in prod)
        if config.include_source:
            src_dir = os.path.join(package_path, "src")
            os.makedirs(src_dir)
            with open(os.path.join(src_dir, "kernel.py"), "w") as f:
                f.write("# Sovereign Kernel Source\n")
                
        # 4. Model Weights (Mock)
        if config.include_models:
            models_dir = os.path.join(package_path, "models")
            os.makedirs(models_dir)
            with open(os.path.join(models_dir, "scds_v1.weights"), "w") as f:
                f.write("BINARY_DATA_MOCK")
                
        # 5. Zip it up
        shutil.make_archive(package_path, 'zip', package_path)
        print(f"✅ Package created: {package_path}.zip")
        return f"{package_path}.zip"

# --- Verification ---
if __name__ == "__main__":
    packager = SovereignPackager()
    config = SovereignConfig(
        client_name="MINISTRY_OF_DEFENSE",
        include_source=True,
        include_models=True,
        encryption_level="MILITARY"
    )
    packager.create_package(config)
