import asyncio
import logging
import os
import yaml
import psutil
import torch
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, Literal, List, Type

from huggingface_hub import hf_hub_download, snapshot_download
from transformers import AutoModel, AutoTokenizer, AutoConfig

# Assuming core_ai_exceptions.py is in the parent directory or accessible in PYTHONPATH
# from ..core_ai_exceptions import ModelLoadingError, ModelNotFoundError, ConfigurationError, ResourceNotAvailableError
# For standalone execution, let's define them simply if not found
try:
    from ..core_ai_exceptions import ModelLoadingError, ModelNotFoundError, ConfigurationError, ResourceNotAvailableError
except ImportError:
    class ModelLoadingError(Exception):
        pass
    class ModelNotFoundError(Exception):
        pass
    class ConfigurationError(Exception):
        pass
    class ResourceNotAvailableError(Exception):
        pass

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ModelConfiguration:
    model_id: str
    source_type: Literal["huggingface", "local", "s3", "external_service"]
    source_path: str
    model_format: Literal["transformers_pt", "safetensors", "gguf", "onnx"]
    revision: Optional[str] = None
    quantization_bits: Optional[int] = None
    device_preference: Literal["cuda", "cpu", "auto"] = "auto"
    required_gpu_memory_mb: Optional[int] = None
    required_ram_mb: Optional[int] = None # Added for CPU RAM
    custom_loader_params: Optional[Dict[str, Any]] = None
    tokenizer_path: Optional[str] = None
    trust_remote_code: bool = False # Specific to HuggingFace

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if not hasattr(self, 'trust_remote_code'): # ensure default
            self.trust_remote_code = False
        if not hasattr(self, 'required_ram_mb'):
            self.required_ram_mb = None

class LoadedModel:
    config: ModelConfiguration
    model_object: Any
    tokenizer_object: Any
    device: str

    def __init__(self, config: ModelConfiguration, model_object: Any, tokenizer_object: Any, device: str):
        self.config = config
        self.model_object = model_object
        self.tokenizer_object = tokenizer_object
        self.device = device

class ModelLoaderInterface(ABC):
    @abstractmethod
    async def load(self, config: ModelConfiguration, target_device: str) -> LoadedModel:
        pass

    @abstractmethod
    async def unload(self, loaded_model: LoadedModel):
        pass

class HuggingFaceLoader(ModelLoaderInterface):
    async def load(self, config: ModelConfiguration, target_device: str) -> LoadedModel:
        logger.info(f"Loading Hugging Face model: {config.model_id} from {config.source_path} on {target_device}")
        try:
            model_kwargs = {'trust_remote_code': config.trust_remote_code}
            if config.revision:
                model_kwargs['revision'] = config.revision
            
            # For full model download (snapshot)
            # model_path = snapshot_download(repo_id=config.source_path, revision=config.revision, allow_patterns=["*.json", "*.safetensors", "*.bin", "*.py", "*.md"])
            # model = AutoModel.from_pretrained(model_path, **model_kwargs)
            
            # Direct loading
            model = AutoModel.from_pretrained(config.source_path, **model_kwargs)
            tokenizer = AutoTokenizer.from_pretrained(config.tokenizer_path or config.source_path, trust_remote_code=config.trust_remote_code)
            
            model.to(target_device)
            logger.info(f"Model {config.model_id} loaded to {target_device}")
            return LoadedModel(config=config, model_object=model, tokenizer_object=tokenizer, device=target_device)
        except Exception as e:
            logger.error(f"Error loading Hugging Face model {config.model_id}: {e}")
            raise ModelLoadingError(f"Failed to load Hugging Face model {config.model_id}: {e}")

    async def unload(self, loaded_model: LoadedModel):
        logger.info(f"Unloading Hugging Face model: {loaded_model.config.model_id}")
        del loaded_model.model_object
        del loaded_model.tokenizer_object
        if torch.cuda.is_available() and 'cuda' in loaded_model.device:
            torch.cuda.empty_cache()
        logger.info(f"Model {loaded_model.config.model_id} unloaded.")

class LocalFileSystemLoader(ModelLoaderInterface):
    async def load(self, config: ModelConfiguration, target_device: str) -> LoadedModel:
        logger.info(f"Loading local model: {config.model_id} from {config.source_path} on {target_device}")
        model_path = Path(config.source_path)
        if not model_path.exists() or not model_path.is_dir():
            raise ConfigurationError(f"Local model path does not exist or is not a directory: {config.source_path}")
        
        try:
            model_kwargs = {'trust_remote_code': config.trust_remote_code}
            model = AutoModel.from_pretrained(str(model_path), **model_kwargs)
            tokenizer_actual_path = config.tokenizer_path or str(model_path)
            tokenizer = AutoTokenizer.from_pretrained(tokenizer_actual_path, trust_remote_code=config.trust_remote_code)
            
            model.to(target_device)
            logger.info(f"Model {config.model_id} loaded to {target_device}")
            return LoadedModel(config=config, model_object=model, tokenizer_object=tokenizer, device=target_device)
        except Exception as e:
            logger.error(f"Error loading local model {config.model_id}: {e}")
            raise ModelLoadingError(f"Failed to load local model {config.model_id}: {e}")

    async def unload(self, loaded_model: LoadedModel):
        logger.info(f"Unloading local model: {loaded_model.config.model_id}")
        del loaded_model.model_object
        del loaded_model.tokenizer_object
        if torch.cuda.is_available() and 'cuda' in loaded_model.device:
            torch.cuda.empty_cache()
        logger.info(f"Model {loaded_model.config.model_id} unloaded.")

class BasicResourceManager:
    def get_available_gpu_memory_mb(self, gpu_id: int = 0) -> Optional[int]:
        if torch.cuda.is_available() and gpu_id < torch.cuda.device_count():
            try:
                # total_mem, free_mem = torch.cuda.mem_get_info(gpu_id) # Pytorch 1.8+
                # return free_mem // (1024 * 1024)
                # Using psutil-like approach for broader compatibility if torch.cuda.mem_get_info is tricky
                # For simplicity, let's assume a large amount if GPU is available, or rely on torch errors.
                # A more robust solution would use pynvml or similar.
                return torch.cuda.get_device_properties(gpu_id).total_memory // (1024**2) - (torch.cuda.memory_allocated(gpu_id) // (1024**2))
            except Exception as e:
                logger.warning(f"Could not get GPU memory info for gpu {gpu_id}: {e}")
                return None # Unknown
        return 0 # No GPU or invalid ID

    def get_available_ram_mb(self) -> int:
        return psutil.virtual_memory().available // (1024 * 1024)

    def check_resources(self, config: ModelConfiguration, target_device: str) -> bool:
        if 'cuda' in target_device:
            gpu_id_str = target_device.split(':')[-1]
            gpu_id = 0 if not gpu_id_str.isdigit() else int(gpu_id_str)
            
            if not (torch.cuda.is_available() and gpu_id < torch.cuda.device_count()):
                logger.warning(f"Requested CUDA device {target_device} not available.")
                return False
            
            available_gpu_mem = self.get_available_gpu_memory_mb(gpu_id)
            if config.required_gpu_memory_mb and available_gpu_mem is not None and available_gpu_mem < config.required_gpu_memory_mb:
                logger.warning(f"Insufficient GPU memory for {config.model_id}. Required: {config.required_gpu_memory_mb}MB, Available: {available_gpu_mem}MB on {target_device}")
                return False
        elif 'cpu' in target_device:
            available_ram = self.get_available_ram_mb()
            if config.required_ram_mb and available_ram < config.required_ram_mb:
                logger.warning(f"Insufficient RAM for {config.model_id}. Required: {config.required_ram_mb}MB, Available: {available_ram}MB")
                return False
        return True

class LLMModelManager:
    def __init__(self, config_path: str, resource_manager: Optional[BasicResourceManager] = None):
        self.model_registry: Dict[str, ModelConfiguration] = {}
        self.loaded_models: Dict[str, LoadedModel] = {}
        self.loaders: Dict[str, ModelLoaderInterface] = self._initialize_loaders()
        self.resource_manager = resource_manager or BasicResourceManager()
        self.config_path = config_path
        self._load_registry_from_config(config_path)
        self.lock = asyncio.Lock()

    def _initialize_loaders(self) -> Dict[str, ModelLoaderInterface]:
        return {
            "huggingface": HuggingFaceLoader(),
            "local": LocalFileSystemLoader(),
            # "s3": S3Loader(), # Future
            # "external_service": ExternalServiceConnector() # Future
        }

    def _load_registry_from_config(self, config_path: str):
        logger.info(f"Loading model registry from config: {config_path}")
        try:
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            if config_data and 'models' in config_data:
                for model_conf_dict in config_data['models']:
                    try:
                        model_config = ModelConfiguration(**model_conf_dict)
                        self.model_registry[model_config.model_id] = model_config
                        logger.info(f"Registered model from config: {model_config.model_id}")
                    except Exception as e:
                        logger.error(f"Invalid model configuration in {config_path} for entry {model_conf_dict.get('model_id', 'UNKNOWN')}: {e}")
            else:
                logger.warning(f"No 'models' section found or empty config file: {config_path}")
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_path}")
            raise ConfigurationError(f"Configuration file not found: {config_path}")
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML configuration file {config_path}: {e}")
            raise ConfigurationError(f"Error parsing YAML configuration file {config_path}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error loading registry from {config_path}: {e}")
            raise ConfigurationError(f"Unexpected error loading registry from {config_path}: {e}")

    async def register_model(self, model_config_dict: Dict[str, Any], persist: bool = True) -> bool:
        async with self.lock:
            try:
                model_config = ModelConfiguration(**model_config_dict)
                if model_config.model_id in self.model_registry and self.model_registry[model_config.model_id] == model_config:
                    logger.info(f"Model {model_config.model_id} already registered with identical configuration.")
                    return True # Or False if update means change
                
                self.model_registry[model_config.model_id] = model_config
                logger.info(f"Dynamically registered model: {model_config.model_id}")
                
                if persist:
                    self._persist_registry_to_config()
                return True
            except Exception as e:
                logger.error(f"Error registering model {model_config_dict.get('model_id', 'UNKNOWN')}: {e}")
                raise ConfigurationError(f"Failed to register model: {e}")

    def _persist_registry_to_config(self):
        logger.info(f"Persisting model registry to config: {self.config_path}")
        models_list = []
        for model_id, model_config_obj in self.model_registry.items():
            # Convert ModelConfiguration object back to dict, carefully handling defaults
            conf_dict = {k: v for k, v in model_config_obj.__dict__.items() if v is not None}
            models_list.append(conf_dict)
        
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump({'models': models_list}, f, sort_keys=False)
            logger.info(f"Successfully persisted registry to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to persist registry to {self.config_path}: {e}")
            # Decide if this should raise an error or just warn

    async def load_model(self, model_id: str, force_reload: bool = False) -> LoadedModel:
        async with self.lock:
            if model_id in self.loaded_models and not force_reload:
                logger.info(f"Model {model_id} already loaded. Returning existing instance.")
                return self.loaded_models[model_id]
            
            if model_id not in self.model_registry:
                logger.error(f"Model {model_id} not found in registry.")
                raise ModelNotFoundError(f"Model {model_id} not found in registry.")

            config = self.model_registry[model_id]
            
            target_device = config.device_preference
            if target_device == "auto":
                target_device = "cuda" if torch.cuda.is_available() else "cpu"
            elif target_device == "cuda" and not torch.cuda.is_available():
                logger.warning(f"CUDA preferred for {model_id} but not available. Falling back to CPU.")
                target_device = "cpu"

            if not self.resource_manager.check_resources(config, target_device):
                raise ResourceNotAvailableError(f"Insufficient resources to load model {model_id} on {target_device}")

            loader = self.loaders.get(config.source_type)
            if not loader:
                logger.error(f"No loader available for source type: {config.source_type} for model {model_id}")
                raise ConfigurationError(f"No loader for source type {config.source_type}")

            logger.info(f"Attempting to load model {model_id} using {config.source_type} loader on {target_device}.")
            try:
                if model_id in self.loaded_models and force_reload:
                    logger.info(f"Force reloading {model_id}. Unloading existing instance first.")
                    await self.unload_model(model_id, acquire_lock=False) # Avoid deadlock
                
                loaded_model_instance = await loader.load(config, target_device)
                self.loaded_models[model_id] = loaded_model_instance
                logger.info(f"Successfully loaded model {model_id} to {loaded_model_instance.device}.")
                return loaded_model_instance
            except Exception as e:
                logger.error(f"Failed to load model {model_id}: {e}")
                # Clean up if partial load occurred, though loader should handle its own state
                if model_id in self.loaded_models:
                    del self.loaded_models[model_id]
                raise ModelLoadingError(f"Failed during model loading process for {model_id}: {e}")

    async def unload_model(self, model_id: str, acquire_lock: bool = True) -> bool:
        # acquire_lock is to allow internal calls without deadlocking
        _lock = None
        if acquire_lock:
            _lock = self.lock
            await _lock.acquire()
        
        try:
            if model_id not in self.loaded_models:
                logger.info(f"Model {model_id} not currently loaded. No action taken.")
                return False
            
            loaded_model_to_unload = self.loaded_models[model_id]
            config = loaded_model_to_unload.config
            loader = self.loaders.get(config.source_type)

            if not loader:
                logger.error(f"No loader found for source type {config.source_type} during unload of {model_id}. Removing from loaded list.")
                del self.loaded_models[model_id]
                return False # Or raise error
            
            logger.info(f"Attempting to unload model {model_id} using {config.source_type} loader.")
            await loader.unload(loaded_model_to_unload)
            del self.loaded_models[model_id]
            logger.info(f"Successfully unloaded model {model_id}.")
            return True
        except Exception as e:
            logger.error(f"Error unloading model {model_id}: {e}")
            # Potentially leave in inconsistent state if loader fails, but we remove from loaded_models
            if model_id in self.loaded_models:
                 del self.loaded_models[model_id] # Ensure it's marked as not loaded
            return False # Or raise an error
        finally:
            if _lock:
                _lock.release()

    async def get_model_instance(self, model_id: str) -> LoadedModel:
        if model_id not in self.loaded_models:
            logger.info(f"Model {model_id} not loaded. Attempting to load.")
            return await self.load_model(model_id)
        return self.loaded_models[model_id]

    async def list_available_models(self) -> List[Dict[str, Any]]:
        async with self.lock:
            model_list = []
            for model_id, config in self.model_registry.items():
                status = "loaded" if model_id in self.loaded_models else "not_loaded"
                device = self.loaded_models[model_id].device if status == "loaded" else "N/A"
                model_list.append({
                    "model_id": model_id,
                    "source_type": config.source_type,
                    "source_path": config.source_path,
                    "status": status,
                    "device": device
                })
            return model_list

    async def get_model_configuration(self, model_id: str) -> ModelConfiguration:
        async with self.lock:
            if model_id not in self.model_registry:
                raise ModelNotFoundError(f"Configuration for model {model_id} not found.")
            return self.model_registry[model_id]

    async def discover_models(self):
        # Placeholder for more advanced discovery (e.g., scanning local dirs, querying remote registries)
        # For now, discovery is primarily through the initial config file loading.
        logger.info("Model discovery currently relies on initial configuration file.")
        return list(self.model_registry.keys())

async def main_test():
    # Create a dummy config file for testing
    test_config_content = {
        "models": [
            {
                "model_id": "tiny-distilroberta",
                "source_type": "huggingface",
                "source_path": "sshleifer/tiny-distilroberta-base",
                "model_format": "transformers_pt",
                "device_preference": "cpu",
                "trust_remote_code": False
            },
            {
                "model_id": "nonexistent-hf-model",
                "source_type": "huggingface",
                "source_path": "org/this-model-does-not-exist-for-testing",
                "model_format": "transformers_pt",
                "device_preference": "cpu"
            },
            {
                "model_id": "dummy-local-model",
                "source_type": "local",
                "source_path": "/tmp/test-model-local-path", # Ensure this path exists with dummy files
                "model_format": "transformers_pt", # Assuming it's HF compatible structure
                "tokenizer_path": "/tmp/test-model-local-path",
                "device_preference": "cpu",
                "trust_remote_code": True # Often needed for local custom models
            }
        ]
    }
    test_config_path = "/tmp/test_llm_models.yaml"
    with open(test_config_path, 'w') as f:
        yaml.dump(test_config_content, f)

    # Create dummy local model files if they don't exist (as done by shell command previously)
    local_model_dir = Path("/tmp/test-model-local-path")
    if not local_model_dir.exists():
        local_model_dir.mkdir(parents=True, exist_ok=True)
        (local_model_dir / "config.json").write_text("{ \"model_type\": \"bert\" }") # Minimal config
        (local_model_dir / "pytorch_model.bin").write_text("dummy model content") # Dummy model file
        (local_model_dir / "tokenizer_config.json").write_text("{ \"model_type\": \"bert\" }")
        (local_model_dir / "vocab.txt").write_text("[UNK]\n[CLS]\n[SEP]")
        logger.info(f"Created dummy files in {local_model_dir}")

    manager = LLMModelManager(config_path=test_config_path)

    print("--- Initial Model Listing ---")
    models = await manager.list_available_models()
    for model_info in models:
        print(model_info)

    print("\n--- Testing Hugging Face Model Load (tiny-distilroberta) ---")
    try:
        loaded_hf_model = await manager.load_model("tiny-distilroberta")
        print(f"Loaded tiny-distilroberta: {type(loaded_hf_model.model_object)}, Device: {loaded_hf_model.device}")
        await manager.unload_model("tiny-distilroberta")
        print("Unloaded tiny-distilroberta.")
    except Exception as e:
        print(f"Error with tiny-distilroberta: {e}")

    print("\n--- Testing Nonexistent Hugging Face Model Load ---")
    try:
        await manager.load_model("nonexistent-hf-model")
    except ModelLoadingError as e:
        print(f"Correctly caught ModelLoadingError for nonexistent-hf-model: {e}")
    except Exception as e:
        print(f"Unexpected error for nonexistent-hf-model: {e}")

    print("\n--- Testing Local Model Load (dummy-local-model) ---")
    try:
        loaded_local_model = await manager.load_model("dummy-local-model")
        print(f"Loaded dummy-local-model: {type(loaded_local_model.model_object)}, Device: {loaded_local_model.device}")
        await manager.unload_model("dummy-local-model")
        print("Unloaded dummy-local-model.")
    except Exception as e:
        print(f"Error with dummy-local-model: {e}")

    print("\n--- Testing Get Model Instance (should load if not loaded) ---")
    try:
        instance = await manager.get_model_instance("tiny-distilroberta")
        print(f"Got instance for tiny-distilroberta. Status: {'loaded' if 'tiny-distilroberta' in manager.loaded_models else 'not loaded'}")
        await manager.unload_model("tiny-distilroberta") # Clean up
    except Exception as e:
        print(f"Error getting instance for tiny-distilroberta: {e}")

    print("\n--- Testing Model Registration (Dynamic) ---")
    new_model_config = {
        "model_id": "dynamic-model-test",
        "source_type": "huggingface",
        "source_path": "google/bert_uncased_L-2_H-128_A-2", # Another small model
        "model_format": "transformers_pt",
        "device_preference": "cpu"
    }
    try:
        await manager.register_model(new_model_config, persist=False) # Test without persisting to avoid changing test file
        print(f"Registered dynamic-model-test. Current registry: {await manager.list_available_models()}")
        loaded_dynamic = await manager.load_model("dynamic-model-test")
        print(f"Loaded dynamic-model-test: {type(loaded_dynamic.model_object)}")
        await manager.unload_model("dynamic-model-test")
        print("Unloaded dynamic-model-test.")
    except Exception as e:
        print(f"Error with dynamic model registration/load: {e}")
    
    # Clean up test config file
    # os.remove(test_config_path)
    # logger.info(f"Cleaned up {test_config_path}")

if __name__ == "__main__":
    asyncio.run(main_test())

