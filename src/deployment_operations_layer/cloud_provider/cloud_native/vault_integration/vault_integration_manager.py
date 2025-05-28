"""
Vault Integration Manager

This module provides integration with HashiCorp Vault for the Deployment Operations Layer.
It handles deployment, configuration, and management of Vault resources
including secrets, authentication methods, policies, and roles.

Classes:
    VaultIntegrationManager: Manages Vault integration
    SecretManager: Manages Vault secrets
    AuthMethodManager: Manages Vault authentication methods
    PolicyManager: Manages Vault policies
    RoleManager: Manages Vault roles
    VaultExecutor: Executes Vault API calls
"""

import json
import logging
import os
import subprocess
import tempfile
import requests
from typing import Dict, List, Any, Optional, Tuple, Union

from ....agent.agent_utils import AgentResponse
from ....protocol.mcp_integration.mcp_context_schema import MCPContext

logger = logging.getLogger(__name__)

class VaultIntegrationManager:
    """
    Manages HashiCorp Vault integration for the Deployment Operations Layer.
    
    This class provides a unified interface for interacting with Vault,
    handling secrets, authentication methods, policies, and roles.
    """
    
    def __init__(self, vault_addr: Optional[str] = None,
                vault_token: Optional[str] = None,
                working_dir: Optional[str] = None,
                kubernetes_auth: bool = True):
        """
        Initialize the Vault Integration Manager.
        
        Args:
            vault_addr: Vault server address (optional, defaults to VAULT_ADDR env var)
            vault_token: Vault token (optional, defaults to VAULT_TOKEN env var)
            working_dir: Working directory for Vault operations (optional)
            kubernetes_auth: Whether to use Kubernetes authentication (default: True)
        """
        self.vault_addr = vault_addr or os.environ.get("VAULT_ADDR", "http://vault:8200")
        self.vault_token = vault_token or os.environ.get("VAULT_TOKEN", "")
        self.working_dir = working_dir or tempfile.mkdtemp(prefix="vault_")
        self.kubernetes_auth = kubernetes_auth
        
        self.executor = VaultExecutor(
            self.vault_addr, 
            self.vault_token,
            self.working_dir
        )
        self.secret_manager = SecretManager(self.executor)
        self.auth_method_manager = AuthMethodManager(self.executor)
        self.policy_manager = PolicyManager(self.executor)
        self.role_manager = RoleManager(self.executor)
    
    def deploy_vault(self, namespace: str = "vault",
                    replicas: int = 1,
                    storage_class: Optional[str] = None) -> AgentResponse:
        """
        Deploy Vault to Kubernetes.
        
        Args:
            namespace: Kubernetes namespace (default: vault)
            replicas: Number of Vault replicas (default: 1)
            storage_class: Storage class for Vault (optional)
            
        Returns:
            AgentResponse: Deployment response
        """
        try:
            # Create namespace if it doesn't exist
            try:
                subprocess.run(
                    ["kubectl", "get", "namespace", namespace],
                    check=True,
                    capture_output=True
                )
            except subprocess.CalledProcessError:
                subprocess.run(
                    ["kubectl", "create", "namespace", namespace],
                    check=True,
                    capture_output=True
                )
            
            # Create Vault configuration
            vault_config = self._create_vault_config(replicas, storage_class)
            
            # Write Vault configuration to file
            vault_config_path = os.path.join(self.working_dir, "vault-config.yaml")
            with open(vault_config_path, "w") as f:
                f.write(vault_config)
            
            # Apply Vault configuration
            subprocess.run(
                ["kubectl", "apply", "-f", vault_config_path, "-n", namespace],
                check=True,
                capture_output=True
            )
            
            return AgentResponse(
                success=True,
                message=f"Vault deployed successfully to namespace {namespace}",
                data={
                    "namespace": namespace,
                    "replicas": replicas
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to deploy Vault: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to deploy Vault: {str(e)}",
                data={}
            )
    
    def _create_vault_config(self, replicas: int, storage_class: Optional[str]) -> str:
        """
        Create Vault configuration YAML.
        
        Args:
            replicas: Number of Vault replicas
            storage_class: Storage class for Vault
            
        Returns:
            str: Vault configuration YAML
        """
        storage_config = ""
        if storage_class:
            storage_config = f"""
      storageClass: {storage_class}
"""
        
        return f"""
apiVersion: v1
kind: ServiceAccount
metadata:
  name: vault
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: vault-server-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: system:auth-delegator
subjects:
- kind: ServiceAccount
  name: vault
  namespace: vault
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: vault-config
data:
  vault-config.json: |
    {{
      "listener": {{
        "tcp": {{
          "address": "0.0.0.0:8200",
          "tls_disable": 1
        }}
      }},
      "storage": {{
        "file": {{
          "path": "/vault/data"
        }}
      }},
      "ui": true
    }}
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: vault
spec:
  serviceName: vault
  replicas: {replicas}
  selector:
    matchLabels:
      app: vault
  template:
    metadata:
      labels:
        app: vault
    spec:
      serviceAccountName: vault
      containers:
      - name: vault
        image: vault:1.12.1
        ports:
        - containerPort: 8200
          name: vault-port
        - containerPort: 8201
          name: cluster-port
        env:
        - name: VAULT_LOCAL_CONFIG
          valueFrom:
            configMapKeyRef:
              name: vault-config
              key: vault-config.json
        - name: VAULT_DEV_ROOT_TOKEN_ID
          value: "root"
        - name: VAULT_DEV_LISTEN_ADDRESS
          value: "0.0.0.0:8200"
        volumeMounts:
        - name: vault-data
          mountPath: /vault/data
        securityContext:
          capabilities:
            add: ["IPC_LOCK"]
  volumeClaimTemplates:
  - metadata:
      name: vault-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 1Gi{storage_config}
---
apiVersion: v1
kind: Service
metadata:
  name: vault
spec:
  selector:
    app: vault
  ports:
  - name: vault-port
    port: 8200
    targetPort: 8200
  - name: cluster-port
    port: 8201
    targetPort: 8201
"""
    
    def initialize_vault(self, unseal_keys_file: Optional[str] = None) -> AgentResponse:
        """
        Initialize Vault.
        
        Args:
            unseal_keys_file: Path to file to store unseal keys (optional)
            
        Returns:
            AgentResponse: Initialization response
        """
        try:
            # Check if Vault is already initialized
            status = self.executor.run_vault_command(["status", "-format=json"])
            status = json.loads(status)
            
            if status.get("initialized", False):
                return AgentResponse(
                    success=True,
                    message="Vault is already initialized",
                    data=status
                )
            
            # Initialize Vault
            init_result = self.executor.run_vault_command([
                "operator", "init",
                "-key-shares=5",
                "-key-threshold=3",
                "-format=json"
            ])
            init_result = json.loads(init_result)
            
            # Store unseal keys if file is provided
            if unseal_keys_file:
                with open(unseal_keys_file, "w") as f:
                    json.dump(init_result, f, indent=2)
            
            # Update token
            self.vault_token = init_result["root_token"]
            self.executor.vault_token = init_result["root_token"]
            
            return AgentResponse(
                success=True,
                message="Vault initialized successfully",
                data=init_result
            )
        
        except Exception as e:
            logger.error(f"Failed to initialize Vault: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to initialize Vault: {str(e)}",
                data={}
            )
    
    def unseal_vault(self, unseal_keys: List[str]) -> AgentResponse:
        """
        Unseal Vault.
        
        Args:
            unseal_keys: Unseal keys
            
        Returns:
            AgentResponse: Unseal response
        """
        try:
            # Check if Vault is already unsealed
            status = self.executor.run_vault_command(["status", "-format=json"])
            status = json.loads(status)
            
            if not status.get("sealed", True):
                return AgentResponse(
                    success=True,
                    message="Vault is already unsealed",
                    data=status
                )
            
            # Unseal Vault
            for key in unseal_keys:
                unseal_result = self.executor.run_vault_command([
                    "operator", "unseal",
                    key
                ])
            
            # Check status after unseal
            status = self.executor.run_vault_command(["status", "-format=json"])
            status = json.loads(status)
            
            return AgentResponse(
                success=not status.get("sealed", True),
                message="Vault unsealed successfully" if not status.get("sealed", True) else "Failed to unseal Vault",
                data=status
            )
        
        except Exception as e:
            logger.error(f"Failed to unseal Vault: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to unseal Vault: {str(e)}",
                data={}
            )
    
    def enable_kubernetes_auth(self, path: str = "kubernetes") -> AgentResponse:
        """
        Enable Kubernetes authentication method.
        
        Args:
            path: Authentication path (default: kubernetes)
            
        Returns:
            AgentResponse: Authentication response
        """
        try:
            # Enable Kubernetes authentication
            self.auth_method_manager.enable_auth_method(
                auth_type="kubernetes",
                path=path
            )
            
            # Configure Kubernetes authentication
            kubernetes_host = "https://kubernetes.default.svc"
            
            # Get service account token
            with open("/var/run/secrets/kubernetes.io/serviceaccount/token", "r") as f:
                token = f.read()
            
            # Configure Kubernetes authentication
            self.executor.run_vault_command([
                "write", f"auth/{path}/config",
                f"kubernetes_host={kubernetes_host}",
                f"token_reviewer_jwt={token}",
                "kubernetes_ca_cert=@/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
            ])
            
            return AgentResponse(
                success=True,
                message=f"Kubernetes authentication enabled at path {path}",
                data={
                    "path": path
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to enable Kubernetes authentication: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to enable Kubernetes authentication: {str(e)}",
                data={}
            )
    
    def create_kubernetes_role(self, name: str,
                              namespace: str,
                              service_account: str,
                              policies: List[str],
                              path: str = "kubernetes") -> AgentResponse:
        """
        Create Kubernetes role.
        
        Args:
            name: Role name
            namespace: Kubernetes namespace
            service_account: Kubernetes service account
            policies: Vault policies
            path: Authentication path (default: kubernetes)
            
        Returns:
            AgentResponse: Role creation response
        """
        try:
            # Create Kubernetes role
            self.role_manager.create_kubernetes_role(
                name=name,
                namespace=namespace,
                service_account=service_account,
                policies=policies,
                path=path
            )
            
            return AgentResponse(
                success=True,
                message=f"Kubernetes role {name} created successfully",
                data={
                    "name": name,
                    "namespace": namespace,
                    "service_account": service_account,
                    "policies": policies,
                    "path": path
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to create Kubernetes role: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create Kubernetes role: {str(e)}",
                data={}
            )
    
    def create_policy(self, name: str, policy: str) -> AgentResponse:
        """
        Create Vault policy.
        
        Args:
            name: Policy name
            policy: Policy content
            
        Returns:
            AgentResponse: Policy creation response
        """
        try:
            # Create policy
            self.policy_manager.create_policy(
                name=name,
                policy=policy
            )
            
            return AgentResponse(
                success=True,
                message=f"Policy {name} created successfully",
                data={
                    "name": name
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to create policy: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create policy: {str(e)}",
                data={}
            )
    
    def enable_secrets_engine(self, engine: str, path: str) -> AgentResponse:
        """
        Enable secrets engine.
        
        Args:
            engine: Secrets engine type
            path: Secrets engine path
            
        Returns:
            AgentResponse: Secrets engine response
        """
        try:
            # Enable secrets engine
            self.executor.run_vault_command([
                "secrets", "enable",
                "-path", path,
                engine
            ])
            
            return AgentResponse(
                success=True,
                message=f"Secrets engine {engine} enabled at path {path}",
                data={
                    "engine": engine,
                    "path": path
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to enable secrets engine: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to enable secrets engine: {str(e)}",
                data={}
            )
    
    def write_secret(self, path: str, data: Dict[str, Any]) -> AgentResponse:
        """
        Write secret.
        
        Args:
            path: Secret path
            data: Secret data
            
        Returns:
            AgentResponse: Secret write response
        """
        try:
            # Write secret
            self.secret_manager.write_secret(
                path=path,
                data=data
            )
            
            return AgentResponse(
                success=True,
                message=f"Secret written to {path}",
                data={
                    "path": path
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to write secret: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to write secret: {str(e)}",
                data={}
            )
    
    def read_secret(self, path: str) -> AgentResponse:
        """
        Read secret.
        
        Args:
            path: Secret path
            
        Returns:
            AgentResponse: Secret read response
        """
        try:
            # Read secret
            secret = self.secret_manager.read_secret(path=path)
            
            return AgentResponse(
                success=True,
                message=f"Secret read from {path}",
                data=secret
            )
        
        except Exception as e:
            logger.error(f"Failed to read secret: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to read secret: {str(e)}",
                data={}
            )
    
    def delete_secret(self, path: str) -> AgentResponse:
        """
        Delete secret.
        
        Args:
            path: Secret path
            
        Returns:
            AgentResponse: Secret delete response
        """
        try:
            # Delete secret
            self.secret_manager.delete_secret(path=path)
            
            return AgentResponse(
                success=True,
                message=f"Secret deleted from {path}",
                data={
                    "path": path
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to delete secret: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to delete secret: {str(e)}",
                data={}
            )
    
    def to_mcp_context(self) -> MCPContext:
        """
        Convert Vault integration information to MCP context.
        
        Returns:
            MCPContext: MCP context with Vault integration information
        """
        return MCPContext(
            context_type="vault_integration",
            vault_addr=self.vault_addr,
            working_dir=self.working_dir
        )


class SecretManager:
    """
    Manages Vault secrets.
    
    This class provides methods for creating, reading, updating, and deleting Vault secrets.
    """
    
    def __init__(self, executor: 'VaultExecutor'):
        """
        Initialize the Secret Manager.
        
        Args:
            executor: Vault executor
        """
        self.executor = executor
    
    def write_secret(self, path: str, data: Dict[str, Any]) -> None:
        """
        Write secret.
        
        Args:
            path: Secret path
            data: Secret data
        """
        # Prepare command arguments
        args = ["kv", "put", path]
        
        # Add data arguments
        for key, value in data.items():
            args.append(f"{key}={value}")
        
        # Write secret
        self.executor.run_vault_command(args)
    
    def read_secret(self, path: str) -> Dict[str, Any]:
        """
        Read secret.
        
        Args:
            path: Secret path
            
        Returns:
            Dict[str, Any]: Secret data
        """
        # Read secret
        result = self.executor.run_vault_command([
            "kv", "get",
            "-format=json",
            path
        ])
        
        # Parse result
        result = json.loads(result)
        
        return result.get("data", {}).get("data", {})
    
    def delete_secret(self, path: str) -> None:
        """
        Delete secret.
        
        Args:
            path: Secret path
        """
        # Delete secret
        self.executor.run_vault_command([
            "kv", "delete",
            path
        ])


class AuthMethodManager:
    """
    Manages Vault authentication methods.
    
    This class provides methods for enabling, configuring, and disabling Vault authentication methods.
    """
    
    def __init__(self, executor: 'VaultExecutor'):
        """
        Initialize the Auth Method Manager.
        
        Args:
            executor: Vault executor
        """
        self.executor = executor
    
    def enable_auth_method(self, auth_type: str, path: Optional[str] = None) -> None:
        """
        Enable authentication method.
        
        Args:
            auth_type: Authentication method type
            path: Authentication method path (optional, defaults to auth_type)
        """
        # Prepare command arguments
        args = ["auth", "enable"]
        
        # Add path if provided
        if path:
            args.extend(["-path", path])
        
        # Add auth type
        args.append(auth_type)
        
        # Enable auth method
        self.executor.run_vault_command(args)
    
    def disable_auth_method(self, path: str) -> None:
        """
        Disable authentication method.
        
        Args:
            path: Authentication method path
        """
        # Disable auth method
        self.executor.run_vault_command([
            "auth", "disable",
            path
        ])


class PolicyManager:
    """
    Manages Vault policies.
    
    This class provides methods for creating, updating, and deleting Vault policies.
    """
    
    def __init__(self, executor: 'VaultExecutor'):
        """
        Initialize the Policy Manager.
        
        Args:
            executor: Vault executor
        """
        self.executor = executor
    
    def create_policy(self, name: str, policy: str) -> None:
        """
        Create policy.
        
        Args:
            name: Policy name
            policy: Policy content
        """
        # Write policy to file
        policy_path = os.path.join(self.executor.working_dir, f"{name}.hcl")
        with open(policy_path, "w") as f:
            f.write(policy)
        
        # Create policy
        self.executor.run_vault_command([
            "policy", "write",
            name,
            policy_path
        ])
    
    def delete_policy(self, name: str) -> None:
        """
        Delete policy.
        
        Args:
            name: Policy name
        """
        # Delete policy
        self.executor.run_vault_command([
            "policy", "delete",
            name
        ])


class RoleManager:
    """
    Manages Vault roles.
    
    This class provides methods for creating, updating, and deleting Vault roles.
    """
    
    def __init__(self, executor: 'VaultExecutor'):
        """
        Initialize the Role Manager.
        
        Args:
            executor: Vault executor
        """
        self.executor = executor
    
    def create_kubernetes_role(self, name: str,
                              namespace: str,
                              service_account: str,
                              policies: List[str],
                              path: str = "kubernetes") -> None:
        """
        Create Kubernetes role.
        
        Args:
            name: Role name
            namespace: Kubernetes namespace
            service_account: Kubernetes service account
            policies: Vault policies
            path: Authentication path (default: kubernetes)
        """
        # Prepare command arguments
        args = [
            "write", f"auth/{path}/role/{name}",
            f"bound_service_account_names={service_account}",
            f"bound_service_account_namespaces={namespace}",
            f"policies={','.join(policies)}"
        ]
        
        # Create role
        self.executor.run_vault_command(args)
    
    def delete_kubernetes_role(self, name: str, path: str = "kubernetes") -> None:
        """
        Delete Kubernetes role.
        
        Args:
            name: Role name
            path: Authentication path (default: kubernetes)
        """
        # Delete role
        self.executor.run_vault_command([
            "delete", f"auth/{path}/role/{name}"
        ])


class VaultExecutor:
    """
    Executes Vault API calls and commands.
    
    This class provides methods for executing Vault API calls and commands
    and handling their output.
    """
    
    def __init__(self, vault_addr: str,
                vault_token: str,
                working_dir: str):
        """
        Initialize the Vault Executor.
        
        Args:
            vault_addr: Vault server address
            vault_token: Vault token
            working_dir: Working directory for Vault operations
        """
        self.vault_addr = vault_addr
        self.vault_token = vault_token
        self.working_dir = working_dir
    
    def run_vault_command(self, args: List[str], check: bool = True) -> str:
        """
        Run a Vault command.
        
        Args:
            args: Command arguments
            check: Whether to check for command success
            
        Returns:
            str: Command output
            
        Raises:
            Exception: If the command fails and check is True
        """
        cmd = ["vault"] + args
        logger.info(f"Running Vault command: {' '.join(cmd)}")
        
        env = os.environ.copy()
        env["VAULT_ADDR"] = self.vault_addr
        env["VAULT_TOKEN"] = self.vault_token
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                check=check,
                env=env
            )
            
            return result.stdout
        
        except subprocess.CalledProcessError as e:
            error_message = f"Vault command failed: {e.stderr}"
            logger.error(error_message)
            
            if check:
                raise Exception(error_message)
            
            return e.stderr
    
    def make_api_request(self, method: str,
                        path: str,
                        data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a Vault API request.
        
        Args:
            method: HTTP method
            path: API path
            data: Request data (optional)
            
        Returns:
            Dict[str, Any]: API response
            
        Raises:
            Exception: If the API request fails
        """
        url = f"{self.vault_addr}/v1/{path}"
        headers = {
            "X-Vault-Token": self.vault_token
        }
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                raise Exception(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            
            return response.json()
        
        except Exception as e:
            error_message = f"Vault API request failed: {str(e)}"
            logger.error(error_message)
            raise Exception(error_message)
