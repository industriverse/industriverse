# Explainability Service (XAI) - Usage and API Documentation

**Version:** 1.0
**Date:** May 13, 2025

## 1. Overview

The Explainability Service (`explainability_service`) is a component within the Core AI Layer of the Industrial Foundry Framework. It provides functionalities to generate and manage explanations for predictions and behaviors of both traditional Machine Learning (ML) models and Large Language Models (LLMs). This service aims to enhance transparency, build trust, aid in debugging, ensure compliance, and promote responsible AI practices.

This document details how to use the service, its API endpoints, data schemas, and integration patterns.

## 2. Core Concepts

*   **Explanation Request**: A request to the service to generate an explanation for a specific model and, optionally, a specific data instance.
*   **Model Identifier**: A structured way to specify the target model, including the service hosting it (e.g., `machine_learning_service`, `llm_service`), model ID, and version.
*   **Explanation Type**: The kind of explanation desired (e.g., `shap_feature_importance`, `shap_instance_explanation`, `attention_map`).
*   **XAI Method Integrator**: A module within the service that wraps a specific explainability technique (e.g., SHAP, LIME).
*   **Model Adapter**: A module that provides a standardized interface to interact with models from different sources (e.g., `MLServiceAdapter` for scikit-learn models, `LLMServiceAdapter` for Hugging Face Transformers).
*   **Explanation Response**: The output from the service, containing the generated explanation data, natural language summaries, and provenance information.
*   **Synchronous/Asynchronous Operations**: The service supports both immediate (synchronous) explanation generation for quick requests and background (asynchronous) processing for potentially long-running XAI methods.

## 3. Architecture Reference

The `explainability_service` is architected with modularity in mind:

```
core_ai_layer/
└── explainability_service/
    ├── __init__.py
    ├── explanation_generator_service.py  # Main orchestrator
    ├── explanation_schemas.py          # Pydantic data models
    ├── xai_exceptions.py               # Custom exceptions
    ├── xai_method_integrators/         # For specific XAI techniques (e.g., shap_integrator.py)
    │   ├── __init__.py
    │   ├── base_integrator.py
    │   └── shap_integrator.py
    │   └── ...
    └── model_adapters/                 # For interfacing with model sources (e.g., ml_service_adapter.py)
        ├── __init__.py
        ├── base_adapter.py
        ├── ml_service_adapter.py
        └── llm_service_adapter.py
        └── ...
```

Refer to the `explainability_service_design.md` document for detailed architectural diagrams and component descriptions.

## 4. API Endpoints and Usage

The service is primarily accessed via an API, which would be exposed through the Protocol Layer of the Industrial Foundry Framework (e.g., via REST, gRPC, or MCP/A2A messages).

### 4.1. Main Service Class

`core_ai_layer.explainability_service.ExplanationGeneratorService`

**Initialization:**

```python
from core_ai_layer.explainability_service import ExplanationGeneratorService
from core_ai_layer.explainability_service.xai_method_integrators import SHAPIntegrator
from core_ai_layer.explainability_service.model_adapters import MLServiceAdapter, LLMServiceAdapter

# Example initialization (integrators and adapters can be auto-discovered or explicitly passed)
# In a deployed system, these would typically be registered at startup.
xai_service = ExplanationGeneratorService(
    integrators=[SHAPIntegrator], 
    adapters=[MLServiceAdapter, LLMServiceAdapter],
    global_xai_config={}
)
```

### 4.2. Generating an Explanation

**Method**: `async explanation_generator_service.generate_explanation(request: ExplanationRequest) -> Union[ExplanationResponse, AsyncJobStatus]`

*   **Request Schema**: `ExplanationRequest` (defined in `explanation_schemas.py`)
*   **Response Schema**: 
    *   `ExplanationResponse` if `request.run_async` is `False`.
    *   `AsyncJobStatus` if `request.run_async` is `True`.

**Example Synchronous Request (ML Model - SHAP Feature Importance):**

```python
from core_ai_layer.explainability_service.explanation_schemas import ExplanationRequest, ModelIdentifier

request_payload = ExplanationRequest(
    model_identifier=ModelIdentifier(
        service_name="machine_learning_service",
        model_id="sample_classifier_001",
        model_version="1.0"
    ),
    explanation_type="shap_feature_importance", # Global explanation
    explanation_parameters={"background_data_sample_size": 50}, # SHAP specific
    output_format="json",
    run_async=False,
    requester_info={"user_id": "developer_test"}
)

# Assuming xai_service is an instance of ExplanationGeneratorService
# In a real application, this would be an async call
# explanation_response = await xai_service.generate_explanation(request_payload)
# print(explanation_response.model_dump_json(indent=2))
```

**Example Asynchronous Request (LLM - SHAP Instance Explanation):**

```python
request_payload_async = ExplanationRequest(
    model_identifier=ModelIdentifier(
        service_name="llm_service",
        model_id="sample_llm_gpt2_001",
        model_version="main"
    ),
    instance_data={"text": "Explain this sentence using SHAP for LLMs."},
    explanation_type="shap_instance_explanation", # Placeholder, specific LLM SHAP type might differ
    explanation_parameters={"detail_level": "token"}, # Example param
    output_format="json",
    run_async=True,
    requester_info={"agent_id": "xai_agent_007"}
)

# async_job_status = await xai_service.generate_explanation(request_payload_async)
# print(f"Async Job ID: {async_job_status.job_id}, Status: {async_job_status.status}")
```

### 4.3. Checking Asynchronous Job Status

**Method**: `async explanation_generator_service.get_async_job_status(job_id: uuid.UUID) -> AsyncJobStatus`

*   **Request**: `job_id` (UUID of the asynchronous job).
*   **Response Schema**: `AsyncJobStatus`.

```python
# job_id_from_previous_step = async_job_status.job_id
# current_status = await xai_service.get_async_job_status(job_id_from_previous_step)
# print(f"Job {current_status.job_id} Status: {current_status.status}, Message: {current_status.message}")

# if current_status.status == "completed" and current_status.result_id:
#     explanation_result = await xai_service.get_explanation_result(current_status.result_id)
#     print(explanation_result.model_dump_json(indent=2))
```

### 4.4. Retrieving Explanation Result (for completed async jobs)

**Method**: `async explanation_generator_service.get_explanation_result(explanation_id: uuid.UUID) -> ExplanationResponse`

*   **Request**: `explanation_id` (UUID of the explanation, usually obtained from a completed `AsyncJobStatus.result_id`).
*   **Response Schema**: `ExplanationResponse`.
*   **Note**: This method currently relies on the `AsyncJobStatus` object holding the full response for demonstration. A production system would use persistent storage for results.

## 5. Data Schemas (`explanation_schemas.py`)

Key Pydantic models are defined in `explanation_schemas.py`. Refer to this file for detailed field descriptions.

*   `ModelIdentifier`: Specifies the model to be explained.
*   `ExplanationRequest`: Input schema for requesting an explanation.
    *   `model_identifier: ModelIdentifier`
    *   `instance_data: Optional[Dict[str, Any]]` (for local explanations)
    *   `explanation_type: str` (e.g., `shap_feature_importance`, `shap_instance_explanation`)
    *   `explanation_parameters: Optional[Dict[str, Any]]` (method-specific)
    *   `output_format: Literal["json", "text", "visualization_data_json"]`
    *   `requester_info: Optional[Dict[str, Any]]` (for auditing)
    *   `run_async: bool`
*   `ExplanationResponse`: Output schema containing the explanation.
    *   `explanation_id: uuid.UUID`
    *   `explanation_data: Optional[Union[...]]` (structured data, e.g., `FeatureImportanceExplanation`, `SHAPExplanation`)
    *   `natural_language_summary: Optional[str]`
    *   `visualization_hints: Optional[Dict[str, Any]]`
    *   `provenance_info: Optional[ProvenanceInfo]`
*   `AsyncJobStatus`: Schema for asynchronous job status.
*   Specific explanation data structures (e.g., `FeatureImportanceExplanation`, `SHAPExplanation`).
*   Parameter models (e.g., `SHAPParameters`).

## 6. XAI Method Integrators

Integrators adapt specific XAI libraries/techniques to a common interface (`XAIMethodIntegratorInterface`).

*   **`SHAPIntegrator` (`shap_integrator.py`)**: Provides explanations using the SHAP library. Supports both global feature importance and local instance explanations. Requires the `shap` library to be installed.
    *   **Supported `explanation_type` values**: `shap_feature_importance`, `shap_instance_explanation`.
    *   **Key `explanation_parameters`**:
        *   `background_data_sample_size` (int, default: 100): For methods like KernelSHAP.

To add new XAI methods, create a new class inheriting from `XAIMethodIntegratorInterface` and implement its abstract methods. Register the new integrator with the `ExplanationGeneratorService`.

## 7. Model Adapters

Adapters provide a bridge to models managed by different services or stored in various formats, implementing `ModelAdapterInterface`.

*   **`MLServiceAdapter` (`ml_service_adapter.py`)**: Interfaces with traditional ML models (e.g., scikit-learn) notionally managed by a `machine_learning_service`. It includes placeholder logic for fetching model details, objects, prediction functions, and background data.
*   **`LLMServiceAdapter` (`llm_service_adapter.py`)**: Interfaces with LLMs (e.g., Hugging Face Transformers) notionally managed by an `llm_service`. Includes placeholder logic for model and tokenizer loading, prediction functions, and relevant metadata.

To support new model sources or types, create a new class inheriting from `ModelAdapterInterface`. Register the new adapter with the `ExplanationGeneratorService`.

## 8. Integration with Core AI Layer and Protocols

*   **`machine_learning_service` & `llm_service`**: The `MLServiceAdapter` and `LLMServiceAdapter` are designed to interact with these services to retrieve model artifacts and metadata. Actual client implementations for these interactions are placeholders and would need to be fully developed based on the APIs of those services.
*   **Data Layer**: Adapters may need to interact with the Data Layer to fetch background/training data. This interaction is also represented by placeholders.
*   **Protocol Layer (MCP/A2A, Agent Capsules)**:
    *   The API of the `explainability_service` (exposed via `ExplanationGeneratorService`) is designed to be wrapped by the Protocol Layer.
    *   Agent capsules or other services can construct `ExplanationRequest` objects and send them via MCP/A2A protocols.
    *   Responses (`ExplanationResponse` or `AsyncJobStatus`) are returned through the same channels.
    *   The `requester_info` field in `ExplanationRequest` can be used to pass agent or user identifiers for auditing.

## 9. Error Handling and Exceptions

The service uses custom exceptions defined in `xai_exceptions.py`:
*   `XAIError`: Base exception.
*   `ConfigurationError`: For issues with service setup or missing dependencies.
*   `ModelAccessError`: If a model cannot be loaded or accessed.
*   `DataAccessError`: If required data (e.g., background data) is inaccessible.
*   `MethodNotApplicableError`: If an XAI method cannot be applied to a model.
*   `ExplanationGenerationError`: For errors during the explanation process itself.
*   `ResourceNotFoundError`: If an async job or other resource is not found.
*   `InvalidInputError`: For invalid request parameters.

These exceptions are caught by the `ExplanationGeneratorService` and are either re-raised (for synchronous calls) or reflected in the `AsyncJobStatus.message` for asynchronous jobs.

## 10. Security and Compliance

*   **Authentication & Authorization**: Assumed to be handled by the broader Industrial Foundry Framework (e.g., API Gateway, Protocol Layer) before requests reach the service.
*   **Data Privacy**: Instance data passed for local explanations should be handled with care. The service itself does not persist instance data beyond the scope of processing a request unless explicitly configured for audit logging (which should also be secure).
*   **Auditability & Provenance**: 
    *   The `ExplanationRequest.requester_info` field allows tracking who requested an explanation.
    *   The `ExplanationResponse.provenance_info` field logs details about the XAI method used, its parameters, and the model version explained.
    *   Comprehensive logging (INFO, DEBUG, ERROR levels) is implemented throughout the service to trace operations.
*   **Input Validation**: Pydantic schemas enforce type checking and basic validation on request and response data.

## 11. Configuration

*   **Global Configuration**: The `ExplanationGeneratorService` can be initialized with a `global_xai_config` dictionary, which can be used to pass down configurations to adapters and integrators (e.g., client instances for other services, default parameters).
*   **Logging**: Standard Python logging is used. Configure logging level and handlers as per the framework-wide logging strategy.

## 12. Extensibility

*   **Adding New XAI Methods**: Implement a new class derived from `XAIMethodIntegratorInterface` and register it.
*   **Supporting New Model Types/Sources**: Implement a new class derived from `ModelAdapterInterface` and register it.

This documentation provides a guide to using and understanding the `explainability_service`. For implementation details, refer to the source code and the design document.
