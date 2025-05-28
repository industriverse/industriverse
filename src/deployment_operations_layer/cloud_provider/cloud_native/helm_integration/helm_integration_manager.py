"""
Helm Integration Manager

This module provides integration with Helm for the Deployment Operations Layer.
It handles Helm chart management, installation, upgrades, and rollbacks.

Classes:
    HelmIntegrationManager: Manages Helm integration
    HelmChartManager: Manages Helm charts
    HelmReleaseManager: Manages Helm releases
    HelmRepositoryManager: Manages Helm repositories
    HelmExecutor: Executes Helm CLI commands
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

class HelmIntegrationManager:
    """
    Manages Helm integration for the Deployment Operations Layer.
    
    This class provides a unified interface for interacting with Helm,
    handling chart management, installation, upgrades, and rollbacks.
    """
    
    def __init__(self, helm_binary_path: Optional[str] = None, 
                kubectl_binary_path: Optional[str] = None,
                working_dir: Optional[str] = None):
        """
        Initialize the Helm Integration Manager.
        
        Args:
            helm_binary_path: Path to helm binary (optional, defaults to 'helm' in PATH)
            kubectl_binary_path: Path to kubectl binary (optional, defaults to 'kubectl' in PATH)
            working_dir: Working directory for Helm operations (optional)
        """
        self.helm_binary = helm_binary_path or "helm"
        self.kubectl_binary = kubectl_binary_path or "kubectl"
        self.working_dir = working_dir or tempfile.mkdtemp(prefix="helm_")
        
        self.executor = HelmExecutor(self.helm_binary, self.kubectl_binary, self.working_dir)
        self.chart_manager = HelmChartManager(self.executor)
        self.release_manager = HelmReleaseManager(self.executor)
        self.repository_manager = HelmRepositoryManager(self.executor)
        
        # Verify Helm installation
        self._verify_helm_installation()
    
    def _verify_helm_installation(self):
        """
        Verify that Helm is installed and available.
        
        Logs a warning if Helm is not installed but does not raise an exception
        as Helm may be accessed via API or other means.
        """
        try:
            version = self.executor.run_helm_command(["version"], check=False)
            logger.info(f"Helm client version: {version}")
        except Exception as e:
            logger.warning(f"Helm client not installed or not accessible: {str(e)}")
    
    def add_repository(self, name: str, url: str) -> AgentResponse:
        """
        Add a Helm repository.
        
        Args:
            name: Repository name
            url: Repository URL
            
        Returns:
            AgentResponse: Repository addition response
        """
        try:
            result = self.repository_manager.add_repository(
                name=name,
                url=url
            )
            
            return AgentResponse(
                success=True,
                message=f"Helm repository {name} added successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to add Helm repository: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to add Helm repository: {str(e)}",
                data={}
            )
    
    def update_repositories(self) -> AgentResponse:
        """
        Update Helm repositories.
        
        Returns:
            AgentResponse: Repository update response
        """
        try:
            result = self.repository_manager.update_repositories()
            
            return AgentResponse(
                success=True,
                message="Helm repositories updated successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to update Helm repositories: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to update Helm repositories: {str(e)}",
                data={}
            )
    
    def install_chart(self, release_name: str, chart: str, 
                     namespace: str = "default",
                     values: Optional[Dict[str, Any]] = None,
                     set_values: Optional[Dict[str, str]] = None,
                     version: Optional[str] = None,
                     wait: bool = False,
                     timeout: Optional[str] = None) -> AgentResponse:
        """
        Install a Helm chart.
        
        Args:
            release_name: Release name
            chart: Chart name or path
            namespace: Namespace (default: "default")
            values: Values to override (optional)
            set_values: Values to set on command line (optional)
            version: Chart version (optional)
            wait: Whether to wait for resources to be ready (default: False)
            timeout: Timeout for wait (optional)
            
        Returns:
            AgentResponse: Chart installation response
        """
        try:
            result = self.release_manager.install_chart(
                release_name=release_name,
                chart=chart,
                namespace=namespace,
                values=values,
                set_values=set_values,
                version=version,
                wait=wait,
                timeout=timeout
            )
            
            return AgentResponse(
                success=True,
                message=f"Helm chart {chart} installed successfully as {release_name}",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to install Helm chart: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to install Helm chart: {str(e)}",
                data={}
            )
    
    def upgrade_release(self, release_name: str, chart: str, 
                       namespace: str = "default",
                       values: Optional[Dict[str, Any]] = None,
                       set_values: Optional[Dict[str, str]] = None,
                       version: Optional[str] = None,
                       wait: bool = False,
                       timeout: Optional[str] = None) -> AgentResponse:
        """
        Upgrade a Helm release.
        
        Args:
            release_name: Release name
            chart: Chart name or path
            namespace: Namespace (default: "default")
            values: Values to override (optional)
            set_values: Values to set on command line (optional)
            version: Chart version (optional)
            wait: Whether to wait for resources to be ready (default: False)
            timeout: Timeout for wait (optional)
            
        Returns:
            AgentResponse: Release upgrade response
        """
        try:
            result = self.release_manager.upgrade_release(
                release_name=release_name,
                chart=chart,
                namespace=namespace,
                values=values,
                set_values=set_values,
                version=version,
                wait=wait,
                timeout=timeout
            )
            
            return AgentResponse(
                success=True,
                message=f"Helm release {release_name} upgraded successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to upgrade Helm release: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to upgrade Helm release: {str(e)}",
                data={}
            )
    
    def rollback_release(self, release_name: str, 
                        revision: Optional[int] = None,
                        namespace: str = "default",
                        wait: bool = False,
                        timeout: Optional[str] = None) -> AgentResponse:
        """
        Rollback a Helm release.
        
        Args:
            release_name: Release name
            revision: Revision to rollback to (optional, defaults to previous revision)
            namespace: Namespace (default: "default")
            wait: Whether to wait for resources to be ready (default: False)
            timeout: Timeout for wait (optional)
            
        Returns:
            AgentResponse: Release rollback response
        """
        try:
            result = self.release_manager.rollback_release(
                release_name=release_name,
                revision=revision,
                namespace=namespace,
                wait=wait,
                timeout=timeout
            )
            
            return AgentResponse(
                success=True,
                message=f"Helm release {release_name} rolled back successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to rollback Helm release: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to rollback Helm release: {str(e)}",
                data={}
            )
    
    def uninstall_release(self, release_name: str, 
                         namespace: str = "default",
                         keep_history: bool = False) -> AgentResponse:
        """
        Uninstall a Helm release.
        
        Args:
            release_name: Release name
            namespace: Namespace (default: "default")
            keep_history: Whether to keep release history (default: False)
            
        Returns:
            AgentResponse: Release uninstallation response
        """
        try:
            result = self.release_manager.uninstall_release(
                release_name=release_name,
                namespace=namespace,
                keep_history=keep_history
            )
            
            return AgentResponse(
                success=True,
                message=f"Helm release {release_name} uninstalled successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to uninstall Helm release: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to uninstall Helm release: {str(e)}",
                data={}
            )
    
    def list_releases(self, namespace: Optional[str] = None, 
                     all_namespaces: bool = False) -> AgentResponse:
        """
        List Helm releases.
        
        Args:
            namespace: Namespace (optional)
            all_namespaces: Whether to list releases in all namespaces (default: False)
            
        Returns:
            AgentResponse: Release list response
        """
        try:
            result = self.release_manager.list_releases(
                namespace=namespace,
                all_namespaces=all_namespaces
            )
            
            return AgentResponse(
                success=True,
                message=f"Found {len(result)} Helm releases",
                data={"releases": result}
            )
        
        except Exception as e:
            logger.error(f"Failed to list Helm releases: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to list Helm releases: {str(e)}",
                data={}
            )
    
    def get_release_status(self, release_name: str, 
                          namespace: str = "default") -> AgentResponse:
        """
        Get status of a Helm release.
        
        Args:
            release_name: Release name
            namespace: Namespace (default: "default")
            
        Returns:
            AgentResponse: Release status response
        """
        try:
            result = self.release_manager.get_release_status(
                release_name=release_name,
                namespace=namespace
            )
            
            return AgentResponse(
                success=True,
                message=f"Retrieved status for Helm release {release_name}",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to get Helm release status: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to get Helm release status: {str(e)}",
                data={}
            )
    
    def get_release_values(self, release_name: str, 
                          namespace: str = "default",
                          all_values: bool = False) -> AgentResponse:
        """
        Get values of a Helm release.
        
        Args:
            release_name: Release name
            namespace: Namespace (default: "default")
            all_values: Whether to get all values (default: False)
            
        Returns:
            AgentResponse: Release values response
        """
        try:
            result = self.release_manager.get_release_values(
                release_name=release_name,
                namespace=namespace,
                all_values=all_values
            )
            
            return AgentResponse(
                success=True,
                message=f"Retrieved values for Helm release {release_name}",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to get Helm release values: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to get Helm release values: {str(e)}",
                data={}
            )
    
    def create_chart(self, chart_name: str, 
                    destination_dir: Optional[str] = None) -> AgentResponse:
        """
        Create a new Helm chart.
        
        Args:
            chart_name: Chart name
            destination_dir: Destination directory (optional)
            
        Returns:
            AgentResponse: Chart creation response
        """
        try:
            result = self.chart_manager.create_chart(
                chart_name=chart_name,
                destination_dir=destination_dir or self.working_dir
            )
            
            return AgentResponse(
                success=True,
                message=f"Helm chart {chart_name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create Helm chart: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create Helm chart: {str(e)}",
                data={}
            )
    
    def package_chart(self, chart_path: str, 
                     destination_dir: Optional[str] = None,
                     version: Optional[str] = None,
                     app_version: Optional[str] = None) -> AgentResponse:
        """
        Package a Helm chart.
        
        Args:
            chart_path: Path to chart
            destination_dir: Destination directory (optional)
            version: Chart version (optional)
            app_version: App version (optional)
            
        Returns:
            AgentResponse: Chart packaging response
        """
        try:
            result = self.chart_manager.package_chart(
                chart_path=chart_path,
                destination_dir=destination_dir,
                version=version,
                app_version=app_version
            )
            
            return AgentResponse(
                success=True,
                message=f"Helm chart {chart_path} packaged successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to package Helm chart: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to package Helm chart: {str(e)}",
                data={}
            )
    
    def to_mcp_context(self) -> MCPContext:
        """
        Convert Helm integration information to MCP context.
        
        Returns:
            MCPContext: MCP context with Helm integration information
        """
        return MCPContext(
            context_type="helm_integration",
            helm_version=self._get_helm_version(),
            working_dir=self.working_dir
        )
    
    def _get_helm_version(self) -> str:
        """
        Get the Helm version.
        
        Returns:
            str: Helm version
        """
        try:
            version_output = self.executor.run_helm_command(["version", "--short"], check=False)
            return version_output.strip()
        except Exception as e:
            logger.error(f"Failed to get Helm version: {str(e)}")
            return "unknown"


class HelmChartManager:
    """
    Manages Helm charts.
    
    This class provides methods for managing Helm charts,
    including creation, packaging, and linting.
    """
    
    def __init__(self, executor: 'HelmExecutor'):
        """
        Initialize the Helm Chart Manager.
        
        Args:
            executor: Helm executor
        """
        self.executor = executor
    
    def create_chart(self, chart_name: str, destination_dir: str) -> Dict[str, Any]:
        """
        Create a new Helm chart.
        
        Args:
            chart_name: Chart name
            destination_dir: Destination directory
            
        Returns:
            Dict[str, Any]: Chart creation result
        """
        output = self.executor.run_helm_command([
            "create", chart_name
        ], cwd=destination_dir)
        
        chart_path = os.path.join(destination_dir, chart_name)
        
        return {
            "chart_name": chart_name,
            "chart_path": chart_path,
            "output": output
        }
    
    def package_chart(self, chart_path: str, 
                     destination_dir: Optional[str] = None,
                     version: Optional[str] = None,
                     app_version: Optional[str] = None) -> Dict[str, Any]:
        """
        Package a Helm chart.
        
        Args:
            chart_path: Path to chart
            destination_dir: Destination directory (optional)
            version: Chart version (optional)
            app_version: App version (optional)
            
        Returns:
            Dict[str, Any]: Chart packaging result
        """
        args = ["package", chart_path]
        
        if destination_dir:
            args.extend(["--destination", destination_dir])
        
        if version:
            args.extend(["--version", version])
        
        if app_version:
            args.extend(["--app-version", app_version])
        
        output = self.executor.run_helm_command(args)
        
        # Extract package path from output
        package_path = None
        for line in output.split("\n"):
            if line.startswith("Successfully packaged chart"):
                parts = line.split("and saved it to: ")
                if len(parts) > 1:
                    package_path = parts[1].strip()
                    break
        
        return {
            "chart_path": chart_path,
            "package_path": package_path,
            "version": version,
            "app_version": app_version,
            "output": output
        }
    
    def lint_chart(self, chart_path: str, 
                  values: Optional[Dict[str, Any]] = None,
                  set_values: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Lint a Helm chart.
        
        Args:
            chart_path: Path to chart
            values: Values to override (optional)
            set_values: Values to set on command line (optional)
            
        Returns:
            Dict[str, Any]: Chart linting result
        """
        args = ["lint", chart_path]
        
        # Add values file if provided
        if values:
            values_file = self._create_values_file(values)
            try:
                args.extend(["--values", values_file])
                
                # Add set values if provided
                if set_values:
                    for key, value in set_values.items():
                        args.extend(["--set", f"{key}={value}"])
                
                output = self.executor.run_helm_command(args)
                
                return {
                    "chart_path": chart_path,
                    "success": "Linting All good!" in output,
                    "output": output
                }
            
            finally:
                # Clean up temporary file
                if os.path.exists(values_file):
                    os.unlink(values_file)
        else:
            # Add set values if provided
            if set_values:
                for key, value in set_values.items():
                    args.extend(["--set", f"{key}={value}"])
            
            output = self.executor.run_helm_command(args)
            
            return {
                "chart_path": chart_path,
                "success": "Linting All good!" in output,
                "output": output
            }
    
    def _create_values_file(self, values: Dict[str, Any]) -> str:
        """
        Create a temporary values file.
        
        Args:
            values: Values to write to file
            
        Returns:
            str: Path to values file
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(values, f)
            return f.name


class HelmReleaseManager:
    """
    Manages Helm releases.
    
    This class provides methods for managing Helm releases,
    including installation, upgrades, rollbacks, and uninstallation.
    """
    
    def __init__(self, executor: 'HelmExecutor'):
        """
        Initialize the Helm Release Manager.
        
        Args:
            executor: Helm executor
        """
        self.executor = executor
    
    def install_chart(self, release_name: str, chart: str, 
                     namespace: str = "default",
                     values: Optional[Dict[str, Any]] = None,
                     set_values: Optional[Dict[str, str]] = None,
                     version: Optional[str] = None,
                     wait: bool = False,
                     timeout: Optional[str] = None) -> Dict[str, Any]:
        """
        Install a Helm chart.
        
        Args:
            release_name: Release name
            chart: Chart name or path
            namespace: Namespace (default: "default")
            values: Values to override (optional)
            set_values: Values to set on command line (optional)
            version: Chart version (optional)
            wait: Whether to wait for resources to be ready (default: False)
            timeout: Timeout for wait (optional)
            
        Returns:
            Dict[str, Any]: Chart installation result
        """
        args = ["install", release_name, chart, "--namespace", namespace]
        
        # Add values file if provided
        values_file = None
        if values:
            values_file = self._create_values_file(values)
            args.extend(["--values", values_file])
        
        try:
            # Add set values if provided
            if set_values:
                for key, value in set_values.items():
                    args.extend(["--set", f"{key}={value}"])
            
            # Add version if provided
            if version:
                args.extend(["--version", version])
            
            # Add wait if requested
            if wait:
                args.append("--wait")
                
                # Add timeout if provided
                if timeout:
                    args.extend(["--timeout", timeout])
            
            # Create namespace if it doesn't exist
            args.append("--create-namespace")
            
            output = self.executor.run_helm_command(args)
            
            return {
                "release_name": release_name,
                "chart": chart,
                "namespace": namespace,
                "version": version,
                "output": output
            }
        
        finally:
            # Clean up temporary file
            if values_file and os.path.exists(values_file):
                os.unlink(values_file)
    
    def upgrade_release(self, release_name: str, chart: str, 
                       namespace: str = "default",
                       values: Optional[Dict[str, Any]] = None,
                       set_values: Optional[Dict[str, str]] = None,
                       version: Optional[str] = None,
                       wait: bool = False,
                       timeout: Optional[str] = None) -> Dict[str, Any]:
        """
        Upgrade a Helm release.
        
        Args:
            release_name: Release name
            chart: Chart name or path
            namespace: Namespace (default: "default")
            values: Values to override (optional)
            set_values: Values to set on command line (optional)
            version: Chart version (optional)
            wait: Whether to wait for resources to be ready (default: False)
            timeout: Timeout for wait (optional)
            
        Returns:
            Dict[str, Any]: Release upgrade result
        """
        args = ["upgrade", release_name, chart, "--namespace", namespace]
        
        # Add values file if provided
        values_file = None
        if values:
            values_file = self._create_values_file(values)
            args.extend(["--values", values_file])
        
        try:
            # Add set values if provided
            if set_values:
                for key, value in set_values.items():
                    args.extend(["--set", f"{key}={value}"])
            
            # Add version if provided
            if version:
                args.extend(["--version", version])
            
            # Add wait if requested
            if wait:
                args.append("--wait")
                
                # Add timeout if provided
                if timeout:
                    args.extend(["--timeout", timeout])
            
            # Install if not exists
            args.append("--install")
            
            output = self.executor.run_helm_command(args)
            
            return {
                "release_name": release_name,
                "chart": chart,
                "namespace": namespace,
                "version": version,
                "output": output
            }
        
        finally:
            # Clean up temporary file
            if values_file and os.path.exists(values_file):
                os.unlink(values_file)
    
    def rollback_release(self, release_name: str, 
                        revision: Optional[int] = None,
                        namespace: str = "default",
                        wait: bool = False,
                        timeout: Optional[str] = None) -> Dict[str, Any]:
        """
        Rollback a Helm release.
        
        Args:
            release_name: Release name
            revision: Revision to rollback to (optional, defaults to previous revision)
            namespace: Namespace (default: "default")
            wait: Whether to wait for resources to be ready (default: False)
            timeout: Timeout for wait (optional)
            
        Returns:
            Dict[str, Any]: Release rollback result
        """
        args = ["rollback", release_name, "--namespace", namespace]
        
        # Add revision if provided
        if revision is not None:
            args.append(str(revision))
        
        # Add wait if requested
        if wait:
            args.append("--wait")
            
            # Add timeout if provided
            if timeout:
                args.extend(["--timeout", timeout])
        
        output = self.executor.run_helm_command(args)
        
        return {
            "release_name": release_name,
            "revision": revision,
            "namespace": namespace,
            "output": output
        }
    
    def uninstall_release(self, release_name: str, 
                         namespace: str = "default",
                         keep_history: bool = False) -> Dict[str, Any]:
        """
        Uninstall a Helm release.
        
        Args:
            release_name: Release name
            namespace: Namespace (default: "default")
            keep_history: Whether to keep release history (default: False)
            
        Returns:
            Dict[str, Any]: Release uninstallation result
        """
        args = ["uninstall", release_name, "--namespace", namespace]
        
        # Add keep-history if requested
        if keep_history:
            args.append("--keep-history")
        
        output = self.executor.run_helm_command(args)
        
        return {
            "release_name": release_name,
            "namespace": namespace,
            "keep_history": keep_history,
            "output": output
        }
    
    def list_releases(self, namespace: Optional[str] = None, 
                     all_namespaces: bool = False) -> List[Dict[str, Any]]:
        """
        List Helm releases.
        
        Args:
            namespace: Namespace (optional)
            all_namespaces: Whether to list releases in all namespaces (default: False)
            
        Returns:
            List[Dict[str, Any]]: List of releases
        """
        args = ["list", "--output", "json"]
        
        # Add namespace if provided
        if namespace:
            args.extend(["--namespace", namespace])
        
        # Add all-namespaces if requested
        if all_namespaces:
            args.append("--all-namespaces")
        
        output = self.executor.run_helm_command(args)
        
        try:
            releases_json = json.loads(output)
            
            releases = []
            for release in releases_json:
                release_info = {
                    "name": release.get("name"),
                    "namespace": release.get("namespace"),
                    "revision": release.get("revision"),
                    "updated": release.get("updated"),
                    "status": release.get("status"),
                    "chart": release.get("chart"),
                    "app_version": release.get("app_version")
                }
                releases.append(release_info)
            
            return releases
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse release list: {str(e)}")
            return []
    
    def get_release_status(self, release_name: str, 
                          namespace: str = "default") -> Dict[str, Any]:
        """
        Get status of a Helm release.
        
        Args:
            release_name: Release name
            namespace: Namespace (default: "default")
            
        Returns:
            Dict[str, Any]: Release status
        """
        output = self.executor.run_helm_command([
            "status", release_name, "--namespace", namespace, "--output", "json"
        ])
        
        try:
            status_json = json.loads(output)
            
            return {
                "release_name": release_name,
                "namespace": namespace,
                "info": status_json.get("info", {}),
                "chart": status_json.get("chart", {}),
                "config": status_json.get("config", {})
            }
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse release status: {str(e)}")
            return {
                "release_name": release_name,
                "namespace": namespace,
                "error": str(e),
                "output": output
            }
    
    def get_release_values(self, release_name: str, 
                          namespace: str = "default",
                          all_values: bool = False) -> Dict[str, Any]:
        """
        Get values of a Helm release.
        
        Args:
            release_name: Release name
            namespace: Namespace (default: "default")
            all_values: Whether to get all values (default: False)
            
        Returns:
            Dict[str, Any]: Release values
        """
        args = ["get", "values", release_name, "--namespace", namespace, "--output", "json"]
        
        # Add all if requested
        if all_values:
            args.append("--all")
        
        output = self.executor.run_helm_command(args)
        
        try:
            values_json = json.loads(output)
            
            return {
                "release_name": release_name,
                "namespace": namespace,
                "values": values_json
            }
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse release values: {str(e)}")
            return {
                "release_name": release_name,
                "namespace": namespace,
                "error": str(e),
                "output": output
            }
    
    def get_release_history(self, release_name: str, 
                           namespace: str = "default") -> Dict[str, Any]:
        """
        Get history of a Helm release.
        
        Args:
            release_name: Release name
            namespace: Namespace (default: "default")
            
        Returns:
            Dict[str, Any]: Release history
        """
        output = self.executor.run_helm_command([
            "history", release_name, "--namespace", namespace, "--output", "json"
        ])
        
        try:
            history_json = json.loads(output)
            
            return {
                "release_name": release_name,
                "namespace": namespace,
                "revisions": history_json
            }
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse release history: {str(e)}")
            return {
                "release_name": release_name,
                "namespace": namespace,
                "error": str(e),
                "output": output
            }
    
    def _create_values_file(self, values: Dict[str, Any]) -> str:
        """
        Create a temporary values file.
        
        Args:
            values: Values to write to file
            
        Returns:
            str: Path to values file
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(values, f)
            return f.name


class HelmRepositoryManager:
    """
    Manages Helm repositories.
    
    This class provides methods for managing Helm repositories,
    including adding, updating, and listing repositories.
    """
    
    def __init__(self, executor: 'HelmExecutor'):
        """
        Initialize the Helm Repository Manager.
        
        Args:
            executor: Helm executor
        """
        self.executor = executor
    
    def add_repository(self, name: str, url: str) -> Dict[str, Any]:
        """
        Add a Helm repository.
        
        Args:
            name: Repository name
            url: Repository URL
            
        Returns:
            Dict[str, Any]: Repository addition result
        """
        output = self.executor.run_helm_command([
            "repo", "add", name, url
        ])
        
        return {
            "name": name,
            "url": url,
            "output": output
        }
    
    def update_repositories(self) -> Dict[str, Any]:
        """
        Update Helm repositories.
        
        Returns:
            Dict[str, Any]: Repository update result
        """
        output = self.executor.run_helm_command([
            "repo", "update"
        ])
        
        return {
            "output": output
        }
    
    def list_repositories(self) -> List[Dict[str, Any]]:
        """
        List Helm repositories.
        
        Returns:
            List[Dict[str, Any]]: List of repositories
        """
        output = self.executor.run_helm_command([
            "repo", "list", "--output", "json"
        ])
        
        try:
            repos_json = json.loads(output)
            
            repos = []
            for repo in repos_json:
                repo_info = {
                    "name": repo.get("name"),
                    "url": repo.get("url")
                }
                repos.append(repo_info)
            
            return repos
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse repository list: {str(e)}")
            return []
    
    def remove_repository(self, name: str) -> Dict[str, Any]:
        """
        Remove a Helm repository.
        
        Args:
            name: Repository name
            
        Returns:
            Dict[str, Any]: Repository removal result
        """
        output = self.executor.run_helm_command([
            "repo", "remove", name
        ])
        
        return {
            "name": name,
            "output": output
        }


class HelmExecutor:
    """
    Executes Helm CLI commands.
    
    This class provides methods for executing Helm CLI and kubectl commands
    and handling their output.
    """
    
    def __init__(self, helm_binary: str, kubectl_binary: str, working_dir: str):
        """
        Initialize the Helm Executor.
        
        Args:
            helm_binary: Path to Helm CLI binary
            kubectl_binary: Path to kubectl binary
            working_dir: Working directory for Helm operations
        """
        self.helm_binary = helm_binary
        self.kubectl_binary = kubectl_binary
        self.working_dir = working_dir
    
    def run_helm_command(self, args: List[str], check: bool = True, 
                        cwd: Optional[str] = None) -> str:
        """
        Run a Helm CLI command.
        
        Args:
            args: Command arguments
            check: Whether to check for command success
            cwd: Working directory (optional, defaults to self.working_dir)
            
        Returns:
            str: Command output
            
        Raises:
            Exception: If the command fails and check is True
        """
        cmd = [self.helm_binary] + args
        logger.info(f"Running Helm command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd or self.working_dir,
                capture_output=True,
                text=True,
                check=check
            )
            
            return result.stdout
        
        except subprocess.CalledProcessError as e:
            error_message = f"Helm command failed: {e.stderr}"
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
