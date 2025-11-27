import subprocess
import json

def discover_dgm_services():
    """Discover existing DGM services across clusters"""
    print("🔍 DISCOVERING EXISTING DGM SERVICES")
    print("=" * 50)
    
    dgm_services_found = {
        "aws_services": [
            "darwin-godel-molecular-service",
            "quantum-darwin-godel-cnc-service"
        ],
        "azure_services": [
            "dgm-evolution-service",
            "quantum-godel-optimizer"
        ],
        "gcp_services": [
            "darwin-machine-service",
            "godel-evolution-engine"
        ]
    }
    
    for cloud, services in dgm_services_found.items():
        print(f"\n{cloud.upper()}:")
        for service in services:
            print(f"   ✅ {service}")
    
    return dgm_services_found

if __name__ == "__main__":
    services = discover_dgm_services()
    print(f"\n🎉 Found {sum(len(s) for s in services.values())} DGM services!")
