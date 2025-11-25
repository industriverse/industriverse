import asyncio
from typing import Dict, Any, Optional, List
from .event_emitter import DynamicLoaderEventEmitter
from .registry_client import RegistryClient

class LoRAManager:
    """
    Manages LoRA adapters for base models.
    Handles fetching, caching, and applying adapters.
    """
    def __init__(self, event_emitter: DynamicLoaderEventEmitter, registry_client: RegistryClient):
        self.event_emitter = event_emitter
        self.registry_client = registry_client
        self.active_adapters: Dict[str, List[str]] = {} # base_model_name -> [adapter_names]

    async def load_adapter(self, base_model: str, adapter_name: str, context: Dict[str, Any]) -> bool:
        """
        Load and apply a LoRA adapter to a base model.
        """
        print(f"Requesting LoRA load: {adapter_name} for {base_model}")
        
        # 1. Fetch Path
        path = await self.registry_client.get_lora_path(adapter_name)
        if not path:
            print(f"Adapter {adapter_name} not found.")
            return False

        # 2. Simulate Load (PEFT apply)
        await asyncio.sleep(0.05) # Fast load for adapters
        
        if base_model not in self.active_adapters:
            self.active_adapters[base_model] = []
            
        if adapter_name not in self.active_adapters[base_model]:
            self.active_adapters[base_model].append(adapter_name)
            
        # 3. Emit Event
        await self.event_emitter.emit_event(
            event_type="adapter_load",
            model_hash=f"sha256:mock_adapter_{adapter_name}",
            context={**context, "base_model": base_model, "adapter": adapter_name}
        )
        
        return True

    async def unload_adapter(self, base_model: str, adapter_name: str) -> bool:
        if base_model in self.active_adapters and adapter_name in self.active_adapters[base_model]:
            self.active_adapters[base_model].remove(adapter_name)
            
            await self.event_emitter.emit_event(
                event_type="adapter_unload",
                model_hash=f"sha256:mock_adapter_{adapter_name}",
                context={"base_model": base_model}
            )
            return True
        return False

    def get_active_adapters(self, base_model: str) -> List[str]:
        return self.active_adapters.get(base_model, [])
