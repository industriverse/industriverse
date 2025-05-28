"""
Core implementation of the LLM Fine-Tuning Service.

This service manages the lifecycle of LLM fine-tuning jobs, including submission,
validation, orchestration, execution, monitoring, and model registration.
"""

import asyncio
import logging
import uuid
import os
import shutil # For test cleanup
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Union, Literal, AsyncGenerator
from abc import ABC, abstractmethod

from pydantic import BaseModel, Field, validator

# Attempt to import from LLMModelManager and Core AI Exceptions
# These would be actual dependencies in the integrated Industriverse environment.
try:
    from .llm_model_manager import LLMModelManager, LoadedModel, ModelNotFoundError, ConfigurationError as ModelManagerConfigurationError
    from ..core_ai_exceptions import ServiceConfigurationError, JobExecutionError, InvalidJobConfigError, ResourceNotFoundError
except ImportError:
    logging.warning("LLMFineTuningService: Could not import from .llm_model_manager or ..core_ai_exceptions. Using placeholders.")
    # Placeholder classes if imports fail (e.g., during standalone development)
    class LLMModelManager:
        async def get_model_instance(self, model_id: str, for_training: bool = False) -> Any:
            logging.info(f"Placeholder LLMModelManager: Requesting model {model_id}")
            if model_id == "non_existent_base_model":
                raise ModelNotFoundError(f"Base model {model_id} not found.")
            # Simulate returning a mock model object and tokenizer path
            class MockTokenizer:
                def __init__(self, path):
                    self.name_or_path = path
                def save_pretrained(self, path):
                    logging.info(f"MockTokenizer: Saving to {path}")
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                    with open(path, "w") as f: f.write("mock tokenizer content")
                    pass
            class MockModel:
                def __init__(self, path):
                    self.name_or_path = path
                    self.config = type("config", (), {"model_type": "mock"})()
                def save_pretrained(self, path):
                    logging.info(f"MockModel: Saving to {path}")
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                    with open(path, "w") as f: f.write("mock model content")
                    pass
            # Ensure paths are somewhat realistic for os.path.join later
            mock_model_path = os.path.join("/tmp/mock_models", model_id, "model")
            mock_tokenizer_path = os.path.join("/tmp/mock_models", model_id, "tokenizer")
            return {"model": MockModel(mock_model_path), "tokenizer": MockTokenizer(mock_tokenizer_path), "config": {}}

        async def save_fine_tuned_model(
            self, 
            base_model_id: str,
            new_model_id: str, 
            model_path: str, 
            tokenizer_path: str, # Assuming tokenizer is also saved at model_path for simplicity in mock
            fine_tuning_config: Dict[str, Any],
            metrics: Optional[Dict[str, Any]] = None
        ) -> bool:
            logging.info(f"Placeholder LLMModelManager: Saving fine-tuned model {new_model_id} from {model_path}")
            # In a real scenario, this would copy/register the model artifacts
            # For mock, we just confirm it was called.
            return True

    class LoadedModel: pass
    class ModelNotFoundError(Exception): pass
    class ModelManagerConfigurationError(Exception): pass
    class ServiceConfigurationError(Exception): pass
    class JobExecutionError(Exception): pass
    class InvalidJobConfigError(Exception): pass
    class ResourceNotFoundError(Exception): pass

logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# --- Data Structures (Pydantic Models) ---

class DatasetSourceConfig(BaseModel):
    source_type: Literal["file_path", "data_layer_id", "hf_dataset"] = Field(description="Type of the dataset source.")
    path_or_id: str = Field(description="Path to file/directory, Data Layer ID, or Hugging Face dataset name.")
    format: Optional[Literal["jsonl", "csv", "parquet", "text", "arrow"]] = Field(None, description="Format of the dataset if source_type is file_path.")
    train_split_name: str = Field("train", description="Name of the training split (e.g., \"train\", \"train_sft\").")
    validation_split_name: Optional[str] = Field(None, description="Name of the validation split.")
    test_split_name: Optional[str] = Field(None, description="Name of the test split.")
    prompt_column: Optional[str] = Field("prompt", description="Name of the column containing prompts/inputs.")
    completion_column: Optional[str] = Field("completion", description="Name of the column containing completions/outputs.")
    task_format_details: Optional[Dict[str, Any]] = Field(None, description="Additional details for task-specific data formatting.")

class BaseTechniqueParams(BaseModel):
    pass

class FullFineTuneParams(BaseTechniqueParams):
    pass

class LoRAParams(BaseTechniqueParams):
    r: int = Field(8, description="LoRA rank.")
    lora_alpha: int = Field(16, description="LoRA alpha scaling factor.")
    lora_dropout: float = Field(0.05, description="LoRA dropout rate.")
    target_modules: Optional[List[str]] = Field(None, description="Modules to apply LoRA to (e.g., [\"q_proj\", \"v_proj\"]).")
    bias: Literal["none", "all", "lora_only"] = Field("none", description="Bias training configuration for LoRA.")

class QLoRAParams(LoRAParams):
    bits: Literal[4, 8] = Field(4, description="Quantization bits (4 or 8).")
    quant_type: str = Field("nf4", description="Quantization type (e.g., \"nf4\", \"fp4\").")
    double_quant: bool = Field(True, description="Whether to use double quantization.")

class InstructLabParams(BaseTechniqueParams):
    taxonomy_path: str = Field(description="Path to the InstructLab taxonomy file.")
    teacher_model_id: Optional[str] = Field(None, description="Model ID for the teacher model if applicable.")
    num_synthetic_examples: int = Field(1000, description="Number of synthetic examples to generate.")

class FineTuningTechniqueConfig(BaseModel):
    method: Literal["full", "lora", "qlora", "instructlab"] = Field(description="Fine-tuning method to use.")
    params: Union[FullFineTuneParams, LoRAParams, QLoRAParams, InstructLabParams, None] = Field(None, description="Parameters specific to the chosen fine-tuning method.")

    @validator("params", pre=True, always=True)
    def check_params_for_method(cls, v, values):
        method = values.get("method")
        if method == "full" and (v is None or isinstance(v, FullFineTuneParams)):
            return v or FullFineTuneParams()
        if method == "lora" and (v is None or isinstance(v, LoRAParams)):
            return v or LoRAParams()
        if method == "qlora" and (v is None or isinstance(v, QLoRAParams)):
            return v or QLoRAParams()
        if method == "instructlab" and (v is None or isinstance(v, InstructLabParams)):
            if v is None: raise ValueError("InstructLabParams are required for instructlab method")
            return v
        return v

class TrainingHyperparameters(BaseModel):
    output_dir_base: str = Field("/tmp/fine_tuning_runs", description="Base directory for fine-tuning outputs.")
    num_train_epochs: float = Field(3.0, description="Total number of training epochs to perform.")
    learning_rate: float = Field(5e-5, description="Initial learning rate.")
    per_device_train_batch_size: int = Field(4, description="Batch size per GPU/TPU core/CPU for training.")
    per_device_eval_batch_size: int = Field(4, description="Batch size per GPU/TPU core/CPU for evaluation.")
    gradient_accumulation_steps: int = Field(1, description="Number of updates steps to accumulate before performing a backward/update pass.")
    weight_decay: float = Field(0.01, description="Weight decay to apply.")
    lr_scheduler_type: str = Field("linear", description="Learning rate scheduler type (e.g., linear, cosine).")
    warmup_ratio: float = Field(0.0, description="Ratio of total training steps used for a linear warmup from 0 to learning_rate.")
    warmup_steps: int = Field(0, description="Number of steps for a linear warmup from 0 to learning_rate. Overrides warmup_ratio.")
    optimizer_name: str = Field("adamw_torch", description="Optimizer to use (e.g., adamw_hf, adamw_torch, adafactor).")
    seed: int = Field(42, description="Random seed for initialization.")
    max_steps: Optional[int] = Field(-1, description="If > 0, total number of training steps to perform. Overrides num_train_epochs.")
    logging_steps: int = Field(10, description="Log every X updates steps.")
    save_steps: Optional[int] = Field(500, description="Save checkpoint every X updates steps. If None, uses save_strategy=\"epoch\".")
    save_total_limit: Optional[int] = Field(2, description="Limit the total amount of checkpoints. Deletes the older checkpoints.")
    save_strategy: Literal["no", "epoch", "steps"] = Field("steps", description="The checkpoint save strategy to adopt.")
    eval_steps: Optional[int] = Field(None, description="Run an evaluation every X steps. If None and evaluation_strategy is \"steps\", will use same as logging_steps.")
    evaluation_strategy: Literal["no", "epoch", "steps"] = Field("no", description="The evaluation strategy to adopt.")
    gradient_checkpointing: bool = Field(False, description="Use gradient checkpointing to save memory.")
    fp16: bool = Field(False, description="Whether to use fp16 (mixed) precision training.")
    bf16: bool = Field(False, description="Whether to use bf16 (mixed) precision training (requires Ampere or newer GPUs).")
    max_seq_length: Optional[int] = Field(None, description="Maximum sequence length for tokenization.")

class EvaluationConfig(BaseModel):
    metrics: List[str] = Field(["loss"], description="List of metrics to compute during evaluation (e.g., loss, accuracy, perplexity).")

class FineTuningJobConfig(BaseModel):
    job_name: Optional[str] = Field(None, description="User-friendly name for the fine-tuning job.")
    base_model_id: str = Field(description="Identifier of the base model from LLMModelManager.")
    new_model_id: str = Field(description="Desired identifier for the fine-tuned model.")
    task_type: Optional[str] = Field(None, description="Type of task (e.g., text-generation, classification, summarization). Helps in data formatting.")
    dataset_config: DatasetSourceConfig
    fine_tuning_technique: FineTuningTechniqueConfig
    hyperparameters: TrainingHyperparameters
    evaluation_config: Optional[EvaluationConfig] = Field(None, description="Configuration for model evaluation.")

class FineTuningJobStatusInfo(BaseModel):
    job_id: str = Field(description="Unique identifier for the fine-tuning job.")
    job_name: Optional[str] = Field(None, description="User-friendly name of the job.")
    status: Literal["queued", "preprocessing", "running", "evaluating", "completed", "failed", "cancelled"] = Field(description="Current status of the job.")
    progress_percentage: Optional[float] = Field(None, ge=0, le=100, description="Overall job progress percentage.")
    current_epoch: Optional[float] = Field(None, description="Current training epoch (if applicable).")
    current_step: Optional[int] = Field(None, description="Current training step (if applicable).")
    total_steps: Optional[int] = Field(None, description="Total training steps planned (if known).")
    metrics: Optional[Dict[str, Any]] = Field(None, description="Latest metrics from training/evaluation (e.g., {\"loss\": 0.5, \"accuracy\": 0.8}).")
    logs_location: Optional[str] = Field(None, description="Path or reference to where detailed logs are stored.")
    error_message: Optional[str] = Field(None, description="Error message if the job failed.")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = Field(None)
    completed_at: Optional[datetime] = Field(None)
    fine_tuned_model_id: Optional[str] = Field(None, description="Identifier of the resulting fine-tuned model upon successful completion.")
    output_model_path: Optional[str] = Field(None, description="Path where the final model artifacts are stored.")

# --- Abstract Base Classes for Extensibility ---

class BaseDatasetHandler(ABC):
    def __init__(self, job_config: FineTuningJobConfig, model_manager: LLMModelManager, work_dir: str):
        self.job_config = job_config
        self.model_manager = model_manager
        self.work_dir = work_dir
        self.base_model_tokenizer: Optional[Any] = None
        logger.info(f"DatasetHandler initialized for job {job_config.job_name or job_config.new_model_id}")

    @abstractmethod
    async def prepare_data(self, job_instance: "FineTuningJob") -> Dict[str, Any]:
        """Loads, preprocesses, tokenizes, and splits the dataset."""
        pass

class BaseTrainer(ABC):
    def __init__(self, job_config: FineTuningJobConfig, model_manager: LLMModelManager, 
                 tokenized_datasets: Dict[str, Any], base_model_path: str, base_tokenizer_path: str, output_dir: str):
        self.job_config = job_config
        self.model_manager = model_manager
        self.tokenized_datasets = tokenized_datasets
        self.base_model_path = base_model_path
        self.base_tokenizer_path = base_tokenizer_path
        self.output_dir = output_dir
        self.status_updater: Optional[callable] = None
        logger.info(f"BaseTrainer initialized for job {job_config.job_name or job_config.new_model_id}")

    def set_status_updater(self, updater: callable):
        self.status_updater = updater

    async def _update_status(self, partial_status: Dict[str, Any]):
        if self.status_updater:
            await self.status_updater(partial_status)

    @abstractmethod
    async def train(self, job_instance: "FineTuningJob") -> Dict[str, Any]:
        """Executes the fine-tuning training loop."""
        pass

    @abstractmethod
    async def evaluate(self, job_instance: "FineTuningJob") -> Optional[Dict[str, Any]]:
        """Evaluates the fine-tuned model."""
        pass
    
    def get_final_model_path(self) -> str:
        return self.output_dir

# --- FineTuningJob Class (Internal representation of a job) ---

class FineTuningJob:
    def __init__(self, job_id: str, config: FineTuningJobConfig, service_ref: "LLMFineTuningService"):
        self.job_id = job_id
        self.config = config
        self.service_ref = service_ref
        self.status_info = FineTuningJobStatusInfo(
            job_id=job_id, 
            job_name=config.job_name,
            status="queued"
        )
        self.dataset_handler: Optional[BaseDatasetHandler] = None
        self.trainer: Optional[BaseTrainer] = None
        self.output_dir = os.path.join(config.hyperparameters.output_dir_base, job_id)
        self._cancel_requested = False
        self._run_task: Optional[asyncio.Task] = None
        logger.info(f"FineTuningJob {job_id} initialized for {config.new_model_id}")

    async def update_status(self, partial_status_update: Dict[str, Any]):
        current_time = datetime.now(timezone.utc)
        update_data = partial_status_update.copy()
        
        if "status" in update_data:
            self.status_info.status = update_data["status"]
            if update_data["status"] == "preprocessing" and not self.status_info.started_at:
                 self.status_info.started_at = current_time
            if update_data["status"] == "running" and not self.status_info.started_at:
                 self.status_info.started_at = current_time # Should have been set in preprocessing
            elif update_data["status"] in ["completed", "failed", "cancelled"]:
                self.status_info.completed_at = current_time
        
        for key, value in update_data.items():
            if hasattr(self.status_info, key):
                setattr(self.status_info, key, value)
        
        await self.service_ref._notify_job_update(self.job_id, self.status_info)

    async def run(self):
        logger.info(f"Job {self.job_id}: Starting run.")
        try:
            if self._cancel_requested:
                await self.update_status({"status": "cancelled", "error_message": "Job cancelled before start."})
                logger.info(f"Job {self.job_id}: Cancelled before start.")
                return

            dataset_handler_cls_factory = self.service_ref._get_dataset_handler_factory()
            dataset_handler_cls = dataset_handler_cls_factory(self.config.dataset_config.source_type)
            self.dataset_handler = dataset_handler_cls(self.config, self.service_ref.model_manager, self.output_dir)

            await self.update_status({"status": "preprocessing", "started_at": datetime.now(timezone.utc)})
            os.makedirs(self.output_dir, exist_ok=True)
            self.status_info.logs_location = os.path.join(self.output_dir, "job.log")
            logger.debug(f"Job {self.job_id}: Output directory created/ensured: {self.output_dir}")

            tokenized_datasets = await self.dataset_handler.prepare_data(self) # Pass self (job_instance)
            await self.update_status({"progress_percentage": 20.0})

            if self._cancel_requested:
                await self.update_status({"status": "cancelled", "error_message": "Job cancelled after data preparation."})
                logger.info(f"Job {self.job_id}: Cancelled after data preparation.")
                return

            await self.update_status({"status": "running"})
            mock_base_model_details = await self.service_ref.model_manager.get_model_instance(self.config.base_model_id, for_training=True)
            base_model_path = mock_base_model_details["model"].name_or_path
            base_tokenizer_path = mock_base_model_details["tokenizer"].name_or_path
            
            trainer_cls_factory = self.service_ref._get_trainer_factory()
            trainer_cls = trainer_cls_factory(self.config.fine_tuning_technique.method)
            self.trainer = trainer_cls(self.config, self.service_ref.model_manager, tokenized_datasets, 
                                       base_model_path, base_tokenizer_path, self.output_dir)
            self.trainer.set_status_updater(self.update_status)
            
            train_metrics = await self.trainer.train(self) # Pass self (job_instance)
            await self.update_status({"progress_percentage": 90.0, "metrics": {**(self.status_info.metrics or {}), **train_metrics}})

            if self._cancel_requested:
                await self.update_status({"status": "cancelled", "error_message": "Job cancelled after training."})
                logger.info(f"Job {self.job_id}: Cancelled after training.")
                return

            eval_metrics = None
            if self.config.evaluation_config:
                await self.update_status({"status": "evaluating"})
                eval_metrics = await self.trainer.evaluate(self) # Pass self (job_instance)
                await self.update_status({"progress_percentage": 95.0, "metrics": {**(self.status_info.metrics or {}), **(eval_metrics or {})}})
            
            if self._cancel_requested:
                await self.update_status({"status": "cancelled", "error_message": "Job cancelled after evaluation."})
                logger.info(f"Job {self.job_id}: Cancelled after evaluation.")
                return

            final_model_path = self.trainer.get_final_model_path()
            # For mock, tokenizer path is assumed to be same as model path or handled by model_manager
            await self.service_ref.model_manager.save_fine_tuned_model(
                base_model_id=self.config.base_model_id,
                new_model_id=self.config.new_model_id,
                model_path=final_model_path,
                tokenizer_path=final_model_path, # Placeholder
                fine_tuning_config=self.config.dict(),
                metrics=self.status_info.metrics
            )
            logger.info(f"Job {self.job_id}: Fine-tuned model saved/registered as {self.config.new_model_id}.")
            await self.update_status({"status": "completed", "progress_percentage": 100.0, 
                                    "fine_tuned_model_id": self.config.new_model_id,
                                    "output_model_path": final_model_path})

        except JobExecutionError as e: # Covers cancellation from within prepare_data/train/evaluate
            logger.error(f"Job {self.job_id} execution failed: {e}")
            error_msg = str(e)
            status = "cancelled" if "cancelled by user" in error_msg.lower() else "failed"
            await self.update_status({"status": status, "error_message": error_msg})
        except ModelNotFoundError as e:
            logger.error(f"Job {self.job_id} failed due to ModelNotFoundError: {e}")
            await self.update_status({"status": "failed", "error_message": f"Base model not found: {e}"})
        except Exception as e:
            logger.exception(f"Job {self.job_id} failed with an unexpected error.")
            await self.update_status({"status": "failed", "error_message": f"Unexpected error: {str(e)}"})

    async def cancel(self) -> bool:
        if self.status_info.status in ["completed", "failed", "cancelled"]:
            logger.warning(f"Job {self.job_id} is already in a terminal state ({self.status_info.status}). Cannot cancel.")
            return False
        
        self._cancel_requested = True
        logger.info(f"Job {self.job_id}: Cancellation requested.")

        if self.status_info.status == "queued":
            await self.update_status({"status": "cancelled", "error_message": "Cancelled while queued."})
            logger.info(f"Job {self.job_id}: Cancelled while in queue.")
            # If it was in the service queue, it needs to be removed or skipped by processor
            # The _job_processor_task in the service handles this by checking _cancel_requested
            return True
        
        # If already running, the _run_task will see _cancel_requested and handle it.
        # The FineTuningJob.run() method itself checks _cancel_requested at various points.
        # And the PlaceholderDatasetHandler/Trainer also check it via the passed job_instance.
        if self._run_task and not self._run_task.done():
            # Optionally, one could try to cancel the task more forcefully, but 
            # cooperative cancellation via _cancel_requested is preferred.
            # self._run_task.cancel() # This might be too abrupt
            pass
        return True

# --- LLMFineTuningService Class ---

class LLMFineTuningService:
    def __init__(self, model_manager: LLMModelManager, global_config: Optional[Dict[str, Any]] = None):
        self.model_manager = model_manager
        self.global_config = global_config or {}
        self.job_store: Dict[str, FineTuningJob] = {}
        self.job_status_cache: Dict[str, FineTuningJobStatusInfo] = {}
        self.job_queue: asyncio.Queue[str] = asyncio.Queue()
        self._active_job_tasks: Dict[str, asyncio.Task] = {}
        self._job_processor_task: Optional[asyncio.Task] = None
        self.max_concurrent_jobs = self.global_config.get("max_concurrent_fine_tuning_jobs", 1)
        self.poll_interval = self.global_config.get("job_queue_poll_interval_seconds", 5)
        logger.info("LLMFineTuningService initialized.")

    async def start(self):
        """Starts the background job processor task."""
        if self._job_processor_task is None or self._job_processor_task.done():
            self._job_processor_task = asyncio.create_task(self._process_job_queue())
            logger.info("LLMFineTuningService job processor started.")
        else:
            logger.warning("LLMFineTuningService job processor already running.")

    async def stop(self):
        logger.info("LLMFineTuningService stopping...")
        if self._job_processor_task and not self._job_processor_task.done():
            self._job_processor_task.cancel()
            try:
                await self._job_processor_task
            except asyncio.CancelledError:
                logger.info("Job processor task cancelled.")
        
        active_job_ids = list(self._active_job_tasks.keys())
        if active_job_ids:
            logger.info(f"Cancelling {len(active_job_ids)} active fine-tuning jobs: {active_job_ids}")
            for job_id in active_job_ids:
                await self.cancel_fine_tuning_job(job_id)
            await asyncio.gather(*[task for task in self._active_job_tasks.values() if not task.done()], return_exceptions=True)
        logger.info("LLMFineTuningService stopped.")

    async def _notify_job_update(self, job_id: str, status_info: FineTuningJobStatusInfo):
        self.job_status_cache[job_id] = status_info
        logger.debug(f"Job {job_id} status updated in cache: {status_info.status}")

    def _validate_job_config(self, job_config: FineTuningJobConfig):
        if not job_config.new_model_id:
            raise InvalidJobConfigError("new_model_id must be provided.")
        if not job_config.base_model_id:
            raise InvalidJobConfigError("base_model_id must be provided.")
        logger.info(f"Job config for {job_config.new_model_id} validated.")

    async def submit_fine_tuning_job(self, job_config: FineTuningJobConfig) -> FineTuningJobStatusInfo:
        try:
            self._validate_job_config(job_config)
        except InvalidJobConfigError as e:
            logger.error(f"Invalid job submission: {e}")
            raise

        job_id = str(uuid.uuid4())
        job = FineTuningJob(job_id=job_id, config=job_config, service_ref=self)
        self.job_store[job_id] = job
        self.job_status_cache[job_id] = job.status_info
        
        await self.job_queue.put(job_id)
        logger.info(f"Fine-tuning job {job_id} (New Model: {job_config.new_model_id}) submitted and queued.")
        return job.status_info

    async def get_job_status(self, job_id: str) -> Optional[FineTuningJobStatusInfo]:
        return self.job_status_cache.get(job_id)

    async def list_fine_tuning_jobs(self, limit: int = 20, offset: int = 0, 
                                    status_filter: Optional[str] = None) -> List[FineTuningJobStatusInfo]:
        all_statuses = sorted(self.job_status_cache.values(), key=lambda s: s.created_at, reverse=True)
        filtered_statuses = [s for s in all_statuses if not status_filter or s.status == status_filter]
        return filtered_statuses[offset : offset + limit]

    async def cancel_fine_tuning_job(self, job_id: str) -> bool:
        job = self.job_store.get(job_id)
        if not job:
            logger.warning(f"Attempted to cancel non-existent job {job_id}.")
            return False
        return await job.cancel()

    def _get_dataset_handler_factory(self) -> callable:
        class PlaceholderDatasetHandler(BaseDatasetHandler):
            async def prepare_data(self, job_instance: "FineTuningJob") -> Dict[str, Any]:
                logger.warning(f"Job {self.job_config.job_name or self.job_config.new_model_id} (PlaceholderDatasetHandler): Using placeholder data preparation.")
                await job_instance.update_status({"progress_percentage": 5.0})

                for i in range(3): # Simulate a few steps
                    if job_instance._cancel_requested:
                        logger.info(f"Job {job_instance.job_id} (PlaceholderDatasetHandler): Cancellation detected during data preparation.")
                        raise JobExecutionError("Data preparation cancelled by user.")
                    await asyncio.sleep(0.05) # Simulate I/O or short computation
                    await job_instance.update_status({"progress_percentage": 5.0 + (i + 1) * 5})

                if self.job_config.base_model_id == "force_dataset_failure_model":
                    logger.error(f"Job {self.job_config.job_name} (PlaceholderDatasetHandler): Simulating dataset preparation failure.")
                    raise JobExecutionError("Simulated dataset preparation failure.")

                logger.info(f"Job {self.job_config.job_name or self.job_config.new_model_id} (PlaceholderDatasetHandler): Mock data preparation completed.")
                return {"train": "mock_train_dataset", "eval": "mock_eval_dataset", "test": "mock_test_dataset"}
        # This factory now returns the class itself, to be instantiated with (job_config, model_manager, work_dir)
        # The type hint for the factory in the service should be `Callable[[str], Type[BaseDatasetHandler]]` if it took type_str
        # Or just `Type[BaseDatasetHandler]` if it always returns one type like this placeholder.
        # For simplicity, we assume the factory returns the class, and the caller instantiates.
        # The current _get_dataset_handler_factory returns a callable that when called with source_type returns the class.
        # Let's simplify: the factory returns the class directly for placeholder.
        def factory(source_type: str):
            # Here one could switch based on source_type if multiple handlers existed
            return PlaceholderDatasetHandler
        return factory

    def _get_trainer_factory(self) -> callable:
        class PlaceholderTrainer(BaseTrainer):
            async def train(self, job_instance: "FineTuningJob") -> Dict[str, Any]:
                logger.warning(f"Job {self.job_config.job_name or self.job_config.new_model_id} (PlaceholderTrainer): Using placeholder training loop.")
                await self._update_status({"progress_percentage": 25.0, "current_epoch": 0, "current_step": 0, "total_steps": 10})

                for step in range(1, 11):
                    if job_instance._cancel_requested:
                        logger.info(f"Job {job_instance.job_id} (PlaceholderTrainer): Cancellation detected during training.")
                        raise JobExecutionError("Training cancelled by user.")
                    
                    await asyncio.sleep(0.1)
                    current_progress = 25.0 + (step / 10.0) * 65.0
                    await self._update_status({
                        "progress_percentage": round(current_progress, 1),
                        "current_step": step,
                        "metrics": {"loss": 1.0 - (step / 20.0), "mock_accuracy": 0.5 + (step / 20.0)}
                    })
                    if step % self.job_config.hyperparameters.logging_steps == 0:
                         logger.info(f"Job {self.job_config.job_name}: Mock Train Step {step}/10, Loss: {1.0 - (step / 20.0)}")

                if self.job_config.base_model_id == "force_train_failure_model":
                    logger.error(f"Job {self.job_config.job_name} (PlaceholderTrainer): Simulating training failure.")
                    raise JobExecutionError("Simulated training failure mid-run.")

                logger.info(f"Job {self.job_config.job_name or self.job_config.new_model_id} (PlaceholderTrainer): Placeholder training completed.")
                return {"final_loss": 0.5, "mock_final_accuracy": 0.95, "epochs_trained": self.job_config.hyperparameters.num_train_epochs}

            async def evaluate(self, job_instance: "FineTuningJob") -> Optional[Dict[str, Any]]:
                logger.warning(f"Job {self.job_config.job_name or self.job_config.new_model_id} (PlaceholderTrainer): Using placeholder evaluation.")
                if job_instance._cancel_requested:
                    logger.info(f"Job {job_instance.job_id} (PlaceholderTrainer): Cancellation detected before evaluation.")
                    raise JobExecutionError("Evaluation cancelled by user.")
                
                await asyncio.sleep(0.05)
                await self._update_status({"progress_percentage": 95.0})
                logger.info(f"Job {self.job_config.job_name or self.job_config.new_model_id} (PlaceholderTrainer): Placeholder evaluation completed.")
                return {"eval_loss": 0.45, "eval_mock_accuracy": 0.96}
        # Similar to dataset handler factory, this returns a callable that takes method and returns class.
        def factory(method_name: str):
            return PlaceholderTrainer
        return factory

    async def _run_fine_tuning_job_internal(self, job: FineTuningJob):
        logger.info(f"Job {job.job_id}: Internal run process started.")
        try:
            if job._cancel_requested: # Check if cancelled while in queue
                await job.update_status({"status": "cancelled", "error_message": "Job cancelled while queued before processing."})
                logger.info(f"Job {job.job_id}: Skipped processing as it was cancelled in queue.")
                return

            dataset_handler_cls_factory = self._get_dataset_handler_factory()
            dataset_handler_cls = dataset_handler_cls_factory(job.config.dataset_config.source_type)
            job.dataset_handler = dataset_handler_cls(job.config, self.model_manager, job.output_dir)

            tokenized_datasets = await job.dataset_handler.prepare_data(job) 

            mock_base_model_details = await self.model_manager.get_model_instance(job.config.base_model_id, for_training=True)
            base_model_path = mock_base_model_details["model"].name_or_path
            base_tokenizer_path = mock_base_model_details["tokenizer"].name_or_path
            
            trainer_cls_factory = self._get_trainer_factory()
            trainer_cls = trainer_cls_factory(job.config.fine_tuning_technique.method)
            job.trainer = trainer_cls(job.config, self.model_manager, tokenized_datasets, 
                                      base_model_path, base_tokenizer_path, job.output_dir)
            job.trainer.set_status_updater(job.update_status)
            
            # Call job.run() which orchestrates the steps and handles its own status updates
            await job.run() # job.run() will call prepare_data, train, evaluate internally now

        except Exception as e: # Catch-all for unexpected errors during setup before job.run() takes over
            logger.exception(f"Job {job.job_id}: Unexpected error during setup phase of internal run: {e}")
            await job.update_status({"status": "failed", "error_message": f"Unexpected setup error: {str(e)}"})
        finally:
            self._active_job_tasks.pop(job.job_id, None)
            logger.info(f"Job {job.job_id}: Internal run process finished. Active tasks: {len(self._active_job_tasks)}")

    async def _process_job_queue(self):
        while True:
            try:
                if len(self._active_job_tasks) < self.max_concurrent_jobs:
                    try:
                        job_id = await asyncio.wait_for(self.job_queue.get(), timeout=self.poll_interval)
                    except asyncio.TimeoutError:
                        continue # No job in queue, continue polling

                    job = self.job_store.get(job_id)
                    if not job:
                        logger.error(f"Job {job_id} found in queue but not in store. Discarding.")
                        self.job_queue.task_done()
                        continue
                    
                    if job._cancel_requested and job.status_info.status == "queued":
                        logger.info(f"Job {job_id} was cancelled while in queue. Updating status and skipping execution.")
                        await job.update_status({"status": "cancelled", "error_message": "Cancelled while queued."})
                        self.job_queue.task_done()
                        continue

                    logger.info(f"Dequeued job {job_id} for processing. Active tasks: {len(self._active_job_tasks)}")
                    # Store the task itself in FineTuningJob, so it can be awaited/cancelled if needed
                    job._run_task = asyncio.create_task(self._run_fine_tuning_job_internal(job))
                    self._active_job_tasks[job_id] = job._run_task
                    self.job_queue.task_done()
                else:
                    await asyncio.sleep(self.poll_interval) # Wait before checking queue again
            except asyncio.CancelledError:
                logger.info("Job processor task is shutting down.")
                break
            except Exception as e:
                logger.exception(f"Error in job processor loop: {e}")
                await asyncio.sleep(self.poll_interval) # Avoid fast spinning on error

# Example usage (for testing or as a script)
if __name__ == "__main__":
    TEST_OUTPUT_BASE_DIR = "/tmp/test_fine_tuning_runs"
    if os.path.exists(TEST_OUTPUT_BASE_DIR):
        shutil.rmtree(TEST_OUTPUT_BASE_DIR)
    os.makedirs(TEST_OUTPUT_BASE_DIR)

    async def main_test():
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        logger.info("--- Starting LLMFineTuningService Test Suite ---")

        mock_model_manager = LLMModelManager()
        ft_service_config = {
            "max_concurrent_fine_tuning_jobs": 1,
            "job_queue_poll_interval_seconds": 0.1 # Faster polling for tests
        }
        ft_service = LLMFineTuningService(model_manager=mock_model_manager, global_config=ft_service_config)
        await ft_service.start()

        test_results = {"passed": 0, "failed": 0}

        def print_test_result(test_name, success, message=""):
            nonlocal test_results
            if success:
                logger.info(f"TEST PASSED: {test_name} {message}")
                test_results["passed"] += 1
            else:
                logger.error(f"TEST FAILED: {test_name} {message}")
                test_results["failed"] += 1

        # --- Test Case 1: Submit a valid LoRA job and monitor to completion ---
        logger.info("--- Test Case 1: Valid LoRA Job Submission and Completion ---")
        job_config_1 = FineTuningJobConfig(
            job_name="Test LoRA Job Success",
            base_model_id="gpt2-medium",
            new_model_id="gpt2-medium-lora-custom-test1",
            task_type="text-generation",
            dataset_config=DatasetSourceConfig(
                source_type="hf_dataset", path_or_id="wikitext", format="arrow",
                train_split_name="train", validation_split_name="test",
                task_format_details={"dataset_config_name": "wikitext-2-raw-v1", "text_column": "text"}
            ),
            fine_tuning_technique=FineTuningTechniqueConfig(method="lora", params=LoRAParams(r=2, lora_alpha=4)),
            hyperparameters=TrainingHyperparameters(
                num_train_epochs=0.01, learning_rate=1e-4, per_device_train_batch_size=1,
                logging_steps=1, save_steps=5, eval_steps=2, evaluation_strategy="steps",
                max_seq_length=64, output_dir_base=TEST_OUTPUT_BASE_DIR
            ),
            evaluation_config=EvaluationConfig(metrics=["perplexity"])
        )
        status1_submitted = await ft_service.submit_fine_tuning_job(job_config_1)
        print_test_result("Job1 Submission", status1_submitted.status == "queued", f"ID: {status1_submitted.job_id}")

        # --- Test Case 2: Job Submission with Non-Existent Base Model ---
        logger.info("--- Test Case 2: Job Submission with Non-Existent Base Model ---")
        job_config_nonexist_base = FineTuningJobConfig(
            job_name="Test Job Failure (Bad Base Model)",
            base_model_id="non_existent_base_model",
            new_model_id="test-fail-model-nonexist-base",
            dataset_config=job_config_1.dataset_config,
            fine_tuning_technique=FineTuningTechniqueConfig(method="full"),
            hyperparameters=TrainingHyperparameters(num_train_epochs=0.01, output_dir_base=TEST_OUTPUT_BASE_DIR)
        )
        status_nonexist_base_submitted = await ft_service.submit_fine_tuning_job(job_config_nonexist_base)
        print_test_result("JobNonExistBase Submission", status_nonexist_base_submitted.status == "queued", f"ID: {status_nonexist_base_submitted.job_id}")

        # --- Test Case 3: Job Submission and Cancellation ---
        logger.info("--- Test Case 3: Job Submission and Cancellation ---")
        job_config_cancel = FineTuningJobConfig(
            job_name="Test Job Cancellation",
            base_model_id="distilgpt2", new_model_id="distilgpt2-cancel-test",
            dataset_config=job_config_1.dataset_config,
            fine_tuning_technique=FineTuningTechniqueConfig(method="full"),
            hyperparameters=TrainingHyperparameters(num_train_epochs=0.1, output_dir_base=TEST_OUTPUT_BASE_DIR, logging_steps=1)
        )
        status_cancel_submitted = await ft_service.submit_fine_tuning_job(job_config_cancel)
        print_test_result("JobCancel Submission", status_cancel_submitted.status == "queued", f"ID: {status_cancel_submitted.job_id}")
        
        await asyncio.sleep(0.2) # Let queue processor pick it up
        s_cancel_before_obj = await ft_service.get_job_status(status_cancel_submitted.job_id)
        if s_cancel_before_obj and s_cancel_before_obj.status in ["preprocessing", "running"]:
            logger.info(f"Attempting to cancel JobCancel ({status_cancel_submitted.job_id}) in status {s_cancel_before_obj.status}")
            cancel_success = await ft_service.cancel_fine_tuning_job(status_cancel_submitted.job_id)
            print_test_result("JobCancel Cancellation Request", cancel_success)
        else:
            # If it processes too fast, try cancelling anyway if queued
            if s_cancel_before_obj and s_cancel_before_obj.status == "queued":
                logger.info(f"JobCancel ({status_cancel_submitted.job_id}) still queued, attempting cancel.")
                cancel_success = await ft_service.cancel_fine_tuning_job(status_cancel_submitted.job_id)
                print_test_result("JobCancel Cancellation Request (while queued)", cancel_success)
            else:
                print_test_result("JobCancel Cancellation Request", False, f"Job not in cancellable state or found: {s_cancel_before_obj.status if s_cancel_before_obj else 'Not Found'}")

        # --- Test Case 4: Dataset Preparation Failure ---
        logger.info("--- Test Case 4: Dataset Preparation Failure ---")
        job_config_dataset_fail = FineTuningJobConfig(
            job_name="Test Dataset Prep Failure",
            base_model_id="force_dataset_failure_model",
            new_model_id="test-dataset-fail-model",
            dataset_config=job_config_1.dataset_config,
            fine_tuning_technique=FineTuningTechniqueConfig(method="full"),
            hyperparameters=TrainingHyperparameters(num_train_epochs=0.01, output_dir_base=TEST_OUTPUT_BASE_DIR)
        )
        status_dataset_fail_submitted = await ft_service.submit_fine_tuning_job(job_config_dataset_fail)
        print_test_result("JobDatasetFail Submission", status_dataset_fail_submitted.status == "queued", f"ID: {status_dataset_fail_submitted.job_id}")

        # --- Test Case 5: Training Failure ---
        logger.info("--- Test Case 5: Training Failure ---")
        job_config_train_fail = FineTuningJobConfig(
            job_name="Test Training Failure",
            base_model_id="force_train_failure_model",
            new_model_id="test-train-fail-model",
            dataset_config=job_config_1.dataset_config,
            fine_tuning_technique=FineTuningTechniqueConfig(method="full"),
            hyperparameters=TrainingHyperparameters(num_train_epochs=0.01, output_dir_base=TEST_OUTPUT_BASE_DIR)
        )
        status_train_fail_submitted = await ft_service.submit_fine_tuning_job(job_config_train_fail)
        print_test_result("JobTrainFail Submission", status_train_fail_submitted.status == "queued", f"ID: {status_train_fail_submitted.job_id}")

        # Monitor jobs
        logger.info("--- Monitoring all submitted jobs ---")
        submitted_job_statuses = [s for s in [status1_submitted, status_nonexist_base_submitted, status_cancel_submitted, status_dataset_fail_submitted, status_train_fail_submitted] if s]
        active_jobs_ids = [s.job_id for s in submitted_job_statuses]
        
        max_monitoring_loops = 60 # ~30 seconds with 0.5s sleep
        for i in range(max_monitoring_loops):
            if not active_jobs_ids: break
            current_statuses_str = []
            for job_id in active_jobs_ids[:]:
                s = await ft_service.get_job_status(job_id)
                if s:
                    current_statuses_str.append(f"{s.job_name or s.job_id}: {s.status} ({s.progress_percentage or 0}%)")
                    if s.status in ["completed", "failed", "cancelled"]:
                        if job_id == status1_submitted.job_id:
                            print_test_result(f"Job1 ({s.job_id}) Final Status", s.status == "completed", f"Status: {s.status}")
                        elif job_id == status_nonexist_base_submitted.job_id:
                            print_test_result(f"JobNonExistBase ({s.job_id}) Final Status", s.status == "failed", f"Status: {s.status}")
                            if s.status == "failed": print_test_result(f"JobNonExistBase Error Msg", "Base model not found" in (s.error_message or ""))
                        elif job_id == status_cancel_submitted.job_id:
                            print_test_result(f"JobCancel ({s.job_id}) Final Status", s.status == "cancelled", f"Status: {s.status}")
                        elif job_id == status_dataset_fail_submitted.job_id:
                            print_test_result(f"JobDatasetFail ({s.job_id}) Final Status", s.status == "failed", f"Status: {s.status}")
                            if s.status == "failed": print_test_result(f"JobDatasetFail Error Msg", "Simulated dataset preparation failure" in (s.error_message or ""))
                        elif job_id == status_train_fail_submitted.job_id:
                            print_test_result(f"JobTrainFail ({s.job_id}) Final Status", s.status == "failed", f"Status: {s.status}")
                            if s.status == "failed": print_test_result(f"JobTrainFail Error Msg", "Simulated training failure mid-run" in (s.error_message or ""))
                        active_jobs_ids.remove(job_id)
            
            if current_statuses_str: logger.info(f"Monitoring Iteration {i+1}: {'; '.join(current_statuses_str)}")
            if not active_jobs_ids: logger.info("All monitored jobs reached terminal states."); break
            await asyncio.sleep(0.5)
        else:
            logger.warning("Monitoring loop timed out.")
            for job_id in active_jobs_ids:
                 s = await ft_service.get_job_status(job_id)
                 print_test_result(f"Job {s.job_name or job_id} Timeout Check", False, f"Did not reach terminal state. Final status: {s.status}")

        # --- Test Case 6: List jobs ---
        logger.info("--- Test Case 6: List Jobs ---")
        listed_jobs = await ft_service.list_fine_tuning_jobs(limit=10)
        print_test_result("List Jobs Count", len(listed_jobs) >= 5, f"Found {len(listed_jobs)} jobs. Expected at least 5.")

        # --- Test Case 7: Invalid Job Config Submission (e.g., missing new_model_id) ---
        logger.info("--- Test Case 7: Invalid Job Config Submission ---")
        try:
            job_config_invalid = FineTuningJobConfig(
                base_model_id="gpt2", new_model_id="", dataset_config=job_config_1.dataset_config,
                fine_tuning_technique=FineTuningTechniqueConfig(method="full"),
                hyperparameters=TrainingHyperparameters(output_dir_base=TEST_OUTPUT_BASE_DIR)
            )
            await ft_service.submit_fine_tuning_job(job_config_invalid)
            print_test_result("Invalid Job Submission (Empty new_model_id)", False, "Should have raised InvalidJobConfigError")
        except InvalidJobConfigError:
            print_test_result("Invalid Job Submission (Empty new_model_id)", True, "Correctly raised InvalidJobConfigError")
        except Exception as e:
            print_test_result("Invalid Job Submission (Empty new_model_id)", False, f"Raised unexpected error: {e}")

        logger.info("--- Test Suite Finished ---")
        logger.info(f"SUMMARY: Passed: {test_results['passed']}, Failed: {test_results['failed']}")

        await ft_service.stop()
        if os.path.exists(TEST_OUTPUT_BASE_DIR):
            logger.warning(f"Test output directory {TEST_OUTPUT_BASE_DIR} was NOT automatically cleaned up for inspection.")

    asyncio.run(main_test())

