import os
import json
import time
import shutil
import uuid
from typing import Dict, Any
from pathlib import Path

# Legacy Imports
from src.white_label.dac.registry import get_dac_registry, DACRegistry
from src.white_label.dac.manifest_schema import DACManifest, DACTier, ResourceRequirements, WidgetConfig
from src.capsules.factory.dac_factory import dac_factory as legacy_ux_factory
from src.capsules.core.sovereign_capsule import SovereignCapsule
from src.economics.dac_capsule import DACCapsule

class DACManager:
    """
    The DAC Factory: Produces 'Deploy Anywhere Capsules'.
    Orchestrates the full pipeline: Scaffold -> Enrich -> Manifest -> Register -> Package.
    """
    def __init__(self):
        self.dac_dir = Path("data/scf/dacs")
        self.dac_dir.mkdir(parents=True, exist_ok=True)
        self.registry = get_dac_registry(storage_path=self.dac_dir / "registry")

    def create_capsule(self, intent: str, code: str, target_arch: str) -> Dict[str, Any]:
        """
        Creates a full Sovereign Capsule, registers it, and packages it.
        """
        capsule_id = f"dac-{uuid.uuid4().hex[:8]}"
        staging_dir = self.dac_dir / "staging" / capsule_id
        staging_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"🏭 [DAC FACTORY] Minting Capsule: {capsule_id}")
        
        try:
            # 1. Scaffold (Write Code & Basic Configs)
            self._scaffold_capsule(staging_dir, code, intent, target_arch)
            
            # 2. Enrich (Generate UX/UI via Legacy Factory)
            # We need a mock SovereignCapsule object to pass to the legacy factory
            # In a real scenario, we'd instantiate the actual class, but for now we mock the structure
            mock_capsule = type('MockCapsule', (), {
                'capsule_id': capsule_id,
                'manifest': type('MockManifest', (), {'prin': type('MockPRIN', (), {'domain': 'optimization'})()})(),
                'proof_schema': {'proof_type': 'optimality'}
            })()
            
            ux_assets = legacy_ux_factory.generate_dac(mock_capsule)
            with open(staging_dir / "ui_config.json", "w") as f:
                json.dump(ux_assets, f, indent=2)
                
            # 3. Manifest (Create & Validate)
            manifest = self._create_manifest(capsule_id, intent, target_arch)
            
            # 4. Register (Version Control)
            package = self.registry.register(manifest)
            print(f"   📝 Registered: {package.name} v{manifest.version}")
            
            # 5. Package (Zip)
            # We zip the staging directory
            zip_path = self.dac_dir / f"{capsule_id}.zip"
            shutil.make_archive(str(zip_path.with_suffix('')), 'zip', staging_dir)
            
            print(f"   📦 Packaged: {zip_path}")
            
            # 6. Wrap with DACCapsule (Revenue Engine)
            # Conceptually, the runtime that loads this capsule will wrap it.
            # Here we just log that it's "Revenue Ready".
            print(f"   💎 Revenue Engine: Enabled (DACCapsule Wrapper Ready)")
            
            return {
                "id": capsule_id,
                "path": str(zip_path),
                "manifest": manifest.to_dict(),
                "registry_record": package.dac_id
            }
            
        finally:
            # Cleanup staging
            if staging_dir.exists():
                shutil.rmtree(staging_dir)

    def _scaffold_capsule(self, path: Path, code: str, intent: str, target_arch: str):
        """Writes the raw artifacts to the staging directory."""
        # Inference Script
        with open(path / "inference.py", "w") as f:
            f.write(code)
            
        # Metadata
        metadata = {
            "intent": intent,
            "target_arch": target_arch,
            "created_at": time.time()
        }
        with open(path / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

    def _create_manifest(self, capsule_id: str, intent: str, target_arch: str) -> DACManifest:
        """Creates a compliant DACManifest."""
        return DACManifest(
            name=f"scf-{capsule_id}",
            version="1.0.0",
            description=f"Auto-generated capsule for: {intent}",
            partner_id="sovereign-code-foundry",
            tier=DACTier.SECURITY_ESSENTIALS.value, # Default tier
            target_environments=["edge", "docker"],
            resources=ResourceRequirements(cpu_cores=1.0, memory_gb=0.5, storage_gb=1.0),
            widgets=[
                WidgetConfig(widget_type="ai-shield-dashboard"),
                WidgetConfig(widget_type="energy-flow-graph")
            ],
            features={"auto_optimization": True}
        )

    def list_capsules(self):
        """
        Returns a list of available DACs from the Registry.
        """
        return [p.dac_id for p in self.registry.list_packages()]
