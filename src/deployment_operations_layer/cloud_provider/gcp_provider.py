"""
Google Cloud Provider Integration

This module provides integration with Google Cloud Platform (GCP) services for the Deployment Operations Layer.
It handles GCP-specific deployment operations, resource management, and service interactions.

Classes:
    GCPProviderAdapter: Adapter for GCP cloud services integration
    GCPResourceManager: Manages GCP resources for deployments
    GCPDeploymentHandler: Handles deployment operations on GCP
"""

import json
import logging
import os
from typing import Dict, List, Any, Optional
from google.oauth2 import service_account
from google.cloud import storage, compute, container_v1
from google.cloud.exceptions import GoogleCloudError

from ..agent.agent_utils import AgentResponse
from ..protocol.mcp_integration.mcp_context_schema import MCPContext

logger = logging.getLogger(__name__)

class GCPProviderAdapter:
    """
    Adapter for Google Cloud Platform services integration.
    
    This class provides a standardized interface for interacting with GCP services
    within the Deployment Operations Layer.
    """
    
    def __init__(self, project_id: str, credentials_path: Optional[str] = None):
        """
        Initialize the GCP Provider Adapter.
        
        Args:
            project_id: GCP project ID
            credentials_path: Path to service account credentials JSON file (optional)
        """
        self.project_id = project_id
        self.credentials_path = credentials_path
        self.credentials = self._load_credentials()
        self.resource_manager = GCPResourceManager(self.project_id, self.credentials)
        self.deployment_handler = GCPDeploymentHandler(self.project_id, self.credentials)
        
    def _load_credentials(self) -> Optional[service_account.Credentials]:
        """
        Load GCP service account credentials.
        
        Returns:
            service_account.Credentials: GCP credentials or None if using default credentials
        """
        if self.credentials_path and os.path.exists(self.credentials_path):
            return service_account.Credentials.from_service_account_file(
                self.credentials_path
            )
        return None
    
    def validate_credentials(self) -> bool:
        """
        Validate GCP credentials.
        
        Returns:
            bool: True if credentials are valid, False otherwise
        """
        try:
            # Try to list storage buckets as a simple validation
            storage_client = storage.Client(
                project=self.project_id,
                credentials=self.credentials
            )
            list(storage_client.list_buckets(max_results=1))
            return True
        except Exception as e:
            logger.error(f"GCP credentials validation failed: {str(e)}")
            return False
    
    def get_available_services(self) -> List[str]:
        """
        Get list of available GCP services.
        
        Returns:
            List[str]: List of available service names
        """
        # This is a simplified list of common GCP services
        return [
            "compute",
            "storage",
            "container",
            "functions",
            "run",
            "bigquery",
            "pubsub",
            "dataflow",
            "dataproc",
            "spanner",
            "firestore"
        ]
    
    def create_deployment_context(self, mission_id: str) -> Dict[str, Any]:
        """
        Create GCP-specific deployment context for a mission.
        
        Args:
            mission_id: Unique identifier for the mission
            
        Returns:
            Dict[str, Any]: GCP deployment context
        """
        return {
            "provider": "gcp",
            "project_id": self.project_id,
            "mission_id": mission_id,
            "services": self.get_available_services()
        }
    
    def to_mcp_context(self) -> MCPContext:
        """
        Convert GCP provider information to MCP context.
        
        Returns:
            MCPContext: MCP context with GCP provider information
        """
        return MCPContext(
            context_type="cloud_provider",
            provider="gcp",
            project_id=self.project_id,
            services=self.get_available_services()
        )


class GCPResourceManager:
    """
    Manages GCP resources for deployments.
    
    This class handles resource provisioning, monitoring, and cleanup for
    GCP-based deployments.
    """
    
    def __init__(self, project_id: str, credentials: Optional[service_account.Credentials] = None):
        """
        Initialize the GCP Resource Manager.
        
        Args:
            project_id: GCP project ID
            credentials: GCP service account credentials (optional)
        """
        self.project_id = project_id
        self.credentials = credentials
        
    def provision_resources(self, resource_specs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provision GCP resources based on specifications.
        
        Args:
            resource_specs: Resource specifications
            
        Returns:
            Dict[str, Any]: Provisioned resource details
        """
        resources = {}
        
        # Process each resource type
        for resource_type, specs in resource_specs.items():
            if resource_type == "compute":
                resources["compute"] = self._provision_compute(specs)
            elif resource_type == "storage":
                resources["storage"] = self._provision_storage(specs)
            elif resource_type == "gke":
                resources["gke"] = self._provision_gke(specs)
            elif resource_type == "cloud_run":
                resources["cloud_run"] = self._provision_cloud_run(specs)
                
        return resources
    
    def _provision_compute(self, specs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provision Compute Engine instances.
        
        Args:
            specs: Compute Engine specifications
            
        Returns:
            Dict[str, Any]: Compute Engine resource details
        """
        compute_client = compute.InstancesClient(credentials=self.credentials)
        instances = []
        
        try:
            for instance_spec in specs.get("instances", []):
                zone = instance_spec.get("zone")
                instance_name = instance_spec.get("name")
                
                # Create instance
                machine_type = f"zones/{zone}/machineTypes/{instance_spec.get('machine_type', 'e2-medium')}"
                
                # Configure disks
                boot_disk = compute.AttachedDisk(
                    auto_delete=True,
                    boot=True,
                    initialize_params=compute.AttachedDiskInitializeParams(
                        source_image=instance_spec.get("source_image", "projects/debian-cloud/global/images/family/debian-10"),
                        disk_size_gb=instance_spec.get("disk_size_gb", 10),
                        disk_type=f"zones/{zone}/diskTypes/pd-standard"
                    )
                )
                
                # Configure network interfaces
                network_interfaces = [
                    compute.NetworkInterface(
                        network=f"global/networks/{instance_spec.get('network', 'default')}",
                        access_configs=[
                            compute.AccessConfig(
                                name="External NAT",
                                type_="ONE_TO_ONE_NAT"
                            )
                        ]
                    )
                ]
                
                # Create instance resource
                instance = compute.Instance(
                    name=instance_name,
                    machine_type=machine_type,
                    disks=[boot_disk],
                    network_interfaces=network_interfaces,
                    metadata=compute.Metadata(
                        items=[
                            compute.Items(
                                key="startup-script",
                                value=instance_spec.get("startup_script", "")
                            )
                        ]
                    )
                )
                
                # Create the instance
                operation = compute_client.insert(
                    project=self.project_id,
                    zone=zone,
                    instance_resource=instance
                )
                
                # Wait for the operation to complete
                operation_client = compute.ZoneOperationsClient(credentials=self.credentials)
                operation_client.wait(
                    project=self.project_id,
                    zone=zone,
                    operation=operation.name
                )
                
                # Get the created instance
                created_instance = compute_client.get(
                    project=self.project_id,
                    zone=zone,
                    instance=instance_name
                )
                
                instances.append({
                    "name": created_instance.name,
                    "zone": zone,
                    "machine_type": created_instance.machine_type,
                    "status": created_instance.status,
                    "network_interfaces": [
                        {
                            "network": ni.network,
                            "internal_ip": ni.network_ip,
                            "external_ip": ni.access_configs[0].nat_ip if ni.access_configs else None
                        }
                        for ni in created_instance.network_interfaces
                    ]
                })
                
            return {"instances": instances}
        
        except GoogleCloudError as e:
            logger.error(f"Failed to provision Compute Engine instances: {str(e)}")
            return {"error": str(e)}
    
    def _provision_storage(self, specs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provision Cloud Storage buckets.
        
        Args:
            specs: Cloud Storage specifications
            
        Returns:
            Dict[str, Any]: Cloud Storage resource details
        """
        storage_client = storage.Client(
            project=self.project_id,
            credentials=self.credentials
        )
        buckets = []
        
        try:
            for bucket_spec in specs.get("buckets", []):
                bucket_name = bucket_spec.get("name")
                location = bucket_spec.get("location", "us-central1")
                storage_class = bucket_spec.get("storage_class", "STANDARD")
                
                # Create bucket
                bucket = storage_client.create_bucket(
                    bucket_name,
                    location=location
                )
                
                # Set storage class
                bucket.storage_class = storage_class
                bucket.patch()
                
                buckets.append({
                    "name": bucket.name,
                    "location": bucket.location,
                    "storage_class": bucket.storage_class,
                    "url": f"gs://{bucket.name}"
                })
                
            return {"buckets": buckets}
        
        except GoogleCloudError as e:
            logger.error(f"Failed to provision Cloud Storage buckets: {str(e)}")
            return {"error": str(e)}
    
    def _provision_gke(self, specs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provision Google Kubernetes Engine clusters.
        
        Args:
            specs: GKE specifications
            
        Returns:
            Dict[str, Any]: GKE resource details
        """
        container_client = container_v1.ClusterManagerClient(credentials=self.credentials)
        clusters = []
        
        try:
            for cluster_spec in specs.get("clusters", []):
                cluster_name = cluster_spec.get("name")
                location = cluster_spec.get("location")
                
                # Create cluster
                cluster = container_v1.Cluster(
                    name=cluster_name,
                    initial_node_count=cluster_spec.get("initial_node_count", 3),
                    node_config=container_v1.NodeConfig(
                        machine_type=cluster_spec.get("machine_type", "e2-medium"),
                        disk_size_gb=cluster_spec.get("disk_size_gb", 100),
                        oauth_scopes=[
                            "https://www.googleapis.com/auth/devstorage.read_only",
                            "https://www.googleapis.com/auth/logging.write",
                            "https://www.googleapis.com/auth/monitoring"
                        ]
                    )
                )
                
                # Check if location is a zone or region
                if "-" in location and location.count("-") == 2:
                    # Zone
                    parent = f"projects/{self.project_id}/locations/{location}"
                    operation = container_client.create_cluster(
                        parent=parent,
                        cluster=cluster
                    )
                else:
                    # Region
                    parent = f"projects/{self.project_id}/locations/{location}"
                    cluster.location = location
                    operation = container_client.create_cluster(
                        parent=parent,
                        cluster=cluster
                    )
                
                # Wait for the operation to complete
                operation_client = container_v1.ClusterManagerClient(credentials=self.credentials)
                operation_client.wait_operation(
                    name=operation.name
                )
                
                # Get the created cluster
                created_cluster = container_client.get_cluster(
                    name=f"projects/{self.project_id}/locations/{location}/clusters/{cluster_name}"
                )
                
                clusters.append({
                    "name": created_cluster.name,
                    "location": location,
                    "endpoint": created_cluster.endpoint,
                    "status": created_cluster.status.name,
                    "node_count": created_cluster.current_node_count
                })
                
            return {"clusters": clusters}
        
        except GoogleCloudError as e:
            logger.error(f"Failed to provision GKE clusters: {str(e)}")
            return {"error": str(e)}
    
    def _provision_cloud_run(self, specs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provision Cloud Run services.
        
        Args:
            specs: Cloud Run specifications
            
        Returns:
            Dict[str, Any]: Cloud Run resource details
        """
        # Cloud Run requires the Cloud Run Admin API client
        # This is a simplified implementation
        from google.cloud import run_v2
        
        run_client = run_v2.ServicesClient(credentials=self.credentials)
        services = []
        
        try:
            for service_spec in specs.get("services", []):
                service_name = service_spec.get("name")
                location = service_spec.get("location", "us-central1")
                
                # Create service
                service = run_v2.Service(
                    template=run_v2.RevisionTemplate(
                        containers=[
                            run_v2.Container(
                                image=service_spec.get("image"),
                                ports=[
                                    run_v2.ContainerPort(
                                        container_port=service_spec.get("port", 8080)
                                    )
                                ],
                                resources=run_v2.ResourceRequirements(
                                    limits={
                                        "cpu": service_spec.get("cpu", "1"),
                                        "memory": service_spec.get("memory", "512Mi")
                                    }
                                ),
                                env=[
                                    run_v2.EnvVar(
                                        name=env["name"],
                                        value=env["value"]
                                    )
                                    for env in service_spec.get("env", [])
                                ]
                            )
                        ],
                        scaling=run_v2.RevisionScaling(
                            max_instance_count=service_spec.get("max_instances", 10),
                            min_instance_count=service_spec.get("min_instances", 0)
                        )
                    )
                )
                
                # Create the service
                parent = f"projects/{self.project_id}/locations/{location}"
                operation = run_client.create_service(
                    parent=parent,
                    service=service,
                    service_id=service_name
                )
                
                # Wait for the operation to complete
                operation_client = run_v2.OperationsClient(credentials=self.credentials)
                operation_client.wait_operation(
                    name=operation.name
                )
                
                # Get the created service
                created_service = run_client.get_service(
                    name=f"projects/{self.project_id}/locations/{location}/services/{service_name}"
                )
                
                services.append({
                    "name": created_service.name,
                    "location": location,
                    "url": created_service.uri,
                    "status": created_service.status.conditions[0].type_,
                    "latest_revision": created_service.latest_created_revision
                })
                
            return {"services": services}
        
        except GoogleCloudError as e:
            logger.error(f"Failed to provision Cloud Run services: {str(e)}")
            return {"error": str(e)}
    
    def cleanup_resources(self, resources: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean up provisioned GCP resources.
        
        Args:
            resources: Resource details to clean up
            
        Returns:
            Dict[str, Any]: Cleanup results
        """
        results = {}
        
        # Clean up Compute Engine instances
        if "compute" in resources:
            results["compute"] = self._cleanup_compute(resources["compute"])
            
        # Clean up Cloud Storage buckets
        if "storage" in resources:
            results["storage"] = self._cleanup_storage(resources["storage"])
            
        # Clean up GKE clusters
        if "gke" in resources:
            results["gke"] = self._cleanup_gke(resources["gke"])
            
        # Clean up Cloud Run services
        if "cloud_run" in resources:
            results["cloud_run"] = self._cleanup_cloud_run(resources["cloud_run"])
            
        return results
    
    def _cleanup_compute(self, resources: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean up Compute Engine resources.
        
        Args:
            resources: Compute Engine resource details
            
        Returns:
            Dict[str, Any]: Cleanup results
        """
        compute_client = compute.InstancesClient(credentials=self.credentials)
        results = {"success": [], "failed": []}
        
        try:
            for instance in resources.get("instances", []):
                instance_name = instance["name"]
                zone = instance["zone"]
                
                # Delete the instance
                operation = compute_client.delete(
                    project=self.project_id,
                    zone=zone,
                    instance=instance_name
                )
                
                # Wait for the operation to complete
                operation_client = compute.ZoneOperationsClient(credentials=self.credentials)
                operation_client.wait(
                    project=self.project_id,
                    zone=zone,
                    operation=operation.name
                )
                
                results["success"].append(instance_name)
                
            return results
        
        except GoogleCloudError as e:
            logger.error(f"Failed to clean up Compute Engine instances: {str(e)}")
            results["failed"].append({"name": instance_name, "error": str(e)})
            return results
    
    def _cleanup_storage(self, resources: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean up Cloud Storage resources.
        
        Args:
            resources: Cloud Storage resource details
            
        Returns:
            Dict[str, Any]: Cleanup results
        """
        storage_client = storage.Client(
            project=self.project_id,
            credentials=self.credentials
        )
        results = {"success": [], "failed": []}
        
        try:
            for bucket in resources.get("buckets", []):
                bucket_name = bucket["name"]
                
                # Get the bucket
                bucket_obj = storage_client.bucket(bucket_name)
                
                # Delete all objects in the bucket first
                blobs = bucket_obj.list_blobs()
                for blob in blobs:
                    blob.delete()
                
                # Then delete the bucket
                bucket_obj.delete()
                results["success"].append(bucket_name)
                
            return results
        
        except GoogleCloudError as e:
            logger.error(f"Failed to clean up Cloud Storage buckets: {str(e)}")
            results["failed"].append({"name": bucket_name, "error": str(e)})
            return results
    
    def _cleanup_gke(self, resources: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean up GKE resources.
        
        Args:
            resources: GKE resource details
            
        Returns:
            Dict[str, Any]: Cleanup results
        """
        container_client = container_v1.ClusterManagerClient(credentials=self.credentials)
        results = {"success": [], "failed": []}
        
        try:
            for cluster in resources.get("clusters", []):
                cluster_name = cluster["name"]
                location = cluster["location"]
                
                # Delete the cluster
                name = f"projects/{self.project_id}/locations/{location}/clusters/{cluster_name}"
                operation = container_client.delete_cluster(
                    name=name
                )
                
                # Wait for the operation to complete
                operation_client = container_v1.ClusterManagerClient(credentials=self.credentials)
                operation_client.wait_operation(
                    name=operation.name
                )
                
                results["success"].append(cluster_name)
                
            return results
        
        except GoogleCloudError as e:
            logger.error(f"Failed to clean up GKE clusters: {str(e)}")
            results["failed"].append({"name": cluster_name, "error": str(e)})
            return results
    
    def _cleanup_cloud_run(self, resources: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean up Cloud Run resources.
        
        Args:
            resources: Cloud Run resource details
            
        Returns:
            Dict[str, Any]: Cleanup results
        """
        from google.cloud import run_v2
        
        run_client = run_v2.ServicesClient(credentials=self.credentials)
        results = {"success": [], "failed": []}
        
        try:
            for service in resources.get("services", []):
                service_name = service["name"].split("/")[-1]
                location = service["location"]
                
                # Delete the service
                name = f"projects/{self.project_id}/locations/{location}/services/{service_name}"
                operation = run_client.delete_service(
                    name=name
                )
                
                # Wait for the operation to complete
                operation_client = run_v2.OperationsClient(credentials=self.credentials)
                operation_client.wait_operation(
                    name=operation.name
                )
                
                results["success"].append(service_name)
                
            return results
        
        except GoogleCloudError as e:
            logger.error(f"Failed to clean up Cloud Run services: {str(e)}")
            results["failed"].append({"name": service_name, "error": str(e)})
            return results


class GCPDeploymentHandler:
    """
    Handles deployment operations on GCP.
    
    This class manages the deployment of applications and services to GCP.
    """
    
    def __init__(self, project_id: str, credentials: Optional[service_account.Credentials] = None):
        """
        Initialize the GCP Deployment Handler.
        
        Args:
            project_id: GCP project ID
            credentials: GCP service account credentials (optional)
        """
        self.project_id = project_id
        self.credentials = credentials
        
    def deploy_application(self, deployment_spec: Dict[str, Any]) -> AgentResponse:
        """
        Deploy an application to GCP.
        
        Args:
            deployment_spec: Deployment specifications
            
        Returns:
            AgentResponse: Deployment response
        """
        deployment_type = deployment_spec.get("type", "")
        
        if deployment_type == "cloud_run":
            return self._deploy_cloud_run_application(deployment_spec)
        elif deployment_type == "gke":
            return self._deploy_gke_application(deployment_spec)
        elif deployment_type == "compute":
            return self._deploy_compute_application(deployment_spec)
        elif deployment_type == "cloud_functions":
            return self._deploy_cloud_functions_application(deployment_spec)
        else:
            return AgentResponse(
                success=False,
                message=f"Unsupported deployment type: {deployment_type}",
                data={}
            )
    
    def _deploy_cloud_run_application(self, spec: Dict[str, Any]) -> AgentResponse:
        """
        Deploy a Cloud Run application.
        
        Args:
            spec: Cloud Run deployment specifications
            
        Returns:
            AgentResponse: Deployment response
        """
        from google.cloud import run_v2
        
        run_client = run_v2.ServicesClient(credentials=self.credentials)
        
        try:
            service_name = spec.get("service_name")
            location = spec.get("location", "us-central1")
            image = spec.get("image")
            
            # Create or update service
            parent = f"projects/{self.project_id}/locations/{location}"
            service_id = service_name
            
            # Check if service exists
            try:
                existing_service = run_client.get_service(
                    name=f"{parent}/services/{service_id}"
                )
                
                # Update existing service
                service = run_v2.Service(
                    name=existing_service.name,
                    template=run_v2.RevisionTemplate(
                        containers=[
                            run_v2.Container(
                                image=image,
                                ports=[
                                    run_v2.ContainerPort(
                                        container_port=spec.get("port", 8080)
                                    )
                                ],
                                resources=run_v2.ResourceRequirements(
                                    limits={
                                        "cpu": spec.get("cpu", "1"),
                                        "memory": spec.get("memory", "512Mi")
                                    }
                                ),
                                env=[
                                    run_v2.EnvVar(
                                        name=env["name"],
                                        value=env["value"]
                                    )
                                    for env in spec.get("env", [])
                                ]
                            )
                        ],
                        scaling=run_v2.RevisionScaling(
                            max_instance_count=spec.get("max_instances", 10),
                            min_instance_count=spec.get("min_instances", 0)
                        )
                    )
                )
                
                operation = run_client.update_service(
                    service=service
                )
            except:
                # Create new service
                service = run_v2.Service(
                    template=run_v2.RevisionTemplate(
                        containers=[
                            run_v2.Container(
                                image=image,
                                ports=[
                                    run_v2.ContainerPort(
                                        container_port=spec.get("port", 8080)
                                    )
                                ],
                                resources=run_v2.ResourceRequirements(
                                    limits={
                                        "cpu": spec.get("cpu", "1"),
                                        "memory": spec.get("memory", "512Mi")
                                    }
                                ),
                                env=[
                                    run_v2.EnvVar(
                                        name=env["name"],
                                        value=env["value"]
                                    )
                                    for env in spec.get("env", [])
                                ]
                            )
                        ],
                        scaling=run_v2.RevisionScaling(
                            max_instance_count=spec.get("max_instances", 10),
                            min_instance_count=spec.get("min_instances", 0)
                        )
                    )
                )
                
                operation = run_client.create_service(
                    parent=parent,
                    service=service,
                    service_id=service_id
                )
            
            # Wait for the operation to complete
            operation_client = run_v2.OperationsClient(credentials=self.credentials)
            operation_client.wait_operation(
                name=operation.name
            )
            
            # Get the deployed service
            deployed_service = run_client.get_service(
                name=f"{parent}/services/{service_id}"
            )
            
            return AgentResponse(
                success=True,
                message=f"Successfully deployed Cloud Run service: {service_name}",
                data={
                    "name": deployed_service.name,
                    "url": deployed_service.uri,
                    "status": deployed_service.status.conditions[0].type_,
                    "latest_revision": deployed_service.latest_created_revision
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to deploy Cloud Run application: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to deploy Cloud Run application: {str(e)}",
                data={}
            )
    
    def _deploy_gke_application(self, spec: Dict[str, Any]) -> AgentResponse:
        """
        Deploy an application to GKE.
        
        Args:
            spec: GKE deployment specifications
            
        Returns:
            AgentResponse: Deployment response
        """
        # For GKE deployments, we use kubectl commands through subprocess
        # This is a simplified implementation
        import subprocess
        import tempfile
        import os
        
        try:
            cluster_name = spec.get("cluster")
            location = spec.get("location")
            namespace = spec.get("namespace", "default")
            manifests = spec.get("manifests", [])
            
            # Create a temporary directory for manifests
            with tempfile.TemporaryDirectory() as temp_dir:
                # Write manifests to files
                manifest_files = []
                for i, manifest in enumerate(manifests):
                    file_path = os.path.join(temp_dir, f"manifest_{i}.yaml")
                    with open(file_path, "w") as f:
                        f.write(manifest)
                    manifest_files.append(file_path)
                
                # Get credentials for the cluster
                get_creds_cmd = [
                    "gcloud", "container", "clusters", "get-credentials",
                    cluster_name,
                    "--location", location,
                    "--project", self.project_id
                ]
                
                subprocess.run(get_creds_cmd, check=True)
                
                # Apply manifests
                results = []
                for file_path in manifest_files:
                    apply_cmd = [
                        "kubectl", "apply",
                        "-f", file_path,
                        "-n", namespace
                    ]
                    
                    result = subprocess.run(
                        apply_cmd,
                        check=True,
                        capture_output=True,
                        text=True
                    )
                    
                    results.append({
                        "file": os.path.basename(file_path),
                        "output": result.stdout
                    })
            
            return AgentResponse(
                success=True,
                message=f"Successfully deployed application to GKE cluster: {cluster_name}, namespace: {namespace}",
                data={
                    "cluster": cluster_name,
                    "location": location,
                    "namespace": namespace,
                    "results": results
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to deploy GKE application: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to deploy GKE application: {str(e)}",
                data={}
            )
    
    def _deploy_compute_application(self, spec: Dict[str, Any]) -> AgentResponse:
        """
        Deploy an application to Compute Engine instances.
        
        Args:
            spec: Compute Engine deployment specifications
            
        Returns:
            AgentResponse: Deployment response
        """
        # For Compute Engine deployments, we use SSH to run commands on instances
        # This is a simplified implementation
        import subprocess
        import tempfile
        import os
        
        try:
            instance_names = spec.get("instance_names", [])
            zone = spec.get("zone")
            commands = spec.get("commands", [])
            
            results = []
            for instance_name in instance_names:
                # Create a temporary script file
                with tempfile.NamedTemporaryFile(mode="w", delete=False) as script_file:
                    script_file.write("#!/bin/bash\n")
                    for command in commands:
                        script_file.write(f"{command}\n")
                    script_path = script_file.name
                
                # Make the script executable
                os.chmod(script_path, 0o755)
                
                # Copy the script to the instance
                copy_cmd = [
                    "gcloud", "compute", "scp",
                    script_path,
                    f"{instance_name}:/tmp/deploy.sh",
                    "--zone", zone,
                    "--project", self.project_id
                ]
                
                subprocess.run(copy_cmd, check=True)
                
                # Execute the script on the instance
                ssh_cmd = [
                    "gcloud", "compute", "ssh",
                    instance_name,
                    "--zone", zone,
                    "--project", self.project_id,
                    "--command", "sudo bash /tmp/deploy.sh"
                ]
                
                result = subprocess.run(
                    ssh_cmd,
                    check=True,
                    capture_output=True,
                    text=True
                )
                
                results.append({
                    "instance": instance_name,
                    "output": result.stdout
                })
                
                # Clean up the temporary script
                os.unlink(script_path)
            
            return AgentResponse(
                success=True,
                message=f"Successfully deployed application to Compute Engine instances",
                data={
                    "instances": results
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to deploy Compute Engine application: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to deploy Compute Engine application: {str(e)}",
                data={}
            )
    
    def _deploy_cloud_functions_application(self, spec: Dict[str, Any]) -> AgentResponse:
        """
        Deploy a Cloud Functions application.
        
        Args:
            spec: Cloud Functions deployment specifications
            
        Returns:
            AgentResponse: Deployment response
        """
        from google.cloud import functions_v2
        
        functions_client = functions_v2.FunctionServiceClient(credentials=self.credentials)
        
        try:
            function_name = spec.get("function_name")
            location = spec.get("location", "us-central1")
            source_bucket = spec.get("source_bucket")
            source_object = spec.get("source_object")
            entry_point = spec.get("entry_point")
            runtime = spec.get("runtime", "python39")
            
            # Create or update function
            parent = f"projects/{self.project_id}/locations/{location}"
            function_id = function_name
            
            # Check if function exists
            try:
                existing_function = functions_client.get_function(
                    name=f"{parent}/functions/{function_id}"
                )
                
                # Update existing function
                function = functions_v2.Function(
                    name=existing_function.name,
                    build_config=functions_v2.BuildConfig(
                        runtime=runtime,
                        entry_point=entry_point,
                        source=functions_v2.Source(
                            storage_source=functions_v2.StorageSource(
                                bucket=source_bucket,
                                object_=source_object
                            )
                        )
                    ),
                    service_config=functions_v2.ServiceConfig(
                        available_memory=spec.get("memory", "256M"),
                        timeout=functions_v2.Duration(
                            seconds=spec.get("timeout", 60)
                        ),
                        environment_variables=spec.get("env", {})
                    )
                )
                
                operation = functions_client.update_function(
                    function=function
                )
            except:
                # Create new function
                function = functions_v2.Function(
                    build_config=functions_v2.BuildConfig(
                        runtime=runtime,
                        entry_point=entry_point,
                        source=functions_v2.Source(
                            storage_source=functions_v2.StorageSource(
                                bucket=source_bucket,
                                object_=source_object
                            )
                        )
                    ),
                    service_config=functions_v2.ServiceConfig(
                        available_memory=spec.get("memory", "256M"),
                        timeout=functions_v2.Duration(
                            seconds=spec.get("timeout", 60)
                        ),
                        environment_variables=spec.get("env", {})
                    )
                )
                
                operation = functions_client.create_function(
                    parent=parent,
                    function=function,
                    function_id=function_id
                )
            
            # Wait for the operation to complete
            operation_client = functions_v2.OperationsClient(credentials=self.credentials)
            operation_client.wait_operation(
                name=operation.name
            )
            
            # Get the deployed function
            deployed_function = functions_client.get_function(
                name=f"{parent}/functions/{function_id}"
            )
            
            return AgentResponse(
                success=True,
                message=f"Successfully deployed Cloud Functions function: {function_name}",
                data={
                    "name": deployed_function.name,
                    "url": deployed_function.service_config.uri,
                    "state": deployed_function.state.name,
                    "runtime": deployed_function.build_config.runtime,
                    "entry_point": deployed_function.build_config.entry_point
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to deploy Cloud Functions application: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to deploy Cloud Functions application: {str(e)}",
                data={}
            )
