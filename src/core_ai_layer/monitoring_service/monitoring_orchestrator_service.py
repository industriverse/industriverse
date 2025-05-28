# monitoring_orchestrator_service.py

import logging
import asyncio
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union

from .monitoring_schemas import (
    MonitoringConfiguration,
    ModelIdentifier,
    DriftReport,
    ModelPerformanceReport,
    AlertEvent,
    AlertSeverity,
    CreateMonitoringConfigRequest,
    MonitoringStatusResponse,
    ScheduleFrequency,
    DataSourceIdentifier, # Added for clarity
    ModelType # Added for clarity
)
from .monitoring_exceptions import (
    MonitoringServiceError,
    ConfigurationError,
    DataAccessError,
    ResourceNotFoundError,
    InvalidInputError,
    DriftDetectionError, # Added
    MetricCalculationError # Added
)
from .data_drift_detection_service import DataDriftDetectionService
from .model_performance_monitor import ModelPerformanceMonitor
from .alerting_service import AlertingService
from .storage_interface.base_storage_adapter import StorageAdapterInterface
from .monitoring_utils import get_data_from_data_layer_placeholder # Using the placeholder

# Conceptual clients for other services - these would be properly imported and implemented
class DataLayerClientPlaceholder:
    async def fetch_data_sample(self, data_identifier: DataSourceIdentifier, features: Optional[List[str]] = None, time_window_hours: Optional[int] = None) -> Dict[str, List[Any]]:
        logger.info(f"[DataLayerClientPlaceholder] Fetching production data sample for {data_identifier.source_name}")
        # Simulate fetching based on features or a generic sample
        return get_data_from_data_layer_placeholder(data_identifier.model_dump(), "production_sample", time_window_hours)

    async def fetch_baseline_characteristics(self, data_identifier: DataSourceIdentifier, features: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
        logger.info(f"[DataLayerClientPlaceholder] Fetching baseline characteristics for {data_identifier.source_name}")
        return get_data_from_data_layer_placeholder(data_identifier.model_dump(), "baseline_characteristics")

    async def fetch_ground_truth(self, data_identifier: DataSourceIdentifier, prediction_ids: Optional[List[str]] = None, time_window_hours: Optional[int] = None) -> List[Any]:
        logger.info(f"[DataLayerClientPlaceholder] Fetching ground truth for {data_identifier.source_name}")
        return get_data_from_data_layer_placeholder(data_identifier.model_dump(), "ground_truth")

class ModelServiceClientPlaceholder: # Generic placeholder for ML/LLM services
    async def get_predictions_for_monitoring(
        self, 
        model_identifier: ModelIdentifier, 
        data_identifier: Optional[DataSourceIdentifier] = None, # To specify which production data predictions are for
        time_window_hours: Optional[int] = None, 
        count: Optional[int] = None
    ) -> Dict[str, List[Any]]:
        logger.info(f"[ModelServiceClientPlaceholder] Fetching predictions for model {model_identifier.model_id}")
        # Returns a dict like {"predictions": [...], "prediction_probabilities": [...]} or just predictions
        # This is highly dependent on how the actual ML/LLM services expose this data
        num_samples = count or 100
        response_data: Dict[str, List[Any]] = {}
        if model_identifier.model_type == ModelType.CLASSIFICATION:
            response_data["predictions"] = list(np.random.randint(0, 2, num_samples))
            response_data["prediction_probabilities"] = list(np.random.rand(num_samples))
        elif model_identifier.model_type == ModelType.REGRESSION:
            response_data["predictions"] = list(np.random.rand(num_samples) * 10)
        elif model_identifier.model_type == ModelType.LLM_GENERATIVE:
            response_data["predictions"] = [f"Generated text sample {i}" for i in range(num_samples)]
        else:
            response_data["predictions"] = [None] * num_samples # Default
        return response_data

import numpy as np # For placeholder data generation

logger = logging.getLogger(__name__)

class MonitoringOrchestratorService:
    """
    Orchestrates monitoring activities including configuration management,
    job scheduling, data fetching, and invoking sub-services for drift detection,
    performance monitoring, and alerting.
    """

    def __init__(
        self,
        storage_adapter: StorageAdapterInterface,
        drift_detector: DataDriftDetectionService,
        performance_monitor: ModelPerformanceMonitor,
        alerter: AlertingService,
        data_layer_client: Optional[DataLayerClientPlaceholder] = None,
        model_service_client: Optional[ModelServiceClientPlaceholder] = None, # Generic client
        global_config: Optional[Dict[str, Any]] = None
    ):
        self.storage_adapter = storage_adapter
        self.drift_detector = drift_detector
        self.performance_monitor = performance_monitor
        self.alerter = alerter
        self.data_layer_client = data_layer_client or DataLayerClientPlaceholder()
        self.model_service_client = model_service_client or ModelServiceClientPlaceholder()
        self.global_config = global_config or {}
        self.active_monitoring_jobs: Dict[str, asyncio.Task] = {} # config_id to task
        logger.info("MonitoringOrchestratorService initialized with integration placeholders.")

    async def create_monitoring_configuration(self, request: CreateMonitoringConfigRequest) -> MonitoringConfiguration:
        logger.info(f"Creating monitoring configuration for model {request.model_identifier.model_id}")
        if not request.production_data_identifier:
            raise InvalidInputError("Production data identifier is required.")
        
        new_config = MonitoringConfiguration(
            model_identifier=request.model_identifier,
            description=request.description,
            features_to_monitor=request.features_to_monitor,
            performance_metrics_to_track=request.performance_metrics_to_track,
            baseline_data_identifier=request.baseline_data_identifier,
            production_data_identifier=request.production_data_identifier,
            ground_truth_identifier=request.ground_truth_identifier,
            drift_detection_schedule=request.drift_detection_schedule,
            performance_monitoring_schedule=request.performance_monitoring_schedule,
            alert_recipients=request.alert_recipients,
            custom_monitoring_params=request.custom_monitoring_params
        )
        await self.storage_adapter.save_monitoring_configuration(new_config)
        logger.info(f"Monitoring configuration {new_config.config_id} created successfully.")
        self._schedule_monitoring_job_if_needed(new_config)
        return new_config

    async def get_monitoring_configuration(self, config_id: str) -> MonitoringConfiguration:
        config = await self.storage_adapter.get_monitoring_configuration(config_id)
        if not config:
            raise ResourceNotFoundError("MonitoringConfiguration", config_id)
        return config

    async def update_monitoring_configuration(self, config_id: str, updates: Dict[str, Any]) -> MonitoringConfiguration:
        logger.info(f"Updating monitoring configuration {config_id}")
        current_config = await self.get_monitoring_configuration(config_id)
        
        updated_data = current_config.model_dump(exclude_unset=True)
        updated_data.update(updates)
        updated_data["updated_at"] = datetime.utcnow()
        
        try:
            updated_config = MonitoringConfiguration(**updated_data)
        except Exception as e:
            raise InvalidInputError(f"Invalid update data: {e}")

        await self.storage_adapter.save_monitoring_configuration(updated_config)
        logger.info(f"Monitoring configuration {updated_config.config_id} updated.")
        self._cancel_monitoring_job(str(updated_config.config_id))
        if updated_config.is_active:
            self._schedule_monitoring_job_if_needed(updated_config)
        return updated_config

    async def delete_monitoring_configuration(self, config_id: str) -> None:
        logger.info(f"Deleting monitoring configuration {config_id}")
        await self.storage_adapter.delete_monitoring_configuration(config_id)
        self._cancel_monitoring_job(config_id)
        logger.info(f"Monitoring configuration {config_id} deleted.")

    async def list_monitoring_configurations(self, model_id: Optional[str] = None, is_active: Optional[bool] = None) -> List[MonitoringConfiguration]:
        return await self.storage_adapter.list_monitoring_configurations(model_id=model_id, is_active=is_active)

    def _schedule_monitoring_job_if_needed(self, config: MonitoringConfiguration):
        config_id_str = str(config.config_id)
        if not config.is_active:
            logger.info(f"Configuration {config_id_str} is not active. Skipping job scheduling.")
            self._cancel_monitoring_job(config_id_str)
            return

        schedule = config.drift_detection_schedule or config.performance_monitoring_schedule
        if schedule:
            if config_id_str in self.active_monitoring_jobs:
                logger.warning(f"Job for config {config_id_str} already scheduled. Cancelling and rescheduling.")
                self._cancel_monitoring_job(config_id_str)
            
            logger.info(f"Scheduling monitoring job for config {config_id_str} with frequency {schedule.frequency}.")
            task = asyncio.create_task(self._periodic_monitoring_task(config))
            self.active_monitoring_jobs[config_id_str] = task
        else:
            logger.info(f"No schedule defined for config {config_id_str}. No job scheduled.")

    def _cancel_monitoring_job(self, config_id_str: str):
        if config_id_str in self.active_monitoring_jobs:
            task = self.active_monitoring_jobs.pop(config_id_str)
            if not task.done():
                task.cancel()
                logger.info(f"Cancelled monitoring job for config {config_id_str}.")
            else:
                logger.info(f"Monitoring job for config {config_id_str} was already done.")

    async def _periodic_monitoring_task(self, config: MonitoringConfiguration):
        config_id_str = str(config.config_id)
        schedule = config.drift_detection_schedule or config.performance_monitoring_schedule
        if not schedule: return

        interval_seconds = 3600 
        if schedule.frequency == ScheduleFrequency.DAILY: interval_seconds = 24 * 3600
        elif schedule.frequency == ScheduleFrequency.WEEKLY: interval_seconds = 7 * 24 * 3600
        elif schedule.frequency == ScheduleFrequency.CONTINUOUS: interval_seconds = 60 # Example: check every minute for continuous

        logger.info(f"Monitoring task started for config {config_id_str}, interval: {interval_seconds}s.")
        while True:
            try:
                current_config = await self.get_monitoring_configuration(config_id_str)
                if not current_config.is_active:
                    logger.info(f"Monitoring config {config_id_str} is no longer active. Stopping task.")
                    break
                
                await self.run_monitoring_checks(current_config)
                await asyncio.sleep(interval_seconds)
            except asyncio.CancelledError:
                logger.info(f"Monitoring task for config {config_id_str} was cancelled.")
                break
            except ResourceNotFoundError:
                logger.warning(f"Monitoring config {config_id_str} not found. Stopping task.")
                break
            except Exception as e:
                logger.error(f"Error in periodic monitoring task for config {config_id_str}: {e}", exc_info=True)
                await asyncio.sleep(600)

    async def run_monitoring_checks(self, config: MonitoringConfiguration) -> None:
        logger.info(f"Running monitoring checks for config {config.config_id} on model {config.model_identifier.model_id}")
        alerts_to_dispatch: List[AlertEvent] = []

        production_data_sample: Dict[str, List[Any]] = {}
        baseline_characteristics: Dict[str, Dict[str, Any]] = {}
        ground_truth_sample: List[Any] = []
        predictions_data: Dict[str, List[Any]] = {"predictions": []}

        try:
            # Fetch production data for drift detection
            if config.features_to_monitor and config.production_data_identifier:
                logger.info(f"Fetching production data sample for drift check: {config.production_data_identifier.source_name}")
                production_data_sample = await self.data_layer_client.fetch_data_sample(
                    config.production_data_identifier,
                    features=[fc.feature_name for fc in config.features_to_monitor if fc.monitor_for_drift]
                )
            if config.baseline_data_identifier and config.features_to_monitor:
                logger.info(f"Fetching baseline characteristics: {config.baseline_data_identifier.source_name}")
                baseline_characteristics = await self.data_layer_client.fetch_baseline_characteristics(
                    config.baseline_data_identifier,
                    features=[fc.feature_name for fc in config.features_to_monitor if fc.monitor_for_drift]
                )

            # Fetch predictions and ground truth for performance monitoring
            if config.performance_metrics_to_track:
                logger.info(f"Fetching predictions for model {config.model_identifier.model_id}")
                predictions_data = await self.model_service_client.get_predictions_for_monitoring(
                    config.model_identifier,
                    data_identifier=config.production_data_identifier # To link predictions to the data they were made on
                )
                if config.ground_truth_identifier:
                    logger.info(f"Fetching ground truth: {config.ground_truth_identifier.source_name}")
                    # Assuming predictions have IDs that can be used to fetch corresponding ground truth
                    # This part is highly dependent on actual data flow and availability
                    ground_truth_sample = await self.data_layer_client.fetch_ground_truth(config.ground_truth_identifier)
                    if len(predictions_data.get("predictions",[])) != len(ground_truth_sample) and ground_truth_sample:
                        logger.warning("Mismatch between predictions count and ground truth count. Performance metrics might be inaccurate.")
                        # Potentially truncate to the shorter length or handle error

        except DataAccessError as e:
            logger.error(f"Data access error during monitoring checks for {config.config_id}: {e}")
            alert = AlertEvent(
                config_id=config.config_id, model_identifier=config.model_identifier, severity=AlertSeverity.CRITICAL,
                title="Monitoring Data Access Failed", description=f"Failed to access data for monitoring checks: {e.message}", details=e.details
            )
            alerts_to_dispatch.append(alert)
            if config.alert_recipients: await self.alerter.dispatch_alert(alert, config.alert_recipients)
            return
        except Exception as e: # Catch other unexpected errors during data fetching
            logger.error(f"Unexpected error fetching data for {config.config_id}: {e}", exc_info=True)
            alert = AlertEvent(
                config_id=config.config_id, model_identifier=config.model_identifier, severity=AlertSeverity.CRITICAL,
                title="Monitoring Data Fetching Error", description=f"Unexpected error fetching data: {str(e)}"
            )
            alerts_to_dispatch.append(alert)
            if config.alert_recipients: await self.alerter.dispatch_alert(alert, config.alert_recipients)
            return

        # 1. Data Drift Detection
        if config.features_to_monitor and production_data_sample and baseline_characteristics:
            try:
                drift_report = await self.drift_detector.check_data_drift(
                    model_identifier=config.model_identifier, config_id=str(config.config_id),
                    production_data=production_data_sample, baseline_data_characteristics=baseline_characteristics,
                    feature_configs=config.features_to_monitor
                )
                await self.storage_adapter.save_drift_report(drift_report)
                logger.info(f"Drift report {drift_report.report_id} saved for config {config.config_id}.")
                if any(f_res.drift_detected for f_res in drift_report.feature_drift_results):
                    alerts_to_dispatch.append(AlertEvent(
                        config_id=config.config_id, model_identifier=config.model_identifier, severity=AlertSeverity.WARNING,
                        title=f"Data Drift Detected for Model {config.model_identifier.model_id}",
                        description=f"Significant data drift detected. Overall status: {drift_report.overall_drift_status}. Summary: {drift_report.summary}",
                        details=drift_report.model_dump()
                    ))
            except (DriftDetectionError, InvalidInputError) as e:
                logger.error(f"Drift detection error for {config.config_id}: {e}")
                alerts_to_dispatch.append(AlertEvent(
                    config_id=config.config_id, model_identifier=config.model_identifier, severity=AlertSeverity.CRITICAL,
                    title="Drift Detection Failed", description=str(e), details=getattr(e, "details", None)
                ))

        # 2. Model Performance Monitoring
        if config.performance_metrics_to_track and predictions_data.get("predictions") and ground_truth_sample:
            try:
                perf_report = await self.performance_monitor.calculate_performance_metrics(
                    model_identifier=config.model_identifier, config_id=str(config.config_id),
                    predictions=predictions_data["predictions"],
                    ground_truth=ground_truth_sample,
                    metric_configs=config.performance_metrics_to_track,
                    prediction_probabilities=predictions_data.get("prediction_probabilities")
                )
                await self.storage_adapter.save_performance_report(perf_report)
                logger.info(f"Performance report {perf_report.report_id} saved for config {config.config_id}.")
                for metric_val in perf_report.metrics:
                    for m_conf in config.performance_metrics_to_track:
                        if m_conf.metric_name == metric_val.metric_name:
                            alert_sev = None
                            # Assuming lower value is worse for performance metrics for simplicity
                            if m_conf.threshold_critical is not None and metric_val.value < m_conf.threshold_critical:
                                alert_sev = AlertSeverity.CRITICAL
                            elif m_conf.threshold_warning is not None and metric_val.value < m_conf.threshold_warning:
                                alert_sev = AlertSeverity.WARNING
                            if alert_sev:
                                alerts_to_dispatch.append(AlertEvent(
                                    config_id=config.config_id, model_identifier=config.model_identifier, severity=alert_sev,
                                    title=f"Model Performance Alert: {metric_val.metric_name}",
                                    description=f"Metric {metric_val.metric_name} value {metric_val.value:.4f} crossed threshold.",
                                    details=metric_val.model_dump()
                                ))
                            break
            except (MetricCalculationError, InvalidInputError) as e:
                logger.error(f"Performance calculation error for {config.config_id}: {e}")
                alerts_to_dispatch.append(AlertEvent(
                    config_id=config.config_id, model_identifier=config.model_identifier, severity=AlertSeverity.CRITICAL,
                    title="Performance Calculation Failed", description=str(e), details=getattr(e, "details", None)
                ))

        # 3. Dispatch Alerts
        if alerts_to_dispatch and config.alert_recipients:
            for alert_event in alerts_to_dispatch:
                await self.storage_adapter.log_alert_event(alert_event)
                await self.alerter.dispatch_alert(alert_event, config.alert_recipients)
        elif alerts_to_dispatch:
            logger.warning(f"Alerts generated for config {config.config_id} but no recipients configured. Logging alerts locally.")
            for alert_event in alerts_to_dispatch:
                 await self.storage_adapter.log_alert_event(alert_event)

        logger.info(f"Monitoring checks completed for config {config.config_id}.")

    async def get_monitoring_status(self, model_id: str, config_id: Optional[str] = None) -> MonitoringStatusResponse:
        configs = await self.list_monitoring_configurations(model_id=model_id)
        if not configs:
            raise ResourceNotFoundError("ModelMonitoringConfig (any for model_id)", model_id)
        
        target_config = None
        if config_id:
            for cfg in configs:
                if str(cfg.config_id) == config_id: target_config = cfg; break
            if not target_config: raise ResourceNotFoundError("MonitoringConfiguration", config_id)
        else:
            target_config = next((c for c in configs if c.is_active), configs[0])

        # Simplified: In reality, query storage for latest reports and active alerts
        last_drift_reports = await self.storage_adapter.list_drift_reports(config_id=str(target_config.config_id), limit=1)
        last_perf_reports = await self.storage_adapter.list_performance_reports(config_id=str(target_config.config_id), limit=1)
        # Assuming alert status can be queried, or count new/acknowledged
        active_alerts = await self.storage_adapter.list_alert_events(config_id=str(target_config.config_id), severity=AlertSeverity.CRITICAL, limit=5) # Example

        return MonitoringStatusResponse(
            model_identifier=target_config.model_identifier,
            last_drift_check = last_drift_reports[0].timestamp if last_drift_reports else None,
            last_drift_status = last_drift_reports[0].overall_drift_status if last_drift_reports else None,
            last_performance_check = last_perf_reports[0].timestamp if last_perf_reports else None,
            last_performance_summary = {m.metric_name: m.value for m in last_perf_reports[0].metrics} if last_perf_reports and last_perf_reports[0].metrics else None,
            active_alerts_count=len(active_alerts)
        )

    async def startup_scheduler(self):
        logger.info("MonitoringOrchestratorService: Starting up scheduler...")
        active_configs = await self.list_monitoring_configurations(is_active=True)
        for config in active_configs:
            self._schedule_monitoring_job_if_needed(config)
        logger.info(f"Scheduled {len(self.active_monitoring_jobs)} monitoring jobs.")

    async def shutdown_scheduler(self):
        logger.info("MonitoringOrchestratorService: Shutting down scheduler...")
        config_ids_to_cancel = list(self.active_monitoring_jobs.keys())
        for config_id_str in config_ids_to_cancel:
            self._cancel_monitoring_job(config_id_str)
        
        # Wait for tasks to actually finish cancelling
        # Gather tasks that are not None and not done
        tasks_to_await = [task for task in self.active_monitoring_jobs.values() if task and not task.done()]
        if tasks_to_await:
            await asyncio.gather(*tasks_to_await, return_exceptions=True)
        self.active_monitoring_jobs.clear()
        logger.info("All monitoring jobs shut down.")


