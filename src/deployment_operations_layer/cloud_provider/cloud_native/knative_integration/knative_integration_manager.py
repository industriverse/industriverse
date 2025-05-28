"""
Knative Integration Manager

This module provides integration with Knative for serverless workloads
in the Deployment Operations Layer. It handles Knative Serving, Eventing,
and Functions components.

Classes:
    KnativeIntegrationManager: Manages Knative integration
    KnativeServingManager: Manages Knative Serving resources
    KnativeEventingManager: Manages Knative Eventing resources
    KnativeFunctionsManager: Manages Knative Functions
    KnativeExecutor: Executes Knative CLI commands
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

class KnativeIntegrationManager:
    """
    Manages Knative integration for the Deployment Operations Layer.
    
    This class provides a unified interface for interacting with Knative,
    handling Serving, Eventing, and Functions components.
    """
    
    def __init__(self, kn_binary_path: Optional[str] = None, 
                kubectl_binary_path: Optional[str] = None,
                working_dir: Optional[str] = None):
        """
        Initialize the Knative Integration Manager.
        
        Args:
            kn_binary_path: Path to Knative CLI binary (optional, defaults to 'kn' in PATH)
            kubectl_binary_path: Path to kubectl binary (optional, defaults to 'kubectl' in PATH)
            working_dir: Working directory for Knative operations (optional)
        """
        self.kn_binary = kn_binary_path or "kn"
        self.kubectl_binary = kubectl_binary_path or "kubectl"
        self.working_dir = working_dir or tempfile.mkdtemp(prefix="knative_")
        
        self.executor = KnativeExecutor(self.kn_binary, self.kubectl_binary, self.working_dir)
        self.serving_manager = KnativeServingManager(self.executor)
        self.eventing_manager = KnativeEventingManager(self.executor)
        self.functions_manager = KnativeFunctionsManager(self.executor)
        
        # Verify Knative installation
        self._verify_knative_installation()
    
    def _verify_knative_installation(self):
        """
        Verify that Knative is installed and available.
        
        Logs a warning if Knative is not installed but does not raise an exception
        as Knative may be accessed via API or other means.
        """
        try:
            version = self.executor.run_kn_command(["version"], check=False)
            logger.info(f"Knative CLI version: {version}")
        except Exception as e:
            logger.warning(f"Knative CLI not installed or not accessible: {str(e)}")
    
    def install_knative_serving(self, version: str = "latest") -> AgentResponse:
        """
        Install Knative Serving on a Kubernetes cluster.
        
        Args:
            version: Knative Serving version (default: "latest")
            
        Returns:
            AgentResponse: Installation response
        """
        try:
            # Install Knative Serving CRDs
            if version == "latest":
                crds_url = "https://github.com/knative/serving/releases/latest/download/serving-crds.yaml"
            else:
                crds_url = f"https://github.com/knative/serving/releases/download/knative-v{version}/serving-crds.yaml"
            
            crds_output = self.executor.run_kubectl_command([
                "apply", "-f", crds_url
            ])
            
            # Install Knative Serving core
            if version == "latest":
                core_url = "https://github.com/knative/serving/releases/latest/download/serving-core.yaml"
            else:
                core_url = f"https://github.com/knative/serving/releases/download/knative-v{version}/serving-core.yaml"
            
            core_output = self.executor.run_kubectl_command([
                "apply", "-f", core_url
            ])
            
            # Install Kourier networking layer
            if version == "latest":
                kourier_url = "https://github.com/knative/net-kourier/releases/latest/download/kourier.yaml"
            else:
                kourier_url = f"https://github.com/knative/net-kourier/releases/download/knative-v{version}/kourier.yaml"
            
            kourier_output = self.executor.run_kubectl_command([
                "apply", "-f", kourier_url
            ])
            
            # Configure Knative Serving to use Kourier
            config_output = self.executor.run_kubectl_command([
                "patch", "configmap/config-network", 
                "--namespace", "knative-serving", 
                "--type", "merge", 
                "--patch", '{"data":{"ingress.class":"kourier.ingress.networking.knative.dev"}}'
            ])
            
            return AgentResponse(
                success=True,
                message=f"Knative Serving {version} installed successfully",
                data={
                    "version": version,
                    "crds_output": crds_output,
                    "core_output": core_output,
                    "kourier_output": kourier_output,
                    "config_output": config_output
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to install Knative Serving: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to install Knative Serving: {str(e)}",
                data={}
            )
    
    def install_knative_eventing(self, version: str = "latest") -> AgentResponse:
        """
        Install Knative Eventing on a Kubernetes cluster.
        
        Args:
            version: Knative Eventing version (default: "latest")
            
        Returns:
            AgentResponse: Installation response
        """
        try:
            # Install Knative Eventing CRDs
            if version == "latest":
                crds_url = "https://github.com/knative/eventing/releases/latest/download/eventing-crds.yaml"
            else:
                crds_url = f"https://github.com/knative/eventing/releases/download/knative-v{version}/eventing-crds.yaml"
            
            crds_output = self.executor.run_kubectl_command([
                "apply", "-f", crds_url
            ])
            
            # Install Knative Eventing core
            if version == "latest":
                core_url = "https://github.com/knative/eventing/releases/latest/download/eventing-core.yaml"
            else:
                core_url = f"https://github.com/knative/eventing/releases/download/knative-v{version}/eventing-core.yaml"
            
            core_output = self.executor.run_kubectl_command([
                "apply", "-f", core_url
            ])
            
            # Install default in-memory channel
            if version == "latest":
                channel_url = "https://github.com/knative/eventing/releases/latest/download/in-memory-channel.yaml"
            else:
                channel_url = f"https://github.com/knative/eventing/releases/download/knative-v{version}/in-memory-channel.yaml"
            
            channel_output = self.executor.run_kubectl_command([
                "apply", "-f", channel_url
            ])
            
            # Install default broker
            if version == "latest":
                broker_url = "https://github.com/knative/eventing/releases/latest/download/mt-channel-broker.yaml"
            else:
                broker_url = f"https://github.com/knative/eventing/releases/download/knative-v{version}/mt-channel-broker.yaml"
            
            broker_output = self.executor.run_kubectl_command([
                "apply", "-f", broker_url
            ])
            
            return AgentResponse(
                success=True,
                message=f"Knative Eventing {version} installed successfully",
                data={
                    "version": version,
                    "crds_output": crds_output,
                    "core_output": core_output,
                    "channel_output": channel_output,
                    "broker_output": broker_output
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to install Knative Eventing: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to install Knative Eventing: {str(e)}",
                data={}
            )
    
    def create_service(self, name: str, image: str, 
                      namespace: str = "default",
                      env: Optional[Dict[str, str]] = None,
                      min_scale: Optional[int] = None,
                      max_scale: Optional[int] = None) -> AgentResponse:
        """
        Create a Knative Service.
        
        Args:
            name: Service name
            image: Container image
            namespace: Namespace (default: "default")
            env: Environment variables (optional)
            min_scale: Minimum scale (optional)
            max_scale: Maximum scale (optional)
            
        Returns:
            AgentResponse: Service creation response
        """
        try:
            result = self.serving_manager.create_service(
                name=name,
                image=image,
                namespace=namespace,
                env=env,
                min_scale=min_scale,
                max_scale=max_scale
            )
            
            return AgentResponse(
                success=True,
                message=f"Knative Service {name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create Knative Service: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create Knative Service: {str(e)}",
                data={}
            )
    
    def create_broker(self, name: str, namespace: str = "default") -> AgentResponse:
        """
        Create a Knative Broker.
        
        Args:
            name: Broker name
            namespace: Namespace (default: "default")
            
        Returns:
            AgentResponse: Broker creation response
        """
        try:
            result = self.eventing_manager.create_broker(
                name=name,
                namespace=namespace
            )
            
            return AgentResponse(
                success=True,
                message=f"Knative Broker {name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create Knative Broker: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create Knative Broker: {str(e)}",
                data={}
            )
    
    def create_trigger(self, name: str, broker: str, 
                      subscriber: str, 
                      filter_attributes: Optional[Dict[str, str]] = None,
                      namespace: str = "default") -> AgentResponse:
        """
        Create a Knative Trigger.
        
        Args:
            name: Trigger name
            broker: Broker name
            subscriber: Subscriber service
            filter_attributes: Filter attributes (optional)
            namespace: Namespace (default: "default")
            
        Returns:
            AgentResponse: Trigger creation response
        """
        try:
            result = self.eventing_manager.create_trigger(
                name=name,
                broker=broker,
                subscriber=subscriber,
                filter_attributes=filter_attributes,
                namespace=namespace
            )
            
            return AgentResponse(
                success=True,
                message=f"Knative Trigger {name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create Knative Trigger: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create Knative Trigger: {str(e)}",
                data={}
            )
    
    def create_function(self, name: str, runtime: str, 
                       source_dir: str, 
                       namespace: str = "default") -> AgentResponse:
        """
        Create a Knative Function.
        
        Args:
            name: Function name
            runtime: Function runtime (e.g., "python", "node", "go")
            source_dir: Source directory
            namespace: Namespace (default: "default")
            
        Returns:
            AgentResponse: Function creation response
        """
        try:
            result = self.functions_manager.create_function(
                name=name,
                runtime=runtime,
                source_dir=source_dir,
                namespace=namespace
            )
            
            return AgentResponse(
                success=True,
                message=f"Knative Function {name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create Knative Function: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create Knative Function: {str(e)}",
                data={}
            )
    
    def list_services(self, namespace: str = "default") -> AgentResponse:
        """
        List Knative Services.
        
        Args:
            namespace: Namespace (default: "default")
            
        Returns:
            AgentResponse: Service list response
        """
        try:
            result = self.serving_manager.list_services(namespace)
            
            return AgentResponse(
                success=True,
                message=f"Found {len(result)} Knative Services in namespace {namespace}",
                data={
                    "services": result
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to list Knative Services: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to list Knative Services: {str(e)}",
                data={}
            )
    
    def list_brokers(self, namespace: str = "default") -> AgentResponse:
        """
        List Knative Brokers.
        
        Args:
            namespace: Namespace (default: "default")
            
        Returns:
            AgentResponse: Broker list response
        """
        try:
            result = self.eventing_manager.list_brokers(namespace)
            
            return AgentResponse(
                success=True,
                message=f"Found {len(result)} Knative Brokers in namespace {namespace}",
                data={
                    "brokers": result
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to list Knative Brokers: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to list Knative Brokers: {str(e)}",
                data={}
            )
    
    def list_triggers(self, namespace: str = "default") -> AgentResponse:
        """
        List Knative Triggers.
        
        Args:
            namespace: Namespace (default: "default")
            
        Returns:
            AgentResponse: Trigger list response
        """
        try:
            result = self.eventing_manager.list_triggers(namespace)
            
            return AgentResponse(
                success=True,
                message=f"Found {len(result)} Knative Triggers in namespace {namespace}",
                data={
                    "triggers": result
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to list Knative Triggers: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to list Knative Triggers: {str(e)}",
                data={}
            )
    
    def delete_service(self, name: str, namespace: str = "default") -> AgentResponse:
        """
        Delete a Knative Service.
        
        Args:
            name: Service name
            namespace: Namespace (default: "default")
            
        Returns:
            AgentResponse: Deletion response
        """
        try:
            result = self.serving_manager.delete_service(
                name=name,
                namespace=namespace
            )
            
            return AgentResponse(
                success=True,
                message=f"Knative Service {name} deleted successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to delete Knative Service: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to delete Knative Service: {str(e)}",
                data={}
            )
    
    def to_mcp_context(self) -> MCPContext:
        """
        Convert Knative integration information to MCP context.
        
        Returns:
            MCPContext: MCP context with Knative integration information
        """
        return MCPContext(
            context_type="knative_integration",
            knative_version=self._get_knative_version(),
            working_dir=self.working_dir
        )
    
    def _get_knative_version(self) -> str:
        """
        Get the Knative version.
        
        Returns:
            str: Knative version
        """
        try:
            version_output = self.executor.run_kn_command(["version"], check=False)
            return version_output.strip()
        except Exception as e:
            logger.error(f"Failed to get Knative version: {str(e)}")
            return "unknown"


class KnativeServingManager:
    """
    Manages Knative Serving resources.
    
    This class provides methods for managing Knative Serving resources,
    including Services, Revisions, and Routes.
    """
    
    def __init__(self, executor: 'KnativeExecutor'):
        """
        Initialize the Knative Serving Manager.
        
        Args:
            executor: Knative executor
        """
        self.executor = executor
    
    def create_service(self, name: str, image: str, 
                      namespace: str = "default",
                      env: Optional[Dict[str, str]] = None,
                      min_scale: Optional[int] = None,
                      max_scale: Optional[int] = None) -> Dict[str, Any]:
        """
        Create a Knative Service.
        
        Args:
            name: Service name
            image: Container image
            namespace: Namespace (default: "default")
            env: Environment variables (optional)
            min_scale: Minimum scale (optional)
            max_scale: Maximum scale (optional)
            
        Returns:
            Dict[str, Any]: Service creation result
        """
        args = ["service", "create", name, "--image", image, "-n", namespace]
        
        # Add environment variables
        if env:
            for key, value in env.items():
                args.extend(["--env", f"{key}={value}"])
        
        # Add scaling options
        if min_scale is not None:
            args.extend(["--annotation", f"autoscaling.knative.dev/minScale={min_scale}"])
        
        if max_scale is not None:
            args.extend(["--annotation", f"autoscaling.knative.dev/maxScale={max_scale}"])
        
        # Create service
        output = self.executor.run_kn_command(args)
        
        return {
            "name": name,
            "image": image,
            "namespace": namespace,
            "env": env,
            "min_scale": min_scale,
            "max_scale": max_scale,
            "output": output
        }
    
    def update_service(self, name: str, 
                      namespace: str = "default",
                      image: Optional[str] = None,
                      env: Optional[Dict[str, str]] = None,
                      min_scale: Optional[int] = None,
                      max_scale: Optional[int] = None) -> Dict[str, Any]:
        """
        Update a Knative Service.
        
        Args:
            name: Service name
            namespace: Namespace (default: "default")
            image: Container image (optional)
            env: Environment variables (optional)
            min_scale: Minimum scale (optional)
            max_scale: Maximum scale (optional)
            
        Returns:
            Dict[str, Any]: Service update result
        """
        args = ["service", "update", name, "-n", namespace]
        
        # Add image if provided
        if image:
            args.extend(["--image", image])
        
        # Add environment variables
        if env:
            for key, value in env.items():
                args.extend(["--env", f"{key}={value}"])
        
        # Add scaling options
        if min_scale is not None:
            args.extend(["--annotation", f"autoscaling.knative.dev/minScale={min_scale}"])
        
        if max_scale is not None:
            args.extend(["--annotation", f"autoscaling.knative.dev/maxScale={max_scale}"])
        
        # Update service
        output = self.executor.run_kn_command(args)
        
        return {
            "name": name,
            "namespace": namespace,
            "image": image,
            "env": env,
            "min_scale": min_scale,
            "max_scale": max_scale,
            "output": output
        }
    
    def list_services(self, namespace: str = "default") -> List[Dict[str, Any]]:
        """
        List Knative Services.
        
        Args:
            namespace: Namespace (default: "default")
            
        Returns:
            List[Dict[str, Any]]: List of services
        """
        output = self.executor.run_kubectl_command([
            "get", "ksvc", "-n", namespace, "-o", "json"
        ])
        
        try:
            services_json = json.loads(output)
            
            services = []
            for service in services_json.get("items", []):
                service_info = {
                    "name": service["metadata"]["name"],
                    "namespace": service["metadata"]["namespace"],
                    "url": service["status"].get("url"),
                    "latest_created_revision": service["status"].get("latestCreatedRevisionName"),
                    "latest_ready_revision": service["status"].get("latestReadyRevisionName"),
                    "conditions": service["status"].get("conditions", [])
                }
                services.append(service_info)
            
            return services
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse service list: {str(e)}")
            return []
    
    def get_service(self, name: str, namespace: str = "default") -> Dict[str, Any]:
        """
        Get a Knative Service.
        
        Args:
            name: Service name
            namespace: Namespace (default: "default")
            
        Returns:
            Dict[str, Any]: Service details
        """
        output = self.executor.run_kubectl_command([
            "get", "ksvc", name, "-n", namespace, "-o", "json"
        ])
        
        try:
            service_json = json.loads(output)
            
            return {
                "name": service_json["metadata"]["name"],
                "namespace": service_json["metadata"]["namespace"],
                "url": service_json["status"].get("url"),
                "latest_created_revision": service_json["status"].get("latestCreatedRevisionName"),
                "latest_ready_revision": service_json["status"].get("latestReadyRevisionName"),
                "conditions": service_json["status"].get("conditions", []),
                "spec": service_json.get("spec", {})
            }
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse service details: {str(e)}")
            return {"name": name, "namespace": namespace, "error": str(e)}
    
    def delete_service(self, name: str, namespace: str = "default") -> Dict[str, Any]:
        """
        Delete a Knative Service.
        
        Args:
            name: Service name
            namespace: Namespace (default: "default")
            
        Returns:
            Dict[str, Any]: Deletion result
        """
        output = self.executor.run_kn_command([
            "service", "delete", name, "-n", namespace
        ])
        
        return {
            "name": name,
            "namespace": namespace,
            "output": output
        }


class KnativeEventingManager:
    """
    Manages Knative Eventing resources.
    
    This class provides methods for managing Knative Eventing resources,
    including Brokers, Triggers, and Sources.
    """
    
    def __init__(self, executor: 'KnativeExecutor'):
        """
        Initialize the Knative Eventing Manager.
        
        Args:
            executor: Knative executor
        """
        self.executor = executor
    
    def create_broker(self, name: str, namespace: str = "default") -> Dict[str, Any]:
        """
        Create a Knative Broker.
        
        Args:
            name: Broker name
            namespace: Namespace (default: "default")
            
        Returns:
            Dict[str, Any]: Broker creation result
        """
        output = self.executor.run_kn_command([
            "broker", "create", name, "-n", namespace
        ])
        
        return {
            "name": name,
            "namespace": namespace,
            "output": output
        }
    
    def create_trigger(self, name: str, broker: str, 
                      subscriber: str, 
                      filter_attributes: Optional[Dict[str, str]] = None,
                      namespace: str = "default") -> Dict[str, Any]:
        """
        Create a Knative Trigger.
        
        Args:
            name: Trigger name
            broker: Broker name
            subscriber: Subscriber service
            filter_attributes: Filter attributes (optional)
            namespace: Namespace (default: "default")
            
        Returns:
            Dict[str, Any]: Trigger creation result
        """
        args = [
            "trigger", "create", name,
            "--broker", broker,
            "--sink", subscriber,
            "-n", namespace
        ]
        
        # Add filter attributes
        if filter_attributes:
            for key, value in filter_attributes.items():
                args.extend(["--filter", f"{key}={value}"])
        
        # Create trigger
        output = self.executor.run_kn_command(args)
        
        return {
            "name": name,
            "broker": broker,
            "subscriber": subscriber,
            "filter_attributes": filter_attributes,
            "namespace": namespace,
            "output": output
        }
    
    def list_brokers(self, namespace: str = "default") -> List[Dict[str, Any]]:
        """
        List Knative Brokers.
        
        Args:
            namespace: Namespace (default: "default")
            
        Returns:
            List[Dict[str, Any]]: List of brokers
        """
        output = self.executor.run_kubectl_command([
            "get", "brokers", "-n", namespace, "-o", "json"
        ])
        
        try:
            brokers_json = json.loads(output)
            
            brokers = []
            for broker in brokers_json.get("items", []):
                broker_info = {
                    "name": broker["metadata"]["name"],
                    "namespace": broker["metadata"]["namespace"],
                    "url": broker["status"].get("address", {}).get("url"),
                    "conditions": broker["status"].get("conditions", [])
                }
                brokers.append(broker_info)
            
            return brokers
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse broker list: {str(e)}")
            return []
    
    def list_triggers(self, namespace: str = "default") -> List[Dict[str, Any]]:
        """
        List Knative Triggers.
        
        Args:
            namespace: Namespace (default: "default")
            
        Returns:
            List[Dict[str, Any]]: List of triggers
        """
        output = self.executor.run_kubectl_command([
            "get", "triggers", "-n", namespace, "-o", "json"
        ])
        
        try:
            triggers_json = json.loads(output)
            
            triggers = []
            for trigger in triggers_json.get("items", []):
                trigger_info = {
                    "name": trigger["metadata"]["name"],
                    "namespace": trigger["metadata"]["namespace"],
                    "broker": trigger["spec"].get("broker"),
                    "subscriber": trigger["spec"].get("subscriber", {}).get("ref", {}).get("name"),
                    "filters": trigger["spec"].get("filter", {}).get("attributes", {}),
                    "conditions": trigger["status"].get("conditions", [])
                }
                triggers.append(trigger_info)
            
            return triggers
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse trigger list: {str(e)}")
            return []
    
    def delete_broker(self, name: str, namespace: str = "default") -> Dict[str, Any]:
        """
        Delete a Knative Broker.
        
        Args:
            name: Broker name
            namespace: Namespace (default: "default")
            
        Returns:
            Dict[str, Any]: Deletion result
        """
        output = self.executor.run_kn_command([
            "broker", "delete", name, "-n", namespace
        ])
        
        return {
            "name": name,
            "namespace": namespace,
            "output": output
        }
    
    def delete_trigger(self, name: str, namespace: str = "default") -> Dict[str, Any]:
        """
        Delete a Knative Trigger.
        
        Args:
            name: Trigger name
            namespace: Namespace (default: "default")
            
        Returns:
            Dict[str, Any]: Deletion result
        """
        output = self.executor.run_kn_command([
            "trigger", "delete", name, "-n", namespace
        ])
        
        return {
            "name": name,
            "namespace": namespace,
            "output": output
        }


class KnativeFunctionsManager:
    """
    Manages Knative Functions.
    
    This class provides methods for managing Knative Functions,
    including creation, building, and deployment.
    """
    
    def __init__(self, executor: 'KnativeExecutor'):
        """
        Initialize the Knative Functions Manager.
        
        Args:
            executor: Knative executor
        """
        self.executor = executor
    
    def create_function(self, name: str, runtime: str, 
                       source_dir: str, 
                       namespace: str = "default") -> Dict[str, Any]:
        """
        Create a Knative Function.
        
        Args:
            name: Function name
            runtime: Function runtime (e.g., "python", "node", "go")
            source_dir: Source directory
            namespace: Namespace (default: "default")
            
        Returns:
            Dict[str, Any]: Function creation result
        """
        # Create function
        create_output = self.executor.run_kn_command([
            "func", "create", name, "--runtime", runtime, "--template", "http"
        ], cwd=source_dir)
        
        # Build function
        build_output = self.executor.run_kn_command([
            "func", "build", "--path", f"{source_dir}/{name}"
        ])
        
        # Deploy function
        deploy_output = self.executor.run_kn_command([
            "func", "deploy", "--path", f"{source_dir}/{name}", "--namespace", namespace
        ])
        
        return {
            "name": name,
            "runtime": runtime,
            "source_dir": source_dir,
            "namespace": namespace,
            "create_output": create_output,
            "build_output": build_output,
            "deploy_output": deploy_output
        }
    
    def list_functions(self, namespace: str = "default") -> List[Dict[str, Any]]:
        """
        List Knative Functions.
        
        Args:
            namespace: Namespace (default: "default")
            
        Returns:
            List[Dict[str, Any]]: List of functions
        """
        output = self.executor.run_kn_command([
            "func", "list", "-n", namespace, "-o", "json"
        ], check=False)
        
        try:
            functions_json = json.loads(output)
            
            functions = []
            for function in functions_json:
                function_info = {
                    "name": function.get("name"),
                    "namespace": function.get("namespace"),
                    "runtime": function.get("runtime"),
                    "url": function.get("url"),
                    "ready": function.get("ready")
                }
                functions.append(function_info)
            
            return functions
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse function list: {str(e)}")
            return []
    
    def delete_function(self, name: str, namespace: str = "default") -> Dict[str, Any]:
        """
        Delete a Knative Function.
        
        Args:
            name: Function name
            namespace: Namespace (default: "default")
            
        Returns:
            Dict[str, Any]: Deletion result
        """
        output = self.executor.run_kn_command([
            "func", "delete", name, "-n", namespace
        ])
        
        return {
            "name": name,
            "namespace": namespace,
            "output": output
        }


class KnativeExecutor:
    """
    Executes Knative CLI commands.
    
    This class provides methods for executing Knative CLI and kubectl commands
    and handling their output.
    """
    
    def __init__(self, kn_binary: str, kubectl_binary: str, working_dir: str):
        """
        Initialize the Knative Executor.
        
        Args:
            kn_binary: Path to Knative CLI binary
            kubectl_binary: Path to kubectl binary
            working_dir: Working directory for Knative operations
        """
        self.kn_binary = kn_binary
        self.kubectl_binary = kubectl_binary
        self.working_dir = working_dir
    
    def run_kn_command(self, args: List[str], check: bool = True, cwd: Optional[str] = None) -> str:
        """
        Run a Knative CLI command.
        
        Args:
            args: Command arguments
            check: Whether to check for command success
            cwd: Working directory (optional, defaults to self.working_dir)
            
        Returns:
            str: Command output
            
        Raises:
            Exception: If the command fails and check is True
        """
        cmd = [self.kn_binary] + args
        logger.info(f"Running Knative command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd or self.working_dir,
                capture_output=True,
                text=True,
                check=check
            )
            
            return result.stdout
        
        except subprocess.CalledProcessError as e:
            error_message = f"Knative command failed: {e.stderr}"
            logger.error(error_message)
            
            if check:
                raise Exception(error_message)
            
            return e.stderr
    
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
