# Token Usage Tracking Service Usage Guide

## 1. Overview

The `TokenUsageTrackingService` is a core component within the Industriverse Core AI Layer. Its primary function is to monitor, record, analyze, and report the consumption of tokens by Large Language Models (LLMs) across the platform. This service provides essential data for various operational and strategic purposes, including:

*   **Cost Management:** Tracking token usage to understand and allocate LLM operational costs.
*   **Resource Allocation:** Providing insights into resource demand for capacity planning.
*   **Usage Pattern Analysis:** Identifying how LLMs are used, by whom, and for what purposes.
*   **API Monitoring:** Observing the usage of LLM APIs.
*   **Quota Implementation:** Laying the groundwork for enforcing usage quotas (future capability).
*   **Billing Support:** Providing data that could be used for internal chargebacks or external billing (future capability).

The service is designed with scalability, security, and extensibility in mind, aiming for minimal impact on LLM inference performance through asynchronous operations.

## 2. Key Features

*   **Accurate Token Tracking:** Captures both input and output token counts for LLM interactions.
*   **Granular Recording:** Logs usage data with detailed attributes such as user ID, application ID, model ID, tenant ID, and timestamps.
*   **Asynchronous Event Processing:** Designed to ingest usage events via a message queue (though current simulation processes directly if queue is not configured) to avoid blocking LLM inference.
*   **Data Enrichment:** Augments raw usage data with calculated fields like total tokens and estimated costs, and can be extended to include verified identity information.
*   **Configurable Cost Models:** Allows defining cost per token (input/output specific) for different LLM models.
*   **Reporting & Querying API:** Provides methods to retrieve aggregated usage summaries and detailed usage records with flexible filtering.
*   **Security Integration:** Incorporates placeholders for authentication and authorization checks via an `IdentityManagementService`.
*   **Privacy Considerations:** Includes placeholders for data masking and anonymization of sensitive information within usage records.
*   **Audit Logging:** Contains placeholders for logging access and actions for auditability.

## 3. Architecture (Conceptual)

The `TokenUsageTrackingService` is designed to operate within an event-driven architecture:

1.  **Event Publication:** LLM services (e.g., `LLMInferenceService`) publish token usage events after an inference call. These events contain details about the interaction.
2.  **Message Queue (Recommended):** Events are ideally sent to a message queue (e.g., Kafka, RabbitMQ) for asynchronous and decoupled processing. This ensures the LLM service is not blocked.
3.  **Event Consumption & Processing:** The `TokenUsageTrackingService` (or a dedicated worker component) consumes events from the queue.
4.  **Enrichment:** Events are enriched with additional information (e.g., calculated costs, verified user details from an Identity Service).
5.  **Storage:** Enriched events are persisted to a database via the Industriverse `DataLayer`.
6.  **Reporting:** An API is provided to query the stored usage data for analysis and reporting.

*Note: The current implementation includes a simulated in-memory database and can process events synchronously if a message queue or data layer client is not configured. This is primarily for development and testing purposes.*

## 4. Data Model

Each token usage record typically contains the following fields. This model is used for storage and is the basis for reporting.

*   `request_id`: (UUID) Unique identifier for the usage event record.
*   `timestamp`: (String, ISO 8601 DateTime) Timestamp when the event was recorded or occurred.
*   `user_id`: (String) Identifier of the user who initiated the LLM call.
*   `application_id`: (String, Optional) Identifier of the application or service making the LLM call.
*   `tenant_id`: (String, Optional) Identifier of the organization or tenant to which the usage belongs.
*   `model_id`: (String) Identifier of the LLM used (e.g., "gpt-4-turbo").
*   `model_version`: (String, Optional) Specific version of the LLM.
*   `input_tokens`: (Integer) Number of tokens in the input/prompt.
*   `output_tokens`: (Integer) Number of tokens in the output/completion.
*   `total_tokens`: (Integer) Sum of `input_tokens` and `output_tokens`.
*   `estimated_cost`: (Decimal) Calculated cost for the usage, based on configured cost models.
*   `currency`: (String) Currency of the `estimated_cost` (e.g., "USD").
*   `latency_ms`: (Integer, Optional) Latency of the LLM call in milliseconds.
*   `status`: (String, Optional) Status of the LLM call (e.g., "SUCCESS", "FAILURE").
*   `error_message`: (String, Optional) Error message if the LLM call failed.
*   `custom_metadata`: (JSON/Dict, Optional) Any additional relevant metadata, which may be subject to masking/anonymization policies.

## 5. API Reference

The `TokenUsageTrackingService` class provides the following primary methods:

### 5.1. Initialization

```python
class TokenUsageTrackingService:
    def __init__(self, 
                 data_layer_client: Optional[Any] = None, 
                 message_queue_client: Optional[Any] = None, 
                 identity_service_client: Optional[Any] = None, 
                 config: Optional[Dict[str, Any]] = None):
        # ...
```

*   **`data_layer_client`**: (Optional) A client object to interact with the Industriverse Data Layer for persistent storage. If `None`, an in-memory list is used for simulation.
*   **`message_queue_client`**: (Optional) A client object for interacting with a message queue (e.g., Kafka, RabbitMQ). If `None`, event publishing will simulate direct processing.
*   **`identity_service_client`**: (Optional) A client object for interacting with an Identity Management Service. Used for authentication, authorization, and enriching events with verified user/tenant information. Placeholders for actual integration exist.
*   **`config`**: (Optional) A dictionary for service configuration. A key use is for `cost_models` (see Configuration section).

### 5.2. `publish_usage_event_async`

Publishes a token usage event. This is the primary method for other services (like `LLMInferenceService`) to report token usage.

```python
async def publish_usage_event_async(self, 
                                    usage_data: Dict[str, Any], 
                                    user_context: Optional[Dict[str, Any]] = None) -> bool:
    # ...
```

*   **`usage_data`**: A dictionary containing the details of the token usage. Mandatory fields:
    *   `user_id`: (String)
    *   `model_id`: (String)
    *   `input_tokens`: (Integer)
    *   `output_tokens`: (Integer)
    Optional fields include `application_id`, `tenant_id`, `model_version`, `latency_ms`, `status`, `error_message`, `custom_metadata`.
*   **`user_context`**: (Optional) A dictionary representing the authenticated calling user or service. This context is intended to be used by the `identity_service_client` for authorization checks and potentially for enriching the event with verified identity details. Example: `{"user_id": "user-abc", "roles": ["editor"], "tenant_id": "tenant-xyz"}`.
*   **Returns**: `True` if the event was successfully validated and queued for processing (or processed directly in simulation), `False` otherwise (e.g., validation failure).
*   **Behavior**: Validates the event, enriches it (adds `request_id`, `timestamp`, `total_tokens`, `estimated_cost`), and then attempts to publish it to the message queue. If no queue client is configured, it processes the event directly via `process_usage_event_from_queue` for simulation.

### 5.3. `process_usage_event_from_queue` (Internal/Worker Method)

Processes a single token usage event, typically consumed by a worker from the message queue.

```python
async def process_usage_event_from_queue(self, 
                                         event_data: Dict[str, Any], 
                                         user_context: Optional[Dict[str, Any]] = None) -> bool:
    # ...
```

*   **`event_data`**: The usage event data (usually already enriched if coming from `publish_usage_event_async`).
*   **`user_context`**: (Optional) Context that might be passed along with the event if needed for further processing or audit logging at the storage step.
*   **Returns**: `True` if the event was successfully stored (or simulated storage), `False` otherwise.
*   **Behavior**: Ensures the event is fully enriched and then attempts to store it using the `data_layer_client`. If no client is configured, it appends to the in-memory `_simulated_event_store`.

### 5.4. `get_usage_summary`

Retrieves an aggregated summary of token usage based on specified filters.

```python
async def get_usage_summary(self, 
                            user_context: Dict[str, Any], 
                            user_id_filter: Optional[str] = None, 
                            application_id_filter: Optional[str] = None, 
                            model_id_filter: Optional[str] = None, 
                            tenant_id_filter: Optional[str] = None,
                            start_time: Optional[str] = None, 
                            end_time: Optional[str] = None) -> Dict[str, Any]:
    # ...
```

*   **`user_context`**: Mandatory. The context of the user requesting the summary, used for authorization checks (e.g., ensuring a user can only see their own data or that an admin has appropriate permissions).
*   **`*_filter` arguments**: (Optional) Strings to filter the usage records by `user_id`, `application_id`, `model_id`, or `tenant_id`.
*   **`start_time`, `end_time`**: (Optional) ISO 8601 formatted datetime strings to define a time range for the summary.
*   **Returns**: A dictionary containing the summary, including `total_requests`, `total_input_tokens`, `total_output_tokens`, `total_tokens_sum`, `estimated_total_cost`, `currency`, and `filters_applied`.
*   **Authorization**: This method includes a placeholder for an authorization check (`_authorize_action`) using the `user_context`.

### 5.5. `get_detailed_usage_records`

Retrieves a list of detailed token usage records based on specified filters, with pagination support.

```python
async def get_detailed_usage_records(self, 
                                     user_context: Dict[str, Any], 
                                     user_id_filter: Optional[str] = None, 
                                     application_id_filter: Optional[str] = None,
                                     model_id_filter: Optional[str] = None,
                                     tenant_id_filter: Optional[str] = None,
                                     request_id_filter: Optional[str] = None,
                                     start_time: Optional[str] = None, 
                                     end_time: Optional[str] = None,
                                     limit: int = 100, 
                                     offset: int = 0) -> List[Dict[str, Any]]:
    # ...
```

*   **`user_context`**: Mandatory. The context of the user requesting the records, used for authorization.
*   **`*_filter` arguments**: (Optional) Filters for the records.
*   **`request_id_filter`**: (Optional) Filter by a specific `request_id`.
*   **`start_time`, `end_time`**: (Optional) Time range filters.
*   **`limit`**: (Integer, default 100) Maximum number of records to return (for pagination).
*   **`offset`**: (Integer, default 0) Number of records to skip (for pagination).
*   **Returns**: A list of dictionaries, where each dictionary is a detailed token usage record.
*   **Authorization**: Includes a placeholder for an authorization check.

## 6. Integration Points

*   **LLMInferenceService**: This service (or similar LLM interaction points) is the primary producer of token usage events that are published via `publish_usage_event_async`.
*   **IdentityManagementService (Conceptual)**: Used for:
    *   Authenticating calls to the reporting API.
    *   Authorizing actions (e.g., who can publish events, who can view which summaries/records).
    *   Enriching events with verified user/tenant details.
*   **DataLayer (Conceptual)**: The target for persistent storage of token usage records. The `TokenUsageTrackingService` would use a `data_layer_client` to interact with it.
*   **Message Queue (Conceptual)**: The recommended mechanism for ingesting usage events asynchronously (e.g., Kafka, RabbitMQ).
*   **ConfigurationService (Conceptual)**: Would provide service configurations, including `cost_models`.

## 7. Configuration

The service can be configured at initialization, notably with `cost_models`. This dictionary defines the cost per token for different LLMs.

Example `config`:
```python
service_config = {
    "cost_models": {
        "gpt-4-turbo": {"input_per_token": 0.00001, "output_per_token": 0.00003, "currency": "USD"},
        "claude-3-opus": {"input_per_token": 0.000015, "output_per_token": 0.000075, "currency": "USD"},
        "mistral-large": {"per_token": 0.000005, "currency": "USD"} # Fallback if input/output specific not given
    }
}
token_tracker = TokenUsageTrackingService(config=service_config)
```
If a model in `cost_models` has `input_per_token` and `output_per_token`, those are used. If only `per_token` is specified, it's used for both input and output token cost calculation.

## 8. Security and Privacy

*   **Authentication & Authorization**: API methods like `get_usage_summary` and `get_detailed_usage_records` require a `user_context`. The service includes placeholder calls to an `_authorize_action` method, which would integrate with the `IdentityManagementService` to enforce access policies (e.g., users can only see their own data, admins can see broader data).
*   **Data Masking/Anonymization**: The `_enrich_usage_event` method includes a placeholder comment for masking or anonymizing sensitive fields within `custom_metadata` based on defined policies. This is crucial for privacy.
*   **Audit Logging**: The service includes a placeholder `audit_log_action` method. In a production system, calls to this method would log significant actions (e.g., data access, event storage) to a dedicated audit trail for security monitoring and compliance.
*   **Data Encryption**: While not directly implemented in this service's code (as it's an application-level service), it's assumed that the underlying infrastructure (for message queues, databases via Data Layer, API gateways) will enforce encryption in transit (TLS/SSL) and at rest.
*   **Error Handling**: Custom exceptions `AuthenticationError` and `AuthorizationError` are defined and can be raised if security checks fail.

## 9. Error Handling

*   **Validation Errors**: `_validate_usage_event` logs errors if required fields are missing or invalid. `publish_usage_event_async` returns `False` in such cases.
*   **Authorization Errors**: Methods requiring authorization (e.g., `get_usage_summary`) will raise an `AuthorizationError` if the `_authorize_action` (placeholder) determines the user is not permitted. This should be caught by the calling API layer.
*   **Failures in Dependencies**: Errors during interaction with the message queue or data layer are logged. The methods generally return `False` or an error structure if these external operations fail.

## 10. Example Usage (Simulated)

This example demonstrates initializing the service and using its main functionalities with the simulated in-memory store.

```python
import asyncio

# Assuming TokenUsageTrackingService class and SIMULATED_DB are defined as in the service file

async def run_tracking_example():
    # Clear the global SIMULATED_DB for repeatable example runs
    SIMULATED_DB.clear()

    service_config = {
        "cost_models": {
            "gpt-4-turbo": {"input_per_token": 0.00001, "output_per_token": 0.00003, "currency": "USD"},
            "claude-3-opus": {"input_per_token": 0.000015, "output_per_token": 0.000075, "currency": "USD"}
        }
    }
    
    # Simulated identity client and user contexts
    mock_identity_client = object() # Placeholder for a real client
    admin_user_context = {"user_id": "admin-001", "roles": ["admin"], "tenant_id": "system"}
    regular_user_context = {"user_id": "user-123", "roles": ["user"], "tenant_id": "tenant-a"}

    token_tracker = TokenUsageTrackingService(config=service_config, identity_service_client=mock_identity_client)

    # --- Publish Usage Events ---
    usage_event_1 = {
        "user_id": "user-123", "application_id": "app-chat", "tenant_id": "tenant-a",
        "model_id": "gpt-4-turbo", "input_tokens": 120, "output_tokens": 80,
        "status": "SUCCESS", "timestamp": (datetime.datetime.utcnow() - datetime.timedelta(minutes=10)).isoformat()
    }
    await token_tracker.publish_usage_event_async(usage_event_1, user_context=regular_user_context)

    usage_event_2 = {
        "user_id": "user-456", "application_id": "app-summary", "tenant_id": "tenant-b",
        "model_id": "claude-3-opus", "input_tokens": 2000, "output_tokens": 500,
        "custom_metadata": {"job_id": "sum-job-001"}, "timestamp": datetime.datetime.utcnow().isoformat()
    }
    # In a real system, the user_context for publishing might be a system identity if LLMInferenceService publishes
    await token_tracker.publish_usage_event_async(usage_event_2, user_context=admin_user_context) 

    print(f"Simulated DB now has {len(SIMULATED_DB)} records.")

    # --- Get Usage Summary ---
    print("\n--- Testing Get Usage Summary (as admin for tenant-a) ---")
    try:
        summary_admin_tenant_a = await token_tracker.get_usage_summary(
            user_context=admin_user_context, 
            tenant_id_filter="tenant-a"
        )
        print(f"Admin Summary for tenant-a: {json.dumps(summary_admin_tenant_a, indent=2)}")
    except AuthorizationError as e:
        print(f"Authorization Error: {e}")

    print("\n--- Testing Get Usage Summary (as regular user for own data) ---")
    try:
        summary_user = await token_tracker.get_usage_summary(
            user_context=regular_user_context, 
            user_id_filter="user-123" # User should be able to see their own data
        )
        print(f"User Summary for user-123: {json.dumps(summary_user, indent=2)}")
    except AuthorizationError as e:
        print(f"Authorization Error: {e}")

    # --- Get Detailed Usage Records ---
    print("\n--- Testing Get Detailed Usage Records (as admin) ---")
    try:
        detailed_records_admin = await token_tracker.get_detailed_usage_records(
            user_context=admin_user_context,
            limit=5
        )
        print(f"Admin Detailed Records (limit 5): {json.dumps(detailed_records_admin, indent=2)}")
    except AuthorizationError as e:
        print(f"Authorization Error: {e}")

if __name__ == "__main__":
    # This is to make the example runnable if this content is saved to a .py file
    # For the markdown, this section is illustrative.
    # To run, ensure TokenUsageTrackingService and SIMULATED_DB are accessible.
    # For example, copy the class definition here or import it.
    pass
    # Example: asyncio.run(run_tracking_example()) 
```

This guide provides a comprehensive overview of the `TokenUsageTrackingService`, its API, and how to use it. For production deployment, the placeholder integrations for data layer, message queue, and identity services would need to be implemented with actual clients and infrastructure.

