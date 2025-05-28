"""
Terraform Integration Manager

This module provides integration with Terraform for infrastructure as code deployment
in the Deployment Operations Layer. It handles Terraform configuration generation,
execution, state management, and module integration.

Classes:
    TerraformIntegrationManager: Manages Terraform integration
    TerraformExecutor: Executes Terraform commands
    TerraformStateManager: Manages Terraform state
    TerraformModuleRegistry: Manages Terraform modules
"""

import json
import logging
import os
import subprocess
import tempfile
from typing import Dict, List, Any, Optional, Tuple

from ..agent.agent_utils import AgentResponse
from ..protocol.mcp_integration.mcp_context_schema import MCPContext

logger = logging.getLogger(__name__)

class TerraformIntegrationManager:
    """
    Manages Terraform integration for the Deployment Operations Layer.
    
    This class provides a unified interface for interacting with Terraform,
    handling configuration generation, execution, state management, and module integration.
    """
    
    def __init__(self, terraform_binary_path: Optional[str] = None, 
                working_dir: Optional[str] = None):
        """
        Initialize the Terraform Integration Manager.
        
        Args:
            terraform_binary_path: Path to Terraform binary (optional, defaults to 'terraform' in PATH)
            working_dir: Working directory for Terraform operations (optional)
        """
        self.terraform_binary = terraform_binary_path or "terraform"
        self.working_dir = working_dir or tempfile.mkdtemp(prefix="terraform_")
        
        self.executor = TerraformExecutor(self.terraform_binary, self.working_dir)
        self.state_manager = TerraformStateManager(self.executor)
        self.module_registry = TerraformModuleRegistry(self.working_dir)
        
        # Ensure Terraform is installed and available
        self._verify_terraform_installation()
    
    def _verify_terraform_installation(self):
        """
        Verify that Terraform is installed and available.
        
        Raises:
            Exception: If Terraform is not installed or not accessible
        """
        try:
            version_output = self.executor.run_command("version")
            logger.info(f"Terraform version: {version_output}")
        except Exception as e:
            logger.error(f"Failed to verify Terraform installation: {str(e)}")
            raise Exception(f"Terraform not installed or not accessible: {str(e)}")
    
    def generate_configuration(self, resources: Dict[str, Any], 
                              provider_config: Dict[str, Any],
                              variables: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate Terraform configuration from resource specifications.
        
        Args:
            resources: Resource specifications
            provider_config: Provider configuration
            variables: Terraform variables (optional)
            
        Returns:
            str: Path to generated Terraform configuration directory
        """
        # Create a new directory for this configuration
        config_dir = os.path.join(self.working_dir, f"config_{os.urandom(4).hex()}")
        os.makedirs(config_dir, exist_ok=True)
        
        # Generate provider configuration
        provider_hcl = self._generate_provider_hcl(provider_config)
        with open(os.path.join(config_dir, "provider.tf"), "w") as f:
            f.write(provider_hcl)
        
        # Generate resource configuration
        resource_hcl = self._generate_resource_hcl(resources)
        with open(os.path.join(config_dir, "resources.tf"), "w") as f:
            f.write(resource_hcl)
        
        # Generate variables configuration if provided
        if variables:
            variables_hcl = self._generate_variables_hcl(variables)
            with open(os.path.join(config_dir, "variables.tf"), "w") as f:
                f.write(variables_hcl)
            
            # Generate terraform.tfvars file with variable values
            with open(os.path.join(config_dir, "terraform.tfvars"), "w") as f:
                for var_name, var_value in variables.items():
                    if isinstance(var_value, str):
                        f.write(f'{var_name} = "{var_value}"\n')
                    elif isinstance(var_value, (list, dict)):
                        f.write(f'{var_name} = {json.dumps(var_value)}\n')
                    else:
                        f.write(f'{var_name} = {var_value}\n')
        
        # Generate outputs configuration
        outputs_hcl = self._generate_outputs_hcl(resources)
        with open(os.path.join(config_dir, "outputs.tf"), "w") as f:
            f.write(outputs_hcl)
        
        return config_dir
    
    def _generate_provider_hcl(self, provider_config: Dict[str, Any]) -> str:
        """
        Generate Terraform provider configuration in HCL format.
        
        Args:
            provider_config: Provider configuration
            
        Returns:
            str: Provider configuration in HCL format
        """
        provider_type = provider_config.get("type", "aws")
        provider_attrs = provider_config.get("attributes", {})
        
        hcl = f'provider "{provider_type}" {{\n'
        
        for key, value in provider_attrs.items():
            if isinstance(value, str):
                hcl += f'  {key} = "{value}"\n'
            elif isinstance(value, (list, dict)):
                hcl += f'  {key} = {json.dumps(value)}\n'
            else:
                hcl += f'  {key} = {value}\n'
        
        hcl += '}\n'
        
        return hcl
    
    def _generate_resource_hcl(self, resources: Dict[str, Any]) -> str:
        """
        Generate Terraform resource configuration in HCL format.
        
        Args:
            resources: Resource specifications
            
        Returns:
            str: Resource configuration in HCL format
        """
        hcl = ""
        
        for resource_type, resource_configs in resources.items():
            if not isinstance(resource_configs, list):
                resource_configs = [resource_configs]
                
            for resource_config in resource_configs:
                resource_name = resource_config.get("name", f"resource_{os.urandom(4).hex()}")
                resource_attrs = resource_config.get("attributes", {})
                
                hcl += f'resource "{resource_type}" "{resource_name}" {{\n'
                
                for key, value in resource_attrs.items():
                    if isinstance(value, str):
                        hcl += f'  {key} = "{value}"\n'
                    elif isinstance(value, (list, dict)):
                        hcl += self._generate_nested_hcl(key, value, 2)
                    else:
                        hcl += f'  {key} = {value}\n'
                
                hcl += '}\n\n'
        
        return hcl
    
    def _generate_nested_hcl(self, key: str, value: Any, indent_level: int) -> str:
        """
        Generate nested HCL configuration.
        
        Args:
            key: Configuration key
            value: Configuration value
            indent_level: Indentation level
            
        Returns:
            str: Nested HCL configuration
        """
        indent = " " * indent_level
        
        if isinstance(value, dict):
            hcl = f"{indent}{key} {{\n"
            
            for nested_key, nested_value in value.items():
                if isinstance(nested_value, str):
                    hcl += f"{indent}  {nested_key} = \"{nested_value}\"\n"
                elif isinstance(nested_value, (list, dict)):
                    hcl += self._generate_nested_hcl(nested_key, nested_value, indent_level + 2)
                else:
                    hcl += f"{indent}  {nested_key} = {nested_value}\n"
            
            hcl += f"{indent}}}\n"
            return hcl
        
        elif isinstance(value, list):
            if not value:
                return f"{indent}{key} = []\n"
            
            if all(isinstance(item, dict) for item in value):
                hcl = ""
                for item in value:
                    hcl += f"{indent}{key} {{\n"
                    
                    for nested_key, nested_value in item.items():
                        if isinstance(nested_value, str):
                            hcl += f"{indent}  {nested_key} = \"{nested_value}\"\n"
                        elif isinstance(nested_value, (list, dict)):
                            hcl += self._generate_nested_hcl(nested_key, nested_value, indent_level + 2)
                        else:
                            hcl += f"{indent}  {nested_key} = {nested_value}\n"
                    
                    hcl += f"{indent}}}\n"
                return hcl
            else:
                value_str = json.dumps(value)
                return f"{indent}{key} = {value_str}\n"
        
        else:
            return f"{indent}{key} = {json.dumps(value)}\n"
    
    def _generate_variables_hcl(self, variables: Dict[str, Any]) -> str:
        """
        Generate Terraform variables configuration in HCL format.
        
        Args:
            variables: Variable specifications
            
        Returns:
            str: Variables configuration in HCL format
        """
        hcl = ""
        
        for var_name, var_config in variables.items():
            var_type = "string"  # Default type
            var_description = ""
            var_default = None
            
            if isinstance(var_config, dict):
                var_type = var_config.get("type", "string")
                var_description = var_config.get("description", "")
                var_default = var_config.get("default")
            else:
                var_default = var_config
            
            hcl += f'variable "{var_name}" {{\n'
            
            if var_type:
                hcl += f'  type = {var_type}\n'
            
            if var_description:
                hcl += f'  description = "{var_description}"\n'
            
            if var_default is not None:
                if isinstance(var_default, str):
                    hcl += f'  default = "{var_default}"\n'
                elif isinstance(var_default, (list, dict)):
                    hcl += f'  default = {json.dumps(var_default)}\n'
                else:
                    hcl += f'  default = {var_default}\n'
            
            hcl += '}\n\n'
        
        return hcl
    
    def _generate_outputs_hcl(self, resources: Dict[str, Any]) -> str:
        """
        Generate Terraform outputs configuration in HCL format.
        
        Args:
            resources: Resource specifications
            
        Returns:
            str: Outputs configuration in HCL format
        """
        hcl = ""
        
        for resource_type, resource_configs in resources.items():
            if not isinstance(resource_configs, list):
                resource_configs = [resource_configs]
                
            for resource_config in resource_configs:
                resource_name = resource_config.get("name", f"resource_{os.urandom(4).hex()}")
                
                # Generate an output for the resource ID
                hcl += f'output "{resource_name}_id" {{\n'
                hcl += f'  value = {resource_type}.{resource_name}.id\n'
                hcl += f'  description = "The ID of the {resource_name} {resource_type}"\n'
                hcl += '}\n\n'
                
                # Generate outputs for specific resource attributes based on resource type
                if resource_type == "aws_instance":
                    hcl += f'output "{resource_name}_public_ip" {{\n'
                    hcl += f'  value = {resource_type}.{resource_name}.public_ip\n'
                    hcl += f'  description = "The public IP of the {resource_name} instance"\n'
                    hcl += '}\n\n'
                
                elif resource_type == "aws_s3_bucket":
                    hcl += f'output "{resource_name}_bucket_domain_name" {{\n'
                    hcl += f'  value = {resource_type}.{resource_name}.bucket_domain_name\n'
                    hcl += f'  description = "The domain name of the {resource_name} bucket"\n'
                    hcl += '}\n\n'
                
                elif resource_type == "aws_db_instance":
                    hcl += f'output "{resource_name}_endpoint" {{\n'
                    hcl += f'  value = {resource_type}.{resource_name}.endpoint\n'
                    hcl += f'  description = "The endpoint of the {resource_name} database"\n'
                    hcl += '}\n\n'
        
        return hcl
    
    def apply_configuration(self, config_dir: str, auto_approve: bool = False) -> AgentResponse:
        """
        Apply a Terraform configuration.
        
        Args:
            config_dir: Path to Terraform configuration directory
            auto_approve: Whether to automatically approve the apply operation
            
        Returns:
            AgentResponse: Apply operation response
        """
        try:
            # Initialize Terraform
            init_output = self.executor.run_command("init", working_dir=config_dir)
            logger.info(f"Terraform init output: {init_output}")
            
            # Plan the changes
            plan_output = self.executor.run_command("plan", working_dir=config_dir)
            logger.info(f"Terraform plan output: {plan_output}")
            
            # Apply the changes
            apply_args = ["-auto-approve"] if auto_approve else []
            apply_output = self.executor.run_command("apply", args=apply_args, working_dir=config_dir)
            logger.info(f"Terraform apply output: {apply_output}")
            
            # Get the outputs
            outputs = self.get_outputs(config_dir)
            
            return AgentResponse(
                success=True,
                message="Terraform configuration applied successfully",
                data={
                    "outputs": outputs,
                    "apply_output": apply_output
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to apply Terraform configuration: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to apply Terraform configuration: {str(e)}",
                data={}
            )
    
    def destroy_configuration(self, config_dir: str, auto_approve: bool = False) -> AgentResponse:
        """
        Destroy resources created by a Terraform configuration.
        
        Args:
            config_dir: Path to Terraform configuration directory
            auto_approve: Whether to automatically approve the destroy operation
            
        Returns:
            AgentResponse: Destroy operation response
        """
        try:
            # Destroy the resources
            destroy_args = ["-auto-approve"] if auto_approve else []
            destroy_output = self.executor.run_command("destroy", args=destroy_args, working_dir=config_dir)
            logger.info(f"Terraform destroy output: {destroy_output}")
            
            return AgentResponse(
                success=True,
                message="Terraform resources destroyed successfully",
                data={
                    "destroy_output": destroy_output
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to destroy Terraform resources: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to destroy Terraform resources: {str(e)}",
                data={}
            )
    
    def get_outputs(self, config_dir: str) -> Dict[str, Any]:
        """
        Get outputs from a Terraform configuration.
        
        Args:
            config_dir: Path to Terraform configuration directory
            
        Returns:
            Dict[str, Any]: Terraform outputs
        """
        try:
            output_json = self.executor.run_command("output", args=["-json"], working_dir=config_dir)
            return json.loads(output_json)
        
        except Exception as e:
            logger.error(f"Failed to get Terraform outputs: {str(e)}")
            return {}
    
    def import_state(self, config_dir: str, resource_address: str, resource_id: str) -> AgentResponse:
        """
        Import existing infrastructure into Terraform state.
        
        Args:
            config_dir: Path to Terraform configuration directory
            resource_address: Terraform resource address
            resource_id: ID of the existing resource
            
        Returns:
            AgentResponse: Import operation response
        """
        try:
            # Initialize Terraform
            init_output = self.executor.run_command("init", working_dir=config_dir)
            logger.info(f"Terraform init output: {init_output}")
            
            # Import the resource
            import_output = self.executor.run_command("import", args=[resource_address, resource_id], working_dir=config_dir)
            logger.info(f"Terraform import output: {import_output}")
            
            return AgentResponse(
                success=True,
                message=f"Resource {resource_id} imported successfully as {resource_address}",
                data={
                    "import_output": import_output
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to import Terraform resource: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to import Terraform resource: {str(e)}",
                data={}
            )
    
    def add_module(self, module_name: str, module_source: str, module_version: Optional[str] = None) -> AgentResponse:
        """
        Add a Terraform module to the registry.
        
        Args:
            module_name: Name of the module
            module_source: Source of the module
            module_version: Version of the module (optional)
            
        Returns:
            AgentResponse: Module addition response
        """
        try:
            result = self.module_registry.add_module(module_name, module_source, module_version)
            
            return AgentResponse(
                success=True,
                message=f"Module {module_name} added successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to add Terraform module: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to add Terraform module: {str(e)}",
                data={}
            )
    
    def list_modules(self) -> AgentResponse:
        """
        List all Terraform modules in the registry.
        
        Returns:
            AgentResponse: Module list response
        """
        try:
            modules = self.module_registry.list_modules()
            
            return AgentResponse(
                success=True,
                message=f"Found {len(modules)} modules",
                data={
                    "modules": modules
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to list Terraform modules: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to list Terraform modules: {str(e)}",
                data={}
            )
    
    def generate_module_configuration(self, config_dir: str, module_name: str, 
                                     module_source: str, module_version: Optional[str] = None,
                                     module_vars: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate Terraform configuration for a module.
        
        Args:
            config_dir: Path to Terraform configuration directory
            module_name: Name of the module
            module_source: Source of the module
            module_version: Version of the module (optional)
            module_vars: Module variables (optional)
            
        Returns:
            str: Path to the module configuration file
        """
        module_file = os.path.join(config_dir, f"module_{module_name}.tf")
        
        hcl = f'module "{module_name}" {{\n'
        hcl += f'  source = "{module_source}"\n'
        
        if module_version:
            hcl += f'  version = "{module_version}"\n'
        
        if module_vars:
            for var_name, var_value in module_vars.items():
                if isinstance(var_value, str):
                    hcl += f'  {var_name} = "{var_value}"\n'
                elif isinstance(var_value, (list, dict)):
                    hcl += self._generate_nested_hcl(var_name, var_value, 2)
                else:
                    hcl += f'  {var_name} = {var_value}\n'
        
        hcl += '}\n'
        
        with open(module_file, "w") as f:
            f.write(hcl)
        
        return module_file
    
    def to_mcp_context(self) -> MCPContext:
        """
        Convert Terraform integration information to MCP context.
        
        Returns:
            MCPContext: MCP context with Terraform integration information
        """
        return MCPContext(
            context_type="terraform_integration",
            terraform_version=self._get_terraform_version(),
            working_dir=self.working_dir
        )
    
    def _get_terraform_version(self) -> str:
        """
        Get the Terraform version.
        
        Returns:
            str: Terraform version
        """
        try:
            version_output = self.executor.run_command("version")
            # Extract version number from output
            version_line = version_output.split("\n")[0]
            version = version_line.split("v")[1].strip()
            return version
        except Exception as e:
            logger.error(f"Failed to get Terraform version: {str(e)}")
            return "unknown"


class TerraformExecutor:
    """
    Executes Terraform commands.
    
    This class provides methods for executing Terraform commands and handling their output.
    """
    
    def __init__(self, terraform_binary: str, working_dir: str):
        """
        Initialize the Terraform Executor.
        
        Args:
            terraform_binary: Path to Terraform binary
            working_dir: Working directory for Terraform operations
        """
        self.terraform_binary = terraform_binary
        self.working_dir = working_dir
    
    def run_command(self, command: str, args: Optional[List[str]] = None, 
                   working_dir: Optional[str] = None) -> str:
        """
        Run a Terraform command.
        
        Args:
            command: Terraform command to run
            args: Command arguments (optional)
            working_dir: Working directory for the command (optional)
            
        Returns:
            str: Command output
            
        Raises:
            Exception: If the command fails
        """
        cmd_args = [self.terraform_binary, command]
        
        if args:
            cmd_args.extend(args)
        
        logger.info(f"Running Terraform command: {' '.join(cmd_args)}")
        
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
            error_message = f"Terraform command failed: {e.stderr}"
            logger.error(error_message)
            raise Exception(error_message)


class TerraformStateManager:
    """
    Manages Terraform state.
    
    This class provides methods for managing Terraform state,
    including state locking, remote state configuration, and state manipulation.
    """
    
    def __init__(self, executor: TerraformExecutor):
        """
        Initialize the Terraform State Manager.
        
        Args:
            executor: Terraform executor
        """
        self.executor = executor
    
    def configure_remote_state(self, config_dir: str, backend_type: str, 
                              backend_config: Dict[str, Any]) -> bool:
        """
        Configure remote state for a Terraform configuration.
        
        Args:
            config_dir: Path to Terraform configuration directory
            backend_type: Backend type (e.g., "s3", "azurerm")
            backend_config: Backend configuration
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Generate backend configuration
            backend_hcl = self._generate_backend_hcl(backend_type, backend_config)
            
            # Write backend configuration to file
            with open(os.path.join(config_dir, "backend.tf"), "w") as f:
                f.write(backend_hcl)
            
            # Initialize Terraform with backend configuration
            init_args = []
            for key, value in backend_config.items():
                init_args.extend(["-backend-config", f"{key}={value}"])
            
            self.executor.run_command("init", args=init_args, working_dir=config_dir)
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to configure remote state: {str(e)}")
            return False
    
    def _generate_backend_hcl(self, backend_type: str, backend_config: Dict[str, Any]) -> str:
        """
        Generate Terraform backend configuration in HCL format.
        
        Args:
            backend_type: Backend type
            backend_config: Backend configuration
            
        Returns:
            str: Backend configuration in HCL format
        """
        hcl = 'terraform {\n'
        hcl += f'  backend "{backend_type}" {{\n'
        
        for key, value in backend_config.items():
            if isinstance(value, str):
                hcl += f'    {key} = "{value}"\n'
            else:
                hcl += f'    {key} = {value}\n'
        
        hcl += '  }\n'
        hcl += '}\n'
        
        return hcl
    
    def list_state(self, config_dir: str) -> Dict[str, Any]:
        """
        List resources in the Terraform state.
        
        Args:
            config_dir: Path to Terraform configuration directory
            
        Returns:
            Dict[str, Any]: State resources
        """
        try:
            state_list_json = self.executor.run_command("state", args=["list", "-json"], working_dir=config_dir)
            return json.loads(state_list_json)
        
        except Exception as e:
            logger.error(f"Failed to list Terraform state: {str(e)}")
            return {}
    
    def show_state_resource(self, config_dir: str, resource_address: str) -> Dict[str, Any]:
        """
        Show details of a resource in the Terraform state.
        
        Args:
            config_dir: Path to Terraform configuration directory
            resource_address: Terraform resource address
            
        Returns:
            Dict[str, Any]: Resource details
        """
        try:
            state_show_json = self.executor.run_command("state", args=["show", "-json", resource_address], working_dir=config_dir)
            return json.loads(state_show_json)
        
        except Exception as e:
            logger.error(f"Failed to show Terraform state resource: {str(e)}")
            return {}
    
    def remove_state_resource(self, config_dir: str, resource_address: str) -> bool:
        """
        Remove a resource from the Terraform state.
        
        Args:
            config_dir: Path to Terraform configuration directory
            resource_address: Terraform resource address
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.executor.run_command("state", args=["rm", resource_address], working_dir=config_dir)
            return True
        
        except Exception as e:
            logger.error(f"Failed to remove Terraform state resource: {str(e)}")
            return False
    
    def pull_state(self, config_dir: str) -> str:
        """
        Pull remote state to a local file.
        
        Args:
            config_dir: Path to Terraform configuration directory
            
        Returns:
            str: Path to local state file
        """
        try:
            local_state_file = os.path.join(config_dir, "terraform.tfstate")
            self.executor.run_command("state", args=["pull"], working_dir=config_dir)
            return local_state_file
        
        except Exception as e:
            logger.error(f"Failed to pull Terraform state: {str(e)}")
            return ""
    
    def push_state(self, config_dir: str) -> bool:
        """
        Push local state to remote.
        
        Args:
            config_dir: Path to Terraform configuration directory
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.executor.run_command("state", args=["push"], working_dir=config_dir)
            return True
        
        except Exception as e:
            logger.error(f"Failed to push Terraform state: {str(e)}")
            return False


class TerraformModuleRegistry:
    """
    Manages Terraform modules.
    
    This class provides methods for managing Terraform modules,
    including module registration, discovery, and versioning.
    """
    
    def __init__(self, working_dir: str):
        """
        Initialize the Terraform Module Registry.
        
        Args:
            working_dir: Working directory for module operations
        """
        self.working_dir = working_dir
        self.modules_dir = os.path.join(working_dir, "modules")
        os.makedirs(self.modules_dir, exist_ok=True)
        
        self.modules = {}
        self._load_modules()
    
    def _load_modules(self):
        """
        Load modules from the modules directory.
        """
        try:
            modules_file = os.path.join(self.modules_dir, "modules.json")
            
            if os.path.exists(modules_file):
                with open(modules_file, "r") as f:
                    self.modules = json.load(f)
        
        except Exception as e:
            logger.error(f"Failed to load modules: {str(e)}")
            self.modules = {}
    
    def _save_modules(self):
        """
        Save modules to the modules directory.
        """
        try:
            modules_file = os.path.join(self.modules_dir, "modules.json")
            
            with open(modules_file, "w") as f:
                json.dump(self.modules, f, indent=2)
        
        except Exception as e:
            logger.error(f"Failed to save modules: {str(e)}")
    
    def add_module(self, module_name: str, module_source: str, 
                  module_version: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a module to the registry.
        
        Args:
            module_name: Name of the module
            module_source: Source of the module
            module_version: Version of the module (optional)
            
        Returns:
            Dict[str, Any]: Module information
        """
        module_info = {
            "name": module_name,
            "source": module_source,
            "version": module_version,
            "added_at": str(int(time.time()))
        }
        
        self.modules[module_name] = module_info
        self._save_modules()
        
        return module_info
    
    def get_module(self, module_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a module from the registry.
        
        Args:
            module_name: Name of the module
            
        Returns:
            Optional[Dict[str, Any]]: Module information or None if not found
        """
        return self.modules.get(module_name)
    
    def list_modules(self) -> List[Dict[str, Any]]:
        """
        List all modules in the registry.
        
        Returns:
            List[Dict[str, Any]]: List of module information
        """
        return list(self.modules.values())
    
    def remove_module(self, module_name: str) -> bool:
        """
        Remove a module from the registry.
        
        Args:
            module_name: Name of the module
            
        Returns:
            bool: True if successful, False otherwise
        """
        if module_name in self.modules:
            del self.modules[module_name]
            self._save_modules()
            return True
        
        return False
