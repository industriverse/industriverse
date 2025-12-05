import os
import shutil
from typing import List
from src.scf.mesh.entropy_mesh import EntropyMesh

class EdgeDeployer:
    """
    Deploys BitNet models to edge nodes in the mesh.
    """
    def __init__(self, mesh: EntropyMesh, model_registry_path: str = "models/registry"):
        self.mesh = mesh
        self.registry_path = model_registry_path

    def deploy_model(self, model_name: str, target_nodes: List[str] = None):
        """
        Deploy a model to specified nodes (or all active nodes).
        """
        model_path = os.path.join(self.registry_path, f"{model_name}.onnx")
        if not os.path.exists(model_path):
            print(f"❌ Model not found: {model_path}")
            return

        if target_nodes is None:
            target_nodes = self.mesh.get_active_nodes()

        print(f"🚀 Deploying {model_name} to {len(target_nodes)} nodes...")
        
        for node_id in target_nodes:
            # In a real system, this would use SCP/RSYNC or an API
            # Here we mock the transfer
            print(f"   -> Sending to {node_id}...")
            # Simulate success
            
        print("✅ Deployment Complete.")
