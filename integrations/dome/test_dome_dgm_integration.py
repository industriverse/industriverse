import sys
sys.path.append('src')

from protocols.dgm_service_connector import DGMServiceConnector
from obmi_operators.quantum_operators import OBMIQuantumOperatorGraph

def test_dome_dgm_integration():
    """Test integration between Dome and existing DGM services"""
    print("🔗 DOME + DGM INTEGRATION TEST")
    print("=" * 50)
    
    # Connect to existing DGM
    dgm_connector = DGMServiceConnector()
    dgm_connection = dgm_connector.connect_to_existing_dgm("aws")
    
    # Create OBMI operators
    obmi_graph = OBMIQuantumOperatorGraph()
    obmi_graph.create_standard_csi_pipeline()
    
    # Test data
    import numpy as np
    csi_data = np.random.randn(64, 2, 1000)
    
    # Execute OBMI pipeline
    obmi_results = obmi_graph.execute_pipeline(csi_data)
    
    # Request DGM evolution
    sensing_requirements = {
        "obmi_results": len(obmi_results),
        "performance_target": "industrial_wifi_sensing"
    }
    evolution_response = dgm_connector.request_evolution(sensing_requirements)
    
    print(f"\n🎉 INTEGRATION RESULTS:")
    print(f"   DGM Connected: {dgm_connection['status']}")
    print(f"   OBMI Operators: {len(obmi_results)} executed")
    print(f"   Evolution Status: {evolution_response['status']}")
    print(f"   Safety Validated: {evolution_response['safety_validated']}")
    
    return {
        "dgm_connection": dgm_connection,
        "obmi_results": obmi_results,
        "evolution_response": evolution_response
    }

if __name__ == "__main__":
    results = test_dome_dgm_integration()
    print("\n✅ Dome + DGM integration complete!")
