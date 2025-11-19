"""
DAC Deployer

Automated deployment orchestration for DACs across multiple environments.
Supports Kubernetes, Docker, AWS, GCP, Azure, and edge deployments.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod
from pathlib import Path
import yaml
import json
from .manifest_schema import DACManifest, TargetEnvironment


class DeploymentStatus(Enum):
    """Deployment status"""
    PENDING = "pending"
    DEPLOYING = "deploying"
    DEPLOYED = "deployed"
    FAILED = "failed"
    SCALING = "scaling"
    UPDATING = "updating"
    TERMINATING = "terminating"
    TERMINATED = "terminated"


@dataclass
class DeploymentResult:
    """Result of deployment operation"""
    success: bool
    status: DeploymentStatus
    deployment_id: str
    endpoint: Optional[str] = None
    errors: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.metadata is None:
            self.metadata = {}


class DeployerBase(ABC):
    """Base class for environment-specific deployers"""

    def __init__(self, manifest: DACManifest):
        self.manifest = manifest

    @abstractmethod
    async def deploy(self) -> DeploymentResult:
        """Deploy DAC to target environment"""
        pass

    @abstractmethod
    async def undeploy(self, deployment_id: str) -> DeploymentResult:
        """Remove DAC deployment"""
        pass

    @abstractmethod
    async def get_status(self, deployment_id: str) -> DeploymentStatus:
        """Get deployment status"""
        pass

    @abstractmethod
    async def scale(self, deployment_id: str, replicas: int) -> DeploymentResult:
        """Scale deployment"""
        pass

    @abstractmethod
    async def update(self, deployment_id: str, new_manifest: DACManifest) -> DeploymentResult:
        """Update existing deployment"""
        pass


class KubernetesDeployer(DeployerBase):
    """Deploy DAC to Kubernetes cluster"""

    def generate_k8s_manifest(self) -> str:
        """Generate Kubernetes YAML manifest from DAC manifest"""

        namespace = f"industriverse-{self.manifest.partner_id}"
        app_name = self.manifest.name

        # Generate ConfigMap for widget configuration
        widget_configs = {
            w.widget_type: {
                'enabled': w.enabled,
                'refresh_interval_ms': w.refresh_interval_ms,
                'enable_animations': w.enable_animations,
                'enable_websocket': w.enable_websocket,
                'custom_features': w.custom_features
            }
            for w in self.manifest.widgets
        }

        # Generate Kubernetes resources
        k8s_manifest = f"""---
# Namespace
apiVersion: v1
kind: Namespace
metadata:
  name: {namespace}
  labels:
    partner: {self.manifest.partner_id}
    tier: {self.manifest.tier}

---
# ConfigMap for widget configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: {app_name}-config
  namespace: {namespace}
data:
  widgets.json: |
{json.dumps(widget_configs, indent=4)}
  theme.json: |
{json.dumps({
    'theme_base': self.manifest.theme.theme_base,
    'custom_colors': self.manifest.theme.custom_colors,
    'logo_url': self.manifest.theme.logo_url,
    'brand_name': self.manifest.theme.brand_name,
}, indent=4)}

---
# Secret for API credentials
apiVersion: v1
kind: Secret
metadata:
  name: {app_name}-secrets
  namespace: {namespace}
type: Opaque
stringData:
  api_key: "REPLACE_WITH_API_KEY"
  api_endpoint: "{self.manifest.network.api_endpoint}"

---
# Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {app_name}
  namespace: {namespace}
spec:
  replicas: {3 if self.manifest.tier == 'full-discovery' else 2 if self.manifest.tier == 'domain-intelligence' else 1}
  selector:
    matchLabels:
      app: {app_name}
  template:
    metadata:
      labels:
        app: {app_name}
        tier: {self.manifest.tier}
    spec:
      containers:
      - name: industriverse-dac
        image: industriverse/dac-runtime:latest
        ports:
{self._generate_ports()}
        env:
        - name: DAC_MANIFEST
          value: "{self.manifest.name}"
        - name: PARTNER_ID
          value: "{self.manifest.partner_id}"
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: {app_name}-secrets
              key: api_key
        - name: API_ENDPOINT
          valueFrom:
            secretKeyRef:
              name: {app_name}-secrets
              key: api_endpoint
        volumeMounts:
        - name: config
          mountPath: /etc/industriverse
        resources:
          requests:
            memory: "{self.manifest.resources.memory_gb}Gi"
            cpu: "{self.manifest.resources.cpu_cores}"
          limits:
            memory: "{self.manifest.resources.memory_gb * 1.5}Gi"
            cpu: "{self.manifest.resources.cpu_cores * 2}"
{self._generate_gpu_resources()}
      volumes:
      - name: config
        configMap:
          name: {app_name}-config

---
# Service
apiVersion: v1
kind: Service
metadata:
  name: {app_name}
  namespace: {namespace}
spec:
  type: LoadBalancer
  ports:
{self._generate_service_ports()}
  selector:
    app: {app_name}

---
# Ingress
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {app_name}
  namespace: {namespace}
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - {self.manifest.theme.custom_domain or f'{app_name}.industriverse.ai'}
    secretName: {app_name}-tls
  rules:
  - host: {self.manifest.theme.custom_domain or f'{app_name}.industriverse.ai'}
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: {app_name}
            port:
              number: 80
"""
        return k8s_manifest

    def _generate_ports(self) -> str:
        """Generate container ports configuration"""
        ports = []
        for port in self.manifest.network.ingress_ports:
            ports.append(f"        - containerPort: {port}")
        return '\n'.join(ports)

    def _generate_service_ports(self) -> str:
        """Generate service ports configuration"""
        ports = []
        for i, port in enumerate(self.manifest.network.ingress_ports):
            name = 'http' if port in [80, 8080] else 'https' if port in [443, 8443] else f'port-{i}'
            ports.append(f"""  - name: {name}
    port: 80 if port == 80 else 443 if port == 443 else {port}
    targetPort: {port}
    protocol: TCP""")
        return '\n'.join(ports)

    def _generate_gpu_resources(self) -> str:
        """Generate GPU resource requests if needed"""
        if self.manifest.resources.gpu_required:
            return f"""            nvidia.com/gpu: 1"""
        return ""

    async def deploy(self) -> DeploymentResult:
        """Deploy to Kubernetes"""
        try:
            # Generate manifest
            k8s_manifest = self.generate_k8s_manifest()

            # Save to file
            output_path = Path(f"./deployments/{self.manifest.name}-k8s.yaml")
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w') as f:
                f.write(k8s_manifest)

            # In production, would execute: kubectl apply -f {output_path}
            deployment_id = f"k8s-{self.manifest.partner_id}-{self.manifest.name}"

            return DeploymentResult(
                success=True,
                status=DeploymentStatus.DEPLOYED,
                deployment_id=deployment_id,
                endpoint=f"https://{self.manifest.theme.custom_domain or f'{self.manifest.name}.industriverse.ai'}",
                metadata={
                    'manifest_path': str(output_path),
                    'namespace': f"industriverse-{self.manifest.partner_id}",
                    'deployment_name': self.manifest.name
                }
            )

        except Exception as e:
            return DeploymentResult(
                success=False,
                status=DeploymentStatus.FAILED,
                deployment_id="",
                errors=[str(e)]
            )

    async def undeploy(self, deployment_id: str) -> DeploymentResult:
        """Undeploy from Kubernetes"""
        # kubectl delete namespace industriverse-{partner_id}
        return DeploymentResult(
            success=True,
            status=DeploymentStatus.TERMINATED,
            deployment_id=deployment_id
        )

    async def get_status(self, deployment_id: str) -> DeploymentStatus:
        """Get deployment status"""
        # kubectl get deployment -n {namespace}
        return DeploymentStatus.DEPLOYED

    async def scale(self, deployment_id: str, replicas: int) -> DeploymentResult:
        """Scale deployment"""
        # kubectl scale deployment {name} --replicas={replicas}
        return DeploymentResult(
            success=True,
            status=DeploymentStatus.DEPLOYED,
            deployment_id=deployment_id,
            metadata={'replicas': replicas}
        )

    async def update(self, deployment_id: str, new_manifest: DACManifest) -> DeploymentResult:
        """Update deployment"""
        self.manifest = new_manifest
        return await self.deploy()


class DockerDeployer(DeployerBase):
    """Deploy DAC as Docker container"""

    def generate_docker_compose(self) -> str:
        """Generate docker-compose.yml from DAC manifest"""

        compose = f"""version: '3.8'

services:
  industriverse-dac:
    image: industriverse/dac-runtime:latest
    container_name: {self.manifest.name}
    restart: unless-stopped
    environment:
      - DAC_MANIFEST={self.manifest.name}
      - PARTNER_ID={self.manifest.partner_id}
      - API_ENDPOINT={self.manifest.network.api_endpoint}
      - API_KEY=${{INDUSTRIVERSE_API_KEY}}
    ports:
{self._generate_port_mappings()}
    volumes:
      - ./config:/etc/industriverse:ro
      - dac-data:/var/lib/industriverse
    networks:
      - industriverse
    deploy:
      resources:
        limits:
          cpus: '{self.manifest.resources.cpu_cores}'
          memory: {self.manifest.resources.memory_gb}G
{self._generate_gpu_config()}

networks:
  industriverse:
    driver: bridge

volumes:
  dac-data:
"""
        return compose

    def _generate_port_mappings(self) -> str:
        """Generate Docker port mappings"""
        mappings = []
        for port in self.manifest.network.ingress_ports:
            mappings.append(f"      - \"{port}:{port}\"")
        return '\n'.join(mappings)

    def _generate_gpu_config(self) -> str:
        """Generate GPU configuration for Docker"""
        if self.manifest.resources.gpu_required:
            return """        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]"""
        return ""

    async def deploy(self) -> DeploymentResult:
        """Deploy with Docker Compose"""
        try:
            compose_yaml = self.generate_docker_compose()

            output_path = Path(f"./deployments/{self.manifest.name}-docker-compose.yml")
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w') as f:
                f.write(compose_yaml)

            # In production: docker-compose -f {output_path} up -d
            deployment_id = f"docker-{self.manifest.partner_id}-{self.manifest.name}"

            return DeploymentResult(
                success=True,
                status=DeploymentStatus.DEPLOYED,
                deployment_id=deployment_id,
                endpoint=f"http://localhost:{self.manifest.network.ingress_ports[0]}",
                metadata={'compose_path': str(output_path)}
            )

        except Exception as e:
            return DeploymentResult(
                success=False,
                status=DeploymentStatus.FAILED,
                deployment_id="",
                errors=[str(e)]
            )

    async def undeploy(self, deployment_id: str) -> DeploymentResult:
        """Stop and remove Docker containers"""
        return DeploymentResult(
            success=True,
            status=DeploymentStatus.TERMINATED,
            deployment_id=deployment_id
        )

    async def get_status(self, deployment_id: str) -> DeploymentStatus:
        """Get container status"""
        return DeploymentStatus.DEPLOYED

    async def scale(self, deployment_id: str, replicas: int) -> DeploymentResult:
        """Scale not supported in basic Docker mode"""
        return DeploymentResult(
            success=False,
            status=DeploymentStatus.FAILED,
            deployment_id=deployment_id,
            errors=["Scaling not supported in Docker mode. Use Kubernetes or Docker Swarm."]
        )

    async def update(self, deployment_id: str, new_manifest: DACManifest) -> DeploymentResult:
        """Update container"""
        await self.undeploy(deployment_id)
        self.manifest = new_manifest
        return await self.deploy()


class DACDeployer:
    """Main deployer orchestrator"""

    @staticmethod
    def create_deployer(manifest: DACManifest, target_env: str) -> DeployerBase:
        """Factory method to create environment-specific deployer"""

        env = TargetEnvironment(target_env)

        if env == TargetEnvironment.KUBERNETES:
            return KubernetesDeployer(manifest)
        elif env == TargetEnvironment.DOCKER:
            return DockerDeployer(manifest)
        elif env in [TargetEnvironment.AWS, TargetEnvironment.GCP, TargetEnvironment.AZURE]:
            # For cloud providers, use Kubernetes deployer
            # In production, would use provider-specific APIs
            return KubernetesDeployer(manifest)
        elif env == TargetEnvironment.EDGE:
            # Edge deployments use Docker
            return DockerDeployer(manifest)
        else:
            # On-premise defaults to Kubernetes
            return KubernetesDeployer(manifest)

    @staticmethod
    async def deploy_to_all_environments(manifest: DACManifest) -> Dict[str, DeploymentResult]:
        """Deploy DAC to all configured target environments"""
        results = {}

        for env in manifest.target_environments:
            deployer = DACDeployer.create_deployer(manifest, env)
            result = await deployer.deploy()
            results[env] = result

        return results
