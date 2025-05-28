"""
Manifest Deployment Manager - Manages the deployment of manifests

This module manages the deployment of manifests to various environments,
handling the deployment lifecycle and status tracking.
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import os
import uuid
import yaml
import subprocess
import tempfile

logger = logging.getLogger(__name__)

class ManifestDeploymentManager:
    """
    Manages the deployment of manifests.
    
    This component is responsible for deploying manifests to various environments,
    handling the deployment lifecycle and status tracking.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Manifest Deployment Manager.
        
        Args:
            config: Configuration dictionary for the manager
        """
        self.config = config or {}
        self.deployments = {}  # Deployment ID -> Deployment
        self.deployment_history = {}  # Deployment ID -> List of history events
        self.max_history_length = self.config.get("max_history_length", 100)
        
        # Default kubectl path
        self.kubectl_path = self.config.get("kubectl_path", "kubectl")
        
        # Default environment
        self.default_environment = self.config.get("default_environment", "development")
        
        # Environment configurations
        self.environments = self.config.get("environments", {
            "development": {
                "kubeconfig": os.environ.get("KUBECONFIG", "~/.kube/config"),
                "context": "minikube",
                "namespace": "default"
            }
        })
        
        logger.info("Initializing Manifest Deployment Manager")
    
    def initialize(self):
        """Initialize the manager and load deployments."""
        logger.info("Initializing Manifest Deployment Manager")
        
        # Load deployments
        self._load_deployments()
        
        logger.info(f"Loaded {len(self.deployments)} deployments")
        return True
    
    def deploy_manifest(self, manifest: Dict[str, Any], environment: str = None, 
                      variables: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Deploy a manifest to an environment.
        
        Args:
            manifest: Manifest to deploy
            environment: Environment to deploy to (if None, uses default)
            variables: Variables for substitution (if None, uses empty dict)
            
        Returns:
            Dictionary with deployment result
        """
        logger.info(f"Deploying manifest {manifest.get('id', 'unknown')}")
        
        try:
            # Set default values
            if not environment:
                environment = self.default_environment
            
            if not variables:
                variables = {}
            
            # Check if environment exists
            if environment not in self.environments:
                logger.error(f"Environment {environment} not found")
                return {"success": False, "error": f"Environment {environment} not found"}
            
            # Get environment configuration
            env_config = self.environments[environment]
            
            # Generate deployment ID
            deployment_id = str(uuid.uuid4())
            
            # Create deployment record
            deployment = {
                "id": deployment_id,
                "manifest_id": manifest.get("id", "unknown"),
                "environment": environment,
                "status": "pending",
                "created": datetime.now().isoformat(),
                "updated": datetime.now().isoformat(),
                "variables": variables
            }
            
            # Save deployment
            self.deployments[deployment_id] = deployment
            
            # Record deployment event
            self._record_deployment_event(deployment_id, "create", "Deployment created")
            
            # Render manifest
            rendered_manifest = self._render_manifest(manifest, variables)
            
            if not rendered_manifest["success"]:
                # Update deployment status
                deployment["status"] = "failed"
                deployment["error"] = rendered_manifest["error"]
                deployment["updated"] = datetime.now().isoformat()
                
                # Record failure event
                self._record_deployment_event(deployment_id, "fail", f"Rendering failed: {rendered_manifest['error']}")
                
                logger.error(f"Failed to render manifest: {rendered_manifest['error']}")
                return {"success": False, "error": f"Failed to render manifest: {rendered_manifest['error']}"}
            
            # Get rendered content
            rendered_content = rendered_manifest["content"]
            
            # Deploy to environment
            deploy_result = self._deploy_to_environment(rendered_content, env_config)
            
            if not deploy_result["success"]:
                # Update deployment status
                deployment["status"] = "failed"
                deployment["error"] = deploy_result["error"]
                deployment["updated"] = datetime.now().isoformat()
                
                # Record failure event
                self._record_deployment_event(deployment_id, "fail", f"Deployment failed: {deploy_result['error']}")
                
                logger.error(f"Failed to deploy to environment: {deploy_result['error']}")
                return {"success": False, "error": f"Failed to deploy to environment: {deploy_result['error']}"}
            
            # Update deployment status
            deployment["status"] = "deployed"
            deployment["updated"] = datetime.now().isoformat()
            deployment["resources"] = deploy_result.get("resources", [])
            
            # Record success event
            self._record_deployment_event(deployment_id, "deploy", "Deployment successful")
            
            # Save deployments
            self._save_deployments()
            
            logger.info(f"Successfully deployed manifest {manifest.get('id', 'unknown')} to {environment}")
            
            return {
                "success": True,
                "deployment_id": deployment_id,
                "status": "deployed",
                "resources": deploy_result.get("resources", [])
            }
        except Exception as e:
            logger.error(f"Failed to deploy manifest: {str(e)}")
            return {"success": False, "error": f"Failed to deploy manifest: {str(e)}"}
    
    def undeploy_manifest(self, deployment_id: str) -> Dict[str, Any]:
        """
        Undeploy a manifest.
        
        Args:
            deployment_id: ID of the deployment
            
        Returns:
            Dictionary with undeployment result
        """
        logger.info(f"Undeploying manifest for deployment {deployment_id}")
        
        try:
            # Check if deployment exists
            if deployment_id not in self.deployments:
                logger.error(f"Deployment {deployment_id} not found")
                return {"success": False, "error": f"Deployment {deployment_id} not found"}
            
            # Get deployment
            deployment = self.deployments[deployment_id]
            
            # Check if deployment is already undeployed
            if deployment["status"] == "undeployed":
                logger.warning(f"Deployment {deployment_id} is already undeployed")
                return {"success": True, "deployment_id": deployment_id, "status": "undeployed"}
            
            # Get environment
            environment = deployment["environment"]
            
            # Check if environment exists
            if environment not in self.environments:
                logger.error(f"Environment {environment} not found")
                return {"success": False, "error": f"Environment {environment} not found"}
            
            # Get environment configuration
            env_config = self.environments[environment]
            
            # Undeploy from environment
            undeploy_result = self._undeploy_from_environment(deployment, env_config)
            
            if not undeploy_result["success"]:
                # Update deployment status
                deployment["status"] = "failed"
                deployment["error"] = undeploy_result["error"]
                deployment["updated"] = datetime.now().isoformat()
                
                # Record failure event
                self._record_deployment_event(deployment_id, "fail", f"Undeployment failed: {undeploy_result['error']}")
                
                logger.error(f"Failed to undeploy from environment: {undeploy_result['error']}")
                return {"success": False, "error": f"Failed to undeploy from environment: {undeploy_result['error']}"}
            
            # Update deployment status
            deployment["status"] = "undeployed"
            deployment["updated"] = datetime.now().isoformat()
            
            # Record success event
            self._record_deployment_event(deployment_id, "undeploy", "Undeployment successful")
            
            # Save deployments
            self._save_deployments()
            
            logger.info(f"Successfully undeployed manifest for deployment {deployment_id}")
            
            return {
                "success": True,
                "deployment_id": deployment_id,
                "status": "undeployed"
            }
        except Exception as e:
            logger.error(f"Failed to undeploy manifest: {str(e)}")
            return {"success": False, "error": f"Failed to undeploy manifest: {str(e)}"}
    
    def get_deployment(self, deployment_id: str) -> Dict[str, Any]:
        """
        Get a deployment.
        
        Args:
            deployment_id: ID of the deployment
            
        Returns:
            Dictionary with deployment retrieval result
        """
        # Check if deployment exists
        if deployment_id not in self.deployments:
            logger.warning(f"Deployment {deployment_id} not found")
            return {"success": False, "error": "Deployment not found"}
        
        # Get deployment
        deployment = self.deployments[deployment_id]
        
        logger.info(f"Retrieved deployment {deployment_id}")
        
        return {
            "success": True,
            "deployment": deployment
        }
    
    def get_deployment_status(self, deployment_id: str) -> Dict[str, Any]:
        """
        Get the status of a deployment.
        
        Args:
            deployment_id: ID of the deployment
            
        Returns:
            Dictionary with status retrieval result
        """
        # Check if deployment exists
        if deployment_id not in self.deployments:
            logger.warning(f"Deployment {deployment_id} not found")
            return {"success": False, "error": "Deployment not found"}
        
        # Get deployment
        deployment = self.deployments[deployment_id]
        
        # Get status
        status = deployment["status"]
        
        logger.info(f"Retrieved status for deployment {deployment_id}: {status}")
        
        return {
            "success": True,
            "deployment_id": deployment_id,
            "status": status
        }
    
    def get_deployment_history(self, deployment_id: str) -> Dict[str, Any]:
        """
        Get history for a deployment.
        
        Args:
            deployment_id: ID of the deployment
            
        Returns:
            Dictionary with history retrieval result
        """
        # Check if deployment exists
        if deployment_id not in self.deployment_history:
            logger.warning(f"Deployment {deployment_id} not found")
            return {"success": False, "error": "Deployment not found"}
        
        # Get history
        history = self.deployment_history[deployment_id]
        
        logger.info(f"Retrieved history for deployment {deployment_id}")
        
        return {
            "success": True,
            "deployment_id": deployment_id,
            "history": history
        }
    
    def get_deployments_by_environment(self, environment: str) -> Dict[str, Any]:
        """
        Get deployments by environment.
        
        Args:
            environment: Environment to filter by
            
        Returns:
            Dictionary with deployments in the environment
        """
        # Filter deployments by environment
        filtered_deployments = []
        
        for deployment in self.deployments.values():
            if deployment["environment"] == environment:
                filtered_deployments.append(deployment)
        
        logger.info(f"Retrieved {len(filtered_deployments)} deployments for environment {environment}")
        
        return {
            "success": True,
            "environment": environment,
            "deployments": filtered_deployments
        }
    
    def get_deployments_by_manifest(self, manifest_id: str) -> Dict[str, Any]:
        """
        Get deployments by manifest.
        
        Args:
            manifest_id: ID of the manifest
            
        Returns:
            Dictionary with deployments for the manifest
        """
        # Filter deployments by manifest
        filtered_deployments = []
        
        for deployment in self.deployments.values():
            if deployment["manifest_id"] == manifest_id:
                filtered_deployments.append(deployment)
        
        logger.info(f"Retrieved {len(filtered_deployments)} deployments for manifest {manifest_id}")
        
        return {
            "success": True,
            "manifest_id": manifest_id,
            "deployments": filtered_deployments
        }
    
    def get_deployments_by_status(self, status: str) -> Dict[str, Any]:
        """
        Get deployments by status.
        
        Args:
            status: Status to filter by
            
        Returns:
            Dictionary with deployments with the status
        """
        # Filter deployments by status
        filtered_deployments = []
        
        for deployment in self.deployments.values():
            if deployment["status"] == status:
                filtered_deployments.append(deployment)
        
        logger.info(f"Retrieved {len(filtered_deployments)} deployments with status {status}")
        
        return {
            "success": True,
            "status": status,
            "deployments": filtered_deployments
        }
    
    def get_all_deployments(self) -> Dict[str, Any]:
        """
        Get all deployments.
        
        Returns:
            Dictionary with all deployments
        """
        deployments = list(self.deployments.values())
        
        logger.info(f"Retrieved {len(deployments)} deployments")
        
        return {
            "success": True,
            "deployments": deployments
        }
    
    def get_environment_config(self, environment: str) -> Dict[str, Any]:
        """
        Get configuration for an environment.
        
        Args:
            environment: Environment to get configuration for
            
        Returns:
            Dictionary with environment configuration
        """
        # Check if environment exists
        if environment not in self.environments:
            logger.warning(f"Environment {environment} not found")
            return {"success": False, "error": "Environment not found"}
        
        # Get environment configuration
        env_config = self.environments[environment]
        
        logger.info(f"Retrieved configuration for environment {environment}")
        
        return {
            "success": True,
            "environment": environment,
            "config": env_config
        }
    
    def get_all_environments(self) -> Dict[str, Any]:
        """
        Get all environments.
        
        Returns:
            Dictionary with all environments
        """
        environments = {}
        
        for env_name, env_config in self.environments.items():
            environments[env_name] = env_config
        
        logger.info(f"Retrieved {len(environments)} environments")
        
        return {
            "success": True,
            "environments": environments
        }
    
    def add_environment(self, environment: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add an environment.
        
        Args:
            environment: Name of the environment
            config: Configuration for the environment
            
        Returns:
            Dictionary with addition result
        """
        logger.info(f"Adding environment {environment}")
        
        # Check if environment already exists
        if environment in self.environments:
            logger.warning(f"Environment {environment} already exists")
            return {"success": False, "error": "Environment already exists"}
        
        # Validate configuration
        required_fields = ["kubeconfig", "context", "namespace"]
        for field in required_fields:
            if field not in config:
                logger.error(f"Missing required field in environment configuration: {field}")
                return {"success": False, "error": f"Missing required field in environment configuration: {field}"}
        
        # Add environment
        self.environments[environment] = config
        
        # Save configuration
        self._save_config()
        
        logger.info(f"Added environment {environment}")
        
        return {
            "success": True,
            "environment": environment,
            "config": config
        }
    
    def update_environment(self, environment: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an environment.
        
        Args:
            environment: Name of the environment
            config: Updated configuration for the environment
            
        Returns:
            Dictionary with update result
        """
        logger.info(f"Updating environment {environment}")
        
        # Check if environment exists
        if environment not in self.environments:
            logger.warning(f"Environment {environment} not found")
            return {"success": False, "error": "Environment not found"}
        
        # Validate configuration
        required_fields = ["kubeconfig", "context", "namespace"]
        for field in required_fields:
            if field not in config:
                logger.error(f"Missing required field in environment configuration: {field}")
                return {"success": False, "error": f"Missing required field in environment configuration: {field}"}
        
        # Update environment
        self.environments[environment] = config
        
        # Save configuration
        self._save_config()
        
        logger.info(f"Updated environment {environment}")
        
        return {
            "success": True,
            "environment": environment,
            "config": config
        }
    
    def remove_environment(self, environment: str) -> Dict[str, Any]:
        """
        Remove an environment.
        
        Args:
            environment: Name of the environment
            
        Returns:
            Dictionary with removal result
        """
        logger.info(f"Removing environment {environment}")
        
        # Check if environment exists
        if environment not in self.environments:
            logger.warning(f"Environment {environment} not found")
            return {"success": False, "error": "Environment not found"}
        
        # Check if it's the default environment
        if environment == self.default_environment:
            logger.error("Cannot remove default environment")
            return {"success": False, "error": "Cannot remove default environment"}
        
        # Check if there are deployments in this environment
        for deployment in self.deployments.values():
            if deployment["environment"] == environment:
                logger.error(f"Cannot remove environment with active deployments")
                return {"success": False, "error": "Cannot remove environment with active deployments"}
        
        # Remove environment
        del self.environments[environment]
        
        # Save configuration
        self._save_config()
        
        logger.info(f"Removed environment {environment}")
        
        return {
            "success": True,
            "environment": environment
        }
    
    def set_default_environment(self, environment: str) -> Dict[str, Any]:
        """
        Set the default environment.
        
        Args:
            environment: Name of the environment
            
        Returns:
            Dictionary with result
        """
        logger.info(f"Setting default environment to {environment}")
        
        # Check if environment exists
        if environment not in self.environments:
            logger.warning(f"Environment {environment} not found")
            return {"success": False, "error": "Environment not found"}
        
        # Set default environment
        self.default_environment = environment
        
        # Save configuration
        self._save_config()
        
        logger.info(f"Set default environment to {environment}")
        
        return {
            "success": True,
            "default_environment": environment
        }
    
    def _render_manifest(self, manifest: Dict[str, Any], variables: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render a manifest with variable substitution.
        
        Args:
            manifest: Manifest to render
            variables: Variables for substitution
            
        Returns:
            Dictionary with rendering result
        """
        try:
            # Get manifest content
            content = manifest.get("content", {})
            
            # Create a copy of the content
            content_copy = json.loads(json.dumps(content))
            
            # Convert content to YAML string
            content_yaml = yaml.dump(content_copy, default_flow_style=False)
            
            # Create Jinja2 environment
            env = jinja2.Environment(
                loader=jinja2.BaseLoader(),
                autoescape=False,
                undefined=jinja2.StrictUndefined
            )
            
            # Render YAML string as a template
            template = env.from_string(content_yaml)
            rendered_yaml = template.render(**variables)
            
            # Parse rendered YAML
            rendered_content = yaml.safe_load(rendered_yaml)
            
            return {
                "success": True,
                "content": rendered_content
            }
        except Exception as e:
            logger.error(f"Failed to render manifest: {str(e)}")
            return {"success": False, "error": f"Failed to render manifest: {str(e)}"}
    
    def _deploy_to_environment(self, content: Dict[str, Any], env_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deploy content to an environment.
        
        Args:
            content: Content to deploy
            env_config: Environment configuration
            
        Returns:
            Dictionary with deployment result
        """
        try:
            # Get environment configuration
            kubeconfig = env_config["kubeconfig"]
            context = env_config["context"]
            namespace = env_config["namespace"]
            
            # Create temporary file for manifest
            with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
                yaml.dump(content, f, default_flow_style=False)
                manifest_file = f.name
            
            try:
                # Build kubectl command
                cmd = [
                    self.kubectl_path,
                    "--kubeconfig", kubeconfig,
                    "--context", context,
                    "-n", namespace,
                    "apply",
                    "-f", manifest_file
                ]
                
                # Execute command
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                
                # Parse output to get resources
                resources = []
                for line in result.stdout.splitlines():
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        resource_type = parts[0]
                        resource_name = parts[1]
                        resources.append({
                            "type": resource_type,
                            "name": resource_name
                        })
                
                return {
                    "success": True,
                    "resources": resources
                }
            finally:
                # Clean up temporary file
                os.unlink(manifest_file)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to deploy to environment: {e.stderr}")
            return {"success": False, "error": f"Failed to deploy to environment: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to deploy to environment: {str(e)}")
            return {"success": False, "error": f"Failed to deploy to environment: {str(e)}"}
    
    def _undeploy_from_environment(self, deployment: Dict[str, Any], env_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Undeploy from an environment.
        
        Args:
            deployment: Deployment to undeploy
            env_config: Environment configuration
            
        Returns:
            Dictionary with undeployment result
        """
        try:
            # Get environment configuration
            kubeconfig = env_config["kubeconfig"]
            context = env_config["context"]
            namespace = env_config["namespace"]
            
            # Get resources
            resources = deployment.get("resources", [])
            
            # If no resources, nothing to undeploy
            if not resources:
                return {"success": True}
            
            # Undeploy each resource
            for resource in resources:
                resource_type = resource["type"]
                resource_name = resource["name"]
                
                # Build kubectl command
                cmd = [
                    self.kubectl_path,
                    "--kubeconfig", kubeconfig,
                    "--context", context,
                    "-n", namespace,
                    "delete",
                    resource_type,
                    resource_name
                ]
                
                # Execute command
                subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                "success": True
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to undeploy from environment: {e.stderr}")
            return {"success": False, "error": f"Failed to undeploy from environment: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to undeploy from environment: {str(e)}")
            return {"success": False, "error": f"Failed to undeploy from environment: {str(e)}"}
    
    def _record_deployment_event(self, deployment_id: str, event_type: str, description: str):
        """
        Record a deployment event.
        
        Args:
            deployment_id: ID of the deployment
            event_type: Type of event
            description: Description of the event
        """
        # Create event
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "description": description
        }
        
        # Initialize history for this deployment if it doesn't exist
        if deployment_id not in self.deployment_history:
            self.deployment_history[deployment_id] = []
        
        # Add event to history
        self.deployment_history[deployment_id].append(event)
        
        # Trim history if it exceeds max length
        if len(self.deployment_history[deployment_id]) > self.max_history_length:
            self.deployment_history[deployment_id] = self.deployment_history[deployment_id][-self.max_history_length:]
        
        logger.info(f"Recorded {event_type} event for deployment {deployment_id}")
    
    def _load_deployments(self):
        """Load deployments from storage."""
        try:
            # In a real implementation, this would load from a database or file
            # For now, we'll just initialize with empty data
            self.deployments = {}
            self.deployment_history = {}
            logger.info("Loaded deployments")
        except Exception as e:
            logger.error(f"Failed to load deployments: {str(e)}")
    
    def _save_deployments(self):
        """Save deployments to storage."""
        try:
            # In a real implementation, this would save to a database or file
            # For now, we'll just log it
            logger.info(f"Saved {len(self.deployments)} deployments")
        except Exception as e:
            logger.error(f"Failed to save deployments: {str(e)}")
    
    def _save_config(self):
        """Save configuration to storage."""
        try:
            # In a real implementation, this would save to a database or file
            # For now, we'll just log it
            logger.info("Saved configuration")
        except Exception as e:
            logger.error(f"Failed to save configuration: {str(e)}")
