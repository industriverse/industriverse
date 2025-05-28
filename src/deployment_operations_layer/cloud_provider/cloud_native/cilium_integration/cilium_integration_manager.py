"""
Cilium Integration Manager

This module provides integration with Cilium for the Deployment Operations Layer.
It handles deployment, configuration, and management of Cilium resources
including network policies, hubble observability, and service mesh capabilities.

Classes:
    CiliumIntegrationManager: Manages Cilium integration
    NetworkPolicyManager: Manages Cilium network policies
    HubbleManager: Manages Cilium Hubble observability
    ServiceMeshManager: Manages Cilium service mesh capabilities
    CiliumExecutor: Executes Cilium API calls
"""

import json
import logging
import os
import subprocess
import tempfile
import yaml
import requests
from typing import Dict, List, Any, Optional, Tuple, Union

from ....agent.agent_utils import AgentResponse
from ....protocol.mcp_integration.mcp_context_schema import MCPContext

logger = logging.getLogger(__name__)

class CiliumIntegrationManager:
    """
    Manages Cilium integration for the Deployment Operations Layer.
    
    This class provides a unified interface for interacting with Cilium,
    handling network policies, Hubble observability, and service mesh capabilities.
    """
    
    def __init__(self, kubectl_binary_path: Optional[str] = None,
                cilium_binary_path: Optional[str] = None,
                hubble_binary_path: Optional[str] = None,
                working_dir: Optional[str] = None,
                namespace: str = "kube-system"):
        """
        Initialize the Cilium Integration Manager.
        
        Args:
            kubectl_binary_path: Path to kubectl binary (optional, defaults to 'kubectl' in PATH)
            cilium_binary_path: Path to cilium CLI binary (optional, defaults to 'cilium' in PATH)
            hubble_binary_path: Path to hubble CLI binary (optional, defaults to 'hubble' in PATH)
            working_dir: Working directory for Cilium operations (optional)
            namespace: Kubernetes namespace for Cilium (default: kube-system)
        """
        self.kubectl_binary = kubectl_binary_path or "kubectl"
        self.cilium_binary = cilium_binary_path or "cilium"
        self.hubble_binary = hubble_binary_path or "hubble"
        self.working_dir = working_dir or tempfile.mkdtemp(prefix="cilium_")
        self.namespace = namespace
        
        self.executor = CiliumExecutor(
            self.kubectl_binary,
            self.cilium_binary,
            self.hubble_binary,
            self.working_dir,
            self.namespace
        )
        self.network_policy_manager = NetworkPolicyManager(self.executor)
        self.hubble_manager = HubbleManager(self.executor)
        self.service_mesh_manager = ServiceMeshManager(self.executor)
    
    def deploy_cilium(self, 
                     namespace: Optional[str] = None,
                     enable_hubble: bool = True,
                     enable_service_mesh: bool = False,
                     enable_kube_proxy_replacement: bool = True,
                     enable_external_ips: bool = True,
                     enable_host_reachable_services: bool = True,
                     enable_node_port: bool = True,
                     enable_bgp_control_plane: bool = False,
                     enable_ipv6: bool = False,
                     enable_bandwidth_manager: bool = True,
                     enable_wireguard: bool = False,
                     enable_encryption: bool = False,
                     helm_values: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Deploy Cilium to Kubernetes.
        
        Args:
            namespace: Kubernetes namespace (optional, defaults to self.namespace)
            enable_hubble: Whether to enable Hubble observability (default: True)
            enable_service_mesh: Whether to enable service mesh capabilities (default: False)
            enable_kube_proxy_replacement: Whether to enable kube-proxy replacement (default: True)
            enable_external_ips: Whether to enable external IPs (default: True)
            enable_host_reachable_services: Whether to enable host reachable services (default: True)
            enable_node_port: Whether to enable NodePort (default: True)
            enable_bgp_control_plane: Whether to enable BGP control plane (default: False)
            enable_ipv6: Whether to enable IPv6 (default: False)
            enable_bandwidth_manager: Whether to enable bandwidth manager (default: True)
            enable_wireguard: Whether to enable Wireguard (default: False)
            enable_encryption: Whether to enable encryption (default: False)
            helm_values: Additional Helm values (optional)
            
        Returns:
            AgentResponse: Deployment response
        """
        try:
            namespace = namespace or self.namespace
            
            # Create Helm values
            values = {
                "hubble": {
                    "enabled": enable_hubble,
                    "relay": {
                        "enabled": enable_hubble
                    },
                    "ui": {
                        "enabled": enable_hubble
                    }
                },
                "kubeProxyReplacement": "strict" if enable_kube_proxy_replacement else "disabled",
                "externalIPs": {
                    "enabled": enable_external_ips
                },
                "hostServices": {
                    "enabled": enable_host_reachable_services
                },
                "nodePort": {
                    "enabled": enable_node_port
                },
                "bgpControlPlane": {
                    "enabled": enable_bgp_control_plane
                },
                "ipv6": {
                    "enabled": enable_ipv6
                },
                "bandwidthManager": {
                    "enabled": enable_bandwidth_manager
                },
                "wireguard": {
                    "enabled": enable_wireguard
                },
                "encryption": {
                    "enabled": enable_encryption
                }
            }
            
            # Add service mesh values if enabled
            if enable_service_mesh:
                values["ingressController"] = {
                    "enabled": True
                }
                values["gatewayAPI"] = {
                    "enabled": True
                }
            
            # Add additional Helm values if provided
            if helm_values:
                values.update(helm_values)
            
            # Write Helm values to file
            values_path = os.path.join(self.working_dir, "cilium-values.yaml")
            with open(values_path, "w") as f:
                yaml.dump(values, f)
            
            # Add Cilium Helm repository
            subprocess.run(
                ["helm", "repo", "add", "cilium", "https://helm.cilium.io/"],
                cwd=self.working_dir,
                check=True
            )
            
            # Update Helm repositories
            subprocess.run(
                ["helm", "repo", "update"],
                cwd=self.working_dir,
                check=True
            )
            
            # Install Cilium
            subprocess.run(
                [
                    "helm", "upgrade", "--install",
                    "cilium", "cilium/cilium",
                    "--version", "1.14.0",
                    "--namespace", namespace,
                    "--values", values_path,
                    "--create-namespace"
                ],
                cwd=self.working_dir,
                check=True
            )
            
            return AgentResponse(
                success=True,
                message=f"Cilium deployed successfully to namespace {namespace}",
                data={
                    "namespace": namespace,
                    "hubble_enabled": enable_hubble,
                    "service_mesh_enabled": enable_service_mesh
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to deploy Cilium: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to deploy Cilium: {str(e)}",
                data={}
            )
    
    def create_network_policy(self, name: str, 
                             namespace: str,
                             specs: List[Dict[str, Any]]) -> AgentResponse:
        """
        Create a Cilium NetworkPolicy resource.
        
        Args:
            name: NetworkPolicy name
            namespace: Kubernetes namespace
            specs: List of policy specs
            
        Returns:
            AgentResponse: Creation response
        """
        try:
            # Create NetworkPolicy
            result = self.network_policy_manager.create_network_policy(
                name=name,
                namespace=namespace,
                specs=specs
            )
            
            return AgentResponse(
                success=True,
                message=f"NetworkPolicy {name} created successfully in namespace {namespace}",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create NetworkPolicy: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create NetworkPolicy: {str(e)}",
                data={}
            )
    
    def create_cluster_wide_network_policy(self, name: str, 
                                         specs: List[Dict[str, Any]]) -> AgentResponse:
        """
        Create a Cilium ClusterwideNetworkPolicy resource.
        
        Args:
            name: ClusterwideNetworkPolicy name
            specs: List of policy specs
            
        Returns:
            AgentResponse: Creation response
        """
        try:
            # Create ClusterwideNetworkPolicy
            result = self.network_policy_manager.create_cluster_wide_network_policy(
                name=name,
                specs=specs
            )
            
            return AgentResponse(
                success=True,
                message=f"ClusterwideNetworkPolicy {name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create ClusterwideNetworkPolicy: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create ClusterwideNetworkPolicy: {str(e)}",
                data={}
            )
    
    def enable_hubble(self) -> AgentResponse:
        """
        Enable Hubble observability.
        
        Returns:
            AgentResponse: Enablement response
        """
        try:
            # Enable Hubble
            result = self.hubble_manager.enable_hubble()
            
            return AgentResponse(
                success=True,
                message="Hubble enabled successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to enable Hubble: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to enable Hubble: {str(e)}",
                data={}
            )
    
    def get_hubble_status(self) -> AgentResponse:
        """
        Get Hubble status.
        
        Returns:
            AgentResponse: Status response
        """
        try:
            # Get Hubble status
            result = self.hubble_manager.get_hubble_status()
            
            return AgentResponse(
                success=True,
                message="Hubble status retrieved successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to get Hubble status: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to get Hubble status: {str(e)}",
                data={}
            )
    
    def enable_service_mesh(self) -> AgentResponse:
        """
        Enable Cilium service mesh capabilities.
        
        Returns:
            AgentResponse: Enablement response
        """
        try:
            # Enable service mesh
            result = self.service_mesh_manager.enable_service_mesh()
            
            return AgentResponse(
                success=True,
                message="Service mesh enabled successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to enable service mesh: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to enable service mesh: {str(e)}",
                data={}
            )
    
    def get_cilium_status(self) -> AgentResponse:
        """
        Get Cilium status.
        
        Returns:
            AgentResponse: Status response
        """
        try:
            # Get Cilium status
            result = self.executor.run_cilium_command(["status"])
            
            return AgentResponse(
                success=True,
                message="Cilium status retrieved successfully",
                data={
                    "status": result
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to get Cilium status: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to get Cilium status: {str(e)}",
                data={}
            )
    
    def to_mcp_context(self) -> MCPContext:
        """
        Convert Cilium integration information to MCP context.
        
        Returns:
            MCPContext: MCP context with Cilium integration information
        """
        return MCPContext(
            context_type="cilium_integration",
            namespace=self.namespace,
            working_dir=self.working_dir
        )


class NetworkPolicyManager:
    """
    Manages Cilium network policies.
    
    This class provides methods for creating, updating, and deleting Cilium network policies.
    """
    
    def __init__(self, executor: 'CiliumExecutor'):
        """
        Initialize the Network Policy Manager.
        
        Args:
            executor: Cilium executor
        """
        self.executor = executor
    
    def create_network_policy(self, name: str, 
                             namespace: str,
                             specs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a Cilium NetworkPolicy resource.
        
        Args:
            name: NetworkPolicy name
            namespace: Kubernetes namespace
            specs: List of policy specs
            
        Returns:
            Dict[str, Any]: Created NetworkPolicy
        """
        # Create NetworkPolicy
        network_policy = {
            "apiVersion": "cilium.io/v2",
            "kind": "CiliumNetworkPolicy",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "endpointSelector": specs[0].get("endpointSelector", {}),
                "ingress": specs[0].get("ingress", []),
                "egress": specs[0].get("egress", [])
            }
        }
        
        # Write NetworkPolicy to file
        network_policy_path = os.path.join(self.executor.working_dir, f"network-policy-{name}.yaml")
        with open(network_policy_path, "w") as f:
            yaml.dump(network_policy, f)
        
        # Apply NetworkPolicy
        self.executor.run_kubectl_command(["apply", "-f", network_policy_path])
        
        # Get created NetworkPolicy
        result = self.executor.run_kubectl_command([
            "get", "ciliumnetworkpolicies", name, "-n", namespace, "-o", "json"
        ])
        
        return json.loads(result)
    
    def create_cluster_wide_network_policy(self, name: str, 
                                         specs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a Cilium ClusterwideNetworkPolicy resource.
        
        Args:
            name: ClusterwideNetworkPolicy name
            specs: List of policy specs
            
        Returns:
            Dict[str, Any]: Created ClusterwideNetworkPolicy
        """
        # Create ClusterwideNetworkPolicy
        cluster_wide_network_policy = {
            "apiVersion": "cilium.io/v2",
            "kind": "CiliumClusterwideNetworkPolicy",
            "metadata": {
                "name": name
            },
            "spec": {
                "endpointSelector": specs[0].get("endpointSelector", {}),
                "ingress": specs[0].get("ingress", []),
                "egress": specs[0].get("egress", [])
            }
        }
        
        # Write ClusterwideNetworkPolicy to file
        cluster_wide_network_policy_path = os.path.join(self.executor.working_dir, f"cluster-wide-network-policy-{name}.yaml")
        with open(cluster_wide_network_policy_path, "w") as f:
            yaml.dump(cluster_wide_network_policy, f)
        
        # Apply ClusterwideNetworkPolicy
        self.executor.run_kubectl_command(["apply", "-f", cluster_wide_network_policy_path])
        
        # Get created ClusterwideNetworkPolicy
        result = self.executor.run_kubectl_command([
            "get", "ciliumclusterwidenetworkpolicies", name, "-o", "json"
        ])
        
        return json.loads(result)
    
    def update_network_policy(self, name: str, 
                             namespace: str,
                             specs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Update a Cilium NetworkPolicy resource.
        
        Args:
            name: NetworkPolicy name
            namespace: Kubernetes namespace
            specs: List of policy specs
            
        Returns:
            Dict[str, Any]: Updated NetworkPolicy
        """
        # Get existing NetworkPolicy
        try:
            existing_network_policy = self.executor.run_kubectl_command([
                "get", "ciliumnetworkpolicies", name, "-n", namespace, "-o", "json"
            ])
            existing_network_policy = json.loads(existing_network_policy)
        except Exception:
            # NetworkPolicy doesn't exist, create it
            return self.create_network_policy(
                name=name,
                namespace=namespace,
                specs=specs
            )
        
        # Update NetworkPolicy
        network_policy = {
            "apiVersion": "cilium.io/v2",
            "kind": "CiliumNetworkPolicy",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "endpointSelector": specs[0].get("endpointSelector", {}),
                "ingress": specs[0].get("ingress", []),
                "egress": specs[0].get("egress", [])
            }
        }
        
        # Write NetworkPolicy to file
        network_policy_path = os.path.join(self.executor.working_dir, f"network-policy-{name}.yaml")
        with open(network_policy_path, "w") as f:
            yaml.dump(network_policy, f)
        
        # Apply NetworkPolicy
        self.executor.run_kubectl_command(["apply", "-f", network_policy_path])
        
        # Get updated NetworkPolicy
        result = self.executor.run_kubectl_command([
            "get", "ciliumnetworkpolicies", name, "-n", namespace, "-o", "json"
        ])
        
        return json.loads(result)
    
    def update_cluster_wide_network_policy(self, name: str, 
                                         specs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Update a Cilium ClusterwideNetworkPolicy resource.
        
        Args:
            name: ClusterwideNetworkPolicy name
            specs: List of policy specs
            
        Returns:
            Dict[str, Any]: Updated ClusterwideNetworkPolicy
        """
        # Get existing ClusterwideNetworkPolicy
        try:
            existing_cluster_wide_network_policy = self.executor.run_kubectl_command([
                "get", "ciliumclusterwidenetworkpolicies", name, "-o", "json"
            ])
            existing_cluster_wide_network_policy = json.loads(existing_cluster_wide_network_policy)
        except Exception:
            # ClusterwideNetworkPolicy doesn't exist, create it
            return self.create_cluster_wide_network_policy(
                name=name,
                specs=specs
            )
        
        # Update ClusterwideNetworkPolicy
        cluster_wide_network_policy = {
            "apiVersion": "cilium.io/v2",
            "kind": "CiliumClusterwideNetworkPolicy",
            "metadata": {
                "name": name
            },
            "spec": {
                "endpointSelector": specs[0].get("endpointSelector", {}),
                "ingress": specs[0].get("ingress", []),
                "egress": specs[0].get("egress", [])
            }
        }
        
        # Write ClusterwideNetworkPolicy to file
        cluster_wide_network_policy_path = os.path.join(self.executor.working_dir, f"cluster-wide-network-policy-{name}.yaml")
        with open(cluster_wide_network_policy_path, "w") as f:
            yaml.dump(cluster_wide_network_policy, f)
        
        # Apply ClusterwideNetworkPolicy
        self.executor.run_kubectl_command(["apply", "-f", cluster_wide_network_policy_path])
        
        # Get updated ClusterwideNetworkPolicy
        result = self.executor.run_kubectl_command([
            "get", "ciliumclusterwidenetworkpolicies", name, "-o", "json"
        ])
        
        return json.loads(result)
    
    def delete_network_policy(self, name: str, namespace: str) -> None:
        """
        Delete a Cilium NetworkPolicy resource.
        
        Args:
            name: NetworkPolicy name
            namespace: Kubernetes namespace
        """
        self.executor.run_kubectl_command([
            "delete", "ciliumnetworkpolicies", name, "-n", namespace
        ])
    
    def delete_cluster_wide_network_policy(self, name: str) -> None:
        """
        Delete a Cilium ClusterwideNetworkPolicy resource.
        
        Args:
            name: ClusterwideNetworkPolicy name
        """
        self.executor.run_kubectl_command([
            "delete", "ciliumclusterwidenetworkpolicies", name
        ])
    
    def get_network_policy(self, name: str, namespace: str) -> Dict[str, Any]:
        """
        Get a Cilium NetworkPolicy resource.
        
        Args:
            name: NetworkPolicy name
            namespace: Kubernetes namespace
            
        Returns:
            Dict[str, Any]: NetworkPolicy
        """
        result = self.executor.run_kubectl_command([
            "get", "ciliumnetworkpolicies", name, "-n", namespace, "-o", "json"
        ])
        
        return json.loads(result)
    
    def get_cluster_wide_network_policy(self, name: str) -> Dict[str, Any]:
        """
        Get a Cilium ClusterwideNetworkPolicy resource.
        
        Args:
            name: ClusterwideNetworkPolicy name
            
        Returns:
            Dict[str, Any]: ClusterwideNetworkPolicy
        """
        result = self.executor.run_kubectl_command([
            "get", "ciliumclusterwidenetworkpolicies", name, "-o", "json"
        ])
        
        return json.loads(result)
    
    def list_network_policies(self, namespace: str) -> List[Dict[str, Any]]:
        """
        List Cilium NetworkPolicy resources.
        
        Args:
            namespace: Kubernetes namespace
            
        Returns:
            List[Dict[str, Any]]: NetworkPolicies
        """
        result = self.executor.run_kubectl_command([
            "get", "ciliumnetworkpolicies", "-n", namespace, "-o", "json"
        ])
        
        return json.loads(result).get("items", [])
    
    def list_cluster_wide_network_policies(self) -> List[Dict[str, Any]]:
        """
        List Cilium ClusterwideNetworkPolicy resources.
        
        Returns:
            List[Dict[str, Any]]: ClusterwideNetworkPolicies
        """
        result = self.executor.run_kubectl_command([
            "get", "ciliumclusterwidenetworkpolicies", "-o", "json"
        ])
        
        return json.loads(result).get("items", [])


class HubbleManager:
    """
    Manages Cilium Hubble observability.
    
    This class provides methods for enabling, configuring, and using Hubble observability.
    """
    
    def __init__(self, executor: 'CiliumExecutor'):
        """
        Initialize the Hubble Manager.
        
        Args:
            executor: Cilium executor
        """
        self.executor = executor
    
    def enable_hubble(self) -> Dict[str, Any]:
        """
        Enable Hubble observability.
        
        Returns:
            Dict[str, Any]: Enablement result
        """
        # Create Helm values for enabling Hubble
        values = {
            "hubble": {
                "enabled": True,
                "relay": {
                    "enabled": True
                },
                "ui": {
                    "enabled": True
                }
            }
        }
        
        # Write Helm values to file
        values_path = os.path.join(self.executor.working_dir, "hubble-values.yaml")
        with open(values_path, "w") as f:
            yaml.dump(values, f)
        
        # Update Cilium with Hubble enabled
        subprocess.run(
            [
                "helm", "upgrade", "cilium", "cilium/cilium",
                "--namespace", self.executor.namespace,
                "--values", values_path,
                "--reuse-values"
            ],
            cwd=self.executor.working_dir,
            check=True
        )
        
        # Wait for Hubble to be ready
        self.executor.run_kubectl_command([
            "rollout", "status", "deployment/hubble-relay", "-n", self.executor.namespace
        ])
        
        # Port-forward Hubble Relay
        subprocess.Popen(
            [
                self.executor.kubectl_binary,
                "port-forward", "deployment/hubble-relay",
                "-n", self.executor.namespace,
                "4245:4245"
            ],
            cwd=self.executor.working_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        return {
            "hubble_enabled": True,
            "hubble_relay_port": 4245
        }
    
    def get_hubble_status(self) -> Dict[str, Any]:
        """
        Get Hubble status.
        
        Returns:
            Dict[str, Any]: Hubble status
        """
        # Get Hubble status
        result = self.executor.run_hubble_command(["status"])
        
        # Parse status
        status = {}
        for line in result.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                status[key.strip()] = value.strip()
        
        return status
    
    def get_hubble_flows(self, namespace: Optional[str] = None,
                        selector: Optional[str] = None,
                        last: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get Hubble flows.
        
        Args:
            namespace: Kubernetes namespace (optional)
            selector: Flow selector (optional)
            last: Number of flows to retrieve (optional)
            
        Returns:
            List[Dict[str, Any]]: Hubble flows
        """
        # Build command
        command = ["observe"]
        
        if namespace:
            command.extend(["--namespace", namespace])
        
        if selector:
            command.extend(["--selector", selector])
        
        if last:
            command.extend(["--last", str(last)])
        
        command.append("--output=json")
        
        # Get Hubble flows
        result = self.executor.run_hubble_command(command)
        
        # Parse flows
        flows = []
        for line in result.splitlines():
            if line.strip():
                flows.append(json.loads(line))
        
        return flows
    
    def get_hubble_metrics(self) -> Dict[str, Any]:
        """
        Get Hubble metrics.
        
        Returns:
            Dict[str, Any]: Hubble metrics
        """
        # Get Hubble metrics
        result = self.executor.run_hubble_command(["metrics"])
        
        # Parse metrics
        metrics = {}
        current_metric = None
        
        for line in result.splitlines():
            line = line.strip()
            if not line:
                continue
            
            if line.startswith("Metric:"):
                current_metric = line.split(":", 1)[1].strip()
                metrics[current_metric] = {}
            elif current_metric and ":" in line:
                key, value = line.split(":", 1)
                metrics[current_metric][key.strip()] = value.strip()
        
        return metrics


class ServiceMeshManager:
    """
    Manages Cilium service mesh capabilities.
    
    This class provides methods for enabling, configuring, and using Cilium service mesh capabilities.
    """
    
    def __init__(self, executor: 'CiliumExecutor'):
        """
        Initialize the Service Mesh Manager.
        
        Args:
            executor: Cilium executor
        """
        self.executor = executor
    
    def enable_service_mesh(self) -> Dict[str, Any]:
        """
        Enable Cilium service mesh capabilities.
        
        Returns:
            Dict[str, Any]: Enablement result
        """
        # Create Helm values for enabling service mesh
        values = {
            "ingressController": {
                "enabled": True
            },
            "gatewayAPI": {
                "enabled": True
            }
        }
        
        # Write Helm values to file
        values_path = os.path.join(self.executor.working_dir, "service-mesh-values.yaml")
        with open(values_path, "w") as f:
            yaml.dump(values, f)
        
        # Update Cilium with service mesh enabled
        subprocess.run(
            [
                "helm", "upgrade", "cilium", "cilium/cilium",
                "--namespace", self.executor.namespace,
                "--values", values_path,
                "--reuse-values"
            ],
            cwd=self.executor.working_dir,
            check=True
        )
        
        return {
            "service_mesh_enabled": True
        }
    
    def create_gateway(self, name: str, 
                      namespace: str,
                      listeners: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a Gateway API Gateway resource.
        
        Args:
            name: Gateway name
            namespace: Kubernetes namespace
            listeners: List of listeners
            
        Returns:
            Dict[str, Any]: Created Gateway
        """
        # Create Gateway
        gateway = {
            "apiVersion": "gateway.networking.k8s.io/v1beta1",
            "kind": "Gateway",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "gatewayClassName": "cilium",
                "listeners": listeners
            }
        }
        
        # Write Gateway to file
        gateway_path = os.path.join(self.executor.working_dir, f"gateway-{name}.yaml")
        with open(gateway_path, "w") as f:
            yaml.dump(gateway, f)
        
        # Apply Gateway
        self.executor.run_kubectl_command(["apply", "-f", gateway_path])
        
        # Get created Gateway
        result = self.executor.run_kubectl_command([
            "get", "gateway", name, "-n", namespace, "-o", "json"
        ])
        
        return json.loads(result)
    
    def create_http_route(self, name: str, 
                         namespace: str,
                         parent_refs: List[Dict[str, Any]],
                         hostnames: List[str],
                         rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a Gateway API HTTPRoute resource.
        
        Args:
            name: HTTPRoute name
            namespace: Kubernetes namespace
            parent_refs: List of parent references
            hostnames: List of hostnames
            rules: List of rules
            
        Returns:
            Dict[str, Any]: Created HTTPRoute
        """
        # Create HTTPRoute
        http_route = {
            "apiVersion": "gateway.networking.k8s.io/v1beta1",
            "kind": "HTTPRoute",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "parentRefs": parent_refs,
                "hostnames": hostnames,
                "rules": rules
            }
        }
        
        # Write HTTPRoute to file
        http_route_path = os.path.join(self.executor.working_dir, f"http-route-{name}.yaml")
        with open(http_route_path, "w") as f:
            yaml.dump(http_route, f)
        
        # Apply HTTPRoute
        self.executor.run_kubectl_command(["apply", "-f", http_route_path])
        
        # Get created HTTPRoute
        result = self.executor.run_kubectl_command([
            "get", "httproute", name, "-n", namespace, "-o", "json"
        ])
        
        return json.loads(result)
    
    def create_tls_route(self, name: str, 
                        namespace: str,
                        parent_refs: List[Dict[str, Any]],
                        hostnames: List[str],
                        rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a Gateway API TLSRoute resource.
        
        Args:
            name: TLSRoute name
            namespace: Kubernetes namespace
            parent_refs: List of parent references
            hostnames: List of hostnames
            rules: List of rules
            
        Returns:
            Dict[str, Any]: Created TLSRoute
        """
        # Create TLSRoute
        tls_route = {
            "apiVersion": "gateway.networking.k8s.io/v1alpha2",
            "kind": "TLSRoute",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "parentRefs": parent_refs,
                "hostnames": hostnames,
                "rules": rules
            }
        }
        
        # Write TLSRoute to file
        tls_route_path = os.path.join(self.executor.working_dir, f"tls-route-{name}.yaml")
        with open(tls_route_path, "w") as f:
            yaml.dump(tls_route, f)
        
        # Apply TLSRoute
        self.executor.run_kubectl_command(["apply", "-f", tls_route_path])
        
        # Get created TLSRoute
        result = self.executor.run_kubectl_command([
            "get", "tlsroute", name, "-n", namespace, "-o", "json"
        ])
        
        return json.loads(result)


class CiliumExecutor:
    """
    Executes Cilium API calls and kubectl/cilium/hubble commands.
    
    This class provides methods for executing Cilium API calls and kubectl/cilium/hubble commands
    and handling their output.
    """
    
    def __init__(self, kubectl_binary: str,
                cilium_binary: str,
                hubble_binary: str,
                working_dir: str,
                namespace: str):
        """
        Initialize the Cilium Executor.
        
        Args:
            kubectl_binary: Path to kubectl binary
            cilium_binary: Path to cilium binary
            hubble_binary: Path to hubble binary
            working_dir: Working directory for Cilium operations
            namespace: Kubernetes namespace
        """
        self.kubectl_binary = kubectl_binary
        self.cilium_binary = cilium_binary
        self.hubble_binary = hubble_binary
        self.working_dir = working_dir
        self.namespace = namespace
    
    def run_kubectl_command(self, args: List[str], check: bool = True) -> str:
        """
        Run a kubectl command.
        
        Args:
            args: Command arguments
            check: Whether to check for command success
            
        Returns:
            str: Command output
            
        Raises:
            Exception: If the command fails and check is True
        """
        cmd = [self.kubectl_binary] + args
        logger.info(f"Running kubectl command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                check=check
            )
            
            return result.stdout
        
        except subprocess.CalledProcessError as e:
            error_message = f"kubectl command failed: {e.stderr}"
            logger.error(error_message)
            
            if check:
                raise Exception(error_message)
            
            return e.stderr
    
    def run_cilium_command(self, args: List[str], check: bool = True) -> str:
        """
        Run a cilium command.
        
        Args:
            args: Command arguments
            check: Whether to check for command success
            
        Returns:
            str: Command output
            
        Raises:
            Exception: If the command fails and check is True
        """
        cmd = [self.cilium_binary] + args
        logger.info(f"Running cilium command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                check=check
            )
            
            return result.stdout
        
        except subprocess.CalledProcessError as e:
            error_message = f"cilium command failed: {e.stderr}"
            logger.error(error_message)
            
            if check:
                raise Exception(error_message)
            
            return e.stderr
    
    def run_hubble_command(self, args: List[str], check: bool = True) -> str:
        """
        Run a hubble command.
        
        Args:
            args: Command arguments
            check: Whether to check for command success
            
        Returns:
            str: Command output
            
        Raises:
            Exception: If the command fails and check is True
        """
        cmd = [self.hubble_binary] + args
        logger.info(f"Running hubble command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                check=check
            )
            
            return result.stdout
        
        except subprocess.CalledProcessError as e:
            error_message = f"hubble command failed: {e.stderr}"
            logger.error(error_message)
            
            if check:
                raise Exception(error_message)
            
            return e.stderr
