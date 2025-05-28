"""
Core implementation of the LLM Evaluation Service.

This service manages the lifecycle of LLM evaluation jobs, including submission,
validation, orchestration, execution, monitoring, and reporting.
"""

import asyncio
import logging
import uuid
import os
import shutil # For test cleanup
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Union, Literal, AsyncGenerator, Type
from abc import ABC, abstractmethod

from pydantic import BaseModel, Field, validator

# Attempt to import from LLMModelManager and Core AI Exceptions
try:
    from .llm_model_manager import LLMModelManager, LoadedModel, ModelNotFoundError
    from .llm_inference_service import LLMInferenceService, InferenceRequest, InferenceResponse # For getting predictions
    from ..core_ai_exceptions import ServiceConfigurationError, JobExecutionError, InvalidJobConfigError, ResourceNotFoundError
except ImportError:
    logging.warning("LLMEvaluationService: Could not import from .llm_model_manager, .llm_inference_service or ..core_ai_exceptions. Using placeholders.")
    class LLMModelManager:
        async def get_model_instance(self, model_id: str, for_training: bool = False) -> Any:
            logging.info(f"Placeholder LLMModelManager: Requesting model {model_id}")
            if model_id == "non_existent_model":
                raise ModelNotFoundError(f"Model {model_id} not found.")
            # Simulate returning a mock model object
            class MockModel:
                def __init__(self, path):
                    self.name_or_path = path
                    self.config = type("config", (), {"model_type": "mock"})()
            return {"model": MockModel(f"/tmp/mock_models/{model_id}"), "tokenizer": None, "config": {}}

    class LLMInferenceService:
        def __init__(self, model_manager):
            self.model_manager = model_manager
            self.simulate_inference_failure = False # New flag for testing
            self.simulate_critical_failure = False # New flag

        async def process_inference_request(self, request: "InferenceRequest") -> "InferenceResponse":
            logging.info(f"Placeholder LLMInferenceService: Processing request for {request.model_id}")
            if self.simulate_critical_failure:
                raise JobExecutionError("Simulated critical inference failure.")
            if self.simulate_inference_failure:
                return InferenceResponse(request_id=request.request_id, model_id=request.model_id, generated_text=None, error_message="Simulated inference error", completed_at=datetime.now(timezone.utc))
            
            # Simulate predictions
            if request.prompt == "What is the capital of France?":
                 return InferenceResponse(request_id=request.request_id, model_id=request.model_id, generated_text="Paris", error_message=None, completed_at=datetime.now(timezone.utc))
            return InferenceResponse(request_id=request.request_id, model_id=request.model_id, generated_text="mock prediction", error_message=None, completed_at=datetime.now(timezone.utc))

    class InferenceRequest(BaseModel):
        model_id: str
        prompt: str
        request_id: Optional[str] = None
        generation_params: Optional[Dict[str, Any]] = None
        stream: bool = False

    class InferenceResponse(BaseModel):
        request_id: str
        model_id: str
        generated_text: Optional[str] = None
        error_message: Optional[str] = None
        completed_at: datetime

    class LoadedModel: pass
    class ModelNotFoundError(Exception): pass
    class ServiceConfigurationError(Exception): pass
    class JobExecutionError(Exception): pass
    class InvalidJobConfigError(Exception): pass
    class ResourceNotFoundError(Exception): pass

logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# --- Data Models (Pydantic) ---

class ModelTargetConfig(BaseModel):
    model_id: str = Field(description="Identifier of the model from LLMModelManager.")
    version: Optional[str] = Field(None, description="Specific version of the model, if applicable.")
    # path: Optional[str] = Field(None, description="Direct path to model if not managed by LLMModelManager") # Consider if needed

class MetricConfig(BaseModel):
    metric_name: str = Field(description="Name of the metric to compute (e.g., \"accuracy\", \"rougeL\").")
    params: Optional[Dict[str, Any]] = Field(None, description="Parameters for the metric computation.")
    output_key: Optional[str] = Field(None, description="If the metric function returns a dict, specify the key for the desired value.")
    library: Literal["evaluate", "lm-evaluation-harness", "custom"] = Field("evaluate", description="Library or source of the metric.")

class EvaluationDatasetConfig(BaseModel):
    dataset_id: str = Field(description="Unique identifier for this dataset configuration within the job.")
    source_type: Literal["hf_dataset", "local_path", "data_layer_id"] = Field(description="Type of the dataset source.")
    path_or_id: str = Field(description="Path to file/directory, Data Layer ID, or Hugging Face dataset name.")
    split: Optional[str] = Field("test", description="Dataset split to use (e.g., \"train\", \"validation\", \"test\").")
    input_column_names: List[str] = Field(["text"], description="Name(s) of the column(s) containing input text/prompts.")
    target_column_name: Optional[str] = Field(None, description="Name of the column containing target/reference text.")
    task_type: Optional[Literal["text-generation", "summarization", "question-answering", "classification"]] = Field(None, description="Type of task, helps guide preprocessing and metric selection.")
    preprocessing_params: Optional[Dict[str, Any]] = Field(None, description="Parameters for dataset preprocessing.")

class EvaluationJobConfig(BaseModel):
    job_name: Optional[str] = Field(None, description="User-friendly name for the evaluation job.")
    model_targets: List[ModelTargetConfig] = Field(description="List of models to evaluate.")
    datasets: List[EvaluationDatasetConfig] = Field(description="List of dataset configurations to evaluate against.")
    metrics: List[MetricConfig] = Field(description="List of metrics to compute.")
    evaluation_parameters: Optional[Dict[str, Any]] = Field(None, description="Global parameters for the evaluation process (e.g., batch_size, device).")
    # output_options: Optional[Dict[str, Any]] = Field(None, description="Options for report generation or storage.")

class EvaluationJobStatusInfo(BaseModel):
    job_id: str = Field(description="Unique identifier for the evaluation job.")
    job_name: Optional[str] = Field(None)
    status: Literal["queued", "preprocessing", "running_inference", "computing_metrics", "generating_report", "completed", "failed", "cancelled"] = Field("queued")
    progress_percentage: Optional[float] = Field(None, ge=0, le=100)
    current_model_id: Optional[str] = None
    current_dataset_id: Optional[str] = None
    current_metric_name: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MetricResult(BaseModel):
    metric_name: str
    metric_library: str
    value: Any
    params: Optional[Dict[str, Any]] = None
    dataset_id: str
    model_id: str
    model_version: Optional[str] = None

class EvaluationReport(BaseModel):
    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_id: str
    job_config: EvaluationJobConfig
    status_info: EvaluationJobStatusInfo # Final status at time of report generation
    results_per_model_dataset: Dict[str, Dict[str, List[MetricResult]]] = Field(description="Results nested by model_id then dataset_id")
    # comparison_summary: Optional[Dict] = None # For future multi-model comparison summaries
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    errors: List[str] = Field(default_factory=list)

# --- Abstract Base Classes for Extensibility ---

class BaseDatasetLoader(ABC):
    def __init__(self, dataset_config: EvaluationDatasetConfig, job_config: EvaluationJobConfig):
        self.dataset_config = dataset_config
        self.job_config = job_config
        logger.info(f"BaseDatasetLoader initialized for dataset {dataset_config.dataset_id}")

    @abstractmethod
    async def load_and_preprocess_data(self) -> Any: # Should return an iterable of processed samples
        """Loads, preprocesses, and yields data samples."""
        pass

class BaseMetricHandler(ABC):
    def __init__(self, metric_config: MetricConfig, job_config: EvaluationJobConfig):
        self.metric_config = metric_config
        self.job_config = job_config
        logger.info(f"BaseMetricHandler initialized for metric {metric_config.metric_name}")

    @abstractmethod
    async def compute(self, predictions: List[str], references: Optional[List[str]] = None, inputs: Optional[List[str]] = None) -> Dict[str, Any]:
        """Computes the metric given predictions and optional references/inputs."""
        pass

# --- Placeholder Implementations (to be expanded) ---

class HuggingFaceDatasetLoader(BaseDatasetLoader):
    async def load_and_preprocess_data(self) -> AsyncGenerator[Dict[str, Any], None]:
        try:
            from datasets import load_dataset
            logger.info(f"Loading HF dataset: {self.dataset_config.path_or_id}, split: {self.dataset_config.split}")
            # This is a simplified loader. Real implementation needs error handling, caching, streaming, preprocessing.
            dataset = load_dataset(self.dataset_config.path_or_id, split=self.dataset_config.split, streaming=True)
            input_cols = self.dataset_config.input_column_names
            target_col = self.dataset_config.target_column_name
            
            count = 0
            for example in dataset:
                # Basic preprocessing - construct prompt from multiple input columns if needed
                prompt = " ".join([str(example.get(col, "")) for col in input_cols])
                reference = str(example.get(target_col, "")) if target_col else None
                yield {"id": str(count), "prompt": prompt, "reference": reference, "raw_input": {col: example.get(col) for col in input_cols}}
                count += 1
                if count >= 10: # Limiting for mock testing
                    logger.warning("HuggingFaceDatasetLoader: Limiting to 10 samples for mock testing.")
                    break 
        except ImportError:
            logger.error("HuggingFaceDatasetLoader: `datasets` library not installed. Cannot load HF datasets.")
            raise JobExecutionError("`datasets` library not installed.")
        except Exception as e:
            logger.error(f"HuggingFaceDatasetLoader: Error loading dataset {self.dataset_config.path_or_id}: {e}")
            raise JobExecutionError(f"Error loading dataset {self.dataset_config.path_or_id}: {e}")

class EvaluateMetricHandler(BaseMetricHandler):
    async def compute(self, predictions: List[str], references: Optional[List[str]] = None, inputs: Optional[List[str]] = None) -> Dict[str, Any]:
        try:
            import evaluate
            metric_name = self.metric_config.metric_name
            params = self.metric_config.params or {}
            logger.info(f"Computing metric {metric_name} using HF Evaluate with params: {params}")
            
            metric_fn = evaluate.load(metric_name, **params.get("load_params", {}))
            
            compute_args = {"predictions": predictions}
            if references is not None:
                compute_args["references"] = references
            # Some metrics might need inputs (e.g. for context in QA)
            # This is a simplification; actual mapping of inputs to metric.compute() args is complex.
            if inputs is not None and "inputs" in metric_fn.compute.__code__.co_varnames: # Basic check
                 compute_args["inputs"] = inputs 

            # Handle metrics that require specific arguments or configurations
            if metric_name == "bertscore" and "lang" not in params:
                params["lang"] = "en" # Default lang for bertscore if not specified
            
            # Forcing specific args for some metrics if not provided
            if metric_name in ["rouge", "bleu", "meteor"] and not references:
                logger.warning(f"Metric {metric_name} requires references, but none provided. Returning empty.")
                return {metric_name: "N/A - References required"}

            result = metric_fn.compute(**compute_args, **params.get("compute_params", {}))
            
            if self.metric_config.output_key and isinstance(result, dict):
                return {self.metric_config.output_key: result.get(self.metric_config.output_key)}
            elif isinstance(result, dict):
                return result # Return the whole dict if no specific key or if key not found
            else: # If metric returns a single value not in a dict
                return {metric_name: result}

        except ImportError:
            logger.error("EvaluateMetricHandler: `evaluate` library not installed.")
            raise JobExecutionError("`evaluate` library not installed.")
        except Exception as e:
            logger.error(f"EvaluateMetricHandler: Error computing metric {self.metric_config.metric_name}: {e}")
            # Check if it is a known issue like missing references for certain metrics
            if "references" in str(e).lower() and not references:
                 return {self.metric_config.metric_name: f"Error: {e} (References might be missing)"}
            raise JobExecutionError(f"Error computing metric {self.metric_config.metric_name}: {e}")

# --- EvaluationJob Class (Internal representation of a job) ---

class EvaluationJob:
    def __init__(self, job_id: str, config: EvaluationJobConfig, service_ref: "LLMEvaluationService"):
        self.job_id = job_id
        self.config = config
        self.service_ref = service_ref # Reference to the main service for accessing model_manager etc.
        self.status_info = EvaluationJobStatusInfo(job_id=job_id, job_name=config.job_name)
        self._cancel_requested = False
        self._run_task: Optional[asyncio.Task] = None
        self.results: Dict[str, Dict[str, List[MetricResult]]] = {}
        self.errors: List[str] = []
        logger.info(f"EvaluationJob {job_id} initialized for {config.job_name or 'Unnamed Job'}")

    async def update_status(self, partial_status_update: Dict[str, Any]):
        now = datetime.now(timezone.utc)
        changed = False
        for key, value in partial_status_update.items():
            if hasattr(self.status_info, key) and getattr(self.status_info, key) != value:
                setattr(self.status_info, key, value)
                changed = True
        
        if changed and self.status_info.status in ["running_inference", "computing_metrics"] and not self.status_info.start_time:
            self.status_info.start_time = now
        if self.status_info.status in ["completed", "failed", "cancelled"] and not self.status_info.end_time:
            self.status_info.end_time = now
        # logger.debug(f"Job {self.job_id} status updated: {self.status_info.model_dump_json(indent=2)}")

    async def _execute_evaluation_for_model_dataset(self, model_config: ModelTargetConfig, dataset_loader: BaseDatasetLoader):
        model_id = model_config.model_id
        dataset_id = dataset_loader.dataset_config.dataset_id
        self.results.setdefault(model_id, {}).setdefault(dataset_id, [])

        await self.update_status({"status": "running_inference", "current_model_id": model_id, "current_dataset_id": dataset_id})
        
        predictions = []
        references = []
        inputs = [] # For metrics that might need original inputs
        sample_ids = []

        try:
            # 1. Load Model (via LLMInferenceService which uses LLMModelManager)
            # For simplicity, we assume LLMInferenceService is available and handles model loading.
            # In a real scenario, you might load the model once per model_target.
            # Here, we'll make inference requests per sample.

            # 2. Iterate through dataset and get predictions
            processed_samples_count = 0
            async for sample in dataset_loader.load_and_preprocess_data():
                if self._cancel_requested: raise asyncio.CancelledError("Job cancelled during inference.")
                
                sample_ids.append(sample["id"])
                inputs.append(sample["prompt"])
                if sample["reference"] is not None:
                    references.append(sample["reference"])
                
                # Use LLMInferenceService to get predictions
                inference_req = InferenceRequest(
                    model_id=model_id,
                    prompt=sample["prompt"],
                    # generation_params=self.config.evaluation_parameters.get("generation_params", {})
                )
                try:
                    inference_resp = await self.service_ref.inference_service.process_inference_request(inference_req)
                    if inference_resp.error_message:
                        logger.warning(f"Inference error for model {model_id}, sample {sample['id']}: {inference_resp.error_message}")
                        predictions.append("ERROR_DURING_INFERENCE") # Placeholder for error
                    else:
                        predictions.append(inference_resp.generated_text or "")
                except Exception as e_inf:
                    logger.error(f"Critical inference failure for model {model_id}, sample {sample['id']}: {e_inf}")
                    predictions.append("CRITICAL_INFERENCE_ERROR")
                    self.errors.append(f"Critical inference error for {model_id} on sample {sample['id']}: {e_inf}")
                
                processed_samples_count += 1
                # TODO: Add progress update based on dataset size if known
                await self.update_status({"progress_percentage": (processed_samples_count / 10.0) * 50}) # Mock progress for 10 samples

            if not predictions:
                logger.warning(f"No predictions generated for model {model_id} on dataset {dataset_id}. Skipping metrics.")
                self.errors.append(f"No predictions for {model_id} on {dataset_id}.")
                return

            # 3. Compute Metrics
            await self.update_status({"status": "computing_metrics"})
            for metric_conf in self.config.metrics:
                if self._cancel_requested: raise asyncio.CancelledError("Job cancelled during metric computation.")
                await self.update_status({"current_metric_name": metric_conf.metric_name})
                
                metric_handler_cls = self.service_ref._get_metric_handler_factory(metric_conf.library)
                if not metric_handler_cls:
                    logger.warning(f"No metric handler found for library {metric_conf.library}. Skipping metric {metric_conf.metric_name}.")
                    self.errors.append(f"No handler for {metric_conf.library} (metric: {metric_conf.metric_name})")
                    continue
                
                metric_handler = metric_handler_cls(metric_conf, self.config)
                try:
                    metric_values = await metric_handler.compute(predictions, references if references else None, inputs)
                    for key, value in metric_values.items():
                        self.results[model_id][dataset_id].append(MetricResult(
                            metric_name=key, # Use key from result dict as metric name
                            metric_library=metric_conf.library,
                            value=value,
                            params=metric_conf.params,
                            dataset_id=dataset_id,
                            model_id=model_id,
                            model_version=model_config.version
                        ))
                except Exception as e_metric:
                    logger.error(f"Error computing metric {metric_conf.metric_name} for model {model_id} on dataset {dataset_id}: {e_metric}")
                    self.errors.append(f"Error for metric {metric_conf.metric_name} on {model_id}/{dataset_id}: {e_metric}")
                    self.results[model_id][dataset_id].append(MetricResult(
                        metric_name=metric_conf.metric_name,
                        metric_library=metric_conf.library,
                        value=f"ERROR: {e_metric}", # Store error as value
                        params=metric_conf.params,
                        dataset_id=dataset_id,
                        model_id=model_id,
                        model_version=model_config.version
                    ))
        except asyncio.CancelledError:
            logger.info(f"Evaluation for model {model_id} on dataset {dataset_id} cancelled.")
            await self.update_status({"status": "cancelled"})
            self.errors.append(f"Cancelled during evaluation of {model_id} on {dataset_id}.")
            raise # Re-raise to be caught by the main run method
        except Exception as e:
            logger.error(f"Error during evaluation for model {model_id} on dataset {dataset_id}: {e}")
            await self.update_status({"status": "failed", "error_message": str(e)})
            self.errors.append(f"General error for {model_id} on {dataset_id}: {e}")
            # No re-raise, allow job to complete other model/dataset pairs if possible, or mark as failed globally

    async def run(self):
        logger.info(f"Starting EvaluationJob {self.job_id} for {self.config.job_name or 'Unnamed Job'}")
        await self.update_status({"status": "preprocessing", "start_time": datetime.now(timezone.utc)})
        total_model_dataset_pairs = len(self.config.model_targets) * len(self.config.datasets)
        completed_pairs = 0

        try:
            for model_conf in self.config.model_targets:
                # TODO: Potentially load model once here if LLMInferenceService doesn't cache effectively
                # or if we need direct model access for some evaluation types not going through inference service.
                for dataset_conf in self.config.datasets:
                    if self._cancel_requested: raise asyncio.CancelledError("Job cancelled before processing a model/dataset pair.")
                    
                    dataset_loader_cls = self.service_ref._get_dataset_loader_factory(dataset_conf.source_type)
                    if not dataset_loader_cls:
                        logger.warning(f"No dataset loader for source type {dataset_conf.source_type}. Skipping dataset {dataset_conf.dataset_id}.")
                        self.errors.append(f"No loader for {dataset_conf.source_type} (dataset: {dataset_conf.dataset_id})")
                        continue
                    
                    dataset_loader = dataset_loader_cls(dataset_conf, self.config)
                    await self._execute_evaluation_for_model_dataset(model_conf, dataset_loader)
                    
                    completed_pairs += 1
                    await self.update_status({"progress_percentage": (completed_pairs / total_model_dataset_pairs) * 100 if total_model_dataset_pairs > 0 else 100})

            if self._cancel_requested:
                 await self.update_status({"status": "cancelled", "error_message": "Job cancelled by user."})
            elif self.errors: # If there were non-critical errors but job wasn't cancelled
                final_error_summary = "; ".join(self.errors[:3]) + ("..." if len(self.errors) > 3 else "")
                await self.update_status({"status": "completed_with_errors" if not self.status_info.status == "failed" else self.status_info.status, "error_message": f"Completed with errors: {final_error_summary}"})
            else:
                await self.update_status({"status": "completed"})
        
        except asyncio.CancelledError:
            logger.info(f"EvaluationJob {self.job_id} was cancelled.")
            await self.update_status({"status": "cancelled", "error_message": "Job cancelled by user."})
        except Exception as e:
            logger.error(f"Critical error in EvaluationJob {self.job_id}: {e}", exc_info=True)
            await self.update_status({"status": "failed", "error_message": str(e)})
        finally:
            await self.update_status({"end_time": datetime.now(timezone.utc)})
            logger.info(f"EvaluationJob {self.job_id} finished with status: {self.status_info.status}")
            # Persist report or notify completion
            await self.service_ref._persist_report(self)

    def cancel(self):
        if self.status_info.status not in ["completed", "failed", "cancelled"]:
            self._cancel_requested = True
            if self._run_task and not self._run_task.done():
                self._run_task.cancel()
            logger.info(f"Cancellation requested for EvaluationJob {self.job_id}")
            return True
        return False

# --- Main LLMEvaluationService Class ---

class LLMEvaluationService:
    def __init__(self, model_manager: LLMModelManager, inference_service: LLMInferenceService, global_config: Optional[Dict[str, Any]] = None):
        self.model_manager = model_manager
        self.inference_service = inference_service # Used to get predictions
        self.config = global_config or {}
        self.active_jobs: Dict[str, EvaluationJob] = {}
        self.job_reports: Dict[str, EvaluationReport] = {} # Simple in-memory store for reports
        self._job_tasks: Dict[str, asyncio.Task] = {}
        self._is_running = False
        logger.info(f"LLMEvaluationService initialized with ModelManager: {type(model_manager).__name__} and InferenceService: {type(inference_service).__name__}.")
        self._dataset_loader_factories: Dict[str, Type[BaseDatasetLoader]] = {
            "hf_dataset": HuggingFaceDatasetLoader,
            # "local_pat        self._metric_handler_factories: Dict[str, Type[BaseMetricHandler]] = {
            "evaluate": EvaluateMetricHandler,
            # "lm-evaluation-harness": LMEvalHarnessHandler, # To be implemented
            # "custom": CustomMetricHandler, # Example
        }
        logger.info(f"LLMEvaluationService initialized with ModelManager: {type(model_manager).__name__} and InferenceService: {type(inference_service).__name__}.")

    def _get_dataset_loader_factory(self, source_type: str) -> Optional[Type[BaseDatasetLoader]]:
        return self._dataset_loader_factories.get(source_type)

    def _get_metric_handler_factory(self, library_name: str) -> Optional[Type[BaseMetricHandler]]:
        return self._metric_handler_factories.get(library_name)

    async def register_dataset_loader(self, source_type: str, loader_class: Type[BaseDatasetLoader]):
        if not issubclass(loader_class, BaseDatasetLoader):
            raise TypeError("loader_class must be a subclass of BaseDatasetLoader")
        self._dataset_loader_factories[source_type] = loader_class
        logger.info(f"Registered dataset loader for source type \'{source_type}\' with class {loader_class.__name__}.")

    async def register_metric_handler(self, library_name: str, handler_class: Type[BaseMetricHandler]):
        if not issubclass(handler_class, BaseMetricHandler):
            raise TypeError("handler_class must be a subclass of BaseMetricHandler")
        self._metric_handler_factories[library_name] = handler_class
        logger.info(f"Registered metric handler for library \'{library_name}\' with class {handler_class.__name__}.")

    async def submit_evaluation_job(self, config: EvaluationJobConfig) -> EvaluationJobStatusInfo:
        job_id = str(uuid.uuid4())
        logger.info(f"Submitting new evaluation job {job_id} with name: {config.job_name or 'Unnamed Job'}")
        
        # Basic validation (can be expanded)
        if not config.model_targets:
            raise InvalidJobConfigError("At least one model target must be specified.")
        if not config.datasets:
            raise InvalidJobConfigError("At least one dataset must be specified.")
        if not config.metrics:
            raise InvalidJobConfigError("At least one metric must be specified.")

        job = EvaluationJob(job_id=job_id, config=config, service_ref=self)
        self.active_jobs[job_id] = job
        
        # Run the job in the background
        run_task = asyncio.create_task(job.run())
        job._run_task = run_task # Store task reference in job for cancellation
        self._job_tasks[job_id] = run_task # Store task reference in service for shutdown
        
        logger.info(f"Evaluation job {job_id} submitted and task created.")
        return job.status_info

    async def get_evaluation_job_status(self, job_id: str) -> Optional[EvaluationJobStatusInfo]:
        logger.debug(f"Requesting status for job {job_id}")
        if job_id in self.active_jobs:
            return self.active_jobs[job_id].status_info
        elif job_id in self.job_reports: # Check if job is completed and report exists
            return self.job_reports[job_id].status_info
        logger.warning(f"Job {job_id} not found for status request.")
        return None

    async def list_evaluation_jobs(self, limit: int = 20, offset: int = 0, status_filter: Optional[str] = None) -> List[EvaluationJobStatusInfo]:
        logger.debug(f"Listing evaluation jobs with limit={limit}, offset={offset}, status_filter={status_filter}")
        all_statuses = []
        # Collect statuses from active jobs
        for job in self.active_jobs.values():
            all_statuses.append(job.status_info)
        # Collect statuses from completed jobs (via reports)
        for report in self.job_reports.values():
            # Avoid duplicates if a job is somehow in both (should not happen with proper state management)
            if report.job_id not in self.active_jobs:
                all_statuses.append(report.status_info)
        
        # Sort by creation time, newest first
        all_statuses.sort(key=lambda s: s.created_at, reverse=True)
        
        filtered_statuses = []
        if status_filter:
            for status_info in all_statuses:
                if status_info.status == status_filter:
                    filtered_statuses.append(status_info)
        else:
            filtered_statuses = all_statuses
            
        return filtered_statuses[offset : offset + limit]

    async def get_evaluation_report(self, job_id: str) -> Optional[EvaluationReport]:
        logger.debug(f"Requesting report for job {job_id}")
        report = self.job_reports.get(job_id)
        if not report:
            logger.warning(f"Report for job {job_id} not found.")
        return report

    async def cancel_evaluation_job(self, job_id: str) -> bool:
        logger.info(f"Attempting to cancel job {job_id}")
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            cancelled = job.cancel() # This now also cancels the asyncio task
            if cancelled:
                logger.info(f"Job {job_id} cancellation initiated successfully.")
            else:
                logger.warning(f"Job {job_id} could not be cancelled (already completed or failed).")
            return cancelled
        logger.warning(f"Job {job_id} not found for cancellation.")
        return False

    async def _persist_report(self, job: EvaluationJob):
        # This is a placeholder for actual report persistence (e.g., to a file system or database)
        report = EvaluationReport(
            job_id=job.job_id,
            job_config=job.config,
            status_info=job.status_info,
            results_per_model_dataset=job.results,
            errors=job.errors
        )
        self.job_reports[job.job_id] = report
        logger.info(f"Report for job {job.job_id} persisted (in-memory). Path: N/A for mock.")
        # Once report is persisted, job might be removed from active_jobs if it's truly finished
        if job.job_id in self.active_jobs and job.status_info.status in ["completed", "failed", "cancelled", "completed_with_errors"]:
            logger.debug(f"Removing job {job.job_id} from active_jobs as it is finished.")
            # del self.active_jobs[job.job_id] # Be careful with modifying dict during iteration if run() is not awaited directly
            # It's safer to let the job task complete and then clean up if needed, or manage active_jobs carefully.
            # For now, we keep it in active_jobs but its status reflects completion.
            # The _job_tasks dict will also keep the task reference until it's cleaned up.

    async def start(self):
        if self._is_running:
            logger.warning("LLMEvaluationService is already running.")
            return
        self._is_running = True
        # In a real service, might start background tasks for queue polling if jobs are not run immediately
        logger.info("LLMEvaluationService started.")

    async def stop(self):
        if not self._is_running:
            logger.warning("LLMEvaluationService is not running.")
            return
        self._is_running = False
        logger.info("LLMEvaluationService stopping... Attempting to cancel active jobs.")
        active_job_ids = list(self._job_tasks.keys())
        for job_id in active_job_ids:
            if job_id in self.active_jobs:
                self.active_jobs[job_id].cancel()
        
        # Wait for tasks to complete or be cancelled
        await asyncio.gather(*[task for task in self._job_tasks.values() if task and not task.done()], return_exceptions=True)
        logger.info("LLMEvaluationService stopped. All active job tasks processed.")

# --- Example Usage (for testing/demonstration) ---
async def main_test():
    logger.info("--- Starting LLMEvaluationService Test Suite ---")
    # Mock dependencies
    mock_model_manager = LLMModelManager()
    mock_inference_service = LLMInferenceService(model_manager=mock_model_manager)
    
    eval_service = LLMEvaluationService(model_manager=mock_model_manager, inference_service=mock_inference_service)
    await eval_service.start()

    test_results = {"passed": 0, "failed": 0}
    def print_test_result(name, success, details=""):
        status = "PASSED" if success else "FAILED"
        logger.info(f"TEST {status}: {name} {details}")
        if success: test_results["passed"] += 1
        else: test_results["failed"] += 1

    # --- Test Case 1: Basic Evaluation Job ---
    logger.info("--- Test Case 1: Basic Evaluation Job ---")
    job_config_1 = EvaluationJobConfig(
        job_name="Test Eval Job 1",
        model_targets=[ModelTargetConfig(model_id="gpt2-medium")],
        datasets=[
            EvaluationDatasetConfig(
                dataset_id="wikitext_sample",
                source_type="hf_dataset",
                path_or_id="wikitext",
                split="test", # Using test split of wikitext-2-raw-v1
                input_column_names=["text"],
                task_type="text-generation",
                preprocessing_params={"dataset_config_name": "wikitext-2-raw-v1"} # Specific to wikitext
            )
        ],
        metrics=[
            MetricConfig(metric_name="rouge", params={"rouge_types": ["rougeL"]}),
            MetricConfig(metric_name="bleu") # Will likely fail/warn without references for text-gen
        ],
        evaluation_parameters={"batch_size": 1}
    )
    try:
        status_info_1 = await eval_service.submit_evaluation_job(job_config_1)
        print_test_result("Job Submission (Test 1)", status_info_1.status == "queued")
        
        # Monitor job completion (simplified polling)
        for _ in range(20): # Max 10 seconds wait for this simple test
            await asyncio.sleep(0.5)
            current_status = await eval_service.get_evaluation_job_status(status_info_1.job_id)
            if current_status and current_status.status in ["completed", "failed", "completed_with_errors"]:
                logger.info(f"Job 1 final status: {current_status.status}, Error: {current_status.error_message}")
                print_test_result("Job Completion (Test 1)", current_status.status == "completed" or current_status.status == "completed_with_errors")
                report = await eval_service.get_evaluation_report(status_info_1.job_id)
                if report:
                    print_test_result("Report Generation (Test 1)", True)
                    logger.info(f"Report (Test 1) content: {report.model_dump_json(indent=2)}")
                    # Check if ROUGE-L is present (actual value depends on mock predictions)
                    has_rouge = any("rougeL" in res.metric_name for m_res_list in report.results_per_model_dataset.values() for d_res_list in m_res_list.values() for res in d_res_list)
                    print_test_result("ROUGE Metric in Report (Test 1)", has_rouge)
                else:
                    print_test_result("Report Generation (Test 1)", False, "Report not found")
                break
        else:
            print_test_result("Job Completion (Test 1)", False, "Job did not complete in time")

    except Exception as e:
        print_test_result("Test Case 1 Execution", False, f"Error: {e}")

    # --- Test Case 2: Model Not Found ---
    logger.info("--- Test Case 2: Model Not Found ---")
    job_config_2 = EvaluationJobConfig(
        job_name="Test Model Not Found",
        model_targets=[ModelTargetConfig(model_id="non_existent_model")],
        datasets=[job_config_1.datasets[0]], # Reuse dataset config
        metrics=[MetricConfig(metric_name="accuracy")] # Placeholder metric
    )
    try:
        status_info_2 = await eval_service.submit_evaluation_job(job_config_2)
        print_test_result("Job Submission (Test 2)", status_info_2.status == "queued")
        for _ in range(10):
            await asyncio.sleep(0.5)
            current_status_2 = await eval_service.get_evaluation_job_status(status_info_2.job_id)
            if current_status_2 and current_status_2.status == "failed":
                print_test_result("Job Failure (Model Not Found - Test 2)", True, f"Error: {current_status_2.error_message}")
                assert "not found" in (current_status_2.error_message or "").lower()
                break
        else:
            print_test_result("Job Failure (Model Not Found - Test 2)", False, "Job did not fail as expected or in time")
    except Exception as e:
        print_test_result("Test Case 2 Execution", False, f"Error: {e}")

    # --- Test Case 3: Job Cancellation (if implemented and testable simply) ---
    # This is harder to test reliably in a short script without more sophisticated job control
    # For now, we assume cancellation is tested via unit tests on EvaluationJob directly.

    # --- Test Case 4: List Jobs ---
    logger.info("--- Test Case 4: List Jobs ---")
    jobs_list = await eval_service.list_evaluation_jobs()
    print_test_result("List Jobs", len(jobs_list) >= 2, f"Found {len(jobs_list)} jobs")
    if jobs_list:
        logger.info(f"First job in list: {jobs_list[0].job_id}, Status: {jobs_list[0].status}")

    await eval_service.stop()
    logger.info("--- LLMEvaluationService Test Suite Finished ---")
    logger.info(f"SUMMARY: Passed: {test_results['passed']}, Failed: {test_results['failed']}")

if __name__ == "__main__":
    asyncio.run(main_test())

