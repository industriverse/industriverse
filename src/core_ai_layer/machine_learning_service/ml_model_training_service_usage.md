# MLModelTrainingService Usage Guide

This document details the usage of the `MLModelTrainingService`, a component of the `machine_learning_service` within the Core AI Layer. It is responsible for managing and executing machine learning model training jobs.

## 1. Overview

The `MLModelTrainingService` allows users to submit training jobs by specifying data sources, algorithms, hyperparameters, and other configurations. It simulates the process of fetching data, training a model, performing hyperparameter tuning (if configured), and storing the resulting model artifacts and metrics, potentially integrating with a Data Layer and a Model Registry.

## 2. Initialization

To use the `MLModelTrainingService`, instantiate it, optionally providing clients for Data Layer and Model Registry integration:

```python
from core_ai_layer.machine_learning_service.ml_model_training_service import MLModelTrainingService
# Assuming you have concrete implementations of these interfaces:
# from your_concrete_implementations import MyDataClient, MyModelRegistryClient

# data_client = MyDataClient() # Optional
# model_registry_client = MyModelRegistryClient() # Optional

# training_service = MLModelTrainingService(
#     data_layer_client=data_client, 
#     model_registry_client=model_registry_client
# )
# For placeholder usage without external clients:
training_service = MLModelTrainingService()
```

## 3. Core Functionalities

### 3.1. Submitting a Training Job

To start a new training job, call the `submit_training_job` method with a `TrainingJobRequest` object.

**Method:** `async submit_training_job(request: TrainingJobRequest) -> TrainingJobStatusResponse`

**Request Schema (`TrainingJobRequest` from `ml_models_schemas.py`):**

*   `model_name: str`: Name for the model being trained.
*   `model_version: Optional[str]`: Version for the model (e.g., "1.0.0"). Defaults if not provided.
*   `data_source_config: DataSourceConfig`: Configuration for accessing the training data.
*   `algorithm_config: AlgorithmConfig`: Configuration for the training algorithm and framework.
*   `hyperparameter_tuning_config: Optional[HyperparameterTuningConfig]`: (Optional) Configuration for hyperparameter tuning.
*   `resource_config: Optional[ResourceConfig]`: (Optional) Resource allocation for the job (conceptual).
*   `experiment_name: Optional[str]`: (Optional) Name of the experiment for tracking in a model registry.
*   `tags: Optional[Dict[str, Any]]`: (Optional) Tags for the training run.

**Response Schema (`TrainingJobStatusResponse` from `ml_models_schemas.py`):**

Returns the initial status of the job, including a unique `job_id`.

**Example:**

```python
# from core_ai_layer.machine_learning_service.ml_models_schemas import (
#     TrainingJobRequest, DataSourceConfig, AlgorithmConfig
# )
# import asyncio

# async def run_submit_example():
#     sample_data_config = DataSourceConfig(
#         path="s3://my-bucket/training-data/data.parquet",
#         type="parquet",
#         feature_columns=["feature1", "feature2"],
#         target_column="target"
#     )
#     sample_algo_config = AlgorithmConfig(
#         name="RandomForestClassifier",
#         framework="scikit-learn",
#         parameters={"n_estimators": 100, "random_state": 42}
#     )
#     training_request = TrainingJobRequest(
#         model_name="MyClassificationModel",
#         data_source_config=sample_data_config,
#         algorithm_config=sample_algo_config,
#         experiment_name="ClassificationExperiment_01"
#     )
#     try:
#         job_status = await training_service.submit_training_job(training_request)
#         print(f"Submitted training job ID: {job_status.job_id}, Status: {job_status.status}")
#     except ConfigurationError as e:
#         print(f"Configuration Error: {e.message}")

# asyncio.run(run_submit_example())
```

### 3.2. Getting Training Job Status

Retrieve the current status of a previously submitted training job using its `job_id`.

**Method:** `async get_training_job_status(job_id: uuid.UUID) -> TrainingJobStatusResponse`

**Response Schema (`TrainingJobStatusResponse`):**

Contains detailed status information, including `status` (e.g., "pending", "running", "completed", "failed"), `message`, `progress`, `metrics`, `artifacts_location`, etc.

**Example:**

```python
# import uuid
# # Assuming job_id was obtained from submit_training_job
# # target_job_id = uuid.UUID("your-job-id-here") 
# async def run_status_example(target_job_id):
#     try:
#         status = await training_service.get_training_job_status(target_job_id)
#         print(f"Job {status.job_id} Status: {status.status}, Progress: {status.progress}%")
#         if status.status == "completed":
#             print(f"Metrics: {status.metrics}")
#             print(f"Artifacts at: {status.artifacts_location}")
#         elif status.status == "failed":
#             print(f"Error Message: {status.message}")
#     except ResourceNotFoundError as e:
#         print(e.message)

# # To run: asyncio.run(run_status_example(target_job_id))
```

### 3.3. Listing Training Jobs

List all active (or recently completed/failed) training jobs, with optional pagination.

**Method:** `async list_training_jobs(limit: int = 100, offset: int = 0) -> List[TrainingJobStatusResponse]`

**Response:** A list of `TrainingJobStatusResponse` objects.

**Example:**

```python
# async def run_list_example():
#     jobs = await training_service.list_training_jobs(limit=10)
#     print(f"Found {len(jobs)} training jobs:")
#     for job in jobs:
#         print(f"  ID: {job.job_id}, Model: {job.model_name}, Status: {job.status}")

# # To run: asyncio.run(run_list_example())
```

## 4. Asynchronous Job Execution (`_execute_training_job`)

This is an internal method triggered by `submit_training_job`. It simulates the following steps:

1.  **Experiment Tracking Setup (Optional)**: If a `ModelRegistryClient` is provided and an `experiment_name` is specified, it attempts to create or use an existing experiment and starts a new run.
2.  **Data Fetching**: Simulates fetching data using the `DataLayerClient` (if provided).
3.  **Model Training**: Simulates the core model training process based on `AlgorithmConfig`.
4.  **Hyperparameter Tuning (Optional)**: Simulates HPT if `HyperparameterTuningConfig` is provided.
5.  **Artifact Storage**: Simulates storing the trained model and logs. If `ModelRegistryClient` is available, it attempts to log the model, parameters, and metrics to the registry. Otherwise, it uses a placeholder path.

Throughout this process, the `TrainingJobStatusResponse` for the job is updated with progress, status changes, and eventual outcomes (metrics, artifact locations).

## 5. Error Handling

The service uses custom exceptions defined in `ml_service_exceptions.py`:

*   `ConfigurationError`: Raised for invalid or missing request parameters during job submission.
*   `ResourceNotFoundError`: Raised by `get_training_job_status` if the job ID is not found.
*   `DataAccessError`: Raised during job execution if the `DataLayerClient` encounters an issue.
*   `ModelRegistryError`: Raised during job execution if the `ModelRegistryClient` encounters an issue.
*   `TrainingJobError`: A general error for issues within the training job execution itself (though currently, specific errors like `DataAccessError` are raised directly from the execution flow).

Failed jobs will have their status set to "failed" in the `TrainingJobStatusResponse`, with details in the `message` field.

## 6. Dependencies and Configuration

*   **Pydantic Schemas**: All data structures are defined in `ml_models_schemas.py`.
*   **Client Interfaces**: For full functionality, especially involving external data sources and model registries, concrete implementations of `DataLayerClientInterface` and `ModelRegistryClientInterface` (from `.data_layer_client_interface` and `.model_registry_client_interface` respectively) should be passed during service initialization.
*   **Logging**: The service uses standard Python logging. Configure a logger named `__name__` (i.e., `ml_model_training_service`) to see detailed logs.

This guide provides a foundational understanding of the `MLModelTrainingService`. Refer to the source code and the Pydantic schemas for more detailed specifications.
