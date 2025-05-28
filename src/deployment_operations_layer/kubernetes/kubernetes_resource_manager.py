"""
Kubernetes Resource Manager - Manages Kubernetes resources

This module provides functionality for managing Kubernetes resources,
including creation, updating, deletion, and monitoring.
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import os
import yaml
import subprocess
import tempfile
from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException

logger = logging.getLogger(__name__)

class KubernetesResourceManager:
    """
    Manages Kubernetes resources.
    
    This component is responsible for managing Kubernetes resources,
    including creation, updating, deletion, and monitoring.
    """
    
    def __init__(self, config_dict: Dict[str, Any] = None):
        """
        Initialize the Kubernetes Resource Manager.
        
        Args:
            config_dict: Configuration dictionary for the manager
        """
        self.config_dict = config_dict or {}
        self.kube_client = None
        self.api_client = None
        self.core_v1_api = None
        self.apps_v1_api = None
        self.batch_v1_api = None
        self.networking_v1_api = None
        self.rbac_v1_api = None
        self.custom_objects_api = None
        
        # Default namespace
        self.namespace = self.config_dict.get("namespace", "default")
        
        logger.info("Initializing Kubernetes Resource Manager")
    
    def initialize(self, kubeconfig: str = None, context: str = None):
        """
        Initialize the manager with Kubernetes client.
        
        Args:
            kubeconfig: Path to kubeconfig file
            context: Kubernetes context to use
            
        Returns:
            True if initialization successful, False otherwise
        """
        logger.info("Initializing Kubernetes Resource Manager")
        
        try:
            # Load Kubernetes configuration
            if kubeconfig:
                config.load_kube_config(config_file=kubeconfig, context=context)
            else:
                # Try to load from default location
                config.load_kube_config(context=context)
            
            # Create API clients
            self.api_client = client.ApiClient()
            self.core_v1_api = client.CoreV1Api(self.api_client)
            self.apps_v1_api = client.AppsV1Api(self.api_client)
            self.batch_v1_api = client.BatchV1Api(self.api_client)
            self.networking_v1_api = client.NetworkingV1Api(self.api_client)
            self.rbac_v1_api = client.RbacAuthorizationV1Api(self.api_client)
            self.custom_objects_api = client.CustomObjectsApi(self.api_client)
            
            logger.info("Kubernetes Resource Manager initialization successful")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Kubernetes Resource Manager: {str(e)}")
            return False
    
    def set_namespace(self, namespace: str):
        """
        Set the namespace to use.
        
        Args:
            namespace: Namespace to use
        """
        self.namespace = namespace
        logger.info(f"Set namespace to {namespace}")
    
    def get_namespace(self) -> str:
        """
        Get the current namespace.
        
        Returns:
            Current namespace
        """
        return self.namespace
    
    def create_namespace(self, name: str, labels: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Create a namespace.
        
        Args:
            name: Name of the namespace
            labels: Labels to apply to the namespace
            
        Returns:
            Dictionary with creation result
        """
        logger.info(f"Creating namespace {name}")
        
        try:
            # Create namespace object
            namespace = client.V1Namespace(
                metadata=client.V1ObjectMeta(
                    name=name,
                    labels=labels
                )
            )
            
            # Create namespace
            result = self.core_v1_api.create_namespace(namespace)
            
            logger.info(f"Successfully created namespace {name}")
            
            return {
                "success": True,
                "namespace": name,
                "result": result.to_dict()
            }
        except ApiException as e:
            logger.error(f"Failed to create namespace: {str(e)}")
            return {"success": False, "error": f"Failed to create namespace: {str(e)}"}
        except Exception as e:
            logger.error(f"Failed to create namespace: {str(e)}")
            return {"success": False, "error": f"Failed to create namespace: {str(e)}"}
    
    def delete_namespace(self, name: str) -> Dict[str, Any]:
        """
        Delete a namespace.
        
        Args:
            name: Name of the namespace
            
        Returns:
            Dictionary with deletion result
        """
        logger.info(f"Deleting namespace {name}")
        
        try:
            # Delete namespace
            result = self.core_v1_api.delete_namespace(name)
            
            logger.info(f"Successfully deleted namespace {name}")
            
            return {
                "success": True,
                "namespace": name,
                "result": result.to_dict()
            }
        except ApiException as e:
            logger.error(f"Failed to delete namespace: {str(e)}")
            return {"success": False, "error": f"Failed to delete namespace: {str(e)}"}
        except Exception as e:
            logger.error(f"Failed to delete namespace: {str(e)}")
            return {"success": False, "error": f"Failed to delete namespace: {str(e)}"}
    
    def get_namespaces(self) -> Dict[str, Any]:
        """
        Get all namespaces.
        
        Returns:
            Dictionary with namespaces
        """
        logger.info("Getting all namespaces")
        
        try:
            # Get namespaces
            result = self.core_v1_api.list_namespace()
            
            # Extract namespaces
            namespaces = []
            for item in result.items:
                namespaces.append(item.to_dict())
            
            logger.info(f"Successfully retrieved {len(namespaces)} namespaces")
            
            return {
                "success": True,
                "namespaces": namespaces
            }
        except ApiException as e:
            logger.error(f"Failed to get namespaces: {str(e)}")
            return {"success": False, "error": f"Failed to get namespaces: {str(e)}"}
        except Exception as e:
            logger.error(f"Failed to get namespaces: {str(e)}")
            return {"success": False, "error": f"Failed to get namespaces: {str(e)}"}
    
    def create_deployment(self, name: str, image: str, replicas: int = 1, 
                        labels: Dict[str, str] = None, namespace: str = None) -> Dict[str, Any]:
        """
        Create a deployment.
        
        Args:
            name: Name of the deployment
            image: Container image to use
            replicas: Number of replicas
            labels: Labels to apply to the deployment
            namespace: Namespace to create the deployment in (if None, uses default)
            
        Returns:
            Dictionary with creation result
        """
        logger.info(f"Creating deployment {name}")
        
        try:
            # Set namespace
            if not namespace:
                namespace = self.namespace
            
            # Set default labels if not provided
            if not labels:
                labels = {"app": name}
            
            # Create deployment object
            deployment = client.V1Deployment(
                metadata=client.V1ObjectMeta(
                    name=name,
                    labels=labels
                ),
                spec=client.V1DeploymentSpec(
                    replicas=replicas,
                    selector=client.V1LabelSelector(
                        match_labels=labels
                    ),
                    template=client.V1PodTemplateSpec(
                        metadata=client.V1ObjectMeta(
                            labels=labels
                        ),
                        spec=client.V1PodSpec(
                            containers=[
                                client.V1Container(
                                    name=name,
                                    image=image
                                )
                            ]
                        )
                    )
                )
            )
            
            # Create deployment
            result = self.apps_v1_api.create_namespaced_deployment(
                namespace=namespace,
                body=deployment
            )
            
            logger.info(f"Successfully created deployment {name} in namespace {namespace}")
            
            return {
                "success": True,
                "deployment": name,
                "namespace": namespace,
                "result": result.to_dict()
            }
        except ApiException as e:
            logger.error(f"Failed to create deployment: {str(e)}")
            return {"success": False, "error": f"Failed to create deployment: {str(e)}"}
        except Exception as e:
            logger.error(f"Failed to create deployment: {str(e)}")
            return {"success": False, "error": f"Failed to create deployment: {str(e)}"}
    
    def delete_deployment(self, name: str, namespace: str = None) -> Dict[str, Any]:
        """
        Delete a deployment.
        
        Args:
            name: Name of the deployment
            namespace: Namespace the deployment is in (if None, uses default)
            
        Returns:
            Dictionary with deletion result
        """
        logger.info(f"Deleting deployment {name}")
        
        try:
            # Set namespace
            if not namespace:
                namespace = self.namespace
            
            # Delete deployment
            result = self.apps_v1_api.delete_namespaced_deployment(
                name=name,
                namespace=namespace
            )
            
            logger.info(f"Successfully deleted deployment {name} from namespace {namespace}")
            
            return {
                "success": True,
                "deployment": name,
                "namespace": namespace,
                "result": result.to_dict()
            }
        except ApiException as e:
            logger.error(f"Failed to delete deployment: {str(e)}")
            return {"success": False, "error": f"Failed to delete deployment: {str(e)}"}
        except Exception as e:
            logger.error(f"Failed to delete deployment: {str(e)}")
            return {"success": False, "error": f"Failed to delete deployment: {str(e)}"}
    
    def get_deployments(self, namespace: str = None) -> Dict[str, Any]:
        """
        Get all deployments in a namespace.
        
        Args:
            namespace: Namespace to get deployments from (if None, uses default)
            
        Returns:
            Dictionary with deployments
        """
        logger.info("Getting deployments")
        
        try:
            # Set namespace
            if not namespace:
                namespace = self.namespace
            
            # Get deployments
            result = self.apps_v1_api.list_namespaced_deployment(namespace=namespace)
            
            # Extract deployments
            deployments = []
            for item in result.items:
                deployments.append(item.to_dict())
            
            logger.info(f"Successfully retrieved {len(deployments)} deployments from namespace {namespace}")
            
            return {
                "success": True,
                "namespace": namespace,
                "deployments": deployments
            }
        except ApiException as e:
            logger.error(f"Failed to get deployments: {str(e)}")
            return {"success": False, "error": f"Failed to get deployments: {str(e)}"}
        except Exception as e:
            logger.error(f"Failed to get deployments: {str(e)}")
            return {"success": False, "error": f"Failed to get deployments: {str(e)}"}
    
    def create_service(self, name: str, selector: Dict[str, str], ports: List[Dict[str, Any]], 
                     service_type: str = "ClusterIP", namespace: str = None) -> Dict[str, Any]:
        """
        Create a service.
        
        Args:
            name: Name of the service
            selector: Label selector for the service
            ports: List of port configurations
            service_type: Type of service (ClusterIP, NodePort, LoadBalancer)
            namespace: Namespace to create the service in (if None, uses default)
            
        Returns:
            Dictionary with creation result
        """
        logger.info(f"Creating service {name}")
        
        try:
            # Set namespace
            if not namespace:
                namespace = self.namespace
            
            # Create service ports
            service_ports = []
            for port_config in ports:
                port = client.V1ServicePort(
                    name=port_config.get("name"),
                    port=port_config["port"],
                    target_port=port_config.get("target_port", port_config["port"]),
                    protocol=port_config.get("protocol", "TCP")
                )
                service_ports.append(port)
            
            # Create service object
            service = client.V1Service(
                metadata=client.V1ObjectMeta(
                    name=name
                ),
                spec=client.V1ServiceSpec(
                    selector=selector,
                    ports=service_ports,
                    type=service_type
                )
            )
            
            # Create service
            result = self.core_v1_api.create_namespaced_service(
                namespace=namespace,
                body=service
            )
            
            logger.info(f"Successfully created service {name} in namespace {namespace}")
            
            return {
                "success": True,
                "service": name,
                "namespace": namespace,
                "result": result.to_dict()
            }
        except ApiException as e:
            logger.error(f"Failed to create service: {str(e)}")
            return {"success": False, "error": f"Failed to create service: {str(e)}"}
        except Exception as e:
            logger.error(f"Failed to create service: {str(e)}")
            return {"success": False, "error": f"Failed to create service: {str(e)}"}
    
    def delete_service(self, name: str, namespace: str = None) -> Dict[str, Any]:
        """
        Delete a service.
        
        Args:
            name: Name of the service
            namespace: Namespace the service is in (if None, uses default)
            
        Returns:
            Dictionary with deletion result
        """
        logger.info(f"Deleting service {name}")
        
        try:
            # Set namespace
            if not namespace:
                namespace = self.namespace
            
            # Delete service
            result = self.core_v1_api.delete_namespaced_service(
                name=name,
                namespace=namespace
            )
            
            logger.info(f"Successfully deleted service {name} from namespace {namespace}")
            
            return {
                "success": True,
                "service": name,
                "namespace": namespace,
                "result": result.to_dict()
            }
        except ApiException as e:
            logger.error(f"Failed to delete service: {str(e)}")
            return {"success": False, "error": f"Failed to delete service: {str(e)}"}
        except Exception as e:
            logger.error(f"Failed to delete service: {str(e)}")
            return {"success": False, "error": f"Failed to delete service: {str(e)}"}
    
    def get_services(self, namespace: str = None) -> Dict[str, Any]:
        """
        Get all services in a namespace.
        
        Args:
            namespace: Namespace to get services from (if None, uses default)
            
        Returns:
            Dictionary with services
        """
        logger.info("Getting services")
        
        try:
            # Set namespace
            if not namespace:
                namespace = self.namespace
            
            # Get services
            result = self.core_v1_api.list_namespaced_service(namespace=namespace)
            
            # Extract services
            services = []
            for item in result.items:
                services.append(item.to_dict())
            
            logger.info(f"Successfully retrieved {len(services)} services from namespace {namespace}")
            
            return {
                "success": True,
                "namespace": namespace,
                "services": services
            }
        except ApiException as e:
            logger.error(f"Failed to get services: {str(e)}")
            return {"success": False, "error": f"Failed to get services: {str(e)}"}
        except Exception as e:
            logger.error(f"Failed to get services: {str(e)}")
            return {"success": False, "error": f"Failed to get services: {str(e)}"}
    
    def create_configmap(self, name: str, data: Dict[str, str], 
                       namespace: str = None) -> Dict[str, Any]:
        """
        Create a ConfigMap.
        
        Args:
            name: Name of the ConfigMap
            data: Data for the ConfigMap
            namespace: Namespace to create the ConfigMap in (if None, uses default)
            
        Returns:
            Dictionary with creation result
        """
        logger.info(f"Creating ConfigMap {name}")
        
        try:
            # Set namespace
            if not namespace:
                namespace = self.namespace
            
            # Create ConfigMap object
            configmap = client.V1ConfigMap(
                metadata=client.V1ObjectMeta(
                    name=name
                ),
                data=data
            )
            
            # Create ConfigMap
            result = self.core_v1_api.create_namespaced_config_map(
                namespace=namespace,
                body=configmap
            )
            
            logger.info(f"Successfully created ConfigMap {name} in namespace {namespace}")
            
            return {
                "success": True,
                "configmap": name,
                "namespace": namespace,
                "result": result.to_dict()
            }
        except ApiException as e:
            logger.error(f"Failed to create ConfigMap: {str(e)}")
            return {"success": False, "error": f"Failed to create ConfigMap: {str(e)}"}
        except Exception as e:
            logger.error(f"Failed to create ConfigMap: {str(e)}")
            return {"success": False, "error": f"Failed to create ConfigMap: {str(e)}"}
    
    def delete_configmap(self, name: str, namespace: str = None) -> Dict[str, Any]:
        """
        Delete a ConfigMap.
        
        Args:
            name: Name of the ConfigMap
            namespace: Namespace the ConfigMap is in (if None, uses default)
            
        Returns:
            Dictionary with deletion result
        """
        logger.info(f"Deleting ConfigMap {name}")
        
        try:
            # Set namespace
            if not namespace:
                namespace = self.namespace
            
            # Delete ConfigMap
            result = self.core_v1_api.delete_namespaced_config_map(
                name=name,
                namespace=namespace
            )
            
            logger.info(f"Successfully deleted ConfigMap {name} from namespace {namespace}")
            
            return {
                "success": True,
                "configmap": name,
                "namespace": namespace,
                "result": result.to_dict()
            }
        except ApiException as e:
            logger.error(f"Failed to delete ConfigMap: {str(e)}")
            return {"success": False, "error": f"Failed to delete ConfigMap: {str(e)}"}
        except Exception as e:
            logger.error(f"Failed to delete ConfigMap: {str(e)}")
            return {"success": False, "error": f"Failed to delete ConfigMap: {str(e)}"}
    
    def get_configmaps(self, namespace: str = None) -> Dict[str, Any]:
        """
        Get all ConfigMaps in a namespace.
        
        Args:
            namespace: Namespace to get ConfigMaps from (if None, uses default)
            
        Returns:
            Dictionary with ConfigMaps
        """
        logger.info("Getting ConfigMaps")
        
        try:
            # Set namespace
            if not namespace:
                namespace = self.namespace
            
            # Get ConfigMaps
            result = self.core_v1_api.list_namespaced_config_map(namespace=namespace)
            
            # Extract ConfigMaps
            configmaps = []
            for item in result.items:
                configmaps.append(item.to_dict())
            
            logger.info(f"Successfully retrieved {len(configmaps)} ConfigMaps from namespace {namespace}")
            
            return {
                "success": True,
                "namespace": namespace,
                "configmaps": configmaps
            }
        except ApiException as e:
            logger.error(f"Failed to get ConfigMaps: {str(e)}")
            return {"success": False, "error": f"Failed to get ConfigMaps: {str(e)}"}
        except Exception as e:
            logger.error(f"Failed to get ConfigMaps: {str(e)}")
            return {"success": False, "error": f"Failed to get ConfigMaps: {str(e)}"}
    
    def create_secret(self, name: str, data: Dict[str, str], secret_type: str = "Opaque", 
                    namespace: str = None) -> Dict[str, Any]:
        """
        Create a Secret.
        
        Args:
            name: Name of the Secret
            data: Data for the Secret (values will be base64 encoded)
            secret_type: Type of Secret
            namespace: Namespace to create the Secret in (if None, uses default)
            
        Returns:
            Dictionary with creation result
        """
        logger.info(f"Creating Secret {name}")
        
        try:
            # Set namespace
            if not namespace:
                namespace = self.namespace
            
            # Create Secret object
            secret = client.V1Secret(
                metadata=client.V1ObjectMeta(
                    name=name
                ),
                string_data=data,
                type=secret_type
            )
            
            # Create Secret
            result = self.core_v1_api.create_namespaced_secret(
                namespace=namespace,
                body=secret
            )
            
            logger.info(f"Successfully created Secret {name} in namespace {namespace}")
            
            return {
                "success": True,
                "secret": name,
                "namespace": namespace,
                "result": result.to_dict()
            }
        except ApiException as e:
            logger.error(f"Failed to create Secret: {str(e)}")
            return {"success": False, "error": f"Failed to create Secret: {str(e)}"}
        except Exception as e:
            logger.error(f"Failed to create Secret: {str(e)}")
            return {"success": False, "error": f"Failed to create Secret: {str(e)}"}
    
    def delete_secret(self, name: str, namespace: str = None) -> Dict[str, Any]:
        """
        Delete a Secret.
        
        Args:
            name: Name of the Secret
            namespace: Namespace the Secret is in (if None, uses default)
            
        Returns:
            Dictionary with deletion result
        """
        logger.info(f"Deleting Secret {name}")
        
        try:
            # Set namespace
            if not namespace:
                namespace = self.namespace
            
            # Delete Secret
            result = self.core_v1_api.delete_namespaced_secret(
                name=name,
                namespace=namespace
            )
            
            logger.info(f"Successfully deleted Secret {name} from namespace {namespace}")
            
            return {
                "success": True,
                "secret": name,
                "namespace": namespace,
                "result": result.to_dict()
            }
        except ApiException as e:
            logger.error(f"Failed to delete Secret: {str(e)}")
            return {"success": False, "error": f"Failed to delete Secret: {str(e)}"}
        except Exception as e:
            logger.error(f"Failed to delete Secret: {str(e)}")
            return {"success": False, "error": f"Failed to delete Secret: {str(e)}"}
    
    def get_secrets(self, namespace: str = None) -> Dict[str, Any]:
        """
        Get all Secrets in a namespace.
        
        Args:
            namespace: Namespace to get Secrets from (if None, uses default)
            
        Returns:
            Dictionary with Secrets
        """
        logger.info("Getting Secrets")
        
        try:
            # Set namespace
            if not namespace:
                namespace = self.namespace
            
            # Get Secrets
            result = self.core_v1_api.list_namespaced_secret(namespace=namespace)
            
            # Extract Secrets
            secrets = []
            for item in result.items:
                secrets.append(item.to_dict())
            
            logger.info(f"Successfully retrieved {len(secrets)} Secrets from namespace {namespace}")
            
            return {
                "success": True,
                "namespace": namespace,
                "secrets": secrets
            }
        except ApiException as e:
            logger.error(f"Failed to get Secrets: {str(e)}")
            return {"success": False, "error": f"Failed to get Secrets: {str(e)}"}
        except Exception as e:
            logger.error(f"Failed to get Secrets: {str(e)}")
            return {"success": False, "error": f"Failed to get Secrets: {str(e)}"}
    
    def create_ingress(self, name: str, rules: List[Dict[str, Any]], 
                     namespace: str = None) -> Dict[str, Any]:
        """
        Create an Ingress.
        
        Args:
            name: Name of the Ingress
            rules: List of Ingress rules
            namespace: Namespace to create the Ingress in (if None, uses default)
            
        Returns:
            Dictionary with creation result
        """
        logger.info(f"Creating Ingress {name}")
        
        try:
            # Set namespace
            if not namespace:
                namespace = self.namespace
            
            # Create Ingress rules
            ingress_rules = []
            for rule_config in rules:
                # Create HTTP paths
                http_paths = []
                for path_config in rule_config.get("paths", []):
                    http_path = client.V1HTTPIngressPath(
                        path=path_config["path"],
                        path_type=path_config.get("path_type", "Prefix"),
                        backend=client.V1IngressBackend(
                            service=client.V1IngressServiceBackend(
                                name=path_config["service_name"],
                                port=client.V1ServiceBackendPort(
                                    number=path_config["service_port"]
                                )
                            )
                        )
                    )
                    http_paths.append(http_path)
                
                # Create rule
                rule = client.V1IngressRule(
                    host=rule_config.get("host"),
                    http=client.V1HTTPIngressRuleValue(
                        paths=http_paths
                    )
                )
                ingress_rules.append(rule)
            
            # Create Ingress object
            ingress = client.V1Ingress(
                metadata=client.V1ObjectMeta(
                    name=name
                ),
                spec=client.V1IngressSpec(
                    rules=ingress_rules
                )
            )
            
            # Create Ingress
            result = self.networking_v1_api.create_namespaced_ingress(
                namespace=namespace,
                body=ingress
            )
            
            logger.info(f"Successfully created Ingress {name} in namespace {namespace}")
            
            return {
                "success": True,
                "ingress": name,
                "namespace": namespace,
                "result": result.to_dict()
            }
        except ApiException as e:
            logger.error(f"Failed to create Ingress: {str(e)}")
            return {"success": False, "error": f"Failed to create Ingress: {str(e)}"}
        except Exception as e:
            logger.error(f"Failed to create Ingress: {str(e)}")
            return {"success": False, "error": f"Failed to create Ingress: {str(e)}"}
    
    def delete_ingress(self, name: str, namespace: str = None) -> Dict[str, Any]:
        """
        Delete an Ingress.
        
        Args:
            name: Name of the Ingress
            namespace: Namespace the Ingress is in (if None, uses default)
            
        Returns:
            Dictionary with deletion result
        """
        logger.info(f"Deleting Ingress {name}")
        
        try:
            # Set namespace
            if not namespace:
                namespace = self.namespace
            
            # Delete Ingress
            result = self.networking_v1_api.delete_namespaced_ingress(
                name=name,
                namespace=namespace
            )
            
            logger.info(f"Successfully deleted Ingress {name} from namespace {namespace}")
            
            return {
                "success": True,
                "ingress": name,
                "namespace": namespace,
                "result": result.to_dict()
            }
        except ApiException as e:
            logger.error(f"Failed to delete Ingress: {str(e)}")
            return {"success": False, "error": f"Failed to delete Ingress: {str(e)}"}
        except Exception as e:
            logger.error(f"Failed to delete Ingress: {str(e)}")
            return {"success": False, "error": f"Failed to delete Ingress: {str(e)}"}
    
    def get_ingresses(self, namespace: str = None) -> Dict[str, Any]:
        """
        Get all Ingresses in a namespace.
        
        Args:
            namespace: Namespace to get Ingresses from (if None, uses default)
            
        Returns:
            Dictionary with Ingresses
        """
        logger.info("Getting Ingresses")
        
        try:
            # Set namespace
            if not namespace:
                namespace = self.namespace
            
            # Get Ingresses
            result = self.networking_v1_api.list_namespaced_ingress(namespace=namespace)
            
            # Extract Ingresses
            ingresses = []
            for item in result.items:
                ingresses.append(item.to_dict())
            
            logger.info(f"Successfully retrieved {len(ingresses)} Ingresses from namespace {namespace}")
            
            return {
                "success": True,
                "namespace": namespace,
                "ingresses": ingresses
            }
        except ApiException as e:
            logger.error(f"Failed to get Ingresses: {str(e)}")
            return {"success": False, "error": f"Failed to get Ingresses: {str(e)}"}
        except Exception as e:
            logger.error(f"Failed to get Ingresses: {str(e)}")
            return {"success": False, "error": f"Failed to get Ingresses: {str(e)}"}
    
    def apply_yaml(self, yaml_content: str, namespace: str = None) -> Dict[str, Any]:
        """
        Apply a YAML manifest.
        
        Args:
            yaml_content: YAML manifest content
            namespace: Namespace to apply the manifest in (if None, uses default)
            
        Returns:
            Dictionary with application result
        """
        logger.info("Applying YAML manifest")
        
        try:
            # Set namespace
            if not namespace:
                namespace = self.namespace
            
            # Create temporary file for manifest
            with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
                f.write(yaml_content.encode())
                manifest_file = f.name
            
            try:
                # Build kubectl command
                cmd = [
                    "kubectl",
                    "apply",
                    "-f", manifest_file,
                    "-n", namespace
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
                
                logger.info(f"Successfully applied YAML manifest in namespace {namespace}")
                
                return {
                    "success": True,
                    "namespace": namespace,
                    "resources": resources,
                    "output": result.stdout
                }
            finally:
                # Clean up temporary file
                os.unlink(manifest_file)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to apply YAML manifest: {e.stderr}")
            return {"success": False, "error": f"Failed to apply YAML manifest: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to apply YAML manifest: {str(e)}")
            return {"success": False, "error": f"Failed to apply YAML manifest: {str(e)}"}
    
    def delete_yaml(self, yaml_content: str, namespace: str = None) -> Dict[str, Any]:
        """
        Delete resources defined in a YAML manifest.
        
        Args:
            yaml_content: YAML manifest content
            namespace: Namespace the resources are in (if None, uses default)
            
        Returns:
            Dictionary with deletion result
        """
        logger.info("Deleting resources from YAML manifest")
        
        try:
            # Set namespace
            if not namespace:
                namespace = self.namespace
            
            # Create temporary file for manifest
            with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
                f.write(yaml_content.encode())
                manifest_file = f.name
            
            try:
                # Build kubectl command
                cmd = [
                    "kubectl",
                    "delete",
                    "-f", manifest_file,
                    "-n", namespace
                ]
                
                # Execute command
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                
                logger.info(f"Successfully deleted resources from YAML manifest in namespace {namespace}")
                
                return {
                    "success": True,
                    "namespace": namespace,
                    "output": result.stdout
                }
            finally:
                # Clean up temporary file
                os.unlink(manifest_file)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to delete resources from YAML manifest: {e.stderr}")
            return {"success": False, "error": f"Failed to delete resources from YAML manifest: {e.stderr}"}
        except Exception as e:
            logger.error(f"Failed to delete resources from YAML manifest: {str(e)}")
            return {"success": False, "error": f"Failed to delete resources from YAML manifest: {str(e)}"}
    
    def watch_resources(self, resource_type: str, namespace: str = None, 
                      timeout_seconds: int = 60) -> Dict[str, Any]:
        """
        Watch resources of a specific type.
        
        Args:
            resource_type: Type of resource to watch
            namespace: Namespace to watch resources in (if None, uses default)
            timeout_seconds: Timeout in seconds
            
        Returns:
            Dictionary with watch result
        """
        logger.info(f"Watching {resource_type} resources")
        
        try:
            # Set namespace
            if not namespace:
                namespace = self.namespace
            
            # Create watch
            w = watch.Watch()
            
            # Watch resources
            events = []
            
            # Determine API method based on resource type
            if resource_type == "pods":
                method = self.core_v1_api.list_namespaced_pod
            elif resource_type == "services":
                method = self.core_v1_api.list_namespaced_service
            elif resource_type == "deployments":
                method = self.apps_v1_api.list_namespaced_deployment
            elif resource_type == "configmaps":
                method = self.core_v1_api.list_namespaced_config_map
            elif resource_type == "secrets":
                method = self.core_v1_api.list_namespaced_secret
            elif resource_type == "ingresses":
                method = self.networking_v1_api.list_namespaced_ingress
            else:
                logger.error(f"Unsupported resource type: {resource_type}")
                return {"success": False, "error": f"Unsupported resource type: {resource_type}"}
            
            # Watch resources
            for event in w.stream(method, namespace=namespace, timeout_seconds=timeout_seconds):
                event_type = event["type"]
                resource = event["object"].to_dict()
                
                events.append({
                    "type": event_type,
                    "resource": resource
                })
            
            logger.info(f"Successfully watched {resource_type} resources in namespace {namespace}")
            
            return {
                "success": True,
                "namespace": namespace,
                "resource_type": resource_type,
                "events": events
            }
        except ApiException as e:
            logger.error(f"Failed to watch resources: {str(e)}")
            return {"success": False, "error": f"Failed to watch resources: {str(e)}"}
        except Exception as e:
            logger.error(f"Failed to watch resources: {str(e)}")
            return {"success": False, "error": f"Failed to watch resources: {str(e)}"}
    
    def get_logs(self, pod_name: str, container_name: str = None, 
               namespace: str = None) -> Dict[str, Any]:
        """
        Get logs from a pod.
        
        Args:
            pod_name: Name of the pod
            container_name: Name of the container (if None, uses first container)
            namespace: Namespace the pod is in (if None, uses default)
            
        Returns:
            Dictionary with logs
        """
        logger.info(f"Getting logs from pod {pod_name}")
        
        try:
            # Set namespace
            if not namespace:
                namespace = self.namespace
            
            # Get logs
            logs = self.core_v1_api.read_namespaced_pod_log(
                name=pod_name,
                namespace=namespace,
                container=container_name
            )
            
            logger.info(f"Successfully retrieved logs from pod {pod_name} in namespace {namespace}")
            
            return {
                "success": True,
                "pod": pod_name,
                "container": container_name,
                "namespace": namespace,
                "logs": logs
            }
        except ApiException as e:
            logger.error(f"Failed to get logs: {str(e)}")
            return {"success": False, "error": f"Failed to get logs: {str(e)}"}
        except Exception as e:
            logger.error(f"Failed to get logs: {str(e)}")
            return {"success": False, "error": f"Failed to get logs: {str(e)}"}
    
    def exec_command(self, pod_name: str, command: List[str], container_name: str = None, 
                   namespace: str = None) -> Dict[str, Any]:
        """
        Execute a command in a pod.
        
        Args:
            pod_name: Name of the pod
            command: Command to execute
            container_name: Name of the container (if None, uses first container)
            namespace: Namespace the pod is in (if None, uses default)
            
        Returns:
            Dictionary with execution result
        """
        logger.info(f"Executing command in pod {pod_name}")
        
        try:
            # Set namespace
            if not namespace:
                namespace = self.namespace
            
            # Execute command
            exec_command = ["/bin/sh", "-c"]
            exec_command.append(" ".join(command))
            
            result = stream(
                self.core_v1_api.connect_get_namespaced_pod_exec,
                name=pod_name,
                namespace=namespace,
                container=container_name,
                command=exec_command,
                stderr=True,
                stdin=False,
                stdout=True,
                tty=False
            )
            
            logger.info(f"Successfully executed command in pod {pod_name} in namespace {namespace}")
            
            return {
                "success": True,
                "pod": pod_name,
                "container": container_name,
                "namespace": namespace,
                "command": command,
                "output": result
            }
        except ApiException as e:
            logger.error(f"Failed to execute command: {str(e)}")
            return {"success": False, "error": f"Failed to execute command: {str(e)}"}
        except Exception as e:
            logger.error(f"Failed to execute command: {str(e)}")
            return {"success": False, "error": f"Failed to execute command: {str(e)}"}
    
    def port_forward(self, pod_name: str, local_port: int, remote_port: int, 
                   namespace: str = None) -> Dict[str, Any]:
        """
        Forward a local port to a port on a pod.
        
        Args:
            pod_name: Name of the pod
            local_port: Local port
            remote_port: Remote port
            namespace: Namespace the pod is in (if None, uses default)
            
        Returns:
            Dictionary with port forwarding result
        """
        logger.info(f"Forwarding port {local_port} to port {remote_port} on pod {pod_name}")
        
        try:
            # Set namespace
            if not namespace:
                namespace = self.namespace
            
            # Build kubectl command
            cmd = [
                "kubectl",
                "port-forward",
                f"pod/{pod_name}",
                f"{local_port}:{remote_port}",
                "-n", namespace
            ]
            
            # Execute command (non-blocking)
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait a bit to ensure port forwarding is established
            time.sleep(2)
            
            # Check if process is still running
            if process.poll() is not None:
                # Process has terminated
                stdout, stderr = process.communicate()
                logger.error(f"Port forwarding failed: {stderr.decode()}")
                return {"success": False, "error": f"Port forwarding failed: {stderr.decode()}"}
            
            logger.info(f"Successfully forwarded port {local_port} to port {remote_port} on pod {pod_name} in namespace {namespace}")
            
            return {
                "success": True,
                "pod": pod_name,
                "namespace": namespace,
                "local_port": local_port,
                "remote_port": remote_port,
                "process": process
            }
        except Exception as e:
            logger.error(f"Failed to forward port: {str(e)}")
            return {"success": False, "error": f"Failed to forward port: {str(e)}"}
    
    def stop_port_forward(self, process) -> Dict[str, Any]:
        """
        Stop a port forwarding process.
        
        Args:
            process: Port forwarding process
            
        Returns:
            Dictionary with stop result
        """
        logger.info("Stopping port forwarding")
        
        try:
            # Terminate process
            process.terminate()
            
            # Wait for process to terminate
            process.wait()
            
            logger.info("Successfully stopped port forwarding")
            
            return {
                "success": True
            }
        except Exception as e:
            logger.error(f"Failed to stop port forwarding: {str(e)}")
            return {"success": False, "error": f"Failed to stop port forwarding: {str(e)}"}
