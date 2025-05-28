# ml_service_exceptions.py

class MachineLearningServiceError(Exception):
    """Base class for exceptions in the Machine Learning Service."""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.status_code = status_code
        self.message = message

class ConfigurationError(MachineLearningServiceError):
    """Exception raised for errors in configuration."""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)

class ResourceNotFoundError(MachineLearningServiceError):
    """Exception raised when a requested resource is not found."""
    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type} with ID acility_id_placeholder{resource_id}acility_id_placeholder not found."
        super().__init__(message, status_code=404)

class TrainingJobError(MachineLearningServiceError):
    """Exception raised for errors during a training job."""
    def __init__(self, job_id: str, message: str):
        full_message = f"Error in training job acility_id_placeholder{job_id}acility_id_placeholder: {message}"
        super().__init__(full_message)

class EvaluationJobError(MachineLearningServiceError):
    """Exception raised for errors during an evaluation job."""
    def __init__(self, job_id: str, message: str):
        full_message = f"Error in evaluation job acility_id_placeholder{job_id}acility_id_placeholder: {message}"
        super().__init__(full_message)

class DeploymentError(MachineLearningServiceError):
    """Exception raised for errors during model deployment."""
    def __init__(self, deployment_name: str, message: str):
        full_message = f"Error in deployment acility_id_placeholder{deployment_name}acility_id_placeholder: {message}"
        super().__init__(full_message)

class DataAccessError(MachineLearningServiceError):
    """Exception raised for errors accessing data from the Data Layer."""
    def __init__(self, message: str):
        super().__init__(f"Data access error: {message}", status_code=503)

class ModelRegistryError(MachineLearningServiceError):
    """Exception raised for errors interacting with the Model Registry."""
    def __init__(self, message: str):
        super().__init__(f"Model registry error: {message}", status_code=503)

class ExternalServiceError(MachineLearningServiceError):
    """Exception for errors from other external services like orchestrators."""
    def __init__(self, service_name: str, message: str):
        super().__init__(f"Error interacting with {service_name}: {message}", status_code=503)

