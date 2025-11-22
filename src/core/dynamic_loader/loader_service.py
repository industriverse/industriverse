import asyncio
from typing import Dict, Any, Optional, List
from .event_emitter import DynamicLoaderEventEmitter
from .registry_client import RegistryClient
from .lora_manager import LoRAManager
from .proof_client import ProofClient
from .visualization_service import VisualizationService

class DynamicLoaderService:
    def __init__(self):
        self.event_emitter = DynamicLoaderEventEmitter()
        self.registry_client = RegistryClient()
        self.lora_manager = LoRAManager(self.event_emitter, self.registry_client)
        self.proof_client = ProofClient()
        self.visualization_service = VisualizationService(self.event_emitter)
        self.active_models: Dict[str, Any] = {} # model_name -> loaded_object

    async def start(self):
        await self.event_emitter.connect()

    async def stop(self):
        await self.event_emitter.close()

    async def load_model(self, model_name: str, context: Dict[str, Any] = None) -> bool:
        """
        Hot-swap load a model with Rollback support and ZK Proofs.
        """
        if context is None:
            context = {}

        print(f"Requesting load for: {model_name}")
        
        # Snapshot current state for rollback
        previous_state = self.active_models.copy()
        
        try:
            # 1. Fetch Info
            info = await self.registry_client.get_model_info(model_name)
            if not info:
                print(f"Model {model_name} not found in registry.")
                return False

            # 2. Simulate Load (Atomic Swap)
            await asyncio.sleep(0.1) # Simulate IO
            
            # SIMULATED FAILURE FOR TESTING ROLLBACK
            if context.get("simulate_failure"):
                raise Exception("Simulated Load Failure")

            self.active_models[model_name] = {"status": "active", "info": info}
            
            # 3. Generate ZK Proof
            proof = await self.proof_client.generate_proof(info["hash"], context)
            
            # 4. Emit Proof Event
            await self.event_emitter.emit_event(
                event_type="model_load",
                model_hash=info["hash"],
                context={**context, "zk_proof": proof}
            )
            
            # 5. Update Visualization
            await self.visualization_service.broadcast_state(self.active_models)
            
            return True
            
        except Exception as e:
            print(f"Load failed: {e}. Initiating ROLLBACK.")
            self.active_models = previous_state
            
            await self.event_emitter.emit_event(
                event_type="rollback",
                model_hash="N/A",
                context={"reason": str(e), "target_model": model_name}
            )
            return False

    async def unload_model(self, model_name: str) -> bool:
        if model_name in self.active_models:
            info = self.active_models[model_name]["info"]
            del self.active_models[model_name]
            
            await self.event_emitter.emit_event(
                event_type="model_unload",
                model_hash=info["hash"],
                context={"reason": "explicit_unload"}
            )
            
            # Update Visualization
            await self.visualization_service.broadcast_state(self.active_models)
            
            return True
        return False

    # Delegate to LoRAManager
    async def load_adapter(self, base_model: str, adapter_name: str, context: Dict[str, Any] = None) -> bool:
        result = await self.lora_manager.load_adapter(base_model, adapter_name, context or {})
        if result:
             await self.visualization_service.broadcast_state(self.active_models)
        return result

    async def unload_adapter(self, base_model: str, adapter_name: str) -> bool:
        result = await self.lora_manager.unload_adapter(base_model, adapter_name)
        if result:
             await self.visualization_service.broadcast_state(self.active_models)
        return result

    def get_active_models(self):
        return self.active_models
        
    def get_active_adapters(self, base_model: str) -> List[str]:
        return self.lora_manager.get_active_adapters(base_model)
