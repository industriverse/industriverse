# base_integrator.py

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type

# Forward reference for ModelAdapterInterface to avoid circular import
# It will be fully defined in model_adapters.base_adapter
class ModelAdapterInterface:
    pass 

class XAIMethodIntegratorInterface(ABC):
    """
    Abstract Base Class for XAI method integrators.
    Each concrete integrator will wrap a specific XAI library or technique.
    """

    @abstractmethod
    def __init__(self, global_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the integrator with any global configurations.
        """
        self.global_config = global_config or {}
        pass

    @abstractmethod
    def can_explain(
        self, 
        model_info: Dict[str, Any], # Information about the model (e.g., type, framework)
        explanation_type_requested: str
    ) -> bool:
        """
        Check if this integrator can handle the requested explanation type for the given model.

        Args:
            model_info: Dictionary containing details about the model.
            explanation_type_requested: The type of explanation being requested (e.g., "shap_summary", "lime_instance").

        Returns:
            True if the integrator can handle the request, False otherwise.
        """
        pass

    @abstractmethod
    async def generate_explanation(
        self,
        model_adapter: Type[ModelAdapterInterface], # The model adapter to interact with the model
        instance_data: Optional[Any] = None, # Instance data for local explanations
        explanation_params: Optional[Dict[str, Any]] = None, # Method-specific parameters
        # model_identifier: Dict[str, Any] # Added to pass to model_adapter
    ) -> Dict[str, Any]:
        """
        Generate the explanation.

        Args:
            model_adapter: An instance of a ModelAdapter to fetch model, prediction function, etc.
            instance_data: The specific data instance for which a local explanation is required. 
                           None for global explanations.
            explanation_params: Dictionary of parameters specific to the XAI method.
                           (e.g., for LIME: num_features, num_samples; for SHAP: background_data_sample_size)
            # model_identifier: Identifier for the model, to be used by the model_adapter.

        Returns:
            A dictionary containing the raw explanation data.
            The structure of this dictionary will be specific to the XAI method.
        """
        pass

