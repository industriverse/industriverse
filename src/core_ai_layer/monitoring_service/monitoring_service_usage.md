# Monitoring Service - Usage Guide

**Version:** 1.0
**Date:** May 14, 2025

## 1. Overview

The Monitoring Service is a critical component of the Core AI Layer, designed to track the performance of deployed AI models (both LLMs and traditional ML), detect data drift, and alert relevant stakeholders to potential issues. This guide provides instructions on how to configure, use, and interpret the outputs of the Monitoring Service.

It comprises several key sub-services:

*   **`MonitoringOrchestratorService`**: Manages configurations, schedules monitoring tasks, and coordinates the other sub-services.
*   **`DataDriftDetectionService`**: Detects statistical drift in model input features or predictions.
*   **`ModelPerformanceMonitor`**: Calculates and tracks various performance metrics for models.
*   **`AlertingService`**: Dispatches alerts based on detected issues and configurations.
*   **`StorageInterface`**: Handles the persistence of monitoring configurations, reports, and alert logs (currently uses a base placeholder adapter).

## 2. Core Concepts

### 2.1. Monitoring Configuration (`MonitoringConfiguration`)

All monitoring activities are driven by a `MonitoringConfiguration`. This Pydantic model defines:

*   **`model_identifier`**: Which model to monitor (ID, version, service name, type).
*   **`description`**: A human-readable description of the configuration.
*   **`features_to_monitor`**: A list of `FeatureMonitoringConfig` specifying which features to check for drift, methods to use, and thresholds.
*   **`performance_metrics_to_track`**: A list of `PerformanceMetricConfig` specifying which performance metrics to calculate and their warning/critical thresholds.
*   **`baseline_data_identifier`**: Identifier for the reference dataset/profile used for drift detection.
*   **`production_data_identifier`**: Identifier for the live production data stream/source.
*   **`ground_truth_identifier`**: Identifier for the source of ground truth labels for performance calculation.
*   **`drift_detection_schedule` & `performance_monitoring_schedule`**: `ScheduleConfig` defining how often to run checks (e.g., HOURLY, DAILY).
*   **`alert_recipients`**: A list of `AlertRecipientConfig` defining who gets alerted, via which channel (EMAIL, SLACK, MCP_A2A, etc.), and at what minimum severity.
*   **`is_active`**: Boolean to enable/disable this monitoring configuration.
*   **`custom_monitoring_params`**: Dictionary for any additional parameters.

### 2.2. Data Identifiers (`DataSourceIdentifier`)

These schemas are used within `MonitoringConfiguration` to point to data sources, typically managed by the Data Layer. They include `source_name`, `source_type`, and `connection_details`.

### 2.3. Reports

*   **`DriftReport`**: Summarizes the results of a data drift check, including `overall_drift_status` and detailed `feature_drift_results` for each monitored feature.
*   **`ModelPerformanceReport`**: Contains calculated `metrics` for a model over a specific data window.

### 2.4. Alerts (`AlertEvent`)

Generated when drift or performance issues exceed configured thresholds, or when system errors occur. Contains `severity`, `title`, `description`, `details`, and context.

## 3. Getting Started: Using the `MonitoringOrchestratorService`

The `MonitoringOrchestratorService` is the primary entry point for managing and running monitoring tasks.

### 3.1. Initialization

```python
from core_ai_layer.monitoring_service import (
    MonitoringOrchestratorService,
    DataDriftDetectionService,
    ModelPerformanceMonitor,
    AlertingService
)
from core_ai_layer.monitoring_service.storage_interface import BaseStorageAdapter

# Initialize components
storage_adapter = BaseStorageAdapter() # Use a concrete adapter in a real scenario
drift_detector = DataDriftDetectionService()
performance_monitor = ModelPerformanceMonitor()
alerter = AlertingService()

# (Optional) Initialize placeholder clients for Data Layer and Model Services if testing integration
# from core_ai_layer.monitoring_service.monitoring_orchestrator_service import DataLayerClientPlaceholder, ModelServiceClientPlaceholder
# data_layer_client = DataLayerClientPlaceholder()
# model_service_client = ModelServiceClientPlaceholder()

orchestrator = MonitoringOrchestratorService(
    storage_adapter=storage_adapter,
    drift_detector=drift_detector,
    performance_monitor=performance_monitor,
    alerter=alerter,
    # data_layer_client=data_layer_client, # Pass if using placeholders
    # model_service_client=model_service_client # Pass if using placeholders
)
```

### 3.2. Creating a Monitoring Configuration

Use the `CreateMonitoringConfigRequest` schema and the orchestrator's `create_monitoring_configuration` method.

```python
from core_ai_layer.monitoring_service.monitoring_schemas import (
    CreateMonitoringConfigRequest,
    ModelIdentifier, ModelType,
    FeatureMonitoringConfig, DriftDetectionMethod,
    PerformanceMetricConfig, MetricType,
    ScheduleConfig, ScheduleFrequency, AlertSeverity,
    AlertRecipientConfig, AlertChannel,
    DataSourceIdentifier
)
import asyncio

async def setup_monitoring():
    config_request = CreateMonitoringConfigRequest(
        model_identifier=ModelIdentifier(
            model_id="fraud_detection_v1.2", 
            model_version="1.2.0", 
            service_name="machine_learning_service",
            model_type=ModelType.CLASSIFICATION
        ),
        description="Monitor fraud detection model for transaction amount drift and F1 score.",
        features_to_monitor=[
            FeatureMonitoringConfig(
                feature_name="transaction_amount",
                monitor_for_drift=True,
                drift_detection_methods=[DriftDetectionMethod.KS_TEST],
                threshold_warning=0.1, # Example threshold for drift score
                threshold_critical=0.2
            )
        ],
        performance_metrics_to_track=[
            PerformanceMetricConfig(
                metric_name=MetricType.F1_SCORE,
                threshold_warning=0.75, # Alert if F1 drops below 0.75
                threshold_critical=0.70
            )
        ],
        baseline_data_identifier=DataSourceIdentifier(source_name="fraud_model_baseline_data_q1_2025", source_type="dataset_snapshot"),
        production_data_identifier=DataSourceIdentifier(source_name="live_transaction_stream_features", source_type="feature_store_view"),
        ground_truth_identifier=DataSourceIdentifier(source_name="verified_fraud_labels_daily", source_type="ground_truth_table"),
        drift_detection_schedule=ScheduleConfig(frequency=ScheduleFrequency.DAILY, cron_expression=None),
        performance_monitoring_schedule=ScheduleConfig(frequency=ScheduleFrequency.DAILY, cron_expression=None),
        alert_recipients=[
            AlertRecipientConfig(
                channel=AlertChannel.EMAIL, 
                target="mlops-alerts@example.com", 
                min_severity=AlertSeverity.WARNING
            ),
            AlertRecipientConfig(
                channel=AlertChannel.MCP_A2A, 
                target="mcp_topic_monitoring_critical", # Example MCP topic
                min_severity=AlertSeverity.CRITICAL
            )
        ]
    )
    
    new_config = await orchestrator.create_monitoring_configuration(config_request)
    print(f"Created monitoring config: {new_config.config_id}")
    return new_config

# To run async code:
# new_config = asyncio.run(setup_monitoring())
```

### 3.3. Managing Configurations

The orchestrator provides methods for:

*   `get_monitoring_configuration(config_id: str)`
*   `update_monitoring_configuration(config_id: str, updates: Dict[str, Any])`
*   `delete_monitoring_configuration(config_id: str)`
*   `list_monitoring_configurations(model_id: Optional[str] = None, is_active: Optional[bool] = None)`

### 3.4. Automatic Monitoring (Scheduler)

Once a configuration is created with a schedule and `is_active=True`, the `MonitoringOrchestratorService` will automatically schedule periodic checks.

*   **Starting the Scheduler**: Call `await orchestrator.startup_scheduler()` when your application starts.
*   **Stopping the Scheduler**: Call `await orchestrator.shutdown_scheduler()` during graceful application shutdown.

### 3.5. Running On-Demand Checks

You can trigger checks manually using `await orchestrator.run_monitoring_checks(config: MonitoringConfiguration)`.
This requires you to first fetch the `MonitoringConfiguration` object.

```python
async def run_on_demand(config_id_to_run: str):
    try:
        config_to_run = await orchestrator.get_monitoring_configuration(config_id_to_run)
        if config_to_run.is_active:
            print(f"Running on-demand checks for config: {config_to_run.config_id}")
            await orchestrator.run_monitoring_checks(config_to_run)
            print("On-demand checks completed.")
        else:
            print(f"Config {config_id_to_run} is not active.")
    except ResourceNotFoundError:
        print(f"Config {config_id_to_run} not found.")

# asyncio.run(run_on_demand("your_config_id_here"))
```

### 3.6. Retrieving Monitoring Status and Reports

*   `get_monitoring_status(model_id: str, config_id: Optional[str] = None)`: Provides a summary status.
*   Use `storage_adapter` methods directly to query detailed reports (this might be exposed via orchestrator API in a full deployment):
    *   `storage_adapter.list_drift_reports(...)`
    *   `storage_adapter.get_drift_report(report_id)`
    *   `storage_adapter.list_performance_reports(...)`
    *   `storage_adapter.get_performance_report(report_id)`
    *   `storage_adapter.list_alert_events(...)`

## 4. Interpreting Outputs

### 4.1. Drift Reports (`DriftReport`)

*   **`overall_drift_status`**: Indicates if significant drift was detected (e.g., `COVARIATE_DRIFT`, `NO_DRIFT_DETECTED`).
*   **`feature_drift_results`**: A list of `FeatureDriftValue` for each monitored feature:
    *   `feature_name`: The name of the feature.
    *   `drift_score`: The calculated drift score (e.g., KS statistic).
    *   `p_value`: (If applicable, e.g., for KS test) The p-value of the test.
    *   `drift_detected`: Boolean indicating if drift was detected for this feature based on its threshold.
    *   `method_used`: The drift detection method applied.
    *   `additional_details`: Method-specific details.

### 4.2. Performance Reports (`ModelPerformanceReport`)

*   **`metrics`**: A list of `PerformanceMetricValue`:
    *   `metric_name`: The name of the metric (e.g., `F1_SCORE`, `RMSE`).
    *   `value`: The calculated value of the metric.
*   **`summary`**: A brief summary of the report.
*   **`timestamp`**, `data_window_start`, `data_window_end`: Contextual time information.

### 4.3. Alerts (`AlertEvent`)

*   **`severity`**: `INFO`, `WARNING`, or `CRITICAL`.
*   **`title`**: A concise summary of the alert.
*   **`description`**: More detailed explanation of the issue.
*   **`details`**: A dictionary with specific data related to the alert (e.g., metric values, drift scores).
*   **`model_identifier`**, `config_id`: Context about the source of the alert.

## 5. Sub-Service Details (Conceptual Usage)

While direct interaction is primarily through the orchestrator, understanding sub-service roles is useful.

### 5.1. `DataDriftDetectionService`

*   **`check_data_drift(...)`**: Takes production data, baseline characteristics, and feature configurations. Returns a `DriftReport`.
*   Relies on statistical methods (currently KS_TEST placeholder, PSI placeholder).
*   Requires baseline data to be in a comparable format (e.g., `reference_sample` for KS_TEST placeholder).

### 5.2. `ModelPerformanceMonitor`

*   **`calculate_performance_metrics(...)`**: Takes predictions, ground truth, and metric configurations. Returns a `ModelPerformanceReport`.
*   Supports various metrics for classification, regression, and LLMs (placeholders for some LLM metrics).
*   For classification metrics like AUC, `prediction_probabilities` are needed.

### 5.3. `AlertingService`

*   **`dispatch_alert(...)`**: Takes an `AlertEvent` and recipient configurations. Sends notifications via configured channels (currently placeholders for actual sending logic).
*   Supports different channels like `EMAIL`, `SLACK`, `MCP_A2A`, `LOG`.

## 6. Integration Points

*   **Data Layer**: The orchestrator (via its `DataLayerClientPlaceholder`) fetches production data, baseline data/characteristics, and ground truth.
*   **Model Services (`llm_service`, `machine_learning_service`)**: The orchestrator (via `ModelServiceClientPlaceholder`) fetches model predictions for performance monitoring.
*   **Protocol Layer (MCP/A2A)**: The `AlertingService` can dispatch alerts via MCP/A2A messages to other systems or agents (e.g., Overseer).
*   **Storage**: All configurations, reports, and alert logs are persisted via the `StorageAdapterInterface`.

## 7. Error Handling

The service uses custom exceptions defined in `monitoring_exceptions.py` (e.g., `ConfigurationError`, `DataAccessError`, `DriftDetectionError`, `MetricCalculationError`, `AlertingError`). These are caught and handled by the orchestrator, often resulting in CRITICAL alerts if a monitoring check fails.

## 8. Customization and Extension

*   **Storage Adapters**: Implement concrete `StorageAdapterInterface` classes for your chosen databases (e.g., `TimeseriesDBAdapter` for InfluxDB, `MetadataStoreAdapter` for PostgreSQL/MongoDB).
*   **Drift Detection Methods**: Add new methods to `DataDriftDetectionService` and update `DriftDetectionMethod` enum.
*   **Performance Metrics**: Add new metric calculations to `ModelPerformanceMonitor` and update `MetricType` enum. For LLMs, integrate specific evaluation libraries.
*   **Alert Channels**: Implement actual sending logic in `AlertingService` for desired channels (e.g., using `smtplib` for email, `slack_sdk` for Slack).
*   **Data Layer/Model Service Clients**: Replace placeholder clients with actual clients that interact with your Data Layer and Model Serving infrastructure.

This usage guide provides a starting point. Refer to the source code and Pydantic schemas for the most detailed information on data structures and available parameters.

