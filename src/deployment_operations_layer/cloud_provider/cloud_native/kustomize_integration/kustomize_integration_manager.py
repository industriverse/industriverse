"""
Kustomize Integration Manager

This module provides integration with Kustomize for the Deployment Operations Layer.
It handles Kustomize overlay management, building, and application.

Classes:
    KustomizeIntegrationManager: Manages Kustomize integration
    KustomizeOverlayManager: Manages Kustomize overlays
    KustomizeExecutor: Executes Kustomize CLI commands
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

class KustomizeIntegrationManager:
    """
    Manages Kustomize integration for the Deployment Operations Layer.
    
    This class provides a unified interface for interacting with Kustomize,
    handling overlay management, building, and application.
    """
    
    def __init__(self, kustomize_binary_path: Optional[str] = None, 
                kubectl_binary_path: Optional[str] = None,
                working_dir: Optional[str] = None):
        """
        Initialize the Kustomize Integration Manager.
        
        Args:
            kustomize_binary_path: Path to kustomize binary (optional, defaults to 'kustomize' in PATH)
            kubectl_binary_path: Path to kubectl binary (optional, defaults to 'kubectl' in PATH)
            working_dir: Working directory for Kustomize operations (optional)
        """
        self.kustomize_binary = kustomize_binary_path or "kustomize"
        self.kubectl_binary = kubectl_binary_path or "kubectl"
        self.working_dir = working_dir or tempfile.mkdtemp(prefix="kustomize_")
        
        self.executor = KustomizeExecutor(self.kustomize_binary, self.kubectl_binary, self.working_dir)
        self.overlay_manager = KustomizeOverlayManager(self.executor)
        
        # Verify Kustomize installation
        self._verify_kustomize_installation()
    
    def _verify_kustomize_installation(self):
        """
        Verify that Kustomize is installed and available.
        
        Logs a warning if Kustomize is not installed but does not raise an exception
        as Kustomize may be accessed via kubectl or other means.
        """
        try:
            version = self.executor.run_kustomize_command(["version"], check=False)
            logger.info(f"Kustomize client version: {version}")
        except Exception as e:
            logger.warning(f"Kustomize client not installed or not accessible: {str(e)}")
            
            # Try kubectl kustomize
            try:
                version = self.executor.run_kubectl_command(["kustomize", "--version"], check=False)
                logger.info(f"Kubectl kustomize version: {version}")
            except Exception as e:
                logger.warning(f"Kubectl kustomize not accessible: {str(e)}")
    
    def create_kustomization(self, path: str, 
                            resources: List[str],
                            namespace: Optional[str] = None,
                            common_labels: Optional[Dict[str, str]] = None,
                            common_annotations: Optional[Dict[str, str]] = None,
                            patches: Optional[List[Dict[str, Any]]] = None) -> AgentResponse:
        """
        Create a Kustomization file.
        
        Args:
            path: Path to create Kustomization file
            resources: List of resources to include
            namespace: Namespace to set (optional)
            common_labels: Common labels to add (optional)
            common_annotations: Common annotations to add (optional)
            patches: List of patches to apply (optional)
            
        Returns:
            AgentResponse: Kustomization creation response
        """
        try:
            result = self.overlay_manager.create_kustomization(
                path=path,
                resources=resources,
                namespace=namespace,
                common_labels=common_labels,
                common_annotations=common_annotations,
                patches=patches
            )
            
            return AgentResponse(
                success=True,
                message=f"Kustomization created at {path}",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create Kustomization: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create Kustomization: {str(e)}",
                data={}
            )
    
    def build(self, path: str) -> AgentResponse:
        """
        Build Kustomization.
        
        Args:
            path: Path to Kustomization directory
            
        Returns:
            AgentResponse: Build response
        """
        try:
            output = self.executor.run_kustomize_command(["build", path])
            
            return AgentResponse(
                success=True,
                message=f"Kustomization built successfully",
                data={"path": path, "output": output}
            )
        
        except Exception as e:
            logger.error(f"Failed to build Kustomization: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to build Kustomization: {str(e)}",
                data={}
            )
    
    def apply(self, path: str, wait: bool = False, 
             prune: bool = False,
             timeout: Optional[str] = None) -> AgentResponse:
        """
        Apply Kustomization.
        
        Args:
            path: Path to Kustomization directory
            wait: Whether to wait for resources to be ready (default: False)
            prune: Whether to prune resources (default: False)
            timeout: Timeout for wait (optional)
            
        Returns:
            AgentResponse: Apply response
        """
        try:
            # Build Kustomization
            build_output = self.executor.run_kustomize_command(["build", path])
            
            # Write build output to temporary file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
                f.write(build_output)
                build_file = f.name
            
            try:
                # Apply build output
                args = ["apply", "-f", build_file]
                
                # Add wait if requested
                if wait:
                    args.append("--wait")
                    
                    # Add timeout if provided
                    if timeout:
                        args.extend(["--timeout", timeout])
                
                # Add prune if requested
                if prune:
                    args.append("--prune")
                
                output = self.executor.run_kubectl_command(args)
                
                return AgentResponse(
                    success=True,
                    message=f"Kustomization applied successfully",
                    data={"path": path, "output": output}
                )
            
            finally:
                # Clean up temporary file
                if os.path.exists(build_file):
                    os.unlink(build_file)
        
        except Exception as e:
            logger.error(f"Failed to apply Kustomization: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to apply Kustomization: {str(e)}",
                data={}
            )
    
    def create_overlay(self, base_path: str, overlay_name: str, 
                      patches: Optional[List[Dict[str, Any]]] = None,
                      resources: Optional[List[str]] = None,
                      namespace: Optional[str] = None,
                      common_labels: Optional[Dict[str, str]] = None,
                      common_annotations: Optional[Dict[str, str]] = None) -> AgentResponse:
        """
        Create a Kustomize overlay.
        
        Args:
            base_path: Path to base Kustomization
            overlay_name: Name of overlay
            patches: List of patches to apply (optional)
            resources: Additional resources to include (optional)
            namespace: Namespace to set (optional)
            common_labels: Common labels to add (optional)
            common_annotations: Common annotations to add (optional)
            
        Returns:
            AgentResponse: Overlay creation response
        """
        try:
            result = self.overlay_manager.create_overlay(
                base_path=base_path,
                overlay_name=overlay_name,
                patches=patches,
                resources=resources,
                namespace=namespace,
                common_labels=common_labels,
                common_annotations=common_annotations
            )
            
            return AgentResponse(
                success=True,
                message=f"Kustomize overlay {overlay_name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create Kustomize overlay: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create Kustomize overlay: {str(e)}",
                data={}
            )
    
    def add_resource(self, path: str, resource: str) -> AgentResponse:
        """
        Add a resource to a Kustomization.
        
        Args:
            path: Path to Kustomization directory
            resource: Resource to add
            
        Returns:
            AgentResponse: Resource addition response
        """
        try:
            result = self.overlay_manager.add_resource(
                path=path,
                resource=resource
            )
            
            return AgentResponse(
                success=True,
                message=f"Resource {resource} added to Kustomization",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to add resource: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to add resource: {str(e)}",
                data={}
            )
    
    def add_patch(self, path: str, patch: Dict[str, Any]) -> AgentResponse:
        """
        Add a patch to a Kustomization.
        
        Args:
            path: Path to Kustomization directory
            patch: Patch to add
            
        Returns:
            AgentResponse: Patch addition response
        """
        try:
            result = self.overlay_manager.add_patch(
                path=path,
                patch=patch
            )
            
            return AgentResponse(
                success=True,
                message=f"Patch added to Kustomization",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to add patch: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to add patch: {str(e)}",
                data={}
            )
    
    def set_namespace(self, path: str, namespace: str) -> AgentResponse:
        """
        Set namespace in a Kustomization.
        
        Args:
            path: Path to Kustomization directory
            namespace: Namespace to set
            
        Returns:
            AgentResponse: Namespace setting response
        """
        try:
            result = self.overlay_manager.set_namespace(
                path=path,
                namespace=namespace
            )
            
            return AgentResponse(
                success=True,
                message=f"Namespace set to {namespace} in Kustomization",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to set namespace: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to set namespace: {str(e)}",
                data={}
            )
    
    def add_common_labels(self, path: str, labels: Dict[str, str]) -> AgentResponse:
        """
        Add common labels to a Kustomization.
        
        Args:
            path: Path to Kustomization directory
            labels: Labels to add
            
        Returns:
            AgentResponse: Labels addition response
        """
        try:
            result = self.overlay_manager.add_common_labels(
                path=path,
                labels=labels
            )
            
            return AgentResponse(
                success=True,
                message=f"Common labels added to Kustomization",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to add common labels: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to add common labels: {str(e)}",
                data={}
            )
    
    def add_common_annotations(self, path: str, annotations: Dict[str, str]) -> AgentResponse:
        """
        Add common annotations to a Kustomization.
        
        Args:
            path: Path to Kustomization directory
            annotations: Annotations to add
            
        Returns:
            AgentResponse: Annotations addition response
        """
        try:
            result = self.overlay_manager.add_common_annotations(
                path=path,
                annotations=annotations
            )
            
            return AgentResponse(
                success=True,
                message=f"Common annotations added to Kustomization",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to add common annotations: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to add common annotations: {str(e)}",
                data={}
            )
    
    def to_mcp_context(self) -> MCPContext:
        """
        Convert Kustomize integration information to MCP context.
        
        Returns:
            MCPContext: MCP context with Kustomize integration information
        """
        return MCPContext(
            context_type="kustomize_integration",
            kustomize_version=self._get_kustomize_version(),
            working_dir=self.working_dir
        )
    
    def _get_kustomize_version(self) -> str:
        """
        Get the Kustomize version.
        
        Returns:
            str: Kustomize version
        """
        try:
            version_output = self.executor.run_kustomize_command(["version"], check=False)
            return version_output.strip()
        except Exception as e:
            logger.error(f"Failed to get Kustomize version: {str(e)}")
            
            # Try kubectl kustomize
            try:
                version_output = self.executor.run_kubectl_command(["kustomize", "--version"], check=False)
                return version_output.strip()
            except Exception as e:
                logger.error(f"Failed to get kubectl kustomize version: {str(e)}")
                return "unknown"


class KustomizeOverlayManager:
    """
    Manages Kustomize overlays.
    
    This class provides methods for managing Kustomize overlays,
    including creation, modification, and resource management.
    """
    
    def __init__(self, executor: 'KustomizeExecutor'):
        """
        Initialize the Kustomize Overlay Manager.
        
        Args:
            executor: Kustomize executor
        """
        self.executor = executor
    
    def create_kustomization(self, path: str, 
                            resources: List[str],
                            namespace: Optional[str] = None,
                            common_labels: Optional[Dict[str, str]] = None,
                            common_annotations: Optional[Dict[str, str]] = None,
                            patches: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Create a Kustomization file.
        
        Args:
            path: Path to create Kustomization file
            resources: List of resources to include
            namespace: Namespace to set (optional)
            common_labels: Common labels to add (optional)
            common_annotations: Common annotations to add (optional)
            patches: List of patches to apply (optional)
            
        Returns:
            Dict[str, Any]: Kustomization creation result
        """
        # Create directory if it doesn't exist
        os.makedirs(path, exist_ok=True)
        
        # Create Kustomization file
        kustomization = {
            "apiVersion": "kustomize.config.k8s.io/v1beta1",
            "kind": "Kustomization",
            "resources": resources
        }
        
        # Add namespace if provided
        if namespace:
            kustomization["namespace"] = namespace
        
        # Add common labels if provided
        if common_labels:
            kustomization["commonLabels"] = common_labels
        
        # Add common annotations if provided
        if common_annotations:
            kustomization["commonAnnotations"] = common_annotations
        
        # Add patches if provided
        if patches:
            kustomization["patches"] = patches
        
        # Write Kustomization file
        kustomization_path = os.path.join(path, "kustomization.yaml")
        with open(kustomization_path, "w") as f:
            yaml.dump(kustomization, f)
        
        return {
            "path": path,
            "kustomization_path": kustomization_path,
            "resources": resources,
            "namespace": namespace,
            "common_labels": common_labels,
            "common_annotations": common_annotations,
            "patches": patches
        }
    
    def create_overlay(self, base_path: str, overlay_name: str, 
                      patches: Optional[List[Dict[str, Any]]] = None,
                      resources: Optional[List[str]] = None,
                      namespace: Optional[str] = None,
                      common_labels: Optional[Dict[str, str]] = None,
                      common_annotations: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Create a Kustomize overlay.
        
        Args:
            base_path: Path to base Kustomization
            overlay_name: Name of overlay
            patches: List of patches to apply (optional)
            resources: Additional resources to include (optional)
            namespace: Namespace to set (optional)
            common_labels: Common labels to add (optional)
            common_annotations: Common annotations to add (optional)
            
        Returns:
            Dict[str, Any]: Overlay creation result
        """
        # Create overlay directory
        overlay_path = os.path.join(os.path.dirname(base_path), overlay_name)
        os.makedirs(overlay_path, exist_ok=True)
        
        # Create Kustomization file
        kustomization = {
            "apiVersion": "kustomize.config.k8s.io/v1beta1",
            "kind": "Kustomization",
            "resources": ["../base"]
        }
        
        # Add additional resources if provided
        if resources:
            kustomization["resources"].extend(resources)
        
        # Add namespace if provided
        if namespace:
            kustomization["namespace"] = namespace
        
        # Add common labels if provided
        if common_labels:
            kustomization["commonLabels"] = common_labels
        
        # Add common annotations if provided
        if common_annotations:
            kustomization["commonAnnotations"] = common_annotations
        
        # Add patches if provided
        if patches:
            kustomization["patches"] = patches
        
        # Write Kustomization file
        kustomization_path = os.path.join(overlay_path, "kustomization.yaml")
        with open(kustomization_path, "w") as f:
            yaml.dump(kustomization, f)
        
        return {
            "base_path": base_path,
            "overlay_name": overlay_name,
            "overlay_path": overlay_path,
            "kustomization_path": kustomization_path,
            "resources": resources,
            "namespace": namespace,
            "common_labels": common_labels,
            "common_annotations": common_annotations,
            "patches": patches
        }
    
    def add_resource(self, path: str, resource: str) -> Dict[str, Any]:
        """
        Add a resource to a Kustomization.
        
        Args:
            path: Path to Kustomization directory
            resource: Resource to add
            
        Returns:
            Dict[str, Any]: Resource addition result
        """
        # Read Kustomization file
        kustomization_path = os.path.join(path, "kustomization.yaml")
        with open(kustomization_path, "r") as f:
            kustomization = yaml.safe_load(f)
        
        # Add resource if not already present
        if "resources" not in kustomization:
            kustomization["resources"] = []
        
        if resource not in kustomization["resources"]:
            kustomization["resources"].append(resource)
        
        # Write Kustomization file
        with open(kustomization_path, "w") as f:
            yaml.dump(kustomization, f)
        
        return {
            "path": path,
            "kustomization_path": kustomization_path,
            "resource": resource,
            "resources": kustomization["resources"]
        }
    
    def add_patch(self, path: str, patch: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a patch to a Kustomization.
        
        Args:
            path: Path to Kustomization directory
            patch: Patch to add
            
        Returns:
            Dict[str, Any]: Patch addition result
        """
        # Read Kustomization file
        kustomization_path = os.path.join(path, "kustomization.yaml")
        with open(kustomization_path, "r") as f:
            kustomization = yaml.safe_load(f)
        
        # Add patch
        if "patches" not in kustomization:
            kustomization["patches"] = []
        
        # Check if patch already exists
        patch_exists = False
        for existing_patch in kustomization["patches"]:
            if existing_patch.get("target", {}).get("name") == patch.get("target", {}).get("name") and \
               existing_patch.get("target", {}).get("kind") == patch.get("target", {}).get("kind"):
                patch_exists = True
                break
        
        if not patch_exists:
            kustomization["patches"].append(patch)
        
        # Write Kustomization file
        with open(kustomization_path, "w") as f:
            yaml.dump(kustomization, f)
        
        return {
            "path": path,
            "kustomization_path": kustomization_path,
            "patch": patch,
            "patches": kustomization["patches"]
        }
    
    def set_namespace(self, path: str, namespace: str) -> Dict[str, Any]:
        """
        Set namespace in a Kustomization.
        
        Args:
            path: Path to Kustomization directory
            namespace: Namespace to set
            
        Returns:
            Dict[str, Any]: Namespace setting result
        """
        # Read Kustomization file
        kustomization_path = os.path.join(path, "kustomization.yaml")
        with open(kustomization_path, "r") as f:
            kustomization = yaml.safe_load(f)
        
        # Set namespace
        kustomization["namespace"] = namespace
        
        # Write Kustomization file
        with open(kustomization_path, "w") as f:
            yaml.dump(kustomization, f)
        
        return {
            "path": path,
            "kustomization_path": kustomization_path,
            "namespace": namespace
        }
    
    def add_common_labels(self, path: str, labels: Dict[str, str]) -> Dict[str, Any]:
        """
        Add common labels to a Kustomization.
        
        Args:
            path: Path to Kustomization directory
            labels: Labels to add
            
        Returns:
            Dict[str, Any]: Labels addition result
        """
        # Read Kustomization file
        kustomization_path = os.path.join(path, "kustomization.yaml")
        with open(kustomization_path, "r") as f:
            kustomization = yaml.safe_load(f)
        
        # Add common labels
        if "commonLabels" not in kustomization:
            kustomization["commonLabels"] = {}
        
        kustomization["commonLabels"].update(labels)
        
        # Write Kustomization file
        with open(kustomization_path, "w") as f:
            yaml.dump(kustomization, f)
        
        return {
            "path": path,
            "kustomization_path": kustomization_path,
            "labels": labels,
            "common_labels": kustomization["commonLabels"]
        }
    
    def add_common_annotations(self, path: str, annotations: Dict[str, str]) -> Dict[str, Any]:
        """
        Add common annotations to a Kustomization.
        
        Args:
            path: Path to Kustomization directory
            annotations: Annotations to add
            
        Returns:
            Dict[str, Any]: Annotations addition result
        """
        # Read Kustomization file
        kustomization_path = os.path.join(path, "kustomization.yaml")
        with open(kustomization_path, "r") as f:
            kustomization = yaml.safe_load(f)
        
        # Add common annotations
        if "commonAnnotations" not in kustomization:
            kustomization["commonAnnotations"] = {}
        
        kustomization["commonAnnotations"].update(annotations)
        
        # Write Kustomization file
        with open(kustomization_path, "w") as f:
            yaml.dump(kustomization, f)
        
        return {
            "path": path,
            "kustomization_path": kustomization_path,
            "annotations": annotations,
            "common_annotations": kustomization["commonAnnotations"]
        }


class KustomizeExecutor:
    """
    Executes Kustomize CLI commands.
    
    This class provides methods for executing Kustomize CLI and kubectl commands
    and handling their output.
    """
    
    def __init__(self, kustomize_binary: str, kubectl_binary: str, working_dir: str):
        """
        Initialize the Kustomize Executor.
        
        Args:
            kustomize_binary: Path to Kustomize CLI binary
            kubectl_binary: Path to kubectl binary
            working_dir: Working directory for Kustomize operations
        """
        self.kustomize_binary = kustomize_binary
        self.kubectl_binary = kubectl_binary
        self.working_dir = working_dir
    
    def run_kustomize_command(self, args: List[str], check: bool = True) -> str:
        """
        Run a Kustomize CLI command.
        
        Args:
            args: Command arguments
            check: Whether to check for command success
            
        Returns:
            str: Command output
            
        Raises:
            Exception: If the command fails and check is True
        """
        cmd = [self.kustomize_binary] + args
        logger.info(f"Running Kustomize command: {' '.join(cmd)}")
        
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
            error_message = f"Kustomize command failed: {e.stderr}"
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
