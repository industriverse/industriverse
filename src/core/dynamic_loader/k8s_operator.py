import asyncio
from typing import Dict, Any, List
from .loader_service import DynamicLoaderService

class DynamicLoaderOperator:
    """
    Kubernetes Operator for Dynamic Loader.
    Watches for 'DynamicModel' CRDs and reconciles state.
    """
    def __init__(self, loader_service: DynamicLoaderService):
        self.loader_service = loader_service
        self.running = False
        # Mock CRD storage
        self.crds: Dict[str, Dict[str, Any]] = {} 

    async def start_watch(self):
        self.running = True
        print("Operator: Watching for DynamicModel CRDs...")
        while self.running:
            # Simulate watch loop
            await self.reconcile()
            await asyncio.sleep(1.0)

    async def stop(self):
        self.running = False
        print("Operator: Stopped.")

    async def reconcile(self):
        """
        Reconcile desired state (CRDs) with actual state (Loader).
        """
        active_models = self.loader_service.get_active_models()
        
        # 1. Check for CRDs that need loading
        for name, spec in self.crds.items():
            if name not in active_models:
                print(f"Operator: Reconciling {name} -> LOAD")
                await self.loader_service.load_model(name, context=spec.get("context", {}))
                
        # 2. Check for Active Models that should be unloaded (deleted CRDs)
        # Copy keys to avoid runtime error during iteration
        for name in list(active_models.keys()):
            if name not in self.crds:
                print(f"Operator: Reconciling {name} -> UNLOAD")
                await self.loader_service.unload_model(name)

    # Mock External API to Apply CRD
    async def apply_crd(self, name: str, spec: Dict[str, Any]):
        print(f"Operator: CRD Applied: {name}")
        self.crds[name] = spec

    async def delete_crd(self, name: str):
        print(f"Operator: CRD Deleted: {name}")
        if name in self.crds:
            del self.crds[name]
