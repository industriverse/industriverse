"""
Kubernetes Integration Manager - Manages integration with Kubernetes clusters

This module provides integration with Kubernetes clusters, handling cluster
management, resource deployment, and status monitoring.
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import os
import yaml
import subprocess
import tempfile
from kubernetes import client, config
from kubernetes.client.rest import ApiException

logger = logging.getLogger(__name__)

class KubernetesIntegrationManager:
    """
    Manages integration with Kubernetes clusters.
    
    This component is responsible for integrating with Kubernetes clusters,
    handling cluster management, resource deployment, and status monitoring.
    """
    
    def __init__(self, config_dict: Dict[str, Any] = None):
        """
        Initialize the Kubernetes Integration Manager.
        
        Args:
            config_dict: Configuration dictionary for the manager
        """
        self.config_dict = config_dict or {}
        self.clusters = {}  # Cluster name -> Cluster configuration
        self.active_cluster = None
        self.active_namespace = "default"
        
        # Default kubectl path
        self.kubectl_path = self.config_dict.get("kubectl_path", "kubectl")
        
        logger.info("Initializing Kubernetes Integration Manager")
    
    def initialize(self):
        """Initialize the manager and load cluster configurations."""
        logger.info("Initializing Kubernetes Integration Manager")
        
        # Load cluster configurations
        self._load_cluster_configurations()
        
        # Set active cluster if available
        if self.clusters:
            default_cluster = self.config_dict.get("default_cluster")
            if default_cluster and default_cluster in self.clusters:
                self.active_cluster = default_cluster
            else:
                self.active_cluster = next(iter(self.clusters))
            
            # Set active namespace
            self.active_namespace = self.clusters[self.active_cluster].get("namespace", "default")
            
            logger.info(f"Set active cluster to {self.active_cluster} and namespace to {self.active_namespace}")
        
        logger.info(f"Loaded {len(self.clusters)} cluster configurations")
        return True
    
    def add_cluster(self, name: str, cluster_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a cluster configuration.
        
        Args:
            name: Name of the cluster
            cluster_config: Cluster configuration
            
        Returns:
            Dictionary with addition result
        """
        logger.info(f"Adding cluster {name}")
        
        # Validate cluster configuration
        required_fields = ["kubeconfig", "context"]
        for field in required_fields:
            if field not in cluster_config:
                logger.error(f"Missing required field in cluster configuration: {field}")
                return {"success": False, "error": f"Missing required field in cluster configuration: {field}"}
        
        # Add cluster
        self.clusters[name] = cluster_config
        
        # Set as active cluster if no active cluster
        if not self.active_cluster:
            self.active_cluster = name
            self.active_namespace = cluster_config.get("namespace", "default")
            logger.info(f"Set active cluster to {name} and namespace to {self.active_namespace}")
        
        # Save cluster configurations
        self._save_cluster_configurations()
        
        logger.info(f"Added cluster {name}")
        
        return {
            "success": True,
            "cluster": name,
            "config": cluster_config
        }
    
    def remove_cluster(self, name: str) -> Dict[str, Any]:
        """
        Remove a cluster configuration.
        
        Args:
            name: Name of the cluster
            
        Returns:
            Dictionary with removal result
        """
        logger.info(f"Removing cluster {name}")
        
        # Check if cluster exists
        if name not in self.clusters:
            logger.warning(f"Cluster {name} not found")
            return {"success": False, "error": "Cluster not found"}
        
        # Remove cluster
        del self.clusters[name]
        
        # Update active cluster if removed
        if self.active_cluster == name:
            if self.clusters:
                self.active_cluster = next(iter(self.clusters))
                self.active_namespace = self.clusters[self.active_cluster].get("namespace", "default")
                logger.info(f"Set active cluster to {self.active_cluster} and namespace to {self.active_namespace}")
            else:
                self.active_cluster = None
                self.active_namespace = "default"
                logger.info("No active cluster")
        
        # Save cluster configurations
        self._save_cluster_configurations()
        
        logger.info(f"Removed cluster {name}")
        
        return {
            "success": True,
            "cluster": name
        }
    
    def get_cluster(self, name: str) -> Dict[str, Any]:
        """
        Get a cluster configuration.
        
        Args:
            name: Name of the cluster
            
        Returns:
            Dictionary with cluster configuration
        """
        # Check if cluster exists
        if name not in self.clusters:
            logger.warning(f"Cluster {name} not found")
            return {"success": False, "error": "Cluster not found"}
        
        # Get cluster configuration
        cluster_config = self.clusters[name]
        
        logger.info(f"Retrieved configuration for cluster {name}")
        
        return {
            "success": True,
            "cluster": name,
            "config": cluster_config
        }
    
    def get_all_clusters(self) -> Dict[str, Any]:
        """
        Get all cluster configurations.
        
        Returns:
            Dictionary with all cluster configurations
        """
        clusters = {}
        
        for name, cluster_config in self.clusters.items():
            clusters[name] = cluster_config
        
        logger.info(f"Retrieved {len(clusters)} cluster configurations")
        
        return {
            "success": True,
            "clusters": clusters
        }
    
    def set_active_cluster(self, name: str) -> Dict[str, Any]:
        """
        Set the active cluster.
        
        Args:
            name: Name of the cluster
            
        Returns:
            Dictionary with result
        """
        logger.info(f"Setting active cluster to {name}")
        
        # Check if cluster exists
        if name not in self.clusters:
            logger.warning(f"Cluster {name} not found")
            return {"success": False, "error": "Cluster not found"}
        
        # Set active cluster
        self.active_cluster = name
        
        # Set active namespace
        self.active_namespace = self.clusters[name].get("namespace", "default")
        
        logger.info(f"Set active cluster to {name} and namespace to {self.active_namespace}")
        
        return {
            "success": True,
            "cluster": name,
            "namespace": self.active_namespace
        }
    
    def set_active_namespace(self, namespace: str) -> Dict[str, Any]:
        """
        Set the active namespace.
        
        Args:
            namespace: Namespace to set as active
            
        Returns:
            Dictionary with result
        """
        logger.info(f"Setting active namespace to {namespace}")
        
        # Check if active cluster is set
        if not self.active_cluster:
            logger.error("No active cluster")
            return {"success": False, "error": "No active cluster"}
        
        # Set active namespace
        self.active_namespace = namespace
        
        # Update cluster configuration
        self.clusters[self.active_cluster]["namespace"] = namespace
        
        # Save cluster configurations
        self._save_cluster_configurations()
        
        logger.info(f"Set active namespace to {namespace}")
        
        return {
            "success": True,
            "cluster": self.active_cluster,
            "namespace": namespace
        }
    
    def get_active_cluster(self) -> Dict[str, Any]:
        """
        Get the active cluster.
        
        Returns:
            Dictionary with active cluster information
        """
        # Check if active cluster is set
        if not self.active_cluster:
            logger.warning("No active cluster")
            return {"success": False, "error": "No active cluster"}
        
        # Get cluster configuration
        cluster_config = self.clusters[self.active_cluster]
        
        logger.info(f"Retrieved active cluster: {self.active_cluster}")
        
        return {
            "success": True,
            "cluster": self.active_cluster,
            "namespace": self.active_namespace,
            "config": cluster_config
        }
    
    def deploy_manifest(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deploy a manifest to the active cluster.
        
        Args:
            manifest: Manifest to deploy
            
        Returns:
            Dictionary with deployment result
        """
        logger.info("Deploying manifest to active cluster")
        
        # Check if active cluster is set
        if not self.active_cluster:
            logger.error("No active cluster")
            return {"success": False, "error": "No active cluster"}
        
        try:
            # Get cluster configuration
            cluster_config = self.clusters[self.active_cluster]
            kubeconfig = cluster_config["kubeconfig"]
            context = cluster_config["context"]
            
            # Create temporary file for manifest
            with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
                yaml.dump(manifest, f, default_flow_style=False)
                manifest_file = f.name
            
            try:
                # Build kubectl command
                cmd = [
                    self.kubectl_path,
                    "--kubeconfig", kubeconfig,
                    "--context", context,
                    "-n", self.active_namespace,
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
                
                logger.info(f"Successfully deployed manifest to cluster {self.active_cluster}")
                
                return {
                    "success": True,
                    "cluster": self.active_cluster,
                    "namespace": self.active_namespace,
                    "resources": resources
                }
            finally:
                # Clean up temporary file
                os.unlink(manifest_file)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to deploy manifest: {e.stderr}")
            return {"success": False, "error": f"Failed to deploy manifest: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to deploy manifest: {str(e)}")
            return {"success": False, "error": f"Failed to deploy manifest: {str(e)}"}
    
    def delete_resource(self, resource_type: str, resource_name: str) -> Dict[str, Any]:
        """
        Delete a resource from the active cluster.
        
        Args:
            resource_type: Type of resource
            resource_name: Name of resource
            
        Returns:
            Dictionary with deletion result
        """
        logger.info(f"Deleting resource {resource_type}/{resource_name} from active cluster")
        
        # Check if active cluster is set
        if not self.active_cluster:
            logger.error("No active cluster")
            return {"success": False, "error": "No active cluster"}
        
        try:
            # Get cluster configuration
            cluster_config = self.clusters[self.active_cluster]
            kubeconfig = cluster_config["kubeconfig"]
            context = cluster_config["context"]
            
            # Build kubectl command
            cmd = [
                self.kubectl_path,
                "--kubeconfig", kubeconfig,
                "--context", context,
                "-n", self.active_namespace,
                "delete",
                resource_type,
                resource_name
            ]
            
            # Execute command
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            logger.info(f"Successfully deleted resource {resource_type}/{resource_name} from cluster {self.active_cluster}")
            
            return {
                "success": True,
                "cluster": self.active_cluster,
                "namespace": self.active_namespace,
                "resource_type": resource_type,
                "resource_name": resource_name
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to delete resource: {e.stderr}")
            return {"success": False, "error": f"Failed to delete resource: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to delete resource: {str(e)}")
            return {"success": False, "error": f"Failed to delete resource: {str(e)}"}
    
    def get_resources(self, resource_type: str = None) -> Dict[str, Any]:
        """
        Get resources from the active cluster.
        
        Args:
            resource_type: Type of resources to get (if None, gets all types)
            
        Returns:
            Dictionary with resources
        """
        logger.info(f"Getting resources from active cluster")
        
        # Check if active cluster is set
        if not self.active_cluster:
            logger.error("No active cluster")
            return {"success": False, "error": "No active cluster"}
        
        try:
            # Get cluster configuration
            cluster_config = self.clusters[self.active_cluster]
            kubeconfig = cluster_config["kubeconfig"]
            context = cluster_config["context"]
            
            # Build kubectl command
            cmd = [
                self.kubectl_path,
                "--kubeconfig", kubeconfig,
                "--context", context,
                "-n", self.active_namespace,
                "get"
            ]
            
            if resource_type:
                cmd.append(resource_type)
            else:
                cmd.append("all")
            
            cmd.extend(["-o", "json"])
            
            # Execute command
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse JSON output
            resources = json.loads(result.stdout)
            
            logger.info(f"Successfully retrieved resources from cluster {self.active_cluster}")
            
            return {
                "success": True,
                "cluster": self.active_cluster,
                "namespace": self.active_namespace,
                "resources": resources
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get resources: {e.stderr}")
            return {"success": False, "error": f"Failed to get resources: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to get resources: {str(e)}")
            return {"success": False, "error": f"Failed to get resources: {str(e)}"}
    
    def get_resource(self, resource_type: str, resource_name: str) -> Dict[str, Any]:
        """
        Get a specific resource from the active cluster.
        
        Args:
            resource_type: Type of resource
            resource_name: Name of resource
            
        Returns:
            Dictionary with resource
        """
        logger.info(f"Getting resource {resource_type}/{resource_name} from active cluster")
        
        # Check if active cluster is set
        if not self.active_cluster:
            logger.error("No active cluster")
            return {"success": False, "error": "No active cluster"}
        
        try:
            # Get cluster configuration
            cluster_config = self.clusters[self.active_cluster]
            kubeconfig = cluster_config["kubeconfig"]
            context = cluster_config["context"]
            
            # Build kubectl command
            cmd = [
                self.kubectl_path,
                "--kubeconfig", kubeconfig,
                "--context", context,
                "-n", self.active_namespace,
                "get",
                resource_type,
                resource_name,
                "-o", "json"
            ]
            
            # Execute command
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse JSON output
            resource = json.loads(result.stdout)
            
            logger.info(f"Successfully retrieved resource {resource_type}/{resource_name} from cluster {self.active_cluster}")
            
            return {
                "success": True,
                "cluster": self.active_cluster,
                "namespace": self.active_namespace,
                "resource": resource
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get resource: {e.stderr}")
            return {"success": False, "error": f"Failed to get resource: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to get resource: {str(e)}")
            return {"success": False, "error": f"Failed to get resource: {str(e)}"}
    
    def get_namespaces(self) -> Dict[str, Any]:
        """
        Get namespaces from the active cluster.
        
        Returns:
            Dictionary with namespaces
        """
        logger.info(f"Getting namespaces from active cluster")
        
        # Check if active cluster is set
        if not self.active_cluster:
            logger.error("No active cluster")
            return {"success": False, "error": "No active cluster"}
        
        try:
            # Get cluster configuration
            cluster_config = self.clusters[self.active_cluster]
            kubeconfig = cluster_config["kubeconfig"]
            context = cluster_config["context"]
            
            # Build kubectl command
            cmd = [
                self.kubectl_path,
                "--kubeconfig", kubeconfig,
                "--context", context,
                "get",
                "namespaces",
                "-o", "json"
            ]
            
            # Execute command
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse JSON output
            namespaces = json.loads(result.stdout)
            
            logger.info(f"Successfully retrieved namespaces from cluster {self.active_cluster}")
            
            return {
                "success": True,
                "cluster": self.active_cluster,
                "namespaces": namespaces
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get namespaces: {e.stderr}")
            return {"success": False, "error": f"Failed to get namespaces: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to get namespaces: {str(e)}")
            return {"success": False, "error": f"Failed to get namespaces: {str(e)}"}
    
    def create_namespace(self, namespace: str) -> Dict[str, Any]:
        """
        Create a namespace in the active cluster.
        
        Args:
            namespace: Name of namespace
            
        Returns:
            Dictionary with creation result
        """
        logger.info(f"Creating namespace {namespace} in active cluster")
        
        # Check if active cluster is set
        if not self.active_cluster:
            logger.error("No active cluster")
            return {"success": False, "error": "No active cluster"}
        
        try:
            # Get cluster configuration
            cluster_config = self.clusters[self.active_cluster]
            kubeconfig = cluster_config["kubeconfig"]
            context = cluster_config["context"]
            
            # Build kubectl command
            cmd = [
                self.kubectl_path,
                "--kubeconfig", kubeconfig,
                "--context", context,
                "create",
                "namespace",
                namespace
            ]
            
            # Execute command
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            logger.info(f"Successfully created namespace {namespace} in cluster {self.active_cluster}")
            
            return {
                "success": True,
                "cluster": self.active_cluster,
                "namespace": namespace
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create namespace: {e.stderr}")
            return {"success": False, "error": f"Failed to create namespace: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to create namespace: {str(e)}")
            return {"success": False, "error": f"Failed to create namespace: {str(e)}"}
    
    def delete_namespace(self, namespace: str) -> Dict[str, Any]:
        """
        Delete a namespace from the active cluster.
        
        Args:
            namespace: Name of namespace
            
        Returns:
            Dictionary with deletion result
        """
        logger.info(f"Deleting namespace {namespace} from active cluster")
        
        # Check if active cluster is set
        if not self.active_cluster:
            logger.error("No active cluster")
            return {"success": False, "error": "No active cluster"}
        
        # Check if trying to delete active namespace
        if namespace == self.active_namespace:
            logger.error("Cannot delete active namespace")
            return {"success": False, "error": "Cannot delete active namespace"}
        
        try:
            # Get cluster configuration
            cluster_config = self.clusters[self.active_cluster]
            kubeconfig = cluster_config["kubeconfig"]
            context = cluster_config["context"]
            
            # Build kubectl command
            cmd = [
                self.kubectl_path,
                "--kubeconfig", kubeconfig,
                "--context", context,
                "delete",
                "namespace",
                namespace
            ]
            
            # Execute command
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            logger.info(f"Successfully deleted namespace {namespace} from cluster {self.active_cluster}")
            
            return {
                "success": True,
                "cluster": self.active_cluster,
                "namespace": namespace
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to delete namespace: {e.stderr}")
            return {"success": False, "error": f"Failed to delete namespace: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to delete namespace: {str(e)}")
            return {"success": False, "error": f"Failed to delete namespace: {str(e)}"}
    
    def get_cluster_info(self) -> Dict[str, Any]:
        """
        Get information about the active cluster.
        
        Returns:
            Dictionary with cluster information
        """
        logger.info(f"Getting information about active cluster")
        
        # Check if active cluster is set
        if not self.active_cluster:
            logger.error("No active cluster")
            return {"success": False, "error": "No active cluster"}
        
        try:
            # Get cluster configuration
            cluster_config = self.clusters[self.active_cluster]
            kubeconfig = cluster_config["kubeconfig"]
            context = cluster_config["context"]
            
            # Build kubectl command
            cmd = [
                self.kubectl_path,
                "--kubeconfig", kubeconfig,
                "--context", context,
                "cluster-info"
            ]
            
            # Execute command
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            logger.info(f"Successfully retrieved information about cluster {self.active_cluster}")
            
            return {
                "success": True,
                "cluster": self.active_cluster,
                "info": result.stdout
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get cluster info: {e.stderr}")
            return {"success": False, "error": f"Failed to get cluster info: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to get cluster info: {str(e)}")
            return {"success": False, "error": f"Failed to get cluster info: {str(e)}"}
    
    def get_nodes(self) -> Dict[str, Any]:
        """
        Get nodes in the active cluster.
        
        Returns:
            Dictionary with nodes
        """
        logger.info(f"Getting nodes in active cluster")
        
        # Check if active cluster is set
        if not self.active_cluster:
            logger.error("No active cluster")
            return {"success": False, "error": "No active cluster"}
        
        try:
            # Get cluster configuration
            cluster_config = self.clusters[self.active_cluster]
            kubeconfig = cluster_config["kubeconfig"]
            context = cluster_config["context"]
            
            # Build kubectl command
            cmd = [
                self.kubectl_path,
                "--kubeconfig", kubeconfig,
                "--context", context,
                "get",
                "nodes",
                "-o", "json"
            ]
            
            # Execute command
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse JSON output
            nodes = json.loads(result.stdout)
            
            logger.info(f"Successfully retrieved nodes in cluster {self.active_cluster}")
            
            return {
                "success": True,
                "cluster": self.active_cluster,
                "nodes": nodes
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get nodes: {e.stderr}")
            return {"success": False, "error": f"Failed to get nodes: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to get nodes: {str(e)}")
            return {"success": False, "error": f"Failed to get nodes: {str(e)}"}
    
    def get_pods(self) -> Dict[str, Any]:
        """
        Get pods in the active namespace.
        
        Returns:
            Dictionary with pods
        """
        logger.info(f"Getting pods in active namespace")
        
        # Check if active cluster is set
        if not self.active_cluster:
            logger.error("No active cluster")
            return {"success": False, "error": "No active cluster"}
        
        try:
            # Get cluster configuration
            cluster_config = self.clusters[self.active_cluster]
            kubeconfig = cluster_config["kubeconfig"]
            context = cluster_config["context"]
            
            # Build kubectl command
            cmd = [
                self.kubectl_path,
                "--kubeconfig", kubeconfig,
                "--context", context,
                "-n", self.active_namespace,
                "get",
                "pods",
                "-o", "json"
            ]
            
            # Execute command
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse JSON output
            pods = json.loads(result.stdout)
            
            logger.info(f"Successfully retrieved pods in namespace {self.active_namespace}")
            
            return {
                "success": True,
                "cluster": self.active_cluster,
                "namespace": self.active_namespace,
                "pods": pods
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get pods: {e.stderr}")
            return {"success": False, "error": f"Failed to get pods: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to get pods: {str(e)}")
            return {"success": False, "error": f"Failed to get pods: {str(e)}"}
    
    def get_services(self) -> Dict[str, Any]:
        """
        Get services in the active namespace.
        
        Returns:
            Dictionary with services
        """
        logger.info(f"Getting services in active namespace")
        
        # Check if active cluster is set
        if not self.active_cluster:
            logger.error("No active cluster")
            return {"success": False, "error": "No active cluster"}
        
        try:
            # Get cluster configuration
            cluster_config = self.clusters[self.active_cluster]
            kubeconfig = cluster_config["kubeconfig"]
            context = cluster_config["context"]
            
            # Build kubectl command
            cmd = [
                self.kubectl_path,
                "--kubeconfig", kubeconfig,
                "--context", context,
                "-n", self.active_namespace,
                "get",
                "services",
                "-o", "json"
            ]
            
            # Execute command
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse JSON output
            services = json.loads(result.stdout)
            
            logger.info(f"Successfully retrieved services in namespace {self.active_namespace}")
            
            return {
                "success": True,
                "cluster": self.active_cluster,
                "namespace": self.active_namespace,
                "services": services
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get services: {e.stderr}")
            return {"success": False, "error": f"Failed to get services: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to get services: {str(e)}")
            return {"success": False, "error": f"Failed to get services: {str(e)}"}
    
    def get_deployments(self) -> Dict[str, Any]:
        """
        Get deployments in the active namespace.
        
        Returns:
            Dictionary with deployments
        """
        logger.info(f"Getting deployments in active namespace")
        
        # Check if active cluster is set
        if not self.active_cluster:
            logger.error("No active cluster")
            return {"success": False, "error": "No active cluster"}
        
        try:
            # Get cluster configuration
            cluster_config = self.clusters[self.active_cluster]
            kubeconfig = cluster_config["kubeconfig"]
            context = cluster_config["context"]
            
            # Build kubectl command
            cmd = [
                self.kubectl_path,
                "--kubeconfig", kubeconfig,
                "--context", context,
                "-n", self.active_namespace,
                "get",
                "deployments",
                "-o", "json"
            ]
            
            # Execute command
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse JSON output
            deployments = json.loads(result.stdout)
            
            logger.info(f"Successfully retrieved deployments in namespace {self.active_namespace}")
            
            return {
                "success": True,
                "cluster": self.active_cluster,
                "namespace": self.active_namespace,
                "deployments": deployments
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get deployments: {e.stderr}")
            return {"success": False, "error": f"Failed to get deployments: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to get deployments: {str(e)}")
            return {"success": False, "error": f"Failed to get deployments: {str(e)}"}
    
    def _load_cluster_configurations(self):
        """Load cluster configurations from storage."""
        try:
            # In a real implementation, this would load from a database or file
            # For now, we'll just initialize with default configurations
            self.clusters = self._get_default_cluster_configurations()
            logger.info("Loaded cluster configurations")
        except Exception as e:
            logger.error(f"Failed to load cluster configurations: {str(e)}")
    
    def _save_cluster_configurations(self):
        """Save cluster configurations to storage."""
        try:
            # In a real implementation, this would save to a database or file
            # For now, we'll just log it
            logger.info(f"Saved {len(self.clusters)} cluster configurations")
        except Exception as e:
            logger.error(f"Failed to save cluster configurations: {str(e)}")
    
    def _get_default_cluster_configurations(self) -> Dict[str, Dict[str, Any]]:
        """
        Get default cluster configurations.
        
        Returns:
            Dictionary of cluster name -> cluster configuration
        """
        clusters = {}
        
        # Default local cluster
        clusters["local"] = {
            "kubeconfig": os.path.expanduser("~/.kube/config"),
            "context": "minikube",
            "namespace": "default"
        }
        
        return clusters
