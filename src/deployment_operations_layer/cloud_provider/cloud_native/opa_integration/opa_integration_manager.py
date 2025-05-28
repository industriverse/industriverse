"""
OPA Integration Manager

This module provides integration with Open Policy Agent (OPA) for the Deployment Operations Layer.
It handles deployment, configuration, and management of OPA resources
including policies, data, and constraints.

Classes:
    OPAIntegrationManager: Manages OPA integration
    PolicyManager: Manages OPA policies
    ConstraintManager: Manages OPA constraints
    OPAExecutor: Executes OPA API calls
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

class OPAIntegrationManager:
    """
    Manages Open Policy Agent (OPA) integration for the Deployment Operations Layer.
    
    This class provides a unified interface for interacting with OPA,
    handling policies, data, and constraints.
    """
    
    def __init__(self, kubectl_binary_path: Optional[str] = None,
                opa_binary_path: Optional[str] = None,
                working_dir: Optional[str] = None,
                namespace: str = "opa"):
        """
        Initialize the OPA Integration Manager.
        
        Args:
            kubectl_binary_path: Path to kubectl binary (optional, defaults to 'kubectl' in PATH)
            opa_binary_path: Path to opa binary (optional, defaults to 'opa' in PATH)
            working_dir: Working directory for OPA operations (optional)
            namespace: Kubernetes namespace for OPA (default: opa)
        """
        self.kubectl_binary = kubectl_binary_path or "kubectl"
        self.opa_binary = opa_binary_path or "opa"
        self.working_dir = working_dir or tempfile.mkdtemp(prefix="opa_")
        self.namespace = namespace
        
        self.executor = OPAExecutor(
            self.kubectl_binary,
            self.opa_binary,
            self.working_dir,
            self.namespace
        )
        self.policy_manager = PolicyManager(self.executor)
        self.constraint_manager = ConstraintManager(self.executor)
    
    def deploy_opa(self, namespace: Optional[str] = None) -> AgentResponse:
        """
        Deploy Open Policy Agent to Kubernetes.
        
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
            
            # Deploy OPA CRDs
            self._deploy_opa_crds()
            
            # Deploy OPA
            self._deploy_opa_controller(namespace)
            
            return AgentResponse(
                success=True,
                message=f"Open Policy Agent deployed successfully to namespace {namespace}",
                data={
                    "namespace": namespace
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to deploy Open Policy Agent: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to deploy Open Policy Agent: {str(e)}",
                data={}
            )
    
    def _deploy_opa_crds(self) -> None:
        """
        Deploy OPA CRDs.
        """
        # Define CRD URL
        crd_url = "https://raw.githubusercontent.com/open-policy-agent/gatekeeper/master/deploy/gatekeeper.yaml"
        
        # Download Gatekeeper YAML
        gatekeeper_path = os.path.join(self.working_dir, "gatekeeper.yaml")
        response = requests.get(crd_url)
        with open(gatekeeper_path, "w") as f:
            f.write(response.text)
        
        # Extract and apply CRDs
        crd_path = os.path.join(self.working_dir, "opa-crds.yaml")
        
        # Parse YAML and extract CRDs
        with open(gatekeeper_path, "r") as f:
            documents = list(yaml.safe_load_all(f))
        
        crds = [doc for doc in documents if doc.get("kind") == "CustomResourceDefinition"]
        
        with open(crd_path, "w") as f:
            yaml.dump_all(crds, f)
        
        # Apply CRDs
        self.executor.run_kubectl_command(["apply", "-f", crd_path])
    
    def _deploy_opa_controller(self, namespace: str) -> None:
        """
        Deploy OPA Controller.
        
        Args:
            namespace: Kubernetes namespace
        """
        # Define controller URL
        controller_url = "https://raw.githubusercontent.com/open-policy-agent/gatekeeper/master/deploy/gatekeeper.yaml"
        
        # Download controller YAML
        controller_path = os.path.join(self.working_dir, "gatekeeper.yaml")
        response = requests.get(controller_url)
        
        # Replace namespace in controller YAML
        controller_yaml = response.text.replace("namespace: gatekeeper-system", f"namespace: {namespace}")
        
        with open(controller_path, "w") as f:
            f.write(controller_yaml)
        
        # Apply controller
        self.executor.run_kubectl_command(["apply", "-f", controller_path])
    
    def create_constraint_template(self, name: str, 
                                  rego_policy: str,
                                  targets: List[Dict[str, Any]],
                                  schema: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Create a ConstraintTemplate resource.
        
        Args:
            name: ConstraintTemplate name
            rego_policy: Rego policy code
            targets: List of targets (e.g., [{"target": "admission.k8s.gatekeeper.sh"}])
            schema: JSON schema for the constraint (optional)
            
        Returns:
            AgentResponse: Creation response
        """
        try:
            # Create ConstraintTemplate
            result = self.constraint_manager.create_constraint_template(
                name=name,
                rego_policy=rego_policy,
                targets=targets,
                schema=schema
            )
            
            return AgentResponse(
                success=True,
                message=f"ConstraintTemplate {name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create ConstraintTemplate: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create ConstraintTemplate: {str(e)}",
                data={}
            )
    
    def create_constraint(self, name: str, 
                         kind: str,
                         match: Dict[str, Any],
                         parameters: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Create a Constraint resource.
        
        Args:
            name: Constraint name
            kind: Constraint kind (e.g., "K8sRequiredLabels")
            match: Match criteria
            parameters: Constraint parameters (optional)
            
        Returns:
            AgentResponse: Creation response
        """
        try:
            # Create Constraint
            result = self.constraint_manager.create_constraint(
                name=name,
                kind=kind,
                match=match,
                parameters=parameters
            )
            
            return AgentResponse(
                success=True,
                message=f"Constraint {name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create Constraint: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create Constraint: {str(e)}",
                data={}
            )
    
    def create_policy(self, name: str, 
                     policy_content: str,
                     namespace: Optional[str] = None) -> AgentResponse:
        """
        Create an OPA policy.
        
        Args:
            name: Policy name
            policy_content: Rego policy content
            namespace: Kubernetes namespace (optional, defaults to self.namespace)
            
        Returns:
            AgentResponse: Creation response
        """
        try:
            namespace = namespace or self.namespace
            
            # Create ConfigMap for policy
            result = self.policy_manager.create_policy(
                name=name,
                policy_content=policy_content,
                namespace=namespace
            )
            
            return AgentResponse(
                success=True,
                message=f"Policy {name} created successfully in namespace {namespace}",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create policy: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create policy: {str(e)}",
                data={}
            )
    
    def validate_policy(self, policy_content: str) -> AgentResponse:
        """
        Validate an OPA policy.
        
        Args:
            policy_content: Rego policy content
            
        Returns:
            AgentResponse: Validation response
        """
        try:
            # Validate policy
            result = self.policy_manager.validate_policy(
                policy_content=policy_content
            )
            
            return AgentResponse(
                success=True,
                message="Policy validated successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to validate policy: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to validate policy: {str(e)}",
                data={}
            )
    
    def test_policy(self, policy_content: str, 
                   input_data: Dict[str, Any]) -> AgentResponse:
        """
        Test an OPA policy against input data.
        
        Args:
            policy_content: Rego policy content
            input_data: Input data to test against
            
        Returns:
            AgentResponse: Test response
        """
        try:
            # Test policy
            result = self.policy_manager.test_policy(
                policy_content=policy_content,
                input_data=input_data
            )
            
            return AgentResponse(
                success=True,
                message="Policy tested successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to test policy: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to test policy: {str(e)}",
                data={}
            )
    
    def to_mcp_context(self) -> MCPContext:
        """
        Convert OPA integration information to MCP context.
        
        Returns:
            MCPContext: MCP context with OPA integration information
        """
        return MCPContext(
            context_type="opa_integration",
            namespace=self.namespace,
            working_dir=self.working_dir
        )


class PolicyManager:
    """
    Manages OPA policies.
    
    This class provides methods for creating, updating, and deleting OPA policies.
    """
    
    def __init__(self, executor: 'OPAExecutor'):
        """
        Initialize the Policy Manager.
        
        Args:
            executor: OPA executor
        """
        self.executor = executor
    
    def create_policy(self, name: str, 
                     policy_content: str,
                     namespace: str) -> Dict[str, Any]:
        """
        Create an OPA policy.
        
        Args:
            name: Policy name
            policy_content: Rego policy content
            namespace: Kubernetes namespace
            
        Returns:
            Dict[str, Any]: Created ConfigMap
        """
        # Validate policy
        self.validate_policy(policy_content)
        
        # Create ConfigMap for policy
        configmap = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": f"opa-policy-{name}",
                "namespace": namespace,
                "labels": {
                    "app": "opa",
                    "opa-policy": "true"
                }
            },
            "data": {
                f"{name}.rego": policy_content
            }
        }
        
        # Write ConfigMap to file
        configmap_path = os.path.join(self.executor.working_dir, f"opa-policy-{name}.yaml")
        with open(configmap_path, "w") as f:
            yaml.dump(configmap, f)
        
        # Apply ConfigMap
        self.executor.run_kubectl_command(["apply", "-f", configmap_path])
        
        # Get created ConfigMap
        result = self.executor.run_kubectl_command([
            "get", "configmap", f"opa-policy-{name}", "-n", namespace, "-o", "json"
        ])
        
        return json.loads(result)
    
    def update_policy(self, name: str, 
                     policy_content: str,
                     namespace: str) -> Dict[str, Any]:
        """
        Update an OPA policy.
        
        Args:
            name: Policy name
            policy_content: Rego policy content
            namespace: Kubernetes namespace
            
        Returns:
            Dict[str, Any]: Updated ConfigMap
        """
        # Get existing ConfigMap
        try:
            existing_configmap = self.executor.run_kubectl_command([
                "get", "configmap", f"opa-policy-{name}", "-n", namespace, "-o", "json"
            ])
            existing_configmap = json.loads(existing_configmap)
        except Exception:
            # ConfigMap doesn't exist, create it
            return self.create_policy(
                name=name,
                policy_content=policy_content,
                namespace=namespace
            )
        
        # Validate policy
        self.validate_policy(policy_content)
        
        # Update ConfigMap
        configmap = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": f"opa-policy-{name}",
                "namespace": namespace,
                "labels": {
                    "app": "opa",
                    "opa-policy": "true"
                }
            },
            "data": {
                f"{name}.rego": policy_content
            }
        }
        
        # Write ConfigMap to file
        configmap_path = os.path.join(self.executor.working_dir, f"opa-policy-{name}.yaml")
        with open(configmap_path, "w") as f:
            yaml.dump(configmap, f)
        
        # Apply ConfigMap
        self.executor.run_kubectl_command(["apply", "-f", configmap_path])
        
        # Get updated ConfigMap
        result = self.executor.run_kubectl_command([
            "get", "configmap", f"opa-policy-{name}", "-n", namespace, "-o", "json"
        ])
        
        return json.loads(result)
    
    def delete_policy(self, name: str, namespace: str) -> None:
        """
        Delete an OPA policy.
        
        Args:
            name: Policy name
            namespace: Kubernetes namespace
        """
        self.executor.run_kubectl_command([
            "delete", "configmap", f"opa-policy-{name}", "-n", namespace
        ])
    
    def validate_policy(self, policy_content: str) -> Dict[str, Any]:
        """
        Validate an OPA policy.
        
        Args:
            policy_content: Rego policy content
            
        Returns:
            Dict[str, Any]: Validation result
        """
        # Write policy to file
        policy_path = os.path.join(self.executor.working_dir, "policy.rego")
        with open(policy_path, "w") as f:
            f.write(policy_content)
        
        # Validate policy
        result = self.executor.run_opa_command([
            "check", policy_path
        ])
        
        return {
            "valid": True,
            "message": result
        }
    
    def test_policy(self, policy_content: str, 
                   input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test an OPA policy against input data.
        
        Args:
            policy_content: Rego policy content
            input_data: Input data to test against
            
        Returns:
            Dict[str, Any]: Test result
        """
        # Write policy to file
        policy_path = os.path.join(self.executor.working_dir, "policy.rego")
        with open(policy_path, "w") as f:
            f.write(policy_content)
        
        # Write input data to file
        input_path = os.path.join(self.executor.working_dir, "input.json")
        with open(input_path, "w") as f:
            json.dump(input_data, f)
        
        # Test policy
        result = self.executor.run_opa_command([
            "eval", "-d", policy_path, "-i", input_path, "data"
        ])
        
        return json.loads(result)


class ConstraintManager:
    """
    Manages OPA constraints.
    
    This class provides methods for creating, updating, and deleting OPA constraints.
    """
    
    def __init__(self, executor: 'OPAExecutor'):
        """
        Initialize the Constraint Manager.
        
        Args:
            executor: OPA executor
        """
        self.executor = executor
    
    def create_constraint_template(self, name: str, 
                                  rego_policy: str,
                                  targets: List[Dict[str, Any]],
                                  schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a ConstraintTemplate resource.
        
        Args:
            name: ConstraintTemplate name
            rego_policy: Rego policy code
            targets: List of targets (e.g., [{"target": "admission.k8s.gatekeeper.sh"}])
            schema: JSON schema for the constraint (optional)
            
        Returns:
            Dict[str, Any]: Created ConstraintTemplate
        """
        # Create ConstraintTemplate
        constraint_template = {
            "apiVersion": "templates.gatekeeper.sh/v1beta1",
            "kind": "ConstraintTemplate",
            "metadata": {
                "name": name
            },
            "spec": {
                "crd": {
                    "spec": {
                        "names": {
                            "kind": name
                        }
                    }
                },
                "targets": targets
            }
        }
        
        # Add schema if provided
        if schema:
            constraint_template["spec"]["crd"]["spec"]["validation"] = schema
        
        # Add rego policy
        constraint_template["spec"]["targets"][0]["rego"] = rego_policy
        
        # Write ConstraintTemplate to file
        constraint_template_path = os.path.join(self.executor.working_dir, f"constraint-template-{name}.yaml")
        with open(constraint_template_path, "w") as f:
            yaml.dump(constraint_template, f)
        
        # Apply ConstraintTemplate
        self.executor.run_kubectl_command(["apply", "-f", constraint_template_path])
        
        # Get created ConstraintTemplate
        result = self.executor.run_kubectl_command([
            "get", "constrainttemplate", name, "-o", "json"
        ])
        
        return json.loads(result)
    
    def create_constraint(self, name: str, 
                         kind: str,
                         match: Dict[str, Any],
                         parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a Constraint resource.
        
        Args:
            name: Constraint name
            kind: Constraint kind (e.g., "K8sRequiredLabels")
            match: Match criteria
            parameters: Constraint parameters (optional)
            
        Returns:
            Dict[str, Any]: Created Constraint
        """
        # Create Constraint
        constraint = {
            "apiVersion": "constraints.gatekeeper.sh/v1beta1",
            "kind": kind,
            "metadata": {
                "name": name
            },
            "spec": {
                "match": match
            }
        }
        
        # Add parameters if provided
        if parameters:
            constraint["spec"]["parameters"] = parameters
        
        # Write Constraint to file
        constraint_path = os.path.join(self.executor.working_dir, f"constraint-{name}.yaml")
        with open(constraint_path, "w") as f:
            yaml.dump(constraint, f)
        
        # Apply Constraint
        self.executor.run_kubectl_command(["apply", "-f", constraint_path])
        
        # Get created Constraint
        result = self.executor.run_kubectl_command([
            "get", kind, name, "-o", "json"
        ])
        
        return json.loads(result)
    
    def update_constraint_template(self, name: str, 
                                  rego_policy: str,
                                  targets: List[Dict[str, Any]],
                                  schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Update a ConstraintTemplate resource.
        
        Args:
            name: ConstraintTemplate name
            rego_policy: Rego policy code
            targets: List of targets (e.g., [{"target": "admission.k8s.gatekeeper.sh"}])
            schema: JSON schema for the constraint (optional)
            
        Returns:
            Dict[str, Any]: Updated ConstraintTemplate
        """
        # Get existing ConstraintTemplate
        try:
            existing_constraint_template = self.executor.run_kubectl_command([
                "get", "constrainttemplate", name, "-o", "json"
            ])
            existing_constraint_template = json.loads(existing_constraint_template)
        except Exception:
            # ConstraintTemplate doesn't exist, create it
            return self.create_constraint_template(
                name=name,
                rego_policy=rego_policy,
                targets=targets,
                schema=schema
            )
        
        # Update ConstraintTemplate
        constraint_template = {
            "apiVersion": "templates.gatekeeper.sh/v1beta1",
            "kind": "ConstraintTemplate",
            "metadata": {
                "name": name
            },
            "spec": {
                "crd": {
                    "spec": {
                        "names": {
                            "kind": name
                        }
                    }
                },
                "targets": targets
            }
        }
        
        # Add schema if provided
        if schema:
            constraint_template["spec"]["crd"]["spec"]["validation"] = schema
        
        # Add rego policy
        constraint_template["spec"]["targets"][0]["rego"] = rego_policy
        
        # Write ConstraintTemplate to file
        constraint_template_path = os.path.join(self.executor.working_dir, f"constraint-template-{name}.yaml")
        with open(constraint_template_path, "w") as f:
            yaml.dump(constraint_template, f)
        
        # Apply ConstraintTemplate
        self.executor.run_kubectl_command(["apply", "-f", constraint_template_path])
        
        # Get updated ConstraintTemplate
        result = self.executor.run_kubectl_command([
            "get", "constrainttemplate", name, "-o", "json"
        ])
        
        return json.loads(result)
    
    def update_constraint(self, name: str, 
                         kind: str,
                         match: Dict[str, Any],
                         parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Update a Constraint resource.
        
        Args:
            name: Constraint name
            kind: Constraint kind (e.g., "K8sRequiredLabels")
            match: Match criteria
            parameters: Constraint parameters (optional)
            
        Returns:
            Dict[str, Any]: Updated Constraint
        """
        # Get existing Constraint
        try:
            existing_constraint = self.executor.run_kubectl_command([
                "get", kind, name, "-o", "json"
            ])
            existing_constraint = json.loads(existing_constraint)
        except Exception:
            # Constraint doesn't exist, create it
            return self.create_constraint(
                name=name,
                kind=kind,
                match=match,
                parameters=parameters
            )
        
        # Update Constraint
        constraint = {
            "apiVersion": "constraints.gatekeeper.sh/v1beta1",
            "kind": kind,
            "metadata": {
                "name": name
            },
            "spec": {
                "match": match
            }
        }
        
        # Add parameters if provided
        if parameters:
            constraint["spec"]["parameters"] = parameters
        
        # Write Constraint to file
        constraint_path = os.path.join(self.executor.working_dir, f"constraint-{name}.yaml")
        with open(constraint_path, "w") as f:
            yaml.dump(constraint, f)
        
        # Apply Constraint
        self.executor.run_kubectl_command(["apply", "-f", constraint_path])
        
        # Get updated Constraint
        result = self.executor.run_kubectl_command([
            "get", kind, name, "-o", "json"
        ])
        
        return json.loads(result)
    
    def delete_constraint_template(self, name: str) -> None:
        """
        Delete a ConstraintTemplate resource.
        
        Args:
            name: ConstraintTemplate name
        """
        self.executor.run_kubectl_command([
            "delete", "constrainttemplate", name
        ])
    
    def delete_constraint(self, name: str, kind: str) -> None:
        """
        Delete a Constraint resource.
        
        Args:
            name: Constraint name
            kind: Constraint kind (e.g., "K8sRequiredLabels")
        """
        self.executor.run_kubectl_command([
            "delete", kind, name
        ])


class OPAExecutor:
    """
    Executes OPA API calls and kubectl/opa commands.
    
    This class provides methods for executing OPA API calls and kubectl/opa commands
    and handling their output.
    """
    
    def __init__(self, kubectl_binary: str,
                opa_binary: str,
                working_dir: str,
                namespace: str):
        """
        Initialize the OPA Executor.
        
        Args:
            kubectl_binary: Path to kubectl binary
            opa_binary: Path to opa binary
            working_dir: Working directory for OPA operations
            namespace: Kubernetes namespace
        """
        self.kubectl_binary = kubectl_binary
        self.opa_binary = opa_binary
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
    
    def run_opa_command(self, args: List[str], check: bool = True) -> str:
        """
        Run an opa command.
        
        Args:
            args: Command arguments
            check: Whether to check for command success
            
        Returns:
            str: Command output
            
        Raises:
            Exception: If the command fails and check is True
        """
        cmd = [self.opa_binary] + args
        logger.info(f"Running opa command: {' '.join(cmd)}")
        
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
            error_message = f"opa command failed: {e.stderr}"
            logger.error(error_message)
            
            if check:
                raise Exception(error_message)
            
            return e.stderr
