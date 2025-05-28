# Workflow Automation Layer API Reference

## Overview

This document provides a comprehensive reference for the APIs exposed by the Industriverse Workflow Automation Layer. These APIs allow external systems, applications, and users to interact with the workflow engine, manage workflows, monitor execution, and integrate with other Industriverse layers.

## Authentication

All API requests must be authenticated using one of the configured methods (OAuth2, API Key, Mutual TLS). Refer to the [Security and Compliance Guide](security_compliance_guide.md) for details on authentication configuration.

## Base URL

The base URL for the API depends on the deployment environment. Typically, it will be something like:

`https://api.industriverse.example.com/workflow/v1`

## API Endpoints

### Workflow Management

#### `POST /workflows`

- **Description**: Create a new workflow definition.
- **Request Body**: Workflow manifest (YAML or JSON format).
- **Response**: Workflow ID and details.
- **Permissions**: `workflow:create`

```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/yaml" \
  --data-binary "@path/to/workflow_manifest.yaml" \
  https://api.industriverse.example.com/workflow/v1/workflows
```

#### `GET /workflows`

- **Description**: List existing workflow definitions.
- **Query Parameters**:
  - `limit` (int, optional): Maximum number of workflows to return.
  - `offset` (int, optional): Offset for pagination.
  - `filter` (string, optional): Filter criteria (e.g., `industry=manufacturing`).
- **Response**: List of workflow definitions.
- **Permissions**: `workflow:read`

```bash
curl -X GET \
  -H "Authorization: Bearer <token>" \
  "https://api.industriverse.example.com/workflow/v1/workflows?limit=10&filter=industry%3Dmanufacturing"
```

#### `GET /workflows/{workflow_id}`

- **Description**: Get details of a specific workflow definition.
- **Path Parameters**:
  - `workflow_id` (string): ID of the workflow.
- **Response**: Workflow definition details.
- **Permissions**: `workflow:read`

```bash
curl -X GET \
  -H "Authorization: Bearer <token>" \
  "https://api.industriverse.example.com/workflow/v1/workflows/predictive-maintenance-workflow"
```

#### `PUT /workflows/{workflow_id}`

- **Description**: Update an existing workflow definition.
- **Path Parameters**:
  - `workflow_id` (string): ID of the workflow.
- **Request Body**: Updated workflow manifest.
- **Response**: Updated workflow details.
- **Permissions**: `workflow:update`

```bash
curl -X PUT \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/yaml" \
  --data-binary "@path/to/updated_workflow_manifest.yaml" \
  "https://api.industriverse.example.com/workflow/v1/workflows/predictive-maintenance-workflow"
```

#### `DELETE /workflows/{workflow_id}`

- **Description**: Delete a workflow definition.
- **Path Parameters**:
  - `workflow_id` (string): ID of the workflow.
- **Response**: Success status.
- **Permissions**: `workflow:delete`

```bash
curl -X DELETE \
  -H "Authorization: Bearer <token>" \
  "https://api.industriverse.example.com/workflow/v1/workflows/predictive-maintenance-workflow"
```

### Workflow Execution

#### `POST /workflows/{workflow_id}/instances`

- **Description**: Start a new instance of a workflow.
- **Path Parameters**:
  - `workflow_id` (string): ID of the workflow to execute.
- **Request Body** (optional): Initial input data for the workflow.
- **Response**: Workflow instance ID and status.
- **Permissions**: `workflow:execute`

```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d 
{
  "input_data": {
    "machine_id": "machine-123",
    "sensor_data": { ... }
  }
}
 \
  "https://api.industriverse.example.com/workflow/v1/workflows/predictive-maintenance-workflow/instances"
```

#### `GET /workflows/instances`

- **Description**: List running or completed workflow instances.
- **Query Parameters**:
  - `limit` (int, optional): Maximum number of instances to return.
  - `offset` (int, optional): Offset for pagination.
  - `status` (string, optional): Filter by status (`running`, `completed`, `failed`, `aborted`).
  - `workflow_id` (string, optional): Filter by workflow ID.
- **Response**: List of workflow instances.
- **Permissions**: `workflow:read`

```bash
curl -X GET \
  -H "Authorization: Bearer <token>" \
  "https://api.industriverse.example.com/workflow/v1/workflows/instances?status=running&limit=20"
```

#### `GET /workflows/instances/{instance_id}`

- **Description**: Get details of a specific workflow instance.
- **Path Parameters**:
  - `instance_id` (string): ID of the workflow instance.
- **Response**: Workflow instance details, including status, tasks, and context.
- **Permissions**: `workflow:read`

```bash
curl -X GET \
  -H "Authorization: Bearer <token>" \
  "https://api.industriverse.example.com/workflow/v1/workflows/instances/instance-123e4567-e89b-12d3-a456-426614174000"
```

#### `POST /workflows/instances/{instance_id}/abort`

- **Description**: Abort a running workflow instance.
- **Path Parameters**:
  - `instance_id` (string): ID of the workflow instance.
- **Response**: Success status.
- **Permissions**: `workflow:execute`

```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  "https://api.industriverse.example.com/workflow/v1/workflows/instances/instance-123e4567-e89b-12d3-a456-426614174000/abort"
```

#### `POST /workflows/instances/{instance_id}/retry`

- **Description**: Retry a failed workflow instance or specific failed tasks.
- **Path Parameters**:
  - `instance_id` (string): ID of the workflow instance.
- **Request Body** (optional):
  - `task_ids` (list[string]): List of specific task IDs to retry.
- **Response**: Success status.
- **Permissions**: `workflow:execute`

```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d 
{
  "task_ids": ["failed-task-1", "failed-task-2"]
}
 \
  "https://api.industriverse.example.com/workflow/v1/workflows/instances/instance-123e4567-e89b-12d3-a456-426614174000/retry"
```

### Task Management

#### `GET /workflows/instances/{instance_id}/tasks`

- **Description**: List tasks within a specific workflow instance.
- **Path Parameters**:
  - `instance_id` (string): ID of the workflow instance.
- **Query Parameters**:
  - `status` (string, optional): Filter by task status (`pending`, `running`, `completed`, `failed`).
- **Response**: List of tasks.
- **Permissions**: `workflow:read`

```bash
curl -X GET \
  -H "Authorization: Bearer <token>" \
  "https://api.industriverse.example.com/workflow/v1/workflows/instances/instance-123e4567-e89b-12d3-a456-426614174000/tasks?status=failed"
```

#### `GET /workflows/instances/{instance_id}/tasks/{task_id}`

- **Description**: Get details of a specific task within a workflow instance.
- **Path Parameters**:
  - `instance_id` (string): ID of the workflow instance.
  - `task_id` (string): ID of the task.
- **Response**: Task details, including status, inputs, outputs, and logs.
- **Permissions**: `workflow:read`

```bash
curl -X GET \
  -H "Authorization: Bearer <token>" \
  "https://api.industriverse.example.com/workflow/v1/workflows/instances/instance-123e4567-e89b-12d3-a456-426614174000/tasks/quality-inspection-task"
```

#### `POST /workflows/instances/{instance_id}/tasks/{task_id}/complete`

- **Description**: Manually complete a task (e.g., for human intervention tasks).
- **Path Parameters**:
  - `instance_id` (string): ID of the workflow instance.
  - `task_id` (string): ID of the task.
- **Request Body** (optional): Task output data.
- **Response**: Success status.
- **Permissions**: `workflow:execute`

```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d 
{
  "output_data": {
    "decision": "approved",
    "reason": "Manual review completed."
  }
}
 \
  "https://api.industriverse.example.com/workflow/v1/workflows/instances/instance-123e4567-e89b-12d3-a456-426614174000/tasks/human-review-task/complete"
```

### Agent Management

#### `GET /agents`

- **Description**: List registered agents in the mesh topology.
- **Query Parameters**:
  - `limit` (int, optional): Maximum number of agents to return.
  - `offset` (int, optional): Offset for pagination.
  - `status` (string, optional): Filter by agent status (`online`, `offline`, `busy`).
  - `capabilities` (string, optional): Filter by required capabilities (comma-separated).
- **Response**: List of agents.
- **Permissions**: `agent:read`

```bash
curl -X GET \
  -H "Authorization: Bearer <token>" \
  "https://api.industriverse.example.com/workflow/v1/agents?status=online&capabilities=image_processing"
```

#### `GET /agents/{agent_id}`

- **Description**: Get details of a specific agent.
- **Path Parameters**:
  - `agent_id` (string): ID of the agent.
- **Response**: Agent details, including status, capabilities, and resource usage.
- **Permissions**: `agent:read`

```bash
curl -X GET \
  -H "Authorization: Bearer <token>" \
  "https://api.industriverse.example.com/workflow/v1/agents/quality-inspection-agent"
```

### n8n Integration

#### `POST /n8n/webhooks/{webhook_id}`

- **Description**: Trigger an n8n workflow via a webhook.
- **Path Parameters**:
  - `webhook_id` (string): ID of the n8n webhook.
- **Request Body**: Data payload for the n8n workflow.
- **Response**: Success status.
- **Permissions**: `n8n:trigger`

```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d 
{
  "event_type": "quality_alert",
  "data": { ... }
}
 \
  "https://api.industriverse.example.com/workflow/v1/n8n/webhooks/n8n-webhook-123"
```

#### `GET /n8n/workflows`

- **Description**: List n8n workflows managed by the integration.
- **Response**: List of n8n workflows.
- **Permissions**: `n8n:read`

```bash
curl -X GET \
  -H "Authorization: Bearer <token>" \
  "https://api.industriverse.example.com/workflow/v1/n8n/workflows"
```

### Monitoring and Telemetry

#### `GET /telemetry/workflows`

- **Description**: Get overall workflow telemetry data.
- **Query Parameters**:
  - `time_range` (string, optional): Time range for telemetry (e.g., `last_hour`, `last_day`).
- **Response**: Aggregated workflow metrics (execution count, success rate, average duration, etc.).
- **Permissions**: `telemetry:read`

```bash
curl -X GET \
  -H "Authorization: Bearer <token>" \
  "https://api.industriverse.example.com/workflow/v1/telemetry/workflows?time_range=last_day"
```

#### `GET /telemetry/workflows/{workflow_id}`

- **Description**: Get telemetry data for a specific workflow definition.
- **Path Parameters**:
  - `workflow_id` (string): ID of the workflow.
- **Query Parameters**:
  - `time_range` (string, optional): Time range for telemetry.
- **Response**: Telemetry data for the specific workflow.
- **Permissions**: `telemetry:read`

```bash
curl -X GET \
  -H "Authorization: Bearer <token>" \
  "https://api.industriverse.example.com/workflow/v1/telemetry/workflows/predictive-maintenance-workflow?time_range=last_week"
```

#### `GET /telemetry/instances/{instance_id}`

- **Description**: Get telemetry data for a specific workflow instance.
- **Path Parameters**:
  - `instance_id` (string): ID of the workflow instance.
- **Response**: Detailed telemetry data for the instance, including task timings and resource usage.
- **Permissions**: `telemetry:read`

```bash
curl -X GET \
  -H "Authorization: Bearer <token>" \
  "https://api.industriverse.example.com/workflow/v1/telemetry/instances/instance-123e4567-e89b-12d3-a456-426614174000"
```

#### `GET /traces`

- **Description**: Query Capsule Debug Traces.
- **Query Parameters**:
  - `limit` (int, optional): Maximum number of traces to return.
  - `offset` (int, optional): Offset for pagination.
  - `workflow_id` (string, optional): Filter by workflow ID.
  - `instance_id` (string, optional): Filter by instance ID.
  - `status` (string, optional): Filter by status.
  - `trace_level` (string, optional): Filter by trace level.
  - `start_time` (string, optional): Filter by start time (ISO 8601).
  - `end_time` (string, optional): Filter by end time (ISO 8601).
- **Response**: List of debug traces.
- **Permissions**: `trace:read`

```bash
curl -X GET \
  -H "Authorization: Bearer <token>" \
  "https://api.industriverse.example.com/workflow/v1/traces?workflow_id=predictive-maintenance-workflow&status=failed&limit=10"
```

#### `GET /traces/{trace_id}`

- **Description**: Get details of a specific debug trace.
- **Path Parameters**:
  - `trace_id` (string): ID of the trace.
- **Response**: Complete debug trace details.
- **Permissions**: `trace:read`

```bash
curl -X GET \
  -H "Authorization: Bearer <token>" \
  "https://api.industriverse.example.com/workflow/v1/traces/trace-123e4567-e89b-12d3-a456-426614174000"
```

### Escalation Management

#### `GET /escalations`

- **Description**: List active or historical escalations.
- **Query Parameters**:
  - `limit` (int, optional): Maximum number of escalations to return.
  - `offset` (int, optional): Offset for pagination.
  - `status` (string, optional): Filter by status (`active`, `resolved`, `unresolved`).
  - `workflow_id` (string, optional): Filter by workflow ID.
  - `instance_id` (string, optional): Filter by instance ID.
- **Response**: List of escalations.
- **Permissions**: `escalation:read`

```bash
curl -X GET \
  -H "Authorization: Bearer <token>" \
  "https://api.industriverse.example.com/workflow/v1/escalations?status=active&limit=10"
```

#### `GET /escalations/{escalation_id}`

- **Description**: Get details of a specific escalation.
- **Path Parameters**:
  - `escalation_id` (string): ID of the escalation.
- **Response**: Escalation details, including issue, status, assigned resolver, and history.
- **Permissions**: `escalation:read`

```bash
curl -X GET \
  -H "Authorization: Bearer <token>" \
  "https://api.industriverse.example.com/workflow/v1/escalations/escalation-123"
```

#### `POST /escalations/{escalation_id}/resolve`

- **Description**: Mark an escalation as resolved.
- **Path Parameters**:
  - `escalation_id` (string): ID of the escalation.
- **Request Body**:
  - `resolution_details` (string): Description of the resolution.
  - `resolution_code` (string, optional): Code indicating the resolution type.
- **Response**: Success status.
- **Permissions**: `escalation:resolve`

```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d 
{
  "resolution_details": "Resolved by adjusting machine parameters.",
  "resolution_code": "OPERATOR_ACTION"
}
 \
  "https://api.industriverse.example.com/workflow/v1/escalations/escalation-123/resolve"
```

## Data Models

Refer to the following specification documents for detailed data models:

- [Workflow Manifest Specification](workflow_manifest_spec.md)
- [Task Contract Specification](task_contract_spec.md)
- [Capsule Debug Trace Specification](capsule_debug_trace_spec.md)

## Error Handling

API errors are returned with standard HTTP status codes and a JSON error body:

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": {}
  }
}
```

Common status codes:

- `400 Bad Request`: Invalid request parameters or body.
- `401 Unauthorized`: Missing or invalid authentication credentials.
- `403 Forbidden`: Insufficient permissions for the requested operation.
- `404 Not Found`: Requested resource does not exist.
- `409 Conflict`: Resource conflict (e.g., trying to create a workflow that already exists).
- `500 Internal Server Error`: Unexpected server error.

## Versioning

The API uses URL versioning (e.g., `/v1`). Future versions will be introduced with a new version prefix.

## Additional Resources

- [Security and Compliance Guide](security_compliance_guide.md)
- [Workflow Manifest Specification](workflow_manifest_spec.md)
- [Task Contract Specification](task_contract_spec.md)
- [Capsule Debug Trace Specification](capsule_debug_trace_spec.md)

## Version History

- **1.0.0** (2025-05-22): Initial API reference
