import asyncio
from typing import Dict, Any, Optional, List
from .schema import T2LRequest, T2LResponse, LoRAMetadata, LoRAStatus
from .generator import LoRAGenerator
from .trainer import LoRATrainer

class TextToLoRAService:
    """
    Orchestrates the Text-to-LoRA pipeline.
    Receives requests from DGM, invokes Generator/Trainer, and manages LoRA lifecycle.
    """
    
    def __init__(self):
        self.generator = LoRAGenerator()
        self.trainer = LoRATrainer()
        self.lora_registry: Dict[str, LoRAMetadata] = {}

    async def create_lora(self, request: T2LRequest) -> T2LResponse:
        """
        Create a new LoRA from a text description.
        """
        try:
            # 1. Generate LoRA weights (simulated)
            metadata = await self.generator.generate(
                prompt=request.prompt,
                base_model=request.base_model,
                rank=request.rank,
                alpha=request.alpha
            )
            
            # 2. Register LoRA
            self.lora_registry[metadata.lora_id] = metadata
            
            return T2LResponse(
                request_id=request.request_id,
                lora_id=metadata.lora_id,
                status=LoRAStatus.READY,
                message=f"Successfully generated LoRA: {metadata.name}",
                estimated_completion_time=0.0
            )
            
        except Exception as e:
            return T2LResponse(
                request_id=request.request_id,
                lora_id="",
                status=LoRAStatus.FAILED,
                message=str(e)
            )

    def get_lora(self, lora_id: str) -> Optional[LoRAMetadata]:
        """Get LoRA metadata by ID"""
        return self.lora_registry.get(lora_id)

    def list_loras(self) -> List[LoRAMetadata]:
        """List all generated LoRAs"""
        return list(self.lora_registry.values())
