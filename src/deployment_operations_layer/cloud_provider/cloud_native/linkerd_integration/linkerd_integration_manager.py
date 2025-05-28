"""
Linkerd Integration Manager

This module provides integration with Linkerd service mesh for the Deployment Operations Layer.
It handles service mesh installation, configuration, traffic management, and observability.

Classes:
    LinkerdIntegrationManager: Manages Linkerd integration
    LinkerdTrafficManager: Manages Linkerd traffic routing
    LinkerdObservabilityManager: Manages Linkerd observability
    LinkerdExecutor: Executes Linkerd CLI commands
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

class LinkerdIntegrationManager:
    """
    Manages Linkerd integration for the Deployment Operations Layer.
    
    This class provides a unified interface for interacting with Linkerd,
    handling service mesh installation, configuration, traffic management, and observability.
    """
    
    def __init__(self, linkerd_binary_path: Optional[str] = None, 
                kubectl_binary_path: Optional[str] = None,
                working_dir: Optional[str] = None):
        """
        Initialize the Linkerd Integration Manager.
        
        Args:
            linkerd_binary_path: Path to linkerd binary (optional, defaults to 'linkerd' in PATH)
            kubectl_binary_path: Path to kubectl binary (optional, defaults to 'kubectl' in PATH)
            working_dir: Working directory for Linkerd operations (optional)
        """
        self.linkerd_binary = linkerd_binary_path or "linkerd"
        self.kubectl_binary = kubectl_binary_path or "kubectl"
        self.working_dir = working_dir or tempfile.mkdtemp(prefix="linkerd_")
        
        self.executor = LinkerdExecutor(self.linkerd_binary, self.kubectl_binary, self.working_dir)
        self.traffic_manager = LinkerdTrafficManager(self.executor)
        self.observability_manager = LinkerdObservabilityManager(self.executor)
        
        # Verify Linkerd installation
        self._verify_linkerd_installation()
    
    def _verify_linkerd_installation(self):
        """
        Verify that Linkerd is installed and available.
        
        Logs a warning if Linkerd is not installed but does not raise an exception
        as Linkerd may be accessed via API or other means.
        """
        try:
            version = self.executor.run_linkerd_command(["version"], check=False)
            logger.info(f"Linkerd client version: {version}")
        except Exception as e:
            logger.warning(f"Linkerd client not installed or not accessible: {str(e)}")
    
    def check_prerequisites(self) -> AgentResponse:
        """
        Check if the prerequisites for Linkerd installation are met.
        
        Returns:
            AgentResponse: Prerequisites check response
        """
        try:
            output = self.executor.run_linkerd_command(["check", "--pre"])
            
            success = "All checks passed" in output
            
            return AgentResponse(
                success=success,
                message="Linkerd prerequisites check completed",
                data={"output": output, "all_checks_passed": success}
            )
        
        except Exception as e:
            logger.error(f"Failed to check Linkerd prerequisites: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to check Linkerd prerequisites: {str(e)}",
                data={}
            )
    
    def install_linkerd(self, ha: bool = False, 
                       enable_ha_components: Optional[List[str]] = None) -> AgentResponse:
        """
        Install Linkerd on a Kubernetes cluster.
        
        Args:
            ha: Whether to install in high-availability mode (default: False)
            enable_ha_components: List of components to enable HA for (optional)
            
        Returns:
            AgentResponse: Installation response
        """
        try:
            args = ["install"]
            
            if ha:
                args.append("--ha")
            
            if enable_ha_components:
                for component in enable_ha_components:
                    args.extend(["--ha-control-plane-replicas", component])
            
            # Generate installation YAML
            install_yaml = self.executor.run_linkerd_command(args)
            
            # Apply installation YAML
            with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
                f.write(install_yaml)
                install_file = f.name
            
            try:
                output = self.executor.run_kubectl_command([
                    "apply", "-f", install_file
                ])
                
                # Check installation
                check_output = self.executor.run_linkerd_command(["check"])
                
                return AgentResponse(
                    success=True,
                    message="Linkerd installed successfully",
                    data={
                        "ha": ha,
                        "enable_ha_components": enable_ha_components,
                        "output": output,
                        "check_output": check_output
                    }
                )
            
            finally:
                # Clean up temporary file
                if os.path.exists(install_file):
                    os.unlink(install_file)
        
        except Exception as e:
            logger.error(f"Failed to install Linkerd: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to install Linkerd: {str(e)}",
                data={}
            )
    
    def install_viz(self) -> AgentResponse:
        """
        Install Linkerd Viz extension.
        
        Returns:
            AgentResponse: Installation response
        """
        try:
            # Generate Viz installation YAML
            viz_yaml = self.executor.run_linkerd_command(["viz", "install"])
            
            # Apply Viz installation YAML
            with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
                f.write(viz_yaml)
                viz_file = f.name
            
            try:
                output = self.executor.run_kubectl_command([
                    "apply", "-f", viz_file
                ])
                
                # Check Viz installation
                check_output = self.executor.run_linkerd_command(["viz", "check"])
                
                return AgentResponse(
                    success=True,
                    message="Linkerd Viz installed successfully",
                    data={
                        "output": output,
                        "check_output": check_output
                    }
                )
            
            finally:
                # Clean up temporary file
                if os.path.exists(viz_file):
                    os.unlink(viz_file)
        
        except Exception as e:
            logger.error(f"Failed to install Linkerd Viz: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to install Linkerd Viz: {str(e)}",
                data={}
            )
    
    def inject_namespace(self, namespace: str) -> AgentResponse:
        """
        Inject Linkerd proxy into all deployments in a namespace.
        
        Args:
            namespace: Namespace to inject
            
        Returns:
            AgentResponse: Injection response
        """
        try:
            # Get all deployments in namespace
            deployments_output = self.executor.run_kubectl_command([
                "get", "deployments", "-n", namespace, "-o", "json"
            ])
            
            deployments_json = json.loads(deployments_output)
            deployment_names = [item["metadata"]["name"] for item in deployments_json.get("items", [])]
            
            results = []
            
            for deployment in deployment_names:
                # Get deployment YAML
                deployment_yaml = self.executor.run_kubectl_command([
                    "get", "deployment", deployment, "-n", namespace, "-o", "yaml"
                ])
                
                # Inject Linkerd proxy
                with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
                    f.write(deployment_yaml)
                    deployment_file = f.name
                
                try:
                    injected_yaml = self.executor.run_linkerd_command([
                        "inject", deployment_file
                    ])
                    
                    # Apply injected YAML
                    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f2:
                        f2.write(injected_yaml)
                        injected_file = f2.name
                    
                    try:
                        output = self.executor.run_kubectl_command([
                            "apply", "-f", injected_file
                        ])
                        
                        results.append({
                            "deployment": deployment,
                            "success": True,
                            "output": output
                        })
                    
                    finally:
                        # Clean up temporary file
                        if os.path.exists(injected_file):
                            os.unlink(injected_file)
                
                finally:
                    # Clean up temporary file
                    if os.path.exists(deployment_file):
                        os.unlink(deployment_file)
            
            return AgentResponse(
                success=True,
                message=f"Linkerd proxy injected into {len(results)} deployments in namespace {namespace}",
                data={
                    "namespace": namespace,
                    "deployments": deployment_names,
                    "results": results
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to inject Linkerd proxy: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to inject Linkerd proxy: {str(e)}",
                data={}
            )
    
    def create_service_profile(self, name: str, namespace: str, 
                              routes: List[Dict[str, Any]]) -> AgentResponse:
        """
        Create a Linkerd ServiceProfile.
        
        Args:
            name: Service name
            namespace: Namespace
            routes: List of routes
            
        Returns:
            AgentResponse: ServiceProfile creation response
        """
        try:
            result = self.traffic_manager.create_service_profile(
                name=name,
                namespace=namespace,
                routes=routes
            )
            
            return AgentResponse(
                success=True,
                message=f"Linkerd ServiceProfile {name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create Linkerd ServiceProfile: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create Linkerd ServiceProfile: {str(e)}",
                data={}
            )
    
    def get_metrics(self, resource_type: str, resource_name: str, 
                   namespace: str) -> AgentResponse:
        """
        Get metrics for a resource.
        
        Args:
            resource_type: Resource type (e.g., "deployment", "pod")
            resource_name: Resource name
            namespace: Namespace
            
        Returns:
            AgentResponse: Metrics response
        """
        try:
            result = self.observability_manager.get_metrics(
                resource_type=resource_type,
                resource_name=resource_name,
                namespace=namespace
            )
            
            return AgentResponse(
                success=True,
                message=f"Retrieved metrics for {resource_type}/{resource_name}",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to get metrics: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to get metrics: {str(e)}",
                data={}
            )
    
    def get_tap(self, resource_type: str, resource_name: str, 
               namespace: str, max_rps: int = 100) -> AgentResponse:
        """
        Get tap data for a resource.
        
        Args:
            resource_type: Resource type (e.g., "deployment", "pod")
            resource_name: Resource name
            namespace: Namespace
            max_rps: Maximum requests per second (default: 100)
            
        Returns:
            AgentResponse: Tap response
        """
        try:
            result = self.observability_manager.get_tap(
                resource_type=resource_type,
                resource_name=resource_name,
                namespace=namespace,
                max_rps=max_rps
            )
            
            return AgentResponse(
                success=True,
                message=f"Retrieved tap data for {resource_type}/{resource_name}",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to get tap data: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to get tap data: {str(e)}",
                data={}
            )
    
    def check_status(self) -> AgentResponse:
        """
        Check Linkerd status.
        
        Returns:
            AgentResponse: Status check response
        """
        try:
            output = self.executor.run_linkerd_command(["check"])
            
            success = "All checks passed" in output
            
            return AgentResponse(
                success=success,
                message="Linkerd status check completed",
                data={"output": output, "all_checks_passed": success}
            )
        
        except Exception as e:
            logger.error(f"Failed to check Linkerd status: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to check Linkerd status: {str(e)}",
                data={}
            )
    
    def to_mcp_context(self) -> MCPContext:
        """
        Convert Linkerd integration information to MCP context.
        
        Returns:
            MCPContext: MCP context with Linkerd integration information
        """
        return MCPContext(
            context_type="linkerd_integration",
            linkerd_version=self._get_linkerd_version(),
            working_dir=self.working_dir
        )
    
    def _get_linkerd_version(self) -> str:
        """
        Get the Linkerd version.
        
        Returns:
            str: Linkerd version
        """
        try:
            version_output = self.executor.run_linkerd_command(["version"], check=False)
            return version_output.strip()
        except Exception as e:
            logger.error(f"Failed to get Linkerd version: {str(e)}")
            return "unknown"


class LinkerdTrafficManager:
    """
    Manages Linkerd traffic routing.
    
    This class provides methods for managing Linkerd traffic routing resources,
    including ServiceProfiles and TrafficSplits.
    """
    
    def __init__(self, executor: 'LinkerdExecutor'):
        """
        Initialize the Linkerd Traffic Manager.
        
        Args:
            executor: Linkerd executor
        """
        self.executor = executor
    
    def create_service_profile(self, name: str, namespace: str, 
                              routes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a Linkerd ServiceProfile.
        
        Args:
            name: Service name
            namespace: Namespace
            routes: List of routes
            
        Returns:
            Dict[str, Any]: ServiceProfile creation result
        """
        service_profile = {
            "apiVersion": "linkerd.io/v1alpha2",
            "kind": "ServiceProfile",
            "metadata": {
                "name": f"{name}.{namespace}.svc.cluster.local",
                "namespace": namespace
            },
            "spec": {
                "routes": routes
            }
        }
        
        # Write ServiceProfile to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(service_profile, f)
            sp_file = f.name
        
        try:
            # Apply ServiceProfile
            output = self.executor.run_kubectl_command([
                "apply", "-f", sp_file
            ])
            
            return {
                "name": name,
                "namespace": namespace,
                "routes": routes,
                "output": output
            }
        
        finally:
            # Clean up temporary file
            if os.path.exists(sp_file):
                os.unlink(sp_file)
    
    def create_traffic_split(self, name: str, service: str, 
                           backends: List[Dict[str, Any]], 
                           namespace: str) -> Dict[str, Any]:
        """
        Create a Linkerd TrafficSplit.
        
        Args:
            name: TrafficSplit name
            service: Service name
            backends: List of backends with weights
            namespace: Namespace
            
        Returns:
            Dict[str, Any]: TrafficSplit creation result
        """
        traffic_split = {
            "apiVersion": "split.smi-spec.io/v1alpha1",
            "kind": "TrafficSplit",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "service": service,
                "backends": backends
            }
        }
        
        # Write TrafficSplit to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(traffic_split, f)
            ts_file = f.name
        
        try:
            # Apply TrafficSplit
            output = self.executor.run_kubectl_command([
                "apply", "-f", ts_file
            ])
            
            return {
                "name": name,
                "service": service,
                "backends": backends,
                "namespace": namespace,
                "output": output
            }
        
        finally:
            # Clean up temporary file
            if os.path.exists(ts_file):
                os.unlink(ts_file)
    
    def list_service_profiles(self, namespace: str) -> List[Dict[str, Any]]:
        """
        List Linkerd ServiceProfiles.
        
        Args:
            namespace: Namespace
            
        Returns:
            List[Dict[str, Any]]: List of ServiceProfiles
        """
        output = self.executor.run_kubectl_command([
            "get", "serviceprofiles", "-n", namespace, "-o", "json"
        ])
        
        try:
            profiles_json = json.loads(output)
            
            profiles = []
            for profile in profiles_json.get("items", []):
                profile_info = {
                    "name": profile["metadata"]["name"],
                    "namespace": profile["metadata"]["namespace"],
                    "routes": profile["spec"].get("routes", [])
                }
                profiles.append(profile_info)
            
            return profiles
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse ServiceProfile list: {str(e)}")
            return []
    
    def list_traffic_splits(self, namespace: str) -> List[Dict[str, Any]]:
        """
        List Linkerd TrafficSplits.
        
        Args:
            namespace: Namespace
            
        Returns:
            List[Dict[str, Any]]: List of TrafficSplits
        """
        output = self.executor.run_kubectl_command([
            "get", "trafficsplits", "-n", namespace, "-o", "json"
        ])
        
        try:
            splits_json = json.loads(output)
            
            splits = []
            for split in splits_json.get("items", []):
                split_info = {
                    "name": split["metadata"]["name"],
                    "namespace": split["metadata"]["namespace"],
                    "service": split["spec"].get("service"),
                    "backends": split["spec"].get("backends", [])
                }
                splits.append(split_info)
            
            return splits
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse TrafficSplit list: {str(e)}")
            return []


class LinkerdObservabilityManager:
    """
    Manages Linkerd observability.
    
    This class provides methods for managing Linkerd observability features,
    including metrics and tap.
    """
    
    def __init__(self, executor: 'LinkerdExecutor'):
        """
        Initialize the Linkerd Observability Manager.
        
        Args:
            executor: Linkerd executor
        """
        self.executor = executor
    
    def get_metrics(self, resource_type: str, resource_name: str, 
                   namespace: str) -> Dict[str, Any]:
        """
        Get metrics for a resource.
        
        Args:
            resource_type: Resource type (e.g., "deployment", "pod")
            resource_name: Resource name
            namespace: Namespace
            
        Returns:
            Dict[str, Any]: Resource metrics
        """
        output = self.executor.run_linkerd_command([
            "stat", f"{resource_type}/{resource_name}", "-n", namespace, "-o", "json"
        ])
        
        try:
            metrics_json = json.loads(output)
            
            return {
                "resource_type": resource_type,
                "resource_name": resource_name,
                "namespace": namespace,
                "metrics": metrics_json
            }
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse metrics: {str(e)}")
            return {
                "resource_type": resource_type,
                "resource_name": resource_name,
                "namespace": namespace,
                "error": str(e),
                "output": output
            }
    
    def get_tap(self, resource_type: str, resource_name: str, 
               namespace: str, max_rps: int = 100) -> Dict[str, Any]:
        """
        Get tap data for a resource.
        
        Args:
            resource_type: Resource type (e.g., "deployment", "pod")
            resource_name: Resource name
            namespace: Namespace
            max_rps: Maximum requests per second (default: 100)
            
        Returns:
            Dict[str, Any]: Resource tap data
        """
        output = self.executor.run_linkerd_command([
            "tap", f"{resource_type}/{resource_name}", "-n", namespace, 
            "--max-rps", str(max_rps), "-o", "json"
        ], timeout=5)  # Limit to 5 seconds
        
        try:
            # Parse JSON lines
            tap_data = []
            for line in output.strip().split("\n"):
                if line:
                    tap_data.append(json.loads(line))
            
            return {
                "resource_type": resource_type,
                "resource_name": resource_name,
                "namespace": namespace,
                "tap_data": tap_data
            }
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse tap data: {str(e)}")
            return {
                "resource_type": resource_type,
                "resource_name": resource_name,
                "namespace": namespace,
                "error": str(e),
                "output": output
            }
    
    def get_routes(self, service_name: str, namespace: str) -> Dict[str, Any]:
        """
        Get routes for a service.
        
        Args:
            service_name: Service name
            namespace: Namespace
            
        Returns:
            Dict[str, Any]: Service routes
        """
        output = self.executor.run_linkerd_command([
            "routes", "service", service_name, "-n", namespace, "-o", "json"
        ])
        
        try:
            routes_json = json.loads(output)
            
            return {
                "service_name": service_name,
                "namespace": namespace,
                "routes": routes_json
            }
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse routes: {str(e)}")
            return {
                "service_name": service_name,
                "namespace": namespace,
                "error": str(e),
                "output": output
            }
    
    def get_edges(self, namespace: str) -> Dict[str, Any]:
        """
        Get service mesh edges for a namespace.
        
        Args:
            namespace: Namespace
            
        Returns:
            Dict[str, Any]: Service mesh edges
        """
        output = self.executor.run_linkerd_command([
            "edges", "-n", namespace, "-o", "json"
        ])
        
        try:
            edges_json = json.loads(output)
            
            return {
                "namespace": namespace,
                "edges": edges_json
            }
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse edges: {str(e)}")
            return {
                "namespace": namespace,
                "error": str(e),
                "output": output
            }


class LinkerdExecutor:
    """
    Executes Linkerd CLI commands.
    
    This class provides methods for executing Linkerd CLI and kubectl commands
    and handling their output.
    """
    
    def __init__(self, linkerd_binary: str, kubectl_binary: str, working_dir: str):
        """
        Initialize the Linkerd Executor.
        
        Args:
            linkerd_binary: Path to Linkerd CLI binary
            kubectl_binary: Path to kubectl binary
            working_dir: Working directory for Linkerd operations
        """
        self.linkerd_binary = linkerd_binary
        self.kubectl_binary = kubectl_binary
        self.working_dir = working_dir
    
    def run_linkerd_command(self, args: List[str], check: bool = True, 
                           timeout: Optional[int] = None) -> str:
        """
        Run a Linkerd CLI command.
        
        Args:
            args: Command arguments
            check: Whether to check for command success
            timeout: Command timeout in seconds (optional)
            
        Returns:
            str: Command output
            
        Raises:
            Exception: If the command fails and check is True
        """
        cmd = [self.linkerd_binary] + args
        logger.info(f"Running Linkerd command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                check=check,
                timeout=timeout
            )
            
            return result.stdout
        
        except subprocess.CalledProcessError as e:
            error_message = f"Linkerd command failed: {e.stderr}"
            logger.error(error_message)
            
            if check:
                raise Exception(error_message)
            
            return e.stderr
        
        except subprocess.TimeoutExpired as e:
            error_message = f"Linkerd command timed out after {timeout} seconds"
            logger.error(error_message)
            
            if check:
                raise Exception(error_message)
            
            return e.stdout or ""
    
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
