# LLMEvaluationService Usage Guide

## 1. Overview

The `LLMEvaluationService` is a component within the Core AI Layer of the Industriverse platform, designed to manage and execute evaluation jobs for Large Language Models (LLMs). It allows users to assess the performance of various models (both base and fine-tuned) against specified datasets using a range of metrics. The service handles the entire lifecycle of an evaluation job, from submission and configuration validation to execution, monitoring, and report generation.

Key functionalities include:
- Submission of evaluation jobs with detailed configurations (models, datasets, metrics).
- Asynchronous execution of evaluation tasks.
- Support for different dataset sources (e.g., Hugging Face Datasets) and metric libraries (e.g., Hugging Face `evaluate`).
- Extensible architecture for adding custom dataset loaders and metric handlers.
- Job status tracking and retrieval.
- Generation of detailed evaluation reports.
- Integration with `LLMModelManager` for accessing model instances and `LLMInferenceService` for generating predictions.

## 2. Core Concepts

- **Evaluation Job (`EvaluationJobConfig`, `EvaluationJobStatusInfo`):** Represents a single evaluation task. It is defined by a configuration specifying models to test, datasets to use, and metrics to compute. Its lifecycle is tracked via status updates.
- **Model Target (`ModelTargetConfig`):** Defines a specific model to be evaluated, identified by its `model_id` from the `LLMModelManager`.
- **Dataset Configuration (`EvaluationDatasetConfig`):** Specifies a dataset to be used for evaluation, including its source, path/ID, relevant columns, and any preprocessing steps.
- **Metric Configuration (`MetricConfig`):** Defines a metric to be computed, including its name, parameters, and the library to use (e.g., `evaluate`).
- **Dataset Loader (`BaseDatasetLoader`):** An abstract class for components responsible for loading and preprocessing data from various sources. Concrete implementations like `HuggingFaceDatasetLoader` handle specific dataset types.
- **Metric Handler (`BaseMetricHandler`):** An abstract class for components responsible for computing specific metrics. Concrete implementations like `EvaluateMetricHandler` use libraries like Hugging Face `evaluate`.
- **Evaluation Report (`EvaluationReport`):** A comprehensive document generated upon completion (or failure) of an evaluation job, containing the job configuration, final status, detailed metric results, and any errors encountered.

## 3. Service API and Usage

The `LLMEvaluationService` provides an asynchronous API for managing evaluation jobs.

### 3.1. Initialization

To use the service, it must first be initialized with instances of `LLMModelManager` and `LLMInferenceService`:

```python
# Assuming model_manager and inference_service are already initialized
# from .llm_model_manager import LLMModelManager
# from .llm_inference_service import LLMInferenceService

# Placeholder initializations for example context
class PlaceholderLLMModelManager:
    async def get_model_instance(self, model_id: str, for_training: bool = False):
        if model_id == "non_existent_model": raise Exception("Model not found")
        return {"model": "mock_model_instance", "tokenizer": "mock_tokenizer_instance"}

class PlaceholderLLMInferenceService:
    def __init__(self, model_manager):
        self.model_manager = model_manager
        self.simulate_inference_failure = False
        self.simulate_critical_failure = False
    async def process_inference_request(self, request):
        if self.simulate_critical_failure: raise Exception("Simulated critical inference failure")
        if self.simulate_inference_failure: return type("Resp", (), {"generated_text": None, "error_message": "Simulated error"})()
        return type("Resp", (), {"generated_text": f"Prediction for {request.prompt}", "error_message": None})()

model_manager = PlaceholderLLMModelManager()
inference_service = PlaceholderLLMInferenceService(model_manager)

eval_service = LLMEvaluationService(
    model_manager=model_manager,
    inference_service=inference_service
)
```

### 3.2. Submitting an Evaluation Job

Jobs are submitted using the `submit_evaluation_job` method, which takes an `EvaluationJobConfig` object.

```python
from datetime import datetime

job_config_data = {
    "job_name": "My First Evaluation Job",
    "model_targets": [
        {"model_id": "gpt2"} # Assuming 'gpt2' is a model managed by LLMModelManager
    ],
    "datasets": [
        {
            "dataset_id": "wikitext_sample_eval",
            "source_type": "hf_dataset",
            "path_or_id": "wikitext", # For real use, specify a config like 'wikitext-2-raw-v1'
            "split": "test",
            "input_column_names": ["text"],
            "target_column_name": "text" # Using 'text' as reference for illustrative purposes
        }
    ],
    "metrics": [
        {"metric_name": "rouge", "library": "evaluate", "params": {"rouge_types": ["rougeL"]}, "output_key": "rougeL"},
        {"metric_name": "bleu", "library": "evaluate"}
    ],
    "evaluation_parameters": {"batch_size": 8}
}

job_config = EvaluationJobConfig(**job_config_data)

# In an async context:
# status_info = await eval_service.submit_evaluation_job(job_config)
# print(f"Job {status_info.job_id} submitted with status: {status_info.status}")
```

**Important Note on `path_or_id` for Hugging Face Datasets:** When using `source_type: "hf_dataset"`, the `path_or_id` should correctly specify the dataset name and, if necessary, a specific configuration. For example, for `wikitext`, a valid `path_or_id` would be `'wikitext', 'wikitext-2-raw-v1'` if you were using `datasets.load_dataset` directly. The current `HuggingFaceDatasetLoader` implementation in the example might need adjustment or the `path_or_id` should be a string that `load_dataset` can directly consume (e.g. `wikitext:wikitext-2-raw-v1` or the test script might need to pass the config name separately if the loader is enhanced).

### 3.3. Checking Job Status

The status of a submitted job can be retrieved using `get_evaluation_job_status`:

```python
# job_id = status_info.job_id # From submission
# current_status = await eval_service.get_evaluation_job_status(job_id)
# if current_status:
#     print(f"Job {job_id} current status: {current_status.status}, Progress: {current_status.progress_percentage}%")
```

### 3.4. Listing Evaluation Jobs

A list of job statuses can be retrieved using `list_evaluation_jobs`:

```python
# all_job_statuses = await eval_service.list_evaluation_jobs(limit=10)
# for status in all_job_statuses:
#     print(f"Job ID: {status.job_id}, Name: {status.job_name}, Status: {status.status}")
```

### 3.5. Retrieving Evaluation Reports

Once a job is completed (or failed), its report can be fetched using `get_evaluation_report`:

```python
# if current_status and current_status.status in ["completed", "failed"]:
#     report = await eval_service.get_evaluation_report(job_id)
#     if report:
#         print(f"Report for Job {job_id} generated at {report.generated_at}:")
#         for model_id, dataset_results in report.results_per_model_dataset.items():
#             print(f"  Model: {model_id}")
#             for dataset_id, metrics in dataset_results.items():
#                 print(f"    Dataset: {dataset_id}")
#                 for metric_result in metrics:
#                     print(f"      Metric: {metric_result.metric_name}, Value: {metric_result.value}")
#         if report.errors:
#             print(f"  Errors encountered: {report.errors}")
```

### 3.6. Cancelling an Evaluation Job

An active job can be cancelled using `cancel_evaluation_job`:

```python
# was_cancelled = await eval_service.cancel_evaluation_job(job_id)
# if was_cancelled:
#     print(f"Job {job_id} cancellation request successful.")
# else:
#     print(f"Job {job_id} could not be cancelled (e.g., already completed or not found).")
```

### 3.7. Service Lifecycle (Start/Stop)

The service has `start()` and `shutdown()` methods for managing its lifecycle, primarily for handling background tasks and graceful cleanup.

```python
# await eval_service.start() # If any background processing/polling is implemented
# ... perform operations ...
# await eval_service.shutdown() # To clean up resources, cancel pending tasks
```

## 4. Configuration Details

### 4.1. `EvaluationJobConfig`

- `job_name` (Optional[str]): A user-friendly name.
- `model_targets` (List[`ModelTargetConfig`]): Specifies models to evaluate.
    - `model_id` (str): ID from `LLMModelManager`.
    - `version` (Optional[str]): Specific model version.
- `datasets` (List[`EvaluationDatasetConfig`]): Specifies datasets.
    - `dataset_id` (str): Unique ID for this dataset config within the job.
    - `source_type` (Literal["hf_dataset", "local_path", "data_layer_id"]): Type of dataset source.
    - `path_or_id` (str): Path, Hugging Face ID, or Data Layer ID.
    - `split` (Optional[str]): Dataset split (default: "test").
    - `input_column_names` (List[str]): Columns for input/prompt (default: ["text"]).
    - `target_column_name` (Optional[str]): Column for reference/target text.
    - `task_type` (Optional[Literal[...]]): Task type (e.g., "text-generation").
    - `preprocessing_params` (Optional[Dict]): Parameters for preprocessing.
- `metrics` (List[`MetricConfig`]): Specifies metrics.
    - `metric_name` (str): Name of the metric (e.g., "accuracy", "rougeL").
    - `params` (Optional[Dict]): Parameters for the metric.
    - `output_key` (Optional[str]): Key if metric returns a dict.
    - `library` (Literal["evaluate", "lm-evaluation-harness", "custom"]): Metric source library (default: "evaluate").
- `evaluation_parameters` (Optional[Dict]): Global parameters (e.g., `batch_size`).

### 4.2. `EvaluationJobStatusInfo`

Provides detailed status of a job, including:
- `job_id`, `job_name`
- `status`: (queued, preprocessing, running_inference, computing_metrics, generating_report, completed, failed, cancelled)
- `progress_percentage`
- `current_model_id`, `current_dataset_id`, `current_metric_name` (during processing)
- `start_time`, `end_time`, `error_message`, `created_at`

### 4.3. `EvaluationReport`

Contains the final results:
- `report_id`, `job_id`, `job_config`, final `status_info`.
- `results_per_model_dataset`: A nested dictionary (`model_id` -> `dataset_id` -> List[`MetricResult`]).
- `generated_at`, `errors` (list of error messages encountered).

## 5. Extensibility

The service is designed to be extensible:

### 5.1. Custom Dataset Loaders

To support new dataset sources or formats:
1. Create a class that inherits from `BaseDatasetLoader`.
2. Implement the `async def load_and_preprocess_data(self) -> AsyncGenerator[Dict[str, Any], None]` method. This method should yield dictionaries, each representing a processed sample with at least `"prompt"` and optionally `"reference"` and `"id"` keys.
3. Register the new loader with the service:
   `await eval_service.register_dataset_loader("my_custom_source_type", MyCustomDatasetLoader)`

### 5.2. Custom Metric Handlers

To support new metrics or metric libraries:
1. Create a class that inherits from `BaseMetricHandler`.
2. Implement the `async def compute(self, predictions: List[str], references: Optional[List[str]] = None, inputs: Optional[List[str]] = None) -> Dict[str, Any]` method. This method should return a dictionary of metric scores.
3. Register the new handler with the service:
   `await eval_service.register_metric_handler("my_custom_library", MyCustomMetricHandler)`

## 6. Error Handling

The service incorporates error handling at various stages:
- **Configuration Validation:** `InvalidJobConfigError` is raised for invalid job configurations during submission.
- **Resource Issues:** `ModelNotFoundError` (from `LLMModelManager`) or `ResourceNotFoundError` can occur if models or other resources are not found.
- **Execution Errors:** `JobExecutionError` is raised for errors during dataset loading, inference, or metric computation. These errors are logged in the job's status and report.
- **Cancellation:** Jobs can be cancelled. The cancellation status is reflected in the job status.

Detailed error messages are stored in `EvaluationJobStatusInfo.error_message` and `EvaluationReport.errors`.

## 7. Logging

The service uses the standard Python `logging` module. Configure the logger as needed to control log levels and output for `LLMEvaluationService` and related components.

## 8. Example Workflow (Conceptual)

1. Initialize `LLMModelManager`, `LLMInferenceService`, and `LLMEvaluationService`.
2. Define an `EvaluationJobConfig` detailing the models, datasets (e.g., a Hugging Face dataset like `'glue', 'mrpc'`), and metrics (e.g., `accuracy`, `f1` from `evaluate`).
3. Submit the job: `status_info = await eval_service.submit_evaluation_job(job_config)`.
4. Periodically check status: `current_status = await eval_service.get_evaluation_job_status(status_info.job_id)`.
5. Once `current_status.status` is `"completed"` or `"failed"`, retrieve the report: `report = await eval_service.get_evaluation_report(status_info.job_id)`.
6. Analyze the `report.results_per_model_dataset` and `report.errors`.
7. Optionally, `await eval_service.shutdown()` when done.

This guide provides a comprehensive overview of the `LLMEvaluationService`. Refer to the source code for specific implementation details and Pydantic model definitions.
