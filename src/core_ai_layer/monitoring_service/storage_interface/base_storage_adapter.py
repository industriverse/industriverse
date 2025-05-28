# base_storage_adapter.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..monitoring_schemas import (
    TimeSeriesDataPoint,
    DriftReport,
    ModelPerformanceReport,
    AlertEvent,
    MonitoringConfiguration
)
from ..monitoring_exceptions import StorageInterfaceError, ResourceNotFoundError

class StorageAdapterInterface(ABC):
    """Interface for all storage adapters within the monitoring service."""

    @abstractmethod
    async def save_time_series_metrics(self, metrics: List[TimeSeriesDataPoint]) -> None:
        """Saves a list of time-series metric data points."""
        pass

    @abstractmethod
    async def get_time_series_metrics(
        self, 
        metric_name: str, 
        start_time: datetime, 
        end_time: datetime, 
        tags: Optional[Dict[str, str]] = None
    ) -> List[TimeSeriesDataPoint]:
        """Retrieves time-series metric data points for a given metric and time range."""
        pass

    @abstractmethod
    async def save_drift_report(self, report: DriftReport) -> None:
        """Saves a data drift report."""
        pass

    @abstractmethod
    async def get_drift_report(self, report_id: str) -> Optional[DriftReport]:
        """Retrieves a data drift report by its ID."""
        pass

    @abstractmethod
    async def list_drift_reports(
        self, 
        model_id: Optional[str] = None, 
        config_id: Optional[str] = None, 
        limit: int = 100, 
        offset: int = 0
    ) -> List[DriftReport]:
        """Lists data drift reports, optionally filtered by model or config ID."""
        pass

    @abstractmethod
    async def save_performance_report(self, report: ModelPerformanceReport) -> None:
        """Saves a model performance report."""
        pass

    @abstractmethod
    async def get_performance_report(self, report_id: str) -> Optional[ModelPerformanceReport]:
        """Retrieves a model performance report by its ID."""
        pass

    @abstractmethod
    async def list_performance_reports(
        self, 
        model_id: Optional[str] = None, 
        config_id: Optional[str] = None, 
        limit: int = 100, 
        offset: int = 0
    ) -> List[ModelPerformanceReport]:
        """Lists model performance reports, optionally filtered by model or config ID."""
        pass

    @abstractmethod
    async def log_alert_event(self, alert: AlertEvent) -> None:
        """Logs an alert event."""
        pass

    @abstractmethod
    async def get_alert_event(self, alert_id: str) -> Optional[AlertEvent]:
        """Retrieves an alert event by its ID."""
        pass

    @abstractmethod
    async def list_alert_events(
        self, 
        model_id: Optional[str] = None, 
        config_id: Optional[str] = None, 
        severity: Optional[str] = None,
        limit: int = 100, 
        offset: int = 0
    ) -> List[AlertEvent]:
        """Lists alert events, with optional filters."""
        pass

    @abstractmethod
    async def save_monitoring_configuration(self, config: MonitoringConfiguration) -> None:
        """Saves a monitoring configuration."""
        pass

    @abstractmethod
    async def get_monitoring_configuration(self, config_id: str) -> Optional[MonitoringConfiguration]:
        """Retrieves a monitoring configuration by its ID."""
        pass

    @abstractmethod
    async def list_monitoring_configurations(
        self, 
        model_id: Optional[str] = None, 
        is_active: Optional[bool] = None,
        limit: int = 100, 
        offset: int = 0
    ) -> List[MonitoringConfiguration]:
        """Lists monitoring configurations, with optional filters."""
        pass

    @abstractmethod
    async def delete_monitoring_configuration(self, config_id: str) -> None:
        """Deletes a monitoring configuration by its ID."""
        pass

class BaseStorageAdapter(StorageAdapterInterface):
    """
    A base implementation for storage adapters providing common error handling
    and placeholder methods. Specific adapters should inherit from this.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        # Initialize connection or resources here if needed

    async def save_time_series_metrics(self, metrics: List[TimeSeriesDataPoint]) -> None:
        # Placeholder implementation
        # In a real adapter, this would interact with a time-series database (e.g., InfluxDB, Prometheus)
        # For demonstration, we can log or store in memory (not for production)
        print(f"[BaseStorageAdapter] Saving {len(metrics)} time-series metrics (placeholder).")
        if not metrics:
            return
        # Example: self._write_to_tsdb(metrics)
        pass

    async def get_time_series_metrics(
        self, 
        metric_name: str, 
        start_time: datetime, 
        end_time: datetime, 
        tags: Optional[Dict[str, str]] = None
    ) -> List[TimeSeriesDataPoint]:
        print(f"[BaseStorageAdapter] Getting time-series metrics for 	{metric_name}	 (placeholder).")
        # Example: return self._query_tsdb(metric_name, start_time, end_time, tags)
        return []

    async def save_drift_report(self, report: DriftReport) -> None:
        print(f"[BaseStorageAdapter] Saving drift report 	{report.report_id}	 (placeholder).")
        # Example: self._write_to_metadata_store("drift_reports", report.report_id, report.model_dump())
        pass

    async def get_drift_report(self, report_id: str) -> Optional[DriftReport]:
        print(f"[BaseStorageAdapter] Getting drift report 	{report_id}	 (placeholder).")
        # data = self._read_from_metadata_store("drift_reports", report_id)
        # return DriftReport(**data) if data else None
        return None

    async def list_drift_reports(
        self, 
        model_id: Optional[str] = None, 
        config_id: Optional[str] = None, 
        limit: int = 100, 
        offset: int = 0
    ) -> List[DriftReport]:
        print(f"[BaseStorageAdapter] Listing drift reports (placeholder).")
        return []

    async def save_performance_report(self, report: ModelPerformanceReport) -> None:
        print(f"[BaseStorageAdapter] Saving performance report 	{report.report_id}	 (placeholder).")
        pass

    async def get_performance_report(self, report_id: str) -> Optional[ModelPerformanceReport]:
        print(f"[BaseStorageAdapter] Getting performance report 	{report_id}	 (placeholder).")
        return None

    async def list_performance_reports(
        self, 
        model_id: Optional[str] = None, 
        config_id: Optional[str] = None, 
        limit: int = 100, 
        offset: int = 0
    ) -> List[ModelPerformanceReport]:
        print(f"[BaseStorageAdapter] Listing performance reports (placeholder).")
        return []

    async def log_alert_event(self, alert: AlertEvent) -> None:
        print(f"[BaseStorageAdapter] Logging alert event 	{alert.alert_id}	 (placeholder).")
        pass

    async def get_alert_event(self, alert_id: str) -> Optional[AlertEvent]:
        print(f"[BaseStorageAdapter] Getting alert event 	{alert_id}	 (placeholder).")
        return None

    async def list_alert_events(
        self, 
        model_id: Optional[str] = None, 
        config_id: Optional[str] = None, 
        severity: Optional[str] = None,
        limit: int = 100, 
        offset: int = 0
    ) -> List[AlertEvent]:
        print(f"[BaseStorageAdapter] Listing alert events (placeholder).")
        return []

    async def save_monitoring_configuration(self, config: MonitoringConfiguration) -> None:
        print(f"[BaseStorageAdapter] Saving monitoring configuration 	{config.config_id}	 (placeholder).")
        pass

    async def get_monitoring_configuration(self, config_id: str) -> Optional[MonitoringConfiguration]:
        print(f"[BaseStorageAdapter] Getting monitoring configuration 	{config_id}	 (placeholder).")
        # Example: Simulate not found for a specific ID for testing purposes
        if config_id == "non_existent_config_id":
            return None
        # Example: Return a dummy config for other IDs
        # This would be replaced by actual DB interaction
        # return MonitoringConfiguration(config_id=config_id, model_identifier=..., production_data_identifier=...)
        return None # Default to None for placeholder

    async def list_monitoring_configurations(
        self, 
        model_id: Optional[str] = None, 
        is_active: Optional[bool] = None,
        limit: int = 100, 
        offset: int = 0
    ) -> List[MonitoringConfiguration]:
        print(f"[BaseStorageAdapter] Listing monitoring configurations (placeholder).")
        return []

    async def delete_monitoring_configuration(self, config_id: str) -> None:
        print(f"[BaseStorageAdapter] Deleting monitoring configuration 	{config_id}	 (placeholder).")
        # Example: Check if exists, then delete. If not, raise ResourceNotFoundError.
        # if not await self.get_monitoring_configuration(config_id):
        #     raise ResourceNotFoundError("MonitoringConfiguration", config_id)
        pass

    # --- Helper methods for actual DB interaction (to be implemented in specific adapters) ---
    # def _write_to_tsdb(self, data):
    #     raise NotImplementedError
    # def _query_tsdb(self, ...):
    #     raise NotImplementedError
    # def _write_to_metadata_store(self, collection, doc_id, data):
    #     raise NotImplementedError
    # def _read_from_metadata_store(self, collection, doc_id):
    #     raise NotImplementedError

