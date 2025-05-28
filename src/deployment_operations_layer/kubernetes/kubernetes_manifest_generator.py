"""
Kubernetes Manifest Generator for the Deployment Operations Layer.

This module provides manifest generation capabilities for Kubernetes deployments
across the Industriverse ecosystem.
"""

import os
import json
import logging
import uuid
import yaml
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class KubernetesManifestGenerator:
    """
    Generator for Kubernetes manifests.
    
    This class provides methods for generating Kubernetes manifests for
    various resource types, including deployments, services, and ingresses.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the Kubernetes Manifest Generator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.generator_id = config.get("generator_id", f"manifest-generator-{uuid.uuid4().hex[:8]}")
        self.namespace = config.get("namespace", "default")
        self.default_labels = config.get("default_labels", {})
        self.default_annotations = config.get("default_annotations", {})
        
        # Initialize template storage
        self.storage_type = config.get("storage_type", "file")
        self.storage_path = config.get("storage_path", "/tmp/k8s_templates")
        
        # Create storage directory if it doesn't exist
        if self.storage_type == "file":
            os.makedirs(self.storage_path, exist_ok=True)
        
        # Initialize security integration
        from ..security.security_integration import SecurityIntegration
        self.security = SecurityIntegration(config.get("security", {}))
        
        logger.info(f"Kubernetes Manifest Generator {self.generator_id} initialized")
    
    def generate_deployment(self, name: str, image: str, replicas: int = 1, options: Dict = None) -> Dict:
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
            # Initialize options
            if not options:
                options = {}
            
            # Get namespace from options or default
            namespace = options.get("namespace", self.namespace)
            
            # Get labels from options or default
            labels = self.default_labels.copy()
            if "labels" in options:
                labels.update(options["labels"])
            
            # Get annotations from options or default
            annotations = self.default_annotations.copy()
            if "annotations" in options:
                annotations.update(options["annotations"])
            
            # Get container options
            container_options = options.get("container", {})
            
            # Build deployment manifest
            manifest = {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {
                    "name": name,
                    "namespace": namespace,
                    "labels": labels,
                    "annotations": annotations
                },
                "spec": {
                    "replicas": replicas,
                    "selector": {
                        "matchLabels": {
                            "app": name
                        }
                    },
                    "template": {
                        "metadata": {
                            "labels": {
                                "app": name
                            }
                        },
                        "spec": {
                            "containers": [
                                {
                                    "name": name,
                                    "image": image,
                                    "imagePullPolicy": container_options.get("imagePullPolicy", "Always"),
                                    "resources": container_options.get("resources", {
                                        "limits": {
                                            "cpu": "500m",
                                            "memory": "512Mi"
                                        },
                                        "requests": {
                                            "cpu": "100m",
                                            "memory": "128Mi"
                                        }
                                    })
                                }
                            ]
                        }
                    }
                }
            }
            
            # Add container ports if provided
            if "ports" in container_options:
                manifest["spec"]["template"]["spec"]["containers"][0]["ports"] = container_options["ports"]
            
            # Add container environment variables if provided
            if "env" in container_options:
                manifest["spec"]["template"]["spec"]["containers"][0]["env"] = container_options["env"]
            
            # Add container volume mounts if provided
            if "volumeMounts" in container_options:
                manifest["spec"]["template"]["spec"]["containers"][0]["volumeMounts"] = container_options["volumeMounts"]
            
            # Add volumes if provided
            if "volumes" in options:
                manifest["spec"]["template"]["spec"]["volumes"] = options["volumes"]
            
            # Add image pull secrets if provided
            if "imagePullSecrets" in options:
                manifest["spec"]["template"]["spec"]["imagePullSecrets"] = options["imagePullSecrets"]
            
            # Add node selector if provided
            if "nodeSelector" in options:
                manifest["spec"]["template"]["spec"]["nodeSelector"] = options["nodeSelector"]
            
            # Add affinity if provided
            if "affinity" in options:
                manifest["spec"]["template"]["spec"]["affinity"] = options["affinity"]
            
            # Add tolerations if provided
            if "tolerations" in options:
                manifest["spec"]["template"]["spec"]["tolerations"] = options["tolerations"]
            
            # Add service account if provided
            if "serviceAccountName" in options:
                manifest["spec"]["template"]["spec"]["serviceAccountName"] = options["serviceAccountName"]
            
            # Add security context if provided
            if "securityContext" in options:
                manifest["spec"]["template"]["spec"]["securityContext"] = options["securityContext"]
            
            # Add container security context if provided
            if "securityContext" in container_options:
                manifest["spec"]["template"]["spec"]["containers"][0]["securityContext"] = container_options["securityContext"]
            
            # Add container liveness probe if provided
            if "livenessProbe" in container_options:
                manifest["spec"]["template"]["spec"]["containers"][0]["livenessProbe"] = container_options["livenessProbe"]
            
            # Add container readiness probe if provided
            if "readinessProbe" in container_options:
                manifest["spec"]["template"]["spec"]["containers"][0]["readinessProbe"] = container_options["readinessProbe"]
            
            # Add container startup probe if provided
            if "startupProbe" in container_options:
                manifest["spec"]["template"]["spec"]["containers"][0]["startupProbe"] = container_options["startupProbe"]
            
            # Add container command if provided
            if "command" in container_options:
                manifest["spec"]["template"]["spec"]["containers"][0]["command"] = container_options["command"]
            
            # Add container args if provided
            if "args" in container_options:
                manifest["spec"]["template"]["spec"]["containers"][0]["args"] = container_options["args"]
            
            # Add container working directory if provided
            if "workingDir" in container_options:
                manifest["spec"]["template"]["spec"]["containers"][0]["workingDir"] = container_options["workingDir"]
            
            # Add container lifecycle hooks if provided
            if "lifecycle" in container_options:
                manifest["spec"]["template"]["spec"]["containers"][0]["lifecycle"] = container_options["lifecycle"]
            
            # Add init containers if provided
            if "initContainers" in options:
                manifest["spec"]["template"]["spec"]["initContainers"] = options["initContainers"]
            
            # Add deployment strategy if provided
            if "strategy" in options:
                manifest["spec"]["strategy"] = options["strategy"]
            
            # Add revision history limit if provided
            if "revisionHistoryLimit" in options:
                manifest["spec"]["revisionHistoryLimit"] = options["revisionHistoryLimit"]
            
            # Add progress deadline seconds if provided
            if "progressDeadlineSeconds" in options:
                manifest["spec"]["progressDeadlineSeconds"] = options["progressDeadlineSeconds"]
            
            # Add min ready seconds if provided
            if "minReadySeconds" in options:
                manifest["spec"]["minReadySeconds"] = options["minReadySeconds"]
            
            # Add pod labels if provided
            if "podLabels" in options:
                for key, value in options["podLabels"].items():
                    manifest["spec"]["template"]["metadata"]["labels"][key] = value
            
            # Add pod annotations if provided
            if "podAnnotations" in options:
                if "annotations" not in manifest["spec"]["template"]["metadata"]:
                    manifest["spec"]["template"]["metadata"]["annotations"] = {}
                
                for key, value in options["podAnnotations"].items():
                    manifest["spec"]["template"]["metadata"]["annotations"][key] = value
            
            # Convert to YAML
            manifest_yaml = yaml.dump(manifest)
            
            # Save manifest to file
            manifest_id = options.get("manifest_id", uuid.uuid4().hex)
            manifest_file = os.path.join(self.storage_path, f"{manifest_id}.yaml")
            with open(manifest_file, "w") as f:
                f.write(manifest_yaml)
            
            return {
                "status": "success",
                "message": "Deployment manifest generated successfully",
                "manifest_id": manifest_id,
                "manifest_file": manifest_file,
                "manifest": manifest,
                "manifest_yaml": manifest_yaml
            }
        except Exception as e:
            logger.error(f"Error generating deployment manifest: {e}")
            return {"status": "error", "message": str(e)}
    
    def generate_service(self, name: str, port: int, target_port: int, selector: Dict, options: Dict = None) -> Dict:
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
            # Initialize options
            if not options:
                options = {}
            
            # Get namespace from options or default
            namespace = options.get("namespace", self.namespace)
            
            # Get labels from options or default
            labels = self.default_labels.copy()
            if "labels" in options:
                labels.update(options["labels"])
            
            # Get annotations from options or default
            annotations = self.default_annotations.copy()
            if "annotations" in options:
                annotations.update(options["annotations"])
            
            # Get service type
            service_type = options.get("type", "ClusterIP")
            
            # Build service manifest
            manifest = {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {
                    "name": name,
                    "namespace": namespace,
                    "labels": labels,
                    "annotations": annotations
                },
                "spec": {
                    "type": service_type,
                    "selector": selector,
                    "ports": [
                        {
                            "port": port,
                            "targetPort": target_port,
                            "protocol": options.get("protocol", "TCP")
                        }
                    ]
                }
            }
            
            # Add port name if provided
            if "portName" in options:
                manifest["spec"]["ports"][0]["name"] = options["portName"]
            
            # Add node port if provided
            if "nodePort" in options and service_type in ["NodePort", "LoadBalancer"]:
                manifest["spec"]["ports"][0]["nodePort"] = options["nodePort"]
            
            # Add additional ports if provided
            if "additionalPorts" in options:
                manifest["spec"]["ports"].extend(options["additionalPorts"])
            
            # Add external traffic policy if provided
            if "externalTrafficPolicy" in options:
                manifest["spec"]["externalTrafficPolicy"] = options["externalTrafficPolicy"]
            
            # Add health check node port if provided
            if "healthCheckNodePort" in options:
                manifest["spec"]["healthCheckNodePort"] = options["healthCheckNodePort"]
            
            # Add load balancer IP if provided
            if "loadBalancerIP" in options:
                manifest["spec"]["loadBalancerIP"] = options["loadBalancerIP"]
            
            # Add load balancer source ranges if provided
            if "loadBalancerSourceRanges" in options:
                manifest["spec"]["loadBalancerSourceRanges"] = options["loadBalancerSourceRanges"]
            
            # Add session affinity if provided
            if "sessionAffinity" in options:
                manifest["spec"]["sessionAffinity"] = options["sessionAffinity"]
            
            # Add session affinity config if provided
            if "sessionAffinityConfig" in options:
                manifest["spec"]["sessionAffinityConfig"] = options["sessionAffinityConfig"]
            
            # Add publish not ready addresses if provided
            if "publishNotReadyAddresses" in options:
                manifest["spec"]["publishNotReadyAddresses"] = options["publishNotReadyAddresses"]
            
            # Add IP families if provided
            if "ipFamilies" in options:
                manifest["spec"]["ipFamilies"] = options["ipFamilies"]
            
            # Add IP family policy if provided
            if "ipFamilyPolicy" in options:
                manifest["spec"]["ipFamilyPolicy"] = options["ipFamilyPolicy"]
            
            # Add cluster IP if provided
            if "clusterIP" in options:
                manifest["spec"]["clusterIP"] = options["clusterIP"]
            
            # Add cluster IPs if provided
            if "clusterIPs" in options:
                manifest["spec"]["clusterIPs"] = options["clusterIPs"]
            
            # Convert to YAML
            manifest_yaml = yaml.dump(manifest)
            
            # Save manifest to file
            manifest_id = options.get("manifest_id", uuid.uuid4().hex)
            manifest_file = os.path.join(self.storage_path, f"{manifest_id}.yaml")
            with open(manifest_file, "w") as f:
                f.write(manifest_yaml)
            
            return {
                "status": "success",
                "message": "Service manifest generated successfully",
                "manifest_id": manifest_id,
                "manifest_file": manifest_file,
                "manifest": manifest,
                "manifest_yaml": manifest_yaml
            }
        except Exception as e:
            logger.error(f"Error generating service manifest: {e}")
            return {"status": "error", "message": str(e)}
    
    def generate_ingress(self, name: str, rules: List[Dict], options: Dict = None) -> Dict:
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
            # Initialize options
            if not options:
                options = {}
            
            # Get namespace from options or default
            namespace = options.get("namespace", self.namespace)
            
            # Get labels from options or default
            labels = self.default_labels.copy()
            if "labels" in options:
                labels.update(options["labels"])
            
            # Get annotations from options or default
            annotations = self.default_annotations.copy()
            if "annotations" in options:
                annotations.update(options["annotations"])
            
            # Get ingress class name
            ingress_class_name = options.get("ingressClassName")
            
            # Build ingress manifest
            manifest = {
                "apiVersion": "networking.k8s.io/v1",
                "kind": "Ingress",
                "metadata": {
                    "name": name,
                    "namespace": namespace,
                    "labels": labels,
                    "annotations": annotations
                },
                "spec": {
                    "rules": []
                }
            }
            
            # Add ingress class name if provided
            if ingress_class_name:
                manifest["spec"]["ingressClassName"] = ingress_class_name
            
            # Add TLS if provided
            if "tls" in options:
                manifest["spec"]["tls"] = options["tls"]
            
            # Add default backend if provided
            if "defaultBackend" in options:
                manifest["spec"]["defaultBackend"] = options["defaultBackend"]
            
            # Add rules
            for rule in rules:
                ingress_rule = {}
                
                # Add host if provided
                if "host" in rule:
                    ingress_rule["host"] = rule["host"]
                
                # Add paths
                if "paths" in rule:
                    ingress_rule["http"] = {
                        "paths": []
                    }
                    
                    for path in rule["paths"]:
                        ingress_path = {
                            "path": path["path"],
                            "pathType": path.get("pathType", "Prefix"),
                            "backend": {
                                "service": {
                                    "name": path["serviceName"],
                                    "port": {
                                        "number": path["servicePort"]
                                    }
                                }
                            }
                        }
                        
                        ingress_rule["http"]["paths"].append(ingress_path)
                
                manifest["spec"]["rules"].append(ingress_rule)
            
            # Convert to YAML
            manifest_yaml = yaml.dump(manifest)
            
            # Save manifest to file
            manifest_id = options.get("manifest_id", uuid.uuid4().hex)
            manifest_file = os.path.join(self.storage_path, f"{manifest_id}.yaml")
            with open(manifest_file, "w") as f:
                f.write(manifest_yaml)
            
            return {
                "status": "success",
                "message": "Ingress manifest generated successfully",
                "manifest_id": manifest_id,
                "manifest_file": manifest_file,
                "manifest": manifest,
                "manifest_yaml": manifest_yaml
            }
        except Exception as e:
            logger.error(f"Error generating ingress manifest: {e}")
            return {"status": "error", "message": str(e)}
    
    def generate_configmap(self, name: str, data: Dict, options: Dict = None) -> Dict:
        """
        Generate a Kubernetes configmap manifest.
        
        Args:
            name: ConfigMap name
            data: ConfigMap data
            options: Additional options
            
        Returns:
            Dict: Generation results
        """
        try:
            # Initialize options
            if not options:
                options = {}
            
            # Get namespace from options or default
            namespace = options.get("namespace", self.namespace)
            
            # Get labels from options or default
            labels = self.default_labels.copy()
            if "labels" in options:
                labels.update(options["labels"])
            
            # Get annotations from options or default
            annotations = self.default_annotations.copy()
            if "annotations" in options:
                annotations.update(options["annotations"])
            
            # Build configmap manifest
            manifest = {
                "apiVersion": "v1",
                "kind": "ConfigMap",
                "metadata": {
                    "name": name,
                    "namespace": namespace,
                    "labels": labels,
                    "annotations": annotations
                },
                "data": data
            }
            
            # Convert to YAML
            manifest_yaml = yaml.dump(manifest)
            
            # Save manifest to file
            manifest_id = options.get("manifest_id", uuid.uuid4().hex)
            manifest_file = os.path.join(self.storage_path, f"{manifest_id}.yaml")
            with open(manifest_file, "w") as f:
                f.write(manifest_yaml)
            
            return {
                "status": "success",
                "message": "ConfigMap manifest generated successfully",
                "manifest_id": manifest_id,
                "manifest_file": manifest_file,
                "manifest": manifest,
                "manifest_yaml": manifest_yaml
            }
        except Exception as e:
            logger.error(f"Error generating configmap manifest: {e}")
            return {"status": "error", "message": str(e)}
    
    def generate_secret(self, name: str, data: Dict, options: Dict = None) -> Dict:
        """
        Generate a Kubernetes secret manifest.
        
        Args:
            name: Secret name
            data: Secret data
            options: Additional options
            
        Returns:
            Dict: Generation results
        """
        try:
            # Initialize options
            if not options:
                options = {}
            
            # Get namespace from options or default
            namespace = options.get("namespace", self.namespace)
            
            # Get labels from options or default
            labels = self.default_labels.copy()
            if "labels" in options:
                labels.update(options["labels"])
            
            # Get annotations from options or default
            annotations = self.default_annotations.copy()
            if "annotations" in options:
                annotations.update(options["annotations"])
            
            # Get secret type
            secret_type = options.get("type", "Opaque")
            
            # Build secret manifest
            manifest = {
                "apiVersion": "v1",
                "kind": "Secret",
                "metadata": {
                    "name": name,
                    "namespace": namespace,
                    "labels": labels,
                    "annotations": annotations
                },
                "type": secret_type,
                "data": {}
            }
            
            # Add data
            for key, value in data.items():
                # Encode value as base64
                import base64
                encoded_value = base64.b64encode(value.encode()).decode()
                manifest["data"][key] = encoded_value
            
            # Convert to YAML
            manifest_yaml = yaml.dump(manifest)
            
            # Save manifest to file
            manifest_id = options.get("manifest_id", uuid.uuid4().hex)
            manifest_file = os.path.join(self.storage_path, f"{manifest_id}.yaml")
            with open(manifest_file, "w") as f:
                f.write(manifest_yaml)
            
            return {
                "status": "success",
                "message": "Secret manifest generated successfully",
                "manifest_id": manifest_id,
                "manifest_file": manifest_file,
                "manifest": manifest,
                "manifest_yaml": manifest_yaml
            }
        except Exception as e:
            logger.error(f"Error generating secret manifest: {e}")
            return {"status": "error", "message": str(e)}
    
    def generate_namespace(self, name: str, options: Dict = None) -> Dict:
        """
        Generate a Kubernetes namespace manifest.
        
        Args:
            name: Namespace name
            options: Additional options
            
        Returns:
            Dict: Generation results
        """
        try:
            # Initialize options
            if not options:
                options = {}
            
            # Get labels from options or default
            labels = self.default_labels.copy()
            if "labels" in options:
                labels.update(options["labels"])
            
            # Get annotations from options or default
            annotations = self.default_annotations.copy()
            if "annotations" in options:
                annotations.update(options["annotations"])
            
            # Build namespace manifest
            manifest = {
                "apiVersion": "v1",
                "kind": "Namespace",
                "metadata": {
                    "name": name,
                    "labels": labels,
                    "annotations": annotations
                }
            }
            
            # Convert to YAML
            manifest_yaml = yaml.dump(manifest)
            
            # Save manifest to file
            manifest_id = options.get("manifest_id", uuid.uuid4().hex)
            manifest_file = os.path.join(self.storage_path, f"{manifest_id}.yaml")
            with open(manifest_file, "w") as f:
                f.write(manifest_yaml)
            
            return {
                "status": "success",
                "message": "Namespace manifest generated successfully",
                "manifest_id": manifest_id,
                "manifest_file": manifest_file,
                "manifest": manifest,
                "manifest_yaml": manifest_yaml
            }
        except Exception as e:
            logger.error(f"Error generating namespace manifest: {e}")
            return {"status": "error", "message": str(e)}
    
    def generate_service_account(self, name: str, options: Dict = None) -> Dict:
        """
        Generate a Kubernetes service account manifest.
        
        Args:
            name: Service account name
            options: Additional options
            
        Returns:
            Dict: Generation results
        """
        try:
            # Initialize options
            if not options:
                options = {}
            
            # Get namespace from options or default
            namespace = options.get("namespace", self.namespace)
            
            # Get labels from options or default
            labels = self.default_labels.copy()
            if "labels" in options:
                labels.update(options["labels"])
            
            # Get annotations from options or default
            annotations = self.default_annotations.copy()
            if "annotations" in options:
                annotations.update(options["annotations"])
            
            # Build service account manifest
            manifest = {
                "apiVersion": "v1",
                "kind": "ServiceAccount",
                "metadata": {
                    "name": name,
                    "namespace": namespace,
                    "labels": labels,
                    "annotations": annotations
                }
            }
            
            # Add image pull secrets if provided
            if "imagePullSecrets" in options:
                manifest["imagePullSecrets"] = options["imagePullSecrets"]
            
            # Add automount service account token if provided
            if "automountServiceAccountToken" in options:
                manifest["automountServiceAccountToken"] = options["automountServiceAccountToken"]
            
            # Convert to YAML
            manifest_yaml = yaml.dump(manifest)
            
            # Save manifest to file
            manifest_id = options.get("manifest_id", uuid.uuid4().hex)
            manifest_file = os.path.join(self.storage_path, f"{manifest_id}.yaml")
            with open(manifest_file, "w") as f:
                f.write(manifest_yaml)
            
            return {
                "status": "success",
                "message": "Service account manifest generated successfully",
                "manifest_id": manifest_id,
                "manifest_file": manifest_file,
                "manifest": manifest,
                "manifest_yaml": manifest_yaml
            }
        except Exception as e:
            logger.error(f"Error generating service account manifest: {e}")
            return {"status": "error", "message": str(e)}
    
    def generate_role(self, name: str, rules: List[Dict], options: Dict = None) -> Dict:
        """
        Generate a Kubernetes role manifest.
        
        Args:
            name: Role name
            rules: Role rules
            options: Additional options
            
        Returns:
            Dict: Generation results
        """
        try:
            # Initialize options
            if not options:
                options = {}
            
            # Get namespace from options or default
            namespace = options.get("namespace", self.namespace)
            
            # Get labels from options or default
            labels = self.default_labels.copy()
            if "labels" in options:
                labels.update(options["labels"])
            
            # Get annotations from options or default
            annotations = self.default_annotations.copy()
            if "annotations" in options:
                annotations.update(options["annotations"])
            
            # Build role manifest
            manifest = {
                "apiVersion": "rbac.authorization.k8s.io/v1",
                "kind": "Role",
                "metadata": {
                    "name": name,
                    "namespace": namespace,
                    "labels": labels,
                    "annotations": annotations
                },
                "rules": rules
            }
            
            # Convert to YAML
            manifest_yaml = yaml.dump(manifest)
            
            # Save manifest to file
            manifest_id = options.get("manifest_id", uuid.uuid4().hex)
            manifest_file = os.path.join(self.storage_path, f"{manifest_id}.yaml")
            with open(manifest_file, "w") as f:
                f.write(manifest_yaml)
            
            return {
                "status": "success",
                "message": "Role manifest generated successfully",
                "manifest_id": manifest_id,
                "manifest_file": manifest_file,
                "manifest": manifest,
                "manifest_yaml": manifest_yaml
            }
        except Exception as e:
            logger.error(f"Error generating role manifest: {e}")
            return {"status": "error", "message": str(e)}
    
    def generate_role_binding(self, name: str, role_name: str, subjects: List[Dict], options: Dict = None) -> Dict:
        """
        Generate a Kubernetes role binding manifest.
        
        Args:
            name: Role binding name
            role_name: Role name
            subjects: Role binding subjects
            options: Additional options
            
        Returns:
            Dict: Generation results
        """
        try:
            # Initialize options
            if not options:
                options = {}
            
            # Get namespace from options or default
            namespace = options.get("namespace", self.namespace)
            
            # Get labels from options or default
            labels = self.default_labels.copy()
            if "labels" in options:
                labels.update(options["labels"])
            
            # Get annotations from options or default
            annotations = self.default_annotations.copy()
            if "annotations" in options:
                annotations.update(options["annotations"])
            
            # Get role kind
            role_kind = options.get("roleKind", "Role")
            
            # Build role binding manifest
            manifest = {
                "apiVersion": "rbac.authorization.k8s.io/v1",
                "kind": "RoleBinding",
                "metadata": {
                    "name": name,
                    "namespace": namespace,
                    "labels": labels,
                    "annotations": annotations
                },
                "roleRef": {
                    "apiGroup": "rbac.authorization.k8s.io",
                    "kind": role_kind,
                    "name": role_name
                },
                "subjects": subjects
            }
            
            # Convert to YAML
            manifest_yaml = yaml.dump(manifest)
            
            # Save manifest to file
            manifest_id = options.get("manifest_id", uuid.uuid4().hex)
            manifest_file = os.path.join(self.storage_path, f"{manifest_id}.yaml")
            with open(manifest_file, "w") as f:
                f.write(manifest_yaml)
            
            return {
                "status": "success",
                "message": "Role binding manifest generated successfully",
                "manifest_id": manifest_id,
                "manifest_file": manifest_file,
                "manifest": manifest,
                "manifest_yaml": manifest_yaml
            }
        except Exception as e:
            logger.error(f"Error generating role binding manifest: {e}")
            return {"status": "error", "message": str(e)}
    
    def generate_cluster_role(self, name: str, rules: List[Dict], options: Dict = None) -> Dict:
        """
        Generate a Kubernetes cluster role manifest.
        
        Args:
            name: Cluster role name
            rules: Cluster role rules
            options: Additional options
            
        Returns:
            Dict: Generation results
        """
        try:
            # Initialize options
            if not options:
                options = {}
            
            # Get labels from options or default
            labels = self.default_labels.copy()
            if "labels" in options:
                labels.update(options["labels"])
            
            # Get annotations from options or default
            annotations = self.default_annotations.copy()
            if "annotations" in options:
                annotations.update(options["annotations"])
            
            # Build cluster role manifest
            manifest = {
                "apiVersion": "rbac.authorization.k8s.io/v1",
                "kind": "ClusterRole",
                "metadata": {
                    "name": name,
                    "labels": labels,
                    "annotations": annotations
                },
                "rules": rules
            }
            
            # Convert to YAML
            manifest_yaml = yaml.dump(manifest)
            
            # Save manifest to file
            manifest_id = options.get("manifest_id", uuid.uuid4().hex)
            manifest_file = os.path.join(self.storage_path, f"{manifest_id}.yaml")
            with open(manifest_file, "w") as f:
                f.write(manifest_yaml)
            
            return {
                "status": "success",
                "message": "Cluster role manifest generated successfully",
                "manifest_id": manifest_id,
                "manifest_file": manifest_file,
                "manifest": manifest,
                "manifest_yaml": manifest_yaml
            }
        except Exception as e:
            logger.error(f"Error generating cluster role manifest: {e}")
            return {"status": "error", "message": str(e)}
    
    def generate_cluster_role_binding(self, name: str, role_name: str, subjects: List[Dict], options: Dict = None) -> Dict:
        """
        Generate a Kubernetes cluster role binding manifest.
        
        Args:
            name: Cluster role binding name
            role_name: Cluster role name
            subjects: Cluster role binding subjects
            options: Additional options
            
        Returns:
            Dict: Generation results
        """
        try:
            # Initialize options
            if not options:
                options = {}
            
            # Get labels from options or default
            labels = self.default_labels.copy()
            if "labels" in options:
                labels.update(options["labels"])
            
            # Get annotations from options or default
            annotations = self.default_annotations.copy()
            if "annotations" in options:
                annotations.update(options["annotations"])
            
            # Build cluster role binding manifest
            manifest = {
                "apiVersion": "rbac.authorization.k8s.io/v1",
                "kind": "ClusterRoleBinding",
                "metadata": {
                    "name": name,
                    "labels": labels,
                    "annotations": annotations
                },
                "roleRef": {
                    "apiGroup": "rbac.authorization.k8s.io",
                    "kind": "ClusterRole",
                    "name": role_name
                },
                "subjects": subjects
            }
            
            # Convert to YAML
            manifest_yaml = yaml.dump(manifest)
            
            # Save manifest to file
            manifest_id = options.get("manifest_id", uuid.uuid4().hex)
            manifest_file = os.path.join(self.storage_path, f"{manifest_id}.yaml")
            with open(manifest_file, "w") as f:
                f.write(manifest_yaml)
            
            return {
                "status": "success",
                "message": "Cluster role binding manifest generated successfully",
                "manifest_id": manifest_id,
                "manifest_file": manifest_file,
                "manifest": manifest,
                "manifest_yaml": manifest_yaml
            }
        except Exception as e:
            logger.error(f"Error generating cluster role binding manifest: {e}")
            return {"status": "error", "message": str(e)}
    
    def generate_persistent_volume_claim(self, name: str, storage_class: str, access_modes: List[str], storage: str, options: Dict = None) -> Dict:
        """
        Generate a Kubernetes persistent volume claim manifest.
        
        Args:
            name: Persistent volume claim name
            storage_class: Storage class name
            access_modes: Access modes
            storage: Storage size
            options: Additional options
            
        Returns:
            Dict: Generation results
        """
        try:
            # Initialize options
            if not options:
                options = {}
            
            # Get namespace from options or default
            namespace = options.get("namespace", self.namespace)
            
            # Get labels from options or default
            labels = self.default_labels.copy()
            if "labels" in options:
                labels.update(options["labels"])
            
            # Get annotations from options or default
            annotations = self.default_annotations.copy()
            if "annotations" in options:
                annotations.update(options["annotations"])
            
            # Build persistent volume claim manifest
            manifest = {
                "apiVersion": "v1",
                "kind": "PersistentVolumeClaim",
                "metadata": {
                    "name": name,
                    "namespace": namespace,
                    "labels": labels,
                    "annotations": annotations
                },
                "spec": {
                    "accessModes": access_modes,
                    "storageClassName": storage_class,
                    "resources": {
                        "requests": {
                            "storage": storage
                        }
                    }
                }
            }
            
            # Add volume name if provided
            if "volumeName" in options:
                manifest["spec"]["volumeName"] = options["volumeName"]
            
            # Add selector if provided
            if "selector" in options:
                manifest["spec"]["selector"] = options["selector"]
            
            # Add volume mode if provided
            if "volumeMode" in options:
                manifest["spec"]["volumeMode"] = options["volumeMode"]
            
            # Add data source if provided
            if "dataSource" in options:
                manifest["spec"]["dataSource"] = options["dataSource"]
            
            # Convert to YAML
            manifest_yaml = yaml.dump(manifest)
            
            # Save manifest to file
            manifest_id = options.get("manifest_id", uuid.uuid4().hex)
            manifest_file = os.path.join(self.storage_path, f"{manifest_id}.yaml")
            with open(manifest_file, "w") as f:
                f.write(manifest_yaml)
            
            return {
                "status": "success",
                "message": "Persistent volume claim manifest generated successfully",
                "manifest_id": manifest_id,
                "manifest_file": manifest_file,
                "manifest": manifest,
                "manifest_yaml": manifest_yaml
            }
        except Exception as e:
            logger.error(f"Error generating persistent volume claim manifest: {e}")
            return {"status": "error", "message": str(e)}
    
    def configure(self, config: Dict) -> Dict:
        """
        Configure the Kubernetes Manifest Generator.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Dict: Configuration results
        """
        try:
            # Update local configuration
            if "namespace" in config:
                self.namespace = config["namespace"]
            
            if "default_labels" in config:
                self.default_labels = config["default_labels"]
            
            if "default_annotations" in config:
                self.default_annotations = config["default_annotations"]
            
            if "storage_type" in config:
                self.storage_type = config["storage_type"]
            
            if "storage_path" in config:
                self.storage_path = config["storage_path"]
                
                # Create storage directory if it doesn't exist
                if self.storage_type == "file":
                    os.makedirs(self.storage_path, exist_ok=True)
            
            # Configure security integration
            security_result = None
            if "security" in config:
                security_result = self.security.configure(config["security"])
            
            return {
                "status": "success",
                "message": "Kubernetes Manifest Generator configured successfully",
                "generator_id": self.generator_id,
                "security_result": security_result
            }
        except Exception as e:
            logger.error(f"Error configuring Kubernetes Manifest Generator: {e}")
            return {"status": "error", "message": str(e)}
