# n8n Integration Guide

## Overview

The Industriverse Workflow Automation Layer provides seamless integration with n8n, enabling human-in-the-loop capabilities and visual workflow design. This guide explains how to integrate n8n with the Workflow Automation Layer, configure bidirectional communication, and leverage the full capabilities of both systems.

## Architecture

The integration between the Workflow Automation Layer and n8n follows a bridge architecture:

```
┌─────────────────────────┐      ┌───────────────────┐
│                         │      │                   │
│  Workflow Automation    │◄────►│       n8n         │
│        Layer            │      │                   │
│                         │      │                   │
└─────────────────────────┘      └───────────────────┘
           ▲                              ▲
           │                              │
           ▼                              ▼
┌─────────────────────────┐      ┌───────────────────┐
│                         │      │                   │
│  Industriverse Agents   │      │    n8n Users      │
│                         │      │                   │
└─────────────────────────┘      └───────────────────┘
```

### Key Components

1. **n8n Connector**: Core module for connecting to n8n instances
2. **n8n Bridge Service**: Service for managing bidirectional communication
3. **n8n Adapter Agent**: Agent for translating between Industriverse and n8n
4. **n8n Sync Bridge Agent**: Agent for synchronizing workflow definitions
5. **Industriverse Nodes Plugin**: Custom n8n nodes for Industriverse integration

## Setup and Configuration

### Prerequisites

- Running n8n instance (v0.214.0 or later)
- Industriverse Workflow Automation Layer
- Network connectivity between the two systems

### Configuration Steps

1. **Configure n8n Connection**

Create a configuration file `n8n_config.json`:

```json
{
  "n8n_url": "https://your-n8n-instance.example.com",
  "api_key": "your-n8n-api-key",
  "webhook_base_url": "https://your-industriverse-instance.example.com/webhooks/n8n",
  "sync_interval_seconds": 60,
  "connection_timeout_seconds": 30
}
```

2. **Install Industriverse Nodes Plugin**

```bash
cd /path/to/n8n
npm install n8n-nodes-industriverse
```

3. **Configure Workflow Automation Layer**

Update your Workflow Automation Layer configuration to include n8n integration:

```yaml
workflow_automation:
  n8n_integration:
    enabled: true
    config_path: "/path/to/n8n_config.json"
    auto_sync: true
    default_execution_mode: "human_in_the_loop"
```

4. **Restart Services**

Restart both n8n and the Workflow Automation Layer to apply the configuration.

## Integration Patterns

### 1. Human-in-the-Loop Workflows

This pattern allows for human intervention in automated workflows:

1. Workflow starts in the Workflow Automation Layer
2. At decision points requiring human input, the workflow transitions to n8n
3. Human operators interact with the workflow through n8n's visual interface
4. After human input, the workflow continues in the Workflow Automation Layer

Example configuration in workflow manifest:

```yaml
tasks:
  - task_id: "human-approval-task"
    name: "Human Approval"
    description: "Requires human approval before proceeding"
    agent_id: "n8n-adapter-agent"
    task_type: "human_approval"
    parameters:
      n8n_workflow_id: "approval-workflow"
      timeout_seconds: 3600
      escalation_policy: "manager_escalation"
```

### 2. Visual Workflow Design

This pattern allows workflows to be designed visually in n8n and executed in the Workflow Automation Layer:

1. Design workflow in n8n's visual editor
2. Sync workflow to Workflow Automation Layer
3. Execute workflow in Workflow Automation Layer with full agent capabilities
4. Monitor execution through n8n or Workflow Automation Layer UI

Example n8n to Industriverse workflow synchronization:

```javascript
// In n8n custom node
const industriverse = new IndustriverseSdk();
await industriverse.syncWorkflow({
  n8n_workflow_id: "123",
  target_layer: "workflow_automation",
  execution_mode: "autonomous"
});
```

### 3. Hybrid Execution

This pattern allows parts of a workflow to execute in n8n and parts in the Workflow Automation Layer:

1. Define workflow segments in both systems
2. Use bridge nodes to transition between systems
3. Share context and data between the systems
4. Coordinate execution and handle errors across systems

Example hybrid workflow configuration:

```yaml
cross_layer_integration:
  n8n_integration:
    hybrid_execution:
      enabled: true
      context_sharing: true
      error_propagation: true
      segments:
        - system: "n8n"
          workflow_id: "data-preparation"
          next_segment: "data-analysis"
        - system: "industriverse"
          workflow_id: "data-analysis"
          next_segment: "result-visualization"
        - system: "n8n"
          workflow_id: "result-visualization"
```

## Custom n8n Nodes

The Industriverse Nodes Plugin provides several custom nodes for n8n:

### 1. Industriverse Trigger

Starts a workflow when triggered by the Industriverse Workflow Automation Layer.

**Configuration:**
- Webhook Path: Path for the webhook endpoint
- Authentication: API key or token
- Payload Schema: Expected data structure

### 2. Industriverse Workflow

Executes a workflow in the Industriverse Workflow Automation Layer.

**Configuration:**
- Workflow ID: ID of the workflow to execute
- Input Parameters: Data to pass to the workflow
- Execution Mode: Autonomous, supervised, or manual
- Wait for Completion: Whether to wait for workflow completion

### 3. Industriverse Agent

Interacts with a specific agent in the Industriverse ecosystem.

**Configuration:**
- Agent ID: ID of the agent to interact with
- Action: Action to perform (e.g., query, command)
- Parameters: Action-specific parameters
- Timeout: Maximum time to wait for response

### 4. Industriverse Data

Accesses data from the Industriverse Data Layer.

**Configuration:**
- Data Source: Source to query
- Query: Data query specification
- Transformation: Optional data transformation

## Bidirectional Communication

The integration supports bidirectional communication between the Workflow Automation Layer and n8n:

### Industriverse to n8n

1. **Webhook Triggers**: Industriverse can trigger n8n workflows via webhooks
2. **Data Pushing**: Industriverse can push data to n8n workflows
3. **Status Updates**: Industriverse can send status updates to n8n

Example webhook trigger:

```python
async def trigger_n8n_workflow(workflow_id, data):
    n8n_connector = N8nConnector(config_path="/path/to/n8n_config.json")
    response = await n8n_connector.trigger_webhook(
        webhook_path=f"webhook/{workflow_id}",
        data=data
    )
    return response
```

### n8n to Industriverse

1. **Workflow Execution**: n8n can execute Industriverse workflows
2. **Agent Interaction**: n8n can interact with Industriverse agents
3. **Data Querying**: n8n can query data from Industriverse

Example workflow execution from n8n:

```javascript
// In n8n workflow
const response = await $node["Industriverse Workflow"].execute({
  workflow_id: "predictive-maintenance-workflow",
  input: {
    equipment_id: "pump-123",
    analysis_type: "vibration"
  },
  execution_mode: "autonomous"
});
```

## Trust-Aware Integration

The integration supports trust-aware execution modes:

1. **High Trust**: Fully autonomous execution with minimal human intervention
2. **Medium Trust**: Supervised execution with human approval for critical steps
3. **Low Trust**: Manual execution with human involvement throughout

Example trust-aware configuration:

```yaml
execution_modes:
  default_mode: "supervised"
  trust_thresholds:
    high_trust: 0.8
    medium_trust: 0.5
    low_trust: 0.2
  mode_mapping:
    high_trust: "autonomous"
    medium_trust: "supervised"
    low_trust: "manual"
  n8n_integration:
    high_trust_mode: "background"
    medium_trust_mode: "interactive"
    low_trust_mode: "manual_start"
```

## Debugging and Troubleshooting

### Common Issues

1. **Connection Issues**
   - Check network connectivity between systems
   - Verify API key and URL configuration
   - Check firewall settings

2. **Synchronization Issues**
   - Check sync logs in both systems
   - Verify webhook configurations
   - Check for schema compatibility issues

3. **Execution Issues**
   - Check execution logs in both systems
   - Verify data format compatibility
   - Check for timeout or resource constraints

### Debugging Tools

1. **n8n Console**
   - Access execution logs in n8n
   - Use the built-in debugger for workflow testing

2. **Workflow Automation Layer Logs**
   - Check the n8n integration logs
   - Use the Capsule Debug Trace system for detailed analysis

3. **Integration Test Tools**
   - Use the provided test scripts to verify integration
   - Check connectivity with the `test_n8n_connection.py` script

## Best Practices

1. **Workflow Design**
   - Design workflows with clear boundaries between systems
   - Use appropriate error handling in both systems
   - Consider latency in cross-system communication

2. **Security**
   - Use secure API keys and rotate them regularly
   - Implement proper authentication for webhooks
   - Limit permissions to only what's necessary

3. **Performance**
   - Optimize data transfer between systems
   - Use appropriate timeouts for cross-system operations
   - Consider caching for frequently accessed data

4. **Monitoring**
   - Set up monitoring for integration health
   - Configure alerts for integration failures
   - Regularly review integration logs

## Example: Complete Integration Workflow

This example demonstrates a complete integration between the Workflow Automation Layer and n8n for a predictive maintenance scenario:

1. **Workflow Automation Layer**: Collects and analyzes sensor data
2. **n8n**: Provides human interface for maintenance scheduling
3. **Workflow Automation Layer**: Executes the maintenance workflow

### Step 1: Configure Integration

```yaml
# Workflow Automation Layer configuration
n8n_integration:
  enabled: true
  config_path: "/config/n8n_config.json"
  sync_workflows:
    - workflow_id: "predictive-maintenance"
      n8n_workflow_id: "maintenance-scheduling"
```

### Step 2: Define Workflow in Workflow Automation Layer

```yaml
# Workflow manifest
workflow_id: "predictive-maintenance"
name: "Predictive Maintenance Workflow"
tasks:
  - task_id: "sensor-data-collection"
    agent_id: "data-collection-agent"
    # ...
  - task_id: "anomaly-detection"
    agent_id: "anomaly-detection-agent"
    # ...
  - task_id: "maintenance-scheduling"
    agent_id: "n8n-adapter-agent"
    task_type: "n8n_workflow"
    parameters:
      n8n_workflow_id: "maintenance-scheduling"
      wait_for_completion: true
```

### Step 3: Define Workflow in n8n

Create a workflow in n8n with:
1. Industriverse Trigger node to receive anomaly data
2. Human input nodes for maintenance scheduling
3. Industriverse Workflow node to send the schedule back

### Step 4: Test and Deploy

1. Test the integration with sample data
2. Monitor execution across both systems
3. Deploy to production environment

## Conclusion

The integration between the Workflow Automation Layer and n8n provides powerful capabilities for human-in-the-loop workflows, visual workflow design, and hybrid execution. By following this guide, you can leverage the strengths of both systems to create robust, flexible, and user-friendly workflow automation solutions.

## Additional Resources

- [n8n Documentation](https://docs.n8n.io/)
- [Industriverse Nodes Plugin Documentation](https://docs.industriverse.example.com/n8n-nodes)
- [Workflow Automation Layer API Reference](https://docs.industriverse.example.com/workflow-automation/api)
- [Integration Examples Repository](https://github.com/industriverse/n8n-integration-examples)
