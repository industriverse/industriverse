# LLMModelManager Usage Guide

## 1. Overview

The `LLMModelManager` is a crucial component of the Industriverse Core AI Layer, designed to manage the lifecycle of Large Language Models (LLMs). It handles the registration, discovery, loading, configuration, resource checking, and unloading of various LLMs from different sources like Hugging Face Hub and local file systems. This manager provides a centralized and standardized way for other services (e.g., `LLMInferenceService`, `LLMFineTuningService`) to access and utilize LLMs.

Key features include:
- Configuration-driven model registration (via YAML).
- Dynamic model registration via API.
- Support for multiple model sources (Hugging Face, local files initially).
- Asynchronous operations for non-blocking model loading/unloading.
- Basic resource management (GPU memory, CPU RAM checks).
- Extensible loader interface for supporting new model types or sources in the future.

## 2. Dependencies

Ensure the following Python libraries are installed:
- `PyYAML` (for parsing configuration files)
- `torch` (PyTorch, for model operations and CUDA checks)
- `transformers` (Hugging Face library for model and tokenizer loading)
- `huggingface_hub` (for interacting with the Hugging Face Hub)
- `psutil` (for system resource utilization, like RAM)

These can typically be installed via pip:
```bash
pip install PyYAML torch transformers huggingface_hub psutil
```

## 3. Configuration (`models.yaml`)

The `LLMModelManager` is primarily configured through a YAML file (e.g., `models.yaml`) that defines the models available to the system. This file should contain a list of model configurations under the `models` key.

Each model configuration is an object with the following fields:

- `model_id` (str, required): A unique identifier for the model (e.g., "meta-llama/Llama-2-7b-chat-hf", "my-custom-model").
- `source_type` (str, required): The source of the model. Supported values: `"huggingface"`, `"local"`. (Future: `"s3"`, `"external_service"`).
- `source_path` (str, required): The path or identifier for the model source. 
    - For `huggingface`: The Hugging Face Hub model ID (e.g., "sshleifer/tiny-distilroberta-base").
    - For `local`: The absolute file system path to the model directory.
- `model_format` (str, required): The format of the model. Supported values: `"transformers_pt"` (for PyTorch models compatible with Hugging Face Transformers), `"safetensors"`. (Future: `"gguf"`, `"onnx"`).
- `revision` (str, optional): For Hugging Face models, specifies a branch, tag, or commit hash. Defaults to `main` if not provided.
- `quantization_bits` (int, optional): Specifies if a quantized version of the model should be used (e.g., 4, 8). Default is `None` (full precision).
- `device_preference` (str, optional): Preferred device for loading the model. Values: `"cuda"`, `"cpu"`, `"auto"`. Defaults to `"auto"` (uses CUDA if available, otherwise CPU).
- `required_gpu_memory_mb` (int, optional): Estimated GPU RAM in MB required to load the model. Used for resource checking if `device_preference` is `cuda` or `auto` (and CUDA is chosen).
- `required_ram_mb` (int, optional): Estimated system RAM in MB required to load the model (especially relevant for CPU loading).
- `custom_loader_params` (dict, optional): A dictionary of additional parameters specific to the loader (e.g., `{"auth_token": "YOUR_HF_TOKEN"}` for gated Hugging Face models).
- `tokenizer_path` (str, optional): Path to a specific tokenizer if it's different from the `source_path` or needs separate loading. For local models, if not provided, it assumes the tokenizer is in the `source_path` directory.
- `trust_remote_code` (bool, optional): For Hugging Face models, whether to trust remote code execution. Defaults to `False`. Use with caution.

**Example `models.yaml`:**
```yaml
models:
  - model_id: "tiny-bert"
    source_type: "huggingface"
    source_path: "prajjwal1/bert-tiny"
    model_format: "transformers_pt"
    device_preference: "cpu"
    required_ram_mb: 200
    trust_remote_code: False

  - model_id: "local-custom-model"
    source_type: "local"
    source_path: "/opt/models/my-custom-local-model-dir"
    model_format: "safetensors"
    tokenizer_path: "/opt/models/my-custom-local-model-dir/tokenizer/"
    device_preference: "cuda"
    required_gpu_memory_mb: 4000
    trust_remote_code: True # If your local model has custom code
```

## 4. Initialization

To use the `LLMModelManager`, instantiate it with the path to your configuration file.

```python
import asyncio
from core_ai_layer.llm_service.llm_model_manager import LLMModelManager, ModelConfiguration, ModelLoadingError

async def main():
    config_file_path = "/path/to/your/models.yaml"
    manager = LLMModelManager(config_path=config_file_path)
    
    # Now you can use the manager instance
    # ... see examples below

if __name__ == "__main__":
    asyncio.run(main())
```

## 5. Core Operations

All operations that involve I/O (like loading models) are asynchronous and should be `await`ed.

### 5.1. Listing Available Models

To see all models registered (from the config file or dynamically) and their current status:

```python
async def list_models_example(manager: LLMModelManager):
    available_models = await manager.list_available_models()
    print("Available Models:")
    for model_info in available_models:
        print(f"  ID: {model_info['model_id']}, Source: {model_info['source_type']}, Status: {model_info['status']}, Device: {model_info['device']}")

# await list_models_example(manager)
```

### 5.2. Loading a Model

Models are loaded by their `model_id`. The manager handles resource checks and uses the appropriate loader.

```python
async def load_model_example(manager: LLMModelManager, model_id_to_load: str):
    try:
        print(f"\nAttempting to load model: {model_id_to_load}...")
        loaded_model = await manager.load_model(model_id_to_load)
        print(f"Successfully loaded model '{loaded_model.config.model_id}'")
        print(f"  Model Object Type: {type(loaded_model.model_object)}")
        print(f"  Tokenizer Object Type: {type(loaded_model.tokenizer_object)}")
        print(f"  Loaded on Device: {loaded_model.device}")
        return loaded_model
    except ModelLoadingError as e:
        print(f"Error loading model {model_id_to_load}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while loading {model_id_to_load}: {e}")
    return None

# loaded_model_instance = await load_model_example(manager, "tiny-bert")
```

If `force_reload=True` is passed to `load_model`, any existing loaded instance of that model will be unloaded first, and then the model will be reloaded.

### 5.3. Getting a Model Instance

If you need a model instance and want to load it if it's not already in memory, use `get_model_instance`.

```python
async def get_instance_example(manager: LLMModelManager, model_id_to_get: str):
    try:
        print(f"\nAttempting to get instance for model: {model_id_to_get}...")
        model_instance = await manager.get_model_instance(model_id_to_get)
        print(f"Got instance for '{model_instance.config.model_id}' on device {model_instance.device}")
        # You can now use model_instance.model_object and model_instance.tokenizer_object
    except Exception as e:
        print(f"Error getting instance for {model_id_to_get}: {e}")

# await get_instance_example(manager, "tiny-bert") 
```

### 5.4. Unloading a Model

To free up resources, unload models that are no longer needed.

```python
async def unload_model_example(manager: LLMModelManager, model_id_to_unload: str):
    try:
        print(f"\nAttempting to unload model: {model_id_to_unload}...")
        success = await manager.unload_model(model_id_to_unload)
        if success:
            print(f"Successfully unloaded model '{model_id_to_unload}'.")
        else:
            print(f"Model '{model_id_to_unload}' was not loaded or failed to unload.")
    except Exception as e:
        print(f"An error occurred while unloading {model_id_to_unload}: {e}")

# if loaded_model_instance: # From load_model_example
#     await unload_model_example(manager, loaded_model_instance.config.model_id)
```

### 5.5. Dynamic Model Registration

You can register new models or update existing configurations programmatically. By default, these changes are persisted back to the YAML configuration file.

```python
async def register_model_example(manager: LLMModelManager):
    new_model_config_dict = {
        "model_id": "dynamic-bert-small",
        "source_type": "huggingface",
        "source_path": "google/bert_uncased_L-4_H-256_A-4", # A small BERT model
        "model_format": "transformers_pt",
        "device_preference": "cpu",
        "required_ram_mb": 300
    }
    try:
        print("\nRegistering a new model dynamically...")
        # Set persist=False if you don't want to update the config file
        success = await manager.register_model(new_model_config_dict, persist=True) 
        if success:
            print(f"Successfully registered model: {new_model_config_dict['model_id']}")
            # You can now load this model
            # await manager.load_model(new_model_config_dict['model_id'])
            # await manager.unload_model(new_model_config_dict['model_id'])
        else:
            print(f"Failed to register model: {new_model_config_dict['model_id']}")
    except Exception as e:
        print(f"Error registering dynamic model: {e}")

# await register_model_example(manager)
```

### 5.6. Getting Model Configuration

Retrieve the configuration details for a specific registered model.

```python
async def get_config_example(manager: LLMModelManager, model_id_to_query: str):
    try:
        print(f"\nQuerying configuration for model: {model_id_to_query}...")
        config_obj = await manager.get_model_configuration(model_id_to_query)
        print(f"Configuration for {model_id_to_query}:")
        for key, value in config_obj.__dict__.items():
            print(f"  {key}: {value}")
    except ModelNotFoundError:
        print(f"Model {model_id_to_query} not found in registry.")
    except Exception as e:
        print(f"Error getting configuration for {model_id_to_query}: {e}")

# await get_config_example(manager, "tiny-bert")
```

## 6. Resource Management

The `LLMModelManager` includes a `BasicResourceManager` that performs simple checks before loading a model:
- **GPU Memory**: If a CUDA device is targeted, it checks if the `required_gpu_memory_mb` (specified in the model's configuration) is available on the target GPU. This uses `torch.cuda` functions.
- **System RAM**: If a CPU device is targeted, it checks if the `required_ram_mb` is available using `psutil`.

If resources are deemed insufficient, a `ResourceNotAvailableError` is raised, preventing the load operation.
The `device_preference` in the model configuration (`"cuda"`, `"cpu"`, `"auto"`) guides device selection. `"auto"` will prefer CUDA if available.

## 7. Error Handling

The `LLMModelManager` can raise several custom exceptions (defined in `core_ai_exceptions.py` or within the manager file if the import fails):

- `ConfigurationError`: Issues with the `models.yaml` file (parsing errors, invalid model configurations, file not found).
- `ModelNotFoundError`: Attempting to operate on a `model_id` that is not found in the registry.
- `ModelLoadingError`: An error occurred during the actual model loading process by one of the loaders (e.g., Hugging Face model download failure, issues with model files).
- `ResourceNotAvailableError`: Insufficient GPU memory or system RAM to load the requested model.

It's recommended to wrap calls to the manager's methods in `try...except` blocks to handle these potential errors gracefully.

## 8. Extending with New Loaders

The system is designed to be extensible. To add support for a new model source or format:
1.  Create a new class that inherits from `ModelLoaderInterface`.
2.  Implement the `async def load(...)` and `async def unload(...)` methods.
3.  Register an instance of your new loader in the `_initialize_loaders` method of `LLMModelManager` with a corresponding `source_type` key.

This modular design allows the `LLMModelManager` to adapt to new technologies and model serving paradigms over time.

```python
# Example of the interface (already in llm_model_manager.py)
# from abc import ABC, abstractmethod
# class ModelLoaderInterface(ABC):
#     @abstractmethod
#     async def load(self, config: ModelConfiguration, target_device: str) -> LoadedModel:
#         pass
#
#     @abstractmethod
#     async def unload(self, loaded_model: LoadedModel):
#         pass
```

This guide provides a comprehensive overview of how to use and configure the `LLMModelManager`. For specific implementation details, refer to the source code in `llm_model_manager.py`.

