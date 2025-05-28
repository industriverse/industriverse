"""
Azure Provider Integration

This module provides integration with Microsoft Azure services for the Deployment Operations Layer.
It handles Azure-specific deployment operations, resource management, and service interactions.

Classes:
    AzureProviderAdapter: Adapter for Azure cloud services integration
    AzureResourceManager: Manages Azure resources for deployments
    AzureDeploymentHandler: Handles deployment operations on Azure
"""

import json
import logging
import os
from typing import Dict, List, Any, Optional
import azure.mgmt.resource
import azure.mgmt.compute
import azure.mgmt.storage
import azure.mgmt.containerservice
import azure.mgmt.containerinstance
import azure.mgmt.web
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.core.exceptions import AzureError

from ..agent.agent_utils import AgentResponse
from ..protocol.mcp_integration.mcp_context_schema import MCPContext

logger = logging.getLogger(__name__)

class AzureProviderAdapter:
    """
    Adapter for Microsoft Azure services integration.
    
    This class provides a standardized interface for interacting with Azure services
    within the Deployment Operations Layer.
    """
    
    def __init__(self, subscription_id: str, tenant_id: Optional[str] = None, 
                 client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """
        Initialize the Azure Provider Adapter.
        
        Args:
            subscription_id: Azure subscription ID
            tenant_id: Azure tenant ID (optional for DefaultAzureCredential)
            client_id: Azure client ID (optional for DefaultAzureCredential)
            client_secret: Azure client secret (optional for DefaultAzureCredential)
        """
        self.subscription_id = subscription_id
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.credentials = self._get_credentials()
        self.resource_manager = AzureResourceManager(self.subscription_id, self.credentials)
        self.deployment_handler = AzureDeploymentHandler(self.subscription_id, self.credentials)
        
    def _get_credentials(self):
        """
        Get Azure credentials.
        
        Returns:
            Azure credentials object
        """
        if all([self.tenant_id, self.client_id, self.client_secret]):
            return ClientSecretCredential(
                tenant_id=self.tenant_id,
                client_id=self.client_id,
                client_secret=self.client_secret
            )
        return DefaultAzureCredential()
    
    def validate_credentials(self) -> bool:
        """
        Validate Azure credentials.
        
        Returns:
            bool: True if credentials are valid, False otherwise
        """
        try:
            # Try to list resource groups as a simple validation
            resource_client = azure.mgmt.resource.ResourceManagementClient(
                credential=self.credentials,
                subscription_id=self.subscription_id
            )
            list(resource_client.resource_groups.list())
            return True
        except Exception as e:
            logger.error(f"Azure credentials validation failed: {str(e)}")
            return False
    
    def get_available_services(self) -> List[str]:
        """
        Get list of available Azure services.
        
        Returns:
            List[str]: List of available service names
        """
        # This is a simplified list of common Azure services
        return [
            "compute",
            "storage",
            "aks",
            "aci",
            "app_service",
            "functions",
            "sql",
            "cosmos_db",
            "event_hub",
            "service_bus",
            "key_vault"
        ]
    
    def create_deployment_context(self, mission_id: str) -> Dict[str, Any]:
        """
        Create Azure-specific deployment context for a mission.
        
        Args:
            mission_id: Unique identifier for the mission
            
        Returns:
            Dict[str, Any]: Azure deployment context
        """
        return {
            "provider": "azure",
            "subscription_id": self.subscription_id,
            "mission_id": mission_id,
            "services": self.get_available_services()
        }
    
    def to_mcp_context(self) -> MCPContext:
        """
        Convert Azure provider information to MCP context.
        
        Returns:
            MCPContext: MCP context with Azure provider information
        """
        return MCPContext(
            context_type="cloud_provider",
            provider="azure",
            subscription_id=self.subscription_id,
            services=self.get_available_services()
        )


class AzureResourceManager:
    """
    Manages Azure resources for deployments.
    
    This class handles resource provisioning, monitoring, and cleanup for
    Azure-based deployments.
    """
    
    def __init__(self, subscription_id: str, credentials):
        """
        Initialize the Azure Resource Manager.
        
        Args:
            subscription_id: Azure subscription ID
            credentials: Azure credentials
        """
        self.subscription_id = subscription_id
        self.credentials = credentials
        self.resource_client = azure.mgmt.resource.ResourceManagementClient(
            credential=credentials,
            subscription_id=subscription_id
        )
        
    def provision_resources(self, resource_specs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provision Azure resources based on specifications.
        
        Args:
            resource_specs: Resource specifications
            
        Returns:
            Dict[str, Any]: Provisioned resource details
        """
        resources = {}
        
        # Create resource group if specified
        if "resource_group" in resource_specs:
            resources["resource_group"] = self._provision_resource_group(resource_specs["resource_group"])
        
        # Process each resource type
        for resource_type, specs in resource_specs.items():
            if resource_type == "virtual_machines":
                resources["virtual_machines"] = self._provision_virtual_machines(specs)
            elif resource_type == "storage":
                resources["storage"] = self._provision_storage(specs)
            elif resource_type == "aks":
                resources["aks"] = self._provision_aks(specs)
            elif resource_type == "app_service":
                resources["app_service"] = self._provision_app_service(specs)
                
        return resources
    
    def _provision_resource_group(self, specs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provision an Azure resource group.
        
        Args:
            specs: Resource group specifications
            
        Returns:
            Dict[str, Any]: Resource group details
        """
        try:
            resource_group_name = specs.get("name")
            location = specs.get("location", "eastus")
            tags = specs.get("tags", {})
            
            # Check if resource group exists
            if self._resource_group_exists(resource_group_name):
                # Get existing resource group
                resource_group = self.resource_client.resource_groups.get(resource_group_name)
            else:
                # Create new resource group
                resource_group = self.resource_client.resource_groups.create_or_update(
                    resource_group_name,
                    {
                        "location": location,
                        "tags": tags
                    }
                )
            
            return {
                "name": resource_group.name,
                "location": resource_group.location,
                "id": resource_group.id,
                "tags": resource_group.tags
            }
        
        except AzureError as e:
            logger.error(f"Failed to provision resource group: {str(e)}")
            return {"error": str(e)}
    
    def _resource_group_exists(self, resource_group_name: str) -> bool:
        """
        Check if a resource group exists.
        
        Args:
            resource_group_name: Name of the resource group
            
        Returns:
            bool: True if the resource group exists, False otherwise
        """
        try:
            self.resource_client.resource_groups.get(resource_group_name)
            return True
        except:
            return False
    
    def _provision_virtual_machines(self, specs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provision Azure virtual machines.
        
        Args:
            specs: Virtual machine specifications
            
        Returns:
            Dict[str, Any]: Virtual machine details
        """
        compute_client = azure.mgmt.compute.ComputeManagementClient(
            credential=self.credentials,
            subscription_id=self.subscription_id
        )
        vms = []
        
        try:
            for vm_spec in specs.get("vms", []):
                resource_group_name = vm_spec.get("resource_group")
                vm_name = vm_spec.get("name")
                location = vm_spec.get("location", "eastus")
                
                # Create VM
                poller = compute_client.virtual_machines.begin_create_or_update(
                    resource_group_name,
                    vm_name,
                    {
                        "location": location,
                        "hardware_profile": {
                            "vm_size": vm_spec.get("size", "Standard_DS1_v2")
                        },
                        "storage_profile": {
                            "image_reference": vm_spec.get("image_reference", {
                                "publisher": "Canonical",
                                "offer": "UbuntuServer",
                                "sku": "18.04-LTS",
                                "version": "latest"
                            }),
                            "os_disk": {
                                "name": f"{vm_name}-osdisk",
                                "caching": "ReadWrite",
                                "create_option": "FromImage",
                                "managed_disk": {
                                    "storage_account_type": vm_spec.get("disk_type", "Standard_LRS")
                                }
                            }
                        },
                        "os_profile": {
                            "computer_name": vm_name,
                            "admin_username": vm_spec.get("admin_username", "azureuser"),
                            "admin_password": vm_spec.get("admin_password", ""),
                            "linux_configuration": {
                                "disable_password_authentication": vm_spec.get("disable_password_authentication", True),
                                "ssh": {
                                    "public_keys": [
                                        {
                                            "path": f"/home/{vm_spec.get('admin_username', 'azureuser')}/.ssh/authorized_keys",
                                            "key_data": vm_spec.get("ssh_key", "")
                                        }
                                    ]
                                } if vm_spec.get("ssh_key") else None
                            } if vm_spec.get("os_type", "linux").lower() == "linux" else None
                        },
                        "network_profile": {
                            "network_interfaces": [
                                {
                                    "id": vm_spec.get("network_interface_id")
                                }
                            ]
                        },
                        "tags": vm_spec.get("tags", {})
                    }
                )
                
                vm = poller.result()
                
                vms.append({
                    "name": vm.name,
                    "id": vm.id,
                    "location": vm.location,
                    "size": vm.hardware_profile.vm_size,
                    "resource_group": resource_group_name
                })
                
            return {"vms": vms}
        
        except AzureError as e:
            logger.error(f"Failed to provision virtual machines: {str(e)}")
            return {"error": str(e)}
    
    def _provision_storage(self, specs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provision Azure storage accounts.
        
        Args:
            specs: Storage account specifications
            
        Returns:
            Dict[str, Any]: Storage account details
        """
        storage_client = azure.mgmt.storage.StorageManagementClient(
            credential=self.credentials,
            subscription_id=self.subscription_id
        )
        accounts = []
        
        try:
            for account_spec in specs.get("accounts", []):
                resource_group_name = account_spec.get("resource_group")
                account_name = account_spec.get("name")
                location = account_spec.get("location", "eastus")
                
                # Create storage account
                poller = storage_client.storage_accounts.begin_create(
                    resource_group_name,
                    account_name,
                    {
                        "location": location,
                        "kind": account_spec.get("kind", "StorageV2"),
                        "sku": {
                            "name": account_spec.get("sku", "Standard_LRS")
                        },
                        "tags": account_spec.get("tags", {})
                    }
                )
                
                account = poller.result()
                
                # Create containers if specified
                containers = []
                for container_spec in account_spec.get("containers", []):
                    container_name = container_spec.get("name")
                    public_access = container_spec.get("public_access", "None")
                    
                    container = storage_client.blob_containers.create(
                        resource_group_name,
                        account_name,
                        container_name,
                        {
                            "public_access": public_access
                        }
                    )
                    
                    containers.append({
                        "name": container.name,
                        "public_access": container.public_access
                    })
                
                accounts.append({
                    "name": account.name,
                    "id": account.id,
                    "location": account.location,
                    "kind": account.kind,
                    "sku": account.sku.name,
                    "resource_group": resource_group_name,
                    "containers": containers
                })
                
            return {"accounts": accounts}
        
        except AzureError as e:
            logger.error(f"Failed to provision storage accounts: {str(e)}")
            return {"error": str(e)}
    
    def _provision_aks(self, specs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provision Azure Kubernetes Service (AKS) clusters.
        
        Args:
            specs: AKS cluster specifications
            
        Returns:
            Dict[str, Any]: AKS cluster details
        """
        container_client = azure.mgmt.containerservice.ContainerServiceClient(
            credential=self.credentials,
            subscription_id=self.subscription_id
        )
        clusters = []
        
        try:
            for cluster_spec in specs.get("clusters", []):
                resource_group_name = cluster_spec.get("resource_group")
                cluster_name = cluster_spec.get("name")
                location = cluster_spec.get("location", "eastus")
                
                # Create AKS cluster
                poller = container_client.managed_clusters.begin_create_or_update(
                    resource_group_name,
                    cluster_name,
                    {
                        "location": location,
                        "dns_prefix": cluster_spec.get("dns_prefix", cluster_name),
                        "kubernetes_version": cluster_spec.get("kubernetes_version"),
                        "agent_pool_profiles": [
                            {
                                "name": "agentpool",
                                "count": cluster_spec.get("node_count", 3),
                                "vm_size": cluster_spec.get("vm_size", "Standard_DS2_v2"),
                                "os_type": "Linux",
                                "type": "VirtualMachineScaleSets",
                                "mode": "System"
                            }
                        ],
                        "service_principal_profile": {
                            "client_id": cluster_spec.get("client_id"),
                            "secret": cluster_spec.get("client_secret")
                        } if cluster_spec.get("client_id") and cluster_spec.get("client_secret") else None,
                        "identity": {
                            "type": "SystemAssigned"
                        } if not (cluster_spec.get("client_id") and cluster_spec.get("client_secret")) else None,
                        "tags": cluster_spec.get("tags", {})
                    }
                )
                
                cluster = poller.result()
                
                clusters.append({
                    "name": cluster.name,
                    "id": cluster.id,
                    "location": cluster.location,
                    "kubernetes_version": cluster.kubernetes_version,
                    "fqdn": cluster.fqdn,
                    "resource_group": resource_group_name
                })
                
            return {"clusters": clusters}
        
        except AzureError as e:
            logger.error(f"Failed to provision AKS clusters: {str(e)}")
            return {"error": str(e)}
    
    def _provision_app_service(self, specs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provision Azure App Service plans and apps.
        
        Args:
            specs: App Service specifications
            
        Returns:
            Dict[str, Any]: App Service details
        """
        web_client = azure.mgmt.web.WebSiteManagementClient(
            credential=self.credentials,
            subscription_id=self.subscription_id
        )
        plans = []
        apps = []
        
        try:
            # Create App Service plans
            for plan_spec in specs.get("plans", []):
                resource_group_name = plan_spec.get("resource_group")
                plan_name = plan_spec.get("name")
                location = plan_spec.get("location", "eastus")
                
                # Create App Service plan
                poller = web_client.app_service_plans.begin_create_or_update(
                    resource_group_name,
                    plan_name,
                    {
                        "location": location,
                        "sku": {
                            "name": plan_spec.get("sku", "B1"),
                            "tier": plan_spec.get("tier", "Basic"),
                            "size": plan_spec.get("size", "B1"),
                            "family": plan_spec.get("family", "B"),
                            "capacity": plan_spec.get("capacity", 1)
                        },
                        "kind": "app",
                        "reserved": plan_spec.get("is_linux", False),
                        "tags": plan_spec.get("tags", {})
                    }
                )
                
                plan = poller.result()
                
                plans.append({
                    "name": plan.name,
                    "id": plan.id,
                    "location": plan.location,
                    "sku": plan.sku.name,
                    "resource_group": resource_group_name
                })
                
                # Create apps for this plan
                for app_spec in plan_spec.get("apps", []):
                    app_name = app_spec.get("name")
                    
                    # Create web app
                    poller = web_client.web_apps.begin_create_or_update(
                        resource_group_name,
                        app_name,
                        {
                            "location": location,
                            "server_farm_id": plan.id,
                            "site_config": {
                                "linux_fx_version": app_spec.get("linux_fx_version", ""),
                                "app_settings": [
                                    {
                                        "name": setting["name"],
                                        "value": setting["value"]
                                    }
                                    for setting in app_spec.get("app_settings", [])
                                ]
                            },
                            "tags": app_spec.get("tags", {})
                        }
                    )
                    
                    app = poller.result()
                    
                    apps.append({
                        "name": app.name,
                        "id": app.id,
                        "location": app.location,
                        "default_host_name": app.default_host_name,
                        "resource_group": resource_group_name,
                        "plan": plan_name
                    })
                
            return {
                "plans": plans,
                "apps": apps
            }
        
        except AzureError as e:
            logger.error(f"Failed to provision App Service resources: {str(e)}")
            return {"error": str(e)}
    
    def cleanup_resources(self, resources: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean up provisioned Azure resources.
        
        Args:
            resources: Resource details to clean up
            
        Returns:
            Dict[str, Any]: Cleanup results
        """
        results = {}
        
        # Clean up App Service resources
        if "app_service" in resources:
            results["app_service"] = self._cleanup_app_service(resources["app_service"])
            
        # Clean up AKS clusters
        if "aks" in resources:
            results["aks"] = self._cleanup_aks(resources["aks"])
            
        # Clean up storage accounts
        if "storage" in resources:
            results["storage"] = self._cleanup_storage(resources["storage"])
            
        # Clean up virtual machines
        if "virtual_machines" in resources:
            results["virtual_machines"] = self._cleanup_virtual_machines(resources["virtual_machines"])
            
        # Clean up resource groups
        if "resource_group" in resources:
            results["resource_group"] = self._cleanup_resource_group(resources["resource_group"])
            
        return results
    
    def _cleanup_app_service(self, resources: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean up App Service resources.
        
        Args:
            resources: App Service resource details
            
        Returns:
            Dict[str, Any]: Cleanup results
        """
        web_client = azure.mgmt.web.WebSiteManagementClient(
            credential=self.credentials,
            subscription_id=self.subscription_id
        )
        results = {"success": [], "failed": []}
        
        try:
            # Delete apps first
            for app in resources.get("apps", []):
                app_name = app["name"]
                resource_group_name = app["resource_group"]
                
                try:
                    web_client.web_apps.begin_delete(resource_group_name, app_name).wait()
                    results["success"].append(f"app:{app_name}")
                except Exception as e:
                    results["failed"].append({"name": f"app:{app_name}", "error": str(e)})
            
            # Then delete plans
            for plan in resources.get("plans", []):
                plan_name = plan["name"]
                resource_group_name = plan["resource_group"]
                
                try:
                    web_client.app_service_plans.begin_delete(resource_group_name, plan_name).wait()
                    results["success"].append(f"plan:{plan_name}")
                except Exception as e:
                    results["failed"].append({"name": f"plan:{plan_name}", "error": str(e)})
                
            return results
        
        except AzureError as e:
            logger.error(f"Failed to clean up App Service resources: {str(e)}")
            results["failed"].append({"name": "app_service", "error": str(e)})
            return results
    
    def _cleanup_aks(self, resources: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean up AKS resources.
        
        Args:
            resources: AKS resource details
            
        Returns:
            Dict[str, Any]: Cleanup results
        """
        container_client = azure.mgmt.containerservice.ContainerServiceClient(
            credential=self.credentials,
            subscription_id=self.subscription_id
        )
        results = {"success": [], "failed": []}
        
        try:
            for cluster in resources.get("clusters", []):
                cluster_name = cluster["name"]
                resource_group_name = cluster["resource_group"]
                
                try:
                    container_client.managed_clusters.begin_delete(resource_group_name, cluster_name).wait()
                    results["success"].append(cluster_name)
                except Exception as e:
                    results["failed"].append({"name": cluster_name, "error": str(e)})
                
            return results
        
        except AzureError as e:
            logger.error(f"Failed to clean up AKS clusters: {str(e)}")
            results["failed"].append({"name": "aks", "error": str(e)})
            return results
    
    def _cleanup_storage(self, resources: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean up storage resources.
        
        Args:
            resources: Storage resource details
            
        Returns:
            Dict[str, Any]: Cleanup results
        """
        storage_client = azure.mgmt.storage.StorageManagementClient(
            credential=self.credentials,
            subscription_id=self.subscription_id
        )
        results = {"success": [], "failed": []}
        
        try:
            for account in resources.get("accounts", []):
                account_name = account["name"]
                resource_group_name = account["resource_group"]
                
                try:
                    storage_client.storage_accounts.delete(resource_group_name, account_name)
                    results["success"].append(account_name)
                except Exception as e:
                    results["failed"].append({"name": account_name, "error": str(e)})
                
            return results
        
        except AzureError as e:
            logger.error(f"Failed to clean up storage accounts: {str(e)}")
            results["failed"].append({"name": "storage", "error": str(e)})
            return results
    
    def _cleanup_virtual_machines(self, resources: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean up virtual machine resources.
        
        Args:
            resources: Virtual machine resource details
            
        Returns:
            Dict[str, Any]: Cleanup results
        """
        compute_client = azure.mgmt.compute.ComputeManagementClient(
            credential=self.credentials,
            subscription_id=self.subscription_id
        )
        results = {"success": [], "failed": []}
        
        try:
            for vm in resources.get("vms", []):
                vm_name = vm["name"]
                resource_group_name = vm["resource_group"]
                
                try:
                    compute_client.virtual_machines.begin_delete(resource_group_name, vm_name).wait()
                    results["success"].append(vm_name)
                except Exception as e:
                    results["failed"].append({"name": vm_name, "error": str(e)})
                
            return results
        
        except AzureError as e:
            logger.error(f"Failed to clean up virtual machines: {str(e)}")
            results["failed"].append({"name": "virtual_machines", "error": str(e)})
            return results
    
    def _cleanup_resource_group(self, resource_group: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean up a resource group.
        
        Args:
            resource_group: Resource group details
            
        Returns:
            Dict[str, Any]: Cleanup results
        """
        results = {"success": [], "failed": []}
        
        try:
            resource_group_name = resource_group["name"]
            
            try:
                self.resource_client.resource_groups.begin_delete(resource_group_name).wait()
                results["success"].append(resource_group_name)
            except Exception as e:
                results["failed"].append({"name": resource_group_name, "error": str(e)})
                
            return results
        
        except AzureError as e:
            logger.error(f"Failed to clean up resource group: {str(e)}")
            results["failed"].append({"name": "resource_group", "error": str(e)})
            return results


class AzureDeploymentHandler:
    """
    Handles deployment operations on Azure.
    
    This class manages the deployment of applications and services to Azure.
    """
    
    def __init__(self, subscription_id: str, credentials):
        """
        Initialize the Azure Deployment Handler.
        
        Args:
            subscription_id: Azure subscription ID
            credentials: Azure credentials
        """
        self.subscription_id = subscription_id
        self.credentials = credentials
        self.resource_client = azure.mgmt.resource.ResourceManagementClient(
            credential=credentials,
            subscription_id=subscription_id
        )
        
    def deploy_application(self, deployment_spec: Dict[str, Any]) -> AgentResponse:
        """
        Deploy an application to Azure.
        
        Args:
            deployment_spec: Deployment specifications
            
        Returns:
            AgentResponse: Deployment response
        """
        deployment_type = deployment_spec.get("type", "")
        
        if deployment_type == "arm_template":
            return self._deploy_arm_template(deployment_spec)
        elif deployment_type == "app_service":
            return self._deploy_app_service_application(deployment_spec)
        elif deployment_type == "aks":
            return self._deploy_aks_application(deployment_spec)
        elif deployment_type == "container_instance":
            return self._deploy_container_instance(deployment_spec)
        else:
            return AgentResponse(
                success=False,
                message=f"Unsupported deployment type: {deployment_type}",
                data={}
            )
    
    def _deploy_arm_template(self, spec: Dict[str, Any]) -> AgentResponse:
        """
        Deploy an ARM template.
        
        Args:
            spec: ARM template deployment specifications
            
        Returns:
            AgentResponse: Deployment response
        """
        try:
            resource_group_name = spec.get("resource_group")
            deployment_name = spec.get("deployment_name")
            template = spec.get("template")
            parameters = spec.get("parameters", {})
            
            # Deploy the ARM template
            poller = self.resource_client.deployments.begin_create_or_update(
                resource_group_name,
                deployment_name,
                {
                    "properties": {
                        "template": template,
                        "parameters": {
                            k: {"value": v} for k, v in parameters.items()
                        },
                        "mode": "Incremental"
                    }
                }
            )
            
            deployment = poller.result()
            
            # Get deployment outputs
            outputs = {}
            if deployment.properties.outputs:
                for key, value in deployment.properties.outputs.items():
                    outputs[key] = value.get("value")
            
            return AgentResponse(
                success=True,
                message=f"Successfully deployed ARM template: {deployment_name}",
                data={
                    "deployment_name": deployment_name,
                    "resource_group": resource_group_name,
                    "state": deployment.properties.provisioning_state,
                    "outputs": outputs
                }
            )
        
        except AzureError as e:
            logger.error(f"Failed to deploy ARM template: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to deploy ARM template: {str(e)}",
                data={}
            )
    
    def _deploy_app_service_application(self, spec: Dict[str, Any]) -> AgentResponse:
        """
        Deploy an application to App Service.
        
        Args:
            spec: App Service deployment specifications
            
        Returns:
            AgentResponse: Deployment response
        """
        web_client = azure.mgmt.web.WebSiteManagementClient(
            credential=self.credentials,
            subscription_id=self.subscription_id
        )
        
        try:
            resource_group_name = spec.get("resource_group")
            app_name = spec.get("app_name")
            package_url = spec.get("package_url")
            
            # Deploy the application package
            poller = web_client.web_apps.begin_deploy(
                resource_group_name,
                app_name,
                {
                    "properties": {
                        "package_uri": package_url
                    }
                }
            )
            
            deployment = poller.result()
            
            # Get the app details
            app = web_client.web_apps.get(resource_group_name, app_name)
            
            return AgentResponse(
                success=True,
                message=f"Successfully deployed application to App Service: {app_name}",
                data={
                    "app_name": app_name,
                    "resource_group": resource_group_name,
                    "default_host_name": app.default_host_name,
                    "state": app.state,
                    "url": f"https://{app.default_host_name}"
                }
            )
        
        except AzureError as e:
            logger.error(f"Failed to deploy App Service application: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to deploy App Service application: {str(e)}",
                data={}
            )
    
    def _deploy_aks_application(self, spec: Dict[str, Any]) -> AgentResponse:
        """
        Deploy an application to AKS.
        
        Args:
            spec: AKS deployment specifications
            
        Returns:
            AgentResponse: Deployment response
        """
        # For AKS deployments, we use kubectl commands through subprocess
        # This is a simplified implementation
        import subprocess
        import tempfile
        import os
        
        try:
            resource_group_name = spec.get("resource_group")
            cluster_name = spec.get("cluster_name")
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
                    "az", "aks", "get-credentials",
                    "--resource-group", resource_group_name,
                    "--name", cluster_name,
                    "--overwrite-existing"
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
                message=f"Successfully deployed application to AKS cluster: {cluster_name}, namespace: {namespace}",
                data={
                    "cluster_name": cluster_name,
                    "resource_group": resource_group_name,
                    "namespace": namespace,
                    "results": results
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to deploy AKS application: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to deploy AKS application: {str(e)}",
                data={}
            )
    
    def _deploy_container_instance(self, spec: Dict[str, Any]) -> AgentResponse:
        """
        Deploy a container instance.
        
        Args:
            spec: Container instance deployment specifications
            
        Returns:
            AgentResponse: Deployment response
        """
        aci_client = azure.mgmt.containerinstance.ContainerInstanceManagementClient(
            credential=self.credentials,
            subscription_id=self.subscription_id
        )
        
        try:
            resource_group_name = spec.get("resource_group")
            container_group_name = spec.get("container_group_name")
            location = spec.get("location", "eastus")
            image = spec.get("image")
            cpu = spec.get("cpu", 1.0)
            memory = spec.get("memory", 1.5)
            ports = spec.get("ports", [80])
            environment_variables = spec.get("environment_variables", [])
            
            # Create container group
            container_group = {
                "location": location,
                "containers": [
                    {
                        "name": container_group_name,
                        "image": image,
                        "resources": {
                            "requests": {
                                "memory_in_gb": memory,
                                "cpu": cpu
                            }
                        },
                        "ports": [
                            {
                                "port": port
                            }
                            for port in ports
                        ],
                        "environment_variables": [
                            {
                                "name": env["name"],
                                "value": env["value"]
                            }
                            for env in environment_variables
                        ]
                    }
                ],
                "os_type": "Linux",
                "ip_address": {
                    "type": "Public",
                    "ports": [
                        {
                            "protocol": "tcp",
                            "port": port
                        }
                        for port in ports
                    ]
                },
                "restart_policy": "Always"
            }
            
            # Deploy the container group
            poller = aci_client.container_groups.begin_create_or_update(
                resource_group_name,
                container_group_name,
                container_group
            )
            
            result = poller.result()
            
            return AgentResponse(
                success=True,
                message=f"Successfully deployed container instance: {container_group_name}",
                data={
                    "container_group_name": result.name,
                    "resource_group": resource_group_name,
                    "location": result.location,
                    "ip_address": result.ip_address.ip,
                    "state": result.provisioning_state,
                    "ports": [
                        {
                            "port": port.port,
                            "protocol": port.protocol
                        }
                        for port in result.ip_address.ports
                    ]
                }
            )
        
        except AzureError as e:
            logger.error(f"Failed to deploy container instance: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to deploy container instance: {str(e)}",
                data={}
            )
