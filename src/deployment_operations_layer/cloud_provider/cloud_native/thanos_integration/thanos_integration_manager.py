"""
Thanos Integration Manager

This module provides integration with Thanos for the Deployment Operations Layer.
It handles Thanos query, store, compactor, and sidecar components for high-availability
Prometheus metrics storage and querying.

Classes:
    ThanosIntegrationManager: Manages Thanos integration
    ThanosQueryManager: Manages Thanos query operations
    ThanosStoreManager: Manages Thanos store operations
    ThanosCompactorManager: Manages Thanos compactor operations
    ThanosSidecarManager: Manages Thanos sidecar operations
    ThanosExecutor: Executes Thanos API calls
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

class ThanosIntegrationManager:
    """
    Manages Thanos integration for the Deployment Operations Layer.
    
    This class provides a unified interface for interacting with Thanos,
    handling query, store, compactor, and sidecar components.
    """
    
    def __init__(self, thanos_query_url: Optional[str] = None,
                object_storage_config: Optional[Dict[str, Any]] = None,
                kubectl_binary_path: Optional[str] = None,
                working_dir: Optional[str] = None):
        """
        Initialize the Thanos Integration Manager.
        
        Args:
            thanos_query_url: Thanos Query URL (optional)
            object_storage_config: Object storage configuration (optional)
            kubectl_binary_path: Path to kubectl binary (optional, defaults to 'kubectl' in PATH)
            working_dir: Working directory for Thanos operations (optional)
        """
        self.thanos_query_url = thanos_query_url
        self.object_storage_config = object_storage_config
        self.kubectl_binary = kubectl_binary_path or "kubectl"
        self.working_dir = working_dir or tempfile.mkdtemp(prefix="thanos_")
        
        self.executor = ThanosExecutor(
            self.thanos_query_url, 
            self.kubectl_binary, 
            self.working_dir
        )
        self.query_manager = ThanosQueryManager(self.executor)
        self.store_manager = ThanosStoreManager(self.executor)
        self.compactor_manager = ThanosCompactorManager(self.executor)
        self.sidecar_manager = ThanosSidecarManager(self.executor)
        
        # Verify Thanos connectivity
        if self.thanos_query_url:
            self._verify_thanos_connectivity()
    
    def _verify_thanos_connectivity(self):
        """
        Verify that Thanos is accessible.
        
        Logs a warning if Thanos is not accessible but does not raise an exception
        as Thanos may be accessed via other means.
        """
        try:
            response = self.executor.make_thanos_api_request("GET", "/api/v1/status/flags")
            if response.status_code == 200:
                logger.info("Thanos server is accessible")
            else:
                logger.warning(f"Thanos server returned status code {response.status_code}")
        except Exception as e:
            logger.warning(f"Thanos server is not accessible: {str(e)}")
    
    def query_metrics(self, query: str, 
                     time: Optional[str] = None,
                     timeout: Optional[str] = None) -> AgentResponse:
        """
        Query metrics from Thanos.
        
        Args:
            query: PromQL query
            time: Query time (optional)
            timeout: Query timeout (optional)
            
        Returns:
            AgentResponse: Query response
        """
        try:
            if not self.thanos_query_url:
                raise Exception("Thanos Query URL not configured")
            
            result = self.query_manager.query_metrics(
                query=query,
                time=time,
                timeout=timeout
            )
            
            return AgentResponse(
                success=True,
                message=f"Query executed successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to query metrics: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to query metrics: {str(e)}",
                data={}
            )
    
    def query_range(self, query: str, 
                   start: str,
                   end: str,
                   step: str,
                   timeout: Optional[str] = None) -> AgentResponse:
        """
        Query metrics over a time range from Thanos.
        
        Args:
            query: PromQL query
            start: Start time
            end: End time
            step: Step interval
            timeout: Query timeout (optional)
            
        Returns:
            AgentResponse: Query response
        """
        try:
            if not self.thanos_query_url:
                raise Exception("Thanos Query URL not configured")
            
            result = self.query_manager.query_range(
                query=query,
                start=start,
                end=end,
                step=step,
                timeout=timeout
            )
            
            return AgentResponse(
                success=True,
                message=f"Range query executed successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to query metrics range: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to query metrics range: {str(e)}",
                data={}
            )
    
    def get_labels(self) -> AgentResponse:
        """
        Get all label names from Thanos.
        
        Returns:
            AgentResponse: Labels response
        """
        try:
            if not self.thanos_query_url:
                raise Exception("Thanos Query URL not configured")
            
            result = self.query_manager.get_labels()
            
            return AgentResponse(
                success=True,
                message=f"Retrieved {len(result.get('data', []))} labels from Thanos",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to get labels: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to get labels: {str(e)}",
                data={}
            )
    
    def get_label_values(self, label: str) -> AgentResponse:
        """
        Get values for a label from Thanos.
        
        Args:
            label: Label name
            
        Returns:
            AgentResponse: Label values response
        """
        try:
            if not self.thanos_query_url:
                raise Exception("Thanos Query URL not configured")
            
            result = self.query_manager.get_label_values(label)
            
            return AgentResponse(
                success=True,
                message=f"Retrieved {len(result.get('data', []))} values for label {label} from Thanos",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to get label values: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to get label values: {str(e)}",
                data={}
            )
    
    def get_series(self, match: List[str], 
                  start: Optional[str] = None,
                  end: Optional[str] = None) -> AgentResponse:
        """
        Get time series data from Thanos.
        
        Args:
            match: Series selectors
            start: Start time (optional)
            end: End time (optional)
            
        Returns:
            AgentResponse: Series response
        """
        try:
            if not self.thanos_query_url:
                raise Exception("Thanos Query URL not configured")
            
            result = self.query_manager.get_series(
                match=match,
                start=start,
                end=end
            )
            
            return AgentResponse(
                success=True,
                message=f"Retrieved series data from Thanos",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to get series: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to get series: {str(e)}",
                data={}
            )
    
    def get_stores(self) -> AgentResponse:
        """
        Get store information from Thanos.
        
        Returns:
            AgentResponse: Stores response
        """
        try:
            if not self.thanos_query_url:
                raise Exception("Thanos Query URL not configured")
            
            result = self.store_manager.get_stores()
            
            return AgentResponse(
                success=True,
                message=f"Retrieved store information from Thanos",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to get stores: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to get stores: {str(e)}",
                data={}
            )
    
    def deploy_thanos(self, namespace: str = "thanos",
                     prometheus_namespace: str = "monitoring",
                     storage_config: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Deploy Thanos to Kubernetes.
        
        Args:
            namespace: Kubernetes namespace (default: thanos)
            prometheus_namespace: Prometheus namespace (default: monitoring)
            storage_config: Object storage configuration (optional)
            
        Returns:
            AgentResponse: Deployment response
        """
        try:
            # Use provided storage config or default
            storage_config = storage_config or self.object_storage_config
            
            if not storage_config:
                raise Exception("Object storage configuration is required")
            
            # Create namespace if it doesn't exist
            try:
                self.executor.run_kubectl_command(["get", "namespace", namespace])
            except Exception:
                self.executor.run_kubectl_command(["create", "namespace", namespace])
            
            # Create object storage secret
            objstore_secret = {
                "apiVersion": "v1",
                "kind": "Secret",
                "metadata": {
                    "name": "thanos-objstore-config",
                    "namespace": namespace
                },
                "stringData": {
                    "objstore.yml": yaml.dump(storage_config)
                }
            }
            
            # Write object storage secret to file
            objstore_secret_path = os.path.join(self.working_dir, "thanos-objstore-secret.yaml")
            with open(objstore_secret_path, "w") as f:
                yaml.dump(objstore_secret, f)
            
            # Apply object storage secret
            self.executor.run_kubectl_command(["apply", "-f", objstore_secret_path])
            
            # Deploy Thanos components
            self._deploy_thanos_query(namespace)
            self._deploy_thanos_store(namespace)
            self._deploy_thanos_compactor(namespace)
            self._deploy_thanos_sidecar(namespace, prometheus_namespace)
            
            # Get Thanos query service
            query_service = self.executor.run_kubectl_command(["get", "service", "thanos-query", "-n", namespace, "-o", "jsonpath={.spec.clusterIP}"])
            
            return AgentResponse(
                success=True,
                message=f"Thanos deployed successfully to namespace {namespace}",
                data={
                    "namespace": namespace,
                    "query_service": query_service.strip(),
                    "query_port": 9090,
                    "store_port": 10901,
                    "sidecar_port": 10902
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to deploy Thanos: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to deploy Thanos: {str(e)}",
                data={}
            )
    
    def _deploy_thanos_query(self, namespace: str) -> None:
        """
        Deploy Thanos Query component.
        
        Args:
            namespace: Kubernetes namespace
        """
        # Create Thanos Query deployment
        query_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "thanos-query",
                "namespace": namespace
            },
            "spec": {
                "replicas": 1,
                "selector": {
                    "matchLabels": {
                        "app": "thanos-query"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "thanos-query"
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "thanos-query",
                                "image": "quay.io/thanos/thanos:v0.28.0",
                                "args": [
                                    "query",
                                    "--log.level=info",
                                    "--query.replica-label=replica",
                                    "--store=dnssrv+_grpc._tcp.thanos-store.$(NAMESPACE).svc.cluster.local",
                                    "--store=dnssrv+_grpc._tcp.thanos-sidecar.$(NAMESPACE).svc.cluster.local"
                                ],
                                "env": [
                                    {
                                        "name": "NAMESPACE",
                                        "valueFrom": {
                                            "fieldRef": {
                                                "fieldPath": "metadata.namespace"
                                            }
                                        }
                                    }
                                ],
                                "ports": [
                                    {
                                        "name": "http",
                                        "containerPort": 9090
                                    },
                                    {
                                        "name": "grpc",
                                        "containerPort": 10901
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
        }
        
        # Create Thanos Query service
        query_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "thanos-query",
                "namespace": namespace
            },
            "spec": {
                "selector": {
                    "app": "thanos-query"
                },
                "ports": [
                    {
                        "name": "http",
                        "port": 9090,
                        "targetPort": 9090
                    },
                    {
                        "name": "grpc",
                        "port": 10901,
                        "targetPort": 10901
                    }
                ]
            }
        }
        
        # Write Thanos Query deployment to file
        query_deployment_path = os.path.join(self.working_dir, "thanos-query-deployment.yaml")
        with open(query_deployment_path, "w") as f:
            yaml.dump(query_deployment, f)
        
        # Write Thanos Query service to file
        query_service_path = os.path.join(self.working_dir, "thanos-query-service.yaml")
        with open(query_service_path, "w") as f:
            yaml.dump(query_service, f)
        
        # Apply Thanos Query deployment and service
        self.executor.run_kubectl_command(["apply", "-f", query_deployment_path])
        self.executor.run_kubectl_command(["apply", "-f", query_service_path])
    
    def _deploy_thanos_store(self, namespace: str) -> None:
        """
        Deploy Thanos Store component.
        
        Args:
            namespace: Kubernetes namespace
        """
        # Create Thanos Store statefulset
        store_statefulset = {
            "apiVersion": "apps/v1",
            "kind": "StatefulSet",
            "metadata": {
                "name": "thanos-store",
                "namespace": namespace
            },
            "spec": {
                "replicas": 1,
                "selector": {
                    "matchLabels": {
                        "app": "thanos-store"
                    }
                },
                "serviceName": "thanos-store",
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "thanos-store"
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "thanos-store",
                                "image": "quay.io/thanos/thanos:v0.28.0",
                                "args": [
                                    "store",
                                    "--log.level=info",
                                    "--data-dir=/var/thanos/store",
                                    "--objstore.config-file=/etc/thanos/objstore.yml",
                                    "--index-cache-size=500MB",
                                    "--chunk-pool-size=500MB"
                                ],
                                "ports": [
                                    {
                                        "name": "http",
                                        "containerPort": 10902
                                    },
                                    {
                                        "name": "grpc",
                                        "containerPort": 10901
                                    }
                                ],
                                "volumeMounts": [
                                    {
                                        "name": "thanos-store-data",
                                        "mountPath": "/var/thanos/store"
                                    },
                                    {
                                        "name": "thanos-objstore-config",
                                        "mountPath": "/etc/thanos",
                                        "readOnly": true
                                    }
                                ]
                            }
                        ],
                        "volumes": [
                            {
                                "name": "thanos-objstore-config",
                                "secret": {
                                    "secretName": "thanos-objstore-config"
                                }
                            }
                        ]
                    }
                },
                "volumeClaimTemplates": [
                    {
                        "metadata": {
                            "name": "thanos-store-data"
                        },
                        "spec": {
                            "accessModes": ["ReadWriteOnce"],
                            "resources": {
                                "requests": {
                                    "storage": "10Gi"
                                }
                            }
                        }
                    }
                ]
            }
        }
        
        # Create Thanos Store service
        store_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "thanos-store",
                "namespace": namespace
            },
            "spec": {
                "selector": {
                    "app": "thanos-store"
                },
                "ports": [
                    {
                        "name": "http",
                        "port": 10902,
                        "targetPort": 10902
                    },
                    {
                        "name": "grpc",
                        "port": 10901,
                        "targetPort": 10901
                    }
                ],
                "clusterIP": "None"
            }
        }
        
        # Write Thanos Store statefulset to file
        store_statefulset_path = os.path.join(self.working_dir, "thanos-store-statefulset.yaml")
        with open(store_statefulset_path, "w") as f:
            yaml.dump(store_statefulset, f)
        
        # Write Thanos Store service to file
        store_service_path = os.path.join(self.working_dir, "thanos-store-service.yaml")
        with open(store_service_path, "w") as f:
            yaml.dump(store_service, f)
        
        # Apply Thanos Store statefulset and service
        self.executor.run_kubectl_command(["apply", "-f", store_statefulset_path])
        self.executor.run_kubectl_command(["apply", "-f", store_service_path])
    
    def _deploy_thanos_compactor(self, namespace: str) -> None:
        """
        Deploy Thanos Compactor component.
        
        Args:
            namespace: Kubernetes namespace
        """
        # Create Thanos Compactor statefulset
        compactor_statefulset = {
            "apiVersion": "apps/v1",
            "kind": "StatefulSet",
            "metadata": {
                "name": "thanos-compactor",
                "namespace": namespace
            },
            "spec": {
                "replicas": 1,
                "selector": {
                    "matchLabels": {
                        "app": "thanos-compactor"
                    }
                },
                "serviceName": "thanos-compactor",
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "thanos-compactor"
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "thanos-compactor",
                                "image": "quay.io/thanos/thanos:v0.28.0",
                                "args": [
                                    "compact",
                                    "--log.level=info",
                                    "--data-dir=/var/thanos/compactor",
                                    "--objstore.config-file=/etc/thanos/objstore.yml",
                                    "--wait",
                                    "--retention.resolution-raw=30d",
                                    "--retention.resolution-5m=90d",
                                    "--retention.resolution-1h=1y"
                                ],
                                "ports": [
                                    {
                                        "name": "http",
                                        "containerPort": 10902
                                    }
                                ],
                                "volumeMounts": [
                                    {
                                        "name": "thanos-compactor-data",
                                        "mountPath": "/var/thanos/compactor"
                                    },
                                    {
                                        "name": "thanos-objstore-config",
                                        "mountPath": "/etc/thanos",
                                        "readOnly": true
                                    }
                                ]
                            }
                        ],
                        "volumes": [
                            {
                                "name": "thanos-objstore-config",
                                "secret": {
                                    "secretName": "thanos-objstore-config"
                                }
                            }
                        ]
                    }
                },
                "volumeClaimTemplates": [
                    {
                        "metadata": {
                            "name": "thanos-compactor-data"
                        },
                        "spec": {
                            "accessModes": ["ReadWriteOnce"],
                            "resources": {
                                "requests": {
                                    "storage": "10Gi"
                                }
                            }
                        }
                    }
                ]
            }
        }
        
        # Create Thanos Compactor service
        compactor_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "thanos-compactor",
                "namespace": namespace
            },
            "spec": {
                "selector": {
                    "app": "thanos-compactor"
                },
                "ports": [
                    {
                        "name": "http",
                        "port": 10902,
                        "targetPort": 10902
                    }
                ]
            }
        }
        
        # Write Thanos Compactor statefulset to file
        compactor_statefulset_path = os.path.join(self.working_dir, "thanos-compactor-statefulset.yaml")
        with open(compactor_statefulset_path, "w") as f:
            yaml.dump(compactor_statefulset, f)
        
        # Write Thanos Compactor service to file
        compactor_service_path = os.path.join(self.working_dir, "thanos-compactor-service.yaml")
        with open(compactor_service_path, "w") as f:
            yaml.dump(compactor_service, f)
        
        # Apply Thanos Compactor statefulset and service
        self.executor.run_kubectl_command(["apply", "-f", compactor_statefulset_path])
        self.executor.run_kubectl_command(["apply", "-f", compactor_service_path])
    
    def _deploy_thanos_sidecar(self, namespace: str, prometheus_namespace: str) -> None:
        """
        Deploy Thanos Sidecar component.
        
        Args:
            namespace: Kubernetes namespace
            prometheus_namespace: Prometheus namespace
        """
        # Create Thanos Sidecar service
        sidecar_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "thanos-sidecar",
                "namespace": namespace
            },
            "spec": {
                "selector": {
                    "app": "prometheus",
                    "prometheus": "k8s"
                },
                "ports": [
                    {
                        "name": "grpc",
                        "port": 10901,
                        "targetPort": 10901
                    }
                ],
                "clusterIP": "None"
            }
        }
        
        # Write Thanos Sidecar service to file
        sidecar_service_path = os.path.join(self.working_dir, "thanos-sidecar-service.yaml")
        with open(sidecar_service_path, "w") as f:
            yaml.dump(sidecar_service, f)
        
        # Apply Thanos Sidecar service
        self.executor.run_kubectl_command(["apply", "-f", sidecar_service_path])
        
        # Patch Prometheus deployment to add Thanos sidecar
        try:
            # Get Prometheus deployment
            prometheus_deployment = self.executor.run_kubectl_command([
                "get", "deployment", "prometheus-k8s", "-n", prometheus_namespace, "-o", "yaml"
            ])
            
            # Parse Prometheus deployment
            prometheus_deployment_yaml = yaml.safe_load(prometheus_deployment)
            
            # Add Thanos sidecar container
            prometheus_deployment_yaml["spec"]["template"]["spec"]["containers"].append({
                "name": "thanos-sidecar",
                "image": "quay.io/thanos/thanos:v0.28.0",
                "args": [
                    "sidecar",
                    "--log.level=info",
                    "--tsdb.path=/prometheus",
                    "--prometheus.url=http://localhost:9090",
                    "--objstore.config-file=/etc/thanos/objstore.yml",
                    "--reloader.config-file=/etc/prometheus/prometheus.yaml"
                ],
                "ports": [
                    {
                        "name": "http",
                        "containerPort": 10902
                    },
                    {
                        "name": "grpc",
                        "containerPort": 10901
                    }
                ],
                "volumeMounts": [
                    {
                        "name": "prometheus-data",
                        "mountPath": "/prometheus"
                    },
                    {
                        "name": "prometheus-config",
                        "mountPath": "/etc/prometheus"
                    },
                    {
                        "name": "thanos-objstore-config",
                        "mountPath": "/etc/thanos",
                        "readOnly": true
                    }
                ]
            })
            
            # Add Thanos objstore config volume
            prometheus_deployment_yaml["spec"]["template"]["spec"]["volumes"].append({
                "name": "thanos-objstore-config",
                "secret": {
                    "secretName": "thanos-objstore-config"
                }
            })
            
            # Write patched Prometheus deployment to file
            prometheus_deployment_path = os.path.join(self.working_dir, "prometheus-deployment-patched.yaml")
            with open(prometheus_deployment_path, "w") as f:
                yaml.dump(prometheus_deployment_yaml, f)
            
            # Apply patched Prometheus deployment
            self.executor.run_kubectl_command(["apply", "-f", prometheus_deployment_path, "-n", prometheus_namespace])
        
        except Exception as e:
            logger.error(f"Failed to patch Prometheus deployment: {str(e)}")
            raise Exception(f"Failed to patch Prometheus deployment: {str(e)}")
    
    def to_mcp_context(self) -> MCPContext:
        """
        Convert Thanos integration information to MCP context.
        
        Returns:
            MCPContext: MCP context with Thanos integration information
        """
        return MCPContext(
            context_type="thanos_integration",
            thanos_query_url=self.thanos_query_url,
            object_storage_config=self.object_storage_config,
            working_dir=self.working_dir
        )


class ThanosQueryManager:
    """
    Manages Thanos queries.
    
    This class provides methods for querying Thanos for metrics, labels, and series.
    """
    
    def __init__(self, executor: 'ThanosExecutor'):
        """
        Initialize the Thanos Query Manager.
        
        Args:
            executor: Thanos executor
        """
        self.executor = executor
    
    def query_metrics(self, query: str, 
                     time: Optional[str] = None,
                     timeout: Optional[str] = None) -> Dict[str, Any]:
        """
        Query metrics from Thanos.
        
        Args:
            query: PromQL query
            time: Query time (optional)
            timeout: Query timeout (optional)
            
        Returns:
            Dict[str, Any]: Query result
        """
        # Build query parameters
        params = {
            "query": query
        }
        
        # Add optional parameters
        if time:
            params["time"] = time
        
        if timeout:
            params["timeout"] = timeout
        
        # Query metrics
        response = self.executor.make_thanos_api_request(
            "GET",
            "/api/v1/query",
            params=params
        )
        
        # Check response
        if response.status_code != 200:
            raise Exception(f"Failed to query metrics: {response.text}")
        
        # Parse response
        result = response.json()
        
        return result
    
    def query_range(self, query: str, 
                   start: str,
                   end: str,
                   step: str,
                   timeout: Optional[str] = None) -> Dict[str, Any]:
        """
        Query metrics over a time range from Thanos.
        
        Args:
            query: PromQL query
            start: Start time
            end: End time
            step: Step interval
            timeout: Query timeout (optional)
            
        Returns:
            Dict[str, Any]: Query result
        """
        # Build query parameters
        params = {
            "query": query,
            "start": start,
            "end": end,
            "step": step
        }
        
        # Add optional parameters
        if timeout:
            params["timeout"] = timeout
        
        # Query metrics range
        response = self.executor.make_thanos_api_request(
            "GET",
            "/api/v1/query_range",
            params=params
        )
        
        # Check response
        if response.status_code != 200:
            raise Exception(f"Failed to query metrics range: {response.text}")
        
        # Parse response
        result = response.json()
        
        return result
    
    def get_labels(self) -> Dict[str, Any]:
        """
        Get all label names from Thanos.
        
        Returns:
            Dict[str, Any]: Labels information
        """
        # Get labels
        response = self.executor.make_thanos_api_request(
            "GET",
            "/api/v1/labels"
        )
        
        # Check response
        if response.status_code != 200:
            raise Exception(f"Failed to get labels: {response.text}")
        
        # Parse response
        result = response.json()
        
        return result
    
    def get_label_values(self, label: str) -> Dict[str, Any]:
        """
        Get values for a label from Thanos.
        
        Args:
            label: Label name
            
        Returns:
            Dict[str, Any]: Label values information
        """
        # Get label values
        response = self.executor.make_thanos_api_request(
            "GET",
            f"/api/v1/label/{label}/values"
        )
        
        # Check response
        if response.status_code != 200:
            raise Exception(f"Failed to get label values: {response.text}")
        
        # Parse response
        result = response.json()
        
        return result
    
    def get_series(self, match: List[str], 
                  start: Optional[str] = None,
                  end: Optional[str] = None) -> Dict[str, Any]:
        """
        Get time series data from Thanos.
        
        Args:
            match: Series selectors
            start: Start time (optional)
            end: End time (optional)
            
        Returns:
            Dict[str, Any]: Series information
        """
        # Build query parameters
        params = {
            "match[]": match
        }
        
        # Add optional parameters
        if start:
            params["start"] = start
        
        if end:
            params["end"] = end
        
        # Get series
        response = self.executor.make_thanos_api_request(
            "GET",
            "/api/v1/series",
            params=params
        )
        
        # Check response
        if response.status_code != 200:
            raise Exception(f"Failed to get series: {response.text}")
        
        # Parse response
        result = response.json()
        
        return result


class ThanosStoreManager:
    """
    Manages Thanos stores.
    
    This class provides methods for managing Thanos stores,
    including getting store information.
    """
    
    def __init__(self, executor: 'ThanosExecutor'):
        """
        Initialize the Thanos Store Manager.
        
        Args:
            executor: Thanos executor
        """
        self.executor = executor
    
    def get_stores(self) -> Dict[str, Any]:
        """
        Get store information from Thanos.
        
        Returns:
            Dict[str, Any]: Store information
        """
        # Get stores
        response = self.executor.make_thanos_api_request(
            "GET",
            "/api/v1/stores"
        )
        
        # Check response
        if response.status_code != 200:
            raise Exception(f"Failed to get stores: {response.text}")
        
        # Parse response
        result = response.json()
        
        return result


class ThanosCompactorManager:
    """
    Manages Thanos compactors.
    
    This class provides methods for managing Thanos compactors,
    including getting compaction information.
    """
    
    def __init__(self, executor: 'ThanosExecutor'):
        """
        Initialize the Thanos Compactor Manager.
        
        Args:
            executor: Thanos executor
        """
        self.executor = executor
    
    def get_compaction_status(self) -> Dict[str, Any]:
        """
        Get compaction status from Thanos.
        
        Returns:
            Dict[str, Any]: Compaction status
        """
        # Get compaction status
        response = self.executor.make_thanos_api_request(
            "GET",
            "/api/v1/compaction/status"
        )
        
        # Check response
        if response.status_code != 200:
            raise Exception(f"Failed to get compaction status: {response.text}")
        
        # Parse response
        result = response.json()
        
        return result


class ThanosSidecarManager:
    """
    Manages Thanos sidecars.
    
    This class provides methods for managing Thanos sidecars,
    including getting sidecar information.
    """
    
    def __init__(self, executor: 'ThanosExecutor'):
        """
        Initialize the Thanos Sidecar Manager.
        
        Args:
            executor: Thanos executor
        """
        self.executor = executor
    
    def get_sidecar_status(self) -> Dict[str, Any]:
        """
        Get sidecar status from Thanos.
        
        Returns:
            Dict[str, Any]: Sidecar status
        """
        # Get sidecar status
        response = self.executor.make_thanos_api_request(
            "GET",
            "/api/v1/sidecar/status"
        )
        
        # Check response
        if response.status_code != 200:
            raise Exception(f"Failed to get sidecar status: {response.text}")
        
        # Parse response
        result = response.json()
        
        return result


class ThanosExecutor:
    """
    Executes Thanos API calls and kubectl commands.
    
    This class provides methods for executing Thanos API calls and kubectl commands
    and handling their output.
    """
    
    def __init__(self, thanos_query_url: Optional[str],
                kubectl_binary: str,
                working_dir: str):
        """
        Initialize the Thanos Executor.
        
        Args:
            thanos_query_url: Thanos Query URL
            kubectl_binary: Path to kubectl binary
            working_dir: Working directory for Thanos operations
        """
        self.thanos_query_url = thanos_query_url
        self.kubectl_binary = kubectl_binary
        self.working_dir = working_dir
    
    def make_thanos_api_request(self, method: str, 
                               endpoint: str,
                               params: Optional[Dict[str, Any]] = None,
                               json: Optional[Dict[str, Any]] = None,
                               data: Optional[Dict[str, Any]] = None) -> requests.Response:
        """
        Make a Thanos API request.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters (optional)
            json: JSON body (optional)
            data: Form data (optional)
            
        Returns:
            requests.Response: API response
            
        Raises:
            Exception: If Thanos Query URL is not configured
        """
        if not self.thanos_query_url:
            raise Exception("Thanos Query URL not configured")
        
        # Build URL
        url = f"{self.thanos_query_url.rstrip('/')}{endpoint}"
        
        # Build headers
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Make request
        response = requests.request(
            method=method,
            url=url,
            params=params,
            json=json,
            data=data,
            headers=headers
        )
        
        return response
    
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
