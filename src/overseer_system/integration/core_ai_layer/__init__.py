"""
Core AI Layer Integration Package initialization.

This module initializes the Core AI Layer integration package for the Overseer System,
providing integration with the Industriverse Core AI Layer components.

Author: Manus AI
Date: May 25, 2025
"""

# Core AI Layer integration components
from src.integration.core_ai_layer.llm_adapter import LLMAdapter
from src.integration.core_ai_layer.vq_vae_adapter import VQVAEAdapter
from src.integration.core_ai_layer.model_registry_adapter import ModelRegistryAdapter
from src.integration.core_ai_layer.inference_engine_adapter import InferenceEngineAdapter
from src.integration.core_ai_layer.training_pipeline_adapter import TrainingPipelineAdapter

__all__ = [
    'LLMAdapter',
    'VQVAEAdapter',
    'ModelRegistryAdapter',
    'InferenceEngineAdapter',
    'TrainingPipelineAdapter'
]
