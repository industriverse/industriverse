from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

class LoRAStatus(Enum):
    PENDING = "pending"
    GENERATING = "generating"
    TRAINING = "training"
    READY = "ready"
    FAILED = "failed"

class T2LRequest(BaseModel):
    """Request to generate a LoRA from text description"""
    request_id: str
    prompt: str
    base_model: str
    target_modules: List[str] = Field(default_factory=lambda: ["q_proj", "v_proj"])
    rank: int = 8
    alpha: int = 16
    metadata: Dict[str, Any] = Field(default_factory=dict)

class LoRAMetadata(BaseModel):
    """Metadata for a generated LoRA"""
    lora_id: str
    name: str
    description: str
    base_model: str
    rank: int
    alpha: int
    target_modules: List[str]
    created_at: datetime
    path: str
    status: LoRAStatus
    generation_prompt: str
    training_metrics: Optional[Dict[str, float]] = None

class T2LResponse(BaseModel):
    """Response from T2L Service"""
    request_id: str
    lora_id: str
    status: LoRAStatus
    message: str
    estimated_completion_time: Optional[float] = None
