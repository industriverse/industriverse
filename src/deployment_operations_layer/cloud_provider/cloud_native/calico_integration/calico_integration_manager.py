"""
Calico Integration Manager

This module provides integration with Calico for the Deployment Operations Layer.
It handles deployment, configuration, and management of Calico resources
including network policies, BGP configuration, and IPAM capabilities.

Classes:
    CalicoIntegrationManager: Manages Calico integration
    NetworkPolicyManager: Manages Calico network policies
    BGPConfigurationManager: Manages Calico BGP configuration
    IPAMManager: Manages Calico IPAM
    CalicoExecutor: Executes Calico API calls
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

class CalicoIntegrationManager:
    """
    Manages Calico integration for the Deployment Operations Layer.
    
    This class provides a unified interface for interacting with Calico,
    handling network policies, BGP configuration, and IPAM capabilities.
    """
    
    def __init__(self, kubectl_binary_path: Optional[str] = None,
                calicoctl_binary_path: Optional[str] = None,
                working_dir: Optional[str] = None,
                namespace: str = "kube-system"):
        """
        Initialize the Calico Integration Manager.
        
        Args:
            kubectl_binary_path: Path to kubectl binary (optional, defaults to 'kubectl' in PATH)
            calicoctl_binary_path: Path to calicoctl binary (optional, defaults to 'calicoctl' in PATH)
            working_dir: Working directory for Calico operations (optional)
            namespace: Kubernetes namespace for Calico (default: kube-system)
        """
        self.kubectl_binary = kubectl_binary_path or "kubectl"
        self.calicoctl_binary = calicoctl_binary_path or "calicoctl"
        self.working_dir = working_dir or tempfile.mkdtemp(prefix="calico_")
        self.namespace = namespace
        
        self.executor = CalicoExecutor(
            self.kubectl_binary,
            self.calicoctl_binary,
            self.working_dir,
            self.namespace
        )
        self.network_policy_manager = NetworkPolicyManager(self.executor)
        self.bgp_configuration_manager = BGPConfigurationManager(self.executor)
        self.ipam_manager = IPAMManager(self.executor)
    
    def deploy_calico(self, 
                     namespace: Optional[str] = None,
                     enable_bgp: bool = True,
                     enable_ipv6: bool = False,
                     mtu: int = 1440,
                     ip_autodetection_method: str = "first-found",
                     ipv6_autodetection_method: Optional[str] = None,
                     enable_typha: bool = True,
                     enable_felix_prometheus_metrics: bool = True,
                     enable_felix_wireguard: bool = False,
                     helm_values: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Deploy Calico to Kubernetes.
        
        Args:
            namespace: Kubernetes namespace (optional, defaults to self.namespace)
            enable_bgp: Whether to enable BGP (default: True)
            enable_ipv6: Whether to enable IPv6 (default: False)
            mtu: MTU to configure (default: 1440)
            ip_autodetection_method: IPv4 autodetection method (default: first-found)
            ipv6_autodetection_method: IPv6 autodetection method (optional)
            enable_typha: Whether to enable Typha (default: True)
            enable_felix_prometheus_metrics: Whether to enable Felix Prometheus metrics (default: True)
            enable_felix_wireguard: Whether to enable Felix Wireguard (default: False)
            helm_values: Additional Helm values (optional)
            
        Returns:
            AgentResponse: Deployment response
        """
        try:
            namespace = namespace or self.namespace
            
            # Create Helm values
            values = {
                "installation": {
                    "cni": {
                        "type": "Calico"
                    }
                },
                "calicoctl": {
                    "enabled": True
                },
                "ipam": {
                    "type": "Calico"
                },
                "mtu": mtu,
                "nodeAddressAutodetectionV4": {
                    "method": ip_autodetection_method
                },
                "typha": {
                    "enabled": enable_typha
                },
                "felix": {
                    "prometheusMetricsEnabled": enable_felix_prometheus_metrics,
                    "wireguard": {
                        "enabled": enable_felix_wireguard
                    }
                }
            }
            
            # Add IPv6 configuration if enabled
            if enable_ipv6:
                values["ipam"]["type"] = "Calico"
                values["ipam"]["assignIpv6"] = True
                if ipv6_autodetection_method:
                    values["nodeAddressAutodetectionV6"] = {
                        "method": ipv6_autodetection_method
                    }
            
            # Add BGP configuration if enabled
            if enable_bgp:
                values["bgp"] = {
                    "enabled": True
                }
            else:
                values["bgp"] = {
                    "enabled": False
                }
            
            # Add additional Helm values if provided
            if helm_values:
                values.update(helm_values)
            
            # Write Helm values to file
            values_path = os.path.join(self.working_dir, "calico-values.yaml")
            with open(values_path, "w") as f:
                yaml.dump(values, f)
            
            # Add Calico Helm repository
            subprocess.run(
                ["helm", "repo", "add", "projectcalico", "https://docs.projectcalico.org/charts"],
                cwd=self.working_dir,
                check=True
            )
            
            # Update Helm repositories
            subprocess.run(
                ["helm", "repo", "update"],
                cwd=self.working_dir,
                check=True
            )
            
            # Install Calico
            subprocess.run(
                [
                    "helm", "upgrade", "--install",
                    "calico", "projectcalico/tigera-operator",
                    "--version", "v3.26.0",
                    "--namespace", namespace,
                    "--values", values_path,
                    "--create-namespace"
                ],
                cwd=self.working_dir,
                check=True
            )
            
            return AgentResponse(
                success=True,
                message=f"Calico deployed successfully to namespace {namespace}",
                data={
                    "namespace": namespace,
                    "bgp_enabled": enable_bgp,
                    "ipv6_enabled": enable_ipv6
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to deploy Calico: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to deploy Calico: {str(e)}",
                data={}
            )
    
    def create_network_policy(self, name: str, 
                             namespace: str,
                             selector: str,
                             ingress_rules: List[Dict[str, Any]],
                             egress_rules: List[Dict[str, Any]],
                             types: Optional[List[str]] = None) -> AgentResponse:
        """
        Create a Calico NetworkPolicy resource.
        
        Args:
            name: NetworkPolicy name
            namespace: Kubernetes namespace
            selector: Selector for the policy
            ingress_rules: List of ingress rules
            egress_rules: List of egress rules
            types: Policy types (optional, defaults to ["Ingress", "Egress"])
            
        Returns:
            AgentResponse: Creation response
        """
        try:
            # Create NetworkPolicy
            result = self.network_policy_manager.create_network_policy(
                name=name,
                namespace=namespace,
                selector=selector,
                ingress_rules=ingress_rules,
                egress_rules=egress_rules,
                types=types
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
    
    def create_global_network_policy(self, name: str, 
                                   selector: str,
                                   ingress_rules: List[Dict[str, Any]],
                                   egress_rules: List[Dict[str, Any]],
                                   types: Optional[List[str]] = None) -> AgentResponse:
        """
        Create a Calico GlobalNetworkPolicy resource.
        
        Args:
            name: GlobalNetworkPolicy name
            selector: Selector for the policy
            ingress_rules: List of ingress rules
            egress_rules: List of egress rules
            types: Policy types (optional, defaults to ["Ingress", "Egress"])
            
        Returns:
            AgentResponse: Creation response
        """
        try:
            # Create GlobalNetworkPolicy
            result = self.network_policy_manager.create_global_network_policy(
                name=name,
                selector=selector,
                ingress_rules=ingress_rules,
                egress_rules=egress_rules,
                types=types
            )
            
            return AgentResponse(
                success=True,
                message=f"GlobalNetworkPolicy {name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create GlobalNetworkPolicy: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create GlobalNetworkPolicy: {str(e)}",
                data={}
            )
    
    def configure_bgp(self, as_number: int,
                     node_to_node_mesh_enabled: bool = True,
                     log_severity: str = "Info") -> AgentResponse:
        """
        Configure BGP for Calico.
        
        Args:
            as_number: AS number
            node_to_node_mesh_enabled: Whether to enable node-to-node mesh (default: True)
            log_severity: Log severity (default: Info)
            
        Returns:
            AgentResponse: Configuration response
        """
        try:
            # Configure BGP
            result = self.bgp_configuration_manager.configure_bgp(
                as_number=as_number,
                node_to_node_mesh_enabled=node_to_node_mesh_enabled,
                log_severity=log_severity
            )
            
            return AgentResponse(
                success=True,
                message="BGP configured successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to configure BGP: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to configure BGP: {str(e)}",
                data={}
            )
    
    def create_ip_pool(self, name: str,
                      cidr: str,
                      block_size: int = 26,
                      nat_outgoing: bool = True,
                      ipip_mode: str = "Always",
                      vxlan_mode: str = "Never",
                      disabled: bool = False) -> AgentResponse:
        """
        Create a Calico IPPool resource.
        
        Args:
            name: IPPool name
            cidr: CIDR for the pool
            block_size: Block size (default: 26)
            nat_outgoing: Whether to enable NAT for outgoing traffic (default: True)
            ipip_mode: IPIP mode (default: Always)
            vxlan_mode: VXLAN mode (default: Never)
            disabled: Whether the pool is disabled (default: False)
            
        Returns:
            AgentResponse: Creation response
        """
        try:
            # Create IPPool
            result = self.ipam_manager.create_ip_pool(
                name=name,
                cidr=cidr,
                block_size=block_size,
                nat_outgoing=nat_outgoing,
                ipip_mode=ipip_mode,
                vxlan_mode=vxlan_mode,
                disabled=disabled
            )
            
            return AgentResponse(
                success=True,
                message=f"IPPool {name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create IPPool: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create IPPool: {str(e)}",
                data={}
            )
    
    def get_calico_status(self) -> AgentResponse:
        """
        Get Calico status.
        
        Returns:
            AgentResponse: Status response
        """
        try:
            # Get Calico status
            result = self.executor.run_calicoctl_command(["node", "status"])
            
            return AgentResponse(
                success=True,
                message="Calico status retrieved successfully",
                data={
                    "status": result
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to get Calico status: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to get Calico status: {str(e)}",
                data={}
            )
    
    def to_mcp_context(self) -> MCPContext:
        """
        Convert Calico integration information to MCP context.
        
        Returns:
            MCPContext: MCP context with Calico integration information
        """
        return MCPContext(
            context_type="calico_integration",
            namespace=self.namespace,
            working_dir=self.working_dir
        )


class NetworkPolicyManager:
    """
    Manages Calico network policies.
    
    This class provides methods for creating, updating, and deleting Calico network policies.
    """
    
    def __init__(self, executor: 'CalicoExecutor'):
        """
        Initialize the Network Policy Manager.
        
        Args:
            executor: Calico executor
        """
        self.executor = executor
    
    def create_network_policy(self, name: str, 
                             namespace: str,
                             selector: str,
                             ingress_rules: List[Dict[str, Any]],
                             egress_rules: List[Dict[str, Any]],
                             types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create a Calico NetworkPolicy resource.
        
        Args:
            name: NetworkPolicy name
            namespace: Kubernetes namespace
            selector: Selector for the policy
            ingress_rules: List of ingress rules
            egress_rules: List of egress rules
            types: Policy types (optional, defaults to ["Ingress", "Egress"])
            
        Returns:
            Dict[str, Any]: Created NetworkPolicy
        """
        # Set default types if not provided
        if types is None:
            types = ["Ingress", "Egress"]
        
        # Create NetworkPolicy
        network_policy = {
            "apiVersion": "projectcalico.org/v3",
            "kind": "NetworkPolicy",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "selector": selector,
                "ingress": ingress_rules,
                "egress": egress_rules,
                "types": types
            }
        }
        
        # Write NetworkPolicy to file
        network_policy_path = os.path.join(self.executor.working_dir, f"network-policy-{name}.yaml")
        with open(network_policy_path, "w") as f:
            yaml.dump(network_policy, f)
        
        # Apply NetworkPolicy
        self.executor.run_calicoctl_command(["apply", "-f", network_policy_path])
        
        # Get created NetworkPolicy
        result = self.executor.run_calicoctl_command([
            "get", "networkpolicy", name, "-n", namespace, "-o", "json"
        ])
        
        return json.loads(result)
    
    def create_global_network_policy(self, name: str, 
                                   selector: str,
                                   ingress_rules: List[Dict[str, Any]],
                                   egress_rules: List[Dict[str, Any]],
                                   types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create a Calico GlobalNetworkPolicy resource.
        
        Args:
            name: GlobalNetworkPolicy name
            selector: Selector for the policy
            ingress_rules: List of ingress rules
            egress_rules: List of egress rules
            types: Policy types (optional, defaults to ["Ingress", "Egress"])
            
        Returns:
            Dict[str, Any]: Created GlobalNetworkPolicy
        """
        # Set default types if not provided
        if types is None:
            types = ["Ingress", "Egress"]
        
        # Create GlobalNetworkPolicy
        global_network_policy = {
            "apiVersion": "projectcalico.org/v3",
            "kind": "GlobalNetworkPolicy",
            "metadata": {
                "name": name
            },
            "spec": {
                "selector": selector,
                "ingress": ingress_rules,
                "egress": egress_rules,
                "types": types
            }
        }
        
        # Write GlobalNetworkPolicy to file
        global_network_policy_path = os.path.join(self.executor.working_dir, f"global-network-policy-{name}.yaml")
        with open(global_network_policy_path, "w") as f:
            yaml.dump(global_network_policy, f)
        
        # Apply GlobalNetworkPolicy
        self.executor.run_calicoctl_command(["apply", "-f", global_network_policy_path])
        
        # Get created GlobalNetworkPolicy
        result = self.executor.run_calicoctl_command([
            "get", "globalnetworkpolicy", name, "-o", "json"
        ])
        
        return json.loads(result)
    
    def update_network_policy(self, name: str, 
                             namespace: str,
                             selector: str,
                             ingress_rules: List[Dict[str, Any]],
                             egress_rules: List[Dict[str, Any]],
                             types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Update a Calico NetworkPolicy resource.
        
        Args:
            name: NetworkPolicy name
            namespace: Kubernetes namespace
            selector: Selector for the policy
            ingress_rules: List of ingress rules
            egress_rules: List of egress rules
            types: Policy types (optional, defaults to ["Ingress", "Egress"])
            
        Returns:
            Dict[str, Any]: Updated NetworkPolicy
        """
        # Set default types if not provided
        if types is None:
            types = ["Ingress", "Egress"]
        
        # Get existing NetworkPolicy
        try:
            existing_network_policy = self.executor.run_calicoctl_command([
                "get", "networkpolicy", name, "-n", namespace, "-o", "json"
            ])
            existing_network_policy = json.loads(existing_network_policy)
        except Exception:
            # NetworkPolicy doesn't exist, create it
            return self.create_network_policy(
                name=name,
                namespace=namespace,
                selector=selector,
                ingress_rules=ingress_rules,
                egress_rules=egress_rules,
                types=types
            )
        
        # Update NetworkPolicy
        network_policy = {
            "apiVersion": "projectcalico.org/v3",
            "kind": "NetworkPolicy",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "selector": selector,
                "ingress": ingress_rules,
                "egress": egress_rules,
                "types": types
            }
        }
        
        # Write NetworkPolicy to file
        network_policy_path = os.path.join(self.executor.working_dir, f"network-policy-{name}.yaml")
        with open(network_policy_path, "w") as f:
            yaml.dump(network_policy, f)
        
        # Apply NetworkPolicy
        self.executor.run_calicoctl_command(["apply", "-f", network_policy_path])
        
        # Get updated NetworkPolicy
        result = self.executor.run_calicoctl_command([
            "get", "networkpolicy", name, "-n", namespace, "-o", "json"
        ])
        
        return json.loads(result)
    
    def update_global_network_policy(self, name: str, 
                                   selector: str,
                                   ingress_rules: List[Dict[str, Any]],
                                   egress_rules: List[Dict[str, Any]],
                                   types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Update a Calico GlobalNetworkPolicy resource.
        
        Args:
            name: GlobalNetworkPolicy name
            selector: Selector for the policy
            ingress_rules: List of ingress rules
            egress_rules: List of egress rules
            types: Policy types (optional, defaults to ["Ingress", "Egress"])
            
        Returns:
            Dict[str, Any]: Updated GlobalNetworkPolicy
        """
        # Set default types if not provided
        if types is None:
            types = ["Ingress", "Egress"]
        
        # Get existing GlobalNetworkPolicy
        try:
            existing_global_network_policy = self.executor.run_calicoctl_command([
                "get", "globalnetworkpolicy", name, "-o", "json"
            ])
            existing_global_network_policy = json.loads(existing_global_network_policy)
        except Exception:
            # GlobalNetworkPolicy doesn't exist, create it
            return self.create_global_network_policy(
                name=name,
                selector=selector,
                ingress_rules=ingress_rules,
                egress_rules=egress_rules,
                types=types
            )
        
        # Update GlobalNetworkPolicy
        global_network_policy = {
            "apiVersion": "projectcalico.org/v3",
            "kind": "GlobalNetworkPolicy",
            "metadata": {
                "name": name
            },
            "spec": {
                "selector": selector,
                "ingress": ingress_rules,
                "egress": egress_rules,
                "types": types
            }
        }
        
        # Write GlobalNetworkPolicy to file
        global_network_policy_path = os.path.join(self.executor.working_dir, f"global-network-policy-{name}.yaml")
        with open(global_network_policy_path, "w") as f:
            yaml.dump(global_network_policy, f)
        
        # Apply GlobalNetworkPolicy
        self.executor.run_calicoctl_command(["apply", "-f", global_network_policy_path])
        
        # Get updated GlobalNetworkPolicy
        result = self.executor.run_calicoctl_command([
            "get", "globalnetworkpolicy", name, "-o", "json"
        ])
        
        return json.loads(result)
    
    def delete_network_policy(self, name: str, namespace: str) -> None:
        """
        Delete a Calico NetworkPolicy resource.
        
        Args:
            name: NetworkPolicy name
            namespace: Kubernetes namespace
        """
        self.executor.run_calicoctl_command([
            "delete", "networkpolicy", name, "-n", namespace
        ])
    
    def delete_global_network_policy(self, name: str) -> None:
        """
        Delete a Calico GlobalNetworkPolicy resource.
        
        Args:
            name: GlobalNetworkPolicy name
        """
        self.executor.run_calicoctl_command([
            "delete", "globalnetworkpolicy", name
        ])
    
    def get_network_policy(self, name: str, namespace: str) -> Dict[str, Any]:
        """
        Get a Calico NetworkPolicy resource.
        
        Args:
            name: NetworkPolicy name
            namespace: Kubernetes namespace
            
        Returns:
            Dict[str, Any]: NetworkPolicy
        """
        result = self.executor.run_calicoctl_command([
            "get", "networkpolicy", name, "-n", namespace, "-o", "json"
        ])
        
        return json.loads(result)
    
    def get_global_network_policy(self, name: str) -> Dict[str, Any]:
        """
        Get a Calico GlobalNetworkPolicy resource.
        
        Args:
            name: GlobalNetworkPolicy name
            
        Returns:
            Dict[str, Any]: GlobalNetworkPolicy
        """
        result = self.executor.run_calicoctl_command([
            "get", "globalnetworkpolicy", name, "-o", "json"
        ])
        
        return json.loads(result)
    
    def list_network_policies(self, namespace: str) -> List[Dict[str, Any]]:
        """
        List Calico NetworkPolicy resources.
        
        Args:
            namespace: Kubernetes namespace
            
        Returns:
            List[Dict[str, Any]]: NetworkPolicies
        """
        result = self.executor.run_calicoctl_command([
            "get", "networkpolicy", "-n", namespace, "-o", "json"
        ])
        
        return json.loads(result).get("items", [])
    
    def list_global_network_policies(self) -> List[Dict[str, Any]]:
        """
        List Calico GlobalNetworkPolicy resources.
        
        Returns:
            List[Dict[str, Any]]: GlobalNetworkPolicies
        """
        result = self.executor.run_calicoctl_command([
            "get", "globalnetworkpolicy", "-o", "json"
        ])
        
        return json.loads(result).get("items", [])


class BGPConfigurationManager:
    """
    Manages Calico BGP configuration.
    
    This class provides methods for configuring and managing Calico BGP.
    """
    
    def __init__(self, executor: 'CalicoExecutor'):
        """
        Initialize the BGP Configuration Manager.
        
        Args:
            executor: Calico executor
        """
        self.executor = executor
    
    def configure_bgp(self, as_number: int,
                     node_to_node_mesh_enabled: bool = True,
                     log_severity: str = "Info") -> Dict[str, Any]:
        """
        Configure BGP for Calico.
        
        Args:
            as_number: AS number
            node_to_node_mesh_enabled: Whether to enable node-to-node mesh (default: True)
            log_severity: Log severity (default: Info)
            
        Returns:
            Dict[str, Any]: BGP configuration
        """
        # Create BGP configuration
        bgp_configuration = {
            "apiVersion": "projectcalico.org/v3",
            "kind": "BGPConfiguration",
            "metadata": {
                "name": "default"
            },
            "spec": {
                "logSeverityScreen": log_severity,
                "nodeToNodeMeshEnabled": node_to_node_mesh_enabled,
                "asNumber": as_number
            }
        }
        
        # Write BGP configuration to file
        bgp_configuration_path = os.path.join(self.executor.working_dir, "bgp-configuration.yaml")
        with open(bgp_configuration_path, "w") as f:
            yaml.dump(bgp_configuration, f)
        
        # Apply BGP configuration
        self.executor.run_calicoctl_command(["apply", "-f", bgp_configuration_path])
        
        # Get BGP configuration
        result = self.executor.run_calicoctl_command([
            "get", "bgpconfig", "default", "-o", "json"
        ])
        
        return json.loads(result)
    
    def create_bgp_peer(self, name: str,
                       peer_ip: str,
                       as_number: int,
                       node_selector: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a Calico BGPPeer resource.
        
        Args:
            name: BGPPeer name
            peer_ip: Peer IP address
            as_number: AS number
            node_selector: Node selector (optional)
            
        Returns:
            Dict[str, Any]: Created BGPPeer
        """
        # Create BGPPeer
        bgp_peer = {
            "apiVersion": "projectcalico.org/v3",
            "kind": "BGPPeer",
            "metadata": {
                "name": name
            },
            "spec": {
                "peerIP": peer_ip,
                "asNumber": as_number
            }
        }
        
        # Add node selector if provided
        if node_selector:
            bgp_peer["spec"]["nodeSelector"] = node_selector
        
        # Write BGPPeer to file
        bgp_peer_path = os.path.join(self.executor.working_dir, f"bgp-peer-{name}.yaml")
        with open(bgp_peer_path, "w") as f:
            yaml.dump(bgp_peer, f)
        
        # Apply BGPPeer
        self.executor.run_calicoctl_command(["apply", "-f", bgp_peer_path])
        
        # Get created BGPPeer
        result = self.executor.run_calicoctl_command([
            "get", "bgppeer", name, "-o", "json"
        ])
        
        return json.loads(result)
    
    def update_bgp_peer(self, name: str,
                       peer_ip: str,
                       as_number: int,
                       node_selector: Optional[str] = None) -> Dict[str, Any]:
        """
        Update a Calico BGPPeer resource.
        
        Args:
            name: BGPPeer name
            peer_ip: Peer IP address
            as_number: AS number
            node_selector: Node selector (optional)
            
        Returns:
            Dict[str, Any]: Updated BGPPeer
        """
        # Get existing BGPPeer
        try:
            existing_bgp_peer = self.executor.run_calicoctl_command([
                "get", "bgppeer", name, "-o", "json"
            ])
            existing_bgp_peer = json.loads(existing_bgp_peer)
        except Exception:
            # BGPPeer doesn't exist, create it
            return self.create_bgp_peer(
                name=name,
                peer_ip=peer_ip,
                as_number=as_number,
                node_selector=node_selector
            )
        
        # Update BGPPeer
        bgp_peer = {
            "apiVersion": "projectcalico.org/v3",
            "kind": "BGPPeer",
            "metadata": {
                "name": name
            },
            "spec": {
                "peerIP": peer_ip,
                "asNumber": as_number
            }
        }
        
        # Add node selector if provided
        if node_selector:
            bgp_peer["spec"]["nodeSelector"] = node_selector
        
        # Write BGPPeer to file
        bgp_peer_path = os.path.join(self.executor.working_dir, f"bgp-peer-{name}.yaml")
        with open(bgp_peer_path, "w") as f:
            yaml.dump(bgp_peer, f)
        
        # Apply BGPPeer
        self.executor.run_calicoctl_command(["apply", "-f", bgp_peer_path])
        
        # Get updated BGPPeer
        result = self.executor.run_calicoctl_command([
            "get", "bgppeer", name, "-o", "json"
        ])
        
        return json.loads(result)
    
    def delete_bgp_peer(self, name: str) -> None:
        """
        Delete a Calico BGPPeer resource.
        
        Args:
            name: BGPPeer name
        """
        self.executor.run_calicoctl_command([
            "delete", "bgppeer", name
        ])
    
    def get_bgp_peer(self, name: str) -> Dict[str, Any]:
        """
        Get a Calico BGPPeer resource.
        
        Args:
            name: BGPPeer name
            
        Returns:
            Dict[str, Any]: BGPPeer
        """
        result = self.executor.run_calicoctl_command([
            "get", "bgppeer", name, "-o", "json"
        ])
        
        return json.loads(result)
    
    def list_bgp_peers(self) -> List[Dict[str, Any]]:
        """
        List Calico BGPPeer resources.
        
        Returns:
            List[Dict[str, Any]]: BGPPeers
        """
        result = self.executor.run_calicoctl_command([
            "get", "bgppeer", "-o", "json"
        ])
        
        return json.loads(result).get("items", [])
    
    def get_bgp_status(self) -> Dict[str, Any]:
        """
        Get BGP status.
        
        Returns:
            Dict[str, Any]: BGP status
        """
        result = self.executor.run_calicoctl_command([
            "node", "status"
        ])
        
        # Parse BGP status
        status = {}
        current_section = None
        
        for line in result.splitlines():
            line = line.strip()
            if not line:
                continue
            
            if line.startswith("IPv4 BGP status"):
                current_section = "ipv4_bgp_status"
                status[current_section] = []
            elif line.startswith("IPv6 BGP status"):
                current_section = "ipv6_bgp_status"
                status[current_section] = []
            elif current_section and "|" in line:
                parts = [part.strip() for part in line.split("|")]
                if len(parts) >= 4:
                    status[current_section].append({
                        "peer": parts[0],
                        "peer_as": parts[1],
                        "state": parts[2],
                        "since": parts[3]
                    })
        
        return status


class IPAMManager:
    """
    Manages Calico IPAM.
    
    This class provides methods for managing Calico IP address management.
    """
    
    def __init__(self, executor: 'CalicoExecutor'):
        """
        Initialize the IPAM Manager.
        
        Args:
            executor: Calico executor
        """
        self.executor = executor
    
    def create_ip_pool(self, name: str,
                      cidr: str,
                      block_size: int = 26,
                      nat_outgoing: bool = True,
                      ipip_mode: str = "Always",
                      vxlan_mode: str = "Never",
                      disabled: bool = False) -> Dict[str, Any]:
        """
        Create a Calico IPPool resource.
        
        Args:
            name: IPPool name
            cidr: CIDR for the pool
            block_size: Block size (default: 26)
            nat_outgoing: Whether to enable NAT for outgoing traffic (default: True)
            ipip_mode: IPIP mode (default: Always)
            vxlan_mode: VXLAN mode (default: Never)
            disabled: Whether the pool is disabled (default: False)
            
        Returns:
            Dict[str, Any]: Created IPPool
        """
        # Create IPPool
        ip_pool = {
            "apiVersion": "projectcalico.org/v3",
            "kind": "IPPool",
            "metadata": {
                "name": name
            },
            "spec": {
                "cidr": cidr,
                "blockSize": block_size,
                "natOutgoing": nat_outgoing,
                "ipipMode": ipip_mode,
                "vxlanMode": vxlan_mode,
                "disabled": disabled
            }
        }
        
        # Write IPPool to file
        ip_pool_path = os.path.join(self.executor.working_dir, f"ip-pool-{name}.yaml")
        with open(ip_pool_path, "w") as f:
            yaml.dump(ip_pool, f)
        
        # Apply IPPool
        self.executor.run_calicoctl_command(["apply", "-f", ip_pool_path])
        
        # Get created IPPool
        result = self.executor.run_calicoctl_command([
            "get", "ippool", name, "-o", "json"
        ])
        
        return json.loads(result)
    
    def update_ip_pool(self, name: str,
                      cidr: str,
                      block_size: int = 26,
                      nat_outgoing: bool = True,
                      ipip_mode: str = "Always",
                      vxlan_mode: str = "Never",
                      disabled: bool = False) -> Dict[str, Any]:
        """
        Update a Calico IPPool resource.
        
        Args:
            name: IPPool name
            cidr: CIDR for the pool
            block_size: Block size (default: 26)
            nat_outgoing: Whether to enable NAT for outgoing traffic (default: True)
            ipip_mode: IPIP mode (default: Always)
            vxlan_mode: VXLAN mode (default: Never)
            disabled: Whether the pool is disabled (default: False)
            
        Returns:
            Dict[str, Any]: Updated IPPool
        """
        # Get existing IPPool
        try:
            existing_ip_pool = self.executor.run_calicoctl_command([
                "get", "ippool", name, "-o", "json"
            ])
            existing_ip_pool = json.loads(existing_ip_pool)
        except Exception:
            # IPPool doesn't exist, create it
            return self.create_ip_pool(
                name=name,
                cidr=cidr,
                block_size=block_size,
                nat_outgoing=nat_outgoing,
                ipip_mode=ipip_mode,
                vxlan_mode=vxlan_mode,
                disabled=disabled
            )
        
        # Update IPPool
        ip_pool = {
            "apiVersion": "projectcalico.org/v3",
            "kind": "IPPool",
            "metadata": {
                "name": name
            },
            "spec": {
                "cidr": cidr,
                "blockSize": block_size,
                "natOutgoing": nat_outgoing,
                "ipipMode": ipip_mode,
                "vxlanMode": vxlan_mode,
                "disabled": disabled
            }
        }
        
        # Write IPPool to file
        ip_pool_path = os.path.join(self.executor.working_dir, f"ip-pool-{name}.yaml")
        with open(ip_pool_path, "w") as f:
            yaml.dump(ip_pool, f)
        
        # Apply IPPool
        self.executor.run_calicoctl_command(["apply", "-f", ip_pool_path])
        
        # Get updated IPPool
        result = self.executor.run_calicoctl_command([
            "get", "ippool", name, "-o", "json"
        ])
        
        return json.loads(result)
    
    def delete_ip_pool(self, name: str) -> None:
        """
        Delete a Calico IPPool resource.
        
        Args:
            name: IPPool name
        """
        self.executor.run_calicoctl_command([
            "delete", "ippool", name
        ])
    
    def get_ip_pool(self, name: str) -> Dict[str, Any]:
        """
        Get a Calico IPPool resource.
        
        Args:
            name: IPPool name
            
        Returns:
            Dict[str, Any]: IPPool
        """
        result = self.executor.run_calicoctl_command([
            "get", "ippool", name, "-o", "json"
        ])
        
        return json.loads(result)
    
    def list_ip_pools(self) -> List[Dict[str, Any]]:
        """
        List Calico IPPool resources.
        
        Returns:
            List[Dict[str, Any]]: IPPools
        """
        result = self.executor.run_calicoctl_command([
            "get", "ippool", "-o", "json"
        ])
        
        return json.loads(result).get("items", [])
    
    def get_ip_allocations(self) -> Dict[str, Any]:
        """
        Get IP allocations.
        
        Returns:
            Dict[str, Any]: IP allocations
        """
        result = self.executor.run_calicoctl_command([
            "ipam", "show"
        ])
        
        # Parse IP allocations
        allocations = {}
        current_node = None
        
        for line in result.splitlines():
            line = line.strip()
            if not line:
                continue
            
            if line.startswith("Node:"):
                current_node = line.split(":", 1)[1].strip()
                allocations[current_node] = {}
            elif current_node and ":" in line:
                key, value = line.split(":", 1)
                allocations[current_node][key.strip()] = value.strip()
        
        return allocations


class CalicoExecutor:
    """
    Executes Calico API calls and kubectl/calicoctl commands.
    
    This class provides methods for executing Calico API calls and kubectl/calicoctl commands
    and handling their output.
    """
    
    def __init__(self, kubectl_binary: str,
                calicoctl_binary: str,
                working_dir: str,
                namespace: str):
        """
        Initialize the Calico Executor.
        
        Args:
            kubectl_binary: Path to kubectl binary
            calicoctl_binary: Path to calicoctl binary
            working_dir: Working directory for Calico operations
            namespace: Kubernetes namespace
        """
        self.kubectl_binary = kubectl_binary
        self.calicoctl_binary = calicoctl_binary
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
    
    def run_calicoctl_command(self, args: List[str], check: bool = True) -> str:
        """
        Run a calicoctl command.
        
        Args:
            args: Command arguments
            check: Whether to check for command success
            
        Returns:
            str: Command output
            
        Raises:
            Exception: If the command fails and check is True
        """
        cmd = [self.calicoctl_binary] + args
        logger.info(f"Running calicoctl command: {' '.join(cmd)}")
        
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
            error_message = f"calicoctl command failed: {e.stderr}"
            logger.error(error_message)
            
            if check:
                raise Exception(error_message)
            
            return e.stderr
