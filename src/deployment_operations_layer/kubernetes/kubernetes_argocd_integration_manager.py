"""
Kubernetes ArgoCD Integration Manager - Manages integration with ArgoCD for GitOps deployments

This module provides integration with ArgoCD for GitOps-based deployments,
including application management, sync operations, and status monitoring.
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

class KubernetesArgoCDIntegrationManager:
    """
    Manages integration with ArgoCD for GitOps-based deployments.
    
    This component is responsible for integrating with ArgoCD,
    handling application management, sync operations, and status monitoring.
    """
    
    def __init__(self, config_dict: Dict[str, Any] = None):
        """
        Initialize the Kubernetes ArgoCD Integration Manager.
        
        Args:
            config_dict: Configuration dictionary for the manager
        """
        self.config_dict = config_dict or {}
        
        # Default argocd path
        self.argocd_path = self.config_dict.get("argocd_path", "argocd")
        
        # Default server
        self.server = self.config_dict.get("server", "")
        
        # Default auth token
        self.auth_token = self.config_dict.get("auth_token", "")
        
        # Default namespace
        self.namespace = self.config_dict.get("namespace", "argocd")
        
        logger.info("Initializing Kubernetes ArgoCD Integration Manager")
    
    def initialize(self, server: str = None, auth_token: str = None) -> Dict[str, Any]:
        """
        Initialize the manager and verify ArgoCD CLI installation.
        
        Args:
            server: ArgoCD server URL
            auth_token: ArgoCD authentication token
            
        Returns:
            Dictionary with initialization result
        """
        logger.info("Initializing Kubernetes ArgoCD Integration Manager")
        
        try:
            # Set server and auth token if provided
            if server:
                self.server = server
            
            if auth_token:
                self.auth_token = auth_token
            
            # Check if ArgoCD CLI is installed
            cmd = [self.argocd_path, "version", "--client"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse version
            version = result.stdout.strip()
            
            logger.info(f"ArgoCD CLI version: {version}")
            logger.info("Kubernetes ArgoCD Integration Manager initialization successful")
            
            return {
                "success": True,
                "version": version
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to initialize Kubernetes ArgoCD Integration Manager: {e.stderr}")
            return {"success": False, "error": f"Failed to initialize Kubernetes ArgoCD Integration Manager: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to initialize Kubernetes ArgoCD Integration Manager: {str(e)}")
            return {"success": False, "error": f"Failed to initialize Kubernetes ArgoCD Integration Manager: {str(e)}"}
    
    def login(self, server: str, username: str = None, password: str = None, 
            token: str = None, insecure: bool = False) -> Dict[str, Any]:
        """
        Login to ArgoCD server.
        
        Args:
            server: ArgoCD server URL
            username: Username for authentication
            password: Password for authentication
            token: Authentication token
            insecure: Whether to skip TLS verification
            
        Returns:
            Dictionary with login result
        """
        logger.info(f"Logging in to ArgoCD server {server}")
        
        try:
            # Build command
            cmd = [self.argocd_path, "login", server]
            
            if insecure:
                cmd.append("--insecure")
            
            if token:
                cmd.extend(["--auth-token", token])
            elif username and password:
                cmd.extend(["--username", username, "--password", password])
            else:
                logger.error("Either token or username and password must be provided")
                return {"success": False, "error": "Either token or username and password must be provided"}
            
            # Login to server
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Set server
            self.server = server
            
            # Set auth token if provided
            if token:
                self.auth_token = token
            
            logger.info(f"Successfully logged in to ArgoCD server {server}")
            
            return {
                "success": True,
                "server": server,
                "output": result.stdout
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to login to ArgoCD server: {e.stderr}")
            return {"success": False, "error": f"Failed to login to ArgoCD server: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to login to ArgoCD server: {str(e)}")
            return {"success": False, "error": f"Failed to login to ArgoCD server: {str(e)}"}
    
    def set_context(self, context: str) -> Dict[str, Any]:
        """
        Set the current context.
        
        Args:
            context: Context to set
            
        Returns:
            Dictionary with result
        """
        logger.info(f"Setting ArgoCD context to {context}")
        
        try:
            # Build command
            cmd = [self.argocd_path, "context", context]
            
            # Set context
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            logger.info(f"Successfully set ArgoCD context to {context}")
            
            return {
                "success": True,
                "context": context,
                "output": result.stdout
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to set ArgoCD context: {e.stderr}")
            return {"success": False, "error": f"Failed to set ArgoCD context: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to set ArgoCD context: {str(e)}")
            return {"success": False, "error": f"Failed to set ArgoCD context: {str(e)}"}
    
    def list_applications(self) -> Dict[str, Any]:
        """
        List ArgoCD applications.
        
        Returns:
            Dictionary with applications
        """
        logger.info("Listing ArgoCD applications")
        
        try:
            # Build command
            cmd = [self.argocd_path, "app", "list", "--output", "json"]
            
            if self.server:
                cmd.extend(["--server", self.server])
            
            if self.auth_token:
                cmd.extend(["--auth-token", self.auth_token])
            
            # List applications
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse JSON output
            applications = json.loads(result.stdout)
            
            logger.info(f"Successfully listed {len(applications)} ArgoCD applications")
            
            return {
                "success": True,
                "applications": applications
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to list ArgoCD applications: {e.stderr}")
            return {"success": False, "error": f"Failed to list ArgoCD applications: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to list ArgoCD applications: {str(e)}")
            return {"success": False, "error": f"Failed to list ArgoCD applications: {str(e)}"}
    
    def get_application(self, name: str) -> Dict[str, Any]:
        """
        Get information about an ArgoCD application.
        
        Args:
            name: Name of the application
            
        Returns:
            Dictionary with application information
        """
        logger.info(f"Getting information about ArgoCD application {name}")
        
        try:
            # Build command
            cmd = [self.argocd_path, "app", "get", name, "--output", "json"]
            
            if self.server:
                cmd.extend(["--server", self.server])
            
            if self.auth_token:
                cmd.extend(["--auth-token", self.auth_token])
            
            # Get application
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse JSON output
            application = json.loads(result.stdout)
            
            logger.info(f"Successfully retrieved information about ArgoCD application {name}")
            
            return {
                "success": True,
                "application": application
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get ArgoCD application: {e.stderr}")
            return {"success": False, "error": f"Failed to get ArgoCD application: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to get ArgoCD application: {str(e)}")
            return {"success": False, "error": f"Failed to get ArgoCD application: {str(e)}"}
    
    def create_application(self, name: str, repo: str, path: str, dest_server: str, 
                         dest_namespace: str, project: str = "default", 
                         sync_policy: str = None, values: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create an ArgoCD application.
        
        Args:
            name: Name of the application
            repo: Git repository URL
            path: Path in the repository
            dest_server: Destination server
            dest_namespace: Destination namespace
            project: ArgoCD project
            sync_policy: Sync policy (none, automated)
            values: Values to set
            
        Returns:
            Dictionary with creation result
        """
        logger.info(f"Creating ArgoCD application {name}")
        
        try:
            # Build command
            cmd = [
                self.argocd_path, "app", "create", name,
                "--repo", repo,
                "--path", path,
                "--dest-server", dest_server,
                "--dest-namespace", dest_namespace,
                "--project", project
            ]
            
            if self.server:
                cmd.extend(["--server", self.server])
            
            if self.auth_token:
                cmd.extend(["--auth-token", self.auth_token])
            
            if sync_policy:
                cmd.extend(["--sync-policy", sync_policy])
            
            # Add values if specified
            if values:
                # Create temporary file for values
                with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
                    json.dump(values, f)
                    values_file = f.name
                
                cmd.extend(["--values", values_file])
            
            # Create application
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            logger.info(f"Successfully created ArgoCD application {name}")
            
            return {
                "success": True,
                "application": name,
                "output": result.stdout
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create ArgoCD application: {e.stderr}")
            return {"success": False, "error": f"Failed to create ArgoCD application: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to create ArgoCD application: {str(e)}")
            return {"success": False, "error": f"Failed to create ArgoCD application: {str(e)}"}
        finally:
            # Clean up temporary file
            if values and 'values_file' in locals():
                os.unlink(values_file)
    
    def delete_application(self, name: str, cascade: bool = True) -> Dict[str, Any]:
        """
        Delete an ArgoCD application.
        
        Args:
            name: Name of the application
            cascade: Whether to cascade delete resources
            
        Returns:
            Dictionary with deletion result
        """
        logger.info(f"Deleting ArgoCD application {name}")
        
        try:
            # Build command
            cmd = [self.argocd_path, "app", "delete", name, "--yes"]
            
            if self.server:
                cmd.extend(["--server", self.server])
            
            if self.auth_token:
                cmd.extend(["--auth-token", self.auth_token])
            
            if cascade:
                cmd.append("--cascade")
            
            # Delete application
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            logger.info(f"Successfully deleted ArgoCD application {name}")
            
            return {
                "success": True,
                "application": name,
                "output": result.stdout
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to delete ArgoCD application: {e.stderr}")
            return {"success": False, "error": f"Failed to delete ArgoCD application: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to delete ArgoCD application: {str(e)}")
            return {"success": False, "error": f"Failed to delete ArgoCD application: {str(e)}"}
    
    def sync_application(self, name: str, prune: bool = False, dry_run: bool = False) -> Dict[str, Any]:
        """
        Sync an ArgoCD application.
        
        Args:
            name: Name of the application
            prune: Whether to prune resources
            dry_run: Whether to perform a dry run
            
        Returns:
            Dictionary with sync result
        """
        logger.info(f"Syncing ArgoCD application {name}")
        
        try:
            # Build command
            cmd = [self.argocd_path, "app", "sync", name]
            
            if self.server:
                cmd.extend(["--server", self.server])
            
            if self.auth_token:
                cmd.extend(["--auth-token", self.auth_token])
            
            if prune:
                cmd.append("--prune")
            
            if dry_run:
                cmd.append("--dry-run")
            
            # Sync application
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            logger.info(f"Successfully synced ArgoCD application {name}")
            
            return {
                "success": True,
                "application": name,
                "output": result.stdout
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to sync ArgoCD application: {e.stderr}")
            return {"success": False, "error": f"Failed to sync ArgoCD application: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to sync ArgoCD application: {str(e)}")
            return {"success": False, "error": f"Failed to sync ArgoCD application: {str(e)}"}
    
    def get_application_history(self, name: str) -> Dict[str, Any]:
        """
        Get history of an ArgoCD application.
        
        Args:
            name: Name of the application
            
        Returns:
            Dictionary with application history
        """
        logger.info(f"Getting history of ArgoCD application {name}")
        
        try:
            # Build command
            cmd = [self.argocd_path, "app", "history", name, "--output", "json"]
            
            if self.server:
                cmd.extend(["--server", self.server])
            
            if self.auth_token:
                cmd.extend(["--auth-token", self.auth_token])
            
            # Get application history
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse JSON output
            history = json.loads(result.stdout)
            
            logger.info(f"Successfully retrieved history of ArgoCD application {name}")
            
            return {
                "success": True,
                "application": name,
                "history": history
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get ArgoCD application history: {e.stderr}")
            return {"success": False, "error": f"Failed to get ArgoCD application history: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to get ArgoCD application history: {str(e)}")
            return {"success": False, "error": f"Failed to get ArgoCD application history: {str(e)}"}
    
    def rollback_application(self, name: str, revision: str) -> Dict[str, Any]:
        """
        Rollback an ArgoCD application to a previous revision.
        
        Args:
            name: Name of the application
            revision: Revision to rollback to
            
        Returns:
            Dictionary with rollback result
        """
        logger.info(f"Rolling back ArgoCD application {name} to revision {revision}")
        
        try:
            # Build command
            cmd = [self.argocd_path, "app", "rollback", name, revision]
            
            if self.server:
                cmd.extend(["--server", self.server])
            
            if self.auth_token:
                cmd.extend(["--auth-token", self.auth_token])
            
            # Rollback application
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            logger.info(f"Successfully rolled back ArgoCD application {name} to revision {revision}")
            
            return {
                "success": True,
                "application": name,
                "revision": revision,
                "output": result.stdout
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to rollback ArgoCD application: {e.stderr}")
            return {"success": False, "error": f"Failed to rollback ArgoCD application: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to rollback ArgoCD application: {str(e)}")
            return {"success": False, "error": f"Failed to rollback ArgoCD application: {str(e)}"}
    
    def list_projects(self) -> Dict[str, Any]:
        """
        List ArgoCD projects.
        
        Returns:
            Dictionary with projects
        """
        logger.info("Listing ArgoCD projects")
        
        try:
            # Build command
            cmd = [self.argocd_path, "proj", "list", "--output", "json"]
            
            if self.server:
                cmd.extend(["--server", self.server])
            
            if self.auth_token:
                cmd.extend(["--auth-token", self.auth_token])
            
            # List projects
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse JSON output
            projects = json.loads(result.stdout)
            
            logger.info(f"Successfully listed {len(projects)} ArgoCD projects")
            
            return {
                "success": True,
                "projects": projects
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to list ArgoCD projects: {e.stderr}")
            return {"success": False, "error": f"Failed to list ArgoCD projects: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to list ArgoCD projects: {str(e)}")
            return {"success": False, "error": f"Failed to list ArgoCD projects: {str(e)}"}
    
    def get_project(self, name: str) -> Dict[str, Any]:
        """
        Get information about an ArgoCD project.
        
        Args:
            name: Name of the project
            
        Returns:
            Dictionary with project information
        """
        logger.info(f"Getting information about ArgoCD project {name}")
        
        try:
            # Build command
            cmd = [self.argocd_path, "proj", "get", name, "--output", "json"]
            
            if self.server:
                cmd.extend(["--server", self.server])
            
            if self.auth_token:
                cmd.extend(["--auth-token", self.auth_token])
            
            # Get project
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse JSON output
            project = json.loads(result.stdout)
            
            logger.info(f"Successfully retrieved information about ArgoCD project {name}")
            
            return {
                "success": True,
                "project": project
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get ArgoCD project: {e.stderr}")
            return {"success": False, "error": f"Failed to get ArgoCD project: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to get ArgoCD project: {str(e)}")
            return {"success": False, "error": f"Failed to get ArgoCD project: {str(e)}"}
    
    def create_project(self, name: str, description: str = None, 
                     source_repos: List[str] = None, 
                     destinations: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Create an ArgoCD project.
        
        Args:
            name: Name of the project
            description: Description of the project
            source_repos: List of source repositories
            destinations: List of destinations
            
        Returns:
            Dictionary with creation result
        """
        logger.info(f"Creating ArgoCD project {name}")
        
        try:
            # Build command
            cmd = [self.argocd_path, "proj", "create", name]
            
            if self.server:
                cmd.extend(["--server", self.server])
            
            if self.auth_token:
                cmd.extend(["--auth-token", self.auth_token])
            
            if description:
                cmd.extend(["--description", description])
            
            if source_repos:
                for repo in source_repos:
                    cmd.extend(["--source-repo", repo])
            
            if destinations:
                for dest in destinations:
                    cmd.extend(["--dest", f"{dest['server']},{dest['namespace']}"])
            
            # Create project
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            logger.info(f"Successfully created ArgoCD project {name}")
            
            return {
                "success": True,
                "project": name,
                "output": result.stdout
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create ArgoCD project: {e.stderr}")
            return {"success": False, "error": f"Failed to create ArgoCD project: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to create ArgoCD project: {str(e)}")
            return {"success": False, "error": f"Failed to create ArgoCD project: {str(e)}"}
    
    def delete_project(self, name: str) -> Dict[str, Any]:
        """
        Delete an ArgoCD project.
        
        Args:
            name: Name of the project
            
        Returns:
            Dictionary with deletion result
        """
        logger.info(f"Deleting ArgoCD project {name}")
        
        try:
            # Build command
            cmd = [self.argocd_path, "proj", "delete", name, "--yes"]
            
            if self.server:
                cmd.extend(["--server", self.server])
            
            if self.auth_token:
                cmd.extend(["--auth-token", self.auth_token])
            
            # Delete project
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            logger.info(f"Successfully deleted ArgoCD project {name}")
            
            return {
                "success": True,
                "project": name,
                "output": result.stdout
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to delete ArgoCD project: {e.stderr}")
            return {"success": False, "error": f"Failed to delete ArgoCD project: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to delete ArgoCD project: {str(e)}")
            return {"success": False, "error": f"Failed to delete ArgoCD project: {str(e)}"}
    
    def list_repositories(self) -> Dict[str, Any]:
        """
        List ArgoCD repositories.
        
        Returns:
            Dictionary with repositories
        """
        logger.info("Listing ArgoCD repositories")
        
        try:
            # Build command
            cmd = [self.argocd_path, "repo", "list", "--output", "json"]
            
            if self.server:
                cmd.extend(["--server", self.server])
            
            if self.auth_token:
                cmd.extend(["--auth-token", self.auth_token])
            
            # List repositories
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse JSON output
            repositories = json.loads(result.stdout)
            
            logger.info(f"Successfully listed {len(repositories)} ArgoCD repositories")
            
            return {
                "success": True,
                "repositories": repositories
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to list ArgoCD repositories: {e.stderr}")
            return {"success": False, "error": f"Failed to list ArgoCD repositories: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to list ArgoCD repositories: {str(e)}")
            return {"success": False, "error": f"Failed to list ArgoCD repositories: {str(e)}"}
    
    def add_repository(self, repo: str, username: str = None, password: str = None, 
                     ssh_private_key: str = None, insecure: bool = False) -> Dict[str, Any]:
        """
        Add an ArgoCD repository.
        
        Args:
            repo: Repository URL
            username: Username for authentication
            password: Password for authentication
            ssh_private_key: SSH private key for authentication
            insecure: Whether to skip TLS verification
            
        Returns:
            Dictionary with addition result
        """
        logger.info(f"Adding ArgoCD repository {repo}")
        
        try:
            # Build command
            cmd = [self.argocd_path, "repo", "add", repo]
            
            if self.server:
                cmd.extend(["--server", self.server])
            
            if self.auth_token:
                cmd.extend(["--auth-token", self.auth_token])
            
            if username:
                cmd.extend(["--username", username])
            
            if password:
                cmd.extend(["--password", password])
            
            if ssh_private_key:
                cmd.extend(["--ssh-private-key", ssh_private_key])
            
            if insecure:
                cmd.append("--insecure")
            
            # Add repository
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            logger.info(f"Successfully added ArgoCD repository {repo}")
            
            return {
                "success": True,
                "repository": repo,
                "output": result.stdout
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to add ArgoCD repository: {e.stderr}")
            return {"success": False, "error": f"Failed to add ArgoCD repository: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to add ArgoCD repository: {str(e)}")
            return {"success": False, "error": f"Failed to add ArgoCD repository: {str(e)}"}
    
    def remove_repository(self, repo: str) -> Dict[str, Any]:
        """
        Remove an ArgoCD repository.
        
        Args:
            repo: Repository URL
            
        Returns:
            Dictionary with removal result
        """
        logger.info(f"Removing ArgoCD repository {repo}")
        
        try:
            # Build command
            cmd = [self.argocd_path, "repo", "rm", repo]
            
            if self.server:
                cmd.extend(["--server", self.server])
            
            if self.auth_token:
                cmd.extend(["--auth-token", self.auth_token])
            
            # Remove repository
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            logger.info(f"Successfully removed ArgoCD repository {repo}")
            
            return {
                "success": True,
                "repository": repo,
                "output": result.stdout
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to remove ArgoCD repository: {e.stderr}")
            return {"success": False, "error": f"Failed to remove ArgoCD repository: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to remove ArgoCD repository: {str(e)}")
            return {"success": False, "error": f"Failed to remove ArgoCD repository: {str(e)}"}
    
    def list_clusters(self) -> Dict[str, Any]:
        """
        List ArgoCD clusters.
        
        Returns:
            Dictionary with clusters
        """
        logger.info("Listing ArgoCD clusters")
        
        try:
            # Build command
            cmd = [self.argocd_path, "cluster", "list", "--output", "json"]
            
            if self.server:
                cmd.extend(["--server", self.server])
            
            if self.auth_token:
                cmd.extend(["--auth-token", self.auth_token])
            
            # List clusters
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse JSON output
            clusters = json.loads(result.stdout)
            
            logger.info(f"Successfully listed {len(clusters)} ArgoCD clusters")
            
            return {
                "success": True,
                "clusters": clusters
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to list ArgoCD clusters: {e.stderr}")
            return {"success": False, "error": f"Failed to list ArgoCD clusters: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to list ArgoCD clusters: {str(e)}")
            return {"success": False, "error": f"Failed to list ArgoCD clusters: {str(e)}"}
    
    def add_cluster(self, name: str, server: str, context: str = None) -> Dict[str, Any]:
        """
        Add an ArgoCD cluster.
        
        Args:
            name: Name of the cluster
            server: Server URL
            context: Kubernetes context
            
        Returns:
            Dictionary with addition result
        """
        logger.info(f"Adding ArgoCD cluster {name}")
        
        try:
            # Build command
            cmd = [self.argocd_path, "cluster", "add"]
            
            if context:
                cmd.append(context)
            else:
                cmd.append(name)
            
            if self.server:
                cmd.extend(["--server", self.server])
            
            if self.auth_token:
                cmd.extend(["--auth-token", self.auth_token])
            
            # Add cluster
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            logger.info(f"Successfully added ArgoCD cluster {name}")
            
            return {
                "success": True,
                "cluster": name,
                "output": result.stdout
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to add ArgoCD cluster: {e.stderr}")
            return {"success": False, "error": f"Failed to add ArgoCD cluster: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to add ArgoCD cluster: {str(e)}")
            return {"success": False, "error": f"Failed to add ArgoCD cluster: {str(e)}"}
    
    def remove_cluster(self, name: str) -> Dict[str, Any]:
        """
        Remove an ArgoCD cluster.
        
        Args:
            name: Name of the cluster
            
        Returns:
            Dictionary with removal result
        """
        logger.info(f"Removing ArgoCD cluster {name}")
        
        try:
            # Build command
            cmd = [self.argocd_path, "cluster", "rm", name]
            
            if self.server:
                cmd.extend(["--server", self.server])
            
            if self.auth_token:
                cmd.extend(["--auth-token", self.auth_token])
            
            # Remove cluster
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            logger.info(f"Successfully removed ArgoCD cluster {name}")
            
            return {
                "success": True,
                "cluster": name,
                "output": result.stdout
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to remove ArgoCD cluster: {e.stderr}")
            return {"success": False, "error": f"Failed to remove ArgoCD cluster: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to remove ArgoCD cluster: {str(e)}")
            return {"success": False, "error": f"Failed to remove ArgoCD cluster: {str(e)}"}
