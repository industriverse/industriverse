# base_adapter.py

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Callable, Type

# Placeholder for actual model objects or detailed metadata structures
ModelObject = Any 
ModelPredictionFunction = Callable[..., Any] # e.g., Callable[[List[Dict]], List[float]]
ProcessedData = Any

class ModelDetails(ABC):
    """Abstract class to hold detailed information about a model."""
    model_id: str
    model_version: Optional[str]
    model_framework: Optional[str] # e.g., "scikit-learn", "tensorflow", "pytorch", "custom_llm"
    model_type: Optional[str] # e.g., "classifier", "regressor", "transformer_encoder_decoder"
    # Potentially path to artifacts, or how to load it via a service
    artifact_reference: Optional[Dict[str, Any]]
    # Training data reference might be useful for some XAI methods
    training_data_reference: Optional[Dict[str, Any]] = None 

class ModelAdapterInterface(ABC):
    """
    Abstract Base Class for Model Adapters.
    Each concrete adapter will interface with a specific model type or model-serving service.
    """

    @abstractmethod
    def __init__(self, model_identifier: Dict[str, Any], global_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the adapter with the model identifier and any global configurations.
        The model_identifier should contain enough information for the adapter to locate/load the model.
        """
        self.model_identifier = model_identifier
        self.global_config = global_config or {}
        self._model_details: Optional[ModelDetails] = None
        self._model_object: Optional[ModelObject] = None
        self._prediction_fn: Optional[ModelPredictionFunction] = None
        pass

    @abstractmethod
    async def load_model_details(self) -> ModelDetails:
        """
        Load or retrieve detailed information about the model.
        This might involve querying a model registry or another service.
        Should populate self._model_details.
        """
        pass

    @abstractmethod
    async def get_model_object(self) -> ModelObject:
        """
        Load or retrieve the actual model object (e.g., a scikit-learn pipeline, a PyTorch nn.Module).
        Should populate self._model_object if not already loaded.
        Requires model_details to be loaded first.
        """
        pass

    @abstractmethod
    async def get_prediction_function(self) -> ModelPredictionFunction:
        """
        Get a callable prediction function for the model.
        This function should take preprocessed input and return model predictions in a standard format.
        Should populate self._prediction_fn if not already available.
        Requires model_object to be loaded first.
        """
        pass

    @abstractmethod
    async def get_background_data(self, sample_size: int = 100) -> Optional[ProcessedData]:
        """
        Retrieve a sample of background data (e.g., training data) if required by the XAI method.
        The data should be in a format suitable for the model's prediction function.
        Requires model_details to be loaded.

        Args:
            sample_size: The desired number of samples for the background dataset.

        Returns:
            Processed background data, or None if not applicable/available.
        """
        pass
    
    @abstractmethod
    async def preprocess_instance(self, instance_data: Dict[str, Any]) -> ProcessedData:
        """
        Preprocess a single raw data instance into the format expected by the model's prediction function.
        Requires model_details to be loaded.

        Args:
            instance_data: The raw input data instance as a dictionary.

        Returns:
            The preprocessed data instance.
        """
        pass

    # Optional: Method to get specific model metadata relevant for XAI
    async def get_xai_specific_metadata(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve any model-specific metadata that might be useful for XAI methods
        (e.g., feature names, class names, embedding layers for LLMs).
        Requires model_details to be loaded.
        """
        return None

