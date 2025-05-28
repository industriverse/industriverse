"""
Cloud Native Integration Manager

This module provides integration with cloud-native technologies like Kubernetes, 
Istio, Knative, and other CNCF projects for the Deployment Operations Layer.
It handles deployment, service mesh, serverless, and observability integrations.

Classes:
    CloudNativeIntegrationManager: Manages cloud-native integrations
    KubernetesAdapter: Adapts to Kubernetes environments
    IstioAdapter: Adapts to Istio service mesh
    KnativeAdapter: Adapts to Knative serverless platform
    PrometheusAdapter: Adapts to Prometheus monitoring
"""

import json
import logging
import os
import subprocess
import tempfile
import yaml
from typing import Dict, List, Any, Optional, Tuple

from ..agent.agent_utils import AgentResponse
from ..protocol.mcp_integration.mcp_context_schema import MCPContext
from ..kubernetes.kubernetes_integration import KubernetesIntegration

logger = logging.getLogger(__name__)

class CloudNativeIntegrationManager:
    """
    Manages cloud-native integrations for the Deployment Operations Layer.
    
    This class provides a unified interface for interacting with cloud-native technologies,
    handling deployment, service mesh, serverless, and observability integrations.
    """
    
    def __init__(self, working_dir: Optional[str] = None):
        """
        Initialize the Cloud Native Integration Manager.
        
        Args:
            working_dir: Working directory for cloud-native operations (optional)
        """
        self.working_dir = working_dir or tempfile.mkdtemp(prefix="cloud_native_")
        
        # Initialize adapters
        self.kubernetes_adapter = KubernetesAdapter()
        self.istio_adapter = IstioAdapter(self.kubernetes_adapter)
        self.knative_adapter = KnativeAdapter(self.kubernetes_adapter)
        self.prometheus_adapter = PrometheusAdapter(self.kubernetes_adapter)
        
        # Verify installations
        self._verify_installations()
    
    def _verify_installations(self):
        """
        Verify that required tools are installed and available.
        
        Logs warnings if tools are not installed but does not raise exceptions
        as some tools may be optional depending on the deployment environment.
        """
        # Check kubectl
        try:
            version = self.kubernetes_adapter.get_version()
            logger.info(f"Kubernetes client version: {version}")
        except Exception as e:
            logger.warning(f"Kubernetes client not installed or not accessible: {str(e)}")
        
        # Check istioctl
        try:
            version = self.istio_adapter.get_version()
            logger.info(f"Istio version: {version}")
        except Exception as e:
            logger.warning(f"Istio not installed or not accessible: {str(e)}")
        
        # Check kn
        try:
            version = self.knative_adapter.get_version()
            logger.info(f"Knative version: {version}")
        except Exception as e:
            logger.warning(f"Knative not installed or not accessible: {str(e)}")
    
    def deploy_application(self, name: str, namespace: str, 
                          manifests: List[Dict[str, Any]], 
                          service_mesh: bool = False,
                          serverless: bool = False,
                          monitoring: bool = True) -> AgentResponse:
        """
        Deploy an application to a Kubernetes cluster with optional cloud-native features.
        
        Args:
            name: Application name
            namespace: Kubernetes namespace
            manifests: List of Kubernetes manifests
            service_mesh: Whether to enable service mesh (Istio)
            serverless: Whether to deploy as serverless (Knative)
            monitoring: Whether to enable monitoring (Prometheus)
            
        Returns:
            AgentResponse: Deployment response
        """
        try:
            # Create namespace if it doesn't exist
            self.kubernetes_adapter.create_namespace(namespace)
            
            # Apply service mesh if requested
            if service_mesh:
                self.istio_adapter.enable_for_namespace(namespace)
            
            # Modify manifests for serverless if requested
            if serverless:
                manifests = self.knative_adapter.adapt_manifests(manifests)
            
            # Add monitoring annotations if requested
            if monitoring:
                manifests = self.prometheus_adapter.add_monitoring(manifests)
            
            # Deploy manifests
            results = []
            for manifest in manifests:
                result = self.kubernetes_adapter.apply_manifest(manifest, namespace)
                results.append(result)
            
            return AgentResponse(
                success=True,
                message=f"Application {name} deployed successfully to namespace {namespace}",
                data={
                    "name": name,
                    "namespace": namespace,
                    "service_mesh": service_mesh,
                    "serverless": serverless,
                    "monitoring": monitoring,
                    "results": results
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to deploy application: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to deploy application: {str(e)}",
                data={}
            )
    
    def get_application_status(self, name: str, namespace: str) -> AgentResponse:
        """
        Get the status of a deployed application.
        
        Args:
            name: Application name
            namespace: Kubernetes namespace
            
        Returns:
            AgentResponse: Application status response
        """
        try:
            # Get deployment status
            deployment_status = self.kubernetes_adapter.get_deployment_status(name, namespace)
            
            # Get service status
            service_status = self.kubernetes_adapter.get_service_status(name, namespace)
            
            # Get pod statuses
            pod_statuses = self.kubernetes_adapter.get_pod_statuses(name, namespace)
            
            # Get Istio status if available
            istio_status = {}
            try:
                istio_status = self.istio_adapter.get_status(name, namespace)
            except Exception as e:
                logger.warning(f"Failed to get Istio status: {str(e)}")
            
            # Get Knative status if available
            knative_status = {}
            try:
                knative_status = self.knative_adapter.get_status(name, namespace)
            except Exception as e:
                logger.warning(f"Failed to get Knative status: {str(e)}")
            
            # Get Prometheus metrics if available
            prometheus_metrics = {}
            try:
                prometheus_metrics = self.prometheus_adapter.get_metrics(name, namespace)
            except Exception as e:
                logger.warning(f"Failed to get Prometheus metrics: {str(e)}")
            
            return AgentResponse(
                success=True,
                message=f"Retrieved status for application {name} in namespace {namespace}",
                data={
                    "name": name,
                    "namespace": namespace,
                    "deployment": deployment_status,
                    "service": service_status,
                    "pods": pod_statuses,
                    "istio": istio_status,
                    "knative": knative_status,
                    "prometheus": prometheus_metrics
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to get application status: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to get application status: {str(e)}",
                data={}
            )
    
    def delete_application(self, name: str, namespace: str) -> AgentResponse:
        """
        Delete a deployed application.
        
        Args:
            name: Application name
            namespace: Kubernetes namespace
            
        Returns:
            AgentResponse: Deletion response
        """
        try:
            # Delete Knative resources if they exist
            try:
                self.knative_adapter.delete_resources(name, namespace)
            except Exception as e:
                logger.warning(f"Failed to delete Knative resources: {str(e)}")
            
            # Delete Istio resources if they exist
            try:
                self.istio_adapter.delete_resources(name, namespace)
            except Exception as e:
                logger.warning(f"Failed to delete Istio resources: {str(e)}")
            
            # Delete Kubernetes resources
            self.kubernetes_adapter.delete_deployment(name, namespace)
            self.kubernetes_adapter.delete_service(name, namespace)
            
            return AgentResponse(
                success=True,
                message=f"Application {name} deleted successfully from namespace {namespace}",
                data={
                    "name": name,
                    "namespace": namespace
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to delete application: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to delete application: {str(e)}",
                data={}
            )
    
    def get_cluster_info(self) -> AgentResponse:
        """
        Get information about the Kubernetes cluster.
        
        Returns:
            AgentResponse: Cluster information response
        """
        try:
            # Get Kubernetes cluster info
            cluster_info = self.kubernetes_adapter.get_cluster_info()
            
            # Get Istio info if available
            istio_info = {}
            try:
                istio_info = self.istio_adapter.get_cluster_info()
            except Exception as e:
                logger.warning(f"Failed to get Istio cluster info: {str(e)}")
            
            # Get Knative info if available
            knative_info = {}
            try:
                knative_info = self.knative_adapter.get_cluster_info()
            except Exception as e:
                logger.warning(f"Failed to get Knative cluster info: {str(e)}")
            
            # Get Prometheus info if available
            prometheus_info = {}
            try:
                prometheus_info = self.prometheus_adapter.get_cluster_info()
            except Exception as e:
                logger.warning(f"Failed to get Prometheus cluster info: {str(e)}")
            
            return AgentResponse(
                success=True,
                message="Retrieved cluster information",
                data={
                    "kubernetes": cluster_info,
                    "istio": istio_info,
                    "knative": knative_info,
                    "prometheus": prometheus_info
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to get cluster information: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to get cluster information: {str(e)}",
                data={}
            )
    
    def to_mcp_context(self) -> MCPContext:
        """
        Convert cloud-native integration information to MCP context.
        
        Returns:
            MCPContext: MCP context with cloud-native integration information
        """
        return MCPContext(
            context_type="cloud_native_integration",
            kubernetes_version=self.kubernetes_adapter.get_version(),
            istio_version=self.istio_adapter.get_version(),
            knative_version=self.knative_adapter.get_version(),
            working_dir=self.working_dir
        )


class KubernetesAdapter:
    """
    Adapts to Kubernetes environments.
    
    This class provides methods for interacting with Kubernetes clusters,
    handling deployments, services, and other Kubernetes resources.
    """
    
    def __init__(self, kubectl_binary: str = "kubectl"):
        """
        Initialize the Kubernetes Adapter.
        
        Args:
            kubectl_binary: Path to kubectl binary (default: "kubectl")
        """
        self.kubectl_binary = kubectl_binary
        self.kubernetes_integration = KubernetesIntegration()
    
    def run_command(self, args: List[str], check: bool = True) -> str:
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
    
    def get_version(self) -> str:
        """
        Get the kubectl version.
        
        Returns:
            str: kubectl version
        """
        output = self.run_command(["version", "--client", "--output=json"])
        
        try:
            version_json = json.loads(output)
            return version_json["clientVersion"]["gitVersion"]
        except (json.JSONDecodeError, KeyError):
            # If JSON parsing fails, extract version from output
            if "Client Version:" in output:
                version_line = [line for line in output.split("\n") if "Client Version:" in line][0]
                return version_line.split("Client Version:")[1].strip()
            else:
                return "unknown"
    
    def create_namespace(self, namespace: str) -> Dict[str, Any]:
        """
        Create a Kubernetes namespace if it doesn't exist.
        
        Args:
            namespace: Namespace name
            
        Returns:
            Dict[str, Any]: Namespace creation result
        """
        # Check if namespace exists
        try:
            self.run_command(["get", "namespace", namespace])
            return {"status": "exists", "namespace": namespace}
        except Exception:
            # Namespace doesn't exist, create it
            output = self.run_command(["create", "namespace", namespace])
            return {"status": "created", "namespace": namespace, "output": output}
    
    def apply_manifest(self, manifest: Dict[str, Any], namespace: str) -> Dict[str, Any]:
        """
        Apply a Kubernetes manifest.
        
        Args:
            manifest: Kubernetes manifest
            namespace: Namespace to apply the manifest to
            
        Returns:
            Dict[str, Any]: Manifest application result
        """
        # Write manifest to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(manifest, f)
            manifest_file = f.name
        
        try:
            # Apply manifest
            output = self.run_command(["apply", "-f", manifest_file, "-n", namespace])
            
            return {
                "status": "applied",
                "kind": manifest.get("kind"),
                "name": manifest.get("metadata", {}).get("name"),
                "namespace": namespace,
                "output": output
            }
        
        finally:
            # Clean up temporary file
            os.unlink(manifest_file)
    
    def get_deployment_status(self, name: str, namespace: str) -> Dict[str, Any]:
        """
        Get the status of a Kubernetes deployment.
        
        Args:
            name: Deployment name
            namespace: Namespace
            
        Returns:
            Dict[str, Any]: Deployment status
        """
        try:
            output = self.run_command(["get", "deployment", name, "-n", namespace, "-o", "json"])
            deployment = json.loads(output)
            
            return {
                "name": deployment["metadata"]["name"],
                "namespace": deployment["metadata"]["namespace"],
                "replicas": deployment["spec"]["replicas"],
                "available_replicas": deployment["status"].get("availableReplicas", 0),
                "ready_replicas": deployment["status"].get("readyReplicas", 0),
                "updated_replicas": deployment["status"].get("updatedReplicas", 0),
                "conditions": deployment["status"].get("conditions", [])
            }
        
        except Exception as e:
            logger.error(f"Failed to get deployment status: {str(e)}")
            return {"error": str(e)}
    
    def get_service_status(self, name: str, namespace: str) -> Dict[str, Any]:
        """
        Get the status of a Kubernetes service.
        
        Args:
            name: Service name
            namespace: Namespace
            
        Returns:
            Dict[str, Any]: Service status
        """
        try:
            output = self.run_command(["get", "service", name, "-n", namespace, "-o", "json"])
            service = json.loads(output)
            
            return {
                "name": service["metadata"]["name"],
                "namespace": service["metadata"]["namespace"],
                "type": service["spec"]["type"],
                "cluster_ip": service["spec"].get("clusterIP"),
                "external_ips": service["spec"].get("externalIPs", []),
                "ports": service["spec"].get("ports", []),
                "selector": service["spec"].get("selector", {})
            }
        
        except Exception as e:
            logger.error(f"Failed to get service status: {str(e)}")
            return {"error": str(e)}
    
    def get_pod_statuses(self, selector: str, namespace: str) -> List[Dict[str, Any]]:
        """
        Get the statuses of Kubernetes pods matching a selector.
        
        Args:
            selector: Pod selector (e.g., "app=myapp")
            namespace: Namespace
            
        Returns:
            List[Dict[str, Any]]: Pod statuses
        """
        try:
            output = self.run_command(["get", "pods", "-l", f"app={selector}", "-n", namespace, "-o", "json"])
            pods_json = json.loads(output)
            
            pod_statuses = []
            for pod in pods_json.get("items", []):
                pod_status = {
                    "name": pod["metadata"]["name"],
                    "namespace": pod["metadata"]["namespace"],
                    "phase": pod["status"]["phase"],
                    "conditions": pod["status"].get("conditions", []),
                    "container_statuses": pod["status"].get("containerStatuses", [])
                }
                pod_statuses.append(pod_status)
            
            return pod_statuses
        
        except Exception as e:
            logger.error(f"Failed to get pod statuses: {str(e)}")
            return [{"error": str(e)}]
    
    def delete_deployment(self, name: str, namespace: str) -> Dict[str, Any]:
        """
        Delete a Kubernetes deployment.
        
        Args:
            name: Deployment name
            namespace: Namespace
            
        Returns:
            Dict[str, Any]: Deployment deletion result
        """
        try:
            output = self.run_command(["delete", "deployment", name, "-n", namespace])
            
            return {
                "status": "deleted",
                "kind": "Deployment",
                "name": name,
                "namespace": namespace,
                "output": output
            }
        
        except Exception as e:
            logger.error(f"Failed to delete deployment: {str(e)}")
            return {"error": str(e)}
    
    def delete_service(self, name: str, namespace: str) -> Dict[str, Any]:
        """
        Delete a Kubernetes service.
        
        Args:
            name: Service name
            namespace: Namespace
            
        Returns:
            Dict[str, Any]: Service deletion result
        """
        try:
            output = self.run_command(["delete", "service", name, "-n", namespace])
            
            return {
                "status": "deleted",
                "kind": "Service",
                "name": name,
                "namespace": namespace,
                "output": output
            }
        
        except Exception as e:
            logger.error(f"Failed to delete service: {str(e)}")
            return {"error": str(e)}
    
    def get_cluster_info(self) -> Dict[str, Any]:
        """
        Get information about the Kubernetes cluster.
        
        Returns:
            Dict[str, Any]: Cluster information
        """
        try:
            # Get cluster info
            cluster_info_output = self.run_command(["cluster-info"])
            
            # Get nodes
            nodes_output = self.run_command(["get", "nodes", "-o", "json"])
            nodes_json = json.loads(nodes_output)
            
            # Get namespaces
            namespaces_output = self.run_command(["get", "namespaces", "-o", "json"])
            namespaces_json = json.loads(namespaces_output)
            
            # Get version
            version = self.get_version()
            
            return {
                "cluster_info": cluster_info_output,
                "version": version,
                "nodes": [
                    {
                        "name": node["metadata"]["name"],
                        "status": node["status"]["conditions"],
                        "capacity": node["status"]["capacity"],
                        "allocatable": node["status"]["allocatable"]
                    }
                    for node in nodes_json.get("items", [])
                ],
                "namespaces": [
                    {
                        "name": namespace["metadata"]["name"],
                        "status": namespace["status"]["phase"]
                    }
                    for namespace in namespaces_json.get("items", [])
                ]
            }
        
        except Exception as e:
            logger.error(f"Failed to get cluster information: {str(e)}")
            return {"error": str(e)}


class IstioAdapter:
    """
    Adapts to Istio service mesh.
    
    This class provides methods for interacting with Istio service mesh,
    handling virtual services, gateways, and other Istio resources.
    """
    
    def __init__(self, kubernetes_adapter: KubernetesAdapter, istioctl_binary: str = "istioctl"):
        """
        Initialize the Istio Adapter.
        
        Args:
            kubernetes_adapter: Kubernetes adapter
            istioctl_binary: Path to istioctl binary (default: "istioctl")
        """
        self.kubernetes_adapter = kubernetes_adapter
        self.istioctl_binary = istioctl_binary
    
    def run_command(self, args: List[str], check: bool = True) -> str:
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
    
    def get_version(self) -> str:
        """
        Get the Istio version.
        
        Returns:
            str: Istio version
        """
        try:
            output = self.run_command(["version", "--remote=false"])
            
            # Extract client version
            if "client version:" in output.lower():
                version_line = [line for line in output.split("\n") if "client version:" in line.lower()][0]
                return version_line.split("client version:")[1].strip()
            else:
                return output.strip()
        
        except Exception as e:
            logger.error(f"Failed to get Istio version: {str(e)}")
            return "unknown"
    
    def enable_for_namespace(self, namespace: str) -> Dict[str, Any]:
        """
        Enable Istio for a namespace.
        
        Args:
            namespace: Namespace name
            
        Returns:
            Dict[str, Any]: Namespace labeling result
        """
        try:
            # Label namespace for Istio injection
            output = self.kubernetes_adapter.run_command([
                "label", "namespace", namespace, "istio-injection=enabled", "--overwrite"
            ])
            
            return {
                "status": "enabled",
                "namespace": namespace,
                "output": output
            }
        
        except Exception as e:
            logger.error(f"Failed to enable Istio for namespace: {str(e)}")
            return {"error": str(e)}
    
    def create_virtual_service(self, name: str, namespace: str, 
                              hosts: List[str], gateways: List[str], 
                              http_routes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create an Istio virtual service.
        
        Args:
            name: Virtual service name
            namespace: Namespace
            hosts: List of hosts
            gateways: List of gateways
            http_routes: List of HTTP routes
            
        Returns:
            Dict[str, Any]: Virtual service creation result
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
        
        return self.kubernetes_adapter.apply_manifest(virtual_service, namespace)
    
    def create_gateway(self, name: str, namespace: str, 
                      selector: Dict[str, str], servers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create an Istio gateway.
        
        Args:
            name: Gateway name
            namespace: Namespace
            selector: Gateway selector
            servers: List of servers
            
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
        
        return self.kubernetes_adapter.apply_manifest(gateway, namespace)
    
    def get_status(self, name: str, namespace: str) -> Dict[str, Any]:
        """
        Get the status of Istio resources for an application.
        
        Args:
            name: Application name
            namespace: Namespace
            
        Returns:
            Dict[str, Any]: Istio status
        """
        try:
            # Get virtual services
            vs_output = self.kubernetes_adapter.run_command([
                "get", "virtualservice", "-l", f"app={name}", "-n", namespace, "-o", "json"
            ])
            vs_json = json.loads(vs_output)
            
            # Get gateways
            gw_output = self.kubernetes_adapter.run_command([
                "get", "gateway", "-l", f"app={name}", "-n", namespace, "-o", "json"
            ])
            gw_json = json.loads(gw_output)
            
            # Get destination rules
            dr_output = self.kubernetes_adapter.run_command([
                "get", "destinationrule", "-l", f"app={name}", "-n", namespace, "-o", "json"
            ])
            dr_json = json.loads(dr_output)
            
            return {
                "virtual_services": vs_json.get("items", []),
                "gateways": gw_json.get("items", []),
                "destination_rules": dr_json.get("items", [])
            }
        
        except Exception as e:
            logger.error(f"Failed to get Istio status: {str(e)}")
            return {"error": str(e)}
    
    def delete_resources(self, name: str, namespace: str) -> Dict[str, Any]:
        """
        Delete Istio resources for an application.
        
        Args:
            name: Application name
            namespace: Namespace
            
        Returns:
            Dict[str, Any]: Resource deletion result
        """
        try:
            # Delete virtual services
            vs_output = self.kubernetes_adapter.run_command([
                "delete", "virtualservice", "-l", f"app={name}", "-n", namespace
            ], check=False)
            
            # Delete gateways
            gw_output = self.kubernetes_adapter.run_command([
                "delete", "gateway", "-l", f"app={name}", "-n", namespace
            ], check=False)
            
            # Delete destination rules
            dr_output = self.kubernetes_adapter.run_command([
                "delete", "destinationrule", "-l", f"app={name}", "-n", namespace
            ], check=False)
            
            return {
                "status": "deleted",
                "name": name,
                "namespace": namespace,
                "virtual_services": vs_output,
                "gateways": gw_output,
                "destination_rules": dr_output
            }
        
        except Exception as e:
            logger.error(f"Failed to delete Istio resources: {str(e)}")
            return {"error": str(e)}
    
    def get_cluster_info(self) -> Dict[str, Any]:
        """
        Get information about Istio in the cluster.
        
        Returns:
            Dict[str, Any]: Istio information
        """
        try:
            # Get Istio version
            version = self.get_version()
            
            # Get Istio status
            status_output = self.run_command(["proxy-status"], check=False)
            
            # Get Istio config status
            config_output = self.run_command(["analyze", "--all-namespaces"], check=False)
            
            return {
                "version": version,
                "proxy_status": status_output,
                "config_status": config_output
            }
        
        except Exception as e:
            logger.error(f"Failed to get Istio cluster information: {str(e)}")
            return {"error": str(e)}


class KnativeAdapter:
    """
    Adapts to Knative serverless platform.
    
    This class provides methods for interacting with Knative,
    handling serverless deployments and services.
    """
    
    def __init__(self, kubernetes_adapter: KubernetesAdapter, kn_binary: str = "kn"):
        """
        Initialize the Knative Adapter.
        
        Args:
            kubernetes_adapter: Kubernetes adapter
            kn_binary: Path to kn binary (default: "kn")
        """
        self.kubernetes_adapter = kubernetes_adapter
        self.kn_binary = kn_binary
    
    def run_command(self, args: List[str], check: bool = True) -> str:
        """
        Run a kn command.
        
        Args:
            args: Command arguments
            check: Whether to check for command success
            
        Returns:
            str: Command output
            
        Raises:
            Exception: If the command fails and check is True
        """
        cmd = [self.kn_binary] + args
        logger.info(f"Running kn command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=check
            )
            
            return result.stdout
        
        except subprocess.CalledProcessError as e:
            error_message = f"kn command failed: {e.stderr}"
            logger.error(error_message)
            
            if check:
                raise Exception(error_message)
            
            return e.stderr
    
    def get_version(self) -> str:
        """
        Get the Knative version.
        
        Returns:
            str: Knative version
        """
        try:
            output = self.run_command(["version"])
            
            # Extract client version
            if "client version:" in output.lower():
                version_line = [line for line in output.split("\n") if "client version:" in line.lower()][0]
                return version_line.split("client version:")[1].strip()
            else:
                return output.strip()
        
        except Exception as e:
            logger.error(f"Failed to get Knative version: {str(e)}")
            return "unknown"
    
    def adapt_manifests(self, manifests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Adapt Kubernetes manifests for Knative.
        
        Args:
            manifests: List of Kubernetes manifests
            
        Returns:
            List[Dict[str, Any]]: Adapted manifests
        """
        adapted_manifests = []
        
        for manifest in manifests:
            kind = manifest.get("kind")
            
            if kind == "Deployment":
                # Convert Deployment to Knative Service
                knative_service = self._convert_to_knative_service(manifest)
                adapted_manifests.append(knative_service)
            elif kind == "Service":
                # Skip regular Kubernetes Service as Knative Service includes it
                continue
            else:
                # Keep other manifests as is
                adapted_manifests.append(manifest)
        
        return adapted_manifests
    
    def _convert_to_knative_service(self, deployment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert a Kubernetes Deployment to a Knative Service.
        
        Args:
            deployment: Kubernetes Deployment manifest
            
        Returns:
            Dict[str, Any]: Knative Service manifest
        """
        metadata = deployment.get("metadata", {})
        spec = deployment.get("spec", {})
        template = spec.get("template", {})
        template_spec = template.get("spec", {})
        containers = template_spec.get("containers", [])
        
        knative_service = {
            "apiVersion": "serving.knative.dev/v1",
            "kind": "Service",
            "metadata": {
                "name": metadata.get("name"),
                "namespace": metadata.get("namespace"),
                "labels": metadata.get("labels", {})
            },
            "spec": {
                "template": {
                    "metadata": template.get("metadata", {}),
                    "spec": {
                        "containers": containers
                    }
                }
            }
        }
        
        return knative_service
    
    def create_service(self, name: str, namespace: str, image: str, 
                      env: Optional[List[Dict[str, str]]] = None,
                      min_scale: Optional[int] = None,
                      max_scale: Optional[int] = None) -> Dict[str, Any]:
        """
        Create a Knative service.
        
        Args:
            name: Service name
            namespace: Namespace
            image: Container image
            env: Environment variables (optional)
            min_scale: Minimum scale (optional)
            max_scale: Maximum scale (optional)
            
        Returns:
            Dict[str, Any]: Service creation result
        """
        service = {
            "apiVersion": "serving.knative.dev/v1",
            "kind": "Service",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "template": {
                    "metadata": {
                        "annotations": {}
                    },
                    "spec": {
                        "containers": [
                            {
                                "image": image
                            }
                        ]
                    }
                }
            }
        }
        
        # Add environment variables if provided
        if env:
            service["spec"]["template"]["spec"]["containers"][0]["env"] = env
        
        # Add scaling annotations if provided
        if min_scale is not None:
            service["spec"]["template"]["metadata"]["annotations"]["autoscaling.knative.dev/minScale"] = str(min_scale)
        
        if max_scale is not None:
            service["spec"]["template"]["metadata"]["annotations"]["autoscaling.knative.dev/maxScale"] = str(max_scale)
        
        return self.kubernetes_adapter.apply_manifest(service, namespace)
    
    def get_status(self, name: str, namespace: str) -> Dict[str, Any]:
        """
        Get the status of a Knative service.
        
        Args:
            name: Service name
            namespace: Namespace
            
        Returns:
            Dict[str, Any]: Service status
        """
        try:
            output = self.kubernetes_adapter.run_command([
                "get", "ksvc", name, "-n", namespace, "-o", "json"
            ])
            service = json.loads(output)
            
            return {
                "name": service["metadata"]["name"],
                "namespace": service["metadata"]["namespace"],
                "url": service["status"].get("url"),
                "latest_created_revision": service["status"].get("latestCreatedRevisionName"),
                "latest_ready_revision": service["status"].get("latestReadyRevisionName"),
                "conditions": service["status"].get("conditions", [])
            }
        
        except Exception as e:
            logger.error(f"Failed to get Knative service status: {str(e)}")
            return {"error": str(e)}
    
    def delete_resources(self, name: str, namespace: str) -> Dict[str, Any]:
        """
        Delete Knative resources for an application.
        
        Args:
            name: Application name
            namespace: Namespace
            
        Returns:
            Dict[str, Any]: Resource deletion result
        """
        try:
            # Delete Knative service
            output = self.kubernetes_adapter.run_command([
                "delete", "ksvc", name, "-n", namespace
            ], check=False)
            
            return {
                "status": "deleted",
                "name": name,
                "namespace": namespace,
                "output": output
            }
        
        except Exception as e:
            logger.error(f"Failed to delete Knative resources: {str(e)}")
            return {"error": str(e)}
    
    def get_cluster_info(self) -> Dict[str, Any]:
        """
        Get information about Knative in the cluster.
        
        Returns:
            Dict[str, Any]: Knative information
        """
        try:
            # Get Knative version
            version = self.get_version()
            
            # Get Knative serving status
            serving_output = self.kubernetes_adapter.run_command([
                "get", "knativeserving", "--all-namespaces", "-o", "json"
            ], check=False)
            
            try:
                serving_json = json.loads(serving_output)
                serving_status = serving_json.get("items", [])
            except json.JSONDecodeError:
                serving_status = serving_output
            
            # Get Knative eventing status
            eventing_output = self.kubernetes_adapter.run_command([
                "get", "knativeeventing", "--all-namespaces", "-o", "json"
            ], check=False)
            
            try:
                eventing_json = json.loads(eventing_output)
                eventing_status = eventing_json.get("items", [])
            except json.JSONDecodeError:
                eventing_status = eventing_output
            
            return {
                "version": version,
                "serving": serving_status,
                "eventing": eventing_status
            }
        
        except Exception as e:
            logger.error(f"Failed to get Knative cluster information: {str(e)}")
            return {"error": str(e)}


class PrometheusAdapter:
    """
    Adapts to Prometheus monitoring.
    
    This class provides methods for interacting with Prometheus,
    handling metrics collection and monitoring.
    """
    
    def __init__(self, kubernetes_adapter: KubernetesAdapter):
        """
        Initialize the Prometheus Adapter.
        
        Args:
            kubernetes_adapter: Kubernetes adapter
        """
        self.kubernetes_adapter = kubernetes_adapter
    
    def add_monitoring(self, manifests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Add Prometheus monitoring annotations to manifests.
        
        Args:
            manifests: List of Kubernetes manifests
            
        Returns:
            List[Dict[str, Any]]: Manifests with monitoring annotations
        """
        for manifest in manifests:
            kind = manifest.get("kind")
            
            if kind == "Deployment" or kind == "StatefulSet" or kind == "DaemonSet":
                # Add Prometheus annotations to pod template
                template = manifest.get("spec", {}).get("template", {})
                metadata = template.get("metadata", {})
                annotations = metadata.get("annotations", {})
                
                # Add Prometheus scraping annotations
                annotations["prometheus.io/scrape"] = "true"
                annotations["prometheus.io/path"] = "/metrics"
                annotations["prometheus.io/port"] = "8080"
                
                metadata["annotations"] = annotations
                template["metadata"] = metadata
                manifest["spec"]["template"] = template
            
            elif kind == "Service":
                # Add Prometheus annotations to service
                metadata = manifest.get("metadata", {})
                annotations = metadata.get("annotations", {})
                
                # Add Prometheus scraping annotations
                annotations["prometheus.io/scrape"] = "true"
                annotations["prometheus.io/path"] = "/metrics"
                annotations["prometheus.io/port"] = "8080"
                
                metadata["annotations"] = annotations
                manifest["metadata"] = metadata
        
        return manifests
    
    def create_service_monitor(self, name: str, namespace: str, 
                              selector: Dict[str, str], 
                              endpoints: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a Prometheus ServiceMonitor.
        
        Args:
            name: ServiceMonitor name
            namespace: Namespace
            selector: Label selector
            endpoints: List of endpoints to scrape
            
        Returns:
            Dict[str, Any]: ServiceMonitor creation result
        """
        service_monitor = {
            "apiVersion": "monitoring.coreos.com/v1",
            "kind": "ServiceMonitor",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "selector": {
                    "matchLabels": selector
                },
                "endpoints": endpoints
            }
        }
        
        return self.kubernetes_adapter.apply_manifest(service_monitor, namespace)
    
    def get_metrics(self, name: str, namespace: str) -> Dict[str, Any]:
        """
        Get Prometheus metrics for an application.
        
        Args:
            name: Application name
            namespace: Namespace
            
        Returns:
            Dict[str, Any]: Metrics
        """
        try:
            # Check if Prometheus is available
            prometheus_ns_output = self.kubernetes_adapter.run_command([
                "get", "namespace", "monitoring"
            ], check=False)
            
            if "NotFound" in prometheus_ns_output:
                return {"status": "prometheus_not_installed"}
            
            # Get ServiceMonitors
            sm_output = self.kubernetes_adapter.run_command([
                "get", "servicemonitor", "-l", f"app={name}", "-n", namespace, "-o", "json"
            ], check=False)
            
            try:
                sm_json = json.loads(sm_output)
                service_monitors = sm_json.get("items", [])
            except json.JSONDecodeError:
                service_monitors = []
            
            # Get PrometheusRules
            rule_output = self.kubernetes_adapter.run_command([
                "get", "prometheusrule", "-l", f"app={name}", "-n", namespace, "-o", "json"
            ], check=False)
            
            try:
                rule_json = json.loads(rule_output)
                prometheus_rules = rule_json.get("items", [])
            except json.JSONDecodeError:
                prometheus_rules = []
            
            return {
                "service_monitors": service_monitors,
                "prometheus_rules": prometheus_rules
            }
        
        except Exception as e:
            logger.error(f"Failed to get Prometheus metrics: {str(e)}")
            return {"error": str(e)}
    
    def get_cluster_info(self) -> Dict[str, Any]:
        """
        Get information about Prometheus in the cluster.
        
        Returns:
            Dict[str, Any]: Prometheus information
        """
        try:
            # Check if Prometheus is available
            prometheus_ns_output = self.kubernetes_adapter.run_command([
                "get", "namespace", "monitoring"
            ], check=False)
            
            if "NotFound" in prometheus_ns_output:
                return {"status": "prometheus_not_installed"}
            
            # Get Prometheus instances
            prometheus_output = self.kubernetes_adapter.run_command([
                "get", "prometheus", "--all-namespaces", "-o", "json"
            ], check=False)
            
            try:
                prometheus_json = json.loads(prometheus_output)
                prometheus_instances = prometheus_json.get("items", [])
            except json.JSONDecodeError:
                prometheus_instances = []
            
            # Get Alertmanager instances
            alertmanager_output = self.kubernetes_adapter.run_command([
                "get", "alertmanager", "--all-namespaces", "-o", "json"
            ], check=False)
            
            try:
                alertmanager_json = json.loads(alertmanager_output)
                alertmanager_instances = alertmanager_json.get("items", [])
            except json.JSONDecodeError:
                alertmanager_instances = []
            
            return {
                "prometheus_instances": prometheus_instances,
                "alertmanager_instances": alertmanager_instances
            }
        
        except Exception as e:
            logger.error(f"Failed to get Prometheus cluster information: {str(e)}")
            return {"error": str(e)}
