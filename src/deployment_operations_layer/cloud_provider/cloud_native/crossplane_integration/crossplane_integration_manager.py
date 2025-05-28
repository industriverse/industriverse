"""
Crossplane Integration Manager

This module provides integration with Crossplane for the Deployment Operations Layer.
It handles Crossplane resource management, provider configuration, and composition.

Classes:
    CrossplaneIntegrationManager: Manages Crossplane integration
    CrossplaneProviderManager: Manages Crossplane providers
    CrossplaneCompositionManager: Manages Crossplane compositions
    CrossplaneExecutor: Executes Crossplane CLI commands
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

class CrossplaneIntegrationManager:
    """
    Manages Crossplane integration for the Deployment Operations Layer.
    
    This class provides a unified interface for interacting with Crossplane,
    handling provider configuration, resource management, and composition.
    """
    
    def __init__(self, kubectl_binary_path: Optional[str] = None,
                working_dir: Optional[str] = None):
        """
        Initialize the Crossplane Integration Manager.
        
        Args:
            kubectl_binary_path: Path to kubectl binary (optional, defaults to 'kubectl' in PATH)
            working_dir: Working directory for Crossplane operations (optional)
        """
        self.kubectl_binary = kubectl_binary_path or "kubectl"
        self.working_dir = working_dir or tempfile.mkdtemp(prefix="crossplane_")
        
        self.executor = CrossplaneExecutor(self.kubectl_binary, self.working_dir)
        self.provider_manager = CrossplaneProviderManager(self.executor)
        self.composition_manager = CrossplaneCompositionManager(self.executor)
        
        # Verify Crossplane installation
        self._verify_crossplane_installation()
    
    def _verify_crossplane_installation(self):
        """
        Verify that Crossplane is installed and available.
        
        Logs a warning if Crossplane is not installed but does not raise an exception
        as Crossplane may be accessed via API or other means.
        """
        try:
            # Check if crossplane namespace exists
            output = self.executor.run_kubectl_command(["get", "namespace", "crossplane-system", "--no-headers"], check=False)
            if "crossplane-system" in output:
                logger.info("Crossplane namespace found")
            else:
                logger.warning("Crossplane namespace not found")
        except Exception as e:
            logger.warning(f"Failed to check Crossplane namespace: {str(e)}")
    
    def install_provider(self, provider_name: str, 
                        package: str,
                        version: Optional[str] = None) -> AgentResponse:
        """
        Install a Crossplane provider.
        
        Args:
            provider_name: Provider name
            package: Provider package
            version: Provider version (optional)
            
        Returns:
            AgentResponse: Provider installation response
        """
        try:
            result = self.provider_manager.install_provider(
                provider_name=provider_name,
                package=package,
                version=version
            )
            
            return AgentResponse(
                success=True,
                message=f"Crossplane provider {provider_name} installed successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to install Crossplane provider: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to install Crossplane provider: {str(e)}",
                data={}
            )
    
    def configure_provider(self, provider_name: str, 
                          config: Dict[str, Any],
                          secret_name: Optional[str] = None) -> AgentResponse:
        """
        Configure a Crossplane provider.
        
        Args:
            provider_name: Provider name
            config: Provider configuration
            secret_name: Secret name (optional)
            
        Returns:
            AgentResponse: Provider configuration response
        """
        try:
            result = self.provider_manager.configure_provider(
                provider_name=provider_name,
                config=config,
                secret_name=secret_name
            )
            
            return AgentResponse(
                success=True,
                message=f"Crossplane provider {provider_name} configured successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to configure Crossplane provider: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to configure Crossplane provider: {str(e)}",
                data={}
            )
    
    def create_composition(self, name: str, 
                          resources: List[Dict[str, Any]],
                          composition_spec: Dict[str, Any]) -> AgentResponse:
        """
        Create a Crossplane composition.
        
        Args:
            name: Composition name
            resources: List of resources
            composition_spec: Composition specification
            
        Returns:
            AgentResponse: Composition creation response
        """
        try:
            result = self.composition_manager.create_composition(
                name=name,
                resources=resources,
                composition_spec=composition_spec
            )
            
            return AgentResponse(
                success=True,
                message=f"Crossplane composition {name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create Crossplane composition: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create Crossplane composition: {str(e)}",
                data={}
            )
    
    def create_composition_revision(self, name: str, 
                                  composition_name: str,
                                  resources: List[Dict[str, Any]],
                                  composition_spec: Dict[str, Any]) -> AgentResponse:
        """
        Create a Crossplane composition revision.
        
        Args:
            name: Revision name
            composition_name: Composition name
            resources: List of resources
            composition_spec: Composition specification
            
        Returns:
            AgentResponse: Composition revision creation response
        """
        try:
            result = self.composition_manager.create_composition_revision(
                name=name,
                composition_name=composition_name,
                resources=resources,
                composition_spec=composition_spec
            )
            
            return AgentResponse(
                success=True,
                message=f"Crossplane composition revision {name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create Crossplane composition revision: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create Crossplane composition revision: {str(e)}",
                data={}
            )
    
    def create_composite_resource_definition(self, name: str, 
                                           group: str,
                                           kind: str,
                                           version: str,
                                           schema: Dict[str, Any]) -> AgentResponse:
        """
        Create a Crossplane composite resource definition.
        
        Args:
            name: Definition name
            group: API group
            kind: Resource kind
            version: API version
            schema: Resource schema
            
        Returns:
            AgentResponse: Composite resource definition creation response
        """
        try:
            result = self.composition_manager.create_composite_resource_definition(
                name=name,
                group=group,
                kind=kind,
                version=version,
                schema=schema
            )
            
            return AgentResponse(
                success=True,
                message=f"Crossplane composite resource definition {name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create Crossplane composite resource definition: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create Crossplane composite resource definition: {str(e)}",
                data={}
            )
    
    def create_claim(self, name: str, 
                    namespace: str,
                    kind: str,
                    api_version: str,
                    spec: Dict[str, Any]) -> AgentResponse:
        """
        Create a Crossplane claim.
        
        Args:
            name: Claim name
            namespace: Namespace
            kind: Resource kind
            api_version: API version
            spec: Claim specification
            
        Returns:
            AgentResponse: Claim creation response
        """
        try:
            # Create claim manifest
            claim = {
                "apiVersion": api_version,
                "kind": kind,
                "metadata": {
                    "name": name,
                    "namespace": namespace
                },
                "spec": spec
            }
            
            # Write claim to temporary file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
                yaml.dump(claim, f)
                claim_file = f.name
            
            try:
                # Apply claim
                output = self.executor.run_kubectl_command([
                    "apply", "-f", claim_file
                ])
                
                return AgentResponse(
                    success=True,
                    message=f"Crossplane claim {name} created successfully",
                    data={
                        "name": name,
                        "namespace": namespace,
                        "kind": kind,
                        "api_version": api_version,
                        "spec": spec,
                        "output": output
                    }
                )
            
            finally:
                # Clean up temporary file
                if os.path.exists(claim_file):
                    os.unlink(claim_file)
        
        except Exception as e:
            logger.error(f"Failed to create Crossplane claim: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create Crossplane claim: {str(e)}",
                data={}
            )
    
    def get_claim_status(self, name: str, 
                        namespace: str,
                        kind: str,
                        api_version: str) -> AgentResponse:
        """
        Get status of a Crossplane claim.
        
        Args:
            name: Claim name
            namespace: Namespace
            kind: Resource kind
            api_version: API version
            
        Returns:
            AgentResponse: Claim status response
        """
        try:
            # Get claim
            output = self.executor.run_kubectl_command([
                "get", kind.lower(), name, "-n", namespace, "-o", "json"
            ])
            
            try:
                claim_json = json.loads(output)
                
                return AgentResponse(
                    success=True,
                    message=f"Retrieved status for Crossplane claim {name}",
                    data={
                        "name": name,
                        "namespace": namespace,
                        "kind": kind,
                        "api_version": api_version,
                        "status": claim_json.get("status", {}),
                        "spec": claim_json.get("spec", {})
                    }
                )
            
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"Failed to parse claim status: {str(e)}")
                return AgentResponse(
                    success=False,
                    message=f"Failed to parse claim status: {str(e)}",
                    data={}
                )
        
        except Exception as e:
            logger.error(f"Failed to get Crossplane claim status: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to get Crossplane claim status: {str(e)}",
                data={}
            )
    
    def list_providers(self) -> AgentResponse:
        """
        List Crossplane providers.
        
        Returns:
            AgentResponse: Provider list response
        """
        try:
            result = self.provider_manager.list_providers()
            
            return AgentResponse(
                success=True,
                message=f"Found {len(result)} Crossplane providers",
                data={"providers": result}
            )
        
        except Exception as e:
            logger.error(f"Failed to list Crossplane providers: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to list Crossplane providers: {str(e)}",
                data={}
            )
    
    def list_compositions(self) -> AgentResponse:
        """
        List Crossplane compositions.
        
        Returns:
            AgentResponse: Composition list response
        """
        try:
            result = self.composition_manager.list_compositions()
            
            return AgentResponse(
                success=True,
                message=f"Found {len(result)} Crossplane compositions",
                data={"compositions": result}
            )
        
        except Exception as e:
            logger.error(f"Failed to list Crossplane compositions: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to list Crossplane compositions: {str(e)}",
                data={}
            )
    
    def to_mcp_context(self) -> MCPContext:
        """
        Convert Crossplane integration information to MCP context.
        
        Returns:
            MCPContext: MCP context with Crossplane integration information
        """
        return MCPContext(
            context_type="crossplane_integration",
            crossplane_version=self._get_crossplane_version(),
            working_dir=self.working_dir
        )
    
    def _get_crossplane_version(self) -> str:
        """
        Get the Crossplane version.
        
        Returns:
            str: Crossplane version
        """
        try:
            # Get Crossplane deployment
            output = self.executor.run_kubectl_command([
                "get", "deployment", "crossplane", "-n", "crossplane-system", "-o", "jsonpath={.spec.template.spec.containers[0].image}"
            ], check=False)
            
            return output.strip()
        except Exception as e:
            logger.error(f"Failed to get Crossplane version: {str(e)}")
            return "unknown"


class CrossplaneProviderManager:
    """
    Manages Crossplane providers.
    
    This class provides methods for managing Crossplane providers,
    including installation, configuration, and listing.
    """
    
    def __init__(self, executor: 'CrossplaneExecutor'):
        """
        Initialize the Crossplane Provider Manager.
        
        Args:
            executor: Crossplane executor
        """
        self.executor = executor
    
    def install_provider(self, provider_name: str, 
                        package: str,
                        version: Optional[str] = None) -> Dict[str, Any]:
        """
        Install a Crossplane provider.
        
        Args:
            provider_name: Provider name
            package: Provider package
            version: Provider version (optional)
            
        Returns:
            Dict[str, Any]: Provider installation result
        """
        # Create provider manifest
        provider = {
            "apiVersion": "pkg.crossplane.io/v1",
            "kind": "Provider",
            "metadata": {
                "name": provider_name
            },
            "spec": {
                "package": package
            }
        }
        
        # Add version if provided
        if version:
            provider["spec"]["packagePullPolicy"] = {
                "semverConstraint": version
            }
        
        # Write provider to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(provider, f)
            provider_file = f.name
        
        try:
            # Apply provider
            output = self.executor.run_kubectl_command([
                "apply", "-f", provider_file
            ])
            
            return {
                "provider_name": provider_name,
                "package": package,
                "version": version,
                "output": output
            }
        
        finally:
            # Clean up temporary file
            if os.path.exists(provider_file):
                os.unlink(provider_file)
    
    def configure_provider(self, provider_name: str, 
                          config: Dict[str, Any],
                          secret_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Configure a Crossplane provider.
        
        Args:
            provider_name: Provider name
            config: Provider configuration
            secret_name: Secret name (optional)
            
        Returns:
            Dict[str, Any]: Provider configuration result
        """
        # Create provider config manifest
        provider_config = {
            "apiVersion": f"{provider_name}.crossplane.io/v1alpha1",
            "kind": "ProviderConfig",
            "metadata": {
                "name": "default"
            },
            "spec": {
                "credentials": {}
            }
        }
        
        # Add secret reference if provided
        if secret_name:
            provider_config["spec"]["credentials"]["source"] = "Secret"
            provider_config["spec"]["credentials"]["secretRef"] = {
                "namespace": "crossplane-system",
                "name": secret_name,
                "key": "credentials"
            }
        else:
            # Add inline credentials
            provider_config["spec"]["credentials"]["source"] = "Inline"
            provider_config["spec"]["credentials"]["inline"] = config
        
        # Write provider config to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(provider_config, f)
            provider_config_file = f.name
        
        try:
            # Apply provider config
            output = self.executor.run_kubectl_command([
                "apply", "-f", provider_config_file
            ])
            
            return {
                "provider_name": provider_name,
                "config": config,
                "secret_name": secret_name,
                "output": output
            }
        
        finally:
            # Clean up temporary file
            if os.path.exists(provider_config_file):
                os.unlink(provider_config_file)
    
    def list_providers(self) -> List[Dict[str, Any]]:
        """
        List Crossplane providers.
        
        Returns:
            List[Dict[str, Any]]: List of providers
        """
        output = self.executor.run_kubectl_command([
            "get", "providers", "-o", "json"
        ])
        
        try:
            providers_json = json.loads(output)
            
            providers = []
            for provider in providers_json.get("items", []):
                provider_info = {
                    "name": provider["metadata"]["name"],
                    "package": provider["spec"].get("package"),
                    "version": provider["spec"].get("packagePullPolicy", {}).get("semverConstraint"),
                    "status": provider.get("status", {})
                }
                providers.append(provider_info)
            
            return providers
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse provider list: {str(e)}")
            return []
    
    def get_provider_status(self, provider_name: str) -> Dict[str, Any]:
        """
        Get status of a Crossplane provider.
        
        Args:
            provider_name: Provider name
            
        Returns:
            Dict[str, Any]: Provider status
        """
        output = self.executor.run_kubectl_command([
            "get", "provider", provider_name, "-o", "json"
        ])
        
        try:
            provider_json = json.loads(output)
            
            return {
                "name": provider_json["metadata"]["name"],
                "package": provider_json["spec"].get("package"),
                "version": provider_json["spec"].get("packagePullPolicy", {}).get("semverConstraint"),
                "status": provider_json.get("status", {})
            }
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse provider status: {str(e)}")
            return {
                "name": provider_name,
                "error": str(e),
                "output": output
            }


class CrossplaneCompositionManager:
    """
    Manages Crossplane compositions.
    
    This class provides methods for managing Crossplane compositions,
    including creation, revision, and listing.
    """
    
    def __init__(self, executor: 'CrossplaneExecutor'):
        """
        Initialize the Crossplane Composition Manager.
        
        Args:
            executor: Crossplane executor
        """
        self.executor = executor
    
    def create_composition(self, name: str, 
                          resources: List[Dict[str, Any]],
                          composition_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a Crossplane composition.
        
        Args:
            name: Composition name
            resources: List of resources
            composition_spec: Composition specification
            
        Returns:
            Dict[str, Any]: Composition creation result
        """
        # Create composition manifest
        composition = {
            "apiVersion": "apiextensions.crossplane.io/v1",
            "kind": "Composition",
            "metadata": {
                "name": name
            },
            "spec": composition_spec
        }
        
        # Add resources
        composition["spec"]["resources"] = resources
        
        # Write composition to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(composition, f)
            composition_file = f.name
        
        try:
            # Apply composition
            output = self.executor.run_kubectl_command([
                "apply", "-f", composition_file
            ])
            
            return {
                "name": name,
                "resources": resources,
                "composition_spec": composition_spec,
                "output": output
            }
        
        finally:
            # Clean up temporary file
            if os.path.exists(composition_file):
                os.unlink(composition_file)
    
    def create_composition_revision(self, name: str, 
                                  composition_name: str,
                                  resources: List[Dict[str, Any]],
                                  composition_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a Crossplane composition revision.
        
        Args:
            name: Revision name
            composition_name: Composition name
            resources: List of resources
            composition_spec: Composition specification
            
        Returns:
            Dict[str, Any]: Composition revision creation result
        """
        # Create composition revision manifest
        composition_revision = {
            "apiVersion": "apiextensions.crossplane.io/v1",
            "kind": "CompositionRevision",
            "metadata": {
                "name": name
            },
            "spec": {
                "compositionRef": {
                    "name": composition_name
                },
                "revision": 1
            }
        }
        
        # Add composition spec
        composition_revision["spec"].update(composition_spec)
        
        # Add resources
        composition_revision["spec"]["resources"] = resources
        
        # Write composition revision to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(composition_revision, f)
            composition_revision_file = f.name
        
        try:
            # Apply composition revision
            output = self.executor.run_kubectl_command([
                "apply", "-f", composition_revision_file
            ])
            
            return {
                "name": name,
                "composition_name": composition_name,
                "resources": resources,
                "composition_spec": composition_spec,
                "output": output
            }
        
        finally:
            # Clean up temporary file
            if os.path.exists(composition_revision_file):
                os.unlink(composition_revision_file)
    
    def create_composite_resource_definition(self, name: str, 
                                           group: str,
                                           kind: str,
                                           version: str,
                                           schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a Crossplane composite resource definition.
        
        Args:
            name: Definition name
            group: API group
            kind: Resource kind
            version: API version
            schema: Resource schema
            
        Returns:
            Dict[str, Any]: Composite resource definition creation result
        """
        # Create XRD manifest
        xrd = {
            "apiVersion": "apiextensions.crossplane.io/v1",
            "kind": "CompositeResourceDefinition",
            "metadata": {
                "name": name
            },
            "spec": {
                "group": group,
                "names": {
                    "kind": kind,
                    "plural": f"{kind.lower()}s"
                },
                "versions": [
                    {
                        "name": version,
                        "served": True,
                        "referenceable": True,
                        "schema": {
                            "openAPIV3Schema": schema
                        }
                    }
                ],
                "claimNames": {
                    "kind": f"{kind}Claim",
                    "plural": f"{kind.lower()}claims"
                }
            }
        }
        
        # Write XRD to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(xrd, f)
            xrd_file = f.name
        
        try:
            # Apply XRD
            output = self.executor.run_kubectl_command([
                "apply", "-f", xrd_file
            ])
            
            return {
                "name": name,
                "group": group,
                "kind": kind,
                "version": version,
                "schema": schema,
                "output": output
            }
        
        finally:
            # Clean up temporary file
            if os.path.exists(xrd_file):
                os.unlink(xrd_file)
    
    def list_compositions(self) -> List[Dict[str, Any]]:
        """
        List Crossplane compositions.
        
        Returns:
            List[Dict[str, Any]]: List of compositions
        """
        output = self.executor.run_kubectl_command([
            "get", "compositions", "-o", "json"
        ])
        
        try:
            compositions_json = json.loads(output)
            
            compositions = []
            for composition in compositions_json.get("items", []):
                composition_info = {
                    "name": composition["metadata"]["name"],
                    "compositeTypeRef": composition["spec"].get("compositeTypeRef", {}),
                    "resources": len(composition["spec"].get("resources", [])),
                    "writeConnectionSecretsToNamespace": composition["spec"].get("writeConnectionSecretsToNamespace")
                }
                compositions.append(composition_info)
            
            return compositions
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse composition list: {str(e)}")
            return []
    
    def list_composite_resource_definitions(self) -> List[Dict[str, Any]]:
        """
        List Crossplane composite resource definitions.
        
        Returns:
            List[Dict[str, Any]]: List of composite resource definitions
        """
        output = self.executor.run_kubectl_command([
            "get", "compositeresourcedefinitions", "-o", "json"
        ])
        
        try:
            xrds_json = json.loads(output)
            
            xrds = []
            for xrd in xrds_json.get("items", []):
                xrd_info = {
                    "name": xrd["metadata"]["name"],
                    "group": xrd["spec"].get("group"),
                    "kind": xrd["spec"].get("names", {}).get("kind"),
                    "versions": [v.get("name") for v in xrd["spec"].get("versions", [])]
                }
                xrds.append(xrd_info)
            
            return xrds
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse composite resource definition list: {str(e)}")
            return []


class CrossplaneExecutor:
    """
    Executes Crossplane CLI commands.
    
    This class provides methods for executing kubectl commands for Crossplane
    and handling their output.
    """
    
    def __init__(self, kubectl_binary: str, working_dir: str):
        """
        Initialize the Crossplane Executor.
        
        Args:
            kubectl_binary: Path to kubectl binary
            working_dir: Working directory for Crossplane operations
        """
        self.kubectl_binary = kubectl_binary
        self.working_dir = working_dir
    
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
