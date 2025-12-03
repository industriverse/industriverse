from typing import Any, Dict
from src.edge.bitnet_deployer import BitNetDeployer
from src.edge.edge_node_manager import EdgeNodeManager

class BitNetAutoDeploy:
    """
    Handles automated deployment of distilled models to BitNet edge nodes.
    Uses the real BitNetDeployer.
    """
    def __init__(self):
        self.node_manager = EdgeNodeManager()
        # Register a dummy node if none exist (for demo purposes)
        if not self.node_manager.nodes:
            self.node_manager.register_node("edge_node_01", "arm64", 4, 8)
            
        self.deployer = BitNetDeployer(self.node_manager)

    def deploy(self, code_artifact: Any, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Deploys the artifact to the optimal edge node.
        """
        # 1. Determine Target Architecture (Mock logic for now)
        target_arch = "arm64"
        model_name = "scf_generated_v1"
        
        # 2. Deploy using BitNetDeployer
        print(f"🚀 BitNetAutoDeploy: Deploying {model_name} to {target_arch}...")
        try:
            self.deployer.deploy_model(model_name, target_arch)
            return {
                "status": "success",
                "target": target_arch,
                "nodes": [n.hostname for n in self.node_manager.nodes.values() if n.arch == target_arch],
                "artifact": str(code_artifact)[:50]
            }
        except Exception as e:
            print(f"❌ BitNetAutoDeploy Failed: {e}")
            return {"status": "error", "error": str(e)}
