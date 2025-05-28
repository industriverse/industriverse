# Machine Learning Service Usage Guide

This document provides a comprehensive guide to using the `machine_learning_service` within the Core AI Layer. This service is designed to manage the lifecycle of traditional machine learning models, including training, evaluation, and deployment.

## 1. Overview

The `machine_learning_service` is composed of three primary sub-services:

*   **`MLModelTrainingService`**: Manages the training of machine learning models. It handles data ingestion (via the Data Layer), model training using specified algorithms and frameworks, hyperparameter tuning, and the storage of trained model artifacts (typically via a Model Registry).
*   **`MLModelEvaluationService`**: Manages the evaluation of trained machine learning models. It loads models (from a Model Registry or path), fetches evaluation datasets, calculates various performance metrics, and can generate evaluation reports.
*   **`MLModelDeploymentService`**: Manages the deployment of trained and evaluated machine learning models. It handles packaging models for serving, provisioning deployment targets (e.g., API endpoints, batch inference jobs), and managing the lifecycle of these deployments.

These services are designed to be used together to create robust MLOps pipelines. They rely on defined Pydantic schemas for request and response objects, ensuring data consistency and validation.

## 2. Core Concepts

*   **Asynchronous Operations**: Most operations that involve significant processing (training, evaluation, deployment) are asynchronous. Submitting a job to these services will typically return an initial status response with a unique job ID. You can then use this job ID to query the status of the operation.
*   **Client Interfaces**: The services are designed to integrate with other components of the Industrial Foundry Framework, such as a Data Layer and a Model Registry (e.g., MLflow). These integrations are facilitated through abstract client interfaces (`DataLayerClientInterface`, `ModelRegistryClientInterface`). Concrete implementations of these clients must be provided when initializing the services for full functionality.
*   **Configuration via Pydantic Schemas**: All interactions with the services are governed by Pydantic models defined in `ml_models_schemas.py`. This ensures that requests are well-formed and provides clear data contracts.
*   **Error Handling**: The services use a set of custom exceptions defined in `ml_service_exceptions.py` to report errors in a structured manner. API responses for failed operations will reflect these errors.

## 3. Sub-Service Usage Guides

For detailed information on how to use each sub-service, including API specifications, request/response schemas, and code examples, please refer to their individual usage guides:

*   [MLModelTrainingService Usage Guide](./ml_model_training_service_usage.md)
*   [MLModelEvaluationService Usage Guide](./ml_model_evaluation_service_usage.md)
*   [MLModelDeploymentService Usage Guide](./ml_model_deployment_service_usage.md)

## 4. Common Pydantic Schemas (`ml_models_schemas.py`)

Several Pydantic models are shared or used as building blocks across the sub-services. Key common schemas include:

*   `DataSourceConfig`: Defines the source and configuration of data to be used for training or evaluation.
*   `AlgorithmConfig`: Specifies the machine learning algorithm, framework, and its parameters for training.
*   `HyperparameterTuningConfig`: Configuration for hyperparameter optimization during training.
*   `ResourceConfig`: Defines resource allocation for jobs (e.g., CPU, memory) - primarily conceptual in the current placeholder implementation.
*   `DeploymentTargetConfig`: Specifies the configuration for deploying a model, such as target type (API, batch), serving image, and replicas.

Refer to `ml_models_schemas.py` for the complete definitions of all request, response, and configuration models.

## 5. Initialization and Dependencies

To use the `machine_learning_service` components, you will typically initialize them with concrete implementations of the `DataLayerClientInterface` and `ModelRegistryClientInterface` if you intend to use features that rely on data fetching or model/experiment tracking with a registry.

```python
# Example: Conceptual Initialization
# from .ml_model_training_service import MLModelTrainingService
# from .ml_model_evaluation_service import MLModelEvaluationService
# from .ml_model_deployment_service import MLModelDeploymentService

# from .data_layer_client_interface import DataLayerClientInterface # Your concrete implementation
# from .model_registry_client_interface import ModelRegistryClientInterface # Your concrete implementation

# # Instantiate concrete clients (these are placeholders for your actual client classes)
# class MyDataClient(DataLayerClientInterface):
#     async def load_data(self, config): pass
#     async def get_data_schema(self, config): pass

# class MyRegistryClient(ModelRegistryClientInterface):
#     async def log_model(self, model, model_name, ...) -> str: pass
#     async def load_model(self, model_uri: str): pass
#     async def log_metrics(self, run_id: str, metrics, ...): pass
#     async def log_params(self, run_id: str, params): pass
#     async def log_artifact(self, run_id: str, local_path, ...): pass
#     async def download_artifacts(self, ...) -> str: pass
#     async def create_experiment(self, name, ...) -> str: pass
#     async def get_experiment_by_name(self, name): pass
#     async def start_run(self, ...): pass
#     async def end_run(self, run_id, ...): pass

# data_client = MyDataClient()
# registry_client = MyRegistryClient()

# training_service = MLModelTrainingService(data_layer_client=data_client, model_registry_client=registry_client)
# evaluation_service = MLModelEvaluationService(data_layer_client=data_client, model_registry_client=registry_client)
# deployment_service = MLModelDeploymentService(model_registry_client=registry_client)

# print("Machine Learning Services initialized (conceptually).")
```

If these clients are not provided, the services will operate with limited functionality (e.g., relying on simulated operations or direct paths for artifacts, and potentially raising `ConfigurationError` if a client is essential for a requested operation).

## 6. Error Handling

Each service method is designed to handle errors gracefully. When an error occurs (e.g., invalid configuration, resource not found, failure during job execution), the services will typically:

1.  Log the error with detailed information.
2.  For job-based operations, update the job status to "failed" and include an error message in the status response.
3.  For direct API calls that fail (e.g., requesting status of a non-existent job), raise a specific exception from `ml_service_exceptions.py` (e.g., `ResourceNotFoundError`, `ConfigurationError`).

Consumers of these services should implement try-except blocks to handle these exceptions and check job statuses for operational failures.

Refer to the individual service usage guides for more specific error handling details related to their operations.

