# PromptTemplateManagementService Usage Guide

---

## 1. Overview

The `PromptTemplateManagementService` is a core component within the Industriverse Core AI Layer, specifically as part of the `llm_service`. Its primary responsibility is to manage the lifecycle of prompt templates. This includes discovering, parsing, indexing, versioning, retrieving, and rendering prompt templates stored in a structured file system.

Prompt templates are crucial for standardizing interactions with Large Language Models (LLMs), ensuring consistency, reusability, and maintainability of prompts across various applications and services within the Industriverse platform.

Key functionalities include:
-   Scanning a designated directory structure for template files (in Markdown format with YAML frontmatter).
-   Parsing template metadata (name, version, description, parameters, engine, etc.) and raw template content.
-   Indexing templates by a unique `template_id` and `version`.
-   Providing methods to list available templates and retrieve specific template versions.
-   Supporting different templating engines (e.g., f-strings, Jinja2) through an adapter pattern, allowing for extensibility.
-   Validating parameters against template definitions before rendering.
-   Rendering templates with provided parameters.
-   Managing the lifecycle state of template versions (e.g., Draft, Active, Archived).

## 2. Core Concepts

### 2.1. Template File Structure

Templates are expected to be Markdown files (`.md`) with a YAML frontmatter block defining their metadata, followed by the raw template content.

-   **Directory Structure:** Templates are organized in a hierarchical directory structure under a `template_base_dir`. The path relative to this base directory (excluding the versioned filename) forms the `template_id`. For example, a file at `template_base_dir/category/sub_category/my_template_name/v1.0.0.md` would have a `template_id` of `category/sub_category/my_template_name`.
-   **Filename Convention:** Template files should be named according to their version, e.g., `v1.0.0.md`, `v1.2.3-alpha.md`.

### 2.2. YAML Frontmatter Metadata

The YAML frontmatter at the beginning of each template file defines its properties. Key metadata fields include:

-   `name`: (string) User-friendly name of the template.
-   `description`: (string, optional) Detailed description.
-   `version`: (string) Semantic version string (e.g., "1.0.0", "2.1.0-beta"). **Required**.
-   `lifecycle_state`: (string, optional, default: "Draft") Current state (e.g., "Draft", "Testing", "Active", "Deprecated", "Archived").
-   `author`: (string, optional) Creator of the template version.
-   `created_at`: (datetime string, optional, default: current UTC time) Creation timestamp.
-   `updated_at`: (datetime string, optional, default: current UTC time) Last update timestamp.
-   `use_cases`: (list of strings, optional) Scenarios where this template is applicable.
-   `tags`: (list of strings, optional) Keywords for categorization and search.
-   `parameters`: (list of objects, optional) Definitions for parameters the template expects. Each parameter object can have:
    -   `name`: (string) Parameter name.
    -   `param_type`: (string, default: "string") Expected data type (e.g., "string", "integer").
    -   `description`: (string, optional) Description.
    -   `required`: (boolean, default: True) If the parameter is mandatory.
    -   `default_value`: (any, optional) Default value if not provided.
    -   `validation_rules`: (dict, optional) Future placeholder for validation rules.
-   `template_engine`: (string, optional, default: service default, e.g., "fstring") Specifies the templating engine (e.g., "fstring", "jinja2").
-   `notes`: (string, optional) Version-specific change notes.

**Example Frontmatter:**
```yaml
---
name: User Welcome Email
description: Template for generating a personalized welcome email to new users.
version: "1.1.0"
lifecycle_state: "Active"
author: "Marketing Team"
created_at: "2023-10-26T10:00:00Z"
updated_at: "2023-10-27T14:30:00Z"
tags: ["email", "user_onboarding", "welcome"]
parameters:
  - name: "username"
    param_type: "string"
    description: "The recipient's username."
    required: true
  - name: "signup_date"
    param_type: "string"
    description: "The date the user signed up."
    required: false
    default_value: "a recent date"
template_engine: "jinja2"
notes: "Added optional signup_date parameter."
---
Hello {{username}},

Welcome to Industriverse! We are thrilled to have you join us.
We noted you signed up on {{signup_date}}.

Best regards,
The Industriverse Team
```

### 2.3. Template ID

A `template_id` is a unique string identifier for a collection of template versions that serve the same logical purpose. It is derived from the directory path of the template file relative to the `template_base_dir`, up to the parent directory of the versioned file. For example, if `template_base_dir` is `/opt/templates`, a file at `/opt/templates/notifications/email/user_signup/v1.0.0.md` will have the `template_id` `notifications/email/user_signup`.

### 2.4. Templating Engines

The service supports multiple templating engines through an adapter pattern (`BaseTemplateEngineAdapter`). Out-of-the-box support includes:
-   **fstring**: Uses Python's built-in f-string formatting (`template_string.format(**parameters)`).
-   **jinja2**: Uses the Jinja2 templating library. Requires `Jinja2` to be installed (`pip install Jinja2`).

The default engine can be specified during service initialization. Individual templates can override this by specifying a `template_engine` in their metadata.

## 3. Service Initialization

To use the service, instantiate it with the path to the base directory where template files are stored:

```python
from prompt_template_management import PromptTemplateManagementService

async def initialize_service():
    template_dir = "/path/to/your/templates"
    # Ensure the directory exists or the service will attempt to create it.
    service = PromptTemplateManagementService(
        template_base_dir=template_dir,
        default_engine_name="jinja2" # Optional, defaults to "fstring"
    )
    
    # It is crucial to call scan_and_index_templates after initialization
    # or after any changes to the template files on disk.
    await service.scan_and_index_templates()
    return service

# Example usage:
# async def main():
#     service = await initialize_service()
#     # ... use the service
```

## 4. API Methods

All public methods of the service are asynchronous (`async`).

### 4.1. `scan_and_index_templates()`

Scans the `template_base_dir` recursively for template files (`*.md`), parses them, and updates the internal index.
This method should be called after service initialization and whenever template files are added, modified, or removed on disk to ensure the service's index is up-to-date.

-   **Usage:** `await service.scan_and_index_templates()`
-   **Returns:** `None`

### 4.2. `list_templates(filter_by_tags: Optional[List[str]] = None, filter_by_state: Optional[str] = None) -> List[PromptTemplateMetadata]`

Lists metadata for all indexed template versions, optionally filtering by tags or lifecycle state.

-   `filter_by_tags`: A list of tags. Templates matching any of these tags will be returned.
-   `filter_by_state`: A lifecycle state string (e.g., "Active", "Draft").
-   **Returns:** A list of `PromptTemplateMetadata` objects.

**Example:**
```python
active_email_templates = await service.list_templates(filter_by_tags=["email"], filter_by_state="Active")
for meta in active_email_templates:
    print(f"Active Email Template: {meta.template_id} v{meta.version} - {meta.name}")
```

### 4.3. `get_template_metadata(template_id: str, version: Optional[str] = None) -> Optional[PromptTemplateMetadata]`

Retrieves the metadata for a specific template version.

-   `template_id`: The unique ID of the template.
-   `version`: The specific version string. If `None`, it attempts to retrieve the latest "Active" version.
-   **Returns:** A `PromptTemplateMetadata` object if found, else `None`.

**Example:**
```python
metadata = await service.get_template_metadata("notifications/email/user_signup", "v1.0.0")
if metadata:
    print(f"Found template: {metadata.name}, Version: {metadata.version}")

latest_active_meta = await service.get_template_metadata("notifications/email/user_signup") # Gets latest active
```

### 4.4. `get_template_content(template_id: str, version: Optional[str] = None) -> Optional[PromptTemplate]`

Retrieves the full template object, including metadata and raw content, for a specific version.

-   `template_id`: The unique ID of the template.
-   `version`: The specific version string. If `None`, it attempts to retrieve the latest "Active" version.
-   **Returns:** A `PromptTemplate` object (containing `metadata` and `content_raw`) if found, else `None`.

**Example:**
```python
template_obj = await service.get_template_content("greetings/common/hello_world", "v1.1.0")
if template_obj:
    print(f"Template Content (raw): {template_obj.content_raw}")
```

### 4.5. `render_template(request: TemplateRenderRequest) -> PromptTemplate`

Renders a template with the provided parameters.

-   `request`: A `TemplateRenderRequest` object containing:
    -   `template_id`: (str) The ID of the template to render.
    -   `version`: (str, optional) The specific version. If `None`, uses the latest "Active" version.
    -   `parameters`: (dict) A dictionary of parameter names and their values.
-   **Returns:** A `PromptTemplate` object with the `content_rendered` field populated.
-   **Raises:**
    -   `ResourceNotFoundError`: If the template or version is not found.
    -   `InvalidJobConfigError`: If required parameters are missing or validation fails (basic validation currently implemented).
    -   `JobExecutionError`: If there is an error during the rendering process by the template engine.
    -   `ServiceConfigurationError`: If the specified or default template engine is not supported or configured correctly (e.g., Jinja2 not installed).

**Example:**
```python
from prompt_template_management import TemplateRenderRequest

render_request = TemplateRenderRequest(
    template_id="greetings/common/hello_world",
    version="v1.1.0",
    parameters={"user": "Alice", "day": "Tuesday", "mood": "fantastic"}
)
try:
    rendered_template = await service.render_template(render_request)
    print(f"Rendered Output: {rendered_template.content_rendered}")
except Exception as e:
    print(f"Error rendering template: {e}")
```

### 4.6. `get_template_versions(template_id: str) -> List[PromptTemplateMetadata]`

Retrieves metadata for all available versions of a specific template ID.

-   `template_id`: The unique ID of the template.
-   **Returns:** A list of `PromptTemplateMetadata` objects for all versions of the given template ID. Returns an empty list if the `template_id` is not found.

**Example:**
```python
all_versions = await service.get_template_versions("greetings/common/hello_world")
for meta in all_versions:
    print(f"Version: {meta.version}, State: {meta.lifecycle_state}")
```

### 4.7. `set_template_lifecycle_state(template_id: str, version: str, state: Literal["Draft", "Testing", "Active", "Deprecated", "Archived"]) -> PromptTemplateMetadata`

Updates the `lifecycle_state` of a specific template version. This operation modifies the template file on disk and updates the in-memory index for that version.

-   `template_id`: The unique ID of the template.
-   `version`: The specific version string.
-   `state`: The new lifecycle state to set.
-   **Returns:** The updated `PromptTemplateMetadata` object.
-   **Raises:**
    -   `ResourceNotFoundError`: If the template version or its file is not found.
    -   `JobExecutionError`: If updating the file or re-indexing fails.

**Example:**
```python
try:
    updated_meta = await service.set_template_lifecycle_state(
        "greetings/common/hello_world", 
        "v0.9.0", 
        "Archived"
    )
    print(f"Set {updated_meta.template_id} v{updated_meta.version} to {updated_meta.lifecycle_state}")
except Exception as e:
    print(f"Failed to update lifecycle state: {e}")
```

### 4.8. `register_template_engine(engine_name: str, engine_adapter: BaseTemplateEngineAdapter)`

Allows registration of custom template engine adapters.

-   `engine_name`: A string name to identify the engine (e.g., "custom_handlebars").
-   `engine_adapter`: An instance of a class that inherits from `BaseTemplateEngineAdapter` and implements the `render` method.
-   **Returns:** `None`
-   **Raises:** `ServiceConfigurationError` if the adapter is not a valid instance.

**Example (Conceptual for a custom adapter):**
```python
# class MyCustomAdapter(BaseTemplateEngineAdapter):
#     async def render(self, template_string: str, parameters: Dict[str, Any]) -> str:
#         # ... custom rendering logic ...
#         return "rendered_by_custom_adapter"
#
# await service.register_template_engine("my_custom", MyCustomAdapter())
```

## 5. Data Models

The service uses Pydantic models for data validation and structuring.

-   `TemplateParameterDefinition`: Defines a single parameter for a template.
-   `PromptTemplateMetadata`: Holds all metadata associated with a template version.
-   `PromptTemplate`: Represents a full template, including its metadata and raw/rendered content.
-   `TemplateRenderRequest`: Encapsulates the information needed to render a template.

Refer to the source code (`prompt_template_management.py`) for detailed field descriptions within these models.

## 6. Error Handling

The service defines and uses custom exceptions (or placeholders if `core_ai_exceptions` is not found):
-   `ServiceConfigurationError`: For issues related to service setup or configuration (e.g., invalid base directory, engine issues).
-   `ResourceNotFoundError`: When a requested template or version cannot be found.
-   `InvalidJobConfigError`: For problems with request data, such as missing required parameters for rendering or invalid template metadata during parsing.
-   `JobExecutionError`: For general errors during an operation, like rendering failures or file I/O issues during state updates.

Standard Python exceptions like `FileNotFoundError` or `yaml.YAMLError` might also be logged during internal operations but are generally caught and re-raised as one of the service-specific exceptions.

## 7. Logging

The service uses Python's standard `logging` module. Logger name is `prompt_template_management`. Ensure your application's logging is configured to see messages from this service. Default log level for basicConfig is INFO.

## 8. Extensibility

### Adding New Template Engines
1.  Create a new class that inherits from `BaseTemplateEngineAdapter`.
2.  Implement the asynchronous `render(self, template_string: str, parameters: Dict[str, Any]) -> str` method.
3.  Instantiate your adapter and register it with the service using `await service.register_template_engine("your_engine_name", YourAdapterInstance())`.
4.  Templates can then specify `template_engine: "your_engine_name"` in their frontmatter.

## 9. Integration with Other Services

-   **LLMInferenceService**: The `LLMInferenceService` (or a higher-level orchestrator) can use this service to fetch and render prompt templates before sending the final prompt to an LLM. This ensures that prompts are standardized and managed centrally.
    ```python
    # Conceptual integration with an inference service
    # async def get_prompt_for_inference(template_service, template_id, params):
    #     render_req = TemplateRenderRequest(template_id=template_id, parameters=params)
    #     rendered_template = await template_service.render_template(render_req)
    #     return rendered_template.content_rendered
    ```
-   **Workflow/Orchestration Layer**: Any service that needs to generate dynamic text based on predefined structures can leverage this service.

## 10. Best Practices

-   **Regularly Scan:** Call `await service.scan_and_index_templates()` after any changes to the template files on disk to keep the index current.
-   **Versioning:** Use semantic versioning for your templates (e.g., `v1.0.0`, `v1.0.1`, `v1.1.0`).
-   **Lifecycle States:** Utilize lifecycle states (`Draft`, `Testing`, `Active`, `Deprecated`, `Archived`) to manage the promotion and retirement of template versions.
-   **Clear Parameter Definitions:** Clearly define expected parameters in the template metadata, including types, descriptions, and whether they are required. This aids in validation and usability.
-   **Idempotent File Operations:** Operations like `set_template_lifecycle_state` modify files. Ensure appropriate backup or version control strategies for your template directory if manual rollbacks are critical.
-   **Engine Choice:** Choose the template engine appropriate for the complexity of your templates. F-strings are simple and fast for basic substitutions. Jinja2 offers more power for complex logic.
-   **Error Handling:** Wrap calls to `render_template` and other methods in try-except blocks to handle potential errors gracefully.

## 11. Example Usage (Comprehensive Test Script)

The `prompt_template_management.py` file itself contains an extensive `async def main_test()` function when run as `if __name__ == "__main__":`. This script demonstrates:
-   Service initialization.
-   Creation of sample template files with varying metadata and engines.
-   Scanning and indexing.
-   Listing and filtering templates.
-   Retrieving metadata and content for specific versions.
-   Parameter validation.
-   Rendering templates using both f-string and Jinja2 engines.
-   Fetching all versions of a template.
-   Updating lifecycle states.

This test script serves as a practical, runnable example of how to use most of the service's functionalities. It is recommended to review and run this script to understand the service in action.

To run the embedded tests (ensure `Jinja2` and `PyYAML` are installed):
```bash
# pip install Jinja2 PyYAML packaging
python path/to/prompt_template_management.py
```
This will create a `test_prompt_templates_main` directory with sample templates and run through the test assertions.

---

