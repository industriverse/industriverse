"""
Cert Manager Integration Manager

This module provides integration with Cert Manager for the Deployment Operations Layer.
It handles deployment, configuration, and management of Cert Manager resources
including Certificates, Issuers, ClusterIssuers, and CertificateRequests.

Classes:
    CertManagerIntegrationManager: Manages Cert Manager integration
    CertificateManager: Manages Certificate resources
    IssuerManager: Manages Issuer resources
    ClusterIssuerManager: Manages ClusterIssuer resources
    CertificateRequestManager: Manages CertificateRequest resources
    CertManagerExecutor: Executes Cert Manager API calls
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

class CertManagerIntegrationManager:
    """
    Manages Cert Manager integration for the Deployment Operations Layer.
    
    This class provides a unified interface for interacting with Cert Manager,
    handling Certificates, Issuers, ClusterIssuers, and CertificateRequests.
    """
    
    def __init__(self, kubectl_binary_path: Optional[str] = None,
                working_dir: Optional[str] = None,
                namespace: str = "cert-manager"):
        """
        Initialize the Cert Manager Integration Manager.
        
        Args:
            kubectl_binary_path: Path to kubectl binary (optional, defaults to 'kubectl' in PATH)
            working_dir: Working directory for Cert Manager operations (optional)
            namespace: Kubernetes namespace for Cert Manager (default: cert-manager)
        """
        self.kubectl_binary = kubectl_binary_path or "kubectl"
        self.working_dir = working_dir or tempfile.mkdtemp(prefix="cert_manager_")
        self.namespace = namespace
        
        self.executor = CertManagerExecutor(
            self.kubectl_binary, 
            self.working_dir,
            self.namespace
        )
        self.certificate_manager = CertificateManager(self.executor)
        self.issuer_manager = IssuerManager(self.executor)
        self.cluster_issuer_manager = ClusterIssuerManager(self.executor)
        self.certificate_request_manager = CertificateRequestManager(self.executor)
    
    def deploy_cert_manager(self, namespace: Optional[str] = None) -> AgentResponse:
        """
        Deploy Cert Manager to Kubernetes.
        
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
            
            # Deploy Cert Manager CRDs
            self._deploy_cert_manager_crds()
            
            # Deploy Cert Manager
            self._deploy_cert_manager_deployment(namespace)
            
            return AgentResponse(
                success=True,
                message=f"Cert Manager deployed successfully to namespace {namespace}",
                data={
                    "namespace": namespace
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to deploy Cert Manager: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to deploy Cert Manager: {str(e)}",
                data={}
            )
    
    def _deploy_cert_manager_crds(self) -> None:
        """
        Deploy Cert Manager CRDs.
        """
        # Define CRD URL
        crd_url = "https://github.com/cert-manager/cert-manager/releases/download/v1.11.0/cert-manager.crds.yaml"
        
        # Download CRDs
        crd_path = os.path.join(self.working_dir, "cert-manager-crds.yaml")
        response = requests.get(crd_url)
        with open(crd_path, "w") as f:
            f.write(response.text)
        
        # Apply CRDs
        self.executor.run_kubectl_command(["apply", "-f", crd_path])
    
    def _deploy_cert_manager_deployment(self, namespace: str) -> None:
        """
        Deploy Cert Manager deployment.
        
        Args:
            namespace: Kubernetes namespace
        """
        # Create Cert Manager deployment YAML
        cert_manager_yaml = f"""
apiVersion: v1
kind: ServiceAccount
metadata:
  name: cert-manager
  namespace: {namespace}
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cert-manager
  namespace: {namespace}
  labels:
    app: cert-manager
spec:
  replicas: 1
  selector:
    matchLabels:
      app: cert-manager
  template:
    metadata:
      labels:
        app: cert-manager
    spec:
      serviceAccountName: cert-manager
      containers:
      - name: cert-manager
        image: quay.io/jetstack/cert-manager-controller:v1.11.0
        args:
        - --v=2
        - --cluster-resource-namespace=$(POD_NAMESPACE)
        - --leader-election-namespace=$(POD_NAMESPACE)
        env:
        - name: POD_NAMESPACE
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: cert-manager-cainjector
  namespace: {namespace}
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cert-manager-cainjector
  namespace: {namespace}
  labels:
    app: cainjector
spec:
  replicas: 1
  selector:
    matchLabels:
      app: cainjector
  template:
    metadata:
      labels:
        app: cainjector
    spec:
      serviceAccountName: cert-manager-cainjector
      containers:
      - name: cert-manager-cainjector
        image: quay.io/jetstack/cert-manager-cainjector:v1.11.0
        args:
        - --v=2
        - --leader-election-namespace=$(POD_NAMESPACE)
        env:
        - name: POD_NAMESPACE
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: cert-manager-webhook
  namespace: {namespace}
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cert-manager-webhook
  namespace: {namespace}
  labels:
    app: webhook
spec:
  replicas: 1
  selector:
    matchLabels:
      app: webhook
  template:
    metadata:
      labels:
        app: webhook
    spec:
      serviceAccountName: cert-manager-webhook
      containers:
      - name: cert-manager-webhook
        image: quay.io/jetstack/cert-manager-webhook:v1.11.0
        args:
        - --v=2
        - --secure-port=10250
        - --dynamic-serving-ca-secret-namespace=$(POD_NAMESPACE)
        - --dynamic-serving-ca-secret-name=cert-manager-webhook-ca
        - --dynamic-serving-dns-names=cert-manager-webhook,cert-manager-webhook.{namespace},cert-manager-webhook.{namespace}.svc
        env:
        - name: POD_NAMESPACE
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
        ports:
        - name: https
          containerPort: 10250
---
apiVersion: v1
kind: Service
metadata:
  name: cert-manager-webhook
  namespace: {namespace}
spec:
  selector:
    app: webhook
  ports:
  - name: https
    port: 443
    targetPort: https
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: cert-manager
rules:
- apiGroups: ["cert-manager.io"]
  resources: ["certificates", "certificaterequests", "issuers", "clusterissuers"]
  verbs: ["*"]
- apiGroups: [""]
  resources: ["configmaps", "secrets", "events", "services", "pods"]
  verbs: ["*"]
- apiGroups: ["networking.k8s.io"]
  resources: ["ingresses"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["networking.k8s.io"]
  resources: ["ingresses/finalizers"]
  verbs: ["update"]
- apiGroups: [""]
  resources: ["endpoints"]
  verbs: ["get", "list", "watch", "create", "update", "patch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: cert-manager
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cert-manager
subjects:
- kind: ServiceAccount
  name: cert-manager
  namespace: {namespace}
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: cert-manager-cainjector
rules:
- apiGroups: ["cert-manager.io"]
  resources: ["certificates"]
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["get", "list", "watch", "update"]
- apiGroups: ["admissionregistration.k8s.io"]
  resources: ["validatingwebhookconfigurations", "mutatingwebhookconfigurations"]
  verbs: ["get", "list", "watch", "update"]
- apiGroups: ["apiregistration.k8s.io"]
  resources: ["apiservices"]
  verbs: ["get", "list", "watch", "update"]
- apiGroups: ["apiextensions.k8s.io"]
  resources: ["customresourcedefinitions"]
  verbs: ["get", "list", "watch", "update"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: cert-manager-cainjector
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cert-manager-cainjector
subjects:
- kind: ServiceAccount
  name: cert-manager-cainjector
  namespace: {namespace}
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: cert-manager-webhook
rules:
- apiGroups: ["cert-manager.io"]
  resources: ["certificates", "certificaterequests", "issuers", "clusterissuers"]
  verbs: ["create", "update", "patch"]
- apiGroups: ["cert-manager.io"]
  resources: ["certificates/status", "certificaterequests/status", "issuers/status", "clusterissuers/status"]
  verbs: ["update", "patch"]
- apiGroups: ["admissionregistration.k8s.io"]
  resources: ["validatingwebhookconfigurations", "mutatingwebhookconfigurations"]
  verbs: ["create", "update", "patch"]
- apiGroups: ["apiregistration.k8s.io"]
  resources: ["apiservices"]
  verbs: ["create", "update", "patch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: cert-manager-webhook
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cert-manager-webhook
subjects:
- kind: ServiceAccount
  name: cert-manager-webhook
  namespace: {namespace}
"""
        
        # Write Cert Manager deployment YAML to file
        cert_manager_path = os.path.join(self.working_dir, "cert-manager.yaml")
        with open(cert_manager_path, "w") as f:
            f.write(cert_manager_yaml)
        
        # Apply Cert Manager deployment
        self.executor.run_kubectl_command(["apply", "-f", cert_manager_path])
    
    def create_issuer(self, name: str, 
                     namespace: str,
                     issuer_type: str,
                     issuer_config: Dict[str, Any]) -> AgentResponse:
        """
        Create an Issuer resource.
        
        Args:
            name: Issuer name
            namespace: Issuer namespace
            issuer_type: Issuer type (e.g., 'SelfSigned', 'CA', 'ACME')
            issuer_config: Issuer configuration
            
        Returns:
            AgentResponse: Creation response
        """
        try:
            result = self.issuer_manager.create_issuer(
                name=name,
                namespace=namespace,
                issuer_type=issuer_type,
                issuer_config=issuer_config
            )
            
            return AgentResponse(
                success=True,
                message=f"Issuer {name} created successfully in namespace {namespace}",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create Issuer: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create Issuer: {str(e)}",
                data={}
            )
    
    def create_cluster_issuer(self, name: str, 
                             issuer_type: str,
                             issuer_config: Dict[str, Any]) -> AgentResponse:
        """
        Create a ClusterIssuer resource.
        
        Args:
            name: ClusterIssuer name
            issuer_type: Issuer type (e.g., 'SelfSigned', 'CA', 'ACME')
            issuer_config: Issuer configuration
            
        Returns:
            AgentResponse: Creation response
        """
        try:
            result = self.cluster_issuer_manager.create_cluster_issuer(
                name=name,
                issuer_type=issuer_type,
                issuer_config=issuer_config
            )
            
            return AgentResponse(
                success=True,
                message=f"ClusterIssuer {name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create ClusterIssuer: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create ClusterIssuer: {str(e)}",
                data={}
            )
    
    def create_certificate(self, name: str, 
                          namespace: str,
                          issuer_ref: Dict[str, str],
                          common_name: Optional[str] = None,
                          dns_names: Optional[List[str]] = None,
                          secret_name: Optional[str] = None,
                          duration: str = "2160h",  # 90 days
                          renew_before: str = "360h") -> AgentResponse:  # 15 days
        """
        Create a Certificate resource.
        
        Args:
            name: Certificate name
            namespace: Certificate namespace
            issuer_ref: Issuer reference (e.g., {'name': 'my-issuer', 'kind': 'Issuer'})
            common_name: Common name (optional)
            dns_names: DNS names (optional)
            secret_name: Secret name (optional, defaults to certificate name)
            duration: Certificate duration (default: 2160h, 90 days)
            renew_before: Certificate renewal time (default: 360h, 15 days)
            
        Returns:
            AgentResponse: Creation response
        """
        try:
            result = self.certificate_manager.create_certificate(
                name=name,
                namespace=namespace,
                issuer_ref=issuer_ref,
                common_name=common_name,
                dns_names=dns_names,
                secret_name=secret_name or name,
                duration=duration,
                renew_before=renew_before
            )
            
            return AgentResponse(
                success=True,
                message=f"Certificate {name} created successfully in namespace {namespace}",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create Certificate: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create Certificate: {str(e)}",
                data={}
            )
    
    def create_self_signed_issuer(self, name: str, namespace: str) -> AgentResponse:
        """
        Create a self-signed Issuer resource.
        
        Args:
            name: Issuer name
            namespace: Issuer namespace
            
        Returns:
            AgentResponse: Creation response
        """
        try:
            issuer_config = {
                "selfSigned": {}
            }
            
            result = self.issuer_manager.create_issuer(
                name=name,
                namespace=namespace,
                issuer_type="SelfSigned",
                issuer_config=issuer_config
            )
            
            return AgentResponse(
                success=True,
                message=f"Self-signed Issuer {name} created successfully in namespace {namespace}",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create self-signed Issuer: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create self-signed Issuer: {str(e)}",
                data={}
            )
    
    def create_acme_issuer(self, name: str, 
                          namespace: str,
                          email: str,
                          server: str,
                          solver_type: str,
                          solver_config: Dict[str, Any]) -> AgentResponse:
        """
        Create an ACME Issuer resource.
        
        Args:
            name: Issuer name
            namespace: Issuer namespace
            email: ACME email
            server: ACME server URL
            solver_type: ACME solver type (e.g., 'http01', 'dns01')
            solver_config: ACME solver configuration
            
        Returns:
            AgentResponse: Creation response
        """
        try:
            # Create private key secret for ACME account
            private_key_secret_name = f"{name}-private-key"
            private_key_secret = {
                "apiVersion": "v1",
                "kind": "Secret",
                "metadata": {
                    "name": private_key_secret_name,
                    "namespace": namespace
                },
                "type": "Opaque"
            }
            
            # Write private key secret to file
            private_key_secret_path = os.path.join(self.working_dir, f"{private_key_secret_name}.yaml")
            with open(private_key_secret_path, "w") as f:
                yaml.dump(private_key_secret, f)
            
            # Apply private key secret
            self.executor.run_kubectl_command(["apply", "-f", private_key_secret_path])
            
            # Create ACME issuer configuration
            issuer_config = {
                "acme": {
                    "email": email,
                    "server": server,
                    "privateKeySecretRef": {
                        "name": private_key_secret_name
                    },
                    "solvers": [
                        {
                            solver_type: solver_config
                        }
                    ]
                }
            }
            
            result = self.issuer_manager.create_issuer(
                name=name,
                namespace=namespace,
                issuer_type="ACME",
                issuer_config=issuer_config
            )
            
            return AgentResponse(
                success=True,
                message=f"ACME Issuer {name} created successfully in namespace {namespace}",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create ACME Issuer: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create ACME Issuer: {str(e)}",
                data={}
            )
    
    def to_mcp_context(self) -> MCPContext:
        """
        Convert Cert Manager integration information to MCP context.
        
        Returns:
            MCPContext: MCP context with Cert Manager integration information
        """
        return MCPContext(
            context_type="cert_manager_integration",
            namespace=self.namespace,
            working_dir=self.working_dir
        )


class CertificateManager:
    """
    Manages Certificate resources.
    
    This class provides methods for creating, updating, and deleting Certificate resources.
    """
    
    def __init__(self, executor: 'CertManagerExecutor'):
        """
        Initialize the Certificate Manager.
        
        Args:
            executor: Cert Manager executor
        """
        self.executor = executor
    
    def create_certificate(self, name: str, 
                          namespace: str,
                          issuer_ref: Dict[str, str],
                          common_name: Optional[str] = None,
                          dns_names: Optional[List[str]] = None,
                          secret_name: Optional[str] = None,
                          duration: str = "2160h",  # 90 days
                          renew_before: str = "360h") -> Dict[str, Any]:  # 15 days
        """
        Create a Certificate resource.
        
        Args:
            name: Certificate name
            namespace: Certificate namespace
            issuer_ref: Issuer reference (e.g., {'name': 'my-issuer', 'kind': 'Issuer'})
            common_name: Common name (optional)
            dns_names: DNS names (optional)
            secret_name: Secret name (optional, defaults to certificate name)
            duration: Certificate duration (default: 2160h, 90 days)
            renew_before: Certificate renewal time (default: 360h, 15 days)
            
        Returns:
            Dict[str, Any]: Created Certificate
        """
        # Create Certificate
        certificate = {
            "apiVersion": "cert-manager.io/v1",
            "kind": "Certificate",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "secretName": secret_name or name,
                "issuerRef": issuer_ref,
                "duration": duration,
                "renewBefore": renew_before
            }
        }
        
        # Add common name if provided
        if common_name:
            certificate["spec"]["commonName"] = common_name
        
        # Add DNS names if provided
        if dns_names:
            certificate["spec"]["dnsNames"] = dns_names
        
        # Write Certificate to file
        certificate_path = os.path.join(self.executor.working_dir, f"certificate-{name}.yaml")
        with open(certificate_path, "w") as f:
            yaml.dump(certificate, f)
        
        # Apply Certificate
        self.executor.run_kubectl_command(["apply", "-f", certificate_path])
        
        # Get created Certificate
        result = self.executor.run_kubectl_command([
            "get", "certificate", name, "-n", namespace, "-o", "json"
        ])
        
        return json.loads(result)
    
    def update_certificate(self, name: str, 
                          namespace: str,
                          issuer_ref: Dict[str, str],
                          common_name: Optional[str] = None,
                          dns_names: Optional[List[str]] = None,
                          secret_name: Optional[str] = None,
                          duration: str = "2160h",  # 90 days
                          renew_before: str = "360h") -> Dict[str, Any]:  # 15 days
        """
        Update a Certificate resource.
        
        Args:
            name: Certificate name
            namespace: Certificate namespace
            issuer_ref: Issuer reference (e.g., {'name': 'my-issuer', 'kind': 'Issuer'})
            common_name: Common name (optional)
            dns_names: DNS names (optional)
            secret_name: Secret name (optional, defaults to certificate name)
            duration: Certificate duration (default: 2160h, 90 days)
            renew_before: Certificate renewal time (default: 360h, 15 days)
            
        Returns:
            Dict[str, Any]: Updated Certificate
        """
        # Get existing Certificate
        try:
            existing_certificate = self.executor.run_kubectl_command([
                "get", "certificate", name, "-n", namespace, "-o", "json"
            ])
            existing_certificate = json.loads(existing_certificate)
        except Exception:
            # Certificate doesn't exist, create it
            return self.create_certificate(
                name=name,
                namespace=namespace,
                issuer_ref=issuer_ref,
                common_name=common_name,
                dns_names=dns_names,
                secret_name=secret_name,
                duration=duration,
                renew_before=renew_before
            )
        
        # Update Certificate
        certificate = {
            "apiVersion": "cert-manager.io/v1",
            "kind": "Certificate",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "secretName": secret_name or name,
                "issuerRef": issuer_ref,
                "duration": duration,
                "renewBefore": renew_before
            }
        }
        
        # Add common name if provided
        if common_name:
            certificate["spec"]["commonName"] = common_name
        
        # Add DNS names if provided
        if dns_names:
            certificate["spec"]["dnsNames"] = dns_names
        
        # Write Certificate to file
        certificate_path = os.path.join(self.executor.working_dir, f"certificate-{name}.yaml")
        with open(certificate_path, "w") as f:
            yaml.dump(certificate, f)
        
        # Apply Certificate
        self.executor.run_kubectl_command(["apply", "-f", certificate_path])
        
        # Get updated Certificate
        result = self.executor.run_kubectl_command([
            "get", "certificate", name, "-n", namespace, "-o", "json"
        ])
        
        return json.loads(result)
    
    def delete_certificate(self, name: str, namespace: str) -> None:
        """
        Delete a Certificate resource.
        
        Args:
            name: Certificate name
            namespace: Certificate namespace
        """
        self.executor.run_kubectl_command([
            "delete", "certificate", name, "-n", namespace
        ])


class IssuerManager:
    """
    Manages Issuer resources.
    
    This class provides methods for creating, updating, and deleting Issuer resources.
    """
    
    def __init__(self, executor: 'CertManagerExecutor'):
        """
        Initialize the Issuer Manager.
        
        Args:
            executor: Cert Manager executor
        """
        self.executor = executor
    
    def create_issuer(self, name: str, 
                     namespace: str,
                     issuer_type: str,
                     issuer_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an Issuer resource.
        
        Args:
            name: Issuer name
            namespace: Issuer namespace
            issuer_type: Issuer type (e.g., 'SelfSigned', 'CA', 'ACME')
            issuer_config: Issuer configuration
            
        Returns:
            Dict[str, Any]: Created Issuer
        """
        # Create Issuer
        issuer = {
            "apiVersion": "cert-manager.io/v1",
            "kind": "Issuer",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": issuer_config
        }
        
        # Write Issuer to file
        issuer_path = os.path.join(self.executor.working_dir, f"issuer-{name}.yaml")
        with open(issuer_path, "w") as f:
            yaml.dump(issuer, f)
        
        # Apply Issuer
        self.executor.run_kubectl_command(["apply", "-f", issuer_path])
        
        # Get created Issuer
        result = self.executor.run_kubectl_command([
            "get", "issuer", name, "-n", namespace, "-o", "json"
        ])
        
        return json.loads(result)
    
    def update_issuer(self, name: str, 
                     namespace: str,
                     issuer_type: str,
                     issuer_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an Issuer resource.
        
        Args:
            name: Issuer name
            namespace: Issuer namespace
            issuer_type: Issuer type (e.g., 'SelfSigned', 'CA', 'ACME')
            issuer_config: Issuer configuration
            
        Returns:
            Dict[str, Any]: Updated Issuer
        """
        # Get existing Issuer
        try:
            existing_issuer = self.executor.run_kubectl_command([
                "get", "issuer", name, "-n", namespace, "-o", "json"
            ])
            existing_issuer = json.loads(existing_issuer)
        except Exception:
            # Issuer doesn't exist, create it
            return self.create_issuer(
                name=name,
                namespace=namespace,
                issuer_type=issuer_type,
                issuer_config=issuer_config
            )
        
        # Update Issuer
        issuer = {
            "apiVersion": "cert-manager.io/v1",
            "kind": "Issuer",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": issuer_config
        }
        
        # Write Issuer to file
        issuer_path = os.path.join(self.executor.working_dir, f"issuer-{name}.yaml")
        with open(issuer_path, "w") as f:
            yaml.dump(issuer, f)
        
        # Apply Issuer
        self.executor.run_kubectl_command(["apply", "-f", issuer_path])
        
        # Get updated Issuer
        result = self.executor.run_kubectl_command([
            "get", "issuer", name, "-n", namespace, "-o", "json"
        ])
        
        return json.loads(result)
    
    def delete_issuer(self, name: str, namespace: str) -> None:
        """
        Delete an Issuer resource.
        
        Args:
            name: Issuer name
            namespace: Issuer namespace
        """
        self.executor.run_kubectl_command([
            "delete", "issuer", name, "-n", namespace
        ])


class ClusterIssuerManager:
    """
    Manages ClusterIssuer resources.
    
    This class provides methods for creating, updating, and deleting ClusterIssuer resources.
    """
    
    def __init__(self, executor: 'CertManagerExecutor'):
        """
        Initialize the ClusterIssuer Manager.
        
        Args:
            executor: Cert Manager executor
        """
        self.executor = executor
    
    def create_cluster_issuer(self, name: str, 
                             issuer_type: str,
                             issuer_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a ClusterIssuer resource.
        
        Args:
            name: ClusterIssuer name
            issuer_type: Issuer type (e.g., 'SelfSigned', 'CA', 'ACME')
            issuer_config: Issuer configuration
            
        Returns:
            Dict[str, Any]: Created ClusterIssuer
        """
        # Create ClusterIssuer
        cluster_issuer = {
            "apiVersion": "cert-manager.io/v1",
            "kind": "ClusterIssuer",
            "metadata": {
                "name": name
            },
            "spec": issuer_config
        }
        
        # Write ClusterIssuer to file
        cluster_issuer_path = os.path.join(self.executor.working_dir, f"cluster-issuer-{name}.yaml")
        with open(cluster_issuer_path, "w") as f:
            yaml.dump(cluster_issuer, f)
        
        # Apply ClusterIssuer
        self.executor.run_kubectl_command(["apply", "-f", cluster_issuer_path])
        
        # Get created ClusterIssuer
        result = self.executor.run_kubectl_command([
            "get", "clusterissuer", name, "-o", "json"
        ])
        
        return json.loads(result)
    
    def update_cluster_issuer(self, name: str, 
                             issuer_type: str,
                             issuer_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a ClusterIssuer resource.
        
        Args:
            name: ClusterIssuer name
            issuer_type: Issuer type (e.g., 'SelfSigned', 'CA', 'ACME')
            issuer_config: Issuer configuration
            
        Returns:
            Dict[str, Any]: Updated ClusterIssuer
        """
        # Get existing ClusterIssuer
        try:
            existing_cluster_issuer = self.executor.run_kubectl_command([
                "get", "clusterissuer", name, "-o", "json"
            ])
            existing_cluster_issuer = json.loads(existing_cluster_issuer)
        except Exception:
            # ClusterIssuer doesn't exist, create it
            return self.create_cluster_issuer(
                name=name,
                issuer_type=issuer_type,
                issuer_config=issuer_config
            )
        
        # Update ClusterIssuer
        cluster_issuer = {
            "apiVersion": "cert-manager.io/v1",
            "kind": "ClusterIssuer",
            "metadata": {
                "name": name
            },
            "spec": issuer_config
        }
        
        # Write ClusterIssuer to file
        cluster_issuer_path = os.path.join(self.executor.working_dir, f"cluster-issuer-{name}.yaml")
        with open(cluster_issuer_path, "w") as f:
            yaml.dump(cluster_issuer, f)
        
        # Apply ClusterIssuer
        self.executor.run_kubectl_command(["apply", "-f", cluster_issuer_path])
        
        # Get updated ClusterIssuer
        result = self.executor.run_kubectl_command([
            "get", "clusterissuer", name, "-o", "json"
        ])
        
        return json.loads(result)
    
    def delete_cluster_issuer(self, name: str) -> None:
        """
        Delete a ClusterIssuer resource.
        
        Args:
            name: ClusterIssuer name
        """
        self.executor.run_kubectl_command([
            "delete", "clusterissuer", name
        ])


class CertificateRequestManager:
    """
    Manages CertificateRequest resources.
    
    This class provides methods for creating, updating, and deleting CertificateRequest resources.
    """
    
    def __init__(self, executor: 'CertManagerExecutor'):
        """
        Initialize the CertificateRequest Manager.
        
        Args:
            executor: Cert Manager executor
        """
        self.executor = executor
    
    def create_certificate_request(self, name: str, 
                                  namespace: str,
                                  issuer_ref: Dict[str, str],
                                  csr: str) -> Dict[str, Any]:
        """
        Create a CertificateRequest resource.
        
        Args:
            name: CertificateRequest name
            namespace: CertificateRequest namespace
            issuer_ref: Issuer reference (e.g., {'name': 'my-issuer', 'kind': 'Issuer'})
            csr: Certificate Signing Request (base64-encoded)
            
        Returns:
            Dict[str, Any]: Created CertificateRequest
        """
        # Create CertificateRequest
        certificate_request = {
            "apiVersion": "cert-manager.io/v1",
            "kind": "CertificateRequest",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "issuerRef": issuer_ref,
                "request": csr
            }
        }
        
        # Write CertificateRequest to file
        certificate_request_path = os.path.join(self.executor.working_dir, f"certificate-request-{name}.yaml")
        with open(certificate_request_path, "w") as f:
            yaml.dump(certificate_request, f)
        
        # Apply CertificateRequest
        self.executor.run_kubectl_command(["apply", "-f", certificate_request_path])
        
        # Get created CertificateRequest
        result = self.executor.run_kubectl_command([
            "get", "certificaterequest", name, "-n", namespace, "-o", "json"
        ])
        
        return json.loads(result)
    
    def delete_certificate_request(self, name: str, namespace: str) -> None:
        """
        Delete a CertificateRequest resource.
        
        Args:
            name: CertificateRequest name
            namespace: CertificateRequest namespace
        """
        self.executor.run_kubectl_command([
            "delete", "certificaterequest", name, "-n", namespace
        ])


class CertManagerExecutor:
    """
    Executes Cert Manager API calls and kubectl commands.
    
    This class provides methods for executing Cert Manager API calls and kubectl commands
    and handling their output.
    """
    
    def __init__(self, kubectl_binary: str,
                working_dir: str,
                namespace: str):
        """
        Initialize the Cert Manager Executor.
        
        Args:
            kubectl_binary: Path to kubectl binary
            working_dir: Working directory for Cert Manager operations
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
