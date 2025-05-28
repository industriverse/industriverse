"""
CI/CD Integration Manager

This module provides integration with CI/CD systems for the Deployment Operations Layer.
It handles CI/CD pipeline management, build triggers, and deployment automation.

Classes:
    CICDIntegrationManager: Manages CI/CD system integrations
    JenkinsIntegration: Integration with Jenkins CI/CD
    GitHubActionsIntegration: Integration with GitHub Actions
    GitLabCIIntegration: Integration with GitLab CI/CD
    AzureDevOpsIntegration: Integration with Azure DevOps
"""

import json
import logging
import os
import requests
import time
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin

from ..agent.agent_utils import AgentResponse
from ..protocol.mcp_integration.mcp_context_schema import MCPContext

logger = logging.getLogger(__name__)

class CICDIntegrationManager:
    """
    Manages CI/CD system integrations for the Deployment Operations Layer.
    
    This class provides a unified interface for interacting with multiple CI/CD systems,
    handling pipeline management, build triggers, and deployment automation.
    """
    
    def __init__(self):
        """
        Initialize the CI/CD Integration Manager.
        """
        self.integrations = {}
        self.default_integration = None
    
    def register_jenkins_integration(self, integration_id: str, url: str, 
                                    username: str, api_token: str,
                                    is_default: bool = False) -> bool:
        """
        Register a Jenkins CI/CD integration.
        
        Args:
            integration_id: Unique identifier for the integration
            url: Jenkins server URL
            username: Jenkins username
            api_token: Jenkins API token
            is_default: Whether this integration should be the default
            
        Returns:
            bool: True if registration was successful, False otherwise
        """
        try:
            integration = JenkinsIntegration(url, username, api_token)
            
            # Validate connection
            if not integration.validate_connection():
                logger.error(f"Failed to validate Jenkins connection for integration {integration_id}")
                return False
            
            self.integrations[integration_id] = integration
            
            if is_default or not self.default_integration:
                self.default_integration = integration_id
                
            return True
        
        except Exception as e:
            logger.error(f"Failed to register Jenkins integration {integration_id}: {str(e)}")
            return False
    
    def register_github_actions_integration(self, integration_id: str, 
                                           repo_owner: str, repo_name: str,
                                           token: str, is_default: bool = False) -> bool:
        """
        Register a GitHub Actions integration.
        
        Args:
            integration_id: Unique identifier for the integration
            repo_owner: GitHub repository owner
            repo_name: GitHub repository name
            token: GitHub personal access token
            is_default: Whether this integration should be the default
            
        Returns:
            bool: True if registration was successful, False otherwise
        """
        try:
            integration = GitHubActionsIntegration(repo_owner, repo_name, token)
            
            # Validate connection
            if not integration.validate_connection():
                logger.error(f"Failed to validate GitHub Actions connection for integration {integration_id}")
                return False
            
            self.integrations[integration_id] = integration
            
            if is_default or not self.default_integration:
                self.default_integration = integration_id
                
            return True
        
        except Exception as e:
            logger.error(f"Failed to register GitHub Actions integration {integration_id}: {str(e)}")
            return False
    
    def register_gitlab_ci_integration(self, integration_id: str, 
                                      gitlab_url: str, project_id: str,
                                      token: str, is_default: bool = False) -> bool:
        """
        Register a GitLab CI integration.
        
        Args:
            integration_id: Unique identifier for the integration
            gitlab_url: GitLab server URL
            project_id: GitLab project ID
            token: GitLab personal access token
            is_default: Whether this integration should be the default
            
        Returns:
            bool: True if registration was successful, False otherwise
        """
        try:
            integration = GitLabCIIntegration(gitlab_url, project_id, token)
            
            # Validate connection
            if not integration.validate_connection():
                logger.error(f"Failed to validate GitLab CI connection for integration {integration_id}")
                return False
            
            self.integrations[integration_id] = integration
            
            if is_default or not self.default_integration:
                self.default_integration = integration_id
                
            return True
        
        except Exception as e:
            logger.error(f"Failed to register GitLab CI integration {integration_id}: {str(e)}")
            return False
    
    def register_azure_devops_integration(self, integration_id: str, 
                                         organization: str, project: str,
                                         token: str, is_default: bool = False) -> bool:
        """
        Register an Azure DevOps integration.
        
        Args:
            integration_id: Unique identifier for the integration
            organization: Azure DevOps organization name
            project: Azure DevOps project name
            token: Azure DevOps personal access token
            is_default: Whether this integration should be the default
            
        Returns:
            bool: True if registration was successful, False otherwise
        """
        try:
            integration = AzureDevOpsIntegration(organization, project, token)
            
            # Validate connection
            if not integration.validate_connection():
                logger.error(f"Failed to validate Azure DevOps connection for integration {integration_id}")
                return False
            
            self.integrations[integration_id] = integration
            
            if is_default or not self.default_integration:
                self.default_integration = integration_id
                
            return True
        
        except Exception as e:
            logger.error(f"Failed to register Azure DevOps integration {integration_id}: {str(e)}")
            return False
    
    def get_integration(self, integration_id: Optional[str] = None):
        """
        Get a registered integration.
        
        Args:
            integration_id: Integration identifier (optional, uses default if not specified)
            
        Returns:
            Integration object or None if not found
        """
        if not integration_id:
            if not self.default_integration:
                logger.error("No default integration set")
                return None
            integration_id = self.default_integration
            
        if integration_id not in self.integrations:
            logger.error(f"Integration {integration_id} not found")
            return None
            
        return self.integrations[integration_id]
    
    def list_integrations(self) -> List[Dict[str, Any]]:
        """
        List all registered integrations.
        
        Returns:
            List[Dict[str, Any]]: List of integration details
        """
        return [
            {
                "id": integration_id,
                "type": self._get_integration_type(integration),
                "is_default": integration_id == self.default_integration
            }
            for integration_id, integration in self.integrations.items()
        ]
    
    def _get_integration_type(self, integration) -> str:
        """
        Get the type of an integration.
        
        Args:
            integration: Integration object
            
        Returns:
            str: Integration type
        """
        if isinstance(integration, JenkinsIntegration):
            return "jenkins"
        elif isinstance(integration, GitHubActionsIntegration):
            return "github_actions"
        elif isinstance(integration, GitLabCIIntegration):
            return "gitlab_ci"
        elif isinstance(integration, AzureDevOpsIntegration):
            return "azure_devops"
        else:
            return "unknown"
    
    def set_default_integration(self, integration_id: str) -> bool:
        """
        Set the default integration.
        
        Args:
            integration_id: Integration identifier
            
        Returns:
            bool: True if successful, False otherwise
        """
        if integration_id not in self.integrations:
            logger.error(f"Integration {integration_id} not found")
            return False
            
        self.default_integration = integration_id
        return True
    
    def unregister_integration(self, integration_id: str) -> bool:
        """
        Unregister an integration.
        
        Args:
            integration_id: Integration identifier
            
        Returns:
            bool: True if successful, False otherwise
        """
        if integration_id not in self.integrations:
            logger.error(f"Integration {integration_id} not found")
            return False
            
        del self.integrations[integration_id]
        
        if self.default_integration == integration_id:
            self.default_integration = next(iter(self.integrations)) if self.integrations else None
            
        return True
    
    def trigger_pipeline(self, integration_id: Optional[str], pipeline_id: str, 
                        parameters: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Trigger a CI/CD pipeline.
        
        Args:
            integration_id: Integration identifier (optional, uses default if not specified)
            pipeline_id: Pipeline identifier
            parameters: Pipeline parameters (optional)
            
        Returns:
            AgentResponse: Pipeline trigger response
        """
        integration = self.get_integration(integration_id)
        
        if not integration:
            return AgentResponse(
                success=False,
                message=f"Integration not found",
                data={}
            )
            
        try:
            result = integration.trigger_pipeline(pipeline_id, parameters)
            
            return AgentResponse(
                success=True,
                message=f"Successfully triggered pipeline {pipeline_id}",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to trigger pipeline: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to trigger pipeline: {str(e)}",
                data={}
            )
    
    def get_pipeline_status(self, integration_id: Optional[str], pipeline_id: str, 
                           build_id: str) -> AgentResponse:
        """
        Get the status of a pipeline build.
        
        Args:
            integration_id: Integration identifier (optional, uses default if not specified)
            pipeline_id: Pipeline identifier
            build_id: Build identifier
            
        Returns:
            AgentResponse: Pipeline status response
        """
        integration = self.get_integration(integration_id)
        
        if not integration:
            return AgentResponse(
                success=False,
                message=f"Integration not found",
                data={}
            )
            
        try:
            status = integration.get_pipeline_status(pipeline_id, build_id)
            
            return AgentResponse(
                success=True,
                message=f"Successfully retrieved pipeline status",
                data=status
            )
        
        except Exception as e:
            logger.error(f"Failed to get pipeline status: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to get pipeline status: {str(e)}",
                data={}
            )
    
    def wait_for_pipeline_completion(self, integration_id: Optional[str], pipeline_id: str, 
                                    build_id: str, timeout_seconds: int = 3600) -> AgentResponse:
        """
        Wait for a pipeline build to complete.
        
        Args:
            integration_id: Integration identifier (optional, uses default if not specified)
            pipeline_id: Pipeline identifier
            build_id: Build identifier
            timeout_seconds: Maximum time to wait in seconds (default: 1 hour)
            
        Returns:
            AgentResponse: Pipeline completion response
        """
        integration = self.get_integration(integration_id)
        
        if not integration:
            return AgentResponse(
                success=False,
                message=f"Integration not found",
                data={}
            )
            
        try:
            start_time = time.time()
            poll_interval = 30  # seconds
            
            while True:
                status = integration.get_pipeline_status(pipeline_id, build_id)
                
                if status["status"] in ["SUCCESS", "FAILURE", "ABORTED", "CANCELLED", "COMPLETED", "FAILED"]:
                    return AgentResponse(
                        success=status["status"] in ["SUCCESS", "COMPLETED"],
                        message=f"Pipeline completed with status: {status['status']}",
                        data=status
                    )
                
                elapsed_time = time.time() - start_time
                if elapsed_time > timeout_seconds:
                    return AgentResponse(
                        success=False,
                        message=f"Pipeline timed out after {timeout_seconds} seconds",
                        data=status
                    )
                
                time.sleep(poll_interval)
        
        except Exception as e:
            logger.error(f"Failed to wait for pipeline completion: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to wait for pipeline completion: {str(e)}",
                data={}
            )
    
    def get_pipeline_artifacts(self, integration_id: Optional[str], pipeline_id: str, 
                              build_id: str) -> AgentResponse:
        """
        Get artifacts from a pipeline build.
        
        Args:
            integration_id: Integration identifier (optional, uses default if not specified)
            pipeline_id: Pipeline identifier
            build_id: Build identifier
            
        Returns:
            AgentResponse: Pipeline artifacts response
        """
        integration = self.get_integration(integration_id)
        
        if not integration:
            return AgentResponse(
                success=False,
                message=f"Integration not found",
                data={}
            )
            
        try:
            artifacts = integration.get_pipeline_artifacts(pipeline_id, build_id)
            
            return AgentResponse(
                success=True,
                message=f"Successfully retrieved pipeline artifacts",
                data=artifacts
            )
        
        except Exception as e:
            logger.error(f"Failed to get pipeline artifacts: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to get pipeline artifacts: {str(e)}",
                data={}
            )
    
    def create_pipeline(self, integration_id: Optional[str], pipeline_config: Dict[str, Any]) -> AgentResponse:
        """
        Create a new CI/CD pipeline.
        
        Args:
            integration_id: Integration identifier (optional, uses default if not specified)
            pipeline_config: Pipeline configuration
            
        Returns:
            AgentResponse: Pipeline creation response
        """
        integration = self.get_integration(integration_id)
        
        if not integration:
            return AgentResponse(
                success=False,
                message=f"Integration not found",
                data={}
            )
            
        try:
            result = integration.create_pipeline(pipeline_config)
            
            return AgentResponse(
                success=True,
                message=f"Successfully created pipeline",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create pipeline: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create pipeline: {str(e)}",
                data={}
            )
    
    def update_pipeline(self, integration_id: Optional[str], pipeline_id: str, 
                       pipeline_config: Dict[str, Any]) -> AgentResponse:
        """
        Update an existing CI/CD pipeline.
        
        Args:
            integration_id: Integration identifier (optional, uses default if not specified)
            pipeline_id: Pipeline identifier
            pipeline_config: Pipeline configuration
            
        Returns:
            AgentResponse: Pipeline update response
        """
        integration = self.get_integration(integration_id)
        
        if not integration:
            return AgentResponse(
                success=False,
                message=f"Integration not found",
                data={}
            )
            
        try:
            result = integration.update_pipeline(pipeline_id, pipeline_config)
            
            return AgentResponse(
                success=True,
                message=f"Successfully updated pipeline {pipeline_id}",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to update pipeline: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to update pipeline: {str(e)}",
                data={}
            )
    
    def delete_pipeline(self, integration_id: Optional[str], pipeline_id: str) -> AgentResponse:
        """
        Delete a CI/CD pipeline.
        
        Args:
            integration_id: Integration identifier (optional, uses default if not specified)
            pipeline_id: Pipeline identifier
            
        Returns:
            AgentResponse: Pipeline deletion response
        """
        integration = self.get_integration(integration_id)
        
        if not integration:
            return AgentResponse(
                success=False,
                message=f"Integration not found",
                data={}
            )
            
        try:
            result = integration.delete_pipeline(pipeline_id)
            
            return AgentResponse(
                success=True,
                message=f"Successfully deleted pipeline {pipeline_id}",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to delete pipeline: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to delete pipeline: {str(e)}",
                data={}
            )
    
    def list_pipelines(self, integration_id: Optional[str]) -> AgentResponse:
        """
        List all pipelines for an integration.
        
        Args:
            integration_id: Integration identifier (optional, uses default if not specified)
            
        Returns:
            AgentResponse: Pipeline list response
        """
        integration = self.get_integration(integration_id)
        
        if not integration:
            return AgentResponse(
                success=False,
                message=f"Integration not found",
                data={}
            )
            
        try:
            pipelines = integration.list_pipelines()
            
            return AgentResponse(
                success=True,
                message=f"Successfully listed pipelines",
                data=pipelines
            )
        
        except Exception as e:
            logger.error(f"Failed to list pipelines: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to list pipelines: {str(e)}",
                data={}
            )


class JenkinsIntegration:
    """
    Integration with Jenkins CI/CD.
    
    This class provides methods for interacting with Jenkins CI/CD,
    including pipeline management, build triggers, and artifact retrieval.
    """
    
    def __init__(self, url: str, username: str, api_token: str):
        """
        Initialize the Jenkins integration.
        
        Args:
            url: Jenkins server URL
            username: Jenkins username
            api_token: Jenkins API token
        """
        self.url = url.rstrip('/')
        self.username = username
        self.api_token = api_token
        self.auth = (username, api_token)
    
    def validate_connection(self) -> bool:
        """
        Validate the Jenkins connection.
        
        Returns:
            bool: True if connection is valid, False otherwise
        """
        try:
            response = requests.get(
                f"{self.url}/api/json",
                auth=self.auth
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to validate Jenkins connection: {str(e)}")
            return False
    
    def trigger_pipeline(self, pipeline_id: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Trigger a Jenkins pipeline.
        
        Args:
            pipeline_id: Pipeline job name
            parameters: Build parameters (optional)
            
        Returns:
            Dict[str, Any]: Build information
        """
        url = f"{self.url}/job/{pipeline_id}/buildWithParameters" if parameters else f"{self.url}/job/{pipeline_id}/build"
        
        response = requests.post(
            url,
            auth=self.auth,
            params=parameters
        )
        
        if response.status_code not in [200, 201]:
            raise Exception(f"Failed to trigger Jenkins pipeline: {response.text}")
        
        # Get the queue item URL from the Location header
        queue_url = response.headers.get('Location')
        
        # Wait for the build to start
        build_number = self._wait_for_build_to_start(queue_url)
        
        return {
            "pipeline_id": pipeline_id,
            "build_id": str(build_number),
            "url": f"{self.url}/job/{pipeline_id}/{build_number}"
        }
    
    def _wait_for_build_to_start(self, queue_url: str, timeout_seconds: int = 60) -> int:
        """
        Wait for a queued build to start.
        
        Args:
            queue_url: Queue item URL
            timeout_seconds: Maximum time to wait in seconds
            
        Returns:
            int: Build number
        """
        start_time = time.time()
        
        while True:
            response = requests.get(
                f"{queue_url}/api/json",
                auth=self.auth
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to get queue item: {response.text}")
            
            data = response.json()
            
            if "executable" in data and "number" in data["executable"]:
                return data["executable"]["number"]
            
            elapsed_time = time.time() - start_time
            if elapsed_time > timeout_seconds:
                raise Exception(f"Timed out waiting for build to start after {timeout_seconds} seconds")
            
            time.sleep(2)
    
    def get_pipeline_status(self, pipeline_id: str, build_id: str) -> Dict[str, Any]:
        """
        Get the status of a Jenkins pipeline build.
        
        Args:
            pipeline_id: Pipeline job name
            build_id: Build number
            
        Returns:
            Dict[str, Any]: Build status information
        """
        response = requests.get(
            f"{self.url}/job/{pipeline_id}/{build_id}/api/json",
            auth=self.auth
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get Jenkins build status: {response.text}")
        
        data = response.json()
        
        return {
            "pipeline_id": pipeline_id,
            "build_id": build_id,
            "status": "SUCCESS" if data["result"] == "SUCCESS" else 
                     "FAILURE" if data["result"] == "FAILURE" else 
                     "ABORTED" if data["result"] == "ABORTED" else 
                     "IN_PROGRESS" if data["building"] else "UNKNOWN",
            "url": data["url"],
            "timestamp": data["timestamp"],
            "duration": data["duration"]
        }
    
    def get_pipeline_artifacts(self, pipeline_id: str, build_id: str) -> Dict[str, Any]:
        """
        Get artifacts from a Jenkins pipeline build.
        
        Args:
            pipeline_id: Pipeline job name
            build_id: Build number
            
        Returns:
            Dict[str, Any]: Build artifacts information
        """
        response = requests.get(
            f"{self.url}/job/{pipeline_id}/{build_id}/api/json?tree=artifacts[*]",
            auth=self.auth
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get Jenkins build artifacts: {response.text}")
        
        data = response.json()
        
        artifacts = []
        for artifact in data["artifacts"]:
            artifacts.append({
                "name": artifact["fileName"],
                "path": artifact["relativePath"],
                "url": f"{self.url}/job/{pipeline_id}/{build_id}/artifact/{artifact['relativePath']}"
            })
        
        return {
            "pipeline_id": pipeline_id,
            "build_id": build_id,
            "artifacts": artifacts
        }
    
    def create_pipeline(self, pipeline_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new Jenkins pipeline.
        
        Args:
            pipeline_config: Pipeline configuration
            
        Returns:
            Dict[str, Any]: Pipeline creation result
        """
        pipeline_name = pipeline_config.get("name")
        pipeline_xml = pipeline_config.get("xml")
        
        headers = {'Content-Type': 'application/xml'}
        
        response = requests.post(
            f"{self.url}/createItem?name={pipeline_name}",
            auth=self.auth,
            headers=headers,
            data=pipeline_xml
        )
        
        if response.status_code not in [200, 201]:
            raise Exception(f"Failed to create Jenkins pipeline: {response.text}")
        
        return {
            "pipeline_id": pipeline_name,
            "url": f"{self.url}/job/{pipeline_name}"
        }
    
    def update_pipeline(self, pipeline_id: str, pipeline_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing Jenkins pipeline.
        
        Args:
            pipeline_id: Pipeline job name
            pipeline_config: Pipeline configuration
            
        Returns:
            Dict[str, Any]: Pipeline update result
        """
        pipeline_xml = pipeline_config.get("xml")
        
        headers = {'Content-Type': 'application/xml'}
        
        response = requests.post(
            f"{self.url}/job/{pipeline_id}/config.xml",
            auth=self.auth,
            headers=headers,
            data=pipeline_xml
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to update Jenkins pipeline: {response.text}")
        
        return {
            "pipeline_id": pipeline_id,
            "url": f"{self.url}/job/{pipeline_id}"
        }
    
    def delete_pipeline(self, pipeline_id: str) -> Dict[str, Any]:
        """
        Delete a Jenkins pipeline.
        
        Args:
            pipeline_id: Pipeline job name
            
        Returns:
            Dict[str, Any]: Pipeline deletion result
        """
        response = requests.post(
            f"{self.url}/job/{pipeline_id}/doDelete",
            auth=self.auth
        )
        
        if response.status_code not in [200, 302]:
            raise Exception(f"Failed to delete Jenkins pipeline: {response.text}")
        
        return {
            "pipeline_id": pipeline_id,
            "deleted": True
        }
    
    def list_pipelines(self) -> Dict[str, Any]:
        """
        List all Jenkins pipelines.
        
        Returns:
            Dict[str, Any]: Pipeline list
        """
        response = requests.get(
            f"{self.url}/api/json?tree=jobs[name,url]",
            auth=self.auth
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to list Jenkins pipelines: {response.text}")
        
        data = response.json()
        
        pipelines = []
        for job in data["jobs"]:
            pipelines.append({
                "id": job["name"],
                "name": job["name"],
                "url": job["url"]
            })
        
        return {
            "pipelines": pipelines
        }


class GitHubActionsIntegration:
    """
    Integration with GitHub Actions.
    
    This class provides methods for interacting with GitHub Actions,
    including workflow management, run triggers, and artifact retrieval.
    """
    
    def __init__(self, repo_owner: str, repo_name: str, token: str):
        """
        Initialize the GitHub Actions integration.
        
        Args:
            repo_owner: GitHub repository owner
            repo_name: GitHub repository name
            token: GitHub personal access token
        """
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.token = token
        self.api_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def validate_connection(self) -> bool:
        """
        Validate the GitHub connection.
        
        Returns:
            bool: True if connection is valid, False otherwise
        """
        try:
            response = requests.get(
                f"{self.api_url}/repos/{self.repo_owner}/{self.repo_name}",
                headers=self.headers
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to validate GitHub connection: {str(e)}")
            return False
    
    def trigger_pipeline(self, pipeline_id: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Trigger a GitHub Actions workflow.
        
        Args:
            pipeline_id: Workflow file name (e.g., "main.yml")
            parameters: Workflow inputs (optional)
            
        Returns:
            Dict[str, Any]: Workflow run information
        """
        url = f"{self.api_url}/repos/{self.repo_owner}/{self.repo_name}/actions/workflows/{pipeline_id}/dispatches"
        
        data = {
            "ref": "main",  # Default branch
            "inputs": parameters or {}
        }
        
        response = requests.post(
            url,
            headers=self.headers,
            json=data
        )
        
        if response.status_code != 204:
            raise Exception(f"Failed to trigger GitHub Actions workflow: {response.text}")
        
        # Get the workflow run ID
        time.sleep(2)  # Wait a bit for the workflow to start
        
        runs_url = f"{self.api_url}/repos/{self.repo_owner}/{self.repo_name}/actions/workflows/{pipeline_id}/runs"
        
        response = requests.get(
            runs_url,
            headers=self.headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get GitHub Actions workflow runs: {response.text}")
        
        data = response.json()
        
        if not data["workflow_runs"]:
            raise Exception("No workflow runs found")
        
        # Get the latest run
        latest_run = data["workflow_runs"][0]
        
        return {
            "pipeline_id": pipeline_id,
            "build_id": str(latest_run["id"]),
            "url": latest_run["html_url"]
        }
    
    def get_pipeline_status(self, pipeline_id: str, build_id: str) -> Dict[str, Any]:
        """
        Get the status of a GitHub Actions workflow run.
        
        Args:
            pipeline_id: Workflow file name (not used, but kept for interface consistency)
            build_id: Workflow run ID
            
        Returns:
            Dict[str, Any]: Workflow run status information
        """
        url = f"{self.api_url}/repos/{self.repo_owner}/{self.repo_name}/actions/runs/{build_id}"
        
        response = requests.get(
            url,
            headers=self.headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get GitHub Actions workflow run status: {response.text}")
        
        data = response.json()
        
        return {
            "pipeline_id": pipeline_id,
            "build_id": build_id,
            "status": "SUCCESS" if data["conclusion"] == "success" else 
                     "FAILURE" if data["conclusion"] == "failure" else 
                     "CANCELLED" if data["conclusion"] == "cancelled" else 
                     "IN_PROGRESS" if data["status"] == "in_progress" else "UNKNOWN",
            "url": data["html_url"],
            "created_at": data["created_at"],
            "updated_at": data["updated_at"]
        }
    
    def get_pipeline_artifacts(self, pipeline_id: str, build_id: str) -> Dict[str, Any]:
        """
        Get artifacts from a GitHub Actions workflow run.
        
        Args:
            pipeline_id: Workflow file name (not used, but kept for interface consistency)
            build_id: Workflow run ID
            
        Returns:
            Dict[str, Any]: Workflow run artifacts information
        """
        url = f"{self.api_url}/repos/{self.repo_owner}/{self.repo_name}/actions/runs/{build_id}/artifacts"
        
        response = requests.get(
            url,
            headers=self.headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get GitHub Actions workflow run artifacts: {response.text}")
        
        data = response.json()
        
        artifacts = []
        for artifact in data["artifacts"]:
            artifacts.append({
                "name": artifact["name"],
                "size": artifact["size_in_bytes"],
                "url": artifact["archive_download_url"]
            })
        
        return {
            "pipeline_id": pipeline_id,
            "build_id": build_id,
            "artifacts": artifacts
        }
    
    def create_pipeline(self, pipeline_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new GitHub Actions workflow.
        
        Args:
            pipeline_config: Workflow configuration
            
        Returns:
            Dict[str, Any]: Workflow creation result
        """
        workflow_name = pipeline_config.get("name")
        workflow_content = pipeline_config.get("content")
        
        # Create or update workflow file via Git API
        url = f"{self.api_url}/repos/{self.repo_owner}/{self.repo_name}/contents/.github/workflows/{workflow_name}"
        
        # Check if file exists
        response = requests.get(
            url,
            headers=self.headers
        )
        
        if response.status_code == 200:
            # File exists, update it
            data = response.json()
            sha = data["sha"]
            
            update_data = {
                "message": f"Update workflow {workflow_name}",
                "content": workflow_content,
                "sha": sha
            }
            
            response = requests.put(
                url,
                headers=self.headers,
                json=update_data
            )
        else:
            # File doesn't exist, create it
            create_data = {
                "message": f"Create workflow {workflow_name}",
                "content": workflow_content
            }
            
            response = requests.put(
                url,
                headers=self.headers,
                json=create_data
            )
        
        if response.status_code not in [200, 201]:
            raise Exception(f"Failed to create GitHub Actions workflow: {response.text}")
        
        return {
            "pipeline_id": workflow_name,
            "url": f"https://github.com/{self.repo_owner}/{self.repo_name}/actions/workflows/{workflow_name}"
        }
    
    def update_pipeline(self, pipeline_id: str, pipeline_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing GitHub Actions workflow.
        
        Args:
            pipeline_id: Workflow file name
            pipeline_config: Workflow configuration
            
        Returns:
            Dict[str, Any]: Workflow update result
        """
        workflow_content = pipeline_config.get("content")
        
        # Update workflow file via Git API
        url = f"{self.api_url}/repos/{self.repo_owner}/{self.repo_name}/contents/.github/workflows/{pipeline_id}"
        
        # Get current file to get its SHA
        response = requests.get(
            url,
            headers=self.headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get GitHub Actions workflow: {response.text}")
        
        data = response.json()
        sha = data["sha"]
        
        update_data = {
            "message": f"Update workflow {pipeline_id}",
            "content": workflow_content,
            "sha": sha
        }
        
        response = requests.put(
            url,
            headers=self.headers,
            json=update_data
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to update GitHub Actions workflow: {response.text}")
        
        return {
            "pipeline_id": pipeline_id,
            "url": f"https://github.com/{self.repo_owner}/{self.repo_name}/actions/workflows/{pipeline_id}"
        }
    
    def delete_pipeline(self, pipeline_id: str) -> Dict[str, Any]:
        """
        Delete a GitHub Actions workflow.
        
        Args:
            pipeline_id: Workflow file name
            
        Returns:
            Dict[str, Any]: Workflow deletion result
        """
        # Delete workflow file via Git API
        url = f"{self.api_url}/repos/{self.repo_owner}/{self.repo_name}/contents/.github/workflows/{pipeline_id}"
        
        # Get current file to get its SHA
        response = requests.get(
            url,
            headers=self.headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get GitHub Actions workflow: {response.text}")
        
        data = response.json()
        sha = data["sha"]
        
        delete_data = {
            "message": f"Delete workflow {pipeline_id}",
            "sha": sha
        }
        
        response = requests.delete(
            url,
            headers=self.headers,
            json=delete_data
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to delete GitHub Actions workflow: {response.text}")
        
        return {
            "pipeline_id": pipeline_id,
            "deleted": True
        }
    
    def list_pipelines(self) -> Dict[str, Any]:
        """
        List all GitHub Actions workflows.
        
        Returns:
            Dict[str, Any]: Workflow list
        """
        url = f"{self.api_url}/repos/{self.repo_owner}/{self.repo_name}/actions/workflows"
        
        response = requests.get(
            url,
            headers=self.headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to list GitHub Actions workflows: {response.text}")
        
        data = response.json()
        
        pipelines = []
        for workflow in data["workflows"]:
            pipelines.append({
                "id": workflow["path"].split("/")[-1],
                "name": workflow["name"],
                "url": workflow["html_url"]
            })
        
        return {
            "pipelines": pipelines
        }


class GitLabCIIntegration:
    """
    Integration with GitLab CI/CD.
    
    This class provides methods for interacting with GitLab CI/CD,
    including pipeline management, job triggers, and artifact retrieval.
    """
    
    def __init__(self, gitlab_url: str, project_id: str, token: str):
        """
        Initialize the GitLab CI integration.
        
        Args:
            gitlab_url: GitLab server URL
            project_id: GitLab project ID
            token: GitLab personal access token
        """
        self.gitlab_url = gitlab_url.rstrip('/')
        self.project_id = project_id
        self.token = token
        self.api_url = f"{self.gitlab_url}/api/v4"
        self.headers = {
            "PRIVATE-TOKEN": token
        }
    
    def validate_connection(self) -> bool:
        """
        Validate the GitLab connection.
        
        Returns:
            bool: True if connection is valid, False otherwise
        """
        try:
            response = requests.get(
                f"{self.api_url}/projects/{self.project_id}",
                headers=self.headers
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to validate GitLab connection: {str(e)}")
            return False
    
    def trigger_pipeline(self, pipeline_id: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Trigger a GitLab CI pipeline.
        
        Args:
            pipeline_id: Branch or tag name
            parameters: Pipeline variables (optional)
            
        Returns:
            Dict[str, Any]: Pipeline information
        """
        url = f"{self.api_url}/projects/{self.project_id}/pipeline"
        
        data = {
            "ref": pipeline_id
        }
        
        if parameters:
            data["variables"] = [
                {"key": key, "value": value}
                for key, value in parameters.items()
            ]
        
        response = requests.post(
            url,
            headers=self.headers,
            json=data
        )
        
        if response.status_code != 201:
            raise Exception(f"Failed to trigger GitLab CI pipeline: {response.text}")
        
        data = response.json()
        
        return {
            "pipeline_id": pipeline_id,
            "build_id": str(data["id"]),
            "url": f"{self.gitlab_url}/{self.project_id}/-/pipelines/{data['id']}"
        }
    
    def get_pipeline_status(self, pipeline_id: str, build_id: str) -> Dict[str, Any]:
        """
        Get the status of a GitLab CI pipeline.
        
        Args:
            pipeline_id: Branch or tag name (not used, but kept for interface consistency)
            build_id: Pipeline ID
            
        Returns:
            Dict[str, Any]: Pipeline status information
        """
        url = f"{self.api_url}/projects/{self.project_id}/pipelines/{build_id}"
        
        response = requests.get(
            url,
            headers=self.headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get GitLab CI pipeline status: {response.text}")
        
        data = response.json()
        
        return {
            "pipeline_id": pipeline_id,
            "build_id": build_id,
            "status": "SUCCESS" if data["status"] == "success" else 
                     "FAILURE" if data["status"] == "failed" else 
                     "CANCELLED" if data["status"] == "canceled" else 
                     "IN_PROGRESS" if data["status"] in ["running", "pending"] else "UNKNOWN",
            "url": f"{self.gitlab_url}/{self.project_id}/-/pipelines/{build_id}",
            "created_at": data["created_at"],
            "updated_at": data["updated_at"]
        }
    
    def get_pipeline_artifacts(self, pipeline_id: str, build_id: str) -> Dict[str, Any]:
        """
        Get artifacts from a GitLab CI pipeline.
        
        Args:
            pipeline_id: Branch or tag name (not used, but kept for interface consistency)
            build_id: Pipeline ID
            
        Returns:
            Dict[str, Any]: Pipeline artifacts information
        """
        # Get jobs for the pipeline
        url = f"{self.api_url}/projects/{self.project_id}/pipelines/{build_id}/jobs"
        
        response = requests.get(
            url,
            headers=self.headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get GitLab CI pipeline jobs: {response.text}")
        
        jobs = response.json()
        
        artifacts = []
        for job in jobs:
            if job["artifacts"]:
                for artifact in job["artifacts"]:
                    artifacts.append({
                        "name": artifact["filename"],
                        "size": artifact["size"],
                        "url": f"{self.api_url}/projects/{self.project_id}/jobs/{job['id']}/artifacts/{artifact['filename']}"
                    })
        
        return {
            "pipeline_id": pipeline_id,
            "build_id": build_id,
            "artifacts": artifacts
        }
    
    def create_pipeline(self, pipeline_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new GitLab CI pipeline configuration.
        
        Args:
            pipeline_config: Pipeline configuration
            
        Returns:
            Dict[str, Any]: Pipeline creation result
        """
        # GitLab CI configuration is stored in .gitlab-ci.yml file
        # We need to update this file via the repository API
        
        file_path = pipeline_config.get("file_path", ".gitlab-ci.yml")
        file_content = pipeline_config.get("content")
        branch = pipeline_config.get("branch", "main")
        
        url = f"{self.api_url}/projects/{self.project_id}/repository/files/{file_path}"
        
        # Check if file exists
        response = requests.get(
            f"{url}?ref={branch}",
            headers=self.headers
        )
        
        if response.status_code == 200:
            # File exists, update it
            data = {
                "branch": branch,
                "content": file_content,
                "commit_message": "Update GitLab CI configuration"
            }
            
            response = requests.put(
                url,
                headers=self.headers,
                json=data
            )
        else:
            # File doesn't exist, create it
            data = {
                "branch": branch,
                "content": file_content,
                "commit_message": "Create GitLab CI configuration"
            }
            
            response = requests.post(
                url,
                headers=self.headers,
                json=data
            )
        
        if response.status_code not in [200, 201]:
            raise Exception(f"Failed to create GitLab CI pipeline configuration: {response.text}")
        
        return {
            "pipeline_id": branch,
            "file_path": file_path,
            "url": f"{self.gitlab_url}/{self.project_id}/-/blob/{branch}/{file_path}"
        }
    
    def update_pipeline(self, pipeline_id: str, pipeline_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing GitLab CI pipeline configuration.
        
        Args:
            pipeline_id: Branch name
            pipeline_config: Pipeline configuration
            
        Returns:
            Dict[str, Any]: Pipeline update result
        """
        # GitLab CI configuration is stored in .gitlab-ci.yml file
        # We need to update this file via the repository API
        
        file_path = pipeline_config.get("file_path", ".gitlab-ci.yml")
        file_content = pipeline_config.get("content")
        
        url = f"{self.api_url}/projects/{self.project_id}/repository/files/{file_path}"
        
        data = {
            "branch": pipeline_id,
            "content": file_content,
            "commit_message": "Update GitLab CI configuration"
        }
        
        response = requests.put(
            url,
            headers=self.headers,
            json=data
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to update GitLab CI pipeline configuration: {response.text}")
        
        return {
            "pipeline_id": pipeline_id,
            "file_path": file_path,
            "url": f"{self.gitlab_url}/{self.project_id}/-/blob/{pipeline_id}/{file_path}"
        }
    
    def delete_pipeline(self, pipeline_id: str) -> Dict[str, Any]:
        """
        Delete a GitLab CI pipeline configuration.
        
        Args:
            pipeline_id: Branch name
            
        Returns:
            Dict[str, Any]: Pipeline deletion result
        """
        # GitLab CI configuration is stored in .gitlab-ci.yml file
        # We need to delete this file via the repository API
        
        file_path = ".gitlab-ci.yml"
        
        url = f"{self.api_url}/projects/{self.project_id}/repository/files/{file_path}"
        
        data = {
            "branch": pipeline_id,
            "commit_message": "Delete GitLab CI configuration"
        }
        
        response = requests.delete(
            url,
            headers=self.headers,
            json=data
        )
        
        if response.status_code != 204:
            raise Exception(f"Failed to delete GitLab CI pipeline configuration: {response.text}")
        
        return {
            "pipeline_id": pipeline_id,
            "deleted": True
        }
    
    def list_pipelines(self) -> Dict[str, Any]:
        """
        List all GitLab CI pipelines.
        
        Returns:
            Dict[str, Any]: Pipeline list
        """
        url = f"{self.api_url}/projects/{self.project_id}/pipelines"
        
        response = requests.get(
            url,
            headers=self.headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to list GitLab CI pipelines: {response.text}")
        
        data = response.json()
        
        pipelines = []
        for pipeline in data:
            pipelines.append({
                "id": str(pipeline["id"]),
                "ref": pipeline["ref"],
                "status": pipeline["status"],
                "url": f"{self.gitlab_url}/{self.project_id}/-/pipelines/{pipeline['id']}"
            })
        
        return {
            "pipelines": pipelines
        }


class AzureDevOpsIntegration:
    """
    Integration with Azure DevOps.
    
    This class provides methods for interacting with Azure DevOps,
    including pipeline management, build triggers, and artifact retrieval.
    """
    
    def __init__(self, organization: str, project: str, token: str):
        """
        Initialize the Azure DevOps integration.
        
        Args:
            organization: Azure DevOps organization name
            project: Azure DevOps project name
            token: Azure DevOps personal access token
        """
        self.organization = organization
        self.project = project
        self.token = token
        self.api_url = f"https://dev.azure.com/{organization}/{project}/_apis"
        self.auth = ("", token)
    
    def validate_connection(self) -> bool:
        """
        Validate the Azure DevOps connection.
        
        Returns:
            bool: True if connection is valid, False otherwise
        """
        try:
            response = requests.get(
                f"{self.api_url}/projects?api-version=6.0",
                auth=self.auth
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to validate Azure DevOps connection: {str(e)}")
            return False
    
    def trigger_pipeline(self, pipeline_id: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Trigger an Azure DevOps pipeline.
        
        Args:
            pipeline_id: Pipeline ID
            parameters: Pipeline parameters (optional)
            
        Returns:
            Dict[str, Any]: Build information
        """
        url = f"{self.api_url}/pipelines/{pipeline_id}/runs?api-version=6.0"
        
        data = {
            "resources": {
                "repositories": {
                    "self": {
                        "refName": "refs/heads/main"
                    }
                }
            }
        }
        
        if parameters:
            data["templateParameters"] = parameters
        
        response = requests.post(
            url,
            auth=self.auth,
            json=data
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to trigger Azure DevOps pipeline: {response.text}")
        
        data = response.json()
        
        return {
            "pipeline_id": pipeline_id,
            "build_id": str(data["id"]),
            "url": data["_links"]["web"]["href"]
        }
    
    def get_pipeline_status(self, pipeline_id: str, build_id: str) -> Dict[str, Any]:
        """
        Get the status of an Azure DevOps pipeline run.
        
        Args:
            pipeline_id: Pipeline ID (not used, but kept for interface consistency)
            build_id: Pipeline run ID
            
        Returns:
            Dict[str, Any]: Pipeline run status information
        """
        url = f"{self.api_url}/pipelines/runs/{build_id}?api-version=6.0"
        
        response = requests.get(
            url,
            auth=self.auth
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get Azure DevOps pipeline run status: {response.text}")
        
        data = response.json()
        
        return {
            "pipeline_id": pipeline_id,
            "build_id": build_id,
            "status": "SUCCESS" if data["result"] == "succeeded" else 
                     "FAILURE" if data["result"] == "failed" else 
                     "CANCELLED" if data["result"] == "canceled" else 
                     "IN_PROGRESS" if data["state"] == "inProgress" else "UNKNOWN",
            "url": data["_links"]["web"]["href"],
            "created_date": data["createdDate"],
            "finished_date": data.get("finishedDate")
        }
    
    def get_pipeline_artifacts(self, pipeline_id: str, build_id: str) -> Dict[str, Any]:
        """
        Get artifacts from an Azure DevOps pipeline run.
        
        Args:
            pipeline_id: Pipeline ID (not used, but kept for interface consistency)
            build_id: Pipeline run ID
            
        Returns:
            Dict[str, Any]: Pipeline run artifacts information
        """
        url = f"{self.api_url}/pipelines/runs/{build_id}/artifacts?api-version=6.0"
        
        response = requests.get(
            url,
            auth=self.auth
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get Azure DevOps pipeline run artifacts: {response.text}")
        
        data = response.json()
        
        artifacts = []
        for artifact in data["value"]:
            artifacts.append({
                "name": artifact["name"],
                "url": artifact["resource"]["downloadUrl"]
            })
        
        return {
            "pipeline_id": pipeline_id,
            "build_id": build_id,
            "artifacts": artifacts
        }
    
    def create_pipeline(self, pipeline_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new Azure DevOps pipeline.
        
        Args:
            pipeline_config: Pipeline configuration
            
        Returns:
            Dict[str, Any]: Pipeline creation result
        """
        url = f"{self.api_url}/pipelines?api-version=6.0"
        
        data = {
            "name": pipeline_config.get("name"),
            "folder": pipeline_config.get("folder", "\\"),
            "configuration": {
                "type": "yaml",
                "path": pipeline_config.get("yaml_path", "azure-pipelines.yml"),
                "repository": {
                    "id": pipeline_config.get("repository_id"),
                    "type": "azureReposGit"
                }
            }
        }
        
        response = requests.post(
            url,
            auth=self.auth,
            json=data
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to create Azure DevOps pipeline: {response.text}")
        
        data = response.json()
        
        return {
            "pipeline_id": str(data["id"]),
            "name": data["name"],
            "url": data["_links"]["web"]["href"]
        }
    
    def update_pipeline(self, pipeline_id: str, pipeline_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing Azure DevOps pipeline.
        
        Args:
            pipeline_id: Pipeline ID
            pipeline_config: Pipeline configuration
            
        Returns:
            Dict[str, Any]: Pipeline update result
        """
        url = f"{self.api_url}/pipelines/{pipeline_id}?api-version=6.0"
        
        data = {
            "name": pipeline_config.get("name"),
            "folder": pipeline_config.get("folder"),
            "configuration": {
                "type": "yaml",
                "path": pipeline_config.get("yaml_path"),
                "repository": {
                    "id": pipeline_config.get("repository_id"),
                    "type": "azureReposGit"
                }
            }
        }
        
        response = requests.patch(
            url,
            auth=self.auth,
            json=data
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to update Azure DevOps pipeline: {response.text}")
        
        data = response.json()
        
        return {
            "pipeline_id": pipeline_id,
            "name": data["name"],
            "url": data["_links"]["web"]["href"]
        }
    
    def delete_pipeline(self, pipeline_id: str) -> Dict[str, Any]:
        """
        Delete an Azure DevOps pipeline.
        
        Args:
            pipeline_id: Pipeline ID
            
        Returns:
            Dict[str, Any]: Pipeline deletion result
        """
        url = f"{self.api_url}/pipelines/{pipeline_id}?api-version=6.0"
        
        response = requests.delete(
            url,
            auth=self.auth
        )
        
        if response.status_code != 204:
            raise Exception(f"Failed to delete Azure DevOps pipeline: {response.text}")
        
        return {
            "pipeline_id": pipeline_id,
            "deleted": True
        }
    
    def list_pipelines(self) -> Dict[str, Any]:
        """
        List all Azure DevOps pipelines.
        
        Returns:
            Dict[str, Any]: Pipeline list
        """
        url = f"{self.api_url}/pipelines?api-version=6.0"
        
        response = requests.get(
            url,
            auth=self.auth
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to list Azure DevOps pipelines: {response.text}")
        
        data = response.json()
        
        pipelines = []
        for pipeline in data["value"]:
            pipelines.append({
                "id": str(pipeline["id"]),
                "name": pipeline["name"],
                "url": pipeline["_links"]["web"]["href"]
            })
        
        return {
            "pipelines": pipelines
        }
