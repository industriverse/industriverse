# Industriverse Workflow Automation Layer Guide

## Introduction

The Workflow Automation Layer orchestrates complex business processes and operational tasks across the Industriverse Framework. It enables the definition, execution, and monitoring of automated workflows that connect different layers, components, and external systems. This layer leverages tools like n8n alongside custom workflow engines to provide flexibility and power in automating industrial processes.

## Architecture Overview

The Workflow Automation Layer integrates tightly with other framework layers, acting as a central coordinator for process execution.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   WORKFLOW AUTOMATION LAYER                             │
│                                                                         │
│  ┌─────────────────────────┐      ┌─────────────────────────┐           │
│  │                         │      │                         │           │
│  │   Workflow Definition   │      │    Workflow Execution   │           │
│  │   (UI, JSON, Code)      │      │   (Engines: n8n, Custom)│           │
│  │                         │      │                         │           │
│  └────────────┬────────────┘      └────────────┬────────────┘           │
│               │                                │                        │
│  ┌────────────┴────────────┐      ┌────────────┴────────────┐           │
│  │                         │      │                         │           │
│  │   Workflow Repository   │      │    Workflow Triggers    │           │
│  │   (Version Control)     │      │ (Events, Schedule, API) │           │
│  │                         │      │                         │           │
│  └────────────┬────────────┘      └────────────┬────────────┘           │
│               │                                │                        │
│  ┌────────────┴────────────────────────────────┴────────────┐           │
│  │                                                         │           │
│  │                     Workflow Services                   │           │
│  │                                                         │           │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │  │             │  │             │  │             │  │             │  │
│  │  │ Monitoring  │  │ State Mgmt  │  │ Error       │  │ Agent       │  │
│  │  │ Service     │  │ Service     │  │ Handling    │  │ Interaction │  │
│  │  │             │  │             │  │             │  │             │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │
│  │                                                         │           │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │  │             │  │             │  │             │  │             │  │
│  │  │ Protocol    │  │ Security    │  │ Data Access │  │ AI Service  │  │
│  │  │ Integration │  │ Integration │  │ Integration │  │ Integration │  │
│  │  │             │  │             │  │             │  │             │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │
│  └─────────────────────────────────────────────────────────┘           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Key Components

1.  **Workflow Definition**: Tools and formats for defining workflows.
    *   **UI Designer**: Visual tools (like n8n UI) for creating workflows.
    *   **JSON/YAML**: Standard formats for storing workflow definitions.
    *   **Code-Based**: Defining workflows using programming languages (e.g., Python SDK).
2.  **Workflow Execution**: Engines responsible for running workflows.
    *   **n8n Engine**: Integrated n8n instance for executing n8n workflows.
    *   **Custom Engines**: Support for custom or domain-specific workflow engines.
3.  **Workflow Repository**: Stores and manages workflow definitions.
    *   **Version Control**: Tracks changes to workflows (e.g., using Git).
    *   **Storage**: Database or file system for storing definitions.
4.  **Workflow Triggers**: Mechanisms to initiate workflow execution.
    *   **Event-Based**: Triggered by events from other layers (e.g., Data Layer events via MCP).
    *   **Scheduled**: Triggered based on time schedules (cron jobs).
    *   **API Call**: Triggered via direct API requests.
    *   **Manual**: Triggered by user interaction.
5.  **Workflow Services**: Supporting services for workflow management.
    *   **Monitoring Service**: Tracks workflow execution status, performance, and logs.
    *   **State Management Service**: Manages the state of long-running workflows.
    *   **Error Handling**: Defines strategies for handling errors during execution (retries, compensation).
    *   **Agent Interaction**: Facilitates communication between workflows and A2A agents.
    *   **Protocol Integration**: Uses MCP/A2A for communication with other layers/agents.
    *   **Security Integration**: Enforces security policies during workflow execution.
    *   **Data Access Integration**: Interacts with the Data Layer.
    *   **AI Service Integration**: Calls models or services from the Core AI Layer.

## Defining Workflows

Workflows can be defined using various methods, offering flexibility for different user preferences and complexity levels.

### Using n8n UI

The integrated n8n instance provides a powerful visual interface for building workflows by connecting nodes representing different operations.

**(Example: Screenshot or description of n8n UI building a simple workflow)**

### Using JSON (n8n Format)

Workflows created in the n8n UI can be exported as JSON. This format can also be used to define workflows programmatically or store them in version control.

```json
// Example: simple_alert_workflow.json (n8n JSON format)
{
  "name": "Simple Alert Workflow",
  "nodes": [
    {
      "parameters": {},
      "name": "Start",
      "type": "n8n-nodes-base.start",
      "typeVersion": 1,
      "position": [ 250, 300 ]
    },
    {
      "parameters": {
        "event": "equipment.high_temperature", // Listen for MCP event
        "sourceLayer": "data",
        "options": {}
      },
      "name": "MCP Event Trigger",
      "type": "industriverse-nodes-base.mcpEventTrigger", // Custom Industriverse node
      "typeVersion": 1,
      "position": [ 450, 300 ]
    },
    {
      "parameters": {
        "subject": "High Temperature Alert: {{ $json.body.payload.equipment_id }}",
        "to": "alerts@example.com",
        "text": "High temperature detected for equipment {{ $json.body.payload.equipment_id }}. Current temperature: {{ $json.body.payload.temperature }} C at {{ $json.body.context.timestamp }}."
      },
      "name": "Send Alert Email",
      "type": "n8n-nodes-base.emailSend",
      "typeVersion": 1,
      "position": [ 650, 300 ]
    }
  ],
  "connections": {
    "Start": { "main": [ [ { "node": "MCP Event Trigger", "type": "main" } ] ] },
    "MCP Event Trigger": { "main": [ [ { "node": "Send Alert Email", "type": "main" } ] ] }
  },
  "settings": {},
  "staticData": null
}
```

### Using Code (Python SDK - Conceptual)

A Python SDK could allow defining workflows programmatically.

```python
from industriverse.workflow import Workflow, Trigger, Step, Action
from industriverse.protocol.mcp import MCPEventTrigger
from industriverse.integrations.email import SendEmailAction

# Define the workflow
workflow = Workflow(name="Simple Alert Workflow")

# Define the trigger
workflow.trigger = MCPEventTrigger(
    event_type="equipment.high_temperature",
    source_layer="data"
)

# Define the steps
workflow.add_step(
    Step(name="Send Alert Email").action(
        SendEmailAction(
            to="alerts@example.com",
            subject="High Temperature Alert: {{ trigger.payload.equipment_id }}",
            body="High temperature detected for equipment {{ trigger.payload.equipment_id }}. Current temperature: {{ trigger.payload.temperature }} C at {{ trigger.context.timestamp }}."
        )
    )
)

# Save or deploy the workflow
workflow.save("./workflows/simple_alert_workflow.pywf")
# workflow.deploy()
```

## Executing Workflows

Workflows are executed by the appropriate engine based on their definition format.

### Triggers

-   **MCP Events**: Workflows can subscribe to MCP events published by other layers.
-   **Scheduled**: Cron expressions define regular execution times.
-   **API Calls**: A dedicated API endpoint allows external systems or UI components to trigger workflows.
-   **Manual**: Users can trigger workflows directly through a management interface.

### Execution Engines

-   **n8n Engine**: Executes workflows defined in the n8n JSON format.
-   **Custom Engines**: Can be integrated to handle specific workflow types (e.g., BPMN engines, state machines).

### State Management

For long-running workflows, the State Management Service persists the workflow state, allowing them to pause and resume (e.g., waiting for human input or external events).

## Monitoring and Error Handling

### Monitoring

The Monitoring Service provides visibility into workflow execution:

-   **Execution History**: Logs of past workflow runs.
-   **Status Tracking**: Real-time status (running, completed, failed).
-   **Performance Metrics**: Execution time, resource usage.
-   **Logs**: Detailed logs generated during execution.

This information is often integrated with the Overseer System for a unified view.

### Error Handling

Robust error handling is crucial:

-   **Retries**: Automatically retry failed steps with configurable backoff.
-   **Error Branches**: Define specific paths in the workflow to handle expected errors.
-   **Compensation Logic**: Define actions to undo completed steps if a later step fails (e.g., in transactional workflows).
-   **Notifications**: Alert administrators or users about failed workflows.

## Integration with Other Layers

Workflows act as glue, connecting functionalities across layers:

-   **Data Layer**: Trigger workflows based on data events (e.g., new data arrival, threshold breach). Read/write data as part of workflow steps.
-   **Core AI Layer**: Call AI models for analysis or prediction within a workflow.
-   **Generative Layer**: Use workflows to orchestrate the generation of code, documents, or UI components.
-   **Application Layer**: Trigger workflows from application events. Workflows can call application APIs.
-   **Protocol Layer**: Use MCP/A2A to communicate with other components or external agents within workflow steps.
-   **UI/UX Layer**: Trigger workflows from user actions. Display workflow status or results in the UI.
-   **Security & Compliance Layer**: Ensure workflows execute within defined security contexts and adhere to compliance rules.
-   **Deployment Operations Layer**: Automate deployment tasks using workflows.
-   **Overseer System**: Report workflow status and metrics. Receive commands (e.g., pause/resume workflow) from Overseer.

## Code Example: Workflow Interacting with Multiple Layers

Let's consider a workflow for processing an anomaly detected by the Core AI Layer.

```json
// Example: anomaly_processing_workflow.json (n8n JSON format)
{
  "name": "Anomaly Processing Workflow",
  "nodes": [
    {
      "parameters": {},
      "name": "Start",
      "type": "n8n-nodes-base.start",
      "typeVersion": 1,
      "position": [ 100, 300 ]
    },
    {
      "parameters": {
        "event": "core_ai.anomaly_detected", // Triggered by Core AI Layer event
        "sourceLayer": "core-ai",
        "options": {}
      },
      "name": "MCP Anomaly Event",
      "type": "industriverse-nodes-base.mcpEventTrigger",
      "typeVersion": 1,
      "position": [ 300, 300 ]
    },
    {
      "parameters": {
        "capability": "data.query", // Query Data Layer for equipment details
        "targetLayer": "data",
        "payload": {
          "query": "SELECT * FROM equipment WHERE id = '{{ $json.body.payload.equipment_id }}'"
        },
        "options": {}
      },
      "name": "Get Equipment Details",
      "type": "industriverse-nodes-base.mcpRequest", // Custom node for MCP requests
      "typeVersion": 1,
      "position": [ 500, 200 ]
    },
    {
      "parameters": {
        "conditions": { // Check anomaly severity
          "string": [
            {
              "value1": "={{ $json.body.payload.severity }}",
              "operation": "equal",
              "value2": "critical"
            }
          ]
        }
      },
      "name": "Is Critical?",
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "position": [ 700, 300 ]
    },
    {
      "parameters": {
        "agentId": "maintenance-dispatch-agent", // Find A2A agent
        "capability": "createMaintenanceTicket",
        "options": {}
      },
      "name": "Find Dispatch Agent",
      "type": "industriverse-nodes-base.a2aDiscoverAgent", // Custom node
      "typeVersion": 1,
      "position": [ 900, 200 ]
    },
    {
      "parameters": {
        "agentId": "={{ $node['Find Dispatch Agent'].json.agentId }}",
        "capability": "createMaintenanceTicket",
        "inputs": {
          "equipmentId": "={{ $json.body.payload.equipment_id }}",
          "description": "Critical anomaly detected: {{ $json.body.payload.anomaly_type }}. Details: {{ $json.body.payload.details }}",
          "priority": "high",
          "location": "={{ $node['Get Equipment Details'].json.result[0].location }}"
        },
        "options": {
          "waitForResult": true
        }
      },
      "name": "Create A2A Ticket",
      "type": "industriverse-nodes-base.a2aCreateTask", // Custom node
      "typeVersion": 1,
      "position": [ 1100, 200 ]
    },
    {
      "parameters": {
        "subject": "Critical Anomaly Ticket Created: {{ $json.body.payload.equipment_id }}",
        "to": "maintenance-manager@example.com",
        "text": "A critical maintenance ticket (ID: {{ $node['Create A2A Ticket'].json.taskId }}) has been created for equipment {{ $json.body.payload.equipment_id }} due to anomaly: {{ $json.body.payload.anomaly_type }}."
      },
      "name": "Notify Manager",
      "type": "n8n-nodes-base.emailSend",
      "typeVersion": 1,
      "position": [ 1300, 200 ]
    },
    {
      "parameters": {
        "message": "Anomaly logged for {{ $json.body.payload.equipment_id }}. Severity: {{ $json.body.payload.severity }}",
        "level": "warning"
      },
      "name": "Log Warning",
      "type": "industriverse-nodes-base.logMessage", // Custom node
      "typeVersion": 1,
      "position": [ 900, 400 ]
    }
  ],
  "connections": {
    "Start": { "main": [ [ { "node": "MCP Anomaly Event", "type": "main" } ] ] },
    "MCP Anomaly Event": { "main": [ [ { "node": "Get Equipment Details", "type": "main" } ] ] },
    "Get Equipment Details": { "main": [ [ { "node": "Is Critical?", "type": "main" } ] ] },
    "Is Critical?": {
      "main": [
        [ { "node": "Find Dispatch Agent", "type": "main" } ], // True (Critical)
        [ { "node": "Log Warning", "type": "main" } ]       // False (Not Critical)
      ]
    },
    "Find Dispatch Agent": { "main": [ [ { "node": "Create A2A Ticket", "type": "main" } ] ] },
    "Create A2A Ticket": { "main": [ [ { "node": "Notify Manager", "type": "main" } ] ] }
  },
  "settings": {},
  "staticData": null
}
```

## Deployment and Configuration

### Manifest Configuration

Workflows are typically defined within Application Layer manifests or as standalone resources managed by the Workflow Automation Layer.

```yaml
# Example: Part of an Application Manifest
apiVersion: industriverse.io/v1
kind: Application
metadata:
  name: predictive-maintenance
  # ... other app metadata ...
spec:
  # ... other app spec ...
  workflows:
    - name: anomaly-processing-workflow
      source: ./workflows/anomaly_processing_workflow.json
      engine: n8n # Specifies the workflow engine
      trigger: 
        type: mcp_event
        config:
          event_type: core_ai.anomaly_detected
          source_layer: core-ai
      enabled: true
      retry_policy:
        max_retries: 3
        delay: 60 # seconds
      error_handling:
        notify_email: admin-errors@example.com
    - name: daily-report-workflow
      source: ./workflows/daily_report_workflow.pywf # Code-based workflow
      engine: python_sdk # Custom engine
      trigger:
        type: schedule
        config:
          cron: "0 8 * * *" # 8 AM daily
      enabled: true
```

### Kubernetes Deployment

The Workflow Automation Layer components (n8n, custom engines, services) are deployed as Kubernetes resources.

```yaml
# Example Deployment for n8n (Simplified)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: n8n-workflow-engine
  namespace: industriverse
spec:
  replicas: 1 # Or more for HA, requires persistent volume for state
  selector:
    matchLabels:
      app: n8n-workflow-engine
  template:
    metadata:
      labels:
        app: n8n-workflow-engine
    spec:
      containers:
      - name: n8n
        image: n8nio/n8n:latest # Use appropriate version
        ports:
        - containerPort: 5678
          name: http
        env:
        - name: N8N_HOST
          value: "n8n.industriverse.example.com" # Set your domain
        - name: WEBHOOK_URL
          value: "https://n8n.industriverse.example.com/" # Public URL for webhooks
        - name: GENERIC_TIMEZONE
          value: "UTC"
        - name: EXECUTIONS_DATA_PRUNE
          value: "true"
        - name: EXECUTIONS_DATA_MAX_AGE
          value: "720" # Prune data older than 30 days (in hours)
        # Add environment variables for database connection if using external DB
        # Add environment variables for Industriverse custom node integration
        - name: INDUSTRIVERSE_MCP_BROKER
          value: "mcp://mcp-broker.industriverse:8080"
        - name: INDUSTRIVERSE_A2A_BROKER
          value: "a2a://a2a-broker.industriverse:8081"
        volumeMounts:
        - name: n8n-data
          mountPath: /home/node/.n8n
        resources:
          requests:
            cpu: "500m"
            memory: "1Gi"
          limits:
            cpu: "2"
            memory: "4Gi"
      volumes:
      - name: n8n-data
        persistentVolumeClaim:
          claimName: n8n-data-pvc # Requires a PVC for persistent storage
---
apiVersion: v1
kind: Service
metadata:
  name: n8n-workflow-engine
  namespace: industriverse
spec:
  selector:
    app: n8n-workflow-engine
  ports:
  - name: http
    port: 80
    targetPort: 5678
  type: ClusterIP # Use LoadBalancer or Ingress for external access
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: n8n-data-pvc
  namespace: industriverse
spec:
  accessModes:
    - ReadWriteOnce # Or ReadWriteMany if using shared storage for HA
  resources:
    requests:
      storage: 10Gi # Adjust size as needed
  # storageClassName: standard # Specify your storage class
```

## Best Practices

1.  **Keep Workflows Focused**: Design workflows to perform specific, well-defined tasks.
2.  **Use Sub-Workflows**: Break down complex processes into smaller, reusable sub-workflows.
3.  **Idempotency**: Design steps to be idempotent where possible, allowing safe retries.
4.  **Clear Naming**: Use descriptive names for workflows and steps.
5.  **Error Handling**: Implement comprehensive error handling and logging.
6.  **Version Control**: Store workflow definitions in a version control system (e.g., Git).
7.  **Parameterize**: Use variables and parameters for flexibility instead of hardcoding values.
8.  **Security**: Secure triggers (especially webhooks) and ensure workflows run with appropriate permissions.
9.  **Monitor**: Actively monitor workflow execution and performance.
10. **Documentation**: Document the purpose, triggers, inputs, outputs, and logic of each workflow.

## Troubleshooting

-   **Workflow Not Triggering**: Check trigger configuration (event names, schedules, webhook URLs, permissions).
-   **Workflow Failing**: Examine execution logs for specific error messages. Test individual nodes/steps.
-   **Incorrect Output**: Debug step logic, check input data transformations, verify API responses from integrated services.
-   **Performance Issues**: Analyze execution times of individual steps. Optimize slow steps (e.g., inefficient queries, long-running API calls).
-   **State Management Problems**: Ensure the state persistence mechanism (database, volume) is working correctly.
-   **n8n Issues**: Consult n8n documentation, check container logs, verify resource allocation.

## Next Steps

-   Explore the [UI/UX Layer Guide](08_ui_ux_layer_guide.md) for details on triggering and visualizing workflows.
-   See the [Overseer System Guide](11_overseer_system_guide.md) for monitoring workflow execution.
-   Consult the [Integration Guide](12_integration_guide.md) for patterns on integrating workflows across the framework.

## Related Guides

-   [Protocol Layer Guide](06_protocol_layer_guide.md)
-   [Application Layer Guide](05_application_layer_guide.md)
-   [Overseer System Guide](11_overseer_system_guide.md)

