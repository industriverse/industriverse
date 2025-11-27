import subprocess
import json

def check_specific_services():
    """Check for specific services mentioned in the plans"""
    print("🎯 CHECKING SPECIFIC SERVICES FROM PLANS")
    print("=" * 60)
    
    target_services = [
        "mcp-bridge-minimal-service",
        "mcp-quantum-bridge-unified", 
        "mcp-protocol-service",
        "azure-mcp-bridge",
        "a2a-deploy-anywhere-service",
        "a2a-multicloud-federation-service",
        "a2a2-federation-bridge-service",
        "edge-device-registry",
        "edge-deployment-orchestrator",
        "ambient-intelligence-orchestrator",
        "ambient-intelligence-interface-service"
    ]
    
    found_services = []
    
    for service in target_services:
        print(f"\n🔍 Searching for: {service}")
        
        try:
            # Search across all namespaces
            result = subprocess.run([
                'kubectl', 'get', 'services', '--all-namespaces', 
                '-o', 'json'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                services_data = json.loads(result.stdout)
                
                for item in services_data.get('items', []):
                    service_name = item['metadata']['name']
                    namespace = item['metadata']['namespace']
                    
                    if service in service_name:
                        cluster_ip = item['spec'].get('clusterIP', 'None')
                        service_type = item['spec'].get('type', 'ClusterIP')
                        
                        found_service = {
                            "name": service_name,
                            "namespace": namespace,
                            "cluster_ip": cluster_ip,
                            "type": service_type,
                            "target": service
                        }
                        
                        found_services.append(found_service)
                        
                        print(f"   ✅ FOUND: {service_name}")
                        print(f"      Namespace: {namespace}")
                        print(f"      Cluster IP: {cluster_ip}")
                        print(f"      Type: {service_type}")
                        
                        # Get additional details
                        get_service_details(service_name, namespace)
            
        except Exception as e:
            print(f"   ❌ Error searching for {service}: {e}")
    
    print(f"\n📊 SUMMARY:")
    print(f"   Target services: {len(target_services)}")
    print(f"   Found services: {len(found_services)}")
    print(f"   Discovery rate: {len(found_services)/len(target_services)*100:.1f}%")
    
    return found_services

def get_service_details(service_name, namespace):
    """Get detailed information about a service"""
    try:
        # Get service details
        result = subprocess.run([
            'kubectl', 'describe', 'service', service_name, 
            '-n', namespace
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            # Extract key information
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Endpoints:' in line or 'Port:' in line or 'LoadBalancer Ingress:' in line:
                    print(f"      {line.strip()}")
    
    except Exception as e:
        print(f"      ❌ Could not get details: {e}")

if __name__ == "__main__":
    found = check_specific_services()
    print("\n🎉 SERVICE CHECK COMPLETE!")
