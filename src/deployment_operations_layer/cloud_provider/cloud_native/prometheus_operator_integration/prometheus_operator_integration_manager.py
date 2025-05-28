"""
Prometheus Operator Integration Manager

This module provides integration with Prometheus Operator for the Deployment Operations Layer.
It handles deployment, configuration, and management of Prometheus Operator resources
including ServiceMonitors, PodMonitors, PrometheusRules, and Alertmanagers.

Classes:
    PrometheusOperatorIntegrationManager: Manages Prometheus Operator integration
    ServiceMonitorManager: Manages ServiceMonitor resources
    PodMonitorManager: Manages PodMonitor resources
    PrometheusRuleManager: Manages PrometheusRule resources
    AlertmanagerManager: Manages Alertmanager resources
    PrometheusOperatorExecutor: Executes Prometheus Operator API calls
"""

import json
import logging
import os
import subprocess
import tempfile
import yaml
import requests
from typing import Dict, List, Any, Optional, Tuple, Union

from ....agent.agent_utils import AgentResponse
from ....protocol.mcp_integration.mcp_context_schema import MCPContext

logger = logging.getLogger(__name__)

class PrometheusOperatorIntegrationManager:
    """
    Manages Prometheus Operator integration for the Deployment Operations Layer.
    
    This class provides a unified interface for interacting with Prometheus Operator,
    handling ServiceMonitors, PodMonitors, PrometheusRules, and Alertmanagers.
    """
    
    def __init__(self, kubectl_binary_path: Optional[str] = None,
                working_dir: Optional[str] = None,
                namespace: str = "monitoring"):
        """
        Initialize the Prometheus Operator Integration Manager.
        
        Args:
            kubectl_binary_path: Path to kubectl binary (optional, defaults to 'kubectl' in PATH)
            working_dir: Working directory for Prometheus Operator operations (optional)
            namespace: Kubernetes namespace for Prometheus Operator (default: monitoring)
        """
        self.kubectl_binary = kubectl_binary_path or "kubectl"
        self.working_dir = working_dir or tempfile.mkdtemp(prefix="prometheus_operator_")
        self.namespace = namespace
        
        self.executor = PrometheusOperatorExecutor(
            self.kubectl_binary, 
            self.working_dir,
            self.namespace
        )
        self.service_monitor_manager = ServiceMonitorManager(self.executor)
        self.pod_monitor_manager = PodMonitorManager(self.executor)
        self.prometheus_rule_manager = PrometheusRuleManager(self.executor)
        self.alertmanager_manager = AlertmanagerManager(self.executor)
    
    def deploy_prometheus_operator(self, namespace: Optional[str] = None) -> AgentResponse:
        """
        Deploy Prometheus Operator to Kubernetes.
        
        Args:
            namespace: Kubernetes namespace (optional, defaults to self.namespace)
            
        Returns:
            AgentResponse: Deployment response
        """
        try:
            namespace = namespace or self.namespace
            
            # Create namespace if it doesn't exist
            try:
                self.executor.run_kubectl_command(["get", "namespace", namespace])
            except Exception:
                self.executor.run_kubectl_command(["create", "namespace", namespace])
            
            # Deploy Prometheus Operator CRDs
            self._deploy_prometheus_operator_crds()
            
            # Deploy Prometheus Operator
            self._deploy_prometheus_operator_deployment(namespace)
            
            # Deploy Prometheus instance
            self._deploy_prometheus_instance(namespace)
            
            # Deploy Alertmanager instance
            self._deploy_alertmanager_instance(namespace)
            
            # Get Prometheus service
            prometheus_service = self.executor.run_kubectl_command([
                "get", "service", "prometheus-operated", "-n", namespace, "-o", "jsonpath={.spec.clusterIP}"
            ])
            
            return AgentResponse(
                success=True,
                message=f"Prometheus Operator deployed successfully to namespace {namespace}",
                data={
                    "namespace": namespace,
                    "prometheus_service": prometheus_service.strip(),
                    "prometheus_port": 9090,
                    "alertmanager_port": 9093
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to deploy Prometheus Operator: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to deploy Prometheus Operator: {str(e)}",
                data={}
            )
    
    def _deploy_prometheus_operator_crds(self) -> None:
        """
        Deploy Prometheus Operator CRDs.
        """
        # Define CRD URLs
        crd_urls = [
            "https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/main/example/prometheus-operator-crd/monitoring.coreos.com_alertmanagerconfigs.yaml",
            "https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/main/example/prometheus-operator-crd/monitoring.coreos.com_alertmanagers.yaml",
            "https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/main/example/prometheus-operator-crd/monitoring.coreos.com_podmonitors.yaml",
            "https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/main/example/prometheus-operator-crd/monitoring.coreos.com_probes.yaml",
            "https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/main/example/prometheus-operator-crd/monitoring.coreos.com_prometheuses.yaml",
            "https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/main/example/prometheus-operator-crd/monitoring.coreos.com_prometheusrules.yaml",
            "https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/main/example/prometheus-operator-crd/monitoring.coreos.com_servicemonitors.yaml",
            "https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/main/example/prometheus-operator-crd/monitoring.coreos.com_thanosrulers.yaml"
        ]
        
        # Download and apply CRDs
        for crd_url in crd_urls:
            crd_name = crd_url.split("/")[-1]
            crd_path = os.path.join(self.working_dir, crd_name)
            
            # Download CRD
            response = requests.get(crd_url)
            with open(crd_path, "w") as f:
                f.write(response.text)
            
            # Apply CRD
            self.executor.run_kubectl_command(["apply", "-f", crd_path])
    
    def _deploy_prometheus_operator_deployment(self, namespace: str) -> None:
        """
        Deploy Prometheus Operator deployment.
        
        Args:
            namespace: Kubernetes namespace
        """
        # Create Prometheus Operator deployment
        operator_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "prometheus-operator",
                "namespace": namespace
            },
            "spec": {
                "replicas": 1,
                "selector": {
                    "matchLabels": {
                        "app": "prometheus-operator"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "prometheus-operator"
                        }
                    },
                    "spec": {
                        "serviceAccountName": "prometheus-operator",
                        "containers": [
                            {
                                "name": "prometheus-operator",
                                "image": "quay.io/prometheus-operator/prometheus-operator:v0.59.1",
                                "args": [
                                    "--kubelet-service=kube-system/kubelet",
                                    "--logtostderr=true",
                                    "--config-reloader-image=quay.io/prometheus-operator/prometheus-config-reloader:v0.59.1",
                                    "--prometheus-config-reloader=quay.io/prometheus-operator/prometheus-config-reloader:v0.59.1"
                                ],
                                "ports": [
                                    {
                                        "containerPort": 8080,
                                        "name": "http"
                                    }
                                ],
                                "resources": {
                                    "limits": {
                                        "cpu": "200m",
                                        "memory": "200Mi"
                                    },
                                    "requests": {
                                        "cpu": "100m",
                                        "memory": "100Mi"
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }
        
        # Create Prometheus Operator service account
        operator_sa = {
            "apiVersion": "v1",
            "kind": "ServiceAccount",
            "metadata": {
                "name": "prometheus-operator",
                "namespace": namespace
            }
        }
        
        # Create Prometheus Operator cluster role
        operator_cr = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "ClusterRole",
            "metadata": {
                "name": "prometheus-operator"
            },
            "rules": [
                {
                    "apiGroups": ["monitoring.coreos.com"],
                    "resources": [
                        "alertmanagers",
                        "alertmanagerconfigs",
                        "podmonitors",
                        "probes",
                        "prometheuses",
                        "prometheusrules",
                        "servicemonitors",
                        "thanosrulers"
                    ],
                    "verbs": ["*"]
                },
                {
                    "apiGroups": ["apps"],
                    "resources": ["statefulsets"],
                    "verbs": ["*"]
                },
                {
                    "apiGroups": [""],
                    "resources": ["configmaps", "secrets"],
                    "verbs": ["*"]
                },
                {
                    "apiGroups": [""],
                    "resources": ["pods"],
                    "verbs": ["list", "delete"]
                },
                {
                    "apiGroups": [""],
                    "resources": ["services", "services/finalizers", "endpoints"],
                    "verbs": ["get", "create", "update", "delete"]
                },
                {
                    "apiGroups": [""],
                    "resources": ["nodes"],
                    "verbs": ["list", "watch"]
                },
                {
                    "apiGroups": [""],
                    "resources": ["namespaces"],
                    "verbs": ["get", "list", "watch"]
                },
                {
                    "apiGroups": ["networking.k8s.io"],
                    "resources": ["ingresses"],
                    "verbs": ["get", "list", "watch"]
                }
            ]
        }
        
        # Create Prometheus Operator cluster role binding
        operator_crb = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "ClusterRoleBinding",
            "metadata": {
                "name": "prometheus-operator"
            },
            "roleRef": {
                "apiGroup": "rbac.authorization.k8s.io",
                "kind": "ClusterRole",
                "name": "prometheus-operator"
            },
            "subjects": [
                {
                    "kind": "ServiceAccount",
                    "name": "prometheus-operator",
                    "namespace": namespace
                }
            ]
        }
        
        # Write Prometheus Operator resources to files
        operator_deployment_path = os.path.join(self.working_dir, "prometheus-operator-deployment.yaml")
        with open(operator_deployment_path, "w") as f:
            yaml.dump(operator_deployment, f)
        
        operator_sa_path = os.path.join(self.working_dir, "prometheus-operator-sa.yaml")
        with open(operator_sa_path, "w") as f:
            yaml.dump(operator_sa, f)
        
        operator_cr_path = os.path.join(self.working_dir, "prometheus-operator-cr.yaml")
        with open(operator_cr_path, "w") as f:
            yaml.dump(operator_cr, f)
        
        operator_crb_path = os.path.join(self.working_dir, "prometheus-operator-crb.yaml")
        with open(operator_crb_path, "w") as f:
            yaml.dump(operator_crb, f)
        
        # Apply Prometheus Operator resources
        self.executor.run_kubectl_command(["apply", "-f", operator_sa_path])
        self.executor.run_kubectl_command(["apply", "-f", operator_cr_path])
        self.executor.run_kubectl_command(["apply", "-f", operator_crb_path])
        self.executor.run_kubectl_command(["apply", "-f", operator_deployment_path])
    
    def _deploy_prometheus_instance(self, namespace: str) -> None:
        """
        Deploy Prometheus instance.
        
        Args:
            namespace: Kubernetes namespace
        """
        # Create Prometheus service account
        prometheus_sa = {
            "apiVersion": "v1",
            "kind": "ServiceAccount",
            "metadata": {
                "name": "prometheus",
                "namespace": namespace
            }
        }
        
        # Create Prometheus cluster role
        prometheus_cr = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "ClusterRole",
            "metadata": {
                "name": "prometheus"
            },
            "rules": [
                {
                    "apiGroups": [""],
                    "resources": ["nodes", "nodes/metrics", "services", "endpoints", "pods"],
                    "verbs": ["get", "list", "watch"]
                },
                {
                    "apiGroups": [""],
                    "resources": ["configmaps"],
                    "verbs": ["get"]
                },
                {
                    "apiGroups": ["networking.k8s.io"],
                    "resources": ["ingresses"],
                    "verbs": ["get", "list", "watch"]
                },
                {
                    "nonResourceURLs": ["/metrics"],
                    "verbs": ["get"]
                }
            ]
        }
        
        # Create Prometheus cluster role binding
        prometheus_crb = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "ClusterRoleBinding",
            "metadata": {
                "name": "prometheus"
            },
            "roleRef": {
                "apiGroup": "rbac.authorization.k8s.io",
                "kind": "ClusterRole",
                "name": "prometheus"
            },
            "subjects": [
                {
                    "kind": "ServiceAccount",
                    "name": "prometheus",
                    "namespace": namespace
                }
            ]
        }
        
        # Create Prometheus instance
        prometheus_instance = {
            "apiVersion": "monitoring.coreos.com/v1",
            "kind": "Prometheus",
            "metadata": {
                "name": "prometheus",
                "namespace": namespace
            },
            "spec": {
                "serviceAccountName": "prometheus",
                "replicas": 1,
                "version": "v2.35.0",
                "serviceMonitorSelector": {},
                "podMonitorSelector": {},
                "ruleSelector": {
                    "matchLabels": {
                        "role": "alert-rules"
                    }
                },
                "resources": {
                    "requests": {
                        "memory": "400Mi"
                    }
                }
            }
        }
        
        # Create Prometheus service
        prometheus_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "prometheus",
                "namespace": namespace
            },
            "spec": {
                "selector": {
                    "prometheus": "prometheus"
                },
                "ports": [
                    {
                        "name": "web",
                        "port": 9090,
                        "targetPort": 9090
                    }
                ]
            }
        }
        
        # Write Prometheus resources to files
        prometheus_sa_path = os.path.join(self.working_dir, "prometheus-sa.yaml")
        with open(prometheus_sa_path, "w") as f:
            yaml.dump(prometheus_sa, f)
        
        prometheus_cr_path = os.path.join(self.working_dir, "prometheus-cr.yaml")
        with open(prometheus_cr_path, "w") as f:
            yaml.dump(prometheus_cr, f)
        
        prometheus_crb_path = os.path.join(self.working_dir, "prometheus-crb.yaml")
        with open(prometheus_crb_path, "w") as f:
            yaml.dump(prometheus_crb, f)
        
        prometheus_instance_path = os.path.join(self.working_dir, "prometheus-instance.yaml")
        with open(prometheus_instance_path, "w") as f:
            yaml.dump(prometheus_instance, f)
        
        prometheus_service_path = os.path.join(self.working_dir, "prometheus-service.yaml")
        with open(prometheus_service_path, "w") as f:
            yaml.dump(prometheus_service, f)
        
        # Apply Prometheus resources
        self.executor.run_kubectl_command(["apply", "-f", prometheus_sa_path])
        self.executor.run_kubectl_command(["apply", "-f", prometheus_cr_path])
        self.executor.run_kubectl_command(["apply", "-f", prometheus_crb_path])
        self.executor.run_kubectl_command(["apply", "-f", prometheus_instance_path])
        self.executor.run_kubectl_command(["apply", "-f", prometheus_service_path])
    
    def _deploy_alertmanager_instance(self, namespace: str) -> None:
        """
        Deploy Alertmanager instance.
        
        Args:
            namespace: Kubernetes namespace
        """
        # Create Alertmanager config
        alertmanager_config = {
            "global": {
                "resolve_timeout": "5m"
            },
            "route": {
                "group_by": ["job"],
                "group_wait": "30s",
                "group_interval": "5m",
                "repeat_interval": "12h",
                "receiver": "null"
            },
            "receivers": [
                {
                    "name": "null"
                }
            ]
        }
        
        # Create Alertmanager config secret
        alertmanager_config_secret = {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": "alertmanager-config",
                "namespace": namespace
            },
            "stringData": {
                "alertmanager.yaml": yaml.dump(alertmanager_config)
            }
        }
        
        # Create Alertmanager instance
        alertmanager_instance = {
            "apiVersion": "monitoring.coreos.com/v1",
            "kind": "Alertmanager",
            "metadata": {
                "name": "alertmanager",
                "namespace": namespace
            },
            "spec": {
                "replicas": 1,
                "configSecret": "alertmanager-config",
                "resources": {
                    "requests": {
                        "memory": "100Mi"
                    }
                }
            }
        }
        
        # Create Alertmanager service
        alertmanager_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "alertmanager",
                "namespace": namespace
            },
            "spec": {
                "selector": {
                    "alertmanager": "alertmanager"
                },
                "ports": [
                    {
                        "name": "web",
                        "port": 9093,
                        "targetPort": 9093
                    }
                ]
            }
        }
        
        # Write Alertmanager resources to files
        alertmanager_config_secret_path = os.path.join(self.working_dir, "alertmanager-config-secret.yaml")
        with open(alertmanager_config_secret_path, "w") as f:
            yaml.dump(alertmanager_config_secret, f)
        
        alertmanager_instance_path = os.path.join(self.working_dir, "alertmanager-instance.yaml")
        with open(alertmanager_instance_path, "w") as f:
            yaml.dump(alertmanager_instance, f)
        
        alertmanager_service_path = os.path.join(self.working_dir, "alertmanager-service.yaml")
        with open(alertmanager_service_path, "w") as f:
            yaml.dump(alertmanager_service, f)
        
        # Apply Alertmanager resources
        self.executor.run_kubectl_command(["apply", "-f", alertmanager_config_secret_path])
        self.executor.run_kubectl_command(["apply", "-f", alertmanager_instance_path])
        self.executor.run_kubectl_command(["apply", "-f", alertmanager_service_path])
    
    def create_service_monitor(self, name: str, 
                              namespace: str,
                              selector: Dict[str, str],
                              port: str,
                              path: str = "/metrics",
                              interval: str = "30s",
                              labels: Optional[Dict[str, str]] = None) -> AgentResponse:
        """
        Create a ServiceMonitor resource.
        
        Args:
            name: ServiceMonitor name
            namespace: ServiceMonitor namespace
            selector: Label selector for services
            port: Service port name
            path: Metrics path (default: /metrics)
            interval: Scrape interval (default: 30s)
            labels: Additional labels (optional)
            
        Returns:
            AgentResponse: Creation response
        """
        try:
            result = self.service_monitor_manager.create_service_monitor(
                name=name,
                namespace=namespace,
                selector=selector,
                port=port,
                path=path,
                interval=interval,
                labels=labels
            )
            
            return AgentResponse(
                success=True,
                message=f"ServiceMonitor {name} created successfully in namespace {namespace}",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create ServiceMonitor: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create ServiceMonitor: {str(e)}",
                data={}
            )
    
    def create_pod_monitor(self, name: str, 
                          namespace: str,
                          selector: Dict[str, str],
                          port: str,
                          path: str = "/metrics",
                          interval: str = "30s",
                          labels: Optional[Dict[str, str]] = None) -> AgentResponse:
        """
        Create a PodMonitor resource.
        
        Args:
            name: PodMonitor name
            namespace: PodMonitor namespace
            selector: Label selector for pods
            port: Pod port name
            path: Metrics path (default: /metrics)
            interval: Scrape interval (default: 30s)
            labels: Additional labels (optional)
            
        Returns:
            AgentResponse: Creation response
        """
        try:
            result = self.pod_monitor_manager.create_pod_monitor(
                name=name,
                namespace=namespace,
                selector=selector,
                port=port,
                path=path,
                interval=interval,
                labels=labels
            )
            
            return AgentResponse(
                success=True,
                message=f"PodMonitor {name} created successfully in namespace {namespace}",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create PodMonitor: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create PodMonitor: {str(e)}",
                data={}
            )
    
    def create_prometheus_rule(self, name: str, 
                              namespace: str,
                              groups: List[Dict[str, Any]],
                              labels: Optional[Dict[str, str]] = None) -> AgentResponse:
        """
        Create a PrometheusRule resource.
        
        Args:
            name: PrometheusRule name
            namespace: PrometheusRule namespace
            groups: Rule groups
            labels: Additional labels (optional)
            
        Returns:
            AgentResponse: Creation response
        """
        try:
            result = self.prometheus_rule_manager.create_prometheus_rule(
                name=name,
                namespace=namespace,
                groups=groups,
                labels=labels
            )
            
            return AgentResponse(
                success=True,
                message=f"PrometheusRule {name} created successfully in namespace {namespace}",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create PrometheusRule: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create PrometheusRule: {str(e)}",
                data={}
            )
    
    def update_alertmanager_config(self, config: Dict[str, Any]) -> AgentResponse:
        """
        Update Alertmanager configuration.
        
        Args:
            config: Alertmanager configuration
            
        Returns:
            AgentResponse: Update response
        """
        try:
            result = self.alertmanager_manager.update_alertmanager_config(config)
            
            return AgentResponse(
                success=True,
                message=f"Alertmanager configuration updated successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to update Alertmanager configuration: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to update Alertmanager configuration: {str(e)}",
                data={}
            )
    
    def to_mcp_context(self) -> MCPContext:
        """
        Convert Prometheus Operator integration information to MCP context.
        
        Returns:
            MCPContext: MCP context with Prometheus Operator integration information
        """
        return MCPContext(
            context_type="prometheus_operator_integration",
            namespace=self.namespace,
            working_dir=self.working_dir
        )


class ServiceMonitorManager:
    """
    Manages ServiceMonitor resources.
    
    This class provides methods for creating, updating, and deleting ServiceMonitor resources.
    """
    
    def __init__(self, executor: 'PrometheusOperatorExecutor'):
        """
        Initialize the ServiceMonitor Manager.
        
        Args:
            executor: Prometheus Operator executor
        """
        self.executor = executor
    
    def create_service_monitor(self, name: str, 
                              namespace: str,
                              selector: Dict[str, str],
                              port: str,
                              path: str = "/metrics",
                              interval: str = "30s",
                              labels: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Create a ServiceMonitor resource.
        
        Args:
            name: ServiceMonitor name
            namespace: ServiceMonitor namespace
            selector: Label selector for services
            port: Service port name
            path: Metrics path (default: /metrics)
            interval: Scrape interval (default: 30s)
            labels: Additional labels (optional)
            
        Returns:
            Dict[str, Any]: Created ServiceMonitor
        """
        # Create ServiceMonitor
        service_monitor = {
            "apiVersion": "monitoring.coreos.com/v1",
            "kind": "ServiceMonitor",
            "metadata": {
                "name": name,
                "namespace": namespace,
                "labels": labels or {}
            },
            "spec": {
                "selector": {
                    "matchLabels": selector
                },
                "endpoints": [
                    {
                        "port": port,
                        "path": path,
                        "interval": interval
                    }
                ]
            }
        }
        
        # Write ServiceMonitor to file
        service_monitor_path = os.path.join(self.executor.working_dir, f"service-monitor-{name}.yaml")
        with open(service_monitor_path, "w") as f:
            yaml.dump(service_monitor, f)
        
        # Apply ServiceMonitor
        self.executor.run_kubectl_command(["apply", "-f", service_monitor_path])
        
        # Get created ServiceMonitor
        result = self.executor.run_kubectl_command([
            "get", "servicemonitor", name, "-n", namespace, "-o", "json"
        ])
        
        return json.loads(result)
    
    def update_service_monitor(self, name: str, 
                              namespace: str,
                              selector: Dict[str, str],
                              port: str,
                              path: str = "/metrics",
                              interval: str = "30s",
                              labels: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Update a ServiceMonitor resource.
        
        Args:
            name: ServiceMonitor name
            namespace: ServiceMonitor namespace
            selector: Label selector for services
            port: Service port name
            path: Metrics path (default: /metrics)
            interval: Scrape interval (default: 30s)
            labels: Additional labels (optional)
            
        Returns:
            Dict[str, Any]: Updated ServiceMonitor
        """
        # Get existing ServiceMonitor
        try:
            existing_service_monitor = self.executor.run_kubectl_command([
                "get", "servicemonitor", name, "-n", namespace, "-o", "json"
            ])
            existing_service_monitor = json.loads(existing_service_monitor)
        except Exception:
            # ServiceMonitor doesn't exist, create it
            return self.create_service_monitor(
                name=name,
                namespace=namespace,
                selector=selector,
                port=port,
                path=path,
                interval=interval,
                labels=labels
            )
        
        # Update ServiceMonitor
        service_monitor = {
            "apiVersion": "monitoring.coreos.com/v1",
            "kind": "ServiceMonitor",
            "metadata": {
                "name": name,
                "namespace": namespace,
                "labels": labels or {}
            },
            "spec": {
                "selector": {
                    "matchLabels": selector
                },
                "endpoints": [
                    {
                        "port": port,
                        "path": path,
                        "interval": interval
                    }
                ]
            }
        }
        
        # Write ServiceMonitor to file
        service_monitor_path = os.path.join(self.executor.working_dir, f"service-monitor-{name}.yaml")
        with open(service_monitor_path, "w") as f:
            yaml.dump(service_monitor, f)
        
        # Apply ServiceMonitor
        self.executor.run_kubectl_command(["apply", "-f", service_monitor_path])
        
        # Get updated ServiceMonitor
        result = self.executor.run_kubectl_command([
            "get", "servicemonitor", name, "-n", namespace, "-o", "json"
        ])
        
        return json.loads(result)
    
    def delete_service_monitor(self, name: str, namespace: str) -> None:
        """
        Delete a ServiceMonitor resource.
        
        Args:
            name: ServiceMonitor name
            namespace: ServiceMonitor namespace
        """
        self.executor.run_kubectl_command([
            "delete", "servicemonitor", name, "-n", namespace
        ])


class PodMonitorManager:
    """
    Manages PodMonitor resources.
    
    This class provides methods for creating, updating, and deleting PodMonitor resources.
    """
    
    def __init__(self, executor: 'PrometheusOperatorExecutor'):
        """
        Initialize the PodMonitor Manager.
        
        Args:
            executor: Prometheus Operator executor
        """
        self.executor = executor
    
    def create_pod_monitor(self, name: str, 
                          namespace: str,
                          selector: Dict[str, str],
                          port: str,
                          path: str = "/metrics",
                          interval: str = "30s",
                          labels: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Create a PodMonitor resource.
        
        Args:
            name: PodMonitor name
            namespace: PodMonitor namespace
            selector: Label selector for pods
            port: Pod port name
            path: Metrics path (default: /metrics)
            interval: Scrape interval (default: 30s)
            labels: Additional labels (optional)
            
        Returns:
            Dict[str, Any]: Created PodMonitor
        """
        # Create PodMonitor
        pod_monitor = {
            "apiVersion": "monitoring.coreos.com/v1",
            "kind": "PodMonitor",
            "metadata": {
                "name": name,
                "namespace": namespace,
                "labels": labels or {}
            },
            "spec": {
                "selector": {
                    "matchLabels": selector
                },
                "podMetricsEndpoints": [
                    {
                        "port": port,
                        "path": path,
                        "interval": interval
                    }
                ]
            }
        }
        
        # Write PodMonitor to file
        pod_monitor_path = os.path.join(self.executor.working_dir, f"pod-monitor-{name}.yaml")
        with open(pod_monitor_path, "w") as f:
            yaml.dump(pod_monitor, f)
        
        # Apply PodMonitor
        self.executor.run_kubectl_command(["apply", "-f", pod_monitor_path])
        
        # Get created PodMonitor
        result = self.executor.run_kubectl_command([
            "get", "podmonitor", name, "-n", namespace, "-o", "json"
        ])
        
        return json.loads(result)
    
    def update_pod_monitor(self, name: str, 
                          namespace: str,
                          selector: Dict[str, str],
                          port: str,
                          path: str = "/metrics",
                          interval: str = "30s",
                          labels: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Update a PodMonitor resource.
        
        Args:
            name: PodMonitor name
            namespace: PodMonitor namespace
            selector: Label selector for pods
            port: Pod port name
            path: Metrics path (default: /metrics)
            interval: Scrape interval (default: 30s)
            labels: Additional labels (optional)
            
        Returns:
            Dict[str, Any]: Updated PodMonitor
        """
        # Get existing PodMonitor
        try:
            existing_pod_monitor = self.executor.run_kubectl_command([
                "get", "podmonitor", name, "-n", namespace, "-o", "json"
            ])
            existing_pod_monitor = json.loads(existing_pod_monitor)
        except Exception:
            # PodMonitor doesn't exist, create it
            return self.create_pod_monitor(
                name=name,
                namespace=namespace,
                selector=selector,
                port=port,
                path=path,
                interval=interval,
                labels=labels
            )
        
        # Update PodMonitor
        pod_monitor = {
            "apiVersion": "monitoring.coreos.com/v1",
            "kind": "PodMonitor",
            "metadata": {
                "name": name,
                "namespace": namespace,
                "labels": labels or {}
            },
            "spec": {
                "selector": {
                    "matchLabels": selector
                },
                "podMetricsEndpoints": [
                    {
                        "port": port,
                        "path": path,
                        "interval": interval
                    }
                ]
            }
        }
        
        # Write PodMonitor to file
        pod_monitor_path = os.path.join(self.executor.working_dir, f"pod-monitor-{name}.yaml")
        with open(pod_monitor_path, "w") as f:
            yaml.dump(pod_monitor, f)
        
        # Apply PodMonitor
        self.executor.run_kubectl_command(["apply", "-f", pod_monitor_path])
        
        # Get updated PodMonitor
        result = self.executor.run_kubectl_command([
            "get", "podmonitor", name, "-n", namespace, "-o", "json"
        ])
        
        return json.loads(result)
    
    def delete_pod_monitor(self, name: str, namespace: str) -> None:
        """
        Delete a PodMonitor resource.
        
        Args:
            name: PodMonitor name
            namespace: PodMonitor namespace
        """
        self.executor.run_kubectl_command([
            "delete", "podmonitor", name, "-n", namespace
        ])


class PrometheusRuleManager:
    """
    Manages PrometheusRule resources.
    
    This class provides methods for creating, updating, and deleting PrometheusRule resources.
    """
    
    def __init__(self, executor: 'PrometheusOperatorExecutor'):
        """
        Initialize the PrometheusRule Manager.
        
        Args:
            executor: Prometheus Operator executor
        """
        self.executor = executor
    
    def create_prometheus_rule(self, name: str, 
                              namespace: str,
                              groups: List[Dict[str, Any]],
                              labels: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Create a PrometheusRule resource.
        
        Args:
            name: PrometheusRule name
            namespace: PrometheusRule namespace
            groups: Rule groups
            labels: Additional labels (optional)
            
        Returns:
            Dict[str, Any]: Created PrometheusRule
        """
        # Create PrometheusRule
        prometheus_rule = {
            "apiVersion": "monitoring.coreos.com/v1",
            "kind": "PrometheusRule",
            "metadata": {
                "name": name,
                "namespace": namespace,
                "labels": labels or {"role": "alert-rules"}
            },
            "spec": {
                "groups": groups
            }
        }
        
        # Write PrometheusRule to file
        prometheus_rule_path = os.path.join(self.executor.working_dir, f"prometheus-rule-{name}.yaml")
        with open(prometheus_rule_path, "w") as f:
            yaml.dump(prometheus_rule, f)
        
        # Apply PrometheusRule
        self.executor.run_kubectl_command(["apply", "-f", prometheus_rule_path])
        
        # Get created PrometheusRule
        result = self.executor.run_kubectl_command([
            "get", "prometheusrule", name, "-n", namespace, "-o", "json"
        ])
        
        return json.loads(result)
    
    def update_prometheus_rule(self, name: str, 
                              namespace: str,
                              groups: List[Dict[str, Any]],
                              labels: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Update a PrometheusRule resource.
        
        Args:
            name: PrometheusRule name
            namespace: PrometheusRule namespace
            groups: Rule groups
            labels: Additional labels (optional)
            
        Returns:
            Dict[str, Any]: Updated PrometheusRule
        """
        # Get existing PrometheusRule
        try:
            existing_prometheus_rule = self.executor.run_kubectl_command([
                "get", "prometheusrule", name, "-n", namespace, "-o", "json"
            ])
            existing_prometheus_rule = json.loads(existing_prometheus_rule)
        except Exception:
            # PrometheusRule doesn't exist, create it
            return self.create_prometheus_rule(
                name=name,
                namespace=namespace,
                groups=groups,
                labels=labels
            )
        
        # Update PrometheusRule
        prometheus_rule = {
            "apiVersion": "monitoring.coreos.com/v1",
            "kind": "PrometheusRule",
            "metadata": {
                "name": name,
                "namespace": namespace,
                "labels": labels or {"role": "alert-rules"}
            },
            "spec": {
                "groups": groups
            }
        }
        
        # Write PrometheusRule to file
        prometheus_rule_path = os.path.join(self.executor.working_dir, f"prometheus-rule-{name}.yaml")
        with open(prometheus_rule_path, "w") as f:
            yaml.dump(prometheus_rule, f)
        
        # Apply PrometheusRule
        self.executor.run_kubectl_command(["apply", "-f", prometheus_rule_path])
        
        # Get updated PrometheusRule
        result = self.executor.run_kubectl_command([
            "get", "prometheusrule", name, "-n", namespace, "-o", "json"
        ])
        
        return json.loads(result)
    
    def delete_prometheus_rule(self, name: str, namespace: str) -> None:
        """
        Delete a PrometheusRule resource.
        
        Args:
            name: PrometheusRule name
            namespace: PrometheusRule namespace
        """
        self.executor.run_kubectl_command([
            "delete", "prometheusrule", name, "-n", namespace
        ])


class AlertmanagerManager:
    """
    Manages Alertmanager resources.
    
    This class provides methods for managing Alertmanager resources,
    including updating Alertmanager configuration.
    """
    
    def __init__(self, executor: 'PrometheusOperatorExecutor'):
        """
        Initialize the Alertmanager Manager.
        
        Args:
            executor: Prometheus Operator executor
        """
        self.executor = executor
    
    def update_alertmanager_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update Alertmanager configuration.
        
        Args:
            config: Alertmanager configuration
            
        Returns:
            Dict[str, Any]: Updated Alertmanager configuration
        """
        # Create Alertmanager config secret
        alertmanager_config_secret = {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": "alertmanager-config",
                "namespace": self.executor.namespace
            },
            "stringData": {
                "alertmanager.yaml": yaml.dump(config)
            }
        }
        
        # Write Alertmanager config secret to file
        alertmanager_config_secret_path = os.path.join(self.executor.working_dir, "alertmanager-config-secret.yaml")
        with open(alertmanager_config_secret_path, "w") as f:
            yaml.dump(alertmanager_config_secret, f)
        
        # Apply Alertmanager config secret
        self.executor.run_kubectl_command(["apply", "-f", alertmanager_config_secret_path])
        
        # Get updated Alertmanager config secret
        result = self.executor.run_kubectl_command([
            "get", "secret", "alertmanager-config", "-n", self.executor.namespace, "-o", "json"
        ])
        
        return json.loads(result)


class PrometheusOperatorExecutor:
    """
    Executes Prometheus Operator API calls and kubectl commands.
    
    This class provides methods for executing Prometheus Operator API calls and kubectl commands
    and handling their output.
    """
    
    def __init__(self, kubectl_binary: str,
                working_dir: str,
                namespace: str):
        """
        Initialize the Prometheus Operator Executor.
        
        Args:
            kubectl_binary: Path to kubectl binary
            working_dir: Working directory for Prometheus Operator operations
            namespace: Kubernetes namespace
        """
        self.kubectl_binary = kubectl_binary
        self.working_dir = working_dir
        self.namespace = namespace
    
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
