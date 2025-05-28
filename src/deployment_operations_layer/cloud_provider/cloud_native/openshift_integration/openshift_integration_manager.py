"""
OpenShift Integration Manager

This module provides integration with OpenShift for the Deployment Operations Layer.
It handles OpenShift-specific resources, routes, builds, and deployment configurations.

Classes:
    OpenShiftIntegrationManager: Manages OpenShift integration
    OpenShiftRouteManager: Manages OpenShift routes
    OpenShiftBuildManager: Manages OpenShift builds
    OpenShiftDeploymentConfigManager: Manages OpenShift deployment configs
    OpenShiftExecutor: Executes OpenShift CLI commands
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

class OpenShiftIntegrationManager:
    """
    Manages OpenShift integration for the Deployment Operations Layer.
    
    This class provides a unified interface for interacting with OpenShift,
    handling routes, builds, deployment configs, and other OpenShift-specific resources.
    """
    
    def __init__(self, oc_binary_path: Optional[str] = None,
                working_dir: Optional[str] = None):
        """
        Initialize the OpenShift Integration Manager.
        
        Args:
            oc_binary_path: Path to oc binary (optional, defaults to 'oc' in PATH)
            working_dir: Working directory for OpenShift operations (optional)
        """
        self.oc_binary = oc_binary_path or "oc"
        self.working_dir = working_dir or tempfile.mkdtemp(prefix="openshift_")
        
        self.executor = OpenShiftExecutor(self.oc_binary, self.working_dir)
        self.route_manager = OpenShiftRouteManager(self.executor)
        self.build_manager = OpenShiftBuildManager(self.executor)
        self.deployment_config_manager = OpenShiftDeploymentConfigManager(self.executor)
        
        # Verify OpenShift CLI installation
        self._verify_openshift_installation()
    
    def _verify_openshift_installation(self):
        """
        Verify that OpenShift CLI is installed and available.
        
        Logs a warning if OpenShift CLI is not installed but does not raise an exception
        as OpenShift may be accessed via API or other means.
        """
        try:
            version = self.executor.run_oc_command(["version"], check=False)
            logger.info(f"OpenShift client version: {version}")
        except Exception as e:
            logger.warning(f"OpenShift client not installed or not accessible: {str(e)}")
    
    def create_route(self, name: str, 
                    namespace: str,
                    service: str,
                    port: int,
                    tls_termination: Optional[str] = None,
                    host: Optional[str] = None) -> AgentResponse:
        """
        Create an OpenShift route.
        
        Args:
            name: Route name
            namespace: Namespace
            service: Service name
            port: Service port
            tls_termination: TLS termination type (optional)
            host: Host name (optional)
            
        Returns:
            AgentResponse: Route creation response
        """
        try:
            result = self.route_manager.create_route(
                name=name,
                namespace=namespace,
                service=service,
                port=port,
                tls_termination=tls_termination,
                host=host
            )
            
            return AgentResponse(
                success=True,
                message=f"OpenShift route {name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create OpenShift route: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create OpenShift route: {str(e)}",
                data={}
            )
    
    def create_build_config(self, name: str, 
                           namespace: str,
                           git_url: str,
                           git_ref: str,
                           context_dir: Optional[str] = None,
                           strategy: str = "Source",
                           builder_image: Optional[str] = None,
                           output_image_stream: Optional[str] = None) -> AgentResponse:
        """
        Create an OpenShift build config.
        
        Args:
            name: Build config name
            namespace: Namespace
            git_url: Git repository URL
            git_ref: Git reference (branch, tag, commit)
            context_dir: Context directory (optional)
            strategy: Build strategy (default: Source)
            builder_image: Builder image (optional)
            output_image_stream: Output image stream (optional)
            
        Returns:
            AgentResponse: Build config creation response
        """
        try:
            result = self.build_manager.create_build_config(
                name=name,
                namespace=namespace,
                git_url=git_url,
                git_ref=git_ref,
                context_dir=context_dir,
                strategy=strategy,
                builder_image=builder_image,
                output_image_stream=output_image_stream
            )
            
            return AgentResponse(
                success=True,
                message=f"OpenShift build config {name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create OpenShift build config: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create OpenShift build config: {str(e)}",
                data={}
            )
    
    def start_build(self, name: str, 
                   namespace: str,
                   follow: bool = False) -> AgentResponse:
        """
        Start an OpenShift build.
        
        Args:
            name: Build config name
            namespace: Namespace
            follow: Whether to follow build logs (default: False)
            
        Returns:
            AgentResponse: Build start response
        """
        try:
            result = self.build_manager.start_build(
                name=name,
                namespace=namespace,
                follow=follow
            )
            
            return AgentResponse(
                success=True,
                message=f"OpenShift build {name} started successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to start OpenShift build: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to start OpenShift build: {str(e)}",
                data={}
            )
    
    def create_deployment_config(self, name: str, 
                               namespace: str,
                               image: str,
                               replicas: int = 1,
                               ports: Optional[List[Dict[str, Any]]] = None,
                               env_vars: Optional[Dict[str, str]] = None,
                               volumes: Optional[List[Dict[str, Any]]] = None,
                               volume_mounts: Optional[List[Dict[str, Any]]] = None) -> AgentResponse:
        """
        Create an OpenShift deployment config.
        
        Args:
            name: Deployment config name
            namespace: Namespace
            image: Container image
            replicas: Number of replicas (default: 1)
            ports: Container ports (optional)
            env_vars: Environment variables (optional)
            volumes: Volumes (optional)
            volume_mounts: Volume mounts (optional)
            
        Returns:
            AgentResponse: Deployment config creation response
        """
        try:
            result = self.deployment_config_manager.create_deployment_config(
                name=name,
                namespace=namespace,
                image=image,
                replicas=replicas,
                ports=ports,
                env_vars=env_vars,
                volumes=volumes,
                volume_mounts=volume_mounts
            )
            
            return AgentResponse(
                success=True,
                message=f"OpenShift deployment config {name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create OpenShift deployment config: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create OpenShift deployment config: {str(e)}",
                data={}
            )
    
    def create_image_stream(self, name: str, 
                           namespace: str,
                           tags: Optional[List[Dict[str, Any]]] = None) -> AgentResponse:
        """
        Create an OpenShift image stream.
        
        Args:
            name: Image stream name
            namespace: Namespace
            tags: Image stream tags (optional)
            
        Returns:
            AgentResponse: Image stream creation response
        """
        try:
            # Create image stream manifest
            image_stream = {
                "apiVersion": "image.openshift.io/v1",
                "kind": "ImageStream",
                "metadata": {
                    "name": name,
                    "namespace": namespace
                },
                "spec": {}
            }
            
            # Add tags if provided
            if tags:
                image_stream["spec"]["tags"] = tags
            
            # Write image stream to temporary file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
                yaml.dump(image_stream, f)
                image_stream_file = f.name
            
            try:
                # Apply image stream
                output = self.executor.run_oc_command([
                    "apply", "-f", image_stream_file
                ])
                
                return AgentResponse(
                    success=True,
                    message=f"OpenShift image stream {name} created successfully",
                    data={
                        "name": name,
                        "namespace": namespace,
                        "tags": tags,
                        "output": output
                    }
                )
            
            finally:
                # Clean up temporary file
                if os.path.exists(image_stream_file):
                    os.unlink(image_stream_file)
        
        except Exception as e:
            logger.error(f"Failed to create OpenShift image stream: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create OpenShift image stream: {str(e)}",
                data={}
            )
    
    def create_project(self, name: str, 
                      display_name: Optional[str] = None,
                      description: Optional[str] = None) -> AgentResponse:
        """
        Create an OpenShift project.
        
        Args:
            name: Project name
            display_name: Display name (optional)
            description: Description (optional)
            
        Returns:
            AgentResponse: Project creation response
        """
        try:
            # Build command
            cmd = ["new-project", name]
            
            # Add display name if provided
            if display_name:
                cmd.extend(["--display-name", display_name])
            
            # Add description if provided
            if description:
                cmd.extend(["--description", description])
            
            # Create project
            output = self.executor.run_oc_command(cmd)
            
            return AgentResponse(
                success=True,
                message=f"OpenShift project {name} created successfully",
                data={
                    "name": name,
                    "display_name": display_name,
                    "description": description,
                    "output": output
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to create OpenShift project: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create OpenShift project: {str(e)}",
                data={}
            )
    
    def process_template(self, template_name: str, 
                        namespace: Optional[str] = None,
                        parameters: Optional[Dict[str, str]] = None,
                        template_file: Optional[str] = None) -> AgentResponse:
        """
        Process an OpenShift template.
        
        Args:
            template_name: Template name
            namespace: Namespace (optional)
            parameters: Template parameters (optional)
            template_file: Template file path (optional)
            
        Returns:
            AgentResponse: Template processing response
        """
        try:
            # Build command
            cmd = ["process"]
            
            # Add namespace if provided
            if namespace:
                cmd.extend(["-n", namespace])
            
            # Add template name or file
            if template_file:
                cmd.extend(["-f", template_file])
            else:
                cmd.append(template_name)
            
            # Add parameters if provided
            if parameters:
                for key, value in parameters.items():
                    cmd.extend(["-p", f"{key}={value}"])
            
            # Process template
            output = self.executor.run_oc_command(cmd)
            
            try:
                # Parse output as YAML
                processed_template = yaml.safe_load_all(output)
                
                return AgentResponse(
                    success=True,
                    message=f"OpenShift template {template_name} processed successfully",
                    data={
                        "template_name": template_name,
                        "namespace": namespace,
                        "parameters": parameters,
                        "template_file": template_file,
                        "processed_template": list(processed_template)
                    }
                )
            
            except yaml.YAMLError as e:
                logger.error(f"Failed to parse processed template: {str(e)}")
                return AgentResponse(
                    success=False,
                    message=f"Failed to parse processed template: {str(e)}",
                    data={
                        "template_name": template_name,
                        "namespace": namespace,
                        "parameters": parameters,
                        "template_file": template_file,
                        "output": output
                    }
                )
        
        except Exception as e:
            logger.error(f"Failed to process OpenShift template: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to process OpenShift template: {str(e)}",
                data={}
            )
    
    def to_mcp_context(self) -> MCPContext:
        """
        Convert OpenShift integration information to MCP context.
        
        Returns:
            MCPContext: MCP context with OpenShift integration information
        """
        return MCPContext(
            context_type="openshift_integration",
            openshift_version=self._get_openshift_version(),
            working_dir=self.working_dir
        )
    
    def _get_openshift_version(self) -> str:
        """
        Get the OpenShift version.
        
        Returns:
            str: OpenShift version
        """
        try:
            version_output = self.executor.run_oc_command(["version"], check=False)
            return version_output.strip()
        except Exception as e:
            logger.error(f"Failed to get OpenShift version: {str(e)}")
            return "unknown"


class OpenShiftRouteManager:
    """
    Manages OpenShift routes.
    
    This class provides methods for managing OpenShift routes,
    including creation, modification, and listing.
    """
    
    def __init__(self, executor: 'OpenShiftExecutor'):
        """
        Initialize the OpenShift Route Manager.
        
        Args:
            executor: OpenShift executor
        """
        self.executor = executor
    
    def create_route(self, name: str, 
                    namespace: str,
                    service: str,
                    port: int,
                    tls_termination: Optional[str] = None,
                    host: Optional[str] = None) -> Dict[str, Any]:
        """
        Create an OpenShift route.
        
        Args:
            name: Route name
            namespace: Namespace
            service: Service name
            port: Service port
            tls_termination: TLS termination type (optional)
            host: Host name (optional)
            
        Returns:
            Dict[str, Any]: Route creation result
        """
        # Create route manifest
        route = {
            "apiVersion": "route.openshift.io/v1",
            "kind": "Route",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "to": {
                    "kind": "Service",
                    "name": service
                },
                "port": {
                    "targetPort": port
                }
            }
        }
        
        # Add host if provided
        if host:
            route["spec"]["host"] = host
        
        # Add TLS if provided
        if tls_termination:
            route["spec"]["tls"] = {
                "termination": tls_termination
            }
        
        # Write route to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(route, f)
            route_file = f.name
        
        try:
            # Apply route
            output = self.executor.run_oc_command([
                "apply", "-f", route_file
            ])
            
            return {
                "name": name,
                "namespace": namespace,
                "service": service,
                "port": port,
                "tls_termination": tls_termination,
                "host": host,
                "output": output
            }
        
        finally:
            # Clean up temporary file
            if os.path.exists(route_file):
                os.unlink(route_file)
    
    def get_route(self, name: str, namespace: str) -> Dict[str, Any]:
        """
        Get an OpenShift route.
        
        Args:
            name: Route name
            namespace: Namespace
            
        Returns:
            Dict[str, Any]: Route information
        """
        output = self.executor.run_oc_command([
            "get", "route", name, "-n", namespace, "-o", "json"
        ])
        
        try:
            route_json = json.loads(output)
            
            return {
                "name": route_json["metadata"]["name"],
                "namespace": route_json["metadata"]["namespace"],
                "host": route_json["spec"].get("host"),
                "service": route_json["spec"]["to"]["name"],
                "port": route_json["spec"]["port"].get("targetPort"),
                "tls_termination": route_json["spec"].get("tls", {}).get("termination"),
                "created_at": route_json["metadata"].get("creationTimestamp")
            }
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse route information: {str(e)}")
            return {
                "name": name,
                "namespace": namespace,
                "error": str(e),
                "output": output
            }
    
    def list_routes(self, namespace: str) -> List[Dict[str, Any]]:
        """
        List OpenShift routes.
        
        Args:
            namespace: Namespace
            
        Returns:
            List[Dict[str, Any]]: List of routes
        """
        output = self.executor.run_oc_command([
            "get", "routes", "-n", namespace, "-o", "json"
        ])
        
        try:
            routes_json = json.loads(output)
            
            routes = []
            for route in routes_json.get("items", []):
                route_info = {
                    "name": route["metadata"]["name"],
                    "namespace": route["metadata"]["namespace"],
                    "host": route["spec"].get("host"),
                    "service": route["spec"]["to"]["name"],
                    "port": route["spec"]["port"].get("targetPort"),
                    "tls_termination": route["spec"].get("tls", {}).get("termination"),
                    "created_at": route["metadata"].get("creationTimestamp")
                }
                routes.append(route_info)
            
            return routes
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse route list: {str(e)}")
            return []


class OpenShiftBuildManager:
    """
    Manages OpenShift builds.
    
    This class provides methods for managing OpenShift builds,
    including build configs, builds, and image streams.
    """
    
    def __init__(self, executor: 'OpenShiftExecutor'):
        """
        Initialize the OpenShift Build Manager.
        
        Args:
            executor: OpenShift executor
        """
        self.executor = executor
    
    def create_build_config(self, name: str, 
                           namespace: str,
                           git_url: str,
                           git_ref: str,
                           context_dir: Optional[str] = None,
                           strategy: str = "Source",
                           builder_image: Optional[str] = None,
                           output_image_stream: Optional[str] = None) -> Dict[str, Any]:
        """
        Create an OpenShift build config.
        
        Args:
            name: Build config name
            namespace: Namespace
            git_url: Git repository URL
            git_ref: Git reference (branch, tag, commit)
            context_dir: Context directory (optional)
            strategy: Build strategy (default: Source)
            builder_image: Builder image (optional)
            output_image_stream: Output image stream (optional)
            
        Returns:
            Dict[str, Any]: Build config creation result
        """
        # Create build config manifest
        build_config = {
            "apiVersion": "build.openshift.io/v1",
            "kind": "BuildConfig",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "source": {
                    "git": {
                        "uri": git_url,
                        "ref": git_ref
                    },
                    "type": "Git"
                },
                "strategy": {
                    "type": strategy
                },
                "output": {}
            }
        }
        
        # Add context directory if provided
        if context_dir:
            build_config["spec"]["source"]["contextDir"] = context_dir
        
        # Add builder image if provided
        if builder_image:
            if strategy == "Source":
                build_config["spec"]["strategy"]["sourceStrategy"] = {
                    "from": {
                        "kind": "ImageStreamTag",
                        "name": builder_image
                    }
                }
            elif strategy == "Docker":
                build_config["spec"]["strategy"]["dockerStrategy"] = {
                    "from": {
                        "kind": "ImageStreamTag",
                        "name": builder_image
                    }
                }
        
        # Add output image stream if provided
        if output_image_stream:
            build_config["spec"]["output"]["to"] = {
                "kind": "ImageStreamTag",
                "name": output_image_stream
            }
        
        # Write build config to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(build_config, f)
            build_config_file = f.name
        
        try:
            # Apply build config
            output = self.executor.run_oc_command([
                "apply", "-f", build_config_file
            ])
            
            return {
                "name": name,
                "namespace": namespace,
                "git_url": git_url,
                "git_ref": git_ref,
                "context_dir": context_dir,
                "strategy": strategy,
                "builder_image": builder_image,
                "output_image_stream": output_image_stream,
                "output": output
            }
        
        finally:
            # Clean up temporary file
            if os.path.exists(build_config_file):
                os.unlink(build_config_file)
    
    def start_build(self, name: str, 
                   namespace: str,
                   follow: bool = False) -> Dict[str, Any]:
        """
        Start an OpenShift build.
        
        Args:
            name: Build config name
            namespace: Namespace
            follow: Whether to follow build logs (default: False)
            
        Returns:
            Dict[str, Any]: Build start result
        """
        # Build command
        cmd = ["start-build", name, "-n", namespace]
        
        # Add follow if requested
        if follow:
            cmd.append("--follow")
        
        # Start build
        output = self.executor.run_oc_command(cmd)
        
        return {
            "name": name,
            "namespace": namespace,
            "follow": follow,
            "output": output
        }
    
    def get_build_logs(self, name: str, namespace: str) -> str:
        """
        Get logs for an OpenShift build.
        
        Args:
            name: Build name
            namespace: Namespace
            
        Returns:
            str: Build logs
        """
        output = self.executor.run_oc_command([
            "logs", "build/" + name, "-n", namespace
        ])
        
        return output
    
    def list_builds(self, namespace: str) -> List[Dict[str, Any]]:
        """
        List OpenShift builds.
        
        Args:
            namespace: Namespace
            
        Returns:
            List[Dict[str, Any]]: List of builds
        """
        output = self.executor.run_oc_command([
            "get", "builds", "-n", namespace, "-o", "json"
        ])
        
        try:
            builds_json = json.loads(output)
            
            builds = []
            for build in builds_json.get("items", []):
                build_info = {
                    "name": build["metadata"]["name"],
                    "namespace": build["metadata"]["namespace"],
                    "build_config": build["metadata"].get("labels", {}).get("buildconfig"),
                    "status": build.get("status", {}).get("phase"),
                    "created_at": build["metadata"].get("creationTimestamp")
                }
                builds.append(build_info)
            
            return builds
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse build list: {str(e)}")
            return []


class OpenShiftDeploymentConfigManager:
    """
    Manages OpenShift deployment configs.
    
    This class provides methods for managing OpenShift deployment configs,
    including creation, modification, and listing.
    """
    
    def __init__(self, executor: 'OpenShiftExecutor'):
        """
        Initialize the OpenShift Deployment Config Manager.
        
        Args:
            executor: OpenShift executor
        """
        self.executor = executor
    
    def create_deployment_config(self, name: str, 
                               namespace: str,
                               image: str,
                               replicas: int = 1,
                               ports: Optional[List[Dict[str, Any]]] = None,
                               env_vars: Optional[Dict[str, str]] = None,
                               volumes: Optional[List[Dict[str, Any]]] = None,
                               volume_mounts: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Create an OpenShift deployment config.
        
        Args:
            name: Deployment config name
            namespace: Namespace
            image: Container image
            replicas: Number of replicas (default: 1)
            ports: Container ports (optional)
            env_vars: Environment variables (optional)
            volumes: Volumes (optional)
            volume_mounts: Volume mounts (optional)
            
        Returns:
            Dict[str, Any]: Deployment config creation result
        """
        # Create deployment config manifest
        deployment_config = {
            "apiVersion": "apps.openshift.io/v1",
            "kind": "DeploymentConfig",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "replicas": replicas,
                "selector": {
                    "app": name
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
                                "image": image
                            }
                        ]
                    }
                },
                "triggers": [
                    {
                        "type": "ConfigChange"
                    }
                ]
            }
        }
        
        # Add ports if provided
        if ports:
            deployment_config["spec"]["template"]["spec"]["containers"][0]["ports"] = ports
        
        # Add environment variables if provided
        if env_vars:
            env = []
            for key, value in env_vars.items():
                env.append({
                    "name": key,
                    "value": value
                })
            deployment_config["spec"]["template"]["spec"]["containers"][0]["env"] = env
        
        # Add volumes if provided
        if volumes:
            deployment_config["spec"]["template"]["spec"]["volumes"] = volumes
        
        # Add volume mounts if provided
        if volume_mounts:
            deployment_config["spec"]["template"]["spec"]["containers"][0]["volumeMounts"] = volume_mounts
        
        # Write deployment config to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(deployment_config, f)
            deployment_config_file = f.name
        
        try:
            # Apply deployment config
            output = self.executor.run_oc_command([
                "apply", "-f", deployment_config_file
            ])
            
            return {
                "name": name,
                "namespace": namespace,
                "image": image,
                "replicas": replicas,
                "ports": ports,
                "env_vars": env_vars,
                "volumes": volumes,
                "volume_mounts": volume_mounts,
                "output": output
            }
        
        finally:
            # Clean up temporary file
            if os.path.exists(deployment_config_file):
                os.unlink(deployment_config_file)
    
    def get_deployment_config(self, name: str, namespace: str) -> Dict[str, Any]:
        """
        Get an OpenShift deployment config.
        
        Args:
            name: Deployment config name
            namespace: Namespace
            
        Returns:
            Dict[str, Any]: Deployment config information
        """
        output = self.executor.run_oc_command([
            "get", "dc", name, "-n", namespace, "-o", "json"
        ])
        
        try:
            dc_json = json.loads(output)
            
            return {
                "name": dc_json["metadata"]["name"],
                "namespace": dc_json["metadata"]["namespace"],
                "replicas": dc_json["spec"].get("replicas"),
                "image": dc_json["spec"]["template"]["spec"]["containers"][0].get("image"),
                "created_at": dc_json["metadata"].get("creationTimestamp"),
                "status": dc_json.get("status", {})
            }
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse deployment config information: {str(e)}")
            return {
                "name": name,
                "namespace": namespace,
                "error": str(e),
                "output": output
            }
    
    def list_deployment_configs(self, namespace: str) -> List[Dict[str, Any]]:
        """
        List OpenShift deployment configs.
        
        Args:
            namespace: Namespace
            
        Returns:
            List[Dict[str, Any]]: List of deployment configs
        """
        output = self.executor.run_oc_command([
            "get", "dc", "-n", namespace, "-o", "json"
        ])
        
        try:
            dcs_json = json.loads(output)
            
            dcs = []
            for dc in dcs_json.get("items", []):
                dc_info = {
                    "name": dc["metadata"]["name"],
                    "namespace": dc["metadata"]["namespace"],
                    "replicas": dc["spec"].get("replicas"),
                    "image": dc["spec"]["template"]["spec"]["containers"][0].get("image"),
                    "created_at": dc["metadata"].get("creationTimestamp"),
                    "status": dc.get("status", {})
                }
                dcs.append(dc_info)
            
            return dcs
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse deployment config list: {str(e)}")
            return []


class OpenShiftExecutor:
    """
    Executes OpenShift CLI commands.
    
    This class provides methods for executing OpenShift CLI commands
    and handling their output.
    """
    
    def __init__(self, oc_binary: str, working_dir: str):
        """
        Initialize the OpenShift Executor.
        
        Args:
            oc_binary: Path to OpenShift CLI binary
            working_dir: Working directory for OpenShift operations
        """
        self.oc_binary = oc_binary
        self.working_dir = working_dir
    
    def run_oc_command(self, args: List[str], check: bool = True) -> str:
        """
        Run an OpenShift CLI command.
        
        Args:
            args: Command arguments
            check: Whether to check for command success
            
        Returns:
            str: Command output
            
        Raises:
            Exception: If the command fails and check is True
        """
        cmd = [self.oc_binary] + args
        logger.info(f"Running OpenShift command: {' '.join(cmd)}")
        
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
            error_message = f"OpenShift command failed: {e.stderr}"
            logger.error(error_message)
            
            if check:
                raise Exception(error_message)
            
            return e.stderr
