# MLModelEvaluationService Usage Guide

This document details the usage of the `MLModelEvaluationService`, a component of the `machine_learning_service` within the Core AI Layer. It is responsible for managing and executing machine learning model evaluation jobs.

## 1. Overview

The `MLModelEvaluationService` allows users to submit evaluation jobs for trained models. It requires specifying the model to evaluate (via a URI, typically from a Model Registry), the evaluation dataset, and the metrics to compute. The service simulates loading the model, fetching data, performing predictions, calculating metrics, and generating/storing evaluation reports.

## 2. Initialization

To use the `MLModelEvaluationService`, instantiate it, optionally providing clients for Data Layer and Model Registry integration:

```python
from core_ai_layer.machine_learning_service.ml_model_evaluation_service import MLModelEvaluationService
# Assuming you have concrete implementations of these interfaces:
# from your_concrete_implementations import MyDataClient, MyModelRegistryClient

# data_client = MyDataClient() # Optional
# model_registry_client = MyModelRegistryClient() # Optional

# evaluation_service = MLModelEvaluationService(
#     data_layer_client=data_client, 
#     model_registry_client=model_registry_client
# )
# For placeholder usage without external clients:
evaluation_service = MLModelEvaluationService()
```

## 3. Core Functionalities

### 3.1. Submitting an Evaluation Job

To start a new evaluation job, call the `submit_evaluation_job` method with an `EvaluationJobRequest` object.

**Method:** `async submit_evaluation_job(request: EvaluationJobRequest) -> EvaluationJobStatusResponse`

**Request Schema (`EvaluationJobRequest` from `ml_models_schemas.py`):**

*   `model_uri: str`: URI of the trained model to be evaluated (e.g., from a model registry like MLflow or a direct path).
*   `data_source_config: DataSourceConfig`: Configuration for accessing the evaluation dataset.
*   `metrics_to_compute: List[str]`: A list of metric names to calculate (e.g., `["accuracy", "precision", "recall", "f1_score", "rmse"]`).
*   `experiment_name: Optional[str]`: (Optional) Name of the experiment if evaluation results are to be tracked in a model registry.
*   `tags: Optional[Dict[str, Any]]`: (Optional) Tags for the evaluation run.

**Response Schema (`EvaluationJobStatusResponse` from `ml_models_schemas.py`):**

Returns the initial status of the job, including a unique `job_id`.

**Example:**

```python
# from core_ai_layer.machine_learning_service.ml_models_schemas import (
#     EvaluationJobRequest, DataSourceConfig
# )
# import asyncio

# async def run_submit_eval_example():
#     sample_eval_data_config = DataSourceConfig(
#         path="s3://my-bucket/evaluation-data/eval_data.parquet",
#         type="parquet",
#         feature_columns=["feature1", "feature2"],
#         target_column="target"
#     )
#     evaluation_request = EvaluationJobRequest(
#         model_uri="mlflow_runs:/<some_run_id>/my_model", # Or e.g., "file:///mnt/models/my_model.pkl"
#         data_source_config=sample_eval_data_config,
#         metrics_to_compute=["accuracy", "f1_score"],
#         experiment_name="MyModel_Evaluation_Run"
#     )
#     try:
#         job_status = await evaluation_service.submit_evaluation_job(evaluation_request)
#         print(f"Submitted evaluation job ID: {job_status.job_id}, Status: {job_status.status}")
#     except ConfigurationError as e:
#         print(f"Configuration Error: {e.message}")

# asyncio.run(run_submit_eval_example())
```

### 3.2. Getting Evaluation Job Status

Retrieve the current status of a previously submitted evaluation job using its `job_id`.

**Method:** `async get_evaluation_job_status(job_id: uuid.UUID) -> EvaluationJobStatusResponse`

**Response Schema (`EvaluationJobStatusResponse`):**

Contains detailed status information, including `status` (e.g., "pending", "running", "completed", "failed"), `message`, calculated `metrics`, `report_location`, etc.

**Example:**

```python
# import uuid
# # Assuming job_id was obtained from submit_evaluation_job
# # target_job_id = uuid.UUID("your-eval-job-id-here") 
# async def run_eval_status_example(target_job_id):
#     try:
#         status = await evaluation_service.get_evaluation_job_status(target_job_id)
#         print(f"Job {status.job_id} Status: {status.status}")
#         if status.status == "completed":
#             print(f"Calculated Metrics: {status.metrics}")
#             print(f"Evaluation Report at: {status.report_location}")
#         elif status.status == "failed":
#             print(f"Error Message: {status.message}")
#     except ResourceNotFoundError as e:
#         print(e.message)

# # To run: asyncio.run(run_eval_status_example(target_job_id))
```

### 3.3. Listing Evaluation Jobs

List all active (or recently completed/failed) evaluation jobs, with optional pagination.

**Method:** `async list_evaluation_jobs(limit: int = 100, offset: int = 0) -> List[EvaluationJobStatusResponse]`

**Response:** A list of `EvaluationJobStatusResponse` objects.

**Example:**

```python
# async def run_list_eval_example():
#     jobs = await evaluation_service.list_evaluation_jobs(limit=10)
#     print(f"Found {len(jobs)} evaluation jobs:")
#     for job in jobs:
#         print(f"  ID: {job.job_id}, Model URI: {job.model_uri}, Status: {job.status}")

# # To run: asyncio.run(run_list_eval_example())
```

## 4. Asynchronous Job Execution (`_execute_evaluation_job`)

This internal method, triggered by `submit_evaluation_job`, simulates the evaluation pipeline:

1.  **Experiment Tracking Setup (Optional)**: If a `ModelRegistryClient` and `experiment_name` are provided, it may start a new run for tracking evaluation metrics and artifacts.
2.  **Load Model**: Simulates loading the specified model using the `ModelRegistryClient` (if available and `model_uri` is a registry URI) or directly (if `model_uri` is a path and no registry client is configured, though this path requires careful handling).
3.  **Fetch Evaluation Data**: Simulates fetching data using the `DataLayerClient` (if provided).
4.  **Perform Predictions**: Simulates making predictions on the evaluation data using the loaded model.
5.  **Calculate Metrics**: Simulates calculating the requested performance metrics.
6.  **Generate and Store Report**: Simulates generating an evaluation report and storing it. If a `ModelRegistryClient` and an active run exist, it may log metrics and the report to the registry. Otherwise, it uses placeholder paths for `report_location` and `visualizations_location`.

The `EvaluationJobStatusResponse` is updated throughout this process.

## 5. Error Handling

The service utilizes custom exceptions from `ml_service_exceptions.py`:

*   `ConfigurationError`: For invalid or missing request parameters.
*   `ResourceNotFoundError`: If an evaluation job ID is not found.
*   `DataAccessError`: If the `DataLayerClient` fails during data fetching.
*   `ModelRegistryError`: If the `ModelRegistryClient` fails (e.g., loading model, logging metrics).
*   `EvaluationJobError`: For general errors during the evaluation job execution.

Failed jobs will reflect a "failed" status and an error message in their `EvaluationJobStatusResponse`.

## 6. Dependencies and Configuration

*   **Pydantic Schemas**: Defined in `ml_models_schemas.py`.
*   **Client Interfaces**: Requires `DataLayerClientInterface` and `ModelRegistryClientInterface` for full functionality. Implementations should be passed during service initialization.
*   **Logging**: Uses standard Python logging. Configure the logger for `ml_model_evaluation_service` to view logs.

This guide provides an overview of the `MLModelEvaluationService`. For precise details, consult the source code and Pydantic schema definitions.
