# monitoring_exceptions.py

class MonitoringServiceError(Exception):
    """Base class for exceptions in the monitoring service."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details if details is not None else {}

    def __str__(self):
        return f"{self.__class__.__name__}: {self.message} {self.details if self.details else ''}"

class ConfigurationError(MonitoringServiceError):
    """Raised when there is an issue with monitoring configuration."""
    pass

class DataAccessError(MonitoringServiceError):
    """Raised when there is an issue accessing data required for monitoring."""
    pass

class MetricCalculationError(MonitoringServiceError):
    """Raised when an error occurs during metric calculation."""
    pass

class DriftDetectionError(MonitoringServiceError):
    """Raised when an error occurs during drift detection."""
    pass

class AlertingError(MonitoringServiceError):
    """Raised when an error occurs in the alerting sub-service."""
    pass

class StorageInterfaceError(MonitoringServiceError):
    """Raised for errors related to the storage interface or adapters."""
    pass

class ResourceNotFoundError(MonitoringServiceError):
    """Raised when a requested resource (e.g., config, report) is not found."""
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(message=f"{resource_type} with ID '{resource_id}' not found.")
        self.resource_type = resource_type
        self.resource_id = resource_id

class InvalidInputError(MonitoringServiceError):
    """Raised when invalid input is provided to a service method."""
    pass

