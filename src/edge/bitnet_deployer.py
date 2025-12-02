from src.edge.edge_node_manager import EdgeNodeManager

class BitNetDeployer:
    """
    The Intelligence Distributor.
    Deploys highly quantized 1-bit LLMs to constrained edge devices.
    """
    
    def __init__(self, node_manager: EdgeNodeManager):
        self.mgr = node_manager
        
    def deploy_model(self, model_name: str, target_arch: str):
        """
        Finds suitable nodes and deploys the model.
        """
        print(f"   🧠 [BITNET] Preparing deployment for '{model_name}' ({target_arch})...")
        
        # 1. Filter Nodes
        candidates = [
            n for n in self.mgr.nodes.values() 
            if n.arch == target_arch and n.status == "ONLINE"
        ]
        
        if not candidates:
            print("     -> ❌ No suitable nodes found.")
            return
            
        # 2. Deploy
        for node in candidates:
            print(f"     -> 📦 Transferring Weights to {node.hostname}...")
            # Mock transfer time
            # time.sleep(0.1) 
            self.mgr.deploy_pod(f"bitnet-inference:{model_name}", node.id)
            print(f"     -> ✅ Intelligence Active on {node.hostname}")

# --- Verification ---
if __name__ == "__main__":
    mgr = EdgeNodeManager()
    mgr.register_node("jetson-nano", "arm64", 4, 4)
    deployer = BitNetDeployer(mgr)
    deployer.deploy_model("BitNet_b1.58_3B", "arm64")
