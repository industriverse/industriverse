# monitoring_schemas.py

import uuid
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional, Union

from pydantic import BaseModel, Field

# --- Enums ---

class ModelType(str, Enum):
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    LLM_GENERATIVE = "llm_generative"
    LLM_EMBEDDING = "llm_embedding"
    OTHER = "other"

class MetricType(str, Enum):
    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    AUC = "auc"
    RMSE = "rmse"
    MAE = "mae"
    R_SQUARED = "r_squared"
    PERPLEXITY = "perplexity"
    BLEU = "bleu"
    ROUGE_L = "rouge_l"
    CUSTOM = "custom"

class DriftType(str, Enum):
    COVARIATE_DRIFT = "covariate_drift"  # Drift in input features
    CONCEPT_DRIFT = "concept_drift"    # Change in relationship P(Y|X)
    LABEL_DRIFT = "label_drift"        # Drift in target variable distribution P(Y)
    PREDICTION_DRIFT = "prediction_drift" # Drift in model output distribution P(Y_hat)

class DriftDetectionMethod(str, Enum):
    KS_TEST = "kolmogorov_smirnov"
    PSI = "population_stability_index"
    CHI_SQUARED = "chi_squared"
    WASSERSTEIN = "wasserstein_distance"
    CUSTOM = "custom_method"

class AlertSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

class AlertChannel(str, Enum):
    EMAIL = "email"
    SLACK = "slack"
    PAGERDUTY = "pagerduty"
    MCP_A2A = "mcp_a2a_message"
    LOG = "log_only"

class ScheduleFrequency(str, Enum):
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CONTINUOUS = "continuous" # For streaming data if applicable

# --- Basic Identifiers and Common Schemas ---

class ModelIdentifier(BaseModel):
    model_id: str = Field(..., description="Unique identifier for the model being monitored.")
    model_version: Optional[str] = Field(None, description="Version of the model.")
    service_name: str = Field(..., description="Name of the service hosting the model (e.g., machine_learning_service, llm_service).")
    model_type: ModelType = Field(..., description="Type of the model (e.g., classification, llm_generative).")

class DataSourceIdentifier(BaseModel):
    source_name: str = Field(..., description="Name of the data source (e.g., specific table, data stream, dataset ID).")
    data_layer_service: str = Field(default="data_query_access_api", description="Service in Data Layer to query from.")

# --- Monitoring Configuration Schemas ---

class FeatureMonitoringConfig(BaseModel):
    feature_name: str = Field(..., description="Name of the feature to monitor.")
    monitor_for_drift: bool = Field(True, description="Whether to monitor this feature for drift.")
    drift_detection_methods: Optional[List[DriftDetectionMethod]] = Field(None, description="Specific drift detection methods for this feature.")
    custom_drift_params: Optional[Dict[str, Any]] = Field(None, description="Parameters for custom drift detection methods.")

class PerformanceMetricConfig(BaseModel):
    metric_name: MetricType = Field(..., description="Name of the performance metric to track.")
    threshold_warning: Optional[float] = Field(None, description="Warning threshold for this metric (e.g., if accuracy drops below this).")
    threshold_critical: Optional[float] = Field(None, description="Critical threshold for this metric.")
    custom_metric_params: Optional[Dict[str, Any]] = Field(None, description="Parameters if this is a custom metric.")

class AlertRecipientConfig(BaseModel):
    channel: AlertChannel = Field(..., description="Notification channel for the alert.")
    target: str = Field(..., description="Target for the notification (e.g., email address, Slack channel ID, MCP/A2A topic).")
    min_severity: AlertSeverity = Field(default=AlertSeverity.WARNING, description="Minimum severity to send to this recipient.")

class MonitoringJobSchedule(BaseModel):
    frequency: ScheduleFrequency = Field(..., description="How often the monitoring job should run.")
    cron_expression: Optional[str] = Field(None, description="Optional cron expression for custom scheduling.")
    # For continuous, other params might be batch_size, window_size etc.

class MonitoringConfiguration(BaseModel):
    config_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique identifier for this monitoring configuration.")
    model_identifier: ModelIdentifier
    description: Optional[str] = Field(None, description="Human-readable description of this configuration.")
    is_active: bool = Field(True, description="Whether this monitoring configuration is currently active.")

    features_to_monitor: Optional[List[FeatureMonitoringConfig]] = Field(None, description="Configuration for features to monitor for drift.")
    performance_metrics_to_track: Optional[List[PerformanceMetricConfig]] = Field(None, description="Configuration for performance metrics.")

    baseline_data_identifier: Optional[DataSourceIdentifier] = Field(None, description="Identifier for the baseline/reference dataset used for drift comparison.")
    production_data_identifier: DataSourceIdentifier = Field(..., description="Identifier for the production data stream/source to monitor.")
    ground_truth_identifier: Optional[DataSourceIdentifier] = Field(None, description="Identifier for the source of ground truth labels (for performance monitoring).")

    drift_detection_schedule: Optional[MonitoringJobSchedule] = Field(None, description="Schedule for data drift detection jobs.")
    performance_monitoring_schedule: Optional[MonitoringJobSchedule] = Field(None, description="Schedule for performance monitoring jobs.")

    alert_recipients: Optional[List[AlertRecipientConfig]] = Field(None, description="List of recipients for alerts generated from this configuration.")
    custom_monitoring_params: Optional[Dict[str, Any]] = Field(None, description="Additional custom parameters for this monitoring setup.")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# --- Data Schemas for Monitoring Inputs/Outputs ---

class FeatureDriftValue(BaseModel):
    feature_name: str
    drift_score: float
    p_value: Optional[float] = None # For statistical tests
    drift_detected: bool
    method_used: DriftDetectionMethod
    additional_details: Optional[Dict[str, Any]] = None

class DriftReport(BaseModel):
    report_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    config_id: uuid.UUID
    model_identifier: ModelIdentifier
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    overall_drift_status: DriftType # Could be an aggregate status or most severe
    feature_drift_results: List[FeatureDriftValue]
    baseline_data_info: Optional[str] = Field(None, description="Information about the baseline data used (e.g., date range, version).")
    production_data_info: Optional[str] = Field(None, description="Information about the production data sample analyzed.")
    summary: Optional[str] = None

class PerformanceMetricValue(BaseModel):
    metric_name: MetricType
    value: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    model_identifier: ModelIdentifier
    config_id: uuid.UUID
    dimensions: Optional[Dict[str, str]] = Field(None, description="Optional dimensions for slicing/dicing, e.g., segment, region.")

class ModelPerformanceReport(BaseModel):
    report_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    config_id: uuid.UUID
    model_identifier: ModelIdentifier
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metrics: List[PerformanceMetricValue]
    data_window_start: Optional[datetime] = None
    data_window_end: Optional[datetime] = None
    summary: Optional[str] = None

# --- Alerting Schemas ---

class AlertEvent(BaseModel):
    alert_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source_service: str = Field(default="monitoring_service", description="Service originating the alert.")
    source_component: Optional[str] = Field(None, description="Specific component within the service (e.g., data_drift_detector).")
    config_id: Optional[uuid.UUID] = Field(None, description="Monitoring configuration ID related to this alert.")
    model_identifier: Optional[ModelIdentifier] = None
    severity: AlertSeverity
    title: str = Field(..., description="A concise title for the alert.")
    description: str = Field(..., description="Detailed description of the alert event.")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional structured details about the event (e.g., drift scores, metric values).")
    status: str = Field(default="new", description="Status of the alert (e.g., new, acknowledged, resolved).")

# --- API Request/Response Schemas (Illustrative) ---

class CreateMonitoringConfigRequest(BaseModel):
    model_identifier: ModelIdentifier
    description: Optional[str] = None
    features_to_monitor: Optional[List[FeatureMonitoringConfig]] = None
    performance_metrics_to_track: Optional[List[PerformanceMetricConfig]] = None
    baseline_data_identifier: Optional[DataSourceIdentifier] = None
    production_data_identifier: DataSourceIdentifier
    ground_truth_identifier: Optional[DataSourceIdentifier] = None
    drift_detection_schedule: Optional[MonitoringJobSchedule] = None
    performance_monitoring_schedule: Optional[MonitoringJobSchedule] = None
    alert_recipients: Optional[List[AlertRecipientConfig]] = None
    custom_monitoring_params: Optional[Dict[str, Any]] = None

class MonitoringStatusResponse(BaseModel):
    model_identifier: ModelIdentifier
    last_drift_check: Optional[datetime] = None
    last_drift_status: Optional[DriftType] = None
    last_performance_check: Optional[datetime] = None
    last_performance_summary: Optional[Dict[MetricType, float]] = None
    active_alerts_count: int = 0

# --- Time-series Metric Storage Schema (Generic) ---

class TimeSeriesDataPoint(BaseModel):
    metric_name: str # e.g., "accuracy", "feature_X_drift_score"
    timestamp: datetime
    value: float
    tags: Dict[str, str] = Field(..., description="Tags for dimensions, e.g., {model_id: ..., model_version: ..., feature_name: ...}")


