"""
ArgoCD Integration Manager

This module provides integration with ArgoCD for GitOps-based continuous delivery
in the Deployment Operations Layer. It handles application management, sync operations,
and ArgoCD project configuration.

Classes:
    ArgoCDIntegrationManager: Manages ArgoCD integration
    ArgoCDApplicationManager: Manages ArgoCD applications
    ArgoCDProjectManager: Manages ArgoCD projects
    ArgoCDExecutor: Executes ArgoCD CLI commands
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

class ArgoCDIntegrationManager:
    """
    Manages ArgoCD integration for the Deployment Operations Layer.
    
    This class provides a unified interface for interacting with ArgoCD,
    handling application management, sync operations, and project configuration.
    """
    
    def __init__(self, argocd_binary_path: Optional[str] = None, 
                working_dir: Optional[str] = None):
        """
        Initialize the ArgoCD Integration Manager.
        
        Args:
            argocd_binary_path: Path to ArgoCD binary (optional, defaults to 'argocd' in PATH)
            working_dir: Working directory for ArgoCD operations (optional)
        """
        self.argocd_binary = argocd_binary_path or "argocd"
        self.working_dir = working_dir or tempfile.mkdtemp(prefix="argocd_")
        
        self.executor = ArgoCDExecutor(self.argocd_binary, self.working_dir)
        self.application_manager = ArgoCDApplicationManager(self.executor)
        self.project_manager = ArgoCDProjectManager(self.executor)
        
        # Verify ArgoCD installation
        self._verify_argocd_installation()
    
    def _verify_argocd_installation(self):
        """
        Verify that ArgoCD is installed and available.
        
        Logs a warning if ArgoCD is not installed but does not raise an exception
        as ArgoCD may be accessed via API or other means.
        """
        try:
            version = self.executor.run_command(["version", "--client"], check=False)
            logger.info(f"ArgoCD client version: {version}")
        except Exception as e:
            logger.warning(f"ArgoCD client not installed or not accessible: {str(e)}")
    
    def login(self, server: str, username: str, password: str, 
             insecure: bool = False) -> AgentResponse:
        """
        Log in to an ArgoCD server.
        
        Args:
            server: ArgoCD server URL
            username: Username
            password: Password
            insecure: Whether to skip TLS verification
            
        Returns:
            AgentResponse: Login response
        """
        try:
            args = ["login", server, "--username", username, "--password", password]
            
            if insecure:
                args.append("--insecure")
            
            output = self.executor.run_command(args)
            
            return AgentResponse(
                success=True,
                message=f"Logged in to ArgoCD server {server}",
                data={
                    "server": server,
                    "output": output
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to log in to ArgoCD server: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to log in to ArgoCD server: {str(e)}",
                data={}
            )
    
    def create_application(self, name: str, repo_url: str, path: str, 
                          dest_server: str, dest_namespace: str,
                          project: str = "default",
                          sync_policy: Optional[str] = None,
                          auto_prune: bool = False,
                          self_heal: bool = False) -> AgentResponse:
        """
        Create an ArgoCD application.
        
        Args:
            name: Application name
            repo_url: Git repository URL
            path: Path in the repository
            dest_server: Destination server
            dest_namespace: Destination namespace
            project: ArgoCD project (default: "default")
            sync_policy: Sync policy (optional)
            auto_prune: Whether to automatically prune resources
            self_heal: Whether to automatically heal resources
            
        Returns:
            AgentResponse: Application creation response
        """
        try:
            result = self.application_manager.create_application(
                name=name,
                repo_url=repo_url,
                path=path,
                dest_server=dest_server,
                dest_namespace=dest_namespace,
                project=project,
                sync_policy=sync_policy,
                auto_prune=auto_prune,
                self_heal=self_heal
            )
            
            return AgentResponse(
                success=True,
                message=f"ArgoCD application {name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create ArgoCD application: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create ArgoCD application: {str(e)}",
                data={}
            )
    
    def sync_application(self, name: str, prune: bool = False, 
                        dry_run: bool = False) -> AgentResponse:
        """
        Sync an ArgoCD application.
        
        Args:
            name: Application name
            prune: Whether to prune resources
            dry_run: Whether to perform a dry run
            
        Returns:
            AgentResponse: Sync response
        """
        try:
            result = self.application_manager.sync_application(
                name=name,
                prune=prune,
                dry_run=dry_run
            )
            
            return AgentResponse(
                success=True,
                message=f"ArgoCD application {name} synced successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to sync ArgoCD application: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to sync ArgoCD application: {str(e)}",
                data={}
            )
    
    def get_application_status(self, name: str) -> AgentResponse:
        """
        Get the status of an ArgoCD application.
        
        Args:
            name: Application name
            
        Returns:
            AgentResponse: Application status response
        """
        try:
            result = self.application_manager.get_application_status(name)
            
            return AgentResponse(
                success=True,
                message=f"Retrieved status for ArgoCD application {name}",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to get ArgoCD application status: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to get ArgoCD application status: {str(e)}",
                data={}
            )
    
    def delete_application(self, name: str, cascade: bool = True) -> AgentResponse:
        """
        Delete an ArgoCD application.
        
        Args:
            name: Application name
            cascade: Whether to cascade the deletion to resources
            
        Returns:
            AgentResponse: Deletion response
        """
        try:
            result = self.application_manager.delete_application(
                name=name,
                cascade=cascade
            )
            
            return AgentResponse(
                success=True,
                message=f"ArgoCD application {name} deleted successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to delete ArgoCD application: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to delete ArgoCD application: {str(e)}",
                data={}
            )
    
    def create_project(self, name: str, description: str, 
                      source_repos: List[str], 
                      destinations: List[Dict[str, str]]) -> AgentResponse:
        """
        Create an ArgoCD project.
        
        Args:
            name: Project name
            description: Project description
            source_repos: List of source repositories
            destinations: List of destinations (server and namespace)
            
        Returns:
            AgentResponse: Project creation response
        """
        try:
            result = self.project_manager.create_project(
                name=name,
                description=description,
                source_repos=source_repos,
                destinations=destinations
            )
            
            return AgentResponse(
                success=True,
                message=f"ArgoCD project {name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create ArgoCD project: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create ArgoCD project: {str(e)}",
                data={}
            )
    
    def delete_project(self, name: str) -> AgentResponse:
        """
        Delete an ArgoCD project.
        
        Args:
            name: Project name
            
        Returns:
            AgentResponse: Deletion response
        """
        try:
            result = self.project_manager.delete_project(name)
            
            return AgentResponse(
                success=True,
                message=f"ArgoCD project {name} deleted successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to delete ArgoCD project: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to delete ArgoCD project: {str(e)}",
                data={}
            )
    
    def list_applications(self) -> AgentResponse:
        """
        List all ArgoCD applications.
        
        Returns:
            AgentResponse: Application list response
        """
        try:
            result = self.application_manager.list_applications()
            
            return AgentResponse(
                success=True,
                message=f"Found {len(result)} ArgoCD applications",
                data={
                    "applications": result
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to list ArgoCD applications: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to list ArgoCD applications: {str(e)}",
                data={}
            )
    
    def list_projects(self) -> AgentResponse:
        """
        List all ArgoCD projects.
        
        Returns:
            AgentResponse: Project list response
        """
        try:
            result = self.project_manager.list_projects()
            
            return AgentResponse(
                success=True,
                message=f"Found {len(result)} ArgoCD projects",
                data={
                    "projects": result
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to list ArgoCD projects: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to list ArgoCD projects: {str(e)}",
                data={}
            )
    
    def to_mcp_context(self) -> MCPContext:
        """
        Convert ArgoCD integration information to MCP context.
        
        Returns:
            MCPContext: MCP context with ArgoCD integration information
        """
        return MCPContext(
            context_type="argocd_integration",
            argocd_version=self._get_argocd_version(),
            working_dir=self.working_dir
        )
    
    def _get_argocd_version(self) -> str:
        """
        Get the ArgoCD version.
        
        Returns:
            str: ArgoCD version
        """
        try:
            version_output = self.executor.run_command(["version", "--client"], check=False)
            # Extract version number from output
            if "argocd: " in version_output:
                version_line = [line for line in version_output.split("\n") if "argocd: " in line][0]
                return version_line.split("argocd: ")[1].strip()
            else:
                return version_output.strip()
        except Exception as e:
            logger.error(f"Failed to get ArgoCD version: {str(e)}")
            return "unknown"


class ArgoCDApplicationManager:
    """
    Manages ArgoCD applications.
    
    This class provides methods for managing ArgoCD applications,
    including creation, deletion, and sync operations.
    """
    
    def __init__(self, executor: 'ArgoCDExecutor'):
        """
        Initialize the ArgoCD Application Manager.
        
        Args:
            executor: ArgoCD executor
        """
        self.executor = executor
    
    def create_application(self, name: str, repo_url: str, path: str, 
                          dest_server: str, dest_namespace: str,
                          project: str = "default",
                          sync_policy: Optional[str] = None,
                          auto_prune: bool = False,
                          self_heal: bool = False) -> Dict[str, Any]:
        """
        Create an ArgoCD application.
        
        Args:
            name: Application name
            repo_url: Git repository URL
            path: Path in the repository
            dest_server: Destination server
            dest_namespace: Destination namespace
            project: ArgoCD project (default: "default")
            sync_policy: Sync policy (optional)
            auto_prune: Whether to automatically prune resources
            self_heal: Whether to automatically heal resources
            
        Returns:
            Dict[str, Any]: Application creation result
        """
        args = [
            "app", "create", name,
            "--repo", repo_url,
            "--path", path,
            "--dest-server", dest_server,
            "--dest-namespace", dest_namespace,
            "--project", project
        ]
        
        if sync_policy:
            args.extend(["--sync-policy", sync_policy])
        
        if auto_prune:
            args.append("--auto-prune")
        
        if self_heal:
            args.append("--self-heal")
        
        output = self.executor.run_command(args)
        
        return {
            "name": name,
            "repo_url": repo_url,
            "path": path,
            "dest_server": dest_server,
            "dest_namespace": dest_namespace,
            "project": project,
            "sync_policy": sync_policy,
            "auto_prune": auto_prune,
            "self_heal": self_heal,
            "output": output
        }
    
    def sync_application(self, name: str, prune: bool = False, 
                        dry_run: bool = False) -> Dict[str, Any]:
        """
        Sync an ArgoCD application.
        
        Args:
            name: Application name
            prune: Whether to prune resources
            dry_run: Whether to perform a dry run
            
        Returns:
            Dict[str, Any]: Sync result
        """
        args = ["app", "sync", name]
        
        if prune:
            args.append("--prune")
        
        if dry_run:
            args.append("--dry-run")
        
        output = self.executor.run_command(args)
        
        return {
            "name": name,
            "prune": prune,
            "dry_run": dry_run,
            "output": output
        }
    
    def get_application_status(self, name: str) -> Dict[str, Any]:
        """
        Get the status of an ArgoCD application.
        
        Args:
            name: Application name
            
        Returns:
            Dict[str, Any]: Application status
        """
        output = self.executor.run_command(["app", "get", name, "-o", "json"])
        
        try:
            app_json = json.loads(output)
            
            return {
                "name": app_json["metadata"]["name"],
                "project": app_json["spec"]["project"],
                "sync_status": app_json["status"]["sync"]["status"],
                "health_status": app_json["status"]["health"]["status"],
                "repo_url": app_json["spec"]["source"]["repoURL"],
                "path": app_json["spec"]["source"]["path"],
                "dest_server": app_json["spec"]["destination"]["server"],
                "dest_namespace": app_json["spec"]["destination"]["namespace"],
                "resources": app_json["status"].get("resources", [])
            }
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse application status: {str(e)}")
            return {"name": name, "output": output, "error": str(e)}
    
    def delete_application(self, name: str, cascade: bool = True) -> Dict[str, Any]:
        """
        Delete an ArgoCD application.
        
        Args:
            name: Application name
            cascade: Whether to cascade the deletion to resources
            
        Returns:
            Dict[str, Any]: Deletion result
        """
        args = ["app", "delete", name, "--yes"]
        
        if not cascade:
            args.append("--cascade=false")
        
        output = self.executor.run_command(args)
        
        return {
            "name": name,
            "cascade": cascade,
            "output": output
        }
    
    def list_applications(self) -> List[Dict[str, Any]]:
        """
        List all ArgoCD applications.
        
        Returns:
            List[Dict[str, Any]]: List of applications
        """
        output = self.executor.run_command(["app", "list", "-o", "json"])
        
        try:
            apps_json = json.loads(output)
            
            applications = []
            for app in apps_json:
                application = {
                    "name": app["metadata"]["name"],
                    "project": app["spec"]["project"],
                    "sync_status": app["status"]["sync"]["status"],
                    "health_status": app["status"]["health"]["status"],
                    "repo_url": app["spec"]["source"]["repoURL"],
                    "path": app["spec"]["source"]["path"],
                    "dest_server": app["spec"]["destination"]["server"],
                    "dest_namespace": app["spec"]["destination"]["namespace"]
                }
                applications.append(application)
            
            return applications
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse application list: {str(e)}")
            return []


class ArgoCDProjectManager:
    """
    Manages ArgoCD projects.
    
    This class provides methods for managing ArgoCD projects,
    including creation, deletion, and configuration.
    """
    
    def __init__(self, executor: 'ArgoCDExecutor'):
        """
        Initialize the ArgoCD Project Manager.
        
        Args:
            executor: ArgoCD executor
        """
        self.executor = executor
    
    def create_project(self, name: str, description: str, 
                      source_repos: List[str], 
                      destinations: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Create an ArgoCD project.
        
        Args:
            name: Project name
            description: Project description
            source_repos: List of source repositories
            destinations: List of destinations (server and namespace)
            
        Returns:
            Dict[str, Any]: Project creation result
        """
        args = ["proj", "create", name, "--description", description]
        
        for repo in source_repos:
            args.extend(["--source-repo", repo])
        
        for dest in destinations:
            server = dest.get("server", "*")
            namespace = dest.get("namespace", "*")
            args.extend(["--dest", f"{server},{namespace}"])
        
        output = self.executor.run_command(args)
        
        return {
            "name": name,
            "description": description,
            "source_repos": source_repos,
            "destinations": destinations,
            "output": output
        }
    
    def delete_project(self, name: str) -> Dict[str, Any]:
        """
        Delete an ArgoCD project.
        
        Args:
            name: Project name
            
        Returns:
            Dict[str, Any]: Deletion result
        """
        output = self.executor.run_command(["proj", "delete", name, "--yes"])
        
        return {
            "name": name,
            "output": output
        }
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """
        List all ArgoCD projects.
        
        Returns:
            List[Dict[str, Any]]: List of projects
        """
        output = self.executor.run_command(["proj", "list", "-o", "json"])
        
        try:
            projects_json = json.loads(output)
            
            projects = []
            for proj in projects_json:
                project = {
                    "name": proj["metadata"]["name"],
                    "description": proj["spec"].get("description", ""),
                    "source_repos": proj["spec"].get("sourceRepos", []),
                    "destinations": proj["spec"].get("destinations", [])
                }
                projects.append(project)
            
            return projects
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse project list: {str(e)}")
            return []


class ArgoCDExecutor:
    """
    Executes ArgoCD CLI commands.
    
    This class provides methods for executing ArgoCD CLI commands and handling their output.
    """
    
    def __init__(self, argocd_binary: str, working_dir: str):
        """
        Initialize the ArgoCD Executor.
        
        Args:
            argocd_binary: Path to ArgoCD binary
            working_dir: Working directory for ArgoCD operations
        """
        self.argocd_binary = argocd_binary
        self.working_dir = working_dir
    
    def run_command(self, args: List[str], check: bool = True) -> str:
        """
        Run an ArgoCD command.
        
        Args:
            args: Command arguments
            check: Whether to check for command success
            
        Returns:
            str: Command output
            
        Raises:
            Exception: If the command fails and check is True
        """
        cmd = [self.argocd_binary] + args
        logger.info(f"Running ArgoCD command: {' '.join(cmd)}")
        
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
            error_message = f"ArgoCD command failed: {e.stderr}"
            logger.error(error_message)
            
            if check:
                raise Exception(error_message)
            
            return e.stderr
"""
