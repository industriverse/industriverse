"""
Kyverno Integration Manager

This module provides integration with Kyverno for the Deployment Operations Layer.
It handles deployment, configuration, and management of Kyverno resources
including policies, policy reports, and validations.

Classes:
    KyvernoIntegrationManager: Manages Kyverno integration
    PolicyManager: Manages Kyverno policies
    ClusterPolicyManager: Manages Kyverno cluster policies
    PolicyReportManager: Manages Kyverno policy reports
    KyvernoExecutor: Executes Kyverno API calls
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

class KyvernoIntegrationManager:
    """
    Manages Kyverno integration for the Deployment Operations Layer.
    
    This class provides a unified interface for interacting with Kyverno,
    handling policies, policy reports, and validations.
    """
    
    def __init__(self, kubectl_binary_path: Optional[str] = None,
                kyverno_binary_path: Optional[str] = None,
                working_dir: Optional[str] = None,
                namespace: str = "kyverno"):
        """
        Initialize the Kyverno Integration Manager.
        
        Args:
            kubectl_binary_path: Path to kubectl binary (optional, defaults to 'kubectl' in PATH)
            kyverno_binary_path: Path to kyverno CLI binary (optional, defaults to 'kyverno' in PATH)
            working_dir: Working directory for Kyverno operations (optional)
            namespace: Kubernetes namespace for Kyverno (default: kyverno)
        """
        self.kubectl_binary = kubectl_binary_path or "kubectl"
        self.kyverno_binary = kyverno_binary_path or "kyverno"
        self.working_dir = working_dir or tempfile.mkdtemp(prefix="kyverno_")
        self.namespace = namespace
        
        self.executor = KyvernoExecutor(
            self.kubectl_binary,
            self.kyverno_binary,
            self.working_dir,
            self.namespace
        )
        self.policy_manager = PolicyManager(self.executor)
        self.cluster_policy_manager = ClusterPolicyManager(self.executor)
        self.policy_report_manager = PolicyReportManager(self.executor)
    
    def deploy_kyverno(self, namespace: Optional[str] = None) -> AgentResponse:
        """
        Deploy Kyverno to Kubernetes.
        
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
            
            # Deploy Kyverno CRDs
            self._deploy_kyverno_crds()
            
            # Deploy Kyverno
            self._deploy_kyverno_controller(namespace)
            
            return AgentResponse(
                success=True,
                message=f"Kyverno deployed successfully to namespace {namespace}",
                data={
                    "namespace": namespace
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to deploy Kyverno: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to deploy Kyverno: {str(e)}",
                data={}
            )
    
    def _deploy_kyverno_crds(self) -> None:
        """
        Deploy Kyverno CRDs.
        """
        # Define CRD URL
        crd_url = "https://raw.githubusercontent.com/kyverno/kyverno/main/config/crds/kyverno.io_clusterpolicies.yaml"
        
        # Download Kyverno CRD YAML
        crd_path = os.path.join(self.working_dir, "kyverno-crds.yaml")
        response = requests.get(crd_url)
        with open(crd_path, "w") as f:
            f.write(response.text)
        
        # Apply CRDs
        self.executor.run_kubectl_command(["apply", "-f", crd_path])
    
    def _deploy_kyverno_controller(self, namespace: str) -> None:
        """
        Deploy Kyverno Controller.
        
        Args:
            namespace: Kubernetes namespace
        """
        # Define controller URL
        controller_url = "https://raw.githubusercontent.com/kyverno/kyverno/main/config/install.yaml"
        
        # Download controller YAML
        controller_path = os.path.join(self.working_dir, "kyverno.yaml")
        response = requests.get(controller_url)
        
        # Replace namespace in controller YAML
        controller_yaml = response.text.replace("namespace: kyverno", f"namespace: {namespace}")
        
        with open(controller_path, "w") as f:
            f.write(controller_yaml)
        
        # Apply controller
        self.executor.run_kubectl_command(["apply", "-f", controller_path])
    
    def create_policy(self, name: str, 
                     rules: List[Dict[str, Any]],
                     namespace: Optional[str] = None,
                     background: bool = True,
                     validate_resources: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Create a Kyverno Policy resource.
        
        Args:
            name: Policy name
            rules: List of policy rules
            namespace: Kubernetes namespace (optional, defaults to self.namespace)
            background: Whether to run policy in background (default: True)
            validate_resources: Resource validation settings (optional)
            
        Returns:
            AgentResponse: Creation response
        """
        try:
            namespace = namespace or self.namespace
            
            # Create Policy
            result = self.policy_manager.create_policy(
                name=name,
                rules=rules,
                namespace=namespace,
                background=background,
                validate_resources=validate_resources
            )
            
            return AgentResponse(
                success=True,
                message=f"Policy {name} created successfully in namespace {namespace}",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create Policy: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create Policy: {str(e)}",
                data={}
            )
    
    def create_cluster_policy(self, name: str, 
                            rules: List[Dict[str, Any]],
                            background: bool = True,
                            validate_resources: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Create a Kyverno ClusterPolicy resource.
        
        Args:
            name: ClusterPolicy name
            rules: List of policy rules
            background: Whether to run policy in background (default: True)
            validate_resources: Resource validation settings (optional)
            
        Returns:
            AgentResponse: Creation response
        """
        try:
            # Create ClusterPolicy
            result = self.cluster_policy_manager.create_cluster_policy(
                name=name,
                rules=rules,
                background=background,
                validate_resources=validate_resources
            )
            
            return AgentResponse(
                success=True,
                message=f"ClusterPolicy {name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create ClusterPolicy: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create ClusterPolicy: {str(e)}",
                data={}
            )
    
    def validate_resource(self, resource_path: str, 
                         policy_path: Optional[str] = None) -> AgentResponse:
        """
        Validate a resource against Kyverno policies.
        
        Args:
            resource_path: Path to resource YAML file
            policy_path: Path to policy YAML file (optional)
            
        Returns:
            AgentResponse: Validation response
        """
        try:
            # Validate resource
            result = self.executor.run_kyverno_command([
                "apply", resource_path, "--policy", policy_path or ""
            ])
            
            return AgentResponse(
                success=True,
                message="Resource validated successfully",
                data={
                    "validation_result": result
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to validate resource: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to validate resource: {str(e)}",
                data={}
            )
    
    def get_policy_reports(self, namespace: Optional[str] = None) -> AgentResponse:
        """
        Get Kyverno PolicyReports.
        
        Args:
            namespace: Kubernetes namespace (optional, defaults to self.namespace)
            
        Returns:
            AgentResponse: PolicyReports response
        """
        try:
            namespace = namespace or self.namespace
            
            # Get PolicyReports
            result = self.policy_report_manager.get_policy_reports(namespace)
            
            return AgentResponse(
                success=True,
                message=f"PolicyReports retrieved successfully from namespace {namespace}",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to get PolicyReports: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to get PolicyReports: {str(e)}",
                data={}
            )
    
    def get_cluster_policy_reports(self) -> AgentResponse:
        """
        Get Kyverno ClusterPolicyReports.
        
        Returns:
            AgentResponse: ClusterPolicyReports response
        """
        try:
            # Get ClusterPolicyReports
            result = self.policy_report_manager.get_cluster_policy_reports()
            
            return AgentResponse(
                success=True,
                message="ClusterPolicyReports retrieved successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to get ClusterPolicyReports: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to get ClusterPolicyReports: {str(e)}",
                data={}
            )
    
    def to_mcp_context(self) -> MCPContext:
        """
        Convert Kyverno integration information to MCP context.
        
        Returns:
            MCPContext: MCP context with Kyverno integration information
        """
        return MCPContext(
            context_type="kyverno_integration",
            namespace=self.namespace,
            working_dir=self.working_dir
        )


class PolicyManager:
    """
    Manages Kyverno policies.
    
    This class provides methods for creating, updating, and deleting Kyverno policies.
    """
    
    def __init__(self, executor: 'KyvernoExecutor'):
        """
        Initialize the Policy Manager.
        
        Args:
            executor: Kyverno executor
        """
        self.executor = executor
    
    def create_policy(self, name: str, 
                     rules: List[Dict[str, Any]],
                     namespace: str,
                     background: bool = True,
                     validate_resources: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a Kyverno Policy resource.
        
        Args:
            name: Policy name
            rules: List of policy rules
            namespace: Kubernetes namespace
            background: Whether to run policy in background (default: True)
            validate_resources: Resource validation settings (optional)
            
        Returns:
            Dict[str, Any]: Created Policy
        """
        # Create Policy
        policy = {
            "apiVersion": "kyverno.io/v1",
            "kind": "Policy",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "background": background,
                "rules": rules
            }
        }
        
        # Add validate_resources if provided
        if validate_resources:
            policy["spec"]["validationFailureAction"] = validate_resources.get("validationFailureAction", "audit")
            policy["spec"]["validationFailureActionOverrides"] = validate_resources.get("validationFailureActionOverrides", [])
        
        # Write Policy to file
        policy_path = os.path.join(self.executor.working_dir, f"policy-{name}.yaml")
        with open(policy_path, "w") as f:
            yaml.dump(policy, f)
        
        # Apply Policy
        self.executor.run_kubectl_command(["apply", "-f", policy_path])
        
        # Get created Policy
        result = self.executor.run_kubectl_command([
            "get", "policy", name, "-n", namespace, "-o", "json"
        ])
        
        return json.loads(result)
    
    def update_policy(self, name: str, 
                     rules: List[Dict[str, Any]],
                     namespace: str,
                     background: bool = True,
                     validate_resources: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Update a Kyverno Policy resource.
        
        Args:
            name: Policy name
            rules: List of policy rules
            namespace: Kubernetes namespace
            background: Whether to run policy in background (default: True)
            validate_resources: Resource validation settings (optional)
            
        Returns:
            Dict[str, Any]: Updated Policy
        """
        # Get existing Policy
        try:
            existing_policy = self.executor.run_kubectl_command([
                "get", "policy", name, "-n", namespace, "-o", "json"
            ])
            existing_policy = json.loads(existing_policy)
        except Exception:
            # Policy doesn't exist, create it
            return self.create_policy(
                name=name,
                rules=rules,
                namespace=namespace,
                background=background,
                validate_resources=validate_resources
            )
        
        # Update Policy
        policy = {
            "apiVersion": "kyverno.io/v1",
            "kind": "Policy",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "background": background,
                "rules": rules
            }
        }
        
        # Add validate_resources if provided
        if validate_resources:
            policy["spec"]["validationFailureAction"] = validate_resources.get("validationFailureAction", "audit")
            policy["spec"]["validationFailureActionOverrides"] = validate_resources.get("validationFailureActionOverrides", [])
        
        # Write Policy to file
        policy_path = os.path.join(self.executor.working_dir, f"policy-{name}.yaml")
        with open(policy_path, "w") as f:
            yaml.dump(policy, f)
        
        # Apply Policy
        self.executor.run_kubectl_command(["apply", "-f", policy_path])
        
        # Get updated Policy
        result = self.executor.run_kubectl_command([
            "get", "policy", name, "-n", namespace, "-o", "json"
        ])
        
        return json.loads(result)
    
    def delete_policy(self, name: str, namespace: str) -> None:
        """
        Delete a Kyverno Policy resource.
        
        Args:
            name: Policy name
            namespace: Kubernetes namespace
        """
        self.executor.run_kubectl_command([
            "delete", "policy", name, "-n", namespace
        ])
    
    def get_policy(self, name: str, namespace: str) -> Dict[str, Any]:
        """
        Get a Kyverno Policy resource.
        
        Args:
            name: Policy name
            namespace: Kubernetes namespace
            
        Returns:
            Dict[str, Any]: Policy
        """
        result = self.executor.run_kubectl_command([
            "get", "policy", name, "-n", namespace, "-o", "json"
        ])
        
        return json.loads(result)
    
    def list_policies(self, namespace: str) -> List[Dict[str, Any]]:
        """
        List Kyverno Policy resources.
        
        Args:
            namespace: Kubernetes namespace
            
        Returns:
            List[Dict[str, Any]]: Policies
        """
        result = self.executor.run_kubectl_command([
            "get", "policy", "-n", namespace, "-o", "json"
        ])
        
        return json.loads(result).get("items", [])


class ClusterPolicyManager:
    """
    Manages Kyverno cluster policies.
    
    This class provides methods for creating, updating, and deleting Kyverno cluster policies.
    """
    
    def __init__(self, executor: 'KyvernoExecutor'):
        """
        Initialize the Cluster Policy Manager.
        
        Args:
            executor: Kyverno executor
        """
        self.executor = executor
    
    def create_cluster_policy(self, name: str, 
                            rules: List[Dict[str, Any]],
                            background: bool = True,
                            validate_resources: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a Kyverno ClusterPolicy resource.
        
        Args:
            name: ClusterPolicy name
            rules: List of policy rules
            background: Whether to run policy in background (default: True)
            validate_resources: Resource validation settings (optional)
            
        Returns:
            Dict[str, Any]: Created ClusterPolicy
        """
        # Create ClusterPolicy
        cluster_policy = {
            "apiVersion": "kyverno.io/v1",
            "kind": "ClusterPolicy",
            "metadata": {
                "name": name
            },
            "spec": {
                "background": background,
                "rules": rules
            }
        }
        
        # Add validate_resources if provided
        if validate_resources:
            cluster_policy["spec"]["validationFailureAction"] = validate_resources.get("validationFailureAction", "audit")
            cluster_policy["spec"]["validationFailureActionOverrides"] = validate_resources.get("validationFailureActionOverrides", [])
        
        # Write ClusterPolicy to file
        cluster_policy_path = os.path.join(self.executor.working_dir, f"cluster-policy-{name}.yaml")
        with open(cluster_policy_path, "w") as f:
            yaml.dump(cluster_policy, f)
        
        # Apply ClusterPolicy
        self.executor.run_kubectl_command(["apply", "-f", cluster_policy_path])
        
        # Get created ClusterPolicy
        result = self.executor.run_kubectl_command([
            "get", "clusterpolicy", name, "-o", "json"
        ])
        
        return json.loads(result)
    
    def update_cluster_policy(self, name: str, 
                            rules: List[Dict[str, Any]],
                            background: bool = True,
                            validate_resources: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Update a Kyverno ClusterPolicy resource.
        
        Args:
            name: ClusterPolicy name
            rules: List of policy rules
            background: Whether to run policy in background (default: True)
            validate_resources: Resource validation settings (optional)
            
        Returns:
            Dict[str, Any]: Updated ClusterPolicy
        """
        # Get existing ClusterPolicy
        try:
            existing_cluster_policy = self.executor.run_kubectl_command([
                "get", "clusterpolicy", name, "-o", "json"
            ])
            existing_cluster_policy = json.loads(existing_cluster_policy)
        except Exception:
            # ClusterPolicy doesn't exist, create it
            return self.create_cluster_policy(
                name=name,
                rules=rules,
                background=background,
                validate_resources=validate_resources
            )
        
        # Update ClusterPolicy
        cluster_policy = {
            "apiVersion": "kyverno.io/v1",
            "kind": "ClusterPolicy",
            "metadata": {
                "name": name
            },
            "spec": {
                "background": background,
                "rules": rules
            }
        }
        
        # Add validate_resources if provided
        if validate_resources:
            cluster_policy["spec"]["validationFailureAction"] = validate_resources.get("validationFailureAction", "audit")
            cluster_policy["spec"]["validationFailureActionOverrides"] = validate_resources.get("validationFailureActionOverrides", [])
        
        # Write ClusterPolicy to file
        cluster_policy_path = os.path.join(self.executor.working_dir, f"cluster-policy-{name}.yaml")
        with open(cluster_policy_path, "w") as f:
            yaml.dump(cluster_policy, f)
        
        # Apply ClusterPolicy
        self.executor.run_kubectl_command(["apply", "-f", cluster_policy_path])
        
        # Get updated ClusterPolicy
        result = self.executor.run_kubectl_command([
            "get", "clusterpolicy", name, "-o", "json"
        ])
        
        return json.loads(result)
    
    def delete_cluster_policy(self, name: str) -> None:
        """
        Delete a Kyverno ClusterPolicy resource.
        
        Args:
            name: ClusterPolicy name
        """
        self.executor.run_kubectl_command([
            "delete", "clusterpolicy", name
        ])
    
    def get_cluster_policy(self, name: str) -> Dict[str, Any]:
        """
        Get a Kyverno ClusterPolicy resource.
        
        Args:
            name: ClusterPolicy name
            
        Returns:
            Dict[str, Any]: ClusterPolicy
        """
        result = self.executor.run_kubectl_command([
            "get", "clusterpolicy", name, "-o", "json"
        ])
        
        return json.loads(result)
    
    def list_cluster_policies(self) -> List[Dict[str, Any]]:
        """
        List Kyverno ClusterPolicy resources.
        
        Returns:
            List[Dict[str, Any]]: ClusterPolicies
        """
        result = self.executor.run_kubectl_command([
            "get", "clusterpolicy", "-o", "json"
        ])
        
        return json.loads(result).get("items", [])


class PolicyReportManager:
    """
    Manages Kyverno policy reports.
    
    This class provides methods for retrieving and analyzing Kyverno policy reports.
    """
    
    def __init__(self, executor: 'KyvernoExecutor'):
        """
        Initialize the Policy Report Manager.
        
        Args:
            executor: Kyverno executor
        """
        self.executor = executor
    
    def get_policy_reports(self, namespace: str) -> List[Dict[str, Any]]:
        """
        Get Kyverno PolicyReport resources.
        
        Args:
            namespace: Kubernetes namespace
            
        Returns:
            List[Dict[str, Any]]: PolicyReports
        """
        try:
            result = self.executor.run_kubectl_command([
                "get", "policyreport", "-n", namespace, "-o", "json"
            ])
            
            return json.loads(result).get("items", [])
        except Exception:
            # No PolicyReports found
            return []
    
    def get_cluster_policy_reports(self) -> List[Dict[str, Any]]:
        """
        Get Kyverno ClusterPolicyReport resources.
        
        Returns:
            List[Dict[str, Any]]: ClusterPolicyReports
        """
        try:
            result = self.executor.run_kubectl_command([
                "get", "clusterpolicyreport", "-o", "json"
            ])
            
            return json.loads(result).get("items", [])
        except Exception:
            # No ClusterPolicyReports found
            return []
    
    def get_policy_report(self, name: str, namespace: str) -> Dict[str, Any]:
        """
        Get a Kyverno PolicyReport resource.
        
        Args:
            name: PolicyReport name
            namespace: Kubernetes namespace
            
        Returns:
            Dict[str, Any]: PolicyReport
        """
        result = self.executor.run_kubectl_command([
            "get", "policyreport", name, "-n", namespace, "-o", "json"
        ])
        
        return json.loads(result)
    
    def get_cluster_policy_report(self, name: str) -> Dict[str, Any]:
        """
        Get a Kyverno ClusterPolicyReport resource.
        
        Args:
            name: ClusterPolicyReport name
            
        Returns:
            Dict[str, Any]: ClusterPolicyReport
        """
        result = self.executor.run_kubectl_command([
            "get", "clusterpolicyreport", name, "-o", "json"
        ])
        
        return json.loads(result)
    
    def analyze_policy_reports(self, namespace: str) -> Dict[str, Any]:
        """
        Analyze Kyverno PolicyReport resources.
        
        Args:
            namespace: Kubernetes namespace
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        policy_reports = self.get_policy_reports(namespace)
        
        # Analyze policy reports
        total_results = 0
        pass_count = 0
        fail_count = 0
        warn_count = 0
        error_count = 0
        skip_count = 0
        
        for report in policy_reports:
            summary = report.get("summary", {})
            total_results += summary.get("total", 0)
            pass_count += summary.get("pass", 0)
            fail_count += summary.get("fail", 0)
            warn_count += summary.get("warn", 0)
            error_count += summary.get("error", 0)
            skip_count += summary.get("skip", 0)
        
        return {
            "total_reports": len(policy_reports),
            "total_results": total_results,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "warn_count": warn_count,
            "error_count": error_count,
            "skip_count": skip_count
        }
    
    def analyze_cluster_policy_reports(self) -> Dict[str, Any]:
        """
        Analyze Kyverno ClusterPolicyReport resources.
        
        Returns:
            Dict[str, Any]: Analysis results
        """
        cluster_policy_reports = self.get_cluster_policy_reports()
        
        # Analyze cluster policy reports
        total_results = 0
        pass_count = 0
        fail_count = 0
        warn_count = 0
        error_count = 0
        skip_count = 0
        
        for report in cluster_policy_reports:
            summary = report.get("summary", {})
            total_results += summary.get("total", 0)
            pass_count += summary.get("pass", 0)
            fail_count += summary.get("fail", 0)
            warn_count += summary.get("warn", 0)
            error_count += summary.get("error", 0)
            skip_count += summary.get("skip", 0)
        
        return {
            "total_reports": len(cluster_policy_reports),
            "total_results": total_results,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "warn_count": warn_count,
            "error_count": error_count,
            "skip_count": skip_count
        }


class KyvernoExecutor:
    """
    Executes Kyverno API calls and kubectl/kyverno commands.
    
    This class provides methods for executing Kyverno API calls and kubectl/kyverno commands
    and handling their output.
    """
    
    def __init__(self, kubectl_binary: str,
                kyverno_binary: str,
                working_dir: str,
                namespace: str):
        """
        Initialize the Kyverno Executor.
        
        Args:
            kubectl_binary: Path to kubectl binary
            kyverno_binary: Path to kyverno binary
            working_dir: Working directory for Kyverno operations
            namespace: Kubernetes namespace
        """
        self.kubectl_binary = kubectl_binary
        self.kyverno_binary = kyverno_binary
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
    
    def run_kyverno_command(self, args: List[str], check: bool = True) -> str:
        """
        Run a kyverno command.
        
        Args:
            args: Command arguments
            check: Whether to check for command success
            
        Returns:
            str: Command output
            
        Raises:
            Exception: If the command fails and check is True
        """
        cmd = [self.kyverno_binary] + args
        logger.info(f"Running kyverno command: {' '.join(cmd)}")
        
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
            error_message = f"kyverno command failed: {e.stderr}"
            logger.error(error_message)
            
            if check:
                raise Exception(error_message)
            
            return e.stderr
