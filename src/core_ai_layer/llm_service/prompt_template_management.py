"""
Core implementation of the Prompt Template Management Service.

This service manages the lifecycle of prompt templates, including their creation,
storage, versioning, retrieval, and rendering.
"""

import asyncio
import logging
import uuid
import os
import shutil # For test cleanup
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Literal, AsyncGenerator, Type
from abc import ABC, abstractmethod
import yaml # For parsing YAML frontmatter
from pathlib import Path
import re # For splitting frontmatter

from pydantic import BaseModel, Field, validator, ValidationError

# Attempt to import from Core AI Exceptions
try:
    from ..core_ai_exceptions import ServiceConfigurationError, JobExecutionError, InvalidJobConfigError, ResourceNotFoundError
except ImportError:
    logging.warning("PromptTemplateManagementService: Could not import from ..core_ai_exceptions. Using placeholders.")
    class ServiceConfigurationError(Exception): pass
    class JobExecutionError(Exception): pass # Reusing for general execution issues
    class InvalidJobConfigError(Exception): pass # Reusing for invalid template data
    class ResourceNotFoundError(Exception): pass

logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# --- Data Models (Pydantic) ---

class TemplateParameterDefinition(BaseModel):
    name: str = Field(description="Name of the parameter.")
    param_type: str = Field(default="string", description="Expected data type (e.g., \"string\", \"integer\", \"boolean\", \"list\").")
    description: Optional[str] = Field(None, description="Description of the parameter.")
    required: bool = Field(default=True, description="Whether the parameter is mandatory.")
    default_value: Optional[Any] = Field(None, description="Default value if not provided.")
    validation_rules: Optional[Dict[str, Any]] = Field(None, description="Rules for validating the parameter (e.g., regex, min/max length).")

class PromptTemplateMetadata(BaseModel):
    template_id: str = Field(description="Unique identifier for the template (e.g., derived from path/name).")
    name: str = Field(description="User-friendly name of the template.")
    description: Optional[str] = Field(None, description="Detailed description of the template's purpose.")
    version: str = Field(description="Semantic version (e.g., \"1.2.0\").")
    lifecycle_state: Literal["Draft", "Testing", "Active", "Deprecated", "Archived"] = Field(default="Draft", description="Current state of the template version.")
    author: Optional[str] = Field(None, description="Creator of the template version.")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Creation timestamp of this version.")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Last update timestamp of this version.")
    use_cases: Optional[List[str]] = Field(default_factory=list, description="Scenarios where this template is applicable.")
    tags: Optional[List[str]] = Field(default_factory=list, description="Keywords for categorization and search.")
    parameters: Optional[List[TemplateParameterDefinition]] = Field(default_factory=list, description="List of parameters the template expects.")
    template_engine: Optional[str] = Field(None, description="Specifies the templating engine to use (e.g., \"jinja2\", \"fstring\").")
    notes: Optional[str] = Field(None, description="Version-specific change notes or comments.")
    file_path: str = Field(description="Absolute path to the template file.")

    @validator("created_at", "updated_at", pre=True, always=True)
    def ensure_datetime_obj(cls, v):
        if isinstance(v, str):
            try:
                dt_obj = datetime.fromisoformat(v.replace("Z", "+00:00"))
                return dt_obj.astimezone(timezone.utc) if dt_obj.tzinfo is None else dt_obj
            except ValueError:
                for fmt in ("%Y-%m-%d %H:%M:%S%z", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f%z"):
                    try:
                        dt_obj = datetime.strptime(v, fmt)
                        return dt_obj.astimezone(timezone.utc) if dt_obj.tzinfo is None else dt_obj
                    except ValueError:
                        continue
                raise ValueError(f"Invalid datetime format: {v}")
        elif isinstance(v, datetime):
            return v.astimezone(timezone.utc) if v.tzinfo is None else v
        return datetime.now(timezone.utc)

class PromptTemplate(BaseModel):
    metadata: PromptTemplateMetadata
    content_raw: str = Field(description="The raw template string (body of the file, after frontmatter).")
    content_rendered: Optional[str] = Field(None, description="The template string after rendering with parameters (if applicable).")

class TemplateRenderRequest(BaseModel):
    template_id: str
    version: Optional[str] = Field(None, description="Specific version to use. If None, latest 'Active' version is used.")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Values for the template parameters.")

# --- Abstract Base Classes for Extensibility ---

class BaseTemplateEngineAdapter(ABC):
    @abstractmethod
    async def render(self, template_string: str, parameters: Dict[str, Any]) -> str:
        """Renders the template string with the given parameters."""
        pass

# --- Concrete Template Engine Adapters ---

class FStringTemplateEngineAdapter(BaseTemplateEngineAdapter):
    async def render(self, template_string: str, parameters: Dict[str, Any]) -> str:
        try:
            return template_string.format(**parameters)
        except KeyError as e:
            logger.error(f"FStringAdapter: Missing parameter {e} for template. Parameters: {list(parameters.keys())}")
            raise InvalidJobConfigError(f"Missing parameter {e} for f-string template.")
        except Exception as e:
            logger.error(f"FStringAdapter: Error rendering template: {e}")
            raise JobExecutionError(f"Error rendering f-string template: {e}")

class Jinja2TemplateEngineAdapter(BaseTemplateEngineAdapter):
    _env: Optional[Any] = None # Class-level cache for Jinja2 environment

    def __init__(self):
        if Jinja2TemplateEngineAdapter._env is None:
            try:
                import jinja2
                Jinja2TemplateEngineAdapter._env = jinja2.Environment(
                    loader=jinja2.BaseLoader(), 
                    undefined=jinja2.StrictUndefined, 
                    enable_async=True
                )
                logger.info("Jinja2 environment initialized.")
            except ImportError:
                logger.error("Jinja2Adapter: Jinja2 library not installed. Please install with `pip install Jinja2`.")
                # Defer raising error to render method to allow service to start if Jinja2 not used

    async def render(self, template_string: str, parameters: Dict[str, Any]) -> str:
        if Jinja2TemplateEngineAdapter._env is None:
             raise ServiceConfigurationError("Jinja2 library not installed. Cannot render Jinja2 template.")
        try:
            template = Jinja2TemplateEngineAdapter._env.from_string(template_string)
            return await template.render_async(**parameters)
        except ImportError: # Should be caught by init, but as a safeguard
            logger.error("Jinja2Adapter: Jinja2 library not installed during render. This should not happen.")
            raise ServiceConfigurationError("Jinja2 library not installed.")
        except Exception as e: # Catches jinja2.exceptions.UndefinedError and others
            logger.error(f"Jinja2Adapter: Error rendering template: {e}. Parameters: {list(parameters.keys())}")
            if "undefined value" in str(e).lower():
                 raise InvalidJobConfigError(f"Undefined variable in Jinja2 template: {e}")
            raise JobExecutionError(f"Error rendering Jinja2 template: {e}")

# --- Core Service Class ---

class PromptTemplateManagementService:
    def __init__(self, template_base_dir: str, default_engine_name: str = "fstring"):
        self.template_base_dir = Path(template_base_dir).resolve()
        if not self.template_base_dir.is_dir():
            logger.warning(f"Template base directory {self.template_base_dir} does not exist. Creating it.")
            try:
                self.template_base_dir.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                logger.error(f"Failed to create template base directory {self.template_base_dir}: {e}")
                raise ServiceConfigurationError(f"Failed to create template base directory: {e}")
        
        self._template_index: Dict[str, Dict[str, PromptTemplateMetadata]] = {} # {template_id: {version_str: metadata}}
        self._engine_adapters: Dict[str, BaseTemplateEngineAdapter] = {}
        self.default_engine_name = default_engine_name.lower()

        # Register default engines
        # asyncio.run() is problematic in __init__ if service is instantiated within an existing event loop.
        # Consider lazy registration or explicit setup method.
        self._engine_adapters["fstring"] = FStringTemplateEngineAdapter()
        self._engine_adapters["jinja2"] = Jinja2TemplateEngineAdapter() # Instantiates, which tries to import jinja2
        
        logger.info(f"PromptTemplateManagementService initialized with base directory: {self.template_base_dir}")
        # Initial scan can be triggered here or by an explicit setup method
        # asyncio.run(self.scan_and_index_templates()) # Avoid asyncio.run in __init__

    async def _ensure_engines_registered(self):
        # This is a workaround for asyncio.run in __init__.
        # Ideally, registration happens during an async setup phase.
        if "fstring" not in self._engine_adapters:
            await self.register_template_engine("fstring", FStringTemplateEngineAdapter())
        if "jinja2" not in self._engine_adapters:
            await self.register_template_engine("jinja2", Jinja2TemplateEngineAdapter())

    async def register_template_engine(self, engine_name: str, engine_adapter: BaseTemplateEngineAdapter):
        if not isinstance(engine_adapter, BaseTemplateEngineAdapter):
            raise ServiceConfigurationError(f"Engine adapter for '{engine_name}' must be an instance of BaseTemplateEngineAdapter.")
        self._engine_adapters[engine_name.lower()] = engine_adapter
        logger.info(f"Registered template engine: {engine_name}")

    async def _parse_template_file(self, file_path: Path) -> Optional[PromptTemplate]:
        try:
            content = file_path.read_text(encoding="utf-8")
            # Regex to split YAML frontmatter from content
            match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", content, re.DOTALL | re.MULTILINE)
            if not match:
                logger.warning(f"File {file_path} does not have valid YAML frontmatter. Skipping.")
                return None

            frontmatter_str, raw_template_content = match.groups()
            metadata_dict = yaml.safe_load(frontmatter_str)
            if not isinstance(metadata_dict, dict):
                logger.warning(f"Invalid YAML frontmatter in {file_path}. Expected a dictionary. Skipping.")
                return None

            # Derive template_id from path relative to base_dir, excluding version file name
            # e.g., base_dir/category/template_name/v1.0.0.md -> category/template_name
            relative_path = file_path.relative_to(self.template_base_dir)
            template_id_parts = list(relative_path.parts[:-1]) # All parts except the filename
            if not template_id_parts:
                 # Handle case where template files are directly under base_dir/version.md (not recommended)
                 # or base_dir/template_name/version.md
                 # If filename is vX.Y.Z.md, parent is template_name
                 if relative_path.parent.name != self.template_base_dir.name:
                     template_id_parts = [relative_path.parent.name]
                 else: # File directly under base_dir, use filename stem as part of ID (less ideal)
                     template_id_parts = [file_path.stem.replace(".v", "_v")] # Avoid version in ID part
            
            template_id = "/".join(template_id_parts)
            if not template_id:
                logger.warning(f"Could not derive template_id for {file_path}. Skipping.")
                return None

            metadata_dict["template_id"] = template_id
            metadata_dict["file_path"] = str(file_path.resolve())
            
            # Ensure version is present for indexing
            if "version" not in metadata_dict:
                logger.warning(f"Missing 'version' in metadata for {file_path}. Skipping.")
                return None

            metadata = PromptTemplateMetadata(**metadata_dict)
            return PromptTemplate(metadata=metadata, content_raw=raw_template_content.strip())
        except ValidationError as e:
            logger.error(f"Validation error parsing metadata for {file_path}: {e}")
            return None
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error for {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error parsing template file {file_path}: {e}")
            return None

    async def scan_and_index_templates(self):
        new_index: Dict[str, Dict[str, PromptTemplateMetadata]] = {}
        logger.info(f"Scanning for templates in {self.template_base_dir}...")
        for file_path in self.template_base_dir.rglob("*.md"):
            if file_path.is_file():
                parsed_template = await self._parse_template_file(file_path)
                if parsed_template:
                    meta = parsed_template.metadata
                    if meta.template_id not in new_index:
                        new_index[meta.template_id] = {}
                    if meta.version in new_index[meta.template_id]:
                        logger.warning(f"Duplicate version {meta.version} for template_id {meta.template_id} found at {file_path}. Overwriting with {meta.file_path}.")
                    new_index[meta.template_id][meta.version] = meta
        self._template_index = new_index
        logger.info(f"Template scan complete. Indexed {sum(len(v) for v in self._template_index.values())} template versions across {len(self._template_index)} template IDs.")

    async def _get_latest_active_version(self, template_id: str) -> Optional[str]:
        if template_id not in self._template_index:
            return None
        
        active_versions = []
        for version_str, meta in self._template_index[template_id].items():
            if meta.lifecycle_state == "Active":
                active_versions.append(version_str)
        
        if not active_versions:
            logger.debug(f"No active versions found for template ID {template_id} during latest active version lookup.")
            return None
        
        # Sort versions semantically (basic sort, can be improved with packaging.version)
        try:
            from packaging.version import parse as parse_version
            active_versions.sort(key=parse_version, reverse=True)
        except ImportError:
            active_versions.sort(reverse=True) # Fallback to lexicographical sort
            logger.warning("packaging library not found, using lexicographical sort for versions. Consider `pip install packaging`.")

        return active_versions[0] if active_versions else None

    async def list_templates(self, filter_by_tags: Optional[List[str]] = None, filter_by_state: Optional[str] = None) -> List[PromptTemplateMetadata]:
        results = []
        for template_id_versions in self._template_index.values():
            for metadata in template_id_versions.values():
                match = True
                if filter_by_state and metadata.lifecycle_state != filter_by_state:
                    match = False
                if filter_by_tags and metadata.tags and not any(tag in metadata.tags for tag in filter_by_tags):
                    match = False
                if match:
                    results.append(metadata)
        return results

    async def get_template_metadata(self, template_id: str, version: Optional[str] = None) -> Optional[PromptTemplateMetadata]:
        if template_id not in self._template_index:
            logger.debug(f"Template ID {template_id} not found in index.")
            return None

        target_version = version
        if not target_version:
            target_version = await self._get_latest_active_version(template_id)
            if not target_version:
                logger.debug(f"No active version found for template ID {template_id}.")
                return None
        
        return self._template_index[template_id].get(target_version)

    async def get_template_content(self, template_id: str, version: Optional[str] = None) -> Optional[PromptTemplate]:
        metadata = await self.get_template_metadata(template_id, version)
        if not metadata:
            return None
        
        try:
            file_path = Path(metadata.file_path)
            # Re-parse to get fresh content, could optimize by caching raw content if files are static
            parsed_template = await self._parse_template_file(file_path)
            if parsed_template and parsed_template.metadata.version == metadata.version: # Ensure we got the right version
                return parsed_template
            logger.error(f"Mismatch or error re-parsing template file {file_path} for {template_id} v{metadata.version}")
            return None # Should not happen if index is correct
        except FileNotFoundError:
            logger.error(f"Template file {metadata.file_path} not found for {template_id} v{metadata.version}. Index might be stale.")
            # Consider re-scanning or removing from index here
            return None
        except Exception as e:
            logger.error(f"Error reading template content for {template_id} v{metadata.version} from {metadata.file_path}: {e}")
            return None

    async def validate_parameters(self, template_id: str, version: Optional[str], parameters: Dict[str, Any]) -> bool:
        metadata = await self.get_template_metadata(template_id, version)
        if not metadata:
            raise ResourceNotFoundError(f"Template {template_id} version {version or 'latest active'} not found for validation.")

        if not metadata.parameters:
            return True # No parameters to validate

        for param_def in metadata.parameters:
            if param_def.required and param_def.name not in parameters:
                if param_def.default_value is None: # Only raise if no default can satisfy requirement
                    logger.error(f"Validation failed for {template_id} v{metadata.version}: Missing required parameter '{param_def.name}'.")
                    raise InvalidJobConfigError(f"Missing required parameter '{param_def.name}' for template {template_id} v{metadata.version}.")
            # Further type checking and validation_rules can be implemented here
            # For example, check if parameters[param_def.name] matches param_def.param_type
            # And apply rules from param_def.validation_rules
            if param_def.name in parameters:
                value = parameters[param_def.name]
                # Basic type check example (can be expanded)
                if param_def.param_type == "integer" and not isinstance(value, int):
                    logger.warning(f"Parameter '{param_def.name}' for {template_id} expected integer, got {type(value)}.")
                elif param_def.param_type == "string" and not isinstance(value, str):
                    logger.warning(f"Parameter '{param_def.name}' for {template_id} expected string, got {type(value)}.")
        return True

    async def render_template(self, request: TemplateRenderRequest) -> PromptTemplate:
        await self._ensure_engines_registered() # Ensure engines are available
        template_obj = await self.get_template_content(request.template_id, request.version)
        if not template_obj:
            raise ResourceNotFoundError(f"Template {request.template_id} version {request.version or 'latest active'} not found.")

        await self.validate_parameters(request.template_id, template_obj.metadata.version, request.parameters)
        
        # Apply defaults for missing non-required parameters
        final_params = {} 
        if template_obj.metadata.parameters:
            for param_def in template_obj.metadata.parameters:
                if param_def.name in request.parameters:
                    final_params[param_def.name] = request.parameters[param_def.name]
                elif param_def.default_value is not None:
                    final_params[param_def.name] = param_def.default_value
                # If required and not present, validate_parameters should have caught it if no default

        engine_name = template_obj.metadata.template_engine or self.default_engine_name
        engine_adapter = self._engine_adapters.get(engine_name.lower())

        if not engine_adapter:
            logger.error(f"Template engine '{engine_name}' not supported for template {request.template_id}.")
            raise ServiceConfigurationError(f"Template engine '{engine_name}' not supported.")

        try:
            rendered_content = await engine_adapter.render(template_obj.content_raw, final_params)
            template_obj.content_rendered = rendered_content
            return template_obj
        except (InvalidJobConfigError, JobExecutionError) as e: # Propagate specific errors from adapter
            raise e 
        except Exception as e:
            logger.error(f"Unexpected error rendering template {request.template_id} with engine {engine_name}: {e}")
            raise JobExecutionError(f"Failed to render template {request.template_id}: {e}")

    async def get_template_versions(self, template_id: str) -> List[PromptTemplateMetadata]:
        if template_id not in self._template_index:
            return []
        return list(self._template_index[template_id].values())

    async def _update_metadata_in_file(self, file_path: Path, updated_metadata_fields: Dict[str, Any]) -> bool:
        try:
            content = file_path.read_text(encoding="utf-8")
            match = re.match(r"^(---\s*\n)(.*?)\n(---\s*\n)(.*)", content, re.DOTALL | re.MULTILINE)
            if not match:
                logger.error(f"Could not parse frontmatter for update in {file_path}")
                return False

            frontmatter_header, frontmatter_str, frontmatter_footer, raw_template_content = match.groups()
            
            try:
                metadata_dict = yaml.safe_load(frontmatter_str) or {}
            except yaml.YAMLError:
                 logger.error(f"Invalid YAML in frontmatter of {file_path} during update.")
                 return False

            metadata_dict.update(updated_metadata_fields)
            metadata_dict["updated_at"] = datetime.now(timezone.utc).isoformat() # Ensure updated_at is fresh
            
            # Remove Pydantic specific fields if they crept in, or fields that should not be in YAML
            if "file_path" in metadata_dict: del metadata_dict["file_path"]
            if "template_id" in metadata_dict: del metadata_dict["template_id"] # This is derived, not stored

            # Convert datetime objects to ISO format strings for YAML
            for key, value in metadata_dict.items():
                if isinstance(value, datetime):
                    metadata_dict[key] = value.isoformat()
                if key == "parameters" and isinstance(value, list):
                    # Pydantic models in list need to be dicts for YAML
                    metadata_dict[key] = [p.model_dump() if isinstance(p, BaseModel) else p for p in value]

            new_frontmatter_str = yaml.dump(metadata_dict, sort_keys=False, allow_unicode=True)
            new_content = f"{frontmatter_header}{new_frontmatter_str}{frontmatter_footer}{raw_template_content}"
            
            file_path.write_text(new_content, encoding="utf-8")
            return True
        except Exception as e:
            logger.error(f"Failed to update metadata in file {file_path}: {e}")
            return False

    async def set_template_lifecycle_state(self, template_id: str, version: str, state: Literal["Draft", "Testing", "Active", "Deprecated", "Archived"]) -> PromptTemplateMetadata:
        metadata = await self.get_template_metadata(template_id, version)
        if not metadata:
            raise ResourceNotFoundError(f"Template {template_id} version {version} not found to update state.")

        file_path = Path(metadata.file_path)
        if not file_path.exists():
            raise ResourceNotFoundError(f"Template file {file_path} for {template_id} v{version} not found on disk.")

        success = await self._update_metadata_in_file(file_path, {"lifecycle_state": state})
        if not success:
            raise JobExecutionError(f"Failed to update lifecycle state in file for {template_id} v{version}.")

        # Re-parse and update index for this specific template version
        updated_template_obj = await self._parse_template_file(file_path)
        if updated_template_obj:
            updated_meta = updated_template_obj.metadata
            if template_id in self._template_index and version in self._template_index[template_id]:
                self._template_index[template_id][version] = updated_meta
                logger.info(f"Updated lifecycle state for {template_id} v{version} to {state}. Re-indexed.")
                return updated_meta
            else:
                logger.error(f"Failed to re-index {template_id} v{version} after state update. Index inconsistency possible.")
                # Fallback to a full rescan if partial update fails to reflect in index
                await self.scan_and_index_templates()
                new_meta = await self.get_template_metadata(template_id, version)
                if new_meta and new_meta.lifecycle_state == state:
                    return new_meta
                raise JobExecutionError(f"Failed to confirm state update for {template_id} v{version} after re-index.")
        else:
            raise JobExecutionError(f"Failed to re-parse template {template_id} v{version} after updating state.")


async def create_test_template_file(base_dir: Path, template_id_path: str, version: str, metadata_override: Optional[Dict] = None, content_body: Optional[str] = None):
    full_id_parts = template_id_path.split("/")
    template_name = full_id_parts[-1]
    category_path = "/".join(full_id_parts[:-1])

    template_dir = base_dir / category_path / template_name
    template_dir.mkdir(parents=True, exist_ok=True)
    template_file_path = template_dir / f"{version}.md"

    default_metadata = {
        "name": template_name.replace("_", " ").title(),
        "description": f"A test template for {template_name}",
        "version": version,
        "lifecycle_state": "Draft",
        "author": "TestGen",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "parameters": [],
        "template_engine": "fstring"
    }
    if metadata_override:
        default_metadata.update(metadata_override)

    body = content_body if content_body is not None else f"This is template {template_name} v{version}. Hello {{name}}!"
    
    yaml_frontmatter = yaml.dump(default_metadata, sort_keys=False, allow_unicode=True)
    file_content = f"---\n{yaml_frontmatter}---\n{body}"
    
    template_file_path.write_text(file_content, encoding="utf-8")
    return template_file_path

async def main_test():
    logger.info("Starting PromptTemplateManagementService test...")
    test_dir = Path("./test_prompt_templates_main")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir(parents=True, exist_ok=True)

    service = PromptTemplateManagementService(template_base_dir=str(test_dir))
    await service._ensure_engines_registered() # Call this as scan_and_index is not in init

    # Create some test templates
    await create_test_template_file(test_dir, "greetings/common/hello_world", "v1.0.0", 
                                    {"lifecycle_state": "Active", "tags": ["general", "greeting"]}, 
                                    "Hello {user}! Today is {day}.")
    await create_test_template_file(test_dir, "greetings/common/hello_world", "v1.1.0", 
                                    {"lifecycle_state": "Active", "tags": ["general", "greeting"], "parameters":[{"name":"user"}, {"name":"day"}, {"name":"mood", "required":False, "default_value":"good"}]}, 
                                    "Hello {user}! It's a {mood} {day}.")
    await create_test_template_file(test_dir, "greetings/common/hello_world", "v0.9.0", 
                                    {"lifecycle_state": "Draft"}, 
                                    "Hi {user}.")
    await create_test_template_file(test_dir, "farewells/formal_goodbye", "v1.0.0", 
                                    {"lifecycle_state": "Active", "template_engine": "jinja2", "parameters":[{"name":"recipient_name"}, {"name":"sender_name"}]}, 
                                    "Dear {{recipient_name}},\n\nIt was a pleasure. \n\nSincerely,\n{{sender_name}}.")
    await create_test_template_file(test_dir, "farewells/formal_goodbye", "v1.0.1", 
                                    {"lifecycle_state": "Testing", "template_engine": "jinja2"}, 
                                    "Goodbye, {{recipient_name}}.")
    await create_test_template_file(test_dir, "notifications/urgent_alert", "v2.0.0",
                                     {"lifecycle_state": "Active", "parameters": [{"name": "message"}], "tags":["alert"]})

    # Test scan_and_index_templates
    await service.scan_and_index_templates()
    assert len(service._template_index) == 3, f"Expected 3 template IDs, got {len(service._template_index)}"
    assert len(service._template_index["greetings/common/hello_world"]) == 3, "Expected 3 versions for hello_world"
    logger.info(f"Scan successful. Index: {service._template_index.keys()}")

    # Test list_templates
    all_templates = await service.list_templates()
    assert len(all_templates) == 6, f"Expected 6 template versions, got {len(all_templates)}"
    active_templates = await service.list_templates(filter_by_state="Active")
    assert len(active_templates) == 3, f"Expected 3 active templates, got {len(active_templates)}"
    greeting_tags = await service.list_templates(filter_by_tags=["greeting"])
    assert len(greeting_tags) == 2, f"Expected 2 templates with 'greeting' tag, got {len(greeting_tags)}"
    logger.info("List templates tests passed.")

    # Test get_template_metadata and _get_latest_active_version
    hw_meta_latest = await service.get_template_metadata("greetings/common/hello_world")
    assert hw_meta_latest and hw_meta_latest.version == "v1.1.0", f"Expected latest active for hello_world to be v1.1.0, got {hw_meta_latest.version if hw_meta_latest else 'None'}"
    hw_meta_v1 = await service.get_template_metadata("greetings/common/hello_world", "v1.0.0")
    assert hw_meta_v1 and hw_meta_v1.version == "v1.0.0"
    logger.info("Get template metadata tests passed.")

    # Test get_template_content
    hw_content_v1 = await service.get_template_content("greetings/common/hello_world", "v1.0.0")
    assert hw_content_v1 and "Hello {user}! Today is {day}." in hw_content_v1.content_raw
    logger.info("Get template content tests passed.")

    # Test validate_parameters
    valid_params = {"user": "Alice", "day": "Monday"}
    assert await service.validate_parameters("greetings/common/hello_world", "v1.0.0", valid_params)
    try:
        await service.validate_parameters("greetings/common/hello_world", "v1.0.0", {"day": "Tuesday"}) # Missing 'user'
        assert False, "Validation should have failed for missing required parameter"
    except InvalidJobConfigError:
        logger.info("Parameter validation correctly failed for missing param.")
    logger.info("Validate parameters tests passed.")

    # Test render_template (fstring)
    render_req_fstring = TemplateRenderRequest(template_id="greetings/common/hello_world", version="v1.1.0", parameters={"user": "Bob", "day": "Friday"})
    rendered_fstring = await service.render_template(render_req_fstring)
    expected_fstring = "Hello Bob! It's a good Friday."
    assert rendered_fstring.content_rendered == expected_fstring, f"Rendered fstring mismatch: got '{rendered_fstring.content_rendered}', expected '{expected_fstring}'"
    logger.info(f"Rendered f-string: {rendered_fstring.content_rendered}")

    # Test render_template (jinja2)
    render_req_jinja = TemplateRenderRequest(template_id="farewells/formal_goodbye", version="v1.0.0", parameters={"recipient_name": "Dr. Evil", "sender_name": "Austin Powers"})
    rendered_jinja = await service.render_template(render_req_jinja)
    assert "Dear Dr. Evil," in rendered_jinja.content_rendered and "Austin Powers" in rendered_jinja.content_rendered
    logger.info(f"Rendered Jinja2: \n{rendered_jinja.content_rendered}")

    # Test get_template_versions
    hw_versions = await service.get_template_versions("greetings/common/hello_world")
    assert len(hw_versions) == 3
    logger.info("Get template versions test passed.")

    # Test set_template_lifecycle_state
    updated_meta = await service.set_template_lifecycle_state("greetings/common/hello_world", "v0.9.0", "Archived")
    assert updated_meta.lifecycle_state == "Archived"
    archived_meta = await service.get_template_metadata("greetings/common/hello_world", "v0.9.0")
    assert archived_meta and archived_meta.lifecycle_state == "Archived"
    logger.info("Set template lifecycle state test passed.")
    
    # Test rendering with default parameter
    render_req_default_param = TemplateRenderRequest(template_id="greetings/common/hello_world", version="v1.1.0", parameters={"user": "Charlie", "day": "Sunday"})
    # 'mood' should use default 'good'
    rendered_default = await service.render_template(render_req_default_param)
    expected_default = "Hello Charlie! It's a good Sunday."
    assert rendered_default.content_rendered == expected_default, f"Rendered with default mismatch: got '{rendered_default.content_rendered}', expected '{expected_default}'"
    logger.info(f"Rendered with default param: {rendered_default.content_rendered}")

    logger.info("All PromptTemplateManagementService tests passed.")
    shutil.rmtree(test_dir) # Clean up

if __name__ == "__main__":
    asyncio.run(main_test())

