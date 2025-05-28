# Pydantic Models for Machine Learning Service APIs

from typing import Dict, Any, Optional, List, Literal, Union
from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class DataSourceConfig(BaseModel):
    path: str = Field(..., description="Path to the data source, e.g., S3 URI, DB table name, local path.")
    type: Literal["csv", "parquet", "json", "database_table", "data_lake_query"] = Field(..., description="Type of the data source.")
    connection_params: Optional[Dict[str, Any]] = Field(None, description="Connection parameters for database or other remote sources.")
    version: Optional[str] = Field(None, description="Version of the dataset, if applicable.")
    feature_columns: Optional[List[str]] = Field(None, description="List of feature column names to be used.")
    target_column: Optional[str] = Field(None, description="Name of the target variable column.")

class AlgorithmConfig(BaseModel):
    name: str = Field(..., description="Name of the algorithm, e.g., RandomForestClassifier, XGBoostRegressor.")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Hyperparameters for the algorithm.")
    framework: Literal["scikit-learn", "xgboost", "lightgbm", "tensorflow", "pytorch"] = Field(..., description="ML framework to be used.")

class HyperparameterTuningConfig(BaseModel):
    method: Literal["grid_search", "random_search", "bayesian_optimization"] = Field(..., description="Hyperparameter tuning method.")
    param_grid: Dict[str, Union[List[Any], Dict[str, Any]]] = Field(..., description="Parameter grid or distributions for tuning.")
    scoring_metric: str = Field(..., description="Metric to optimize during tuning, e.g., accuracy, f1, roc_auc, neg_mean_squared_error.")
    cv_folds: int = Field(default=5, description="Number of cross-validation folds.")
    n_trials: Optional[int] = Field(None, description="Number of trials for random search or Bayesian optimization.")

class ResourceConfig(BaseModel):
    cpu_request: Optional[str] = Field(None, description="CPU resources to request, e.g., '2' for 2 cores.")
    memory_request: Optional[str] = Field(None, description="Memory to request, e.g., '4Gi'.")
    gpu_request: Optional[str] = Field(None, description="GPU resources to request, e.g., '1', 'nvidia.com/gpu: 1'.")

class TrainingJobRequest(BaseModel):
    model_name: str = Field(..., description="User-defined name for the model being trained.")
    model_version: Optional[str] = Field(default="1.0.0", description="Version for the trained model.")
    data_source_config: DataSourceConfig
    algorithm_config: AlgorithmConfig
    hyperparameter_tuning_config: Optional[HyperparameterTuningConfig] = None
    resource_config: Optional[ResourceConfig] = None
    experiment_name: Optional[str] = Field(None, description="Name of the experiment for tracking (e.g., in MLflow).")
    tags: Optional[Dict[str, str]] = Field(default_factory=dict, description="Tags for organizing and filtering jobs/models.")

class TrainingJobStatusResponse(BaseModel):
    job_id: UUID = Field(default_factory=uuid4, description="Unique identifier for the training job.")
    model_name: str
    model_version: str
    status: Literal["pending", "running", "completed", "failed", "cancelled"] = Field(..., description="Current status of the training job.")
    message: Optional[str] = Field(None, description="Additional information or error message.")
    created_at: str # Using str for datetime for simplicity, consider datetime objects
    updated_at: Optional[str] = None
    progress: Optional[float] = Field(None, ge=0, le=100, description="Training progress percentage.")
    metrics: Optional[Dict[str, Any]] = Field(None, description="Key metrics from the training process.")
    artifacts_location: Optional[str] = Field(None, description="Location where trained model artifacts are stored.")
    logs_location: Optional[str] = Field(None, description="Location of training logs.")

class EvaluationJobRequest(BaseModel):
    model_uri: str = Field(..., description="URI or ID of the trained model to be evaluated (e.g., MLflow run ID, path in artifact store).")
    data_source_config: DataSourceConfig
    metrics_to_compute: List[str] = Field(..., description="List of evaluation metrics to calculate.")
    evaluation_slices_config: Optional[Dict[str, str]] = Field(None, description="Configuration for evaluating on specific data slices/segments, e.g., {'gender': 'female'}.")
    experiment_name: Optional[str] = Field(None, description="Name of the experiment for tracking evaluation.")
    tags: Optional[Dict[str, str]] = Field(default_factory=dict)

class EvaluationJobStatusResponse(BaseModel):
    job_id: UUID = Field(default_factory=uuid4, description="Unique identifier for the evaluation job.")
    model_uri: str
    status: Literal["pending", "running", "completed", "failed"] = Field(..., description="Current status of the evaluation job.")
    message: Optional[str] = Field(None)
    created_at: str
    updated_at: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = Field(None, description="Calculated evaluation metrics.")
    report_location: Optional[str] = Field(None, description="Location of the generated evaluation report.")
    visualizations_location: Optional[str] = Field(None, description="Location of any generated visualizations.")

class DeploymentTargetConfig(BaseModel):
    type: Literal["api_service", "batch_inference_job", "edge_device"] = Field(..., description="Type of deployment target.")
    serving_image: Optional[str] = Field(None, description="Docker image to use for serving (for API/containerized deployments).")
    replicas: Optional[int] = Field(default=1, description="Number of replicas for API services.")
    port: Optional[int] = Field(default=8080, description="Port for the API service.")
    instance_type: Optional[str] = Field(None, description="Compute instance type for the deployment.")
    # Add other target-specific configs as needed

class DeploymentRequest(BaseModel):
    model_uri: str = Field(..., description="URI or ID of the trained model to be deployed.")
    deployment_name: str = Field(..., description="Unique name for this deployment.")
    deployment_target_config: DeploymentTargetConfig
    resource_allocation: Optional[ResourceConfig] = None
    version_strategy: Literal["new", "update_existing"] = Field(default="new", description="Strategy for versioning the deployment.")
    tags: Optional[Dict[str, str]] = Field(default_factory=dict)

class DeploymentStatusResponse(BaseModel):
    deployment_id: UUID = Field(default_factory=uuid4, description="Unique identifier for the deployment.")
    deployment_name: str
    model_uri: str
    status: Literal["creating", "active", "inactive", "updating", "failed", "deleting"] = Field(..., description="Current status of the deployment.")
    endpoint_url: Optional[str] = Field(None, description="URL of the deployed API endpoint, if applicable.")
    message: Optional[str] = Field(None)
    created_at: str
    updated_at: Optional[str] = None
    deployed_model_version: Optional[str] = Field(None, description="Version of the model currently active in this deployment.")

# Example of how these might be used in an orchestrator or main service file
# (This part is for illustration and would not be in the schemas file itself)

# class MachineLearningService:
#     async def train_model(self, request: TrainingJobRequest) -> TrainingJobStatusResponse:
#         # ... logic to initiate training ...
#         pass

#     async def get_training_job_status(self, job_id: UUID) -> TrainingJobStatusResponse:
#         # ... logic to get training job status ...
#         pass

#     async def evaluate_model(self, request: EvaluationJobRequest) -> EvaluationJobStatusResponse:
#         # ... logic to initiate evaluation ...
#         pass

#     async def get_evaluation_job_status(self, job_id: UUID) -> EvaluationJobStatusResponse:
#         # ... logic to get evaluation job status ...
#         pass

#     async def deploy_model(self, request: DeploymentRequest) -> DeploymentStatusResponse:
#         # ... logic to initiate deployment ...
#         pass

#     async def get_deployment_status(self, deployment_id: UUID) -> DeploymentStatusResponse:
#         # ... logic to get deployment status ...
#         pass

