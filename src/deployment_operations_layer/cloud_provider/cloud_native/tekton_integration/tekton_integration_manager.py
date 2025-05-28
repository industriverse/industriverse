"""
Tekton Integration Manager

This module provides integration with Tekton for cloud-native CI/CD pipelines
in the Deployment Operations Layer. It handles pipeline management, task creation,
triggers, and event listeners.

Classes:
    TektonIntegrationManager: Manages Tekton integration
    TektonPipelineManager: Manages Tekton pipelines
    TektonTaskManager: Manages Tekton tasks
    TektonTriggerManager: Manages Tekton triggers
    TektonExecutor: Executes Tekton CLI commands
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

class TektonIntegrationManager:
    """
    Manages Tekton integration for the Deployment Operations Layer.
    
    This class provides a unified interface for interacting with Tekton,
    handling pipeline management, task creation, triggers, and event listeners.
    """
    
    def __init__(self, tkn_binary_path: Optional[str] = None, 
                kubectl_binary_path: Optional[str] = None,
                working_dir: Optional[str] = None):
        """
        Initialize the Tekton Integration Manager.
        
        Args:
            tkn_binary_path: Path to Tekton CLI binary (optional, defaults to 'tkn' in PATH)
            kubectl_binary_path: Path to kubectl binary (optional, defaults to 'kubectl' in PATH)
            working_dir: Working directory for Tekton operations (optional)
        """
        self.tkn_binary = tkn_binary_path or "tkn"
        self.kubectl_binary = kubectl_binary_path or "kubectl"
        self.working_dir = working_dir or tempfile.mkdtemp(prefix="tekton_")
        
        self.executor = TektonExecutor(self.tkn_binary, self.kubectl_binary, self.working_dir)
        self.pipeline_manager = TektonPipelineManager(self.executor)
        self.task_manager = TektonTaskManager(self.executor)
        self.trigger_manager = TektonTriggerManager(self.executor)
        
        # Verify Tekton installation
        self._verify_tekton_installation()
    
    def _verify_tekton_installation(self):
        """
        Verify that Tekton is installed and available.
        
        Logs a warning if Tekton is not installed but does not raise an exception
        as Tekton may be accessed via API or other means.
        """
        try:
            version = self.executor.run_tkn_command(["version"], check=False)
            logger.info(f"Tekton CLI version: {version}")
        except Exception as e:
            logger.warning(f"Tekton CLI not installed or not accessible: {str(e)}")
    
    def install_tekton(self, namespace: str = "tekton-pipelines") -> AgentResponse:
        """
        Install Tekton Pipelines on a Kubernetes cluster.
        
        Args:
            namespace: Namespace to install Tekton in (default: "tekton-pipelines")
            
        Returns:
            AgentResponse: Installation response
        """
        try:
            # Create namespace if it doesn't exist
            self.executor.run_kubectl_command([
                "create", "namespace", namespace, "--dry-run=client", "-o", "yaml"
            ], check=False)
            
            # Install Tekton Pipelines
            output = self.executor.run_kubectl_command([
                "apply", "-f", "https://storage.googleapis.com/tekton-releases/pipeline/latest/release.yaml"
            ])
            
            # Install Tekton Dashboard
            dashboard_output = self.executor.run_kubectl_command([
                "apply", "-f", "https://storage.googleapis.com/tekton-releases/dashboard/latest/tekton-dashboard-release.yaml"
            ], check=False)
            
            # Install Tekton Triggers
            triggers_output = self.executor.run_kubectl_command([
                "apply", "-f", "https://storage.googleapis.com/tekton-releases/triggers/latest/release.yaml"
            ], check=False)
            
            return AgentResponse(
                success=True,
                message="Tekton installed successfully",
                data={
                    "namespace": namespace,
                    "pipelines_output": output,
                    "dashboard_output": dashboard_output,
                    "triggers_output": triggers_output
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to install Tekton: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to install Tekton: {str(e)}",
                data={}
            )
    
    def create_pipeline(self, name: str, tasks: List[Dict[str, Any]], 
                       namespace: str = "default",
                       params: Optional[List[Dict[str, Any]]] = None,
                       workspaces: Optional[List[Dict[str, Any]]] = None) -> AgentResponse:
        """
        Create a Tekton Pipeline.
        
        Args:
            name: Pipeline name
            tasks: List of pipeline tasks
            namespace: Namespace (default: "default")
            params: Pipeline parameters (optional)
            workspaces: Pipeline workspaces (optional)
            
        Returns:
            AgentResponse: Pipeline creation response
        """
        try:
            result = self.pipeline_manager.create_pipeline(
                name=name,
                tasks=tasks,
                namespace=namespace,
                params=params,
                workspaces=workspaces
            )
            
            return AgentResponse(
                success=True,
                message=f"Tekton Pipeline {name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create Tekton Pipeline: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create Tekton Pipeline: {str(e)}",
                data={}
            )
    
    def create_task(self, name: str, steps: List[Dict[str, Any]], 
                   namespace: str = "default",
                   params: Optional[List[Dict[str, Any]]] = None,
                   workspaces: Optional[List[Dict[str, Any]]] = None,
                   results: Optional[List[Dict[str, Any]]] = None) -> AgentResponse:
        """
        Create a Tekton Task.
        
        Args:
            name: Task name
            steps: List of task steps
            namespace: Namespace (default: "default")
            params: Task parameters (optional)
            workspaces: Task workspaces (optional)
            results: Task results (optional)
            
        Returns:
            AgentResponse: Task creation response
        """
        try:
            result = self.task_manager.create_task(
                name=name,
                steps=steps,
                namespace=namespace,
                params=params,
                workspaces=workspaces,
                results=results
            )
            
            return AgentResponse(
                success=True,
                message=f"Tekton Task {name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create Tekton Task: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create Tekton Task: {str(e)}",
                data={}
            )
    
    def create_trigger_template(self, name: str, pipeline_name: str, 
                              namespace: str = "default",
                              params: Optional[List[Dict[str, Any]]] = None) -> AgentResponse:
        """
        Create a Tekton TriggerTemplate.
        
        Args:
            name: TriggerTemplate name
            pipeline_name: Pipeline name to trigger
            namespace: Namespace (default: "default")
            params: TriggerTemplate parameters (optional)
            
        Returns:
            AgentResponse: TriggerTemplate creation response
        """
        try:
            result = self.trigger_manager.create_trigger_template(
                name=name,
                pipeline_name=pipeline_name,
                namespace=namespace,
                params=params
            )
            
            return AgentResponse(
                success=True,
                message=f"Tekton TriggerTemplate {name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create Tekton TriggerTemplate: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create Tekton TriggerTemplate: {str(e)}",
                data={}
            )
    
    def create_trigger_binding(self, name: str, bindings: Dict[str, str], 
                             namespace: str = "default") -> AgentResponse:
        """
        Create a Tekton TriggerBinding.
        
        Args:
            name: TriggerBinding name
            bindings: Parameter bindings
            namespace: Namespace (default: "default")
            
        Returns:
            AgentResponse: TriggerBinding creation response
        """
        try:
            result = self.trigger_manager.create_trigger_binding(
                name=name,
                bindings=bindings,
                namespace=namespace
            )
            
            return AgentResponse(
                success=True,
                message=f"Tekton TriggerBinding {name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create Tekton TriggerBinding: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create Tekton TriggerBinding: {str(e)}",
                data={}
            )
    
    def create_event_listener(self, name: str, trigger_template: str, 
                            trigger_binding: str, 
                            namespace: str = "default",
                            service_account: str = "default") -> AgentResponse:
        """
        Create a Tekton EventListener.
        
        Args:
            name: EventListener name
            trigger_template: TriggerTemplate name
            trigger_binding: TriggerBinding name
            namespace: Namespace (default: "default")
            service_account: Service account (default: "default")
            
        Returns:
            AgentResponse: EventListener creation response
        """
        try:
            result = self.trigger_manager.create_event_listener(
                name=name,
                trigger_template=trigger_template,
                trigger_binding=trigger_binding,
                namespace=namespace,
                service_account=service_account
            )
            
            return AgentResponse(
                success=True,
                message=f"Tekton EventListener {name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create Tekton EventListener: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create Tekton EventListener: {str(e)}",
                data={}
            )
    
    def run_pipeline(self, name: str, namespace: str = "default",
                    params: Optional[Dict[str, str]] = None,
                    workspaces: Optional[List[Dict[str, Any]]] = None) -> AgentResponse:
        """
        Run a Tekton Pipeline.
        
        Args:
            name: Pipeline name
            namespace: Namespace (default: "default")
            params: Pipeline parameters (optional)
            workspaces: Pipeline workspaces (optional)
            
        Returns:
            AgentResponse: Pipeline run response
        """
        try:
            result = self.pipeline_manager.run_pipeline(
                name=name,
                namespace=namespace,
                params=params,
                workspaces=workspaces
            )
            
            return AgentResponse(
                success=True,
                message=f"Tekton Pipeline {name} started successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to run Tekton Pipeline: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to run Tekton Pipeline: {str(e)}",
                data={}
            )
    
    def get_pipeline_run_status(self, name: str, 
                              namespace: str = "default") -> AgentResponse:
        """
        Get the status of a Tekton PipelineRun.
        
        Args:
            name: PipelineRun name
            namespace: Namespace (default: "default")
            
        Returns:
            AgentResponse: PipelineRun status response
        """
        try:
            result = self.pipeline_manager.get_pipeline_run_status(
                name=name,
                namespace=namespace
            )
            
            return AgentResponse(
                success=True,
                message=f"Retrieved status for Tekton PipelineRun {name}",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to get Tekton PipelineRun status: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to get Tekton PipelineRun status: {str(e)}",
                data={}
            )
    
    def list_pipelines(self, namespace: str = "default") -> AgentResponse:
        """
        List Tekton Pipelines.
        
        Args:
            namespace: Namespace (default: "default")
            
        Returns:
            AgentResponse: Pipeline list response
        """
        try:
            result = self.pipeline_manager.list_pipelines(namespace)
            
            return AgentResponse(
                success=True,
                message=f"Found {len(result)} Tekton Pipelines in namespace {namespace}",
                data={
                    "pipelines": result
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to list Tekton Pipelines: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to list Tekton Pipelines: {str(e)}",
                data={}
            )
    
    def list_tasks(self, namespace: str = "default") -> AgentResponse:
        """
        List Tekton Tasks.
        
        Args:
            namespace: Namespace (default: "default")
            
        Returns:
            AgentResponse: Task list response
        """
        try:
            result = self.task_manager.list_tasks(namespace)
            
            return AgentResponse(
                success=True,
                message=f"Found {len(result)} Tekton Tasks in namespace {namespace}",
                data={
                    "tasks": result
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to list Tekton Tasks: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to list Tekton Tasks: {str(e)}",
                data={}
            )
    
    def delete_pipeline(self, name: str, namespace: str = "default") -> AgentResponse:
        """
        Delete a Tekton Pipeline.
        
        Args:
            name: Pipeline name
            namespace: Namespace (default: "default")
            
        Returns:
            AgentResponse: Deletion response
        """
        try:
            result = self.pipeline_manager.delete_pipeline(
                name=name,
                namespace=namespace
            )
            
            return AgentResponse(
                success=True,
                message=f"Tekton Pipeline {name} deleted successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to delete Tekton Pipeline: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to delete Tekton Pipeline: {str(e)}",
                data={}
            )
    
    def delete_task(self, name: str, namespace: str = "default") -> AgentResponse:
        """
        Delete a Tekton Task.
        
        Args:
            name: Task name
            namespace: Namespace (default: "default")
            
        Returns:
            AgentResponse: Deletion response
        """
        try:
            result = self.task_manager.delete_task(
                name=name,
                namespace=namespace
            )
            
            return AgentResponse(
                success=True,
                message=f"Tekton Task {name} deleted successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to delete Tekton Task: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to delete Tekton Task: {str(e)}",
                data={}
            )
    
    def to_mcp_context(self) -> MCPContext:
        """
        Convert Tekton integration information to MCP context.
        
        Returns:
            MCPContext: MCP context with Tekton integration information
        """
        return MCPContext(
            context_type="tekton_integration",
            tekton_version=self._get_tekton_version(),
            working_dir=self.working_dir
        )
    
    def _get_tekton_version(self) -> str:
        """
        Get the Tekton version.
        
        Returns:
            str: Tekton version
        """
        try:
            version_output = self.executor.run_tkn_command(["version"], check=False)
            return version_output.strip()
        except Exception as e:
            logger.error(f"Failed to get Tekton version: {str(e)}")
            return "unknown"


class TektonPipelineManager:
    """
    Manages Tekton pipelines.
    
    This class provides methods for managing Tekton Pipeline resources,
    including creation, deletion, and execution.
    """
    
    def __init__(self, executor: 'TektonExecutor'):
        """
        Initialize the Tekton Pipeline Manager.
        
        Args:
            executor: Tekton executor
        """
        self.executor = executor
    
    def create_pipeline(self, name: str, tasks: List[Dict[str, Any]], 
                       namespace: str = "default",
                       params: Optional[List[Dict[str, Any]]] = None,
                       workspaces: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Create a Tekton Pipeline.
        
        Args:
            name: Pipeline name
            tasks: List of pipeline tasks
            namespace: Namespace (default: "default")
            params: Pipeline parameters (optional)
            workspaces: Pipeline workspaces (optional)
            
        Returns:
            Dict[str, Any]: Pipeline creation result
        """
        pipeline = {
            "apiVersion": "tekton.dev/v1beta1",
            "kind": "Pipeline",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "tasks": tasks
            }
        }
        
        if params:
            pipeline["spec"]["params"] = params
        
        if workspaces:
            pipeline["spec"]["workspaces"] = workspaces
        
        # Write pipeline to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(pipeline, f)
            pipeline_file = f.name
        
        try:
            # Apply pipeline
            output = self.executor.run_kubectl_command([
                "apply", "-f", pipeline_file
            ])
            
            return {
                "name": name,
                "namespace": namespace,
                "tasks": tasks,
                "params": params,
                "workspaces": workspaces,
                "output": output
            }
        
        finally:
            # Clean up temporary file
            if os.path.exists(pipeline_file):
                os.unlink(pipeline_file)
    
    def run_pipeline(self, name: str, namespace: str = "default",
                    params: Optional[Dict[str, str]] = None,
                    workspaces: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Run a Tekton Pipeline.
        
        Args:
            name: Pipeline name
            namespace: Namespace (default: "default")
            params: Pipeline parameters (optional)
            workspaces: Pipeline workspaces (optional)
            
        Returns:
            Dict[str, Any]: Pipeline run result
        """
        args = ["pipeline", "start", name, "-n", namespace]
        
        # Add parameters
        if params:
            for param_name, param_value in params.items():
                args.extend(["-p", f"{param_name}={param_value}"])
        
        # Add workspaces
        if workspaces:
            for workspace in workspaces:
                workspace_name = workspace.get("name")
                workspace_type = workspace.get("type", "pvc")
                workspace_value = workspace.get("value")
                
                if workspace_name and workspace_value:
                    args.extend(["-w", f"name={workspace_name},{workspace_type}={workspace_value}"])
        
        # Run pipeline
        output = self.executor.run_tkn_command(args)
        
        # Extract PipelineRun name from output
        pipeline_run_name = None
        if "PipelineRun started:" in output:
            pipeline_run_line = [line for line in output.split("\n") if "PipelineRun started:" in line][0]
            pipeline_run_name = pipeline_run_line.split("PipelineRun started:")[1].strip()
        
        return {
            "pipeline_name": name,
            "namespace": namespace,
            "params": params,
            "workspaces": workspaces,
            "pipeline_run_name": pipeline_run_name,
            "output": output
        }
    
    def get_pipeline_run_status(self, name: str, 
                              namespace: str = "default") -> Dict[str, Any]:
        """
        Get the status of a Tekton PipelineRun.
        
        Args:
            name: PipelineRun name
            namespace: Namespace (default: "default")
            
        Returns:
            Dict[str, Any]: PipelineRun status
        """
        output = self.executor.run_kubectl_command([
            "get", "pipelinerun", name, "-n", namespace, "-o", "json"
        ])
        
        try:
            pipeline_run_json = json.loads(output)
            
            return {
                "name": pipeline_run_json["metadata"]["name"],
                "namespace": pipeline_run_json["metadata"]["namespace"],
                "pipeline_name": pipeline_run_json["spec"]["pipelineRef"]["name"],
                "status": pipeline_run_json["status"]["conditions"][0]["reason"],
                "message": pipeline_run_json["status"]["conditions"][0]["message"],
                "start_time": pipeline_run_json["status"].get("startTime"),
                "completion_time": pipeline_run_json["status"].get("completionTime"),
                "task_runs": pipeline_run_json["status"].get("taskRuns", {})
            }
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse PipelineRun status: {str(e)}")
            return {"name": name, "namespace": namespace, "output": output, "error": str(e)}
    
    def list_pipelines(self, namespace: str = "default") -> List[Dict[str, Any]]:
        """
        List Tekton Pipelines.
        
        Args:
            namespace: Namespace (default: "default")
            
        Returns:
            List[Dict[str, Any]]: List of pipelines
        """
        output = self.executor.run_kubectl_command([
            "get", "pipeline", "-n", namespace, "-o", "json"
        ])
        
        try:
            pipelines_json = json.loads(output)
            
            pipelines = []
            for pipeline in pipelines_json.get("items", []):
                pipeline_info = {
                    "name": pipeline["metadata"]["name"],
                    "namespace": pipeline["metadata"]["namespace"],
                    "tasks": pipeline["spec"].get("tasks", []),
                    "params": pipeline["spec"].get("params", []),
                    "workspaces": pipeline["spec"].get("workspaces", [])
                }
                pipelines.append(pipeline_info)
            
            return pipelines
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse pipeline list: {str(e)}")
            return []
    
    def delete_pipeline(self, name: str, namespace: str = "default") -> Dict[str, Any]:
        """
        Delete a Tekton Pipeline.
        
        Args:
            name: Pipeline name
            namespace: Namespace (default: "default")
            
        Returns:
            Dict[str, Any]: Deletion result
        """
        output = self.executor.run_kubectl_command([
            "delete", "pipeline", name, "-n", namespace
        ])
        
        return {
            "name": name,
            "namespace": namespace,
            "output": output
        }


class TektonTaskManager:
    """
    Manages Tekton tasks.
    
    This class provides methods for managing Tekton Task resources,
    including creation, deletion, and listing.
    """
    
    def __init__(self, executor: 'TektonExecutor'):
        """
        Initialize the Tekton Task Manager.
        
        Args:
            executor: Tekton executor
        """
        self.executor = executor
    
    def create_task(self, name: str, steps: List[Dict[str, Any]], 
                   namespace: str = "default",
                   params: Optional[List[Dict[str, Any]]] = None,
                   workspaces: Optional[List[Dict[str, Any]]] = None,
                   results: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Create a Tekton Task.
        
        Args:
            name: Task name
            steps: List of task steps
            namespace: Namespace (default: "default")
            params: Task parameters (optional)
            workspaces: Task workspaces (optional)
            results: Task results (optional)
            
        Returns:
            Dict[str, Any]: Task creation result
        """
        task = {
            "apiVersion": "tekton.dev/v1beta1",
            "kind": "Task",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "steps": steps
            }
        }
        
        if params:
            task["spec"]["params"] = params
        
        if workspaces:
            task["spec"]["workspaces"] = workspaces
        
        if results:
            task["spec"]["results"] = results
        
        # Write task to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(task, f)
            task_file = f.name
        
        try:
            # Apply task
            output = self.executor.run_kubectl_command([
                "apply", "-f", task_file
            ])
            
            return {
                "name": name,
                "namespace": namespace,
                "steps": steps,
                "params": params,
                "workspaces": workspaces,
                "results": results,
                "output": output
            }
        
        finally:
            # Clean up temporary file
            if os.path.exists(task_file):
                os.unlink(task_file)
    
    def list_tasks(self, namespace: str = "default") -> List[Dict[str, Any]]:
        """
        List Tekton Tasks.
        
        Args:
            namespace: Namespace (default: "default")
            
        Returns:
            List[Dict[str, Any]]: List of tasks
        """
        output = self.executor.run_kubectl_command([
            "get", "task", "-n", namespace, "-o", "json"
        ])
        
        try:
            tasks_json = json.loads(output)
            
            tasks = []
            for task in tasks_json.get("items", []):
                task_info = {
                    "name": task["metadata"]["name"],
                    "namespace": task["metadata"]["namespace"],
                    "steps": task["spec"].get("steps", []),
                    "params": task["spec"].get("params", []),
                    "workspaces": task["spec"].get("workspaces", []),
                    "results": task["spec"].get("results", [])
                }
                tasks.append(task_info)
            
            return tasks
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse task list: {str(e)}")
            return []
    
    def delete_task(self, name: str, namespace: str = "default") -> Dict[str, Any]:
        """
        Delete a Tekton Task.
        
        Args:
            name: Task name
            namespace: Namespace (default: "default")
            
        Returns:
            Dict[str, Any]: Deletion result
        """
        output = self.executor.run_kubectl_command([
            "delete", "task", name, "-n", namespace
        ])
        
        return {
            "name": name,
            "namespace": namespace,
            "output": output
        }


class TektonTriggerManager:
    """
    Manages Tekton triggers.
    
    This class provides methods for managing Tekton Trigger resources,
    including TriggerTemplates, TriggerBindings, and EventListeners.
    """
    
    def __init__(self, executor: 'TektonExecutor'):
        """
        Initialize the Tekton Trigger Manager.
        
        Args:
            executor: Tekton executor
        """
        self.executor = executor
    
    def create_trigger_template(self, name: str, pipeline_name: str, 
                              namespace: str = "default",
                              params: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Create a Tekton TriggerTemplate.
        
        Args:
            name: TriggerTemplate name
            pipeline_name: Pipeline name to trigger
            namespace: Namespace (default: "default")
            params: TriggerTemplate parameters (optional)
            
        Returns:
            Dict[str, Any]: TriggerTemplate creation result
        """
        # Create PipelineRun resource template
        pipeline_run = {
            "apiVersion": "tekton.dev/v1beta1",
            "kind": "PipelineRun",
            "metadata": {
                "generateName": f"{pipeline_name}-run-"
            },
            "spec": {
                "pipelineRef": {
                    "name": pipeline_name
                }
            }
        }
        
        # Add parameters to PipelineRun if provided
        if params:
            pipeline_run_params = []
            for param in params:
                pipeline_run_params.append({
                    "name": param["name"],
                    "value": f"$(tt.params.{param['name']})"
                })
            pipeline_run["spec"]["params"] = pipeline_run_params
        
        # Create TriggerTemplate
        trigger_template = {
            "apiVersion": "triggers.tekton.dev/v1alpha1",
            "kind": "TriggerTemplate",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "params": params or [],
                "resourcetemplates": [pipeline_run]
            }
        }
        
        # Write TriggerTemplate to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(trigger_template, f)
            template_file = f.name
        
        try:
            # Apply TriggerTemplate
            output = self.executor.run_kubectl_command([
                "apply", "-f", template_file
            ])
            
            return {
                "name": name,
                "namespace": namespace,
                "pipeline_name": pipeline_name,
                "params": params,
                "output": output
            }
        
        finally:
            # Clean up temporary file
            if os.path.exists(template_file):
                os.unlink(template_file)
    
    def create_trigger_binding(self, name: str, bindings: Dict[str, str], 
                             namespace: str = "default") -> Dict[str, Any]:
        """
        Create a Tekton TriggerBinding.
        
        Args:
            name: TriggerBinding name
            bindings: Parameter bindings
            namespace: Namespace (default: "default")
            
        Returns:
            Dict[str, Any]: TriggerBinding creation result
        """
        # Convert bindings to list format
        binding_list = []
        for param_name, json_path in bindings.items():
            binding_list.append({
                "name": param_name,
                "value": json_path
            })
        
        # Create TriggerBinding
        trigger_binding = {
            "apiVersion": "triggers.tekton.dev/v1alpha1",
            "kind": "TriggerBinding",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "params": binding_list
            }
        }
        
        # Write TriggerBinding to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(trigger_binding, f)
            binding_file = f.name
        
        try:
            # Apply TriggerBinding
            output = self.executor.run_kubectl_command([
                "apply", "-f", binding_file
            ])
            
            return {
                "name": name,
                "namespace": namespace,
                "bindings": bindings,
                "output": output
            }
        
        finally:
            # Clean up temporary file
            if os.path.exists(binding_file):
                os.unlink(binding_file)
    
    def create_event_listener(self, name: str, trigger_template: str, 
                            trigger_binding: str, 
                            namespace: str = "default",
                            service_account: str = "default") -> Dict[str, Any]:
        """
        Create a Tekton EventListener.
        
        Args:
            name: EventListener name
            trigger_template: TriggerTemplate name
            trigger_binding: TriggerBinding name
            namespace: Namespace (default: "default")
            service_account: Service account (default: "default")
            
        Returns:
            Dict[str, Any]: EventListener creation result
        """
        # Create EventListener
        event_listener = {
            "apiVersion": "triggers.tekton.dev/v1alpha1",
            "kind": "EventListener",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "serviceAccountName": service_account,
                "triggers": [
                    {
                        "name": f"{name}-trigger",
                        "bindings": [
                            {
                                "ref": trigger_binding
                            }
                        ],
                        "template": {
                            "ref": trigger_template
                        }
                    }
                ]
            }
        }
        
        # Write EventListener to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(event_listener, f)
            listener_file = f.name
        
        try:
            # Apply EventListener
            output = self.executor.run_kubectl_command([
                "apply", "-f", listener_file
            ])
            
            return {
                "name": name,
                "namespace": namespace,
                "trigger_template": trigger_template,
                "trigger_binding": trigger_binding,
                "service_account": service_account,
                "output": output
            }
        
        finally:
            # Clean up temporary file
            if os.path.exists(listener_file):
                os.unlink(listener_file)


class TektonExecutor:
    """
    Executes Tekton CLI commands.
    
    This class provides methods for executing Tekton CLI and kubectl commands
    and handling their output.
    """
    
    def __init__(self, tkn_binary: str, kubectl_binary: str, working_dir: str):
        """
        Initialize the Tekton Executor.
        
        Args:
            tkn_binary: Path to Tekton CLI binary
            kubectl_binary: Path to kubectl binary
            working_dir: Working directory for Tekton operations
        """
        self.tkn_binary = tkn_binary
        self.kubectl_binary = kubectl_binary
        self.working_dir = working_dir
    
    def run_tkn_command(self, args: List[str], check: bool = True) -> str:
        """
        Run a Tekton CLI command.
        
        Args:
            args: Command arguments
            check: Whether to check for command success
            
        Returns:
            str: Command output
            
        Raises:
            Exception: If the command fails and check is True
        """
        cmd = [self.tkn_binary] + args
        logger.info(f"Running Tekton command: {' '.join(cmd)}")
        
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
            error_message = f"Tekton command failed: {e.stderr}"
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
