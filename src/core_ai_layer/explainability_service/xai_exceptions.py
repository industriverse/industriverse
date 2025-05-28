# xai_exceptions.py

class XAIError(Exception):
    """Base class for exceptions in the explainability_service."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details if details is not None else {}

    def __str__(self):
        return f"{self.__class__.__name__}: {self.message} (Details: {self.details})"

class ConfigurationError(XAIError):
    """Raised for configuration-related errors."""
    pass

class ModelAccessError(XAIError):
    """Raised when a model cannot be accessed or loaded."""
    pass

class DataAccessError(XAIError):
    """Raised when data required for explanation cannot be accessed."""
    pass

class MethodNotApplicableError(XAIError):
    """Raised when an XAI method is not applicable to a given model or data."""
    pass

class ExplanationGenerationError(XAIError):
    """Raised when an error occurs during the explanation generation process."""
    pass

class ResourceNotFoundError(XAIError):
    """Raised when a requested resource (e.g., a specific explanation job) is not found."""
    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type} with ID 	ron 	{resource_id} not found."
        super().__init__(message, details={"resource_type": resource_type, "resource_id": resource_id})

class InvalidInputError(XAIError):
    """Raised for invalid input provided to an explanation method or service."""
    pass

