import subprocess
import json
import os

def discover_kubernetes_clusters():
    """Discover existing Kubernetes clusters and services"""
    print("🔍 DISCOVERING EXISTING INFRASTRUCTURE")
    print("=" * 60)
    
    discovery_results = {
        "aws_clusters": [],
        "azure_clusters": [],
        "gcp_clusters": [],
        "services_found": {},
        "mcp_services": [],
        "a2a_services": [],
        "edge_services": [],
        "ambient_services": []
    }
    
    # Check if kubectl is available
    try:
        result = subprocess.run(['kubectl', 'version', '--client'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ kubectl is available")
            discover_kubectl_services(discovery_results)
        else:
            print("❌ kubectl not available or not configured")
    except Exception as e:
        print(f"❌ kubectl check failed: {e}")
    
    # Check for cloud CLI tools
    check_cloud_cli_tools(discovery_results)
    
    # Generate discovery report
    generate_discovery_report(discovery_results)
    
    return discovery_results

def discover_kubectl_services(results):
    """Discover services using kubectl"""
    print("\n🔍 Discovering services with kubectl...")
    
    try:
        # Get all contexts
        contexts_result = subprocess.run(['kubectl', 'config', 'get-contexts'], 
                                       capture_output=True, text=True, timeout=10)
        if contexts_result.returncode == 0:
            print("📋 Available kubectl contexts:")
            print(contexts_result.stdout)
        
        # Get current context
        current_context = subprocess.run(['kubectl', 'config', 'current-context'], 
                                       capture_output=True, text=True, timeout=10)
        if current_context.returncode == 0:
            print(f"🎯 Current context: {current_context.stdout.strip()}")
        
        # Get all services
        services_result = subprocess.run(['kubectl', 'get', 'services', '--all-namespaces'], 
                                       capture_output=True, text=True, timeout=30)
        if services_result.returncode == 0:
            print("\n📊 All services across namespaces:")
            print(services_result.stdout)
            parse_kubectl_services(services_result.stdout, results)
        
    except Exception as e:
        print(f"❌ kubectl discovery failed: {e}")

def parse_kubectl_services(kubectl_output, results):
    """Parse kubectl output to find relevant services"""
    lines = kubectl_output.split('\n')
    
    for line in lines[1:]:  # Skip header
        if line.strip():
            parts = line.split()
            if len(parts) >= 2:
                namespace = parts[0]
                service_name = parts[1]
                
                # Check for MCP services
                if 'mcp' in service_name.lower():
                    results["mcp_services"].append({
                        "name": service_name,
                        "namespace": namespace,
                        "type": "mcp"
                    })
                
                # Check for A2A services
                if 'a2a' in service_name.lower():
                    results["a2a_services"].append({
                        "name": service_name,
                        "namespace": namespace,
                        "type": "a2a"
                    })
                
                # Check for edge services
                if 'edge' in service_name.lower():
                    results["edge_services"].append({
                        "name": service_name,
                        "namespace": namespace,
                        "type": "edge"
                    })
                
                # Check for ambient services
                if 'ambient' in service_name.lower():
                    results["ambient_services"].append({
                        "name": service_name,
                        "namespace": namespace,
                        "type": "ambient"
                    })

def check_cloud_cli_tools(results):
    """Check for cloud CLI tools and their configurations"""
    print("\n🌐 Checking cloud CLI tools...")
    
    # Check AWS CLI
    try:
        aws_result = subprocess.run(['aws', 'sts', 'get-caller-identity'], 
                                  capture_output=True, text=True, timeout=10)
        if aws_result.returncode == 0:
            print("✅ AWS CLI configured")
            aws_info = json.loads(aws_result.stdout)
            results["aws_account"] = aws_info.get("Account", "unknown")
            
            # Check EKS clusters
            eks_result = subprocess.run(['aws', 'eks', 'list-clusters'], 
                                      capture_output=True, text=True, timeout=30)
            if eks_result.returncode == 0:
                eks_data = json.loads(eks_result.stdout)
                results["aws_clusters"] = eks_data.get("clusters", [])
                print(f"   EKS Clusters: {results['aws_clusters']}")
        else:
            print("❌ AWS CLI not configured")
    except Exception as e:
        print(f"❌ AWS CLI check failed: {e}")
    
    # Check Azure CLI
    try:
        az_result = subprocess.run(['az', 'account', 'show'], 
                                 capture_output=True, text=True, timeout=10)
        if az_result.returncode == 0:
            print("✅ Azure CLI configured")
            az_info = json.loads(az_result.stdout)
            results["azure_subscription"] = az_info.get("id", "unknown")
            
            # Check AKS clusters
            aks_result = subprocess.run(['az', 'aks', 'list'], 
                                      capture_output=True, text=True, timeout=30)
            if aks_result.returncode == 0:
                aks_data = json.loads(aks_result.stdout)
                results["azure_clusters"] = [cluster["name"] for cluster in aks_data]
                print(f"   AKS Clusters: {results['azure_clusters']}")
        else:
            print("❌ Azure CLI not configured")
    except Exception as e:
        print(f"❌ Azure CLI check failed: {e}")
    
    # Check Google Cloud CLI
    try:
        gcp_result = subprocess.run(['gcloud', 'config', 'get-value', 'project'], 
                                  capture_output=True, text=True, timeout=10)
        if gcp_result.returncode == 0:
            print("✅ Google Cloud CLI configured")
            results["gcp_project"] = gcp_result.stdout.strip()
            
            # Check GKE clusters
            gke_result = subprocess.run(['gcloud', 'container', 'clusters', 'list', '--format=json'], 
                                      capture_output=True, text=True, timeout=30)
            if gke_result.returncode == 0:
                gke_data = json.loads(gke_result.stdout)
                results["gcp_clusters"] = [cluster["name"] for cluster in gke_data]
                print(f"   GKE Clusters: {results['gcp_clusters']}")
        else:
            print("❌ Google Cloud CLI not configured")
    except Exception as e:
        print(f"❌ Google Cloud CLI check failed: {e}")

def generate_discovery_report(results):
    """Generate comprehensive discovery report"""
    print("\n" + "=" * 60)
    print("📊 INFRASTRUCTURE DISCOVERY REPORT")
    print("=" * 60)
    
    # Cloud accounts summary
    print("\n🌐 CLOUD ACCOUNTS:")
    if "aws_account" in results:
        print(f"   AWS Account: {results['aws_account']}")
    if "azure_subscription" in results:
        print(f"   Azure Subscription: {results['azure_subscription']}")
    if "gcp_project" in results:
        print(f"   GCP Project: {results['gcp_project']}")
    
    # Clusters summary
    print(f"\n🏗️ KUBERNETES CLUSTERS:")
    print(f"   AWS EKS: {len(results['aws_clusters'])} clusters")
    for cluster in results['aws_clusters']:
        print(f"      - {cluster}")
    
    print(f"   Azure AKS: {len(results['azure_clusters'])} clusters")
    for cluster in results['azure_clusters']:
        print(f"      - {cluster}")
    
    print(f"   GCP GKE: {len(results['gcp_clusters'])} clusters")
    for cluster in results['gcp_clusters']:
        print(f"      - {cluster}")
    
    # Services summary
    print(f"\n🔗 DISCOVERED SERVICES:")
    print(f"   MCP Services: {len(results['mcp_services'])}")
    for service in results['mcp_services']:
        print(f"      - {service['name']} (namespace: {service['namespace']})")
    
    print(f"   A2A Services: {len(results['a2a_services'])}")
    for service in results['a2a_services']:
        print(f"      - {service['name']} (namespace: {service['namespace']})")
    
    print(f"   Edge Services: {len(results['edge_services'])}")
    for service in results['edge_services']:
        print(f"      - {service['name']} (namespace: {service['namespace']})")
    
    print(f"   Ambient Services: {len(results['ambient_services'])}")
    for service in results['ambient_services']:
        print(f"      - {service['name']} (namespace: {service['namespace']})")
    
    # Save report to file
    with open("infrastructure_discovery_report.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Report saved to: infrastructure_discovery_report.json")

if __name__ == "__main__":
    results = discover_kubernetes_clusters()
    print("\n🎉 INFRASTRUCTURE DISCOVERY COMPLETE!")
