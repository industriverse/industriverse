"""
Pulumi Integration Manager

This module provides integration with Pulumi for infrastructure as code deployment
in the Deployment Operations Layer. It handles Pulumi project management, stack operations,
and resource deployment across multiple cloud providers.

Classes:
    PulumiIntegrationManager: Manages Pulumi integration
    PulumiExecutor: Executes Pulumi commands
    PulumiStackManager: Manages Pulumi stacks
    PulumiProjectManager: Manages Pulumi projects
"""

import json
import logging
import os
import subprocess
import tempfile
import time
from typing import Dict, List, Any, Optional, Tuple

from ..agent.agent_utils import AgentResponse
from ..protocol.mcp_integration.mcp_context_schema import MCPContext

logger = logging.getLogger(__name__)

class PulumiIntegrationManager:
    """
    Manages Pulumi integration for the Deployment Operations Layer.
    
    This class provides a unified interface for interacting with Pulumi,
    handling project management, stack operations, and resource deployment.
    """
    
    def __init__(self, pulumi_binary_path: Optional[str] = None, 
                working_dir: Optional[str] = None):
        """
        Initialize the Pulumi Integration Manager.
        
        Args:
            pulumi_binary_path: Path to Pulumi binary (optional, defaults to 'pulumi' in PATH)
            working_dir: Working directory for Pulumi operations (optional)
        """
        self.pulumi_binary = pulumi_binary_path or "pulumi"
        self.working_dir = working_dir or tempfile.mkdtemp(prefix="pulumi_")
        
        self.executor = PulumiExecutor(self.pulumi_binary, self.working_dir)
        self.stack_manager = PulumiStackManager(self.executor)
        self.project_manager = PulumiProjectManager(self.executor, self.working_dir)
        
        # Ensure Pulumi is installed and available
        self._verify_pulumi_installation()
    
    def _verify_pulumi_installation(self):
        """
        Verify that Pulumi is installed and available.
        
        Raises:
            Exception: If Pulumi is not installed or not accessible
        """
        try:
            version_output = self.executor.run_command("version")
            logger.info(f"Pulumi version: {version_output}")
        except Exception as e:
            logger.error(f"Failed to verify Pulumi installation: {str(e)}")
            raise Exception(f"Pulumi not installed or not accessible: {str(e)}")
    
    def create_project(self, project_name: str, description: str, 
                      runtime: str = "python", template: Optional[str] = None) -> AgentResponse:
        """
        Create a new Pulumi project.
        
        Args:
            project_name: Name of the project
            description: Project description
            runtime: Project runtime (default: python)
            template: Project template (optional)
            
        Returns:
            AgentResponse: Project creation response
        """
        try:
            result = self.project_manager.create_project(project_name, description, runtime, template)
            
            return AgentResponse(
                success=True,
                message=f"Pulumi project {project_name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create Pulumi project: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create Pulumi project: {str(e)}",
                data={}
            )
    
    def create_stack(self, stack_name: str, project_dir: str) -> AgentResponse:
        """
        Create a new Pulumi stack.
        
        Args:
            stack_name: Name of the stack
            project_dir: Path to the project directory
            
        Returns:
            AgentResponse: Stack creation response
        """
        try:
            result = self.stack_manager.create_stack(stack_name, project_dir)
            
            return AgentResponse(
                success=True,
                message=f"Pulumi stack {stack_name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create Pulumi stack: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create Pulumi stack: {str(e)}",
                data={}
            )
    
    def set_stack_config(self, stack_name: str, project_dir: str, 
                        config_key: str, config_value: str, 
                        is_secret: bool = False) -> AgentResponse:
        """
        Set configuration for a Pulumi stack.
        
        Args:
            stack_name: Name of the stack
            project_dir: Path to the project directory
            config_key: Configuration key
            config_value: Configuration value
            is_secret: Whether the value is a secret
            
        Returns:
            AgentResponse: Configuration setting response
        """
        try:
            result = self.stack_manager.set_config(stack_name, project_dir, config_key, config_value, is_secret)
            
            return AgentResponse(
                success=True,
                message=f"Pulumi stack configuration set successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to set Pulumi stack configuration: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to set Pulumi stack configuration: {str(e)}",
                data={}
            )
    
    def generate_program(self, project_dir: str, resources: Dict[str, Any], 
                        provider_config: Dict[str, Any]) -> str:
        """
        Generate a Pulumi program from resource specifications.
        
        Args:
            project_dir: Path to the project directory
            resources: Resource specifications
            provider_config: Provider configuration
            
        Returns:
            str: Path to the generated Pulumi program
        """
        provider_type = provider_config.get("type", "aws")
        
        if provider_type == "aws":
            return self._generate_aws_program(project_dir, resources, provider_config)
        elif provider_type == "azure":
            return self._generate_azure_program(project_dir, resources, provider_config)
        elif provider_type == "gcp":
            return self._generate_gcp_program(project_dir, resources, provider_config)
        else:
            raise Exception(f"Unsupported provider type: {provider_type}")
    
    def _generate_aws_program(self, project_dir: str, resources: Dict[str, Any], 
                             provider_config: Dict[str, Any]) -> str:
        """
        Generate an AWS Pulumi program.
        
        Args:
            project_dir: Path to the project directory
            resources: Resource specifications
            provider_config: Provider configuration
            
        Returns:
            str: Path to the generated Pulumi program
        """
        program_file = os.path.join(project_dir, "__main__.py")
        
        # Generate program content
        content = """import pulumi
import pulumi_aws as aws

# Configure AWS provider
"""
        
        # Add provider configuration
        region = provider_config.get("attributes", {}).get("region", "us-west-2")
        content += f'aws_provider = aws.Provider("aws", region="{region}")\n\n'
        
        # Add resources
        for resource_type, resource_configs in resources.items():
            if not isinstance(resource_configs, list):
                resource_configs = [resource_configs]
                
            for resource_config in resource_configs:
                resource_name = resource_config.get("name", f"resource_{os.urandom(4).hex()}")
                resource_attrs = resource_config.get("attributes", {})
                
                if resource_type == "aws_instance":
                    content += self._generate_aws_instance(resource_name, resource_attrs)
                elif resource_type == "aws_s3_bucket":
                    content += self._generate_aws_s3_bucket(resource_name, resource_attrs)
                elif resource_type == "aws_db_instance":
                    content += self._generate_aws_db_instance(resource_name, resource_attrs)
                else:
                    content += self._generate_generic_resource(resource_type, resource_name, resource_attrs)
        
        # Add exports
        content += "\n# Export resource outputs\n"
        for resource_type, resource_configs in resources.items():
            if not isinstance(resource_configs, list):
                resource_configs = [resource_configs]
                
            for resource_config in resource_configs:
                resource_name = resource_config.get("name", f"resource_{os.urandom(4).hex()}")
                
                content += f'pulumi.export("{resource_name}_id", {resource_name}.id)\n'
                
                if resource_type == "aws_instance":
                    content += f'pulumi.export("{resource_name}_public_ip", {resource_name}.public_ip)\n'
                elif resource_type == "aws_s3_bucket":
                    content += f'pulumi.export("{resource_name}_bucket_domain_name", {resource_name}.bucket_domain_name)\n'
                elif resource_type == "aws_db_instance":
                    content += f'pulumi.export("{resource_name}_endpoint", {resource_name}.endpoint)\n'
        
        # Write program to file
        with open(program_file, "w") as f:
            f.write(content)
        
        # Create requirements.txt
        requirements_file = os.path.join(project_dir, "requirements.txt")
        with open(requirements_file, "w") as f:
            f.write("pulumi>=3.0.0,<4.0.0\n")
            f.write("pulumi-aws>=5.0.0,<6.0.0\n")
        
        return program_file
    
    def _generate_aws_instance(self, resource_name: str, attrs: Dict[str, Any]) -> str:
        """
        Generate AWS EC2 instance resource code.
        
        Args:
            resource_name: Resource name
            attrs: Resource attributes
            
        Returns:
            str: Resource code
        """
        ami = attrs.get("ami", "ami-0c55b159cbfafe1f0")
        instance_type = attrs.get("instance_type", "t2.micro")
        tags = attrs.get("tags", {})
        
        code = f"""
# Create an EC2 instance
{resource_name} = aws.ec2.Instance("{resource_name}",
    ami="{ami}",
    instance_type="{instance_type}",
"""
        
        if tags:
            code += "    tags={\n"
            for key, value in tags.items():
                code += f'        "{key}": "{value}",\n'
            code += "    },\n"
        
        code += ")\n\n"
        
        return code
    
    def _generate_aws_s3_bucket(self, resource_name: str, attrs: Dict[str, Any]) -> str:
        """
        Generate AWS S3 bucket resource code.
        
        Args:
            resource_name: Resource name
            attrs: Resource attributes
            
        Returns:
            str: Resource code
        """
        bucket = attrs.get("bucket")
        acl = attrs.get("acl", "private")
        tags = attrs.get("tags", {})
        
        code = f"""
# Create an S3 bucket
{resource_name} = aws.s3.Bucket("{resource_name}",
"""
        
        if bucket:
            code += f'    bucket="{bucket}",\n'
        
        code += f'    acl="{acl}",\n'
        
        if tags:
            code += "    tags={\n"
            for key, value in tags.items():
                code += f'        "{key}": "{value}",\n'
            code += "    },\n"
        
        code += ")\n\n"
        
        return code
    
    def _generate_aws_db_instance(self, resource_name: str, attrs: Dict[str, Any]) -> str:
        """
        Generate AWS RDS instance resource code.
        
        Args:
            resource_name: Resource name
            attrs: Resource attributes
            
        Returns:
            str: Resource code
        """
        engine = attrs.get("engine", "mysql")
        instance_class = attrs.get("instance_class", "db.t2.micro")
        allocated_storage = attrs.get("allocated_storage", 10)
        username = attrs.get("username", "admin")
        password = attrs.get("password", "password")
        
        code = f"""
# Create an RDS instance
{resource_name} = aws.rds.Instance("{resource_name}",
    engine="{engine}",
    instance_class="{instance_class}",
    allocated_storage={allocated_storage},
    username="{username}",
    password="{password}",
    skip_final_snapshot=True,
"""
        
        code += ")\n\n"
        
        return code
    
    def _generate_azure_program(self, project_dir: str, resources: Dict[str, Any], 
                               provider_config: Dict[str, Any]) -> str:
        """
        Generate an Azure Pulumi program.
        
        Args:
            project_dir: Path to the project directory
            resources: Resource specifications
            provider_config: Provider configuration
            
        Returns:
            str: Path to the generated Pulumi program
        """
        program_file = os.path.join(project_dir, "__main__.py")
        
        # Generate program content
        content = """import pulumi
import pulumi_azure_native as azure_native

# Configure Azure provider
"""
        
        # Add provider configuration
        location = provider_config.get("attributes", {}).get("location", "westus")
        content += f'azure_provider = azure_native.Provider("azure")\n\n'
        
        # Create a resource group for all resources
        content += f"""
# Create a resource group
resource_group = azure_native.resources.ResourceGroup("resourceGroup",
    location="{location}"
)

"""
        
        # Add resources
        for resource_type, resource_configs in resources.items():
            if not isinstance(resource_configs, list):
                resource_configs = [resource_configs]
                
            for resource_config in resource_configs:
                resource_name = resource_config.get("name", f"resource_{os.urandom(4).hex()}")
                resource_attrs = resource_config.get("attributes", {})
                
                if resource_type == "azurerm_virtual_machine":
                    content += self._generate_azure_vm(resource_name, resource_attrs, location)
                elif resource_type == "azurerm_storage_account":
                    content += self._generate_azure_storage(resource_name, resource_attrs, location)
                elif resource_type == "azurerm_sql_server":
                    content += self._generate_azure_sql(resource_name, resource_attrs, location)
                else:
                    content += self._generate_generic_resource(resource_type, resource_name, resource_attrs)
        
        # Add exports
        content += "\n# Export resource outputs\n"
        content += 'pulumi.export("resource_group_name", resource_group.name)\n'
        
        for resource_type, resource_configs in resources.items():
            if not isinstance(resource_configs, list):
                resource_configs = [resource_configs]
                
            for resource_config in resource_configs:
                resource_name = resource_config.get("name", f"resource_{os.urandom(4).hex()}")
                
                content += f'pulumi.export("{resource_name}_id", {resource_name}.id)\n'
                
                if resource_type == "azurerm_virtual_machine":
                    content += f'pulumi.export("{resource_name}_name", {resource_name}.name)\n'
                elif resource_type == "azurerm_storage_account":
                    content += f'pulumi.export("{resource_name}_primary_blob_endpoint", {resource_name}.primary_blob_endpoint)\n'
                elif resource_type == "azurerm_sql_server":
                    content += f'pulumi.export("{resource_name}_fully_qualified_domain_name", {resource_name}.fully_qualified_domain_name)\n'
        
        # Write program to file
        with open(program_file, "w") as f:
            f.write(content)
        
        # Create requirements.txt
        requirements_file = os.path.join(project_dir, "requirements.txt")
        with open(requirements_file, "w") as f:
            f.write("pulumi>=3.0.0,<4.0.0\n")
            f.write("pulumi-azure-native>=1.0.0,<2.0.0\n")
        
        return program_file
    
    def _generate_azure_vm(self, resource_name: str, attrs: Dict[str, Any], location: str) -> str:
        """
        Generate Azure VM resource code.
        
        Args:
            resource_name: Resource name
            attrs: Resource attributes
            location: Azure location
            
        Returns:
            str: Resource code
        """
        vm_size = attrs.get("vm_size", "Standard_DS1_v2")
        admin_username = attrs.get("admin_username", "adminuser")
        
        code = f"""
# Create a virtual machine
{resource_name} = azure_native.compute.VirtualMachine("{resource_name}",
    resource_group_name=resource_group.name,
    location="{location}",
    vm_size="{vm_size}",
    os_profile=azure_native.compute.OSProfileArgs(
        computer_name="{resource_name}",
        admin_username="{admin_username}",
        admin_password="Password1234!",
    ),
    network_profile=azure_native.compute.NetworkProfileArgs(
        network_interfaces=[
            azure_native.compute.NetworkInterfaceReferenceArgs(
                id=network_interface.id,
                primary=True,
            ),
        ],
    ),
    storage_profile=azure_native.compute.StorageProfileArgs(
        os_disk=azure_native.compute.OSDiskArgs(
            create_option="FromImage",
            managed_disk=azure_native.compute.ManagedDiskParametersArgs(
                storage_account_type="Standard_LRS",
            ),
        ),
        image_reference=azure_native.compute.ImageReferenceArgs(
            publisher="Canonical",
            offer="UbuntuServer",
            sku="18.04-LTS",
            version="latest",
        ),
    ),
)

"""
        
        return code
    
    def _generate_azure_storage(self, resource_name: str, attrs: Dict[str, Any], location: str) -> str:
        """
        Generate Azure Storage Account resource code.
        
        Args:
            resource_name: Resource name
            attrs: Resource attributes
            location: Azure location
            
        Returns:
            str: Resource code
        """
        account_tier = attrs.get("account_tier", "Standard")
        account_replication_type = attrs.get("account_replication_type", "LRS")
        
        code = f"""
# Create a storage account
{resource_name} = azure_native.storage.StorageAccount("{resource_name}",
    resource_group_name=resource_group.name,
    location="{location}",
    sku=azure_native.storage.SkuArgs(
        name="{account_tier}_{account_replication_type}",
    ),
    kind="StorageV2",
)

"""
        
        return code
    
    def _generate_azure_sql(self, resource_name: str, attrs: Dict[str, Any], location: str) -> str:
        """
        Generate Azure SQL Server resource code.
        
        Args:
            resource_name: Resource name
            attrs: Resource attributes
            location: Azure location
            
        Returns:
            str: Resource code
        """
        admin_login = attrs.get("admin_login", "adminuser")
        admin_password = attrs.get("admin_password", "Password1234!")
        
        code = f"""
# Create a SQL server
{resource_name} = azure_native.sql.Server("{resource_name}",
    resource_group_name=resource_group.name,
    location="{location}",
    administrator_login="{admin_login}",
    administrator_login_password="{admin_password}",
    version="12.0",
)

"""
        
        return code
    
    def _generate_gcp_program(self, project_dir: str, resources: Dict[str, Any], 
                             provider_config: Dict[str, Any]) -> str:
        """
        Generate a GCP Pulumi program.
        
        Args:
            project_dir: Path to the project directory
            resources: Resource specifications
            provider_config: Provider configuration
            
        Returns:
            str: Path to the generated Pulumi program
        """
        program_file = os.path.join(project_dir, "__main__.py")
        
        # Generate program content
        content = """import pulumi
import pulumi_gcp as gcp

# Configure GCP provider
"""
        
        # Add provider configuration
        project = provider_config.get("attributes", {}).get("project")
        region = provider_config.get("attributes", {}).get("region", "us-central1")
        zone = provider_config.get("attributes", {}).get("zone", "us-central1-a")
        
        content += f'gcp_provider = gcp.Provider("gcp"'
        if project:
            content += f', project="{project}"'
        content += f', region="{region}"'
        content += f', zone="{zone}"'
        content += ')\n\n'
        
        # Add resources
        for resource_type, resource_configs in resources.items():
            if not isinstance(resource_configs, list):
                resource_configs = [resource_configs]
                
            for resource_config in resource_configs:
                resource_name = resource_config.get("name", f"resource_{os.urandom(4).hex()}")
                resource_attrs = resource_config.get("attributes", {})
                
                if resource_type == "google_compute_instance":
                    content += self._generate_gcp_instance(resource_name, resource_attrs, zone)
                elif resource_type == "google_storage_bucket":
                    content += self._generate_gcp_bucket(resource_name, resource_attrs)
                elif resource_type == "google_sql_database_instance":
                    content += self._generate_gcp_sql(resource_name, resource_attrs, region)
                else:
                    content += self._generate_generic_resource(resource_type, resource_name, resource_attrs)
        
        # Add exports
        content += "\n# Export resource outputs\n"
        for resource_type, resource_configs in resources.items():
            if not isinstance(resource_configs, list):
                resource_configs = [resource_configs]
                
            for resource_config in resource_configs:
                resource_name = resource_config.get("name", f"resource_{os.urandom(4).hex()}")
                
                content += f'pulumi.export("{resource_name}_id", {resource_name}.id)\n'
                
                if resource_type == "google_compute_instance":
                    content += f'pulumi.export("{resource_name}_network_ip", {resource_name}.network_interface[0].network_ip)\n'
                elif resource_type == "google_storage_bucket":
                    content += f'pulumi.export("{resource_name}_url", {resource_name}.url)\n'
                elif resource_type == "google_sql_database_instance":
                    content += f'pulumi.export("{resource_name}_connection_name", {resource_name}.connection_name)\n'
        
        # Write program to file
        with open(program_file, "w") as f:
            f.write(content)
        
        # Create requirements.txt
        requirements_file = os.path.join(project_dir, "requirements.txt")
        with open(requirements_file, "w") as f:
            f.write("pulumi>=3.0.0,<4.0.0\n")
            f.write("pulumi-gcp>=6.0.0,<7.0.0\n")
        
        return program_file
    
    def _generate_gcp_instance(self, resource_name: str, attrs: Dict[str, Any], zone: str) -> str:
        """
        Generate GCP Compute Instance resource code.
        
        Args:
            resource_name: Resource name
            attrs: Resource attributes
            zone: GCP zone
            
        Returns:
            str: Resource code
        """
        machine_type = attrs.get("machine_type", "f1-micro")
        image = attrs.get("image", "debian-cloud/debian-10")
        
        code = f"""
# Create a compute instance
{resource_name} = gcp.compute.Instance("{resource_name}",
    machine_type="{machine_type}",
    zone="{zone}",
    boot_disk=gcp.compute.InstanceBootDiskArgs(
        initialize_params=gcp.compute.InstanceBootDiskInitializeParamsArgs(
            image="{image}",
        ),
    ),
    network_interfaces=[
        gcp.compute.InstanceNetworkInterfaceArgs(
            network="default",
            access_configs=[gcp.compute.InstanceNetworkInterfaceAccessConfigArgs()],
        ),
    ],
)

"""
        
        return code
    
    def _generate_gcp_bucket(self, resource_name: str, attrs: Dict[str, Any]) -> str:
        """
        Generate GCP Storage Bucket resource code.
        
        Args:
            resource_name: Resource name
            attrs: Resource attributes
            
        Returns:
            str: Resource code
        """
        name = attrs.get("name")
        location = attrs.get("location", "US")
        
        code = f"""
# Create a storage bucket
{resource_name} = gcp.storage.Bucket("{resource_name}",
"""
        
        if name:
            code += f'    name="{name}",\n'
        
        code += f'    location="{location}",\n'
        code += ")\n\n"
        
        return code
    
    def _generate_gcp_sql(self, resource_name: str, attrs: Dict[str, Any], region: str) -> str:
        """
        Generate GCP SQL Database Instance resource code.
        
        Args:
            resource_name: Resource name
            attrs: Resource attributes
            region: GCP region
            
        Returns:
            str: Resource code
        """
        database_version = attrs.get("database_version", "MYSQL_5_7")
        tier = attrs.get("tier", "db-f1-micro")
        
        code = f"""
# Create a SQL database instance
{resource_name} = gcp.sql.DatabaseInstance("{resource_name}",
    database_version="{database_version}",
    region="{region}",
    settings=gcp.sql.DatabaseInstanceSettingsArgs(
        tier="{tier}",
    ),
)

"""
        
        return code
    
    def _generate_generic_resource(self, resource_type: str, resource_name: str, attrs: Dict[str, Any]) -> str:
        """
        Generate generic resource code.
        
        Args:
            resource_type: Resource type
            resource_name: Resource name
            attrs: Resource attributes
            
        Returns:
            str: Resource code
        """
        # Convert resource_type to Pulumi format (e.g., aws_instance -> aws.ec2.Instance)
        parts = resource_type.split("_")
        provider = parts[0]
        
        if provider == "aws":
            if parts[1] == "instance":
                service = "ec2"
                resource_class = "Instance"
            elif parts[1] == "s3" and parts[2] == "bucket":
                service = "s3"
                resource_class = "Bucket"
            elif parts[1] == "db" and parts[2] == "instance":
                service = "rds"
                resource_class = "Instance"
            else:
                service = parts[1]
                resource_class = "".join(p.capitalize() for p in parts[2:])
        elif provider == "azurerm":
            service = "azure_native"
            resource_class = "".join(p.capitalize() for p in parts[1:])
        elif provider == "google":
            service = "gcp"
            resource_class = "".join(p.capitalize() for p in parts[1:])
        else:
            service = provider
            resource_class = "".join(p.capitalize() for p in parts[1:])
        
        code = f"""
# Create a {resource_type}
{resource_name} = {service}.{resource_class}("{resource_name}",
"""
        
        for key, value in attrs.items():
            if isinstance(value, str):
                code += f'    {key}="{value}",\n'
            elif isinstance(value, (list, dict)):
                code += f'    {key}={value},\n'
            else:
                code += f'    {key}={value},\n'
        
        code += ")\n\n"
        
        return code
    
    def deploy_stack(self, stack_name: str, project_dir: str) -> AgentResponse:
        """
        Deploy a Pulumi stack.
        
        Args:
            stack_name: Name of the stack
            project_dir: Path to the project directory
            
        Returns:
            AgentResponse: Deployment response
        """
        try:
            # Select the stack
            self.stack_manager.select_stack(stack_name, project_dir)
            
            # Deploy the stack
            result = self.stack_manager.update_stack(project_dir)
            
            return AgentResponse(
                success=True,
                message=f"Pulumi stack {stack_name} deployed successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to deploy Pulumi stack: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to deploy Pulumi stack: {str(e)}",
                data={}
            )
    
    def destroy_stack(self, stack_name: str, project_dir: str) -> AgentResponse:
        """
        Destroy a Pulumi stack.
        
        Args:
            stack_name: Name of the stack
            project_dir: Path to the project directory
            
        Returns:
            AgentResponse: Destruction response
        """
        try:
            # Select the stack
            self.stack_manager.select_stack(stack_name, project_dir)
            
            # Destroy the stack
            result = self.stack_manager.destroy_stack(project_dir)
            
            return AgentResponse(
                success=True,
                message=f"Pulumi stack {stack_name} destroyed successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to destroy Pulumi stack: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to destroy Pulumi stack: {str(e)}",
                data={}
            )
    
    def get_stack_outputs(self, stack_name: str, project_dir: str) -> AgentResponse:
        """
        Get outputs from a Pulumi stack.
        
        Args:
            stack_name: Name of the stack
            project_dir: Path to the project directory
            
        Returns:
            AgentResponse: Stack outputs response
        """
        try:
            # Select the stack
            self.stack_manager.select_stack(stack_name, project_dir)
            
            # Get stack outputs
            outputs = self.stack_manager.get_outputs(project_dir)
            
            return AgentResponse(
                success=True,
                message=f"Retrieved outputs from Pulumi stack {stack_name}",
                data={
                    "outputs": outputs
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to get Pulumi stack outputs: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to get Pulumi stack outputs: {str(e)}",
                data={}
            )
    
    def list_stacks(self, project_dir: str) -> AgentResponse:
        """
        List all Pulumi stacks for a project.
        
        Args:
            project_dir: Path to the project directory
            
        Returns:
            AgentResponse: Stack list response
        """
        try:
            stacks = self.stack_manager.list_stacks(project_dir)
            
            return AgentResponse(
                success=True,
                message=f"Found {len(stacks)} Pulumi stacks",
                data={
                    "stacks": stacks
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to list Pulumi stacks: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to list Pulumi stacks: {str(e)}",
                data={}
            )
    
    def to_mcp_context(self) -> MCPContext:
        """
        Convert Pulumi integration information to MCP context.
        
        Returns:
            MCPContext: MCP context with Pulumi integration information
        """
        return MCPContext(
            context_type="pulumi_integration",
            pulumi_version=self._get_pulumi_version(),
            working_dir=self.working_dir
        )
    
    def _get_pulumi_version(self) -> str:
        """
        Get the Pulumi version.
        
        Returns:
            str: Pulumi version
        """
        try:
            version_output = self.executor.run_command("version")
            # Extract version number from output
            version_line = version_output.split("\n")[0]
            version = version_line.split("v")[1].strip()
            return version
        except Exception as e:
            logger.error(f"Failed to get Pulumi version: {str(e)}")
            return "unknown"


class PulumiExecutor:
    """
    Executes Pulumi commands.
    
    This class provides methods for executing Pulumi commands and handling their output.
    """
    
    def __init__(self, pulumi_binary: str, working_dir: str):
        """
        Initialize the Pulumi Executor.
        
        Args:
            pulumi_binary: Path to Pulumi binary
            working_dir: Working directory for Pulumi operations
        """
        self.pulumi_binary = pulumi_binary
        self.working_dir = working_dir
    
    def run_command(self, command: str, args: Optional[List[str]] = None, 
                   working_dir: Optional[str] = None) -> str:
        """
        Run a Pulumi command.
        
        Args:
            command: Pulumi command to run
            args: Command arguments (optional)
            working_dir: Working directory for the command (optional)
            
        Returns:
            str: Command output
            
        Raises:
            Exception: If the command fails
        """
        cmd_args = [self.pulumi_binary, command]
        
        if args:
            cmd_args.extend(args)
        
        logger.info(f"Running Pulumi command: {' '.join(cmd_args)}")
        
        try:
            result = subprocess.run(
                cmd_args,
                cwd=working_dir or self.working_dir,
                capture_output=True,
                text=True,
                check=True
            )
            
            return result.stdout
        
        except subprocess.CalledProcessError as e:
            error_message = f"Pulumi command failed: {e.stderr}"
            logger.error(error_message)
            raise Exception(error_message)


class PulumiStackManager:
    """
    Manages Pulumi stacks.
    
    This class provides methods for managing Pulumi stacks,
    including stack creation, selection, and operations.
    """
    
    def __init__(self, executor: PulumiExecutor):
        """
        Initialize the Pulumi Stack Manager.
        
        Args:
            executor: Pulumi executor
        """
        self.executor = executor
    
    def create_stack(self, stack_name: str, project_dir: str) -> Dict[str, Any]:
        """
        Create a new Pulumi stack.
        
        Args:
            stack_name: Name of the stack
            project_dir: Path to the project directory
            
        Returns:
            Dict[str, Any]: Stack creation result
        """
        try:
            output = self.executor.run_command("stack", args=["init", stack_name], working_dir=project_dir)
            
            return {
                "stack_name": stack_name,
                "output": output
            }
        
        except Exception as e:
            # If stack already exists, select it instead
            if "already exists" in str(e):
                self.select_stack(stack_name, project_dir)
                
                return {
                    "stack_name": stack_name,
                    "output": f"Stack {stack_name} already exists, selected it"
                }
            else:
                raise
    
    def select_stack(self, stack_name: str, project_dir: str) -> Dict[str, Any]:
        """
        Select a Pulumi stack.
        
        Args:
            stack_name: Name of the stack
            project_dir: Path to the project directory
            
        Returns:
            Dict[str, Any]: Stack selection result
        """
        output = self.executor.run_command("stack", args=["select", stack_name], working_dir=project_dir)
        
        return {
            "stack_name": stack_name,
            "output": output
        }
    
    def list_stacks(self, project_dir: str) -> List[Dict[str, Any]]:
        """
        List all Pulumi stacks for a project.
        
        Args:
            project_dir: Path to the project directory
            
        Returns:
            List[Dict[str, Any]]: List of stacks
        """
        output = self.executor.run_command("stack", args=["ls", "--json"], working_dir=project_dir)
        
        try:
            stacks_json = json.loads(output)
            return stacks_json
        except json.JSONDecodeError:
            # If JSON parsing fails, parse the output manually
            stacks = []
            lines = output.strip().split("\n")
            
            for line in lines:
                if line.startswith("*"):
                    line = line[1:].strip()
                    is_current = True
                else:
                    line = line.strip()
                    is_current = False
                
                if line:
                    stacks.append({
                        "name": line,
                        "current": is_current
                    })
            
            return stacks
    
    def update_stack(self, project_dir: str) -> Dict[str, Any]:
        """
        Update (deploy) a Pulumi stack.
        
        Args:
            project_dir: Path to the project directory
            
        Returns:
            Dict[str, Any]: Stack update result
        """
        output = self.executor.run_command("up", args=["--yes"], working_dir=project_dir)
        
        # Parse the output to extract information about created resources
        resources = []
        lines = output.strip().split("\n")
        
        for line in lines:
            if "+ " in line and " created" in line:
                resource_info = line.split("+ ")[1].split(" created")[0].strip()
                resources.append(resource_info)
        
        return {
            "output": output,
            "resources_created": resources
        }
    
    def destroy_stack(self, project_dir: str) -> Dict[str, Any]:
        """
        Destroy a Pulumi stack.
        
        Args:
            project_dir: Path to the project directory
            
        Returns:
            Dict[str, Any]: Stack destruction result
        """
        output = self.executor.run_command("destroy", args=["--yes"], working_dir=project_dir)
        
        # Parse the output to extract information about destroyed resources
        resources = []
        lines = output.strip().split("\n")
        
        for line in lines:
            if "- " in line and " deleted" in line:
                resource_info = line.split("- ")[1].split(" deleted")[0].strip()
                resources.append(resource_info)
        
        return {
            "output": output,
            "resources_destroyed": resources
        }
    
    def get_outputs(self, project_dir: str) -> Dict[str, Any]:
        """
        Get outputs from a Pulumi stack.
        
        Args:
            project_dir: Path to the project directory
            
        Returns:
            Dict[str, Any]: Stack outputs
        """
        output = self.executor.run_command("stack", args=["output", "--json"], working_dir=project_dir)
        
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            return {"error": "Failed to parse stack outputs"}
    
    def set_config(self, stack_name: str, project_dir: str, 
                  key: str, value: str, is_secret: bool = False) -> Dict[str, Any]:
        """
        Set configuration for a Pulumi stack.
        
        Args:
            stack_name: Name of the stack
            project_dir: Path to the project directory
            key: Configuration key
            value: Configuration value
            is_secret: Whether the value is a secret
            
        Returns:
            Dict[str, Any]: Configuration setting result
        """
        # Select the stack first
        self.select_stack(stack_name, project_dir)
        
        # Set the configuration
        args = ["config", "set"]
        
        if is_secret:
            args.append("--secret")
        
        args.extend([key, value])
        
        output = self.executor.run_command("config", args=args, working_dir=project_dir)
        
        return {
            "stack_name": stack_name,
            "key": key,
            "is_secret": is_secret,
            "output": output
        }
    
    def get_config(self, stack_name: str, project_dir: str, key: str) -> Dict[str, Any]:
        """
        Get configuration from a Pulumi stack.
        
        Args:
            stack_name: Name of the stack
            project_dir: Path to the project directory
            key: Configuration key
            
        Returns:
            Dict[str, Any]: Configuration value
        """
        # Select the stack first
        self.select_stack(stack_name, project_dir)
        
        # Get the configuration
        try:
            output = self.executor.run_command("config", args=["get", key], working_dir=project_dir)
            
            return {
                "stack_name": stack_name,
                "key": key,
                "value": output.strip()
            }
        
        except Exception as e:
            if "no value" in str(e):
                return {
                    "stack_name": stack_name,
                    "key": key,
                    "value": None
                }
            else:
                raise


class PulumiProjectManager:
    """
    Manages Pulumi projects.
    
    This class provides methods for managing Pulumi projects,
    including project creation and configuration.
    """
    
    def __init__(self, executor: PulumiExecutor, working_dir: str):
        """
        Initialize the Pulumi Project Manager.
        
        Args:
            executor: Pulumi executor
            working_dir: Working directory for project operations
        """
        self.executor = executor
        self.working_dir = working_dir
    
    def create_project(self, project_name: str, description: str, 
                      runtime: str = "python", template: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new Pulumi project.
        
        Args:
            project_name: Name of the project
            description: Project description
            runtime: Project runtime (default: python)
            template: Project template (optional)
            
        Returns:
            Dict[str, Any]: Project creation result
        """
        # Create project directory
        project_dir = os.path.join(self.working_dir, project_name)
        os.makedirs(project_dir, exist_ok=True)
        
        # Create Pulumi.yaml
        pulumi_yaml = {
            "name": project_name,
            "runtime": runtime,
            "description": description
        }
        
        with open(os.path.join(project_dir, "Pulumi.yaml"), "w") as f:
            f.write(f"name: {project_name}\n")
            f.write(f"runtime: {runtime}\n")
            f.write(f"description: {description}\n")
        
        # If template is provided, use it to initialize the project
        if template:
            try:
                self.executor.run_command("new", args=[template, "--dir", project_dir, "--force"], working_dir=self.working_dir)
            except Exception as e:
                logger.warning(f"Failed to apply template {template}: {str(e)}")
        
        return {
            "project_name": project_name,
            "project_dir": project_dir,
            "runtime": runtime,
            "description": description
        }
    
    def get_project_info(self, project_dir: str) -> Dict[str, Any]:
        """
        Get information about a Pulumi project.
        
        Args:
            project_dir: Path to the project directory
            
        Returns:
            Dict[str, Any]: Project information
        """
        try:
            # Read Pulumi.yaml
            with open(os.path.join(project_dir, "Pulumi.yaml"), "r") as f:
                yaml_content = f.read()
            
            # Parse basic information
            name = None
            runtime = None
            description = None
            
            for line in yaml_content.split("\n"):
                if line.startswith("name:"):
                    name = line.split("name:")[1].strip()
                elif line.startswith("runtime:"):
                    runtime = line.split("runtime:")[1].strip()
                elif line.startswith("description:"):
                    description = line.split("description:")[1].strip()
            
            return {
                "name": name,
                "runtime": runtime,
                "description": description,
                "project_dir": project_dir
            }
        
        except Exception as e:
            logger.error(f"Failed to get project information: {str(e)}")
            return {
                "error": str(e),
                "project_dir": project_dir
            }
