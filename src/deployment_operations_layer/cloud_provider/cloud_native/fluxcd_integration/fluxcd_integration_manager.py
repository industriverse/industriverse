"""
FluxCD Integration Manager

This module provides integration with FluxCD for GitOps-based continuous delivery
in the Deployment Operations Layer. It handles source management, kustomization,
Helm releases, and notification controllers.

Classes:
    FluxCDIntegrationManager: Manages FluxCD integration
    FluxCDSourceManager: Manages FluxCD sources (GitRepository, HelmRepository)
    FluxCDKustomizationManager: Manages FluxCD kustomizations
    FluxCDHelmReleaseManager: Manages FluxCD Helm releases
    FluxCDExecutor: Executes FluxCD CLI commands
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

class FluxCDIntegrationManager:
    """
    Manages FluxCD integration for the Deployment Operations Layer.
    
    This class provides a unified interface for interacting with FluxCD,
    handling source management, kustomization, Helm releases, and notifications.
    """
    
    def __init__(self, flux_binary_path: Optional[str] = None, 
                working_dir: Optional[str] = None):
        """
        Initialize the FluxCD Integration Manager.
        
        Args:
            flux_binary_path: Path to FluxCD binary (optional, defaults to 'flux' in PATH)
            working_dir: Working directory for FluxCD operations (optional)
        """
        self.flux_binary = flux_binary_path or "flux"
        self.working_dir = working_dir or tempfile.mkdtemp(prefix="fluxcd_")
        
        self.executor = FluxCDExecutor(self.flux_binary, self.working_dir)
        self.source_manager = FluxCDSourceManager(self.executor)
        self.kustomization_manager = FluxCDKustomizationManager(self.executor)
        self.helm_release_manager = FluxCDHelmReleaseManager(self.executor)
        
        # Verify FluxCD installation
        self._verify_fluxcd_installation()
    
    def _verify_fluxcd_installation(self):
        """
        Verify that FluxCD is installed and available.
        
        Logs a warning if FluxCD is not installed but does not raise an exception
        as FluxCD may be accessed via API or other means.
        """
        try:
            version = self.executor.run_command(["--version"], check=False)
            logger.info(f"FluxCD client version: {version}")
        except Exception as e:
            logger.warning(f"FluxCD client not installed or not accessible: {str(e)}")
    
    def bootstrap(self, github_token: str, github_user: str, github_repo: str, 
                 path: str, namespace: str = "flux-system") -> AgentResponse:
        """
        Bootstrap FluxCD on a Kubernetes cluster.
        
        Args:
            github_token: GitHub personal access token
            github_user: GitHub username
            github_repo: GitHub repository name
            path: Path in the repository
            namespace: Namespace to install FluxCD in (default: "flux-system")
            
        Returns:
            AgentResponse: Bootstrap response
        """
        try:
            # Set GitHub token environment variable
            os.environ["GITHUB_TOKEN"] = github_token
            
            args = [
                "bootstrap", "github",
                f"--owner={github_user}",
                f"--repository={github_repo}",
                f"--path={path}",
                f"--namespace={namespace}"
            ]
            
            output = self.executor.run_command(args)
            
            return AgentResponse(
                success=True,
                message=f"FluxCD bootstrapped successfully with GitHub repository {github_user}/{github_repo}",
                data={
                    "github_user": github_user,
                    "github_repo": github_repo,
                    "path": path,
                    "namespace": namespace,
                    "output": output
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to bootstrap FluxCD: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to bootstrap FluxCD: {str(e)}",
                data={}
            )
        
        finally:
            # Clear GitHub token environment variable
            if "GITHUB_TOKEN" in os.environ:
                del os.environ["GITHUB_TOKEN"]
    
    def create_source_git(self, name: str, url: str, branch: str, 
                         namespace: str = "flux-system", 
                         interval: str = "1m") -> AgentResponse:
        """
        Create a FluxCD GitRepository source.
        
        Args:
            name: Source name
            url: Git repository URL
            branch: Git branch
            namespace: Namespace (default: "flux-system")
            interval: Sync interval (default: "1m")
            
        Returns:
            AgentResponse: Source creation response
        """
        try:
            result = self.source_manager.create_git_repository(
                name=name,
                url=url,
                branch=branch,
                namespace=namespace,
                interval=interval
            )
            
            return AgentResponse(
                success=True,
                message=f"FluxCD GitRepository source {name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create FluxCD GitRepository source: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create FluxCD GitRepository source: {str(e)}",
                data={}
            )
    
    def create_source_helm(self, name: str, url: str, 
                          namespace: str = "flux-system", 
                          interval: str = "1m") -> AgentResponse:
        """
        Create a FluxCD HelmRepository source.
        
        Args:
            name: Source name
            url: Helm repository URL
            namespace: Namespace (default: "flux-system")
            interval: Sync interval (default: "1m")
            
        Returns:
            AgentResponse: Source creation response
        """
        try:
            result = self.source_manager.create_helm_repository(
                name=name,
                url=url,
                namespace=namespace,
                interval=interval
            )
            
            return AgentResponse(
                success=True,
                message=f"FluxCD HelmRepository source {name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create FluxCD HelmRepository source: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create FluxCD HelmRepository source: {str(e)}",
                data={}
            )
    
    def create_kustomization(self, name: str, source_name: str, path: str, 
                            namespace: str = "flux-system", 
                            target_namespace: Optional[str] = None,
                            interval: str = "1m",
                            prune: bool = True) -> AgentResponse:
        """
        Create a FluxCD Kustomization.
        
        Args:
            name: Kustomization name
            source_name: Source name
            path: Path in the source
            namespace: Namespace (default: "flux-system")
            target_namespace: Target namespace (optional)
            interval: Sync interval (default: "1m")
            prune: Whether to prune resources (default: True)
            
        Returns:
            AgentResponse: Kustomization creation response
        """
        try:
            result = self.kustomization_manager.create_kustomization(
                name=name,
                source_name=source_name,
                path=path,
                namespace=namespace,
                target_namespace=target_namespace,
                interval=interval,
                prune=prune
            )
            
            return AgentResponse(
                success=True,
                message=f"FluxCD Kustomization {name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create FluxCD Kustomization: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create FluxCD Kustomization: {str(e)}",
                data={}
            )
    
    def create_helm_release(self, name: str, source_name: str, chart: str, 
                           namespace: str = "flux-system", 
                           target_namespace: Optional[str] = None,
                           interval: str = "1m",
                           values: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Create a FluxCD HelmRelease.
        
        Args:
            name: HelmRelease name
            source_name: Source name
            chart: Chart name
            namespace: Namespace (default: "flux-system")
            target_namespace: Target namespace (optional)
            interval: Sync interval (default: "1m")
            values: Helm values (optional)
            
        Returns:
            AgentResponse: HelmRelease creation response
        """
        try:
            result = self.helm_release_manager.create_helm_release(
                name=name,
                source_name=source_name,
                chart=chart,
                namespace=namespace,
                target_namespace=target_namespace,
                interval=interval,
                values=values
            )
            
            return AgentResponse(
                success=True,
                message=f"FluxCD HelmRelease {name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create FluxCD HelmRelease: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create FluxCD HelmRelease: {str(e)}",
                data={}
            )
    
    def reconcile(self, kind: str, name: str, 
                 namespace: str = "flux-system") -> AgentResponse:
        """
        Reconcile a FluxCD resource.
        
        Args:
            kind: Resource kind (e.g., "kustomization", "helmrelease")
            name: Resource name
            namespace: Namespace (default: "flux-system")
            
        Returns:
            AgentResponse: Reconciliation response
        """
        try:
            args = ["reconcile", kind, name, "-n", namespace]
            output = self.executor.run_command(args)
            
            return AgentResponse(
                success=True,
                message=f"FluxCD {kind} {name} reconciled successfully",
                data={
                    "kind": kind,
                    "name": name,
                    "namespace": namespace,
                    "output": output
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to reconcile FluxCD resource: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to reconcile FluxCD resource: {str(e)}",
                data={}
            )
    
    def get_status(self, kind: str, name: str, 
                  namespace: str = "flux-system") -> AgentResponse:
        """
        Get the status of a FluxCD resource.
        
        Args:
            kind: Resource kind (e.g., "kustomization", "helmrelease")
            name: Resource name
            namespace: Namespace (default: "flux-system")
            
        Returns:
            AgentResponse: Status response
        """
        try:
            args = ["get", kind, name, "-n", namespace, "-o", "json"]
            output = self.executor.run_command(args)
            
            try:
                resource_json = json.loads(output)
                
                return AgentResponse(
                    success=True,
                    message=f"Retrieved status for FluxCD {kind} {name}",
                    data=resource_json
                )
            
            except json.JSONDecodeError:
                return AgentResponse(
                    success=True,
                    message=f"Retrieved status for FluxCD {kind} {name}",
                    data={"output": output}
                )
        
        except Exception as e:
            logger.error(f"Failed to get FluxCD resource status: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to get FluxCD resource status: {str(e)}",
                data={}
            )
    
    def delete_resource(self, kind: str, name: str, 
                       namespace: str = "flux-system") -> AgentResponse:
        """
        Delete a FluxCD resource.
        
        Args:
            kind: Resource kind (e.g., "kustomization", "helmrelease")
            name: Resource name
            namespace: Namespace (default: "flux-system")
            
        Returns:
            AgentResponse: Deletion response
        """
        try:
            args = ["delete", kind, name, "-n", namespace]
            output = self.executor.run_command(args)
            
            return AgentResponse(
                success=True,
                message=f"FluxCD {kind} {name} deleted successfully",
                data={
                    "kind": kind,
                    "name": name,
                    "namespace": namespace,
                    "output": output
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to delete FluxCD resource: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to delete FluxCD resource: {str(e)}",
                data={}
            )
    
    def check_cluster(self) -> AgentResponse:
        """
        Check if FluxCD is installed on the cluster.
        
        Returns:
            AgentResponse: Check response
        """
        try:
            args = ["check", "--pre"]
            output = self.executor.run_command(args)
            
            return AgentResponse(
                success=True,
                message="FluxCD cluster check completed",
                data={"output": output}
            )
        
        except Exception as e:
            logger.error(f"Failed to check FluxCD cluster: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to check FluxCD cluster: {str(e)}",
                data={}
            )
    
    def to_mcp_context(self) -> MCPContext:
        """
        Convert FluxCD integration information to MCP context.
        
        Returns:
            MCPContext: MCP context with FluxCD integration information
        """
        return MCPContext(
            context_type="fluxcd_integration",
            fluxcd_version=self._get_fluxcd_version(),
            working_dir=self.working_dir
        )
    
    def _get_fluxcd_version(self) -> str:
        """
        Get the FluxCD version.
        
        Returns:
            str: FluxCD version
        """
        try:
            version_output = self.executor.run_command(["--version"], check=False)
            return version_output.strip()
        except Exception as e:
            logger.error(f"Failed to get FluxCD version: {str(e)}")
            return "unknown"


class FluxCDSourceManager:
    """
    Manages FluxCD sources.
    
    This class provides methods for managing FluxCD sources,
    including GitRepository and HelmRepository resources.
    """
    
    def __init__(self, executor: 'FluxCDExecutor'):
        """
        Initialize the FluxCD Source Manager.
        
        Args:
            executor: FluxCD executor
        """
        self.executor = executor
    
    def create_git_repository(self, name: str, url: str, branch: str, 
                             namespace: str = "flux-system", 
                             interval: str = "1m") -> Dict[str, Any]:
        """
        Create a FluxCD GitRepository source.
        
        Args:
            name: Source name
            url: Git repository URL
            branch: Git branch
            namespace: Namespace (default: "flux-system")
            interval: Sync interval (default: "1m")
            
        Returns:
            Dict[str, Any]: Source creation result
        """
        args = [
            "create", "source", "git", name,
            "--url", url,
            "--branch", branch,
            "--interval", interval,
            "-n", namespace
        ]
        
        output = self.executor.run_command(args)
        
        return {
            "name": name,
            "url": url,
            "branch": branch,
            "namespace": namespace,
            "interval": interval,
            "output": output
        }
    
    def create_helm_repository(self, name: str, url: str, 
                              namespace: str = "flux-system", 
                              interval: str = "1m") -> Dict[str, Any]:
        """
        Create a FluxCD HelmRepository source.
        
        Args:
            name: Source name
            url: Helm repository URL
            namespace: Namespace (default: "flux-system")
            interval: Sync interval (default: "1m")
            
        Returns:
            Dict[str, Any]: Source creation result
        """
        args = [
            "create", "source", "helm", name,
            "--url", url,
            "--interval", interval,
            "-n", namespace
        ]
        
        output = self.executor.run_command(args)
        
        return {
            "name": name,
            "url": url,
            "namespace": namespace,
            "interval": interval,
            "output": output
        }
    
    def list_sources(self, kind: str, 
                    namespace: str = "flux-system") -> List[Dict[str, Any]]:
        """
        List FluxCD sources of a specific kind.
        
        Args:
            kind: Source kind (e.g., "git", "helm")
            namespace: Namespace (default: "flux-system")
            
        Returns:
            List[Dict[str, Any]]: List of sources
        """
        args = ["get", "source", kind, "-n", namespace, "-o", "json"]
        output = self.executor.run_command(args)
        
        try:
            sources_json = json.loads(output)
            
            sources = []
            for source in sources_json.get("items", []):
                source_info = {
                    "name": source["metadata"]["name"],
                    "namespace": source["metadata"]["namespace"],
                    "url": source["spec"].get("url"),
                    "interval": source["spec"].get("interval")
                }
                
                if kind == "git":
                    source_info["branch"] = source["spec"].get("ref", {}).get("branch")
                
                sources.append(source_info)
            
            return sources
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse source list: {str(e)}")
            return []


class FluxCDKustomizationManager:
    """
    Manages FluxCD kustomizations.
    
    This class provides methods for managing FluxCD Kustomization resources.
    """
    
    def __init__(self, executor: 'FluxCDExecutor'):
        """
        Initialize the FluxCD Kustomization Manager.
        
        Args:
            executor: FluxCD executor
        """
        self.executor = executor
    
    def create_kustomization(self, name: str, source_name: str, path: str, 
                            namespace: str = "flux-system", 
                            target_namespace: Optional[str] = None,
                            interval: str = "1m",
                            prune: bool = True) -> Dict[str, Any]:
        """
        Create a FluxCD Kustomization.
        
        Args:
            name: Kustomization name
            source_name: Source name
            path: Path in the source
            namespace: Namespace (default: "flux-system")
            target_namespace: Target namespace (optional)
            interval: Sync interval (default: "1m")
            prune: Whether to prune resources (default: True)
            
        Returns:
            Dict[str, Any]: Kustomization creation result
        """
        args = [
            "create", "kustomization", name,
            "--source", source_name,
            "--path", path,
            "--interval", interval,
            "-n", namespace
        ]
        
        if target_namespace:
            args.extend(["--target-namespace", target_namespace])
        
        if prune:
            args.append("--prune")
        
        output = self.executor.run_command(args)
        
        return {
            "name": name,
            "source_name": source_name,
            "path": path,
            "namespace": namespace,
            "target_namespace": target_namespace,
            "interval": interval,
            "prune": prune,
            "output": output
        }
    
    def list_kustomizations(self, namespace: str = "flux-system") -> List[Dict[str, Any]]:
        """
        List FluxCD Kustomizations.
        
        Args:
            namespace: Namespace (default: "flux-system")
            
        Returns:
            List[Dict[str, Any]]: List of kustomizations
        """
        args = ["get", "kustomization", "-n", namespace, "-o", "json"]
        output = self.executor.run_command(args)
        
        try:
            kustomizations_json = json.loads(output)
            
            kustomizations = []
            for kustomization in kustomizations_json.get("items", []):
                kustomization_info = {
                    "name": kustomization["metadata"]["name"],
                    "namespace": kustomization["metadata"]["namespace"],
                    "source_name": kustomization["spec"].get("sourceRef", {}).get("name"),
                    "path": kustomization["spec"].get("path"),
                    "interval": kustomization["spec"].get("interval"),
                    "prune": kustomization["spec"].get("prune", False)
                }
                
                if "targetNamespace" in kustomization["spec"]:
                    kustomization_info["target_namespace"] = kustomization["spec"]["targetNamespace"]
                
                kustomizations.append(kustomization_info)
            
            return kustomizations
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse kustomization list: {str(e)}")
            return []


class FluxCDHelmReleaseManager:
    """
    Manages FluxCD Helm releases.
    
    This class provides methods for managing FluxCD HelmRelease resources.
    """
    
    def __init__(self, executor: 'FluxCDExecutor'):
        """
        Initialize the FluxCD Helm Release Manager.
        
        Args:
            executor: FluxCD executor
        """
        self.executor = executor
    
    def create_helm_release(self, name: str, source_name: str, chart: str, 
                           namespace: str = "flux-system", 
                           target_namespace: Optional[str] = None,
                           interval: str = "1m",
                           values: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a FluxCD HelmRelease.
        
        Args:
            name: HelmRelease name
            source_name: Source name
            chart: Chart name
            namespace: Namespace (default: "flux-system")
            target_namespace: Target namespace (optional)
            interval: Sync interval (default: "1m")
            values: Helm values (optional)
            
        Returns:
            Dict[str, Any]: HelmRelease creation result
        """
        args = [
            "create", "helmrelease", name,
            "--source", f"HelmRepository/{source_name}",
            "--chart", chart,
            "--interval", interval,
            "-n", namespace
        ]
        
        if target_namespace:
            args.extend(["--target-namespace", target_namespace])
        
        # Create values file if provided
        values_file = None
        if values:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
                yaml.dump(values, f)
                values_file = f.name
            
            args.extend(["--values", values_file])
        
        try:
            output = self.executor.run_command(args)
            
            return {
                "name": name,
                "source_name": source_name,
                "chart": chart,
                "namespace": namespace,
                "target_namespace": target_namespace,
                "interval": interval,
                "values": values,
                "output": output
            }
        
        finally:
            # Clean up values file if created
            if values_file and os.path.exists(values_file):
                os.unlink(values_file)
    
    def list_helm_releases(self, namespace: str = "flux-system") -> List[Dict[str, Any]]:
        """
        List FluxCD HelmReleases.
        
        Args:
            namespace: Namespace (default: "flux-system")
            
        Returns:
            List[Dict[str, Any]]: List of helm releases
        """
        args = ["get", "helmrelease", "-n", namespace, "-o", "json"]
        output = self.executor.run_command(args)
        
        try:
            releases_json = json.loads(output)
            
            releases = []
            for release in releases_json.get("items", []):
                release_info = {
                    "name": release["metadata"]["name"],
                    "namespace": release["metadata"]["namespace"],
                    "source_name": release["spec"].get("chart", {}).get("spec", {}).get("sourceRef", {}).get("name"),
                    "chart": release["spec"].get("chart", {}).get("spec", {}).get("chart"),
                    "interval": release["spec"].get("interval")
                }
                
                if "targetNamespace" in release["spec"]:
                    release_info["target_namespace"] = release["spec"]["targetNamespace"]
                
                releases.append(release_info)
            
            return releases
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse helm release list: {str(e)}")
            return []


class FluxCDExecutor:
    """
    Executes FluxCD CLI commands.
    
    This class provides methods for executing FluxCD CLI commands and handling their output.
    """
    
    def __init__(self, flux_binary: str, working_dir: str):
        """
        Initialize the FluxCD Executor.
        
        Args:
            flux_binary: Path to FluxCD binary
            working_dir: Working directory for FluxCD operations
        """
        self.flux_binary = flux_binary
        self.working_dir = working_dir
    
    def run_command(self, args: List[str], check: bool = True) -> str:
        """
        Run a FluxCD command.
        
        Args:
            args: Command arguments
            check: Whether to check for command success
            
        Returns:
            str: Command output
            
        Raises:
            Exception: If the command fails and check is True
        """
        cmd = [self.flux_binary] + args
        logger.info(f"Running FluxCD command: {' '.join(cmd)}")
        
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
            error_message = f"FluxCD command failed: {e.stderr}"
            logger.error(error_message)
            
            if check:
                raise Exception(error_message)
            
            return e.stderr
