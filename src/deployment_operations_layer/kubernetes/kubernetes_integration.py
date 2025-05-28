"""
Kubernetes Integration for the Deployment Operations Layer.

This module provides Kubernetes integration capabilities for deployment operations
across the Industriverse ecosystem.
"""

import os
import json
import logging
import requests
import time
import uuid
import yaml
import subprocess
import base64
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class KubernetesIntegration:
    """
    Integration with Kubernetes for deployment operations.
    
    This class provides methods for interacting with Kubernetes clusters,
    including manifest validation, application, and monitoring.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the Kubernetes Integration.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.integration_id = config.get("integration_id", f"k8s-integration-{uuid.uuid4().hex[:8]}")
        self.kubeconfig = config.get("kubeconfig", os.environ.get("KUBECONFIG", "~/.kube/config"))
        self.context = config.get("context")
        self.namespace = config.get("namespace", "default")
        self.timeout = config.get("timeout", 300)
        self.retry_attempts = config.get("retry_attempts", 3)
        
        # Initialize kubectl command
        self.kubectl_cmd = config.get("kubectl_cmd", "kubectl")
        
        # Initialize manifest storage
        self.storage_type = config.get("storage_type", "file")
        self.storage_path = config.get("storage_path", "/tmp/k8s_manifests")
        
        # Initialize analytics manager for Kubernetes tracking
        from ..analytics.analytics_manager import AnalyticsManager
        self.analytics = AnalyticsManager(config.get("analytics", {}))
        
        # Initialize manifest generator
        from .kubernetes_manifest_generator import KubernetesManifestGenerator
        self.manifest_generator = KubernetesManifestGenerator(config.get("manifest_generator", {}))
        
        # Initialize security integration
        from ..security.security_integration import SecurityIntegration
        self.security = SecurityIntegration(config.get("security", {}))
        
        # Create storage directory if it doesn't exist
        if self.storage_type == "file":
            os.makedirs(self.storage_path, exist_ok=True)
        
        logger.info(f"Kubernetes Integration {self.integration_id} initialized")
    
    def validate_manifest(self, manifest_content: str) -> Dict:
        """
        Validate a Kubernetes manifest.
        
        Args:
            manifest_content: Manifest content
            
        Returns:
            Dict: Validation results
        """
        try:
            # Save manifest to temporary file
            manifest_file = os.path.join(self.storage_path, f"validate-{uuid.uuid4().hex}.yaml")
            with open(manifest_file, "w") as f:
                f.write(manifest_content)
            
            # Build kubectl command
            cmd = [
                self.kubectl_cmd,
                "--kubeconfig", os.path.expanduser(self.kubeconfig)
            ]
            
            # Add context if provided
            if self.context:
                cmd.extend(["--context", self.context])
            
            # Add validation command
            cmd.extend(["apply", "--dry-run=client", "-f", manifest_file])
            
            # Execute command
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Clean up temporary file
            os.remove(manifest_file)
            
            # Check result
            if result.returncode == 0:
                # Validation successful
                return {
                    "status": "success",
                    "message": "Manifest validated successfully",
                    "details": result.stdout.strip()
                }
            else:
                # Validation failed
                return {
                    "status": "error",
                    "message": "Manifest validation failed",
                    "details": result.stderr.strip()
                }
        except Exception as e:
            logger.error(f"Error validating manifest: {e}")
            return {"status": "error", "message": str(e)}
    
    def apply_manifest(self, manifest_content: str, options: Dict = None) -> Dict:
        """
        Apply a Kubernetes manifest.
        
        Args:
            manifest_content: Manifest content
            options: Application options
            
        Returns:
            Dict: Application results
        """
        try:
            # Initialize options
            if not options:
                options = {}
            
            # Get namespace from options or default
            namespace = options.get("namespace", self.namespace)
            
            # Get wait flag from options
            wait = options.get("wait", True)
            
            # Get timeout from options
            timeout = options.get("timeout", self.timeout)
            
            # Save manifest to file
            manifest_id = options.get("manifest_id", uuid.uuid4().hex)
            manifest_file = os.path.join(self.storage_path, f"{manifest_id}.yaml")
            with open(manifest_file, "w") as f:
                f.write(manifest_content)
            
            # Build kubectl command
            cmd = [
                self.kubectl_cmd,
                "--kubeconfig", os.path.expanduser(self.kubeconfig)
            ]
            
            # Add context if provided
            if self.context:
                cmd.extend(["--context", self.context])
            
            # Add namespace
            cmd.extend(["--namespace", namespace])
            
            # Add apply command
            cmd.extend(["apply", "-f", manifest_file])
            
            # Execute command
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Check result
            if result.returncode == 0:
                # Application successful
                application_result = {
                    "status": "success",
                    "message": "Manifest applied successfully",
                    "details": result.stdout.strip(),
                    "manifest_id": manifest_id,
                    "manifest_file": manifest_file
                }
                
                # Wait for resources if requested
                if wait:
                    wait_result = self._wait_for_resources(manifest_content, namespace, timeout)
                    application_result["wait_result"] = wait_result
                
                # Track application
                self._track_kubernetes_event("apply", {
                    "manifest_id": manifest_id,
                    "namespace": namespace,
                    "success": True
                })
                
                return application_result
            else:
                # Application failed
                application_result = {
                    "status": "error",
                    "message": "Manifest application failed",
                    "details": result.stderr.strip(),
                    "manifest_id": manifest_id,
                    "manifest_file": manifest_file
                }
                
                # Track application
                self._track_kubernetes_event("apply", {
                    "manifest_id": manifest_id,
                    "namespace": namespace,
                    "success": False,
                    "error": result.stderr.strip()
                })
                
                return application_result
        except Exception as e:
            logger.error(f"Error applying manifest: {e}")
            return {"status": "error", "message": str(e)}
    
    def delete_manifest(self, manifest_content: str, options: Dict = None) -> Dict:
        """
        Delete resources defined in a Kubernetes manifest.
        
        Args:
            manifest_content: Manifest content
            options: Deletion options
            
        Returns:
            Dict: Deletion results
        """
        try:
            # Initialize options
            if not options:
                options = {}
            
            # Get namespace from options or default
            namespace = options.get("namespace", self.namespace)
            
            # Get wait flag from options
            wait = options.get("wait", True)
            
            # Get timeout from options
            timeout = options.get("timeout", self.timeout)
            
            # Save manifest to file
            manifest_id = options.get("manifest_id", uuid.uuid4().hex)
            manifest_file = os.path.join(self.storage_path, f"{manifest_id}.yaml")
            with open(manifest_file, "w") as f:
                f.write(manifest_content)
            
            # Build kubectl command
            cmd = [
                self.kubectl_cmd,
                "--kubeconfig", os.path.expanduser(self.kubeconfig)
            ]
            
            # Add context if provided
            if self.context:
                cmd.extend(["--context", self.context])
            
            # Add namespace
            cmd.extend(["--namespace", namespace])
            
            # Add delete command
            cmd.extend(["delete", "-f", manifest_file])
            
            # Add wait flag if requested
            if wait:
                cmd.append("--wait")
            
            # Add timeout if requested
            if timeout:
                cmd.extend(["--timeout", f"{timeout}s"])
            
            # Execute command
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Check result
            if result.returncode == 0:
                # Deletion successful
                deletion_result = {
                    "status": "success",
                    "message": "Manifest deleted successfully",
                    "details": result.stdout.strip(),
                    "manifest_id": manifest_id,
                    "manifest_file": manifest_file
                }
                
                # Track deletion
                self._track_kubernetes_event("delete", {
                    "manifest_id": manifest_id,
                    "namespace": namespace,
                    "success": True
                })
                
                return deletion_result
            else:
                # Deletion failed
                deletion_result = {
                    "status": "error",
                    "message": "Manifest deletion failed",
                    "details": result.stderr.strip(),
                    "manifest_id": manifest_id,
                    "manifest_file": manifest_file
                }
                
                # Track deletion
                self._track_kubernetes_event("delete", {
                    "manifest_id": manifest_id,
                    "namespace": namespace,
                    "success": False,
                    "error": result.stderr.strip()
                })
                
                return deletion_result
        except Exception as e:
            logger.error(f"Error deleting manifest: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_resources(self, resource_type: str, namespace: str = None, selector: str = None) -> Dict:
        """
        Get Kubernetes resources.
        
        Args:
            resource_type: Resource type
            namespace: Namespace
            selector: Label selector
            
        Returns:
            Dict: Resources
        """
        try:
            # Get namespace from parameter or default
            if not namespace:
                namespace = self.namespace
            
            # Build kubectl command
            cmd = [
                self.kubectl_cmd,
                "--kubeconfig", os.path.expanduser(self.kubeconfig)
            ]
            
            # Add context if provided
            if self.context:
                cmd.extend(["--context", self.context])
            
            # Add namespace
            cmd.extend(["--namespace", namespace])
            
            # Add get command
            cmd.extend(["get", resource_type, "-o", "json"])
            
            # Add selector if provided
            if selector:
                cmd.extend(["--selector", selector])
            
            # Execute command
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Check result
            if result.returncode == 0:
                # Get successful
                resources = json.loads(result.stdout)
                
                return {
                    "status": "success",
                    "message": f"Resources retrieved successfully",
                    "resource_type": resource_type,
                    "namespace": namespace,
                    "selector": selector,
                    "resources": resources
                }
            else:
                # Get failed
                return {
                    "status": "error",
                    "message": "Resource retrieval failed",
                    "details": result.stderr.strip(),
                    "resource_type": resource_type,
                    "namespace": namespace,
                    "selector": selector
                }
        except Exception as e:
            logger.error(f"Error getting resources: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_resource_status(self, resource_type: str, resource_name: str, namespace: str = None) -> Dict:
        """
        Get the status of a Kubernetes resource.
        
        Args:
            resource_type: Resource type
            resource_name: Resource name
            namespace: Namespace
            
        Returns:
            Dict: Resource status
        """
        try:
            # Get namespace from parameter or default
            if not namespace:
                namespace = self.namespace
            
            # Build kubectl command
            cmd = [
                self.kubectl_cmd,
                "--kubeconfig", os.path.expanduser(self.kubeconfig)
            ]
            
            # Add context if provided
            if self.context:
                cmd.extend(["--context", self.context])
            
            # Add namespace
            cmd.extend(["--namespace", namespace])
            
            # Add get command
            cmd.extend(["get", resource_type, resource_name, "-o", "json"])
            
            # Execute command
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Check result
            if result.returncode == 0:
                # Get successful
                resource = json.loads(result.stdout)
                
                # Extract status
                status = resource.get("status", {})
                
                return {
                    "status": "success",
                    "message": f"Resource status retrieved successfully",
                    "resource_type": resource_type,
                    "resource_name": resource_name,
                    "namespace": namespace,
                    "resource_status": status,
                    "resource": resource
                }
            else:
                # Get failed
                return {
                    "status": "error",
                    "message": "Resource status retrieval failed",
                    "details": result.stderr.strip(),
                    "resource_type": resource_type,
                    "resource_name": resource_name,
                    "namespace": namespace
                }
        except Exception as e:
            logger.error(f"Error getting resource status: {e}")
            return {"status": "error", "message": str(e)}
    
    def scale_deployment(self, deployment_name: str, replicas: int, namespace: str = None) -> Dict:
        """
        Scale a Kubernetes deployment.
        
        Args:
            deployment_name: Deployment name
            replicas: Number of replicas
            namespace: Namespace
            
        Returns:
            Dict: Scaling results
        """
        try:
            # Get namespace from parameter or default
            if not namespace:
                namespace = self.namespace
            
            # Build kubectl command
            cmd = [
                self.kubectl_cmd,
                "--kubeconfig", os.path.expanduser(self.kubeconfig)
            ]
            
            # Add context if provided
            if self.context:
                cmd.extend(["--context", self.context])
            
            # Add namespace
            cmd.extend(["--namespace", namespace])
            
            # Add scale command
            cmd.extend(["scale", "deployment", deployment_name, f"--replicas={replicas}"])
            
            # Execute command
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Check result
            if result.returncode == 0:
                # Scaling successful
                scaling_result = {
                    "status": "success",
                    "message": "Deployment scaled successfully",
                    "details": result.stdout.strip(),
                    "deployment_name": deployment_name,
                    "replicas": replicas,
                    "namespace": namespace
                }
                
                # Track scaling
                self._track_kubernetes_event("scale", {
                    "deployment_name": deployment_name,
                    "replicas": replicas,
                    "namespace": namespace,
                    "success": True
                })
                
                return scaling_result
            else:
                # Scaling failed
                scaling_result = {
                    "status": "error",
                    "message": "Deployment scaling failed",
                    "details": result.stderr.strip(),
                    "deployment_name": deployment_name,
                    "replicas": replicas,
                    "namespace": namespace
                }
                
                # Track scaling
                self._track_kubernetes_event("scale", {
                    "deployment_name": deployment_name,
                    "replicas": replicas,
                    "namespace": namespace,
                    "success": False,
                    "error": result.stderr.strip()
                })
                
                return scaling_result
        except Exception as e:
            logger.error(f"Error scaling deployment: {e}")
            return {"status": "error", "message": str(e)}
    
    def restart_deployment(self, deployment_name: str, namespace: str = None) -> Dict:
        """
        Restart a Kubernetes deployment.
        
        Args:
            deployment_name: Deployment name
            namespace: Namespace
            
        Returns:
            Dict: Restart results
        """
        try:
            # Get namespace from parameter or default
            if not namespace:
                namespace = self.namespace
            
            # Build kubectl command
            cmd = [
                self.kubectl_cmd,
                "--kubeconfig", os.path.expanduser(self.kubeconfig)
            ]
            
            # Add context if provided
            if self.context:
                cmd.extend(["--context", self.context])
            
            # Add namespace
            cmd.extend(["--namespace", namespace])
            
            # Add rollout restart command
            cmd.extend(["rollout", "restart", "deployment", deployment_name])
            
            # Execute command
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Check result
            if result.returncode == 0:
                # Restart successful
                restart_result = {
                    "status": "success",
                    "message": "Deployment restarted successfully",
                    "details": result.stdout.strip(),
                    "deployment_name": deployment_name,
                    "namespace": namespace
                }
                
                # Track restart
                self._track_kubernetes_event("restart", {
                    "deployment_name": deployment_name,
                    "namespace": namespace,
                    "success": True
                })
                
                return restart_result
            else:
                # Restart failed
                restart_result = {
                    "status": "error",
                    "message": "Deployment restart failed",
                    "details": result.stderr.strip(),
                    "deployment_name": deployment_name,
                    "namespace": namespace
                }
                
                # Track restart
                self._track_kubernetes_event("restart", {
                    "deployment_name": deployment_name,
                    "namespace": namespace,
                    "success": False,
                    "error": result.stderr.strip()
                })
                
                return restart_result
        except Exception as e:
            logger.error(f"Error restarting deployment: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_logs(self, pod_name: str, container: str = None, namespace: str = None, tail: int = None) -> Dict:
        """
        Get logs from a Kubernetes pod.
        
        Args:
            pod_name: Pod name
            container: Container name
            namespace: Namespace
            tail: Number of lines to tail
            
        Returns:
            Dict: Logs
        """
        try:
            # Get namespace from parameter or default
            if not namespace:
                namespace = self.namespace
            
            # Build kubectl command
            cmd = [
                self.kubectl_cmd,
                "--kubeconfig", os.path.expanduser(self.kubeconfig)
            ]
            
            # Add context if provided
            if self.context:
                cmd.extend(["--context", self.context])
            
            # Add namespace
            cmd.extend(["--namespace", namespace])
            
            # Add logs command
            cmd.extend(["logs", pod_name])
            
            # Add container if provided
            if container:
                cmd.extend(["--container", container])
            
            # Add tail if provided
            if tail:
                cmd.extend(["--tail", str(tail)])
            
            # Execute command
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Check result
            if result.returncode == 0:
                # Logs retrieval successful
                return {
                    "status": "success",
                    "message": "Logs retrieved successfully",
                    "pod_name": pod_name,
                    "container": container,
                    "namespace": namespace,
                    "logs": result.stdout
                }
            else:
                # Logs retrieval failed
                return {
                    "status": "error",
                    "message": "Logs retrieval failed",
                    "details": result.stderr.strip(),
                    "pod_name": pod_name,
                    "container": container,
                    "namespace": namespace
                }
        except Exception as e:
            logger.error(f"Error getting logs: {e}")
            return {"status": "error", "message": str(e)}
    
    def exec_command(self, pod_name: str, command: List[str], container: str = None, namespace: str = None) -> Dict:
        """
        Execute a command in a Kubernetes pod.
        
        Args:
            pod_name: Pod name
            command: Command to execute
            container: Container name
            namespace: Namespace
            
        Returns:
            Dict: Execution results
        """
        try:
            # Get namespace from parameter or default
            if not namespace:
                namespace = self.namespace
            
            # Build kubectl command
            cmd = [
                self.kubectl_cmd,
                "--kubeconfig", os.path.expanduser(self.kubeconfig)
            ]
            
            # Add context if provided
            if self.context:
                cmd.extend(["--context", self.context])
            
            # Add namespace
            cmd.extend(["--namespace", namespace])
            
            # Add exec command
            cmd.extend(["exec", pod_name])
            
            # Add container if provided
            if container:
                cmd.extend(["--container", container])
            
            # Add command
            cmd.extend(["--", *command])
            
            # Execute command
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Check result
            if result.returncode == 0:
                # Execution successful
                return {
                    "status": "success",
                    "message": "Command executed successfully",
                    "pod_name": pod_name,
                    "container": container,
                    "namespace": namespace,
                    "command": command,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            else:
                # Execution failed
                return {
                    "status": "error",
                    "message": "Command execution failed",
                    "details": result.stderr.strip(),
                    "pod_name": pod_name,
                    "container": container,
                    "namespace": namespace,
                    "command": command,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return {"status": "error", "message": str(e)}
    
    def create_namespace(self, namespace: str, labels: Dict = None) -> Dict:
        """
        Create a Kubernetes namespace.
        
        Args:
            namespace: Namespace name
            labels: Namespace labels
            
        Returns:
            Dict: Creation results
        """
        try:
            # Build namespace manifest
            manifest = {
                "apiVersion": "v1",
                "kind": "Namespace",
                "metadata": {
                    "name": namespace
                }
            }
            
            # Add labels if provided
            if labels:
                manifest["metadata"]["labels"] = labels
            
            # Convert to YAML
            manifest_content = yaml.dump(manifest)
            
            # Apply manifest
            return self.apply_manifest(manifest_content)
        except Exception as e:
            logger.error(f"Error creating namespace: {e}")
            return {"status": "error", "message": str(e)}
    
    def create_secret(self, name: str, data: Dict, namespace: str = None, type: str = "Opaque") -> Dict:
        """
        Create a Kubernetes secret.
        
        Args:
            name: Secret name
            data: Secret data
            namespace: Namespace
            type: Secret type
            
        Returns:
            Dict: Creation results
        """
        try:
            # Get namespace from parameter or default
            if not namespace:
                namespace = self.namespace
            
            # Encode data
            encoded_data = {}
            for key, value in data.items():
                encoded_data[key] = base64.b64encode(value.encode()).decode()
            
            # Build secret manifest
            manifest = {
                "apiVersion": "v1",
                "kind": "Secret",
                "metadata": {
                    "name": name,
                    "namespace": namespace
                },
                "type": type,
                "data": encoded_data
            }
            
            # Convert to YAML
            manifest_content = yaml.dump(manifest)
            
            # Apply manifest
            return self.apply_manifest(manifest_content)
        except Exception as e:
            logger.error(f"Error creating secret: {e}")
            return {"status": "error", "message": str(e)}
    
    def create_configmap(self, name: str, data: Dict, namespace: str = None) -> Dict:
        """
        Create a Kubernetes configmap.
        
        Args:
            name: ConfigMap name
            data: ConfigMap data
            namespace: Namespace
            
        Returns:
            Dict: Creation results
        """
        try:
            # Get namespace from parameter or default
            if not namespace:
                namespace = self.namespace
            
            # Build configmap manifest
            manifest = {
                "apiVersion": "v1",
                "kind": "ConfigMap",
                "metadata": {
                    "name": name,
                    "namespace": namespace
                },
                "data": data
            }
            
            # Convert to YAML
            manifest_content = yaml.dump(manifest)
            
            # Apply manifest
            return self.apply_manifest(manifest_content)
        except Exception as e:
            logger.error(f"Error creating configmap: {e}")
            return {"status": "error", "message": str(e)}
    
    def generate_deployment_manifest(self, name: str, image: str, replicas: int = 1, options: Dict = None) -> Dict:
        """
        Generate a Kubernetes deployment manifest.
        
        Args:
            name: Deployment name
            image: Container image
            replicas: Number of replicas
            options: Additional options
            
        Returns:
            Dict: Generation results
        """
        try:
            # Generate manifest
            return self.manifest_generator.generate_deployment(name, image, replicas, options)
        except Exception as e:
            logger.error(f"Error generating deployment manifest: {e}")
            return {"status": "error", "message": str(e)}
    
    def generate_service_manifest(self, name: str, port: int, target_port: int, selector: Dict, options: Dict = None) -> Dict:
        """
        Generate a Kubernetes service manifest.
        
        Args:
            name: Service name
            port: Service port
            target_port: Target port
            selector: Pod selector
            options: Additional options
            
        Returns:
            Dict: Generation results
        """
        try:
            # Generate manifest
            return self.manifest_generator.generate_service(name, port, target_port, selector, options)
        except Exception as e:
            logger.error(f"Error generating service manifest: {e}")
            return {"status": "error", "message": str(e)}
    
    def generate_ingress_manifest(self, name: str, rules: List[Dict], options: Dict = None) -> Dict:
        """
        Generate a Kubernetes ingress manifest.
        
        Args:
            name: Ingress name
            rules: Ingress rules
            options: Additional options
            
        Returns:
            Dict: Generation results
        """
        try:
            # Generate manifest
            return self.manifest_generator.generate_ingress(name, rules, options)
        except Exception as e:
            logger.error(f"Error generating ingress manifest: {e}")
            return {"status": "error", "message": str(e)}
    
    def _wait_for_resources(self, manifest_content: str, namespace: str, timeout: int) -> Dict:
        """
        Wait for resources to be ready.
        
        Args:
            manifest_content: Manifest content
            namespace: Namespace
            timeout: Timeout in seconds
            
        Returns:
            Dict: Wait results
        """
        try:
            # Parse manifest
            resources = []
            for doc in yaml.safe_load_all(manifest_content):
                if doc:
                    resources.append(doc)
            
            # Initialize results
            results = {
                "status": "success",
                "message": "All resources are ready",
                "resources": []
            }
            
            # Wait for each resource
            for resource in resources:
                # Get resource kind and name
                kind = resource.get("kind")
                name = resource.get("metadata", {}).get("name")
                
                # Skip if kind or name is missing
                if not kind or not name:
                    continue
                
                # Skip if resource kind is not supported for waiting
                if kind not in ["Deployment", "StatefulSet", "DaemonSet", "Pod", "Job"]:
                    continue
                
                # Wait for resource
                wait_result = self._wait_for_resource(kind, name, namespace, timeout)
                
                # Add to results
                results["resources"].append({
                    "kind": kind,
                    "name": name,
                    "ready": wait_result.get("status") == "success",
                    "message": wait_result.get("message"),
                    "details": wait_result.get("details")
                })
                
                # Update overall status if resource is not ready
                if wait_result.get("status") != "success":
                    results["status"] = "error"
                    results["message"] = f"Resource {kind}/{name} is not ready"
            
            return results
        except Exception as e:
            logger.error(f"Error waiting for resources: {e}")
            return {"status": "error", "message": str(e)}
    
    def _wait_for_resource(self, kind: str, name: str, namespace: str, timeout: int) -> Dict:
        """
        Wait for a resource to be ready.
        
        Args:
            kind: Resource kind
            name: Resource name
            namespace: Namespace
            timeout: Timeout in seconds
            
        Returns:
            Dict: Wait results
        """
        try:
            # Build kubectl command
            cmd = [
                self.kubectl_cmd,
                "--kubeconfig", os.path.expanduser(self.kubeconfig)
            ]
            
            # Add context if provided
            if self.context:
                cmd.extend(["--context", self.context])
            
            # Add namespace
            cmd.extend(["--namespace", namespace])
            
            # Add wait command
            if kind == "Deployment":
                cmd.extend(["rollout", "status", "deployment", name, f"--timeout={timeout}s"])
            elif kind == "StatefulSet":
                cmd.extend(["rollout", "status", "statefulset", name, f"--timeout={timeout}s"])
            elif kind == "DaemonSet":
                cmd.extend(["rollout", "status", "daemonset", name, f"--timeout={timeout}s"])
            elif kind == "Pod":
                cmd.extend(["wait", "pod", name, "--for=condition=Ready", f"--timeout={timeout}s"])
            elif kind == "Job":
                cmd.extend(["wait", "job", name, "--for=condition=Complete", f"--timeout={timeout}s"])
            else:
                return {
                    "status": "error",
                    "message": f"Unsupported resource kind for waiting: {kind}"
                }
            
            # Execute command
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Check result
            if result.returncode == 0:
                # Wait successful
                return {
                    "status": "success",
                    "message": f"Resource {kind}/{name} is ready",
                    "details": result.stdout.strip()
                }
            else:
                # Wait failed
                return {
                    "status": "error",
                    "message": f"Resource {kind}/{name} is not ready",
                    "details": result.stderr.strip()
                }
        except Exception as e:
            logger.error(f"Error waiting for resource: {e}")
            return {"status": "error", "message": str(e)}
    
    def _track_kubernetes_event(self, event_type: str, event_data: Dict) -> None:
        """
        Track a Kubernetes event in analytics.
        
        Args:
            event_type: Event type
            event_data: Event data
        """
        try:
            # Prepare metrics
            metrics = {
                "type": f"kubernetes_{event_type}",
                "timestamp": datetime.now().isoformat(),
                "integration_id": self.integration_id
            }
            
            # Add event data
            metrics.update(event_data)
            
            # Track metrics
            self.analytics.track_metrics(metrics)
        except Exception as e:
            logger.error(f"Error tracking Kubernetes event: {e}")
    
    def configure(self, config: Dict) -> Dict:
        """
        Configure the Kubernetes Integration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Dict: Configuration results
        """
        try:
            # Update local configuration
            if "kubeconfig" in config:
                self.kubeconfig = config["kubeconfig"]
            
            if "context" in config:
                self.context = config["context"]
            
            if "namespace" in config:
                self.namespace = config["namespace"]
            
            if "timeout" in config:
                self.timeout = config["timeout"]
            
            if "retry_attempts" in config:
                self.retry_attempts = config["retry_attempts"]
            
            if "kubectl_cmd" in config:
                self.kubectl_cmd = config["kubectl_cmd"]
            
            if "storage_type" in config:
                self.storage_type = config["storage_type"]
            
            if "storage_path" in config:
                self.storage_path = config["storage_path"]
                
                # Create storage directory if it doesn't exist
                if self.storage_type == "file":
                    os.makedirs(self.storage_path, exist_ok=True)
            
            # Configure manifest generator
            manifest_generator_result = None
            if "manifest_generator" in config:
                manifest_generator_result = self.manifest_generator.configure(config["manifest_generator"])
            
            # Configure analytics manager
            analytics_result = None
            if "analytics" in config:
                analytics_result = self.analytics.configure(config["analytics"])
            
            # Configure security integration
            security_result = None
            if "security" in config:
                security_result = self.security.configure(config["security"])
            
            return {
                "status": "success",
                "message": "Kubernetes Integration configured successfully",
                "integration_id": self.integration_id,
                "manifest_generator_result": manifest_generator_result,
                "analytics_result": analytics_result,
                "security_result": security_result
            }
        except Exception as e:
            logger.error(f"Error configuring Kubernetes Integration: {e}")
            return {"status": "error", "message": str(e)}
