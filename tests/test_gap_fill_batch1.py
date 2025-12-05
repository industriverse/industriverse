import pytest
import os
from src.scf.optimization.entropy_arbitrage import EntropyArbitrageSolver, ComputeZone
from src.scf.mesh.entropy_mesh import EntropyMesh
from src.scf.bitnet.deploy_to_edge import EdgeDeployer

def test_arbitrage_solver():
    solver = EntropyArbitrageSolver()
    solver.register_zone(ComputeZone("us-east", 0.12, 0.4, 100))
    solver.register_zone(ComputeZone("iceland", 0.05, 0.0, 100))
    
    # Cost Optimization
    best = solver.find_optimal_zone(10, 'COST')
    assert best == "iceland"
    
    # Carbon Optimization
    best = solver.find_optimal_zone(10, 'CARBON')
    assert best == "iceland"

def test_entropy_mesh():
    mesh = EntropyMesh()
    mesh.register_node("edge-01", "EDGE")
    
    active = mesh.get_active_nodes()
    assert "edge-01" in active
    
    # Simulate timeout (mocking time would be better, but simple check logic is fine)
    mesh.nodes["edge-01"].last_heartbeat -= 100
    active = mesh.get_active_nodes()
    assert "edge-01" not in active

def test_edge_deployer():
    mesh = EntropyMesh()
    mesh.register_node("edge-01", "EDGE")
    
    # Create dummy model
    os.makedirs("models/registry", exist_ok=True)
    with open("models/registry/test_model.onnx", "w") as f:
        f.write("dummy")
        
    deployer = EdgeDeployer(mesh, "models/registry")
    deployer.deploy_model("test_model")
    
    # Cleanup
    os.remove("models/registry/test_model.onnx")
    os.rmdir("models/registry")
