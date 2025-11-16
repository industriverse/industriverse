#!/usr/bin/env python3
"""
Kubernetes Service Scanner
Automatically discovers and registers services across all clusters
"""

import json
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass, asdict

@dataclass
class K8sService:
    """Kubernetes service discovered from cluster"""
    name: str
    namespace: str
    cluster: str
    cloud: str
    service_type: str  # ClusterIP, LoadBalancer, NodePort
    cluster_ip: str
    external_ip: str
    ports: List[Dict]
    age_days: float
    labels: Dict
    annotations: Dict


class K8sServiceScanner:
    """
    Scans Kubernetes clusters and discovers services
    Prepares them for ASI registration
    """
    
    def __init__(self):
        self.discovered_services = []
    
    def scan_cluster(
        self,
        cluster_name: str,
        cloud: str,
        services_data: List[Dict]
    ):
        """Scan a cluster and extract services"""
        
        for svc_data in services_data:
            k8s_svc = K8sService(
                name=svc_data['name'],
                namespace=svc_data['namespace'],
                cluster=cluster_name,
                cloud=cloud,
                service_type=svc_data.get('type', 'ClusterIP'),
                cluster_ip=svc_data.get('cluster_ip', ''),
                external_ip=svc_data.get('external_ip', ''),
                ports=svc_data.get('ports', []),
                age_days=svc_data.get('age_days', 0),
                labels=svc_data.get('labels', {}),
                annotations=svc_data.get('annotations', {})
            )
            
            self.discovered_services.append(k8s_svc)
    
    def infer_capabilities(self, svc: K8sService) -> List[str]:
        """Infer service capabilities from name, labels, annotations"""
        
        capabilities = []
        
        name_lower = svc.name.lower()
        namespace_lower = svc.namespace.lower()
        
        # OBMI services
        if 'obmi' in name_lower or 'obmi' in namespace_lower:
            capabilities.append('obmi_validation')
            if 'aroe' in name_lower:
                capabilities.append('aroe_operator')
            elif 'qero' in name_lower:
                capabilities.append('qero_operator')
            elif 'aesp' in name_lower:
                capabilities.append('aesp_operator')
            elif 'prin' in name_lower:
                capabilities.append('prin_scoring')
        
        # Discovery services
        if 'discovery' in name_lower:
            capabilities.append('discovery_loop')
            capabilities.append('hypothesis_generation')
        
        # Deploy Anywhere
        if 'deploy-anywhere' in namespace_lower or 'deploy-anywhere' in name_lower:
            capabilities.append('deploy_anywhere')
            capabilities.append('capsule_deployment')
        
        # Protocol services
        if 'a2a' in name_lower:
            capabilities.append('a2a_protocol')
        if 'bitnet' in name_lower:
            capabilities.append('bitnet_protocol')
        if 'm2n2' in name_lower:
            capabilities.append('m2n2_protocol')
        if 'mcp' in name_lower:
            capabilities.append('mcp_protocol')
        
        # Enterprise services
        if 'billing' in name_lower:
            capabilities.append('billing')
        if 'sla' in name_lower:
            capabilities.append('sla_monitoring')
        if 'portal' in name_lower or 'client' in name_lower:
            capabilities.append('client_interface')
        
        # Optimization
        if 'optim' in name_lower:
            capabilities.append('optimization')
        if 'orchestrat' in name_lower:
            capabilities.append('orchestration')
        
        # Data & Visualization
        if 'real3d' in name_lower or 'visualization' in name_lower:
            capabilities.append('visualization')
        if 'conversion' in name_lower or 'etl' in name_lower:
            capabilities.append('data_processing')
        
        # Blockchain
        if 'ripple' in name_lower or 'nova' in name_lower or 'chrysalis' in name_lower:
            capabilities.append('blockchain')
        
        # Edge
        if 'edge' in name_lower or 'device' in name_lower:
            capabilities.append('edge_computing')
        
        # Quantum
        if 'quantum' in name_lower:
            capabilities.append('quantum_computing')
        
        # Default capability
        if not capabilities:
            capabilities.append('general_purpose')
        
        return capabilities
    
    def export_to_asi_registry(self, output_path: Path):
        """Export discovered services to ASI registry format"""
        
        asi_services = []
        
        for svc in self.discovered_services:
            # Determine endpoint
            if svc.external_ip and svc.external_ip != '<none>':
                ip = svc.external_ip
            else:
                ip = svc.cluster_ip
            
            # Get primary port
            port = 80
            protocol = 'http'
            if svc.ports:
                port = svc.ports[0].get('port', 80 )
                if port in [8200, 9090]:
                    protocol = 'grpc'
            
            endpoint = f"{protocol}://{ip}:{port}"
            
            # Infer capabilities
            capabilities = self.infer_capabilities(svc)
            
            # Calculate reliability based on age
            reliability = min(0.99, 0.80 + (svc.age_days / 30) * 0.15)
            
            asi_service = {
                'service_id': f"{svc.cloud}-{svc.namespace}-{svc.name}".replace('/', '-'),
                'service_type': protocol,
                'endpoint': endpoint,
                'protocol': protocol,
                'energy_cost': 0.1,
                'reliability': reliability,
                'capabilities': capabilities,
                'metadata': {
                    'cloud': svc.cloud,
                    'cluster': svc.cluster,
                    'namespace': svc.namespace,
                    'k8s_name': svc.name,
                    'service_type': svc.service_type,
                    'age_days': svc.age_days,
                    'labels': svc.labels
                }
            }
            
            asi_services.append(asi_service)
        
        # Save to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(asi_services, f, indent=2)
        
        print(f"✓ Exported {len(asi_services)} services to ASI registry")
        print(f"  File: {output_path}")
        
        # Statistics
        by_cloud = {}
        by_capability = {}
        
        for svc in asi_services:
            cloud = svc['metadata']['cloud']
            by_cloud[cloud] = by_cloud.get(cloud, 0) + 1
            
            for cap in svc['capabilities']:
                by_capability[cap] = by_capability.get(cap, 0) + 1
        
        print("\nStatistics:")
        print(f"  By Cloud: {by_cloud}")
        print(f"  Top Capabilities: {dict(sorted(by_capability.items(), key=lambda x: x[1], reverse=True)[:10])}")
        
        return asi_services


# Example usage - Simulating discovered services
if __name__ == "__main__":
    scanner = K8sServiceScanner()
    
    # Simulate Azure AKS cluster scan
    azure_services = [
        {
            'name': 'aroe-operator-service',
            'namespace': 'obmi-operators',
            'type': 'ClusterIP',
            'cluster_ip': '10.0.45.123',
            'external_ip': '<none>',
            'ports': [{'port': 8200, 'protocol': 'TCP'}],
            'age_days': 15.5,
            'labels': {'app': 'aroe', 'operator': 'obmi'},
            'annotations': {}
        },
        {
            'name': 'discovery-loop-v16',
            'namespace': 'discovery',
            'type': 'ClusterIP',
            'cluster_ip': '10.0.67.89',
            'external_ip': '<none>',
            'ports': [{'port': 8080, 'protocol': 'TCP'}],
            'age_days': 8.2,
            'labels': {'app': 'discovery', 'version': 'v16'},
            'annotations': {}
        },
        {
            'name': 'real3d-viewer',
            'namespace': 'visualization',
            'type': 'LoadBalancer',
            'cluster_ip': '10.0.89.45',
            'external_ip': '20.123.45.67',
            'ports': [{'port': 80, 'protocol': 'TCP'}],
            'age_days': 12.0,
            'labels': {'app': 'real3d'},
            'annotations': {}
        },
    ]
    
    scanner.scan_cluster('industriverse-azure-v2', 'azure', azure_services)
    
    # Simulate AWS EKS cluster scan
    aws_services = [
        {
            'name': 'quantum-advantage-calculator',
            'namespace': 'quantum-ops',
            'type': 'ClusterIP',
            'cluster_ip': '10.100.23.45',
            'external_ip': '<none>',
            'ports': [{'port': 8080, 'protocol': 'TCP'}],
            'age_days': 20.0,
            'labels': {'app': 'quantum'},
            'annotations': {}
        },
    ]
    
    scanner.scan_cluster('molecular-industrial', 'aws', aws_services)
    
    # Simulate GCP GKE cluster scan
    gcp_services = [
        {
            'name': 'edge-agent-controller',
            'namespace': 'edge-compute',
            'type': 'LoadBalancer',
            'cluster_ip': '10.200.34.56',
            'external_ip': '34.123.45.67',
            'ports': [{'port': 7200, 'protocol': 'TCP'}],
            'age_days': 25.0,
            'labels': {'app': 'edge'},
            'annotations': {}
        },
    ]
    
    scanner.scan_cluster('gke-cluster-1', 'gcp', gcp_services)
    
    # Export
    output_path = Path.home() / 'industriverse_week3' / 'systems' / 'asi' / 'registry' / 'discovered_services.json'
    scanner.export_to_asi_registry(output_path)
    
    print("\n" + "="*80)
    print(f"DISCOVERED {len(scanner.discovered_services)} SERVICES")
    print("READY FOR ASI REGISTRATION")
    print("="*80)
