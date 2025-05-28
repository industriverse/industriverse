# Workflow Automation Layer Documentation

## Overview

The Workflow Automation Layer serves as the "executive brain" of the Industriverse ecosystem, orchestrating intelligent, adaptive workflows across all layers of the Industrial Foundry Framework. This layer enables seamless automation of industrial processes while maintaining human oversight where needed, adapting to changing conditions, and continuously optimizing workflow execution.

## Architecture

The Workflow Automation Layer consists of several key components:

### Core Workflow Engine

The Core Workflow Engine is responsible for workflow execution, management, and optimization. It includes:

- **Workflow Runtime**: Executes workflow tasks according to defined manifests
- **Workflow Manifest Parser**: Parses and validates workflow definitions
- **Task Contract Manager**: Manages task contracts and ensures proper execution
- **Workflow Registry**: Maintains a registry of available workflows
- **Workflow Telemetry**: Collects and processes workflow execution metrics
- **Execution Mode Manager**: Manages trust-aware execution modes
- **Mesh Topology Manager**: Manages agent mesh topology and routing
- **Capsule Debug Trace Manager**: Provides comprehensive debugging capabilities

### Agent Framework

The Agent Framework provides the foundation for intelligent agents that participate in workflows:

- **Base Agent**: Foundation class for all workflow agents
- **Workflow Trigger Agent**: Initiates workflows based on events or conditions
- **Workflow Contract Parser**: Parses and validates workflow contracts
- **Human Intervention Agent**: Manages human-in-the-loop interactions
- **Capsule Workflow Controller**: Controls workflow execution within agent capsules
- **n8n Synchronization Bridge**: Bridges between native workflows and n8n
- **Workflow Optimizer**: Continuously optimizes workflow execution

### n8n Integration

The n8n Integration layer enables seamless integration with the n8n workflow automation platform:

- **n8n Connector**: Core connector for bidirectional communication
- **n8n Bridge Service**: Service for synchronizing workflows
- **n8n Node Definitions**: Custom node definitions for Industriverse
- **n8n Workflow Templates**: Pre-defined workflow templates
- **Industriverse Nodes Plugin**: Plugin for extending n8n with Industriverse capabilities

### Industry-Specific Templates

The layer includes industry-specific workflow templates for:

- **Manufacturing**: Predictive maintenance, quality control, etc.
- **Logistics**: Supply chain visibility, warehouse optimization, etc.
- **Energy**: Smart grid management, renewable energy integration, etc.
- **Retail**: Inventory management, customer experience, etc.

### UI and Visualization

The UI and visualization components provide intuitive interfaces for workflow management:

- **Dynamic Agent Capsule**: Floating, adaptive UI nodes for agent interaction
- **Workflow Visualization**: Visualization tools for workflow execution and monitoring

### Security and Compliance

The security and compliance features ensure secure and compliant workflow execution:

- **Trust-Aware Security Manager**: Enforces trust-aware execution policies
- **Compliance Manager**: Ensures compliance with regulatory requirements
- **Audit Logger**: Provides comprehensive audit logging
- **EKIS Security Integration**: Integrates with the EKIS security framework
- **Observability Manager**: Provides observability features for workflows

## Key Features

### Trust-Aware Execution Modes

The Workflow Automation Layer implements trust-aware execution modes that dynamically adjust based on trust scores and confidence levels:

- **Reactive Mode**: Waits for explicit triggers before executing workflows
- **Proactive Mode**: Can initiate workflows based on predicted needs
- **Autonomous Mode**: Can make decisions and execute workflows independently

Each mode has configurable trust and confidence thresholds, as well as human oversight requirements.

### Agent Mesh Topology and Routing

The layer implements a flexible agent mesh topology with configurable routing constraints:

- **Hybrid Mesh**: Supports both centralized and decentralized execution
- **Edge Capabilities**: Enables workflow execution at the edge
- **Trust-Based Routing**: Routes tasks based on trust scores
- **Fallback Paths**: Provides fallback paths for reliability

### DTSL Workflow Embedding

Workflows can be defined directly within DTSL twin configurations, enabling:

- **Edge-Native Autonomy**: Autonomous workflow execution at the edge
- **Twin-Sourced Self-Coordination**: Coordination between digital twins
- **Contextual Workflow Adaptation**: Adaptation based on twin context

### Capsule Debug Trace Schema

The layer includes a comprehensive debug trace schema for workflow debugging:

- **Step-by-Step Agent Logs**: Detailed logs of agent actions
- **Pattern-Based Optimization**: Identification of optimization opportunities
- **AI Workflow Forensics Engine**: AI-powered workflow analysis

### AI-Driven Escalation Logic

The layer implements AI-driven escalation logic for handling exceptions:

- **Dynamic Role Assignment**: Assigns roles based on agent capabilities
- **Bid System**: Enables agents to bid for task execution
- **Real-Time Agent Market**: Creates a market for agent services

## Deployment

### Prerequisites

- Kubernetes cluster (v1.22+)
- Helm (v3.8+)
- Access to container registry
- Persistent storage for workflow data

### Kubernetes Deployment

The Workflow Automation Layer can be deployed using the provided Kubernetes manifests:

1. Create the namespace:
   ```bash
   kubectl create namespace industriverse
   ```

2. Apply the ConfigMap:
   ```bash
   kubectl apply -f kubernetes/configmap.yaml
   ```

3. Create the required secrets:
   ```bash
   kubectl create secret generic workflow-automation-secrets \
     --from-literal=db_user=workflow_user \
     --from-literal=db_password=<password> \
     --from-literal=api_key=<api_key> \
     --from-literal=ekis_api_key=<ekis_api_key> \
     -n industriverse
   ```

4. Apply the storage configuration:
   ```bash
   kubectl apply -f kubernetes/storage.yaml
   ```

5. Apply the deployment:
   ```bash
   kubectl apply -f kubernetes/deployment.yaml
   ```

6. Apply the service:
   ```bash
   kubectl apply -f kubernetes/service.yaml
   ```

### Configuration

The Workflow Automation Layer can be configured using the following ConfigMap keys:

- `log_level`: Logging level (default: "info")
- `execution_mode`: Default execution mode (default: "standard")
- `protocol_layer_url`: URL of the Protocol Layer service
- `n8n_api_url`: URL of the n8n API
- `ekis_security_enabled`: Whether EKIS security is enabled
- `trust_threshold`: Default trust threshold
- `confidence_threshold`: Default confidence threshold
- `mesh_topology_config`: Configuration for mesh topology
- `execution_modes_config`: Configuration for execution modes
- `debug_trace_config`: Configuration for debug tracing

## Integration with Other Layers

### Protocol Layer Integration

The Workflow Automation Layer integrates with the Protocol Layer through:

- **MCP/A2A Standards**: Uses MCP/A2A for communication
- **Protocol Kernel Intelligence**: Leverages PKI for intent-aware routing
- **Self-Healing Fabric**: Utilizes the self-healing protocol fabric

### Core AI Layer Integration

Integration with the Core AI Layer enables:

- **Intelligent Decision Making**: Leverages AI for workflow decisions
- **Predictive Analytics**: Uses predictive models for proactive workflows
- **Semantic Understanding**: Understands workflow context and requirements

### Application Layer Integration

The layer integrates with the Application Layer to:

- **Automate Application Workflows**: Automates workflows within applications
- **Provide Workflow Services**: Offers workflow services to applications
- **Enable Human-in-the-Loop**: Facilitates human interaction with workflows

## Development Guide

### Creating Custom Workflows

Custom workflows can be created using workflow manifests:

```yaml
name: custom_workflow
description: "Custom workflow example"
version: "1.0"
tasks:
  - id: task1
    name: "Task 1"
    description: "First task"
    timeout_seconds: 300
    retry_count: 3
  - id: task2
    name: "Task 2"
    description: "Second task"
    timeout_seconds: 600
    retry_count: 2
workflow:
  transitions:
    - from: task1
      to: task2
      condition: "success"
execution_modes:
  - name: "reactive"
    trust_threshold: 0.5
    confidence_required: 0.6
    human_oversight: true
```

### Creating Custom Agents

Custom agents can be created by extending the BaseAgent class:

```python
from workflow_automation_layer.agents.base_agent import BaseAgent

class CustomAgent(BaseAgent):
    def __init__(self, agent_id, name):
        super().__init__(agent_id, name, "custom")
        
    async def process_task(self, task):
        # Custom task processing logic
        result = await self._perform_custom_operation(task)
        return result
        
    async def _perform_custom_operation(self, task):
        # Implementation of custom operation
        pass
```

### Integrating with n8n

Custom n8n nodes can be created using the Industriverse nodes plugin:

```typescript
import { INodeType, INodeTypeDescription } from 'n8n-workflow';

export class IndustriverseTrigger implements INodeType {
    description: INodeTypeDescription = {
        displayName: 'Industriverse Trigger',
        name: 'industriverseTrigger',
        group: ['trigger'],
        version: 1,
        description: 'Starts the workflow when an Industriverse event occurs',
        defaults: {
            name: 'Industriverse Trigger',
        },
        inputs: [],
        outputs: ['main'],
        credentials: [
            {
                name: 'industriverseTriggerApi',
                required: true,
            },
        ],
        properties: [
            // Node properties
        ],
    };

    async execute() {
        // Node execution logic
    }
}
```

## Best Practices

### Workflow Design

- **Start Simple**: Begin with simple workflows and gradually add complexity
- **Use Templates**: Leverage industry-specific templates as starting points
- **Define Clear Transitions**: Ensure workflow transitions are clearly defined
- **Include Error Handling**: Add error handling for all critical tasks
- **Implement Timeouts**: Set appropriate timeouts for all tasks
- **Enable Retries**: Configure retry policies for transient failures
- **Document Workflows**: Provide clear documentation for all workflows

### Trust and Confidence Management

- **Set Appropriate Thresholds**: Configure trust and confidence thresholds based on criticality
- **Monitor Trust Scores**: Regularly monitor trust scores and adjust as needed
- **Implement Human Oversight**: Ensure human oversight for critical decisions
- **Use Gradual Autonomy**: Gradually increase autonomy as trust is established
- **Audit Execution Modes**: Regularly audit execution mode transitions

### Security and Compliance

- **Follow Least Privilege**: Apply the principle of least privilege
- **Encrypt Sensitive Data**: Ensure sensitive data is encrypted
- **Implement Audit Logging**: Maintain comprehensive audit logs
- **Regularly Review Compliance**: Regularly review compliance with regulations
- **Conduct Security Assessments**: Perform regular security assessments

## Troubleshooting

### Common Issues

#### Workflow Execution Failures

- **Check Task Contracts**: Ensure task contracts are properly defined
- **Verify Dependencies**: Check that all dependencies are available
- **Review Execution Logs**: Examine execution logs for errors
- **Check Trust Scores**: Verify that trust scores meet thresholds
- **Inspect Mesh Routing**: Check mesh routing configuration

#### n8n Integration Issues

- **Verify API Connectivity**: Ensure connectivity to n8n API
- **Check Authentication**: Verify authentication credentials
- **Review Node Definitions**: Check custom node definitions
- **Inspect Bridge Logs**: Examine bridge service logs

#### Security and Compliance Issues

- **Review Policies**: Check security and compliance policies
- **Verify EKIS Integration**: Ensure EKIS integration is working
- **Inspect Audit Logs**: Review audit logs for anomalies
- **Check Trust Enforcement**: Verify trust policy enforcement

## API Reference

### Workflow Engine API

#### Create Workflow

```
POST /api/workflows
Content-Type: application/json

{
  "name": "example_workflow",
  "description": "Example workflow",
  "version": "1.0",
  "tasks": [...],
  "workflow": {...},
  "execution_modes": [...]
}
```

#### Start Workflow

```
POST /api/workflows/{workflow_id}/start
Content-Type: application/json

{
  "input_parameters": {...},
  "execution_mode": "reactive"
}
```

#### Get Workflow Status

```
GET /api/workflows/{workflow_id}/status
```

### Agent API

#### Register Agent

```
POST /api/agents
Content-Type: application/json

{
  "name": "example_agent",
  "type": "custom",
  "capabilities": [...],
  "trust_score": 0.8,
  "confidence_score": 0.9
}
```

#### Assign Task to Agent

```
POST /api/agents/{agent_id}/tasks
Content-Type: application/json

{
  "task_id": "task123",
  "workflow_id": "workflow456",
  "parameters": {...},
  "deadline": "2025-06-01T12:00:00Z"
}
```

### n8n Integration API

#### Sync Workflow with n8n

```
POST /api/n8n/sync
Content-Type: application/json

{
  "workflow_id": "workflow123",
  "n8n_workflow_id": "n8n456",
  "sync_direction": "bidirectional"
}
```

## Glossary

- **Workflow**: A sequence of tasks that achieves a specific goal
- **Task**: A unit of work within a workflow
- **Agent**: An entity that performs tasks within workflows
- **Execution Mode**: A mode of operation with specific trust and confidence requirements
- **Trust Score**: A measure of the reliability of an agent or workflow
- **Confidence Score**: A measure of the certainty of a decision or prediction
- **Mesh Topology**: The structure of connections between agents
- **DTSL**: Digital Twin Swarm Language
- **Capsule**: A UI component representing an agent or workflow
- **n8n**: An open-source workflow automation platform
