"""
Istio Integration Manager

This module provides integration with Istio service mesh for the Deployment Operations Layer.
It handles service mesh configuration, traffic management, security, and observability.

Classes:
    IstioIntegrationManager: Manages Istio integration
    IstioTrafficManager: Manages Istio traffic routing
    IstioSecurityManager: Manages Istio security policies
    IstioObservabilityManager: Manages Istio observability
    IstioExecutor: Executes Istio CLI commands
"""

import json
import logging
import os
import subprocess
import tempfile
import yaml
from typing import Dict, List, Any, Optional, Tuple

from ....agent.agent_utils import AgentResponse
from ....protocol.mcp_integration.mcp_context_schema import MCPContext

logger = logging.getLogger(__name__)

class IstioIntegrationManager:
    """
    Manages Istio integration for the Deployment Operations Layer.
    
    This class provides a unified interface for interacting with Istio,
    handling service mesh configuration, traffic management, security, and observability.
    """
    
    def __init__(self, istioctl_binary_path: Optional[str] = None, 
                kubectl_binary_path: Optional[str] = None,
                working_dir: Optional[str] = None):
        """
        Initialize the Istio Integration Manager.
        
        Args:
            istioctl_binary_path: Path to istioctl binary (optional, defaults to 'istioctl' in PATH)
            kubectl_binary_path: Path to kubectl binary (optional, defaults to 'kubectl' in PATH)
            working_dir: Working directory for Istio operations (optional)
        """
        self.istioctl_binary = istioctl_binary_path or "istioctl"
        self.kubectl_binary = kubectl_binary_path or "kubectl"
        self.working_dir = working_dir or tempfile.mkdtemp(prefix="istio_")
        
        self.executor = IstioExecutor(self.istioctl_binary, self.kubectl_binary, self.working_dir)
        self.traffic_manager = IstioTrafficManager(self.executor)
        self.security_manager = IstioSecurityManager(self.executor)
        self.observability_manager = IstioObservabilityManager(self.executor)
        
        # Verify Istio installation
        self._verify_istio_installation()
    
    def _verify_istio_installation(self):
        """
        Verify that Istio is installed and available.
        
        Logs a warning if Istio is not installed but does not raise an exception
        as Istio may be accessed via API or other means.
        """
        try:
            version = self.executor.run_istioctl_command(["version"], check=False)
            logger.info(f"Istio client version: {version}")
        except Exception as e:
            logger.warning(f"Istio client not installed or not accessible: {str(e)}")
    
    def install_istio(self, profile: str = "default", 
                     namespace: str = "istio-system") -> AgentResponse:
        """
        Install Istio on a Kubernetes cluster.
        
        Args:
            profile: Istio installation profile (default: "default")
            namespace: Namespace to install Istio in (default: "istio-system")
            
        Returns:
            AgentResponse: Installation response
        """
        try:
            # Create namespace if it doesn't exist
            self.executor.run_kubectl_command([
                "create", "namespace", namespace, "--dry-run=client", "-o", "yaml"
            ], check=False)
            
            # Install Istio
            output = self.executor.run_istioctl_command([
                "install", "--set", f"profile={profile}", "-y"
            ])
            
            return AgentResponse(
                success=True,
                message=f"Istio installed successfully with profile {profile}",
                data={
                    "profile": profile,
                    "namespace": namespace,
                    "output": output
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to install Istio: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to install Istio: {str(e)}",
                data={}
            )
    
    def create_virtual_service(self, name: str, hosts: List[str], 
                              gateways: List[str], http_routes: List[Dict[str, Any]], 
                              namespace: str = "default") -> AgentResponse:
        """
        Create an Istio VirtualService.
        
        Args:
            name: VirtualService name
            hosts: List of hosts
            gateways: List of gateways
            http_routes: List of HTTP routes
            namespace: Namespace (default: "default")
            
        Returns:
            AgentResponse: VirtualService creation response
        """
        try:
            result = self.traffic_manager.create_virtual_service(
                name=name,
                hosts=hosts,
                gateways=gateways,
                http_routes=http_routes,
                namespace=namespace
            )
            
            return AgentResponse(
                success=True,
                message=f"Istio VirtualService {name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create Istio VirtualService: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create Istio VirtualService: {str(e)}",
                data={}
            )
    
    def create_destination_rule(self, name: str, host: str, 
                              subsets: List[Dict[str, Any]], 
                              namespace: str = "default") -> AgentResponse:
        """
        Create an Istio DestinationRule.
        
        Args:
            name: DestinationRule name
            host: Host
            subsets: List of subsets
            namespace: Namespace (default: "default")
            
        Returns:
            AgentResponse: DestinationRule creation response
        """
        try:
            result = self.traffic_manager.create_destination_rule(
                name=name,
                host=host,
                subsets=subsets,
                namespace=namespace
            )
            
            return AgentResponse(
                success=True,
                message=f"Istio DestinationRule {name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create Istio DestinationRule: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create Istio DestinationRule: {str(e)}",
                data={}
            )
    
    def create_gateway(self, name: str, selector: Dict[str, str], 
                      servers: List[Dict[str, Any]], 
                      namespace: str = "default") -> AgentResponse:
        """
        Create an Istio Gateway.
        
        Args:
            name: Gateway name
            selector: Gateway selector
            servers: List of servers
            namespace: Namespace (default: "default")
            
        Returns:
            AgentResponse: Gateway creation response
        """
        try:
            result = self.traffic_manager.create_gateway(
                name=name,
                selector=selector,
                servers=servers,
                namespace=namespace
            )
            
            return AgentResponse(
                success=True,
                message=f"Istio Gateway {name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create Istio Gateway: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create Istio Gateway: {str(e)}",
                data={}
            )
    
    def create_authorization_policy(self, name: str, selector: Dict[str, str], 
                                  rules: List[Dict[str, Any]], 
                                  namespace: str = "default") -> AgentResponse:
        """
        Create an Istio AuthorizationPolicy.
        
        Args:
            name: AuthorizationPolicy name
            selector: Policy selector
            rules: List of rules
            namespace: Namespace (default: "default")
            
        Returns:
            AgentResponse: AuthorizationPolicy creation response
        """
        try:
            result = self.security_manager.create_authorization_policy(
                name=name,
                selector=selector,
                rules=rules,
                namespace=namespace
            )
            
            return AgentResponse(
                success=True,
                message=f"Istio AuthorizationPolicy {name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create Istio AuthorizationPolicy: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create Istio AuthorizationPolicy: {str(e)}",
                data={}
            )
    
    def create_peer_authentication(self, name: str, selector: Dict[str, str], 
                                 mtls_mode: str, 
                                 namespace: str = "default") -> AgentResponse:
        """
        Create an Istio PeerAuthentication.
        
        Args:
            name: PeerAuthentication name
            selector: Policy selector
            mtls_mode: mTLS mode (e.g., "STRICT", "PERMISSIVE")
            namespace: Namespace (default: "default")
            
        Returns:
            AgentResponse: PeerAuthentication creation response
        """
        try:
            result = self.security_manager.create_peer_authentication(
                name=name,
                selector=selector,
                mtls_mode=mtls_mode,
                namespace=namespace
            )
            
            return AgentResponse(
                success=True,
                message=f"Istio PeerAuthentication {name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create Istio PeerAuthentication: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create Istio PeerAuthentication: {str(e)}",
                data={}
            )
    
    def analyze_mesh(self) -> AgentResponse:
        """
        Analyze the Istio service mesh for issues.
        
        Returns:
            AgentResponse: Analysis response
        """
        try:
            output = self.executor.run_istioctl_command(["analyze"])
            
            return AgentResponse(
                success=True,
                message="Istio mesh analysis completed",
                data={"output": output}
            )
        
        except Exception as e:
            logger.error(f"Failed to analyze Istio mesh: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to analyze Istio mesh: {str(e)}",
                data={}
            )
    
    def get_proxy_status(self, pod_name: Optional[str] = None, 
                        namespace: str = "default") -> AgentResponse:
        """
        Get the status of Istio proxies.
        
        Args:
            pod_name: Pod name (optional, if not provided, gets all proxies)
            namespace: Namespace (default: "default")
            
        Returns:
            AgentResponse: Proxy status response
        """
        try:
            args = ["proxy-status"]
            
            if pod_name:
                args.append(pod_name)
                args.extend(["-n", namespace])
            
            output = self.executor.run_istioctl_command(args)
            
            return AgentResponse(
                success=True,
                message="Retrieved Istio proxy status",
                data={"output": output}
            )
        
        except Exception as e:
            logger.error(f"Failed to get Istio proxy status: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to get Istio proxy status: {str(e)}",
                data={}
            )
    
    def dashboard(self, dashboard_name: str) -> AgentResponse:
        """
        Open an Istio dashboard.
        
        Args:
            dashboard_name: Dashboard name (e.g., "kiali", "grafana", "jaeger")
            
        Returns:
            AgentResponse: Dashboard response
        """
        try:
            # Run in background to avoid blocking
            args = ["dashboard", dashboard_name, "--browser=false"]
            
            # This will return the URL
            output = self.executor.run_istioctl_command(args, check=False)
            
            # Extract URL from output
            url = None
            for line in output.split("\n"):
                if "http://" in line or "https://" in line:
                    url = line.strip()
                    break
            
            return AgentResponse(
                success=True,
                message=f"Istio {dashboard_name} dashboard URL retrieved",
                data={"dashboard": dashboard_name, "url": url, "output": output}
            )
        
        except Exception as e:
            logger.error(f"Failed to get Istio dashboard: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to get Istio dashboard: {str(e)}",
                data={}
            )
    
    def to_mcp_context(self) -> MCPContext:
        """
        Convert Istio integration information to MCP context.
        
        Returns:
            MCPContext: MCP context with Istio integration information
        """
        return MCPContext(
            context_type="istio_integration",
            istio_version=self._get_istio_version(),
            working_dir=self.working_dir
        )
    
    def _get_istio_version(self) -> str:
        """
        Get the Istio version.
        
        Returns:
            str: Istio version
        """
        try:
            version_output = self.executor.run_istioctl_command(["version"], check=False)
            return version_output.strip()
        except Exception as e:
            logger.error(f"Failed to get Istio version: {str(e)}")
            return "unknown"


class IstioTrafficManager:
    """
    Manages Istio traffic routing.
    
    This class provides methods for managing Istio traffic routing resources,
    including VirtualServices, DestinationRules, and Gateways.
    """
    
    def __init__(self, executor: 'IstioExecutor'):
        """
        Initialize the Istio Traffic Manager.
        
        Args:
            executor: Istio executor
        """
        self.executor = executor
    
    def create_virtual_service(self, name: str, hosts: List[str], 
                              gateways: List[str], http_routes: List[Dict[str, Any]], 
                              namespace: str = "default") -> Dict[str, Any]:
        """
        Create an Istio VirtualService.
        
        Args:
            name: VirtualService name
            hosts: List of hosts
            gateways: List of gateways
            http_routes: List of HTTP routes
            namespace: Namespace (default: "default")
            
        Returns:
            Dict[str, Any]: VirtualService creation result
        """
        virtual_service = {
            "apiVersion": "networking.istio.io/v1alpha3",
            "kind": "VirtualService",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "hosts": hosts,
                "gateways": gateways,
                "http": http_routes
            }
        }
        
        # Write VirtualService to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(virtual_service, f)
            vs_file = f.name
        
        try:
            # Apply VirtualService
            output = self.executor.run_kubectl_command([
                "apply", "-f", vs_file
            ])
            
            return {
                "name": name,
                "namespace": namespace,
                "hosts": hosts,
                "gateways": gateways,
                "http_routes": http_routes,
                "output": output
            }
        
        finally:
            # Clean up temporary file
            if os.path.exists(vs_file):
                os.unlink(vs_file)
    
    def create_destination_rule(self, name: str, host: str, 
                              subsets: List[Dict[str, Any]], 
                              namespace: str = "default") -> Dict[str, Any]:
        """
        Create an Istio DestinationRule.
        
        Args:
            name: DestinationRule name
            host: Host
            subsets: List of subsets
            namespace: Namespace (default: "default")
            
        Returns:
            Dict[str, Any]: DestinationRule creation result
        """
        destination_rule = {
            "apiVersion": "networking.istio.io/v1alpha3",
            "kind": "DestinationRule",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "host": host,
                "subsets": subsets
            }
        }
        
        # Write DestinationRule to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(destination_rule, f)
            dr_file = f.name
        
        try:
            # Apply DestinationRule
            output = self.executor.run_kubectl_command([
                "apply", "-f", dr_file
            ])
            
            return {
                "name": name,
                "namespace": namespace,
                "host": host,
                "subsets": subsets,
                "output": output
            }
        
        finally:
            # Clean up temporary file
            if os.path.exists(dr_file):
                os.unlink(dr_file)
    
    def create_gateway(self, name: str, selector: Dict[str, str], 
                      servers: List[Dict[str, Any]], 
                      namespace: str = "default") -> Dict[str, Any]:
        """
        Create an Istio Gateway.
        
        Args:
            name: Gateway name
            selector: Gateway selector
            servers: List of servers
            namespace: Namespace (default: "default")
            
        Returns:
            Dict[str, Any]: Gateway creation result
        """
        gateway = {
            "apiVersion": "networking.istio.io/v1alpha3",
            "kind": "Gateway",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "selector": selector,
                "servers": servers
            }
        }
        
        # Write Gateway to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(gateway, f)
            gw_file = f.name
        
        try:
            # Apply Gateway
            output = self.executor.run_kubectl_command([
                "apply", "-f", gw_file
            ])
            
            return {
                "name": name,
                "namespace": namespace,
                "selector": selector,
                "servers": servers,
                "output": output
            }
        
        finally:
            # Clean up temporary file
            if os.path.exists(gw_file):
                os.unlink(gw_file)
    
    def list_virtual_services(self, namespace: str = "default") -> List[Dict[str, Any]]:
        """
        List Istio VirtualServices.
        
        Args:
            namespace: Namespace (default: "default")
            
        Returns:
            List[Dict[str, Any]]: List of VirtualServices
        """
        output = self.executor.run_kubectl_command([
            "get", "virtualservices", "-n", namespace, "-o", "json"
        ])
        
        try:
            vs_json = json.loads(output)
            
            virtual_services = []
            for vs in vs_json.get("items", []):
                vs_info = {
                    "name": vs["metadata"]["name"],
                    "namespace": vs["metadata"]["namespace"],
                    "hosts": vs["spec"].get("hosts", []),
                    "gateways": vs["spec"].get("gateways", []),
                    "http_routes": vs["spec"].get("http", [])
                }
                virtual_services.append(vs_info)
            
            return virtual_services
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse VirtualService list: {str(e)}")
            return []
    
    def list_destination_rules(self, namespace: str = "default") -> List[Dict[str, Any]]:
        """
        List Istio DestinationRules.
        
        Args:
            namespace: Namespace (default: "default")
            
        Returns:
            List[Dict[str, Any]]: List of DestinationRules
        """
        output = self.executor.run_kubectl_command([
            "get", "destinationrules", "-n", namespace, "-o", "json"
        ])
        
        try:
            dr_json = json.loads(output)
            
            destination_rules = []
            for dr in dr_json.get("items", []):
                dr_info = {
                    "name": dr["metadata"]["name"],
                    "namespace": dr["metadata"]["namespace"],
                    "host": dr["spec"].get("host"),
                    "subsets": dr["spec"].get("subsets", [])
                }
                destination_rules.append(dr_info)
            
            return destination_rules
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse DestinationRule list: {str(e)}")
            return []
    
    def list_gateways(self, namespace: str = "default") -> List[Dict[str, Any]]:
        """
        List Istio Gateways.
        
        Args:
            namespace: Namespace (default: "default")
            
        Returns:
            List[Dict[str, Any]]: List of Gateways
        """
        output = self.executor.run_kubectl_command([
            "get", "gateways", "-n", namespace, "-o", "json"
        ])
        
        try:
            gw_json = json.loads(output)
            
            gateways = []
            for gw in gw_json.get("items", []):
                gw_info = {
                    "name": gw["metadata"]["name"],
                    "namespace": gw["metadata"]["namespace"],
                    "selector": gw["spec"].get("selector", {}),
                    "servers": gw["spec"].get("servers", [])
                }
                gateways.append(gw_info)
            
            return gateways
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse Gateway list: {str(e)}")
            return []


class IstioSecurityManager:
    """
    Manages Istio security policies.
    
    This class provides methods for managing Istio security resources,
    including AuthorizationPolicies and PeerAuthentications.
    """
    
    def __init__(self, executor: 'IstioExecutor'):
        """
        Initialize the Istio Security Manager.
        
        Args:
            executor: Istio executor
        """
        self.executor = executor
    
    def create_authorization_policy(self, name: str, selector: Dict[str, str], 
                                  rules: List[Dict[str, Any]], 
                                  namespace: str = "default") -> Dict[str, Any]:
        """
        Create an Istio AuthorizationPolicy.
        
        Args:
            name: AuthorizationPolicy name
            selector: Policy selector
            rules: List of rules
            namespace: Namespace (default: "default")
            
        Returns:
            Dict[str, Any]: AuthorizationPolicy creation result
        """
        auth_policy = {
            "apiVersion": "security.istio.io/v1beta1",
            "kind": "AuthorizationPolicy",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "selector": {
                    "matchLabels": selector
                },
                "rules": rules
            }
        }
        
        # Write AuthorizationPolicy to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(auth_policy, f)
            policy_file = f.name
        
        try:
            # Apply AuthorizationPolicy
            output = self.executor.run_kubectl_command([
                "apply", "-f", policy_file
            ])
            
            return {
                "name": name,
                "namespace": namespace,
                "selector": selector,
                "rules": rules,
                "output": output
            }
        
        finally:
            # Clean up temporary file
            if os.path.exists(policy_file):
                os.unlink(policy_file)
    
    def create_peer_authentication(self, name: str, selector: Dict[str, str], 
                                 mtls_mode: str, 
                                 namespace: str = "default") -> Dict[str, Any]:
        """
        Create an Istio PeerAuthentication.
        
        Args:
            name: PeerAuthentication name
            selector: Policy selector
            mtls_mode: mTLS mode (e.g., "STRICT", "PERMISSIVE")
            namespace: Namespace (default: "default")
            
        Returns:
            Dict[str, Any]: PeerAuthentication creation result
        """
        peer_auth = {
            "apiVersion": "security.istio.io/v1beta1",
            "kind": "PeerAuthentication",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "selector": {
                    "matchLabels": selector
                },
                "mtls": {
                    "mode": mtls_mode
                }
            }
        }
        
        # Write PeerAuthentication to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(peer_auth, f)
            auth_file = f.name
        
        try:
            # Apply PeerAuthentication
            output = self.executor.run_kubectl_command([
                "apply", "-f", auth_file
            ])
            
            return {
                "name": name,
                "namespace": namespace,
                "selector": selector,
                "mtls_mode": mtls_mode,
                "output": output
            }
        
        finally:
            # Clean up temporary file
            if os.path.exists(auth_file):
                os.unlink(auth_file)
    
    def list_authorization_policies(self, namespace: str = "default") -> List[Dict[str, Any]]:
        """
        List Istio AuthorizationPolicies.
        
        Args:
            namespace: Namespace (default: "default")
            
        Returns:
            List[Dict[str, Any]]: List of AuthorizationPolicies
        """
        output = self.executor.run_kubectl_command([
            "get", "authorizationpolicies", "-n", namespace, "-o", "json"
        ])
        
        try:
            policy_json = json.loads(output)
            
            policies = []
            for policy in policy_json.get("items", []):
                policy_info = {
                    "name": policy["metadata"]["name"],
                    "namespace": policy["metadata"]["namespace"],
                    "selector": policy["spec"].get("selector", {}).get("matchLabels", {}),
                    "rules": policy["spec"].get("rules", [])
                }
                policies.append(policy_info)
            
            return policies
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse AuthorizationPolicy list: {str(e)}")
            return []
    
    def list_peer_authentications(self, namespace: str = "default") -> List[Dict[str, Any]]:
        """
        List Istio PeerAuthentications.
        
        Args:
            namespace: Namespace (default: "default")
            
        Returns:
            List[Dict[str, Any]]: List of PeerAuthentications
        """
        output = self.executor.run_kubectl_command([
            "get", "peerauthentications", "-n", namespace, "-o", "json"
        ])
        
        try:
            auth_json = json.loads(output)
            
            authentications = []
            for auth in auth_json.get("items", []):
                auth_info = {
                    "name": auth["metadata"]["name"],
                    "namespace": auth["metadata"]["namespace"],
                    "selector": auth["spec"].get("selector", {}).get("matchLabels", {}),
                    "mtls_mode": auth["spec"].get("mtls", {}).get("mode")
                }
                authentications.append(auth_info)
            
            return authentications
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse PeerAuthentication list: {str(e)}")
            return []


class IstioObservabilityManager:
    """
    Manages Istio observability.
    
    This class provides methods for managing Istio observability resources,
    including metrics, tracing, and logging.
    """
    
    def __init__(self, executor: 'IstioExecutor'):
        """
        Initialize the Istio Observability Manager.
        
        Args:
            executor: Istio executor
        """
        self.executor = executor
    
    def get_metrics(self, service_name: str, 
                   namespace: str = "default") -> Dict[str, Any]:
        """
        Get metrics for a service.
        
        Args:
            service_name: Service name
            namespace: Namespace (default: "default")
            
        Returns:
            Dict[str, Any]: Service metrics
        """
        # Use kubectl to get Prometheus metrics via Istio's metrics API
        output = self.executor.run_kubectl_command([
            "exec", "-it", "deploy/prometheus", "-n", "istio-system", "--",
            "curl", "-s", f"http://localhost:9090/api/v1/query?query=istio_requests_total{{destination_service=~\"{service_name}.*\",destination_workload_namespace=\"{namespace}\"}}"
        ], check=False)
        
        try:
            metrics_json = json.loads(output)
            
            return {
                "service_name": service_name,
                "namespace": namespace,
                "metrics": metrics_json
            }
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse metrics: {str(e)}")
            return {
                "service_name": service_name,
                "namespace": namespace,
                "error": str(e),
                "output": output
            }
    
    def get_service_graph(self, namespace: str = "default") -> Dict[str, Any]:
        """
        Get service graph for a namespace.
        
        Args:
            namespace: Namespace (default: "default")
            
        Returns:
            Dict[str, Any]: Service graph
        """
        # Use kubectl to get service graph via Kiali API
        output = self.executor.run_kubectl_command([
            "exec", "-it", "deploy/kiali", "-n", "istio-system", "--",
            "curl", "-s", f"http://localhost:20001/kiali/api/namespaces/{namespace}/graph?graphType=service"
        ], check=False)
        
        try:
            graph_json = json.loads(output)
            
            return {
                "namespace": namespace,
                "graph": graph_json
            }
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse service graph: {str(e)}")
            return {
                "namespace": namespace,
                "error": str(e),
                "output": output
            }
    
    def get_traces(self, service_name: str, 
                  namespace: str = "default") -> Dict[str, Any]:
        """
        Get traces for a service.
        
        Args:
            service_name: Service name
            namespace: Namespace (default: "default")
            
        Returns:
            Dict[str, Any]: Service traces
        """
        # Use kubectl to get traces via Jaeger API
        output = self.executor.run_kubectl_command([
            "exec", "-it", "deploy/jaeger", "-n", "istio-system", "--",
            "curl", "-s", f"http://localhost:16686/api/traces?service={service_name}.{namespace}"
        ], check=False)
        
        try:
            traces_json = json.loads(output)
            
            return {
                "service_name": service_name,
                "namespace": namespace,
                "traces": traces_json
            }
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse traces: {str(e)}")
            return {
                "service_name": service_name,
                "namespace": namespace,
                "error": str(e),
                "output": output
            }


class IstioExecutor:
    """
    Executes Istio CLI commands.
    
    This class provides methods for executing istioctl and kubectl commands
    and handling their output.
    """
    
    def __init__(self, istioctl_binary: str, kubectl_binary: str, working_dir: str):
        """
        Initialize the Istio Executor.
        
        Args:
            istioctl_binary: Path to istioctl binary
            kubectl_binary: Path to kubectl binary
            working_dir: Working directory for Istio operations
        """
        self.istioctl_binary = istioctl_binary
        self.kubectl_binary = kubectl_binary
        self.working_dir = working_dir
    
    def run_istioctl_command(self, args: List[str], check: bool = True) -> str:
        """
        Run an istioctl command.
        
        Args:
            args: Command arguments
            check: Whether to check for command success
            
        Returns:
            str: Command output
            
        Raises:
            Exception: If the command fails and check is True
        """
        cmd = [self.istioctl_binary] + args
        logger.info(f"Running istioctl command: {' '.join(cmd)}")
        
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
            error_message = f"istioctl command failed: {e.stderr}"
            logger.error(error_message)
            
            if check:
                raise Exception(error_message)
            
            return e.stderr
    
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
