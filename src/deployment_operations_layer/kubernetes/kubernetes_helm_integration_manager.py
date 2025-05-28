"""
Kubernetes Helm Integration Manager - Manages integration with Helm charts

This module provides integration with Helm for managing Kubernetes applications
through Helm charts, including installation, upgrading, and uninstallation.
"""

import logging
import json
import os
import subprocess
import tempfile
import yaml
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class KubernetesHelmIntegrationManager:
    """
    Manages integration with Helm for Kubernetes applications.
    
    This component is responsible for integrating with Helm,
    handling chart management, releases, and repositories.
    """
    
    def __init__(self, config_dict: Dict[str, Any] = None):
        """
        Initialize the Kubernetes Helm Integration Manager.
        
        Args:
            config_dict: Configuration dictionary for the manager
        """
        self.config_dict = config_dict or {}
        
        # Default helm path
        self.helm_path = self.config_dict.get("helm_path", "helm")
        
        # Default namespace
        self.namespace = self.config_dict.get("namespace", "default")
        
        # Default kubeconfig
        self.kubeconfig = self.config_dict.get("kubeconfig", os.path.expanduser("~/.kube/config"))
        
        # Default repositories
        self.repositories = self.config_dict.get("repositories", {})
        
        logger.info("Initializing Kubernetes Helm Integration Manager")
    
    def initialize(self) -> Dict[str, Any]:
        """
        Initialize the manager and verify Helm installation.
        
        Returns:
            Dictionary with initialization result
        """
        logger.info("Initializing Kubernetes Helm Integration Manager")
        
        try:
            # Check if Helm is installed
            cmd = [self.helm_path, "version", "--short"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse version
            version = result.stdout.strip()
            
            # Add default repositories
            for repo_name, repo_url in self.repositories.items():
                self.add_repository(repo_name, repo_url)
            
            # Update repositories
            self.update_repositories()
            
            logger.info(f"Helm version: {version}")
            logger.info("Kubernetes Helm Integration Manager initialization successful")
            
            return {
                "success": True,
                "version": version
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to initialize Kubernetes Helm Integration Manager: {e.stderr}")
            return {"success": False, "error": f"Failed to initialize Kubernetes Helm Integration Manager: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to initialize Kubernetes Helm Integration Manager: {str(e)}")
            return {"success": False, "error": f"Failed to initialize Kubernetes Helm Integration Manager: {str(e)}"}
    
    def set_namespace(self, namespace: str) -> Dict[str, Any]:
        """
        Set the namespace to use.
        
        Args:
            namespace: Namespace to use
            
        Returns:
            Dictionary with result
        """
        logger.info(f"Setting namespace to {namespace}")
        
        self.namespace = namespace
        
        return {
            "success": True,
            "namespace": namespace
        }
    
    def get_namespace(self) -> Dict[str, Any]:
        """
        Get the current namespace.
        
        Returns:
            Dictionary with namespace
        """
        return {
            "success": True,
            "namespace": self.namespace
        }
    
    def set_kubeconfig(self, kubeconfig: str) -> Dict[str, Any]:
        """
        Set the kubeconfig to use.
        
        Args:
            kubeconfig: Path to kubeconfig file
            
        Returns:
            Dictionary with result
        """
        logger.info(f"Setting kubeconfig to {kubeconfig}")
        
        self.kubeconfig = kubeconfig
        
        return {
            "success": True,
            "kubeconfig": kubeconfig
        }
    
    def get_kubeconfig(self) -> Dict[str, Any]:
        """
        Get the current kubeconfig.
        
        Returns:
            Dictionary with kubeconfig
        """
        return {
            "success": True,
            "kubeconfig": self.kubeconfig
        }
    
    def add_repository(self, name: str, url: str) -> Dict[str, Any]:
        """
        Add a Helm repository.
        
        Args:
            name: Name of the repository
            url: URL of the repository
            
        Returns:
            Dictionary with addition result
        """
        logger.info(f"Adding Helm repository {name} with URL {url}")
        
        try:
            # Add repository
            cmd = [self.helm_path, "repo", "add", name, url]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Add to repositories
            self.repositories[name] = url
            
            logger.info(f"Successfully added Helm repository {name}")
            
            return {
                "success": True,
                "repository": name,
                "url": url,
                "output": result.stdout
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to add Helm repository: {e.stderr}")
            return {"success": False, "error": f"Failed to add Helm repository: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to add Helm repository: {str(e)}")
            return {"success": False, "error": f"Failed to add Helm repository: {str(e)}"}
    
    def remove_repository(self, name: str) -> Dict[str, Any]:
        """
        Remove a Helm repository.
        
        Args:
            name: Name of the repository
            
        Returns:
            Dictionary with removal result
        """
        logger.info(f"Removing Helm repository {name}")
        
        try:
            # Remove repository
            cmd = [self.helm_path, "repo", "remove", name]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Remove from repositories
            if name in self.repositories:
                del self.repositories[name]
            
            logger.info(f"Successfully removed Helm repository {name}")
            
            return {
                "success": True,
                "repository": name,
                "output": result.stdout
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to remove Helm repository: {e.stderr}")
            return {"success": False, "error": f"Failed to remove Helm repository: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to remove Helm repository: {str(e)}")
            return {"success": False, "error": f"Failed to remove Helm repository: {str(e)}"}
    
    def update_repositories(self) -> Dict[str, Any]:
        """
        Update Helm repositories.
        
        Returns:
            Dictionary with update result
        """
        logger.info("Updating Helm repositories")
        
        try:
            # Update repositories
            cmd = [self.helm_path, "repo", "update"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            logger.info("Successfully updated Helm repositories")
            
            return {
                "success": True,
                "output": result.stdout
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to update Helm repositories: {e.stderr}")
            return {"success": False, "error": f"Failed to update Helm repositories: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to update Helm repositories: {str(e)}")
            return {"success": False, "error": f"Failed to update Helm repositories: {str(e)}"}
    
    def list_repositories(self) -> Dict[str, Any]:
        """
        List Helm repositories.
        
        Returns:
            Dictionary with repositories
        """
        logger.info("Listing Helm repositories")
        
        try:
            # List repositories
            cmd = [self.helm_path, "repo", "list", "--output", "json"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse JSON output
            repositories = json.loads(result.stdout)
            
            logger.info(f"Successfully listed {len(repositories)} Helm repositories")
            
            return {
                "success": True,
                "repositories": repositories
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to list Helm repositories: {e.stderr}")
            return {"success": False, "error": f"Failed to list Helm repositories: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to list Helm repositories: {str(e)}")
            return {"success": False, "error": f"Failed to list Helm repositories: {str(e)}"}
    
    def search_charts(self, keyword: str = None, repository: str = None) -> Dict[str, Any]:
        """
        Search for Helm charts.
        
        Args:
            keyword: Keyword to search for
            repository: Repository to search in
            
        Returns:
            Dictionary with search results
        """
        logger.info(f"Searching for Helm charts with keyword {keyword}")
        
        try:
            # Build command
            cmd = [self.helm_path, "search", "repo"]
            
            if keyword:
                cmd.append(keyword)
            
            if repository:
                cmd.extend(["--repo", repository])
            
            cmd.extend(["--output", "json"])
            
            # Search charts
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse JSON output
            charts = json.loads(result.stdout)
            
            logger.info(f"Successfully found {len(charts)} Helm charts")
            
            return {
                "success": True,
                "charts": charts
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to search Helm charts: {e.stderr}")
            return {"success": False, "error": f"Failed to search Helm charts: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to search Helm charts: {str(e)}")
            return {"success": False, "error": f"Failed to search Helm charts: {str(e)}"}
    
    def install_chart(self, release_name: str, chart: str, values: Dict[str, Any] = None, 
                    namespace: str = None, version: str = None, 
                    set_values: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Install a Helm chart.
        
        Args:
            release_name: Name of the release
            chart: Chart to install
            values: Values to set (as dictionary)
            namespace: Namespace to install in (if None, uses default)
            version: Version of the chart to install
            set_values: Values to set (as command line arguments)
            
        Returns:
            Dictionary with installation result
        """
        logger.info(f"Installing Helm chart {chart} as release {release_name}")
        
        try:
            # Set namespace
            if not namespace:
                namespace = self.namespace
            
            # Build command
            cmd = [
                self.helm_path,
                "install",
                release_name,
                chart,
                "--namespace", namespace,
                "--create-namespace",
                "--kubeconfig", self.kubeconfig
            ]
            
            # Add version if specified
            if version:
                cmd.extend(["--version", version])
            
            # Add values file if specified
            if values:
                # Create temporary file for values
                with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
                    yaml.dump(values, f, default_flow_style=False)
                    values_file = f.name
                
                cmd.extend(["-f", values_file])
            
            # Add set values if specified
            if set_values:
                for key, value in set_values.items():
                    cmd.extend(["--set", f"{key}={value}"])
            
            # Install chart
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            logger.info(f"Successfully installed Helm chart {chart} as release {release_name} in namespace {namespace}")
            
            return {
                "success": True,
                "release": release_name,
                "chart": chart,
                "namespace": namespace,
                "output": result.stdout
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install Helm chart: {e.stderr}")
            return {"success": False, "error": f"Failed to install Helm chart: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to install Helm chart: {str(e)}")
            return {"success": False, "error": f"Failed to install Helm chart: {str(e)}"}
        finally:
            # Clean up temporary file
            if values and 'values_file' in locals():
                os.unlink(values_file)
    
    def upgrade_chart(self, release_name: str, chart: str, values: Dict[str, Any] = None, 
                    namespace: str = None, version: str = None, 
                    set_values: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Upgrade a Helm release.
        
        Args:
            release_name: Name of the release
            chart: Chart to upgrade to
            values: Values to set (as dictionary)
            namespace: Namespace the release is in (if None, uses default)
            version: Version of the chart to upgrade to
            set_values: Values to set (as command line arguments)
            
        Returns:
            Dictionary with upgrade result
        """
        logger.info(f"Upgrading Helm release {release_name} to chart {chart}")
        
        try:
            # Set namespace
            if not namespace:
                namespace = self.namespace
            
            # Build command
            cmd = [
                self.helm_path,
                "upgrade",
                release_name,
                chart,
                "--namespace", namespace,
                "--kubeconfig", self.kubeconfig
            ]
            
            # Add version if specified
            if version:
                cmd.extend(["--version", version])
            
            # Add values file if specified
            if values:
                # Create temporary file for values
                with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
                    yaml.dump(values, f, default_flow_style=False)
                    values_file = f.name
                
                cmd.extend(["-f", values_file])
            
            # Add set values if specified
            if set_values:
                for key, value in set_values.items():
                    cmd.extend(["--set", f"{key}={value}"])
            
            # Upgrade chart
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            logger.info(f"Successfully upgraded Helm release {release_name} to chart {chart} in namespace {namespace}")
            
            return {
                "success": True,
                "release": release_name,
                "chart": chart,
                "namespace": namespace,
                "output": result.stdout
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to upgrade Helm release: {e.stderr}")
            return {"success": False, "error": f"Failed to upgrade Helm release: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to upgrade Helm release: {str(e)}")
            return {"success": False, "error": f"Failed to upgrade Helm release: {str(e)}"}
        finally:
            # Clean up temporary file
            if values and 'values_file' in locals():
                os.unlink(values_file)
    
    def uninstall_release(self, release_name: str, namespace: str = None) -> Dict[str, Any]:
        """
        Uninstall a Helm release.
        
        Args:
            release_name: Name of the release
            namespace: Namespace the release is in (if None, uses default)
            
        Returns:
            Dictionary with uninstallation result
        """
        logger.info(f"Uninstalling Helm release {release_name}")
        
        try:
            # Set namespace
            if not namespace:
                namespace = self.namespace
            
            # Build command
            cmd = [
                self.helm_path,
                "uninstall",
                release_name,
                "--namespace", namespace,
                "--kubeconfig", self.kubeconfig
            ]
            
            # Uninstall release
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            logger.info(f"Successfully uninstalled Helm release {release_name} from namespace {namespace}")
            
            return {
                "success": True,
                "release": release_name,
                "namespace": namespace,
                "output": result.stdout
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to uninstall Helm release: {e.stderr}")
            return {"success": False, "error": f"Failed to uninstall Helm release: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to uninstall Helm release: {str(e)}")
            return {"success": False, "error": f"Failed to uninstall Helm release: {str(e)}"}
    
    def list_releases(self, namespace: str = None, all_namespaces: bool = False) -> Dict[str, Any]:
        """
        List Helm releases.
        
        Args:
            namespace: Namespace to list releases in (if None, uses default)
            all_namespaces: Whether to list releases in all namespaces
            
        Returns:
            Dictionary with releases
        """
        logger.info("Listing Helm releases")
        
        try:
            # Set namespace
            if not namespace and not all_namespaces:
                namespace = self.namespace
            
            # Build command
            cmd = [
                self.helm_path,
                "list",
                "--kubeconfig", self.kubeconfig,
                "--output", "json"
            ]
            
            if all_namespaces:
                cmd.append("--all-namespaces")
            else:
                cmd.extend(["--namespace", namespace])
            
            # List releases
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse JSON output
            releases = json.loads(result.stdout)
            
            logger.info(f"Successfully listed {len(releases)} Helm releases")
            
            return {
                "success": True,
                "namespace": namespace if not all_namespaces else "all",
                "releases": releases
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to list Helm releases: {e.stderr}")
            return {"success": False, "error": f"Failed to list Helm releases: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to list Helm releases: {str(e)}")
            return {"success": False, "error": f"Failed to list Helm releases: {str(e)}"}
    
    def get_release(self, release_name: str, namespace: str = None) -> Dict[str, Any]:
        """
        Get information about a Helm release.
        
        Args:
            release_name: Name of the release
            namespace: Namespace the release is in (if None, uses default)
            
        Returns:
            Dictionary with release information
        """
        logger.info(f"Getting information about Helm release {release_name}")
        
        try:
            # Set namespace
            if not namespace:
                namespace = self.namespace
            
            # Build command
            cmd = [
                self.helm_path,
                "get",
                "all",
                release_name,
                "--namespace", namespace,
                "--kubeconfig", self.kubeconfig
            ]
            
            # Get release information
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            logger.info(f"Successfully retrieved information about Helm release {release_name} in namespace {namespace}")
            
            return {
                "success": True,
                "release": release_name,
                "namespace": namespace,
                "info": result.stdout
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get Helm release information: {e.stderr}")
            return {"success": False, "error": f"Failed to get Helm release information: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to get Helm release information: {str(e)}")
            return {"success": False, "error": f"Failed to get Helm release information: {str(e)}"}
    
    def get_release_values(self, release_name: str, namespace: str = None) -> Dict[str, Any]:
        """
        Get values for a Helm release.
        
        Args:
            release_name: Name of the release
            namespace: Namespace the release is in (if None, uses default)
            
        Returns:
            Dictionary with release values
        """
        logger.info(f"Getting values for Helm release {release_name}")
        
        try:
            # Set namespace
            if not namespace:
                namespace = self.namespace
            
            # Build command
            cmd = [
                self.helm_path,
                "get",
                "values",
                release_name,
                "--namespace", namespace,
                "--kubeconfig", self.kubeconfig,
                "--output", "yaml",
                "--all"
            ]
            
            # Get release values
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse YAML output
            values = yaml.safe_load(result.stdout)
            
            logger.info(f"Successfully retrieved values for Helm release {release_name} in namespace {namespace}")
            
            return {
                "success": True,
                "release": release_name,
                "namespace": namespace,
                "values": values
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get Helm release values: {e.stderr}")
            return {"success": False, "error": f"Failed to get Helm release values: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to get Helm release values: {str(e)}")
            return {"success": False, "error": f"Failed to get Helm release values: {str(e)}"}
    
    def get_release_status(self, release_name: str, namespace: str = None) -> Dict[str, Any]:
        """
        Get status of a Helm release.
        
        Args:
            release_name: Name of the release
            namespace: Namespace the release is in (if None, uses default)
            
        Returns:
            Dictionary with release status
        """
        logger.info(f"Getting status of Helm release {release_name}")
        
        try:
            # Set namespace
            if not namespace:
                namespace = self.namespace
            
            # Build command
            cmd = [
                self.helm_path,
                "status",
                release_name,
                "--namespace", namespace,
                "--kubeconfig", self.kubeconfig
            ]
            
            # Get release status
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            logger.info(f"Successfully retrieved status of Helm release {release_name} in namespace {namespace}")
            
            return {
                "success": True,
                "release": release_name,
                "namespace": namespace,
                "status": result.stdout
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get Helm release status: {e.stderr}")
            return {"success": False, "error": f"Failed to get Helm release status: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to get Helm release status: {str(e)}")
            return {"success": False, "error": f"Failed to get Helm release status: {str(e)}"}
    
    def get_release_history(self, release_name: str, namespace: str = None) -> Dict[str, Any]:
        """
        Get history of a Helm release.
        
        Args:
            release_name: Name of the release
            namespace: Namespace the release is in (if None, uses default)
            
        Returns:
            Dictionary with release history
        """
        logger.info(f"Getting history of Helm release {release_name}")
        
        try:
            # Set namespace
            if not namespace:
                namespace = self.namespace
            
            # Build command
            cmd = [
                self.helm_path,
                "history",
                release_name,
                "--namespace", namespace,
                "--kubeconfig", self.kubeconfig,
                "--output", "json"
            ]
            
            # Get release history
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse JSON output
            history = json.loads(result.stdout)
            
            logger.info(f"Successfully retrieved history of Helm release {release_name} in namespace {namespace}")
            
            return {
                "success": True,
                "release": release_name,
                "namespace": namespace,
                "history": history
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get Helm release history: {e.stderr}")
            return {"success": False, "error": f"Failed to get Helm release history: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to get Helm release history: {str(e)}")
            return {"success": False, "error": f"Failed to get Helm release history: {str(e)}"}
    
    def rollback_release(self, release_name: str, revision: int, namespace: str = None) -> Dict[str, Any]:
        """
        Rollback a Helm release to a previous revision.
        
        Args:
            release_name: Name of the release
            revision: Revision to rollback to
            namespace: Namespace the release is in (if None, uses default)
            
        Returns:
            Dictionary with rollback result
        """
        logger.info(f"Rolling back Helm release {release_name} to revision {revision}")
        
        try:
            # Set namespace
            if not namespace:
                namespace = self.namespace
            
            # Build command
            cmd = [
                self.helm_path,
                "rollback",
                release_name,
                str(revision),
                "--namespace", namespace,
                "--kubeconfig", self.kubeconfig
            ]
            
            # Rollback release
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            logger.info(f"Successfully rolled back Helm release {release_name} to revision {revision} in namespace {namespace}")
            
            return {
                "success": True,
                "release": release_name,
                "namespace": namespace,
                "revision": revision,
                "output": result.stdout
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to rollback Helm release: {e.stderr}")
            return {"success": False, "error": f"Failed to rollback Helm release: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to rollback Helm release: {str(e)}")
            return {"success": False, "error": f"Failed to rollback Helm release: {str(e)}"}
    
    def create_chart(self, chart_name: str, destination_dir: str) -> Dict[str, Any]:
        """
        Create a new Helm chart.
        
        Args:
            chart_name: Name of the chart
            destination_dir: Directory to create the chart in
            
        Returns:
            Dictionary with creation result
        """
        logger.info(f"Creating new Helm chart {chart_name}")
        
        try:
            # Build command
            cmd = [
                self.helm_path,
                "create",
                chart_name,
                "--destination", destination_dir
            ]
            
            # Create chart
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            logger.info(f"Successfully created new Helm chart {chart_name} in {destination_dir}")
            
            return {
                "success": True,
                "chart": chart_name,
                "directory": os.path.join(destination_dir, chart_name),
                "output": result.stdout
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create Helm chart: {e.stderr}")
            return {"success": False, "error": f"Failed to create Helm chart: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to create Helm chart: {str(e)}")
            return {"success": False, "error": f"Failed to create Helm chart: {str(e)}"}
    
    def package_chart(self, chart_dir: str, destination_dir: str = None) -> Dict[str, Any]:
        """
        Package a Helm chart.
        
        Args:
            chart_dir: Directory containing the chart
            destination_dir: Directory to save the packaged chart in
            
        Returns:
            Dictionary with packaging result
        """
        logger.info(f"Packaging Helm chart in {chart_dir}")
        
        try:
            # Build command
            cmd = [
                self.helm_path,
                "package",
                chart_dir
            ]
            
            if destination_dir:
                cmd.extend(["--destination", destination_dir])
            
            # Package chart
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            logger.info(f"Successfully packaged Helm chart in {chart_dir}")
            
            return {
                "success": True,
                "chart_dir": chart_dir,
                "destination_dir": destination_dir,
                "output": result.stdout
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to package Helm chart: {e.stderr}")
            return {"success": False, "error": f"Failed to package Helm chart: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to package Helm chart: {str(e)}")
            return {"success": False, "error": f"Failed to package Helm chart: {str(e)}"}
    
    def lint_chart(self, chart_dir: str) -> Dict[str, Any]:
        """
        Lint a Helm chart.
        
        Args:
            chart_dir: Directory containing the chart
            
        Returns:
            Dictionary with linting result
        """
        logger.info(f"Linting Helm chart in {chart_dir}")
        
        try:
            # Build command
            cmd = [
                self.helm_path,
                "lint",
                chart_dir
            ]
            
            # Lint chart
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            logger.info(f"Successfully linted Helm chart in {chart_dir}")
            
            return {
                "success": True,
                "chart_dir": chart_dir,
                "output": result.stdout
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to lint Helm chart: {e.stderr}")
            return {"success": False, "error": f"Failed to lint Helm chart: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to lint Helm chart: {str(e)}")
            return {"success": False, "error": f"Failed to lint Helm chart: {str(e)}"}
    
    def template_chart(self, chart: str, release_name: str, values: Dict[str, Any] = None, 
                     namespace: str = None, set_values: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Render a Helm chart locally and display the output.
        
        Args:
            chart: Chart to render
            release_name: Name of the release
            values: Values to set (as dictionary)
            namespace: Namespace to render for (if None, uses default)
            set_values: Values to set (as command line arguments)
            
        Returns:
            Dictionary with rendering result
        """
        logger.info(f"Rendering Helm chart {chart} as release {release_name}")
        
        try:
            # Set namespace
            if not namespace:
                namespace = self.namespace
            
            # Build command
            cmd = [
                self.helm_path,
                "template",
                release_name,
                chart,
                "--namespace", namespace
            ]
            
            # Add values file if specified
            if values:
                # Create temporary file for values
                with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
                    yaml.dump(values, f, default_flow_style=False)
                    values_file = f.name
                
                cmd.extend(["-f", values_file])
            
            # Add set values if specified
            if set_values:
                for key, value in set_values.items():
                    cmd.extend(["--set", f"{key}={value}"])
            
            # Render chart
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            logger.info(f"Successfully rendered Helm chart {chart} as release {release_name}")
            
            return {
                "success": True,
                "release": release_name,
                "chart": chart,
                "namespace": namespace,
                "output": result.stdout
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to render Helm chart: {e.stderr}")
            return {"success": False, "error": f"Failed to render Helm chart: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to render Helm chart: {str(e)}")
            return {"success": False, "error": f"Failed to render Helm chart: {str(e)}"}
        finally:
            # Clean up temporary file
            if values and 'values_file' in locals():
                os.unlink(values_file)
