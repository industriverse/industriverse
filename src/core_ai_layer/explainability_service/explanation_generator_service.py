# explanation_generator_service.py

import asyncio
import logging
import uuid
from datetime import datetime # Added missing import
from typing import Dict, Type, List, Optional, Any, Union # Added Union

from .explanation_schemas import (
    ExplanationRequest,
    ExplanationResponse,
    AsyncJobStatus,
    ModelIdentifier,
    ProvenanceInfo
)
from .xai_exceptions import (
    ConfigurationError,
    ModelAccessError,
    MethodNotApplicableError,
    ExplanationGenerationError,
    ResourceNotFoundError,
    InvalidInputError,
    XAIError # Added XAIError for broader catch
)
from .xai_method_integrators.base_integrator import XAIMethodIntegratorInterface
from .model_adapters.base_adapter import ModelAdapterInterface, ModelDetails

# Import implemented integrators and adapters
from .xai_method_integrators.shap_integrator import SHAPIntegrator
from .model_adapters.ml_service_adapter import MLServiceAdapter
from .model_adapters.llm_service_adapter import LLMServiceAdapter

# Register implemented integrators and adapters
REGISTERED_INTEGRATORS: List[Type[XAIMethodIntegratorInterface]] = [SHAPIntegrator]
REGISTERED_ADAPTERS: List[Type[ModelAdapterInterface]] = [MLServiceAdapter, LLMServiceAdapter]

logger = logging.getLogger(__name__)

class ExplanationGeneratorService:
    """
    Service responsible for orchestrating the generation of model explanations.
    It receives requests, selects appropriate XAI methods and model adapters,
    manages the explanation process, and returns the results.
    """

    def __init__(self, 
                 integrators: Optional[List[Type[XAIMethodIntegratorInterface]]] = None,
                 adapters: Optional[List[Type[ModelAdapterInterface]]] = None,
                 global_xai_config: Optional[Dict[str, Any]] = None):
        """
        Initializes the ExplanationGeneratorService.

        Args:
            integrators: A list of XAI method integrator classes.
            adapters: A list of model adapter classes.
            global_xai_config: Global configuration for XAI methods or adapters.
        """
        self.integrators = integrators if integrators is not None else REGISTERED_INTEGRATORS
        self.adapters = adapters if adapters is not None else REGISTERED_ADAPTERS
        self.global_xai_config = global_xai_config or {}
        self.active_async_jobs: Dict[uuid.UUID, AsyncJobStatus] = {}
        logger.info(f"ExplanationGeneratorService initialized with {len(self.integrators)} integrators and {len(self.adapters)} adapters.")

    async def generate_explanation(self, request: ExplanationRequest) -> Union[ExplanationResponse, AsyncJobStatus]:
        """
        Generates an explanation based on the provided request.
        Can run synchronously or asynchronously based on request.run_async.
        """
        logger.info(f"Received explanation request {request.request_id} for model {request.model_identifier.model_id}, type: {request.explanation_type}")

        if request.run_async:
            job_id = uuid.uuid4()
            initial_status = AsyncJobStatus(
                job_id=job_id,
                status="pending",
                message="Explanation job submitted and queued.",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.active_async_jobs[job_id] = initial_status
            asyncio.create_task(self._execute_explanation_job(job_id, request))
            logger.info(f"Asynchronous explanation job {job_id} started for request {request.request_id}.")
            return initial_status
        else:
            try:
                return await self._process_explanation_request(request)
            except XAIError as e:
                logger.error(f"Error processing synchronous request {request.request_id}: {e}", exc_info=True)
                raise
            except Exception as e:
                logger.error(f"Unexpected error processing synchronous request {request.request_id}: {e}", exc_info=True)
                raise ExplanationGenerationError(f"Unexpected error: {str(e)}")

    async def get_async_job_status(self, job_id: uuid.UUID) -> AsyncJobStatus:
        """
        Retrieves the status of an asynchronous explanation job.
        """
        status = self.active_async_jobs.get(job_id)
        if not status:
            raise ResourceNotFoundError("AsyncExplanationJob", str(job_id))
        logger.debug(f"Retrieved status for async job {job_id}: {status.status}")
        return status

    async def get_explanation_result(self, explanation_id: uuid.UUID) -> ExplanationResponse:
        """
        Retrieves a completed explanation result by its ID.
        This method would require a persistent storage mechanism for ExplanationResponse objects.
        """
        # Placeholder: In a real system, this would fetch from a database or cache.
        # Check if any async job completed with this result_id
        for job_status in self.active_async_jobs.values():
            if job_status.result_id == explanation_id and hasattr(job_status, "_full_response"):
                 return job_status._full_response # Non-standard attribute for demo
        raise ResourceNotFoundError("ExplanationResult", str(explanation_id))

    async def _execute_explanation_job(self, job_id: uuid.UUID, request: ExplanationRequest):
        """
        Internal method to execute an explanation job asynchronously.
        Updates the job status in self.active_async_jobs.
        """
        job_status = self.active_async_jobs[job_id]
        job_status.status = "running"
        job_status.message = "Explanation generation in progress."
        job_status.updated_at = datetime.utcnow()

        try:
            explanation_response = await self._process_explanation_request(request)
            job_status.status = "completed"
            job_status.message = "Explanation generated successfully."
            job_status.result_id = explanation_response.explanation_id
            # Storing the full response in the job status for demo purposes (not scalable for real systems)
            job_status._full_response = explanation_response 
            logger.info(f"Async job {job_id} completed successfully. Result ID: {explanation_response.explanation_id}")
        except XAIError as e:
            logger.error(f"Error in async job {job_id} (request {request.request_id}): {e}", exc_info=True)
            job_status.status = "failed"
            job_status.message = f"Job failed: {e.message}"
        except Exception as e:
            logger.error(f"Unexpected error in async job {job_id} (request {request.request_id}): {e}", exc_info=True)
            job_status.status = "failed"
            job_status.message = f"Job failed due to an unexpected error: {str(e)}"
        finally:
            job_status.updated_at = datetime.utcnow()

    async def _process_explanation_request(self, request: ExplanationRequest) -> ExplanationResponse:
        """
        Core logic for processing an explanation request (used by both sync and async paths).
        """
        adapter_instance = self._get_model_adapter(request.model_identifier)
        if not adapter_instance:
            raise ConfigurationError(f"No suitable model adapter found for service {request.model_identifier.service_name} or model ID {request.model_identifier.model_id}.")

        try:
            model_details: ModelDetails = await adapter_instance.load_model_details()
        except Exception as e:
            logger.error(f"Failed to load model details for {request.model_identifier.model_id}: {e}", exc_info=True)
            raise ModelAccessError(f"Failed to load model details for {request.model_identifier.model_id}: {str(e)}")

        integrator_instance = self._get_xai_integrator(model_details, request.explanation_type)
        if not integrator_instance:
            raise MethodNotApplicableError(f"No suitable XAI integrator found for explanation type 	{request.explanation_type}	 and model type 	{model_details.model_type}	.")

        try:
            raw_explanation_data = await integrator_instance.generate_explanation(
                model_adapter=adapter_instance,
                instance_data=request.instance_data,
                explanation_params=request.explanation_parameters
            )
        except Exception as e:
            logger.error(f"Error during explanation generation by integrator: {e}", exc_info=True)
            raise ExplanationGenerationError(f"Core explanation generation failed: {str(e)}")

        nl_summary = self._generate_natural_language_summary(raw_explanation_data, request.explanation_type, model_details, request.instance_data)
        viz_hints = self._generate_visualization_hints(raw_explanation_data, request.explanation_type)
        
        provenance = ProvenanceInfo(
            xai_method_used=request.explanation_type,
            xai_method_parameters=request.explanation_parameters,
            model_version_explained=model_details.model_version
        )

        response = ExplanationResponse(
            request_id=request.request_id,
            model_identifier=request.model_identifier,
            explanation_type=request.explanation_type,
            explanation_data=raw_explanation_data,
            natural_language_summary=nl_summary,
            visualization_hints=viz_hints,
            provenance_info=provenance
        )
        logger.info(f"Successfully processed explanation request {request.request_id}.")
        return response

    def _get_model_adapter(self, model_identifier: ModelIdentifier) -> Optional[ModelAdapterInterface]:
        """Selects and initializes the appropriate model adapter based on model_identifier.service_name."""
        TargetAdapterClass = None
        if model_identifier.service_name == "machine_learning_service":
            TargetAdapterClass = MLServiceAdapter
        elif model_identifier.service_name == "llm_service":
            TargetAdapterClass = LLMServiceAdapter
        # Add more specific adapter selections if needed

        if TargetAdapterClass:
            try:
                return TargetAdapterClass(model_identifier=model_identifier.model_dump(), global_config=self.global_xai_config)
            except Exception as e:
                logger.error(f"Adapter {TargetAdapterClass.__name__} could not be initialized: {e}", exc_info=True)
                return None
        
        logger.warning(f"No specific adapter found for service_name: {model_identifier.service_name}. Trying generic registered adapters.")
        # Fallback to iterating through all registered adapters if no specific match
        for AdapterClass in self.adapters:
            try:
                # A more robust check would be adapter_class.can_handle(model_identifier)
                # For now, attempting initialization and catching errors is a basic check.
                adapter = AdapterClass(model_identifier=model_identifier.model_dump(), global_config=self.global_xai_config)
                # Add a check here if the adapter is suitable, e.g. by trying to load details or a specific method
                # This is still a simplification.
                logger.info(f"Trying generic adapter {AdapterClass.__name__} for {model_identifier.service_name}")
                return adapter # Return the first one that initializes without error (simplistic)
            except Exception as e:
                logger.debug(f"Generic adapter {AdapterClass.__name__} not suitable or failed to init: {e}")
        
        logger.error(f"No matching adapter found for model identifier: {model_identifier}")
        return None

    def _get_xai_integrator(self, model_details: ModelDetails, explanation_type: str) -> Optional[XAIMethodIntegratorInterface]:
        """Selects and initializes the appropriate XAI method integrator."""
        model_info_dict = {
            "model_type": model_details.model_type,
            "model_framework": model_details.model_framework
        }
        for IntegratorClass in self.integrators:
            try:
                integrator = IntegratorClass(global_config=self.global_xai_config)
                if integrator.can_explain(model_info=model_info_dict, explanation_type_requested=explanation_type):
                    logger.info(f"Selected XAI integrator: {IntegratorClass.__name__} for type {explanation_type}")
                    return integrator
            except Exception as e:
                 logger.warning(f"Integrator {IntegratorClass.__name__} could not be initialized or checked: {e}")
        logger.error(f"No matching integrator found for explanation type 	{explanation_type}	 and model details: {model_details}")
        return None

    def _generate_natural_language_summary(self, raw_data: Dict, explanation_type: str, model_details: ModelDetails, instance_data: Optional[Dict]) -> Optional[str]:
        """Generates a basic natural language summary. Placeholder."""
        try:
            if explanation_type == "shap_feature_importance" and isinstance(raw_data, dict) and raw_data.get("type") == "feature_importance":
                importances = raw_data.get("importances", [])
                if importances:
                    top_feature = importances[0]["feature_name"]
                    return f"For the {model_details.model_type} model 	{model_details.model_id}	, the most influential feature globally is 	{top_feature}	 according to SHAP analysis."
            elif explanation_type == "shap_instance_explanation" and isinstance(raw_data, dict) and "values" in raw_data:
                # This is very simplistic. Real summary would need feature names and be more descriptive.
                return f"SHAP instance explanation generated for model 	{model_details.model_id}	. Key contributing factors are detailed in explanation_data."
        except Exception as e:
            logger.error(f"Error generating NL summary: {e}", exc_info=True)
        return f"Explanation of type 	{explanation_type}	 generated for model 	{model_details.model_id}	. Raw data available in 	explanation_data	."

    def _generate_visualization_hints(self, raw_data: Dict, explanation_type: str) -> Optional[Dict]:
        """Generates hints for visualization. Placeholder."""
        try:
            if explanation_type == "shap_feature_importance" and isinstance(raw_data, dict) and raw_data.get("type") == "feature_importance":
                return {"type": "bar_chart", "title": "Global Feature Importance (SHAP)", "data_keys": {"x": "feature_name", "y": "importance_score"}, "data_source": "explanation_data.importances"}
            elif explanation_type == "shap_instance_explanation" and isinstance(raw_data, dict) and "values" in raw_data:
                # Waterfall plots are common for SHAP instance explanations
                return {"type": "waterfall_plot", "title": "Local Instance Explanation (SHAP)", "data_keys": {"values": "values", "base_value": "expected_value", "feature_names": "(from_metadata)"}, "data_source": "explanation_data"}
        except Exception as e:
            logger.error(f"Error generating viz hints: {e}", exc_info=True)
        return None

    def register_integrator(self, integrator_class: Type[XAIMethodIntegratorInterface]):
        if integrator_class not in self.integrators:
            self.integrators.append(integrator_class)
            logger.info(f"Registered XAI integrator: {integrator_class.__name__}")

    def register_adapter(self, adapter_class: Type[ModelAdapterInterface]):
        if adapter_class not in self.adapters:
            self.adapters.append(adapter_class)
            logger.info(f"Registered model adapter: {adapter_class.__name__}")


