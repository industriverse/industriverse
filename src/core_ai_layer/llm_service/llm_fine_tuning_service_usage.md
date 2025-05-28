# LLMFineTuningService Usage Guide

## 1. Introduction

The `LLMFineTuningService` is a core component of the Industriverse Core AI Layer, responsible for managing and executing fine-tuning jobs for Large Language Models (LLMs). It allows users to adapt pre-trained models to specific tasks or datasets, enhancing their performance and tailoring them to particular business needs. This service integrates with the `LLMModelManager` for accessing base models and storing the newly fine-tuned model versions.

This document provides a comprehensive guide on how to use the `LLMFineTuningService`, including its capabilities, configuration options, and examples of how to submit and monitor fine-tuning jobs.

## 2. Core Concepts

Before diving into usage, it's important to understand a few core concepts:

*   **Fine-Tuning Job (`FineTuningJobConfig`):** This is the primary configuration object submitted to the service. It defines all aspects of a fine-tuning task, including the base model, the new model ID, dataset details, the fine-tuning technique (e.g., full fine-tune, LoRA, QLoRA), hyperparameters, and evaluation settings.
*   **Dataset Configuration (`DatasetSourceConfig`):** Specifies where and how to load the dataset for fine-tuning. It supports various sources like local file paths, Hugging Face datasets, or potentially a Data Layer ID in a fully integrated Industriverse environment.
*   **Fine-Tuning Technique (`FineTuningTechniqueConfig`):** Defines the method used for fine-tuning (e.g., `full`, `lora`, `qlora`, `instructlab`) and its specific parameters.
*   **Hyperparameters (`TrainingHyperparameters`):** A detailed set of parameters controlling the training process, such as learning rate, number of epochs, batch size, optimizer, etc. These are largely based on Hugging Face Trainer arguments.
*   **Job Status (`FineTuningJobStatusInfo`):** An object that provides real-time information about a submitted job, including its current status (e.g., `queued`, `preprocessing`, `running`, `completed`, `failed`, `cancelled`), progress, metrics, and any error messages.
*   **Model Manager (`LLMModelManager`):** The service relies on the `LLMModelManager` to fetch base models for fine-tuning and to register/store the resulting fine-tuned models.

## 3. Service Initialization

The `LLMFineTuningService` is initialized with an instance of the `LLMModelManager` and an optional global configuration dictionary.

```python
# Assuming llm_model_manager is an initialized instance of LLMModelManager
# from llm_model_manager import LLMModelManager # (or your actual import path)

# from llm_fine_tuning_service import LLMFineTuningService # (or your actual import path)

# mock_model_manager = LLMModelManager() # Replace with actual manager
# service_config = {
# "max_concurrent_fine_tuning_jobs": 2, # Default is 1
# "job_queue_poll_interval_seconds": 5 # Default is 5
# }
# fine_tuning_service = LLMFineTuningService(model_manager=mock_model_manager, global_config=service_config)

# Start the background job processor
# await fine_tuning_service.start()
```

Key global configuration options:
*   `max_concurrent_fine_tuning_jobs`: The maximum number of fine-tuning jobs that can run simultaneously. Default is 1.
*   `job_queue_poll_interval_seconds`: How often the service checks the queue for new jobs. Default is 5 seconds.

## 4. Submitting a Fine-Tuning Job

To submit a fine-tuning job, you need to create a `FineTuningJobConfig` object and pass it to the `submit_fine_tuning_job` method.

### 4.1. Defining Dataset Configuration (`DatasetSourceConfig`)

```python
# from llm_fine_tuning_service import DatasetSourceConfig

dataset_config = DatasetSourceConfig(
    source_type="hf_dataset",  # Can be "file_path", "data_layer_id", "hf_dataset"
    path_or_id="wikitext",    # E.g., "glue", "squad", or path like "/data/my_dataset.jsonl"
    format="arrow",           # Optional if not file_path, e.g., "jsonl", "csv"
    train_split_name="train",
    validation_split_name="test", # Optional
    # For text-generation on wikitext, specify the text column and dataset config name
    task_format_details={"dataset_config_name": "wikitext-2-raw-v1", "text_column": "text"}
    # For other tasks, you might specify prompt_column and completion_column
    # prompt_column="question",
    # completion_column="answer"
)
```

### 4.2. Defining Fine-Tuning Technique (`FineTuningTechniqueConfig`)

Choose a method and provide its parameters. Examples:

**LoRA:**
```python
# from llm_fine_tuning_service import FineTuningTechniqueConfig, LoRAParams

lora_technique = FineTuningTechniqueConfig(
    method="lora",
    params=LoRAParams(r=8, lora_alpha=16, lora_dropout=0.1, target_modules=["q_proj", "v_proj"])
)
```

**Full Fine-Tune:**
```python
# from llm_fine_tuning_service import FineTuningTechniqueConfig, FullFineTuneParams

full_tune_technique = FineTuningTechniqueConfig(
    method="full",
    params=FullFineTuneParams() # No specific params for basic full fine-tune via this model
)
```

**QLoRA:**
```python
# from llm_fine_tuning_service import FineTuningTechniqueConfig, QLoRAParams

qlora_technique = FineTuningTechniqueConfig(
    method="qlora",
    params=QLoRAParams(r=8, lora_alpha=16, bits=4, quant_type="nf4")
)
```

### 4.3. Defining Training Hyperparameters (`TrainingHyperparameters`)

```python
# from llm_fine_tuning_service import TrainingHyperparameters

hyperparams = TrainingHyperparameters(
    output_dir_base="/tmp/my_finetuning_runs", # Base directory for outputs
    num_train_epochs=1.0, # Short epoch for example
    learning_rate=2e-5,
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    gradient_accumulation_steps=2,
    weight_decay=0.01,
    lr_scheduler_type="cosine",
    warmup_ratio=0.1,
    logging_steps=10,
    save_steps=50, # Save checkpoints every 50 steps
    save_strategy="steps",
    evaluation_strategy="steps", # Evaluate every `eval_steps`
    eval_steps=50,
    fp16=True, # If your hardware supports it
    max_seq_length=512 # Important for managing memory and context
)
```

### 4.4. Defining Evaluation Configuration (`EvaluationConfig`)

```python
# from llm_fine_tuning_service import EvaluationConfig

eval_config = EvaluationConfig(
    metrics=["loss", "perplexity"] # Specify metrics for evaluation
)
```

### 4.5. Assembling the Job Configuration (`FineTuningJobConfig`)

```python
# from llm_fine_tuning_service import FineTuningJobConfig

job_config = FineTuningJobConfig(
    job_name="My First LoRA Fine-Tune",
    base_model_id="gpt2", # Model ID from LLMModelManager
    new_model_id="gpt2-lora-wikitext-custom", # Desired ID for the new model
    task_type="text-generation", # Optional, helps guide data processing
    dataset_config=dataset_config,
    fine_tuning_technique=lora_technique,
    hyperparameters=hyperparams,
    evaluation_config=eval_config # Optional
)
```

### 4.6. Submitting the Job

```python
# try:
#     submitted_job_status = await fine_tuning_service.submit_fine_tuning_job(job_config)
#     print(f"Job submitted successfully! Job ID: {submitted_job_status.job_id}, Status: {submitted_job_status.status}")
# except InvalidJobConfigError as e:
#     print(f"Error submitting job: Invalid configuration - {e}")
# except Exception as e:
#     print(f"An unexpected error occurred during job submission: {e}")
```

The `submit_fine_tuning_job` method returns a `FineTuningJobStatusInfo` object for the newly queued job.

## 5. Monitoring Job Status

You can monitor the status of a job using its `job_id`.

### 5.1. Get Job Status

```python
# job_id_to_check = submitted_job_status.job_id
# current_status_info = await fine_tuning_service.get_job_status(job_id_to_check)

# if current_status_info:
#     print(f"Job ID: {current_status_info.job_id}")
#     print(f"  Name: {current_status_info.job_name}")
#     print(f"  Status: {current_status_info.status}")
#     print(f"  Progress: {current_status_info.progress_percentage}%" if current_status_info.progress_percentage is not None else "  Progress: N/A")
#     print(f"  Current Step: {current_status_info.current_step}")
#     print(f"  Metrics: {current_status_info.metrics}")
#     print(f"  Error: {current_status_info.error_message}" if current_status_info.error_message else "  Error: None")
#     print(f"  Created At: {current_status_info.created_at}")
#     print(f"  Started At: {current_status_info.started_at}")
#     print(f"  Completed At: {current_status_info.completed_at}")
#     print(f"  Fine-tuned Model ID: {current_status_info.fine_tuned_model_id}")
#     print(f"  Output Path: {current_status_info.output_model_path}")
# else:
#     print(f"Job with ID {job_id_to_check} not found.")
```

You would typically poll this method periodically to get updates.

### 5.2. List Fine-Tuning Jobs

You can list existing jobs with optional filtering and pagination.

```python
# all_jobs = await fine_tuning_service.list_fine_tuning_jobs(limit=10, offset=0)
# print(f"Found {len(all_jobs)} jobs:")
# for job_info in all_jobs:
#     print(f"  - Job ID: {job_info.job_id}, Name: {job_info.job_name}, Status: {job_info.status}")

# Filter by status:
# completed_jobs = await fine_tuning_service.list_fine_tuning_jobs(status_filter="completed")
# print(f"\nFound {len(completed_jobs)} completed jobs:")
# for job_info in completed_jobs:
#     print(f"  - Job ID: {job_info.job_id}, Name: {job_info.job_name}")
```

## 6. Cancelling a Fine-Tuning Job

You can request to cancel a job that is `queued`, `preprocessing`, or `running`.

```python
# job_to_cancel_id = submitted_job_status.job_id # Assuming this job is still active
# was_cancel_requested = await fine_tuning_service.cancel_fine_tuning_job(job_to_cancel_id)

# if was_cancel_requested:
#     print(f"Cancellation request for job {job_to_cancel_id} processed. Monitor status for confirmation.")
#     # Poll get_job_status to see it transition to "cancelled"
# else:
#     print(f"Could not request cancellation for job {job_to_cancel_id} (it might be completed, failed, or already cancelled).")
```
The job will attempt to stop gracefully. Its status will eventually update to `cancelled`.

## 7. Error Handling

The service handles various errors:
*   **Invalid Job Configuration (`InvalidJobConfigError`):** Raised during submission if the `FineTuningJobConfig` is invalid (e.g., missing required fields).
*   **Model Not Found (`ModelNotFoundError`):** If the specified `base_model_id` cannot be found by the `LLMModelManager`.
*   **Job Execution Errors (`JobExecutionError`):** General errors during the data preparation, training, or evaluation phases. The `error_message` field in `FineTuningJobStatusInfo` will contain details.
*   **Cancellation:** If a job is cancelled, its status becomes `cancelled`, and `error_message` might indicate the point of cancellation.

Always check the `status` and `error_message` fields in `FineTuningJobStatusInfo`.

## 8. Output and Artifacts

Upon successful completion:
*   The `status` will be `completed`.
*   `fine_tuned_model_id` will contain the ID under which the new model is registered in `LLMModelManager`.
*   `output_model_path` will point to the directory where the fine-tuned model artifacts (model weights, tokenizer, config files) are stored. This path is typically within the `output_dir_base` specified in `TrainingHyperparameters`.
*   `metrics` will contain the final training and evaluation metrics.

The `LLMModelManager` is responsible for the actual storage and management of these artifacts based on the `output_model_path`.

## 9. Stopping the Service

When your application is shutting down, you should stop the `LLMFineTuningService` to allow graceful termination of its background tasks and any active jobs.

```python
# await fine_tuning_service.stop()
# print("Fine-tuning service stopped.")
```

## 10. Extensibility (For Developers)

The service is designed with extensibility in mind:
*   **`BaseDatasetHandler`:** Abstract base class for implementing custom data loading and preprocessing logic for different dataset sources or formats.
*   **`BaseTrainer`:** Abstract base class for implementing different training loops or integrating with various training libraries (beyond the placeholder/mock Hugging Face Trainer logic).

The service uses factory methods (`_get_dataset_handler_factory`, `_get_trainer_factory`) to select the appropriate handler and trainer based on the job configuration. Developers can extend these factories to register new implementations.

## 11. Example Test Scenarios (from `if __name__ == "__main__":`)

The `llm_fine_tuning_service.py` file includes a comprehensive test suite within its `if __name__ == "__main__":` block. This suite demonstrates:
*   Submitting a valid job and monitoring it to completion.
*   Submitting a job with a non-existent base model (expected to fail).
*   Submitting a job and then cancelling it.
*   Simulating a failure during dataset preparation.
*   Simulating a failure during the training phase.
*   Listing jobs.
*   Attempting to submit a job with an invalid configuration.

Reviewing this test code is highly recommended for practical examples of configuring and interacting with the service.

This concludes the usage guide for the `LLMFineTuningService`. Ensure all paths, model IDs, and configurations are adapted to your specific environment and requirements.
