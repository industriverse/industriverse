# explanation_schemas.py

import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List, Union, Literal

from pydantic import BaseModel, Field

class ModelIdentifier(BaseModel):
    """Specifies how to locate the model to be explained."""
    service_name: str = Field(..., description="Name of the service hosting the model (e.g., 'machine_learning_service', 'llm_service').")
    model_id: str = Field(..., description="Unique identifier of the model within its host service.")
    model_version: Optional[str] = Field(None, description="Specific version of the model.")
    # Optional: Further details if needed, e.g., specific endpoint or artifact path if not discoverable by ID/version
    additional_details: Optional[Dict[str, Any]] = Field(None, description="Additional details to locate/access the model.")

class ExplanationParameters(BaseModel):
    """Base model for XAI method-specific parameters."""
    # Common parameters can be added here if any
    pass

class SHAPParameters(ExplanationParameters):
    """Parameters specific to SHAP explanations."""
    background_data_sample_size: int = Field(100, description="Number of samples from background data to use for SHAP.")
    # Add other SHAP-specific params, e.g., explainer type (Kernel, Tree)

class LIMEParameters(ExplanationParameters):
    """Parameters specific to LIME explanations."""
    num_features: int = Field(10, description="Number of features to include in the explanation.")
    num_samples: int = Field(5000, description="Number of samples to generate for LIME.")
    # Add other LIME-specific params

class AttentionVisualizationParameters(ExplanationParameters):
    """Parameters for attention visualization."""
    layer_to_visualize: Optional[Union[int, str]] = Field(None, description="Specific layer or head for attention visualization.")
    # Add other attention-specific params

class ExplanationRequest(BaseModel):
    """Request to generate an explanation for a model's prediction or behavior."""
    request_id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, description="Unique ID for this explanation request.")
    model_identifier: ModelIdentifier = Field(..., description="Identifier for the model to be explained.")
    instance_data: Optional[Dict[str, Any]] = Field(None, description="Input data for which a local explanation is sought. Required for local explanations.")
    explanation_type: str = Field(..., description="Type of explanation requested (e.g., 'shap_summary', 'lime_instance', 'attention_map', 'natural_language_summary', 'feature_importance').")
    explanation_parameters: Optional[Dict[str, Any]] = Field(None, description="Method-specific parameters for the chosen XAI technique (e.g., SHAPParameters, LIMEParameters). Structure depends on explanation_type.")
    output_format: Literal["json", "text", "visualization_data_json"] = Field("json", description="Desired output format for the explanation.")
    requester_info: Optional[Dict[str, Any]] = Field(None, description="Information about the entity requesting the explanation (e.g., user_id, agent_id, service_name) for auditing.")
    # Flag to indicate if the job should be run asynchronously
    run_async: bool = Field(False, description="If true, the job will be run asynchronously and a job ID returned for status polling.")

class FeatureImportanceDetail(BaseModel):
    feature_name: str
    importance_score: float
    # Optional: directionality if applicable (e.g. for SHAP values)
    direction: Optional[Literal["positive", "negative"]] = None 

class ExplanationDataBase(BaseModel):
    """Base for structured explanation data."""
    pass

class FeatureImportanceExplanation(ExplanationDataBase):
    type: Literal["feature_importance"] = "feature_importance"
    importances: List[FeatureImportanceDetail]

class SHAPExplanation(ExplanationDataBase):
    type: Literal["shap_values"] = "shap_values"
    # SHAP values can be complex, e.g., per class for classification
    # For simplicity, a dictionary or a more structured model can be used
    shap_values: Dict[str, Any] # e.g., {"class_0": {"feature1": 0.2, ...}, "base_value": 0.1}
    expected_value: Optional[Any] = None # Base value for SHAP

class LIMEExplanation(ExplanationDataBase):
    type: Literal["lime_weights"] = "lime_weights"
    feature_weights: List[FeatureImportanceDetail]
    # LIME might also include a local prediction probability
    local_prediction: Optional[Dict[str, Any]] = None

class AttentionMapExplanation(ExplanationDataBase):
    type: Literal["attention_map"] = "attention_map"
    # Structure for attention scores, could be nested lists/dicts
    attention_scores: Any # e.g., for text: List[Dict[str, List[float]]] (token -> attention_to_other_tokens)
    tokens_input: Optional[List[str]] = None
    tokens_output: Optional[List[str]] = None # If applicable

class CounterfactualExplanation(ExplanationDataBase):
    type: Literal["counterfactual"] = "counterfactual"
    original_instance: Dict[str, Any]
    counterfactual_instance: Dict[str, Any]
    changed_features: List[str]
    target_outcome: Optional[Any] = None

class ProvenanceInfo(BaseModel):
    xai_method_used: str
    xai_method_parameters: Optional[Dict[str, Any]] = None
    model_version_explained: Optional[str] = None
    data_snapshot_reference: Optional[str] = None # Reference to data used for explanation if applicable

class ExplanationResponse(BaseModel):
    """Response containing the generated explanation."""
    explanation_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique ID for this generated explanation.")
    request_id: Optional[uuid.UUID] = Field(None, description="ID of the original ExplanationRequest.")
    model_identifier: ModelIdentifier = Field(..., description="Identifier of the model that was explained.")
    explanation_type: str = Field(..., description="Type of explanation provided.")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of when the explanation was generated.")
    explanation_data: Optional[Union[
        FeatureImportanceExplanation, 
        SHAPExplanation, 
        LIMEExplanation, 
        AttentionMapExplanation,
        CounterfactualExplanation,
        Dict[str, Any] # Fallback for generic JSON data
    ]] = Field(None, description="Structured explanation data. The exact structure depends on explanation_type.")
    natural_language_summary: Optional[str] = Field(None, description="A human-readable summary of the explanation.")
    visualization_hints: Optional[Dict[str, Any]] = Field(None, description="Data and suggestions for rendering visualizations (e.g., chart type, data points). Consuming service handles actual rendering.")
    confidence_score: Optional[float] = Field(None, description="Confidence score associated with the model's prediction or the explanation itself, if applicable.")
    provenance_info: Optional[ProvenanceInfo] = Field(None, description="Information about how the explanation was generated.")
    error_message: Optional[str] = Field(None, description="Error message if explanation generation failed for this specific response (e.g. if part of a batch).")

class AsyncJobStatus(BaseModel):
    job_id: uuid.UUID
    status: Literal["pending", "running", "completed", "failed"]
    message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    result_id: Optional[uuid.UUID] = Field(None, description="ID of the ExplanationResponse if status is 'completed'.")
    # Optional: progress percentage
    progress: Optional[float] = Field(None, ge=0, le=100)

# Example of how explanation_parameters might be structured in a request:
# request = ExplanationRequest(
#     ...,
#     explanation_type="shap_summary",
#     explanation_parameters=SHAPParameters(background_data_sample_size=200).model_dump()
# )

