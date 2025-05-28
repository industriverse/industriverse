# model_registry_client_interface.py

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List

class ModelRegistryClientInterface(ABC):
    """
    Abstract Base Class defining the interface for a Model Registry client (e.g., MLflow).
    Machine learning services will use this interface to log models, artifacts, metrics,
    and retrieve model information.
    """

    @abstractmethod
    async def log_model(
        self,
        model: Any,
        model_name: str,
        model_version: Optional[str] = None,
        experiment_name: Optional[str] = None,
        run_id: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
        signature: Optional[Any] = None, # Framework-specific model signature
        input_example: Optional[Any] = None # Example input for the model
    ) -> str:
        """
        Logs a trained model to the registry.

        Args:
            model: The trained model object (e.g., scikit-learn model, Keras model).
            model_name: The name to register the model under.
            model_version: (Optional) Specific version for the model.
            experiment_name: (Optional) Name of the experiment to log this run under.
            run_id: (Optional) Existing run ID if logging to an existing run.
            tags: (Optional) Tags to associate with the logged model/run.
            signature: (Optional) Model signature describing inputs and outputs.
            input_example: (Optional) An example of input data the model expects.

        Returns:
            A URI or identifier for the logged model in the registry.
        """
        raise NotImplementedError

    @abstractmethod
    async def load_model(self, model_uri: str) -> Any:
        """
        Loads a model from the specified URI in the registry.

        Args:
            model_uri: The URI of the model to load (e.g., 'models:/MyModel/Production', 'runs:/<run_id>/model').

        Returns:
            The loaded model object.
        """
        raise NotImplementedError

    @abstractmethod
    async def log_metrics(self, run_id: str, metrics: Dict[str, float], step: Optional[int] = None):
        """
        Logs metrics for a given run.

        Args:
            run_id: The ID of the run to log metrics for.
            metrics: A dictionary of metric names and values.
            step: (Optional) The step at which the metrics were recorded (for time-series metrics).
        """
        raise NotImplementedError

    @abstractmethod
    async def log_params(self, run_id: str, params: Dict[str, Any]):
        """
        Logs parameters for a given run.

        Args:
            run_id: The ID of the run to log parameters for.
            params: A dictionary of parameter names and values.
        """
        raise NotImplementedError

    @abstractmethod
    async def log_artifact(self, run_id: str, local_path: str, artifact_path: Optional[str] = None):
        """
        Logs a local file or directory as an artifact for a given run.

        Args:
            run_id: The ID of the run.
            local_path: Path to the local file or directory to log.
            artifact_path: (Optional) Destination path within the run's artifact URI.
        """
        raise NotImplementedError

    @abstractmethod
    async def download_artifacts(
        self, 
        run_id: Optional[str] = None, 
        model_uri: Optional[str] = None, 
        artifact_path: Optional[str] = None, 
        dst_path: Optional[str] = None
    ) -> str:
        """
        Downloads artifacts associated with a run or a specific model URI.

        Args:
            run_id: (Optional) The ID of the run if downloading run-level artifacts.
            model_uri: (Optional) The URI of the model if downloading model-specific artifacts.
            artifact_path: (Optional) Relative path of the artifact to download. If None, downloads all artifacts.
            dst_path: (Optional) Local directory to download artifacts to. If None, creates a temporary directory.

        Returns:
            Path to the downloaded artifacts on the local filesystem.
        """
        raise NotImplementedError

    @abstractmethod
    async def create_experiment(self, name: str, tags: Optional[Dict[str, str]] = None) -> str:
        """
        Creates a new experiment in the registry.

        Args:
            name: The name of the experiment.
            tags: (Optional) Tags to associate with the experiment.

        Returns:
            The ID of the newly created experiment.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_experiment_by_name(self, name: str) -> Optional[Any]:
        """
        Retrieves an experiment by its name.

        Args:
            name: The name of the experiment.

        Returns:
            An object representing the experiment, or None if not found.
        """
        raise NotImplementedError

    @abstractmethod
    async def start_run(self, experiment_id: Optional[str] = None, run_name: Optional[str] = None, tags: Optional[Dict[str, Any]] = None) -> Any:
        """
        Starts a new run within an experiment.

        Args:
            experiment_id: (Optional) The ID of the experiment to create the run in. Uses default if None.
            run_name: (Optional) Name for the run.
            tags: (Optional) Tags for the run.

        Returns:
            An object representing the active run context.
        """
        raise NotImplementedError

    @abstractmethod
    async def end_run(self, run_id: str, status: str = "FINISHED"):
        """
        Ends an active run.

        Args:
            run_id: The ID of the run to end.
            status: (Optional) Final status of the run (e.g., "FINISHED", "FAILED", "KILLED").
        """
        raise NotImplementedError

# Example concrete implementation (placeholder for MLflow)
# import mlflow
# class MLflowClient(ModelRegistryClientInterface):
#     async def log_model(self, model: Any, model_name: str, ...) -> str:
#         mlflow.sklearn.log_model(model, artifact_path=model_name, registered_model_name=model_name)
#         return f"models:/{model_name}/latest" # Simplified
    # ... other methods

