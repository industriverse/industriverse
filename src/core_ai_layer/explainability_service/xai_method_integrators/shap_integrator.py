# shap_integrator.py

import logging
from typing import Any, Dict, Optional, Type
import asyncio

# Attempt to import SHAP, but make it optional for environments where it might not be installed
try:
    import shap
except ImportError:
    shap = None
    logging.warning("SHAP library not found. SHAPIntegrator will not be functional.")

import numpy as np # SHAP often works with numpy arrays

from .base_integrator import XAIMethodIntegratorInterface
from ..model_adapters.base_adapter import ModelAdapterInterface, ProcessedData # Corrected import path
from ..xai_exceptions import ConfigurationError, ExplanationGenerationError, MethodNotApplicableError

logger = logging.getLogger(__name__)

class SHAPIntegrator(XAIMethodIntegratorInterface):
    """
    Integrator for SHAP (SHapley Additive exPlanations) based XAI methods.
    """

    def __init__(self, global_config: Optional[Dict[str, Any]] = None):
        super().__init__(global_config)
        if shap is None:
            logger.error("SHAP library is not installed. SHAPIntegrator cannot function.")
            # raise ImportError("SHAP library is required for SHAPIntegrator but not found.")

    def can_explain(
        self,
        model_info: Dict[str, Any], # Information about the model (e.g., type, framework)
        explanation_type_requested: str
    ) -> bool:
        if shap is None: return False # Cannot explain if SHAP is not installed

        supported_explanation_types = ["shap_feature_importance", "shap_instance_explanation"]
        if explanation_type_requested not in supported_explanation_types:
            return False

        # SHAP can work with many model types, especially tree-based and those with clear prediction functions.
        # For LLMs, specific SHAP variants (e.g., for text/transformers) are needed.
        model_framework = model_info.get("model_framework", "").lower()
        model_type = model_info.get("model_type", "").lower()

        if "llm" in model_type or "transformer" in model_type:
            # SHAP for LLMs often requires specific handling (e.g., shap.Explainer(model, tokenizer))
            # This basic integrator might not fully support complex LLM SHAP out-of-the-box without more setup.
            logger.info("SHAPIntegrator: Basic support for LLM/Transformer models; specific SHAP variants might be needed.")
            return True # Tentatively allow, but generation might be limited
        
        # Generally applicable to scikit-learn, xgboost, lightgbm, etc.
        if model_framework in ["scikit-learn", "xgboost", "lightgbm", "tensorflow", "pytorch"]:
            return True
        
        logger.warning(f"SHAPIntegrator might not be ideal for model framework: {model_framework}")
        return False # Default to False if unsure

    async def generate_explanation(
        self,
        model_adapter: Type[ModelAdapterInterface],
        instance_data: Optional[Any] = None,
        explanation_params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if shap is None:
            raise MethodNotApplicableError("SHAP library not installed, cannot generate SHAP explanations.")

        explanation_params = explanation_params or {}
        logger.info(f"Generating SHAP explanation with params: {explanation_params}")

        try:
            prediction_fn = await model_adapter.get_prediction_function()
            model_object = await model_adapter.get_model_object() # May be needed for some SHAP explainers
        except Exception as e:
            raise ModelAccessError(f"Failed to get model or prediction function via adapter: {e}")

        # Get background data (summary dataset for KernelSHAP or training data for TreeSHAP)
        background_data_sample_size = explanation_params.get("background_data_sample_size", 100)
        background_data: Optional[ProcessedData] = await model_adapter.get_background_data(sample_size=background_data_sample_size)

        if background_data is None and not (hasattr(model_object, "tree_limit") or isinstance(model_object, shap.models.TeacherForcing)): # TreeSHAP might not need background if model is passed directly
            # Some SHAP explainers (like KernelExplainer) require background data.
            # TreeExplainer can sometimes infer it or work directly with tree models.
            logger.warning("Background data not available or not provided, SHAP explanation might be limited or fail for some explainers.")
            # raise ConfigurationError("Background data is required for this SHAP explainer type but not available.")

        # Convert background_data to numpy if it's a list of lists (common for tabular)
        if background_data and isinstance(background_data, list) and all(isinstance(row, list) for row in background_data):
            try:
                background_data_np = np.array(background_data)
            except Exception as e:
                raise ExplanationGenerationError(f"Failed to convert background data to NumPy array: {e}")
        elif background_data and isinstance(background_data, np.ndarray):
            background_data_np = background_data
        else:
            # For text or other data types, SHAP might handle them differently (e.g. list of strings for TextExplainer)
            background_data_np = background_data # Pass as is
            if background_data is None:
                 logger.info("No background data provided for SHAP explainer.")

        # Initialize SHAP Explainer
        # This is a simplified selection; a real system would need more robust logic
        # or expect the user to specify the explainer type.
        try:
            if hasattr(model_object, "_tree") or (isinstance(model_object, dict) and "model" in model_object and hasattr(model_object["model"], "_tree")):
                 # For scikit-learn tree models or similar internal structures
                explainer = shap.TreeExplainer(model_object.get("model", model_object), data=background_data_np)
            elif callable(prediction_fn) and background_data_np is not None:
                # KernelExplainer is a model-agnostic explainer, but can be slow.
                # It requires a summary of the background data if it's large.
                if background_data_np.shape[0] > 200: # Heuristic for summarizing
                    background_summary = shap.kmeans(background_data_np, min(100, background_data_np.shape[0])) 
                else:
                    background_summary = background_data_np
                explainer = shap.KernelExplainer(prediction_fn, background_summary)
            elif isinstance(model_object, dict) and "model" in model_object and "tokenizer" in model_object:
                # For LLMs from Hugging Face Transformers (conceptual)
                # This requires the model to be a transformers model and tokenizer
                # explainer = shap.Explainer(model_object["model"], model_object["tokenizer"])
                # For now, let's simulate this path might fail if not a text model or if prediction_fn is not suitable
                logger.warning("Attempting generic SHAP for LLM; specific TextExplainer or PartitionExplainer might be better.")
                # Fallback to KernelExplainer if prediction_fn is suitable, otherwise this will error
                if callable(prediction_fn) and background_data_np is not None:
                     explainer = shap.KernelExplainer(prediction_fn, background_data_np if background_data_np.ndim > 1 else background_data_np.reshape(-1,1) )
                else:
                    raise MethodNotApplicableError("Cannot automatically determine SHAP explainer for this LLM structure with given data.")
            else:
                raise MethodNotApplicableError("Could not determine a suitable SHAP explainer for the model.")
        except Exception as e:
            logger.error(f"Error initializing SHAP explainer: {e}", exc_info=True)
            raise ExplanationGenerationError(f"Failed to initialize SHAP explainer: {str(e)}")

        # Generate SHAP values
        shap_values_result = None
        if instance_data:
            processed_instance_data = await model_adapter.preprocess_instance(instance_data)
            # Convert instance_data to numpy if it's a list (common for tabular)
            if isinstance(processed_instance_data, list):
                try:
                    instance_data_np = np.array(processed_instance_data)
                except Exception as e:
                    raise ExplanationGenerationError(f"Failed to convert instance data to NumPy array: {e}")
            elif isinstance(processed_instance_data, np.ndarray):
                instance_data_np = processed_instance_data
            elif isinstance(processed_instance_data, str): # For text models
                instance_data_np = processed_instance_data # SHAP TextExplainer takes string
            else:
                raise ExplanationGenerationError("Instance data is not in a recognized format for SHAP (list, ndarray, or string).")
            
            logger.info(f"Calculating SHAP values for instance: {instance_data_np}")
            try:
                # For text, explainer(instance_data_np) might be a list of Explanation objects
                if isinstance(instance_data_np, str) and hasattr(explainer, "model") and hasattr(explainer, "masker") : # Likely a text explainer
                    shap_values_obj = explainer([instance_data_np]) # Pass as a list for consistency
                    # shap_values_result = shap_values_obj[0].values # Extract values from the first (and only) explanation object
                    # For text, SHAP values can be complex. We need to structure them.
                    # Let's try to get a serializable format. This part is highly dependent on the SHAP explainer used for text.
                    # This is a placeholder for more robust text SHAP value extraction.
                    shap_values_result = {"text_shap_values": "Placeholder for complex text SHAP output"} 
                    if hasattr(shap_values_obj[0], "data") and hasattr(shap_values_obj[0], "values") and hasattr(shap_values_obj[0], "output_names") :
                        shap_values_result = {
                            "tokens": list(shap_values_obj[0].data),
                            "values_per_output": {str(name): list(val_array) for name, val_array in zip(shap_values_obj[0].output_names, shap_values_obj[0].values.T)},
                            "base_values": list(shap_values_obj[0].base_values)
                        }

                else:
                    shap_values_obj = explainer(instance_data_np)
                    shap_values_result = shap_values_obj.values
                    # SHAP values might be multi-dimensional for multi-class classification
                    # Convert to list for JSON serialization
                    if isinstance(shap_values_result, np.ndarray):
                        shap_values_result = shap_values_result.tolist()
                    
                    # Try to get expected_value (base_value)
                    expected_value = None
                    if hasattr(shap_values_obj, "base_values"):
                        expected_value = shap_values_obj.base_values
                        if isinstance(expected_value, np.ndarray):
                            expected_value = expected_value.tolist()
                    elif hasattr(explainer, "expected_value"):
                        expected_value = explainer.expected_value
                        if isinstance(expected_value, np.ndarray):
                            expected_value = expected_value.tolist()
                    
                    shap_values_result = {"values": shap_values_result, "expected_value": expected_value}

            except Exception as e:
                logger.error(f"Error calculating SHAP values: {e}", exc_info=True)
                raise ExplanationGenerationError(f"Failed to calculate SHAP values: {str(e)}")
        else: # Global explanation (feature importance from mean absolute SHAP values)
            if background_data_np is None:
                raise ConfigurationError("Background data is required for global SHAP feature importance but not available.")
            logger.info("Calculating global SHAP feature importance.")
            try:
                shap_values_global = explainer(background_data_np).values
                if isinstance(shap_values_global, np.ndarray):
                    if shap_values_global.ndim > 1 and shap_values_global.shape[0] == background_data_np.shape[0]:
                        # For multi-class, average importance over classes or take max, or sum abs values
                        if shap_values_global.ndim == 3: # (n_outputs, n_samples, n_features)
                             mean_abs_shap = np.abs(shap_values_global).mean(axis=1).mean(axis=0)
                        else: # (n_samples, n_features) or (n_samples, n_features, n_outputs) -> need to handle
                             mean_abs_shap = np.abs(shap_values_global).mean(axis=0)
                    else:
                         mean_abs_shap = np.abs(shap_values_global).mean(axis=0)
                    
                    feature_names = (await model_adapter.get_xai_specific_metadata() or {}).get("feature_names")
                    if not feature_names or len(feature_names) != len(mean_abs_shap):
                        feature_names = [f"feature_{i}" for i in range(len(mean_abs_shap))]
                    
                    importances = sorted(
                        [{"feature_name": name, "importance_score": score} for name, score in zip(feature_names, mean_abs_shap)],
                        key=lambda x: x["importance_score"], reverse=True
                    )
                    shap_values_result = {"type": "feature_importance", "importances": importances}
                else:
                    # This case might occur for text explainers where global importance is different
                    shap_values_result = {"global_shap_summary": "Placeholder for non-array global SHAP output"}

            except Exception as e:
                logger.error(f"Error calculating global SHAP feature importance: {e}", exc_info=True)
                raise ExplanationGenerationError(f"Failed to calculate global SHAP feature importance: {str(e)}")

        return shap_values_result

