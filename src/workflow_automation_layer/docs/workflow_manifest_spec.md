# Workflow Manifest Specification

## Overview

The Workflow Manifest is the core definition format for workflows in the Industriverse Workflow Automation Layer. It provides a declarative way to define workflow structure, task relationships, execution constraints, and integration points with other Industriverse layers.

This specification defines the schema, validation rules, and best practices for creating workflow manifests that leverage the full capabilities of the Workflow Automation Layer.

## Schema Definition

A workflow manifest is a JSON or YAML document with the following top-level structure:

```json
{
  "workflow_id": "string",
  "name": "string",
  "version": "string",
  "description": "string",
  "industry_context": "string",
  "tags": ["string"],
  "tasks": [],
  "execution_graph": {},
  "task_timeouts": {},
  "retry_strategies": {},
  "error_handling": {},
  "execution_modes": {},
  "mesh_topology": {},
  "debug_trace_config": {},
  "escalation_protocol": {},
  "dtsl_embedding": {},
  "cross_layer_integration": {}
}
```

### Core Properties

#### `workflow_id` (required)
- Unique identifier for the workflow
- Format: UUID v4 or custom string (must be unique within the system)
- Example: `"workflow-123e4567-e89b-12d3-a456-426614174000"`

#### `name` (required)
- Human-readable name for the workflow
- Example: `"Predictive Maintenance Workflow"`

#### `version` (required)
- Semantic version of the workflow
- Format: `major.minor.patch`
- Example: `"1.0.0"`

#### `description` (optional)
- Detailed description of the workflow's purpose and behavior
- Example: `"This workflow monitors equipment sensors, predicts maintenance needs, and schedules service appointments."`

#### `industry_context` (optional)
- Industry vertical this workflow is designed for
- Example: `"manufacturing"`, `"logistics"`, `"energy"`, `"retail"`

#### `tags` (optional)
- Array of strings for categorization and filtering
- Example: `["predictive-maintenance", "iot", "manufacturing"]`

### Task Definitions

#### `tasks` (required)
- Array of task definitions that make up the workflow
- Each task has the following structure:

```json
{
  "task_id": "string",
  "name": "string",
  "description": "string",
  "agent_id": "string",
  "task_type": "string",
  "parameters": {},
  "inputs": [],
  "outputs": [],
  "constraints": {},
  "execution_mode": "string",
  "debug_trace_level": "string"
}
```

- **task_id** (required): Unique identifier for the task within the workflow
- **name** (required): Human-readable name for the task
- **description** (optional): Detailed description of the task's purpose
- **agent_id** (required): ID of the agent responsible for executing this task
- **task_type** (required): Type of task (e.g., "data_processing", "decision", "notification")
- **parameters** (optional): Task-specific configuration parameters
- **inputs** (optional): Array of input definitions (data required by the task)
- **outputs** (optional): Array of output definitions (data produced by the task)
- **constraints** (optional): Execution constraints for the task
- **execution_mode** (optional): Override of the default execution mode
- **debug_trace_level** (optional): Override of the default debug trace level

### Execution Graph

#### `execution_graph` (required)
- Defines the execution flow between tasks
- Structure:

```json
{
  "node_id": {
    "task_id": "string",
    "next": ["node_id"],
    "condition": "expression",
    "parallel_tasks": ["task_id"],
    "join_type": "string"
  }
}
```

- **node_id**: Unique identifier for the execution node
- **task_id**: ID of the task to execute at this node
- **next**: Array of node IDs to execute after this node
- **condition**: Expression that determines whether to follow a path (for conditional branching)
- **parallel_tasks**: Array of task IDs to execute in parallel
- **join_type**: Type of join for parallel execution ("all", "any", "n_of_m")

### Execution Configuration

#### `task_timeouts` (optional)
- Defines timeout durations for tasks
- Structure: `{"task_id": timeout_in_seconds}`
- Example: `{"data-processing-task": 300}`

#### `retry_strategies` (optional)
- Defines retry behavior for failed tasks
- Structure:

```json
{
  "task_id": {
    "max_retries": 3,
    "initial_delay": 5,
    "backoff_factor": 2,
    "max_delay": 60
  }
}
```

#### `error_handling` (optional)
- Defines how errors are handled for specific tasks
- Structure:

```json
{
  "task_id": {
    "on_failure": "abort|continue|retry|compensate",
    "compensation_task_id": "string",
    "error_notification": {
      "channels": ["email", "slack"],
      "recipients": ["user@example.com"]
    }
  }
}
```

### Advanced Features

#### `execution_modes` (optional)
- Defines trust-aware execution modes for the workflow
- Structure:

```json
{
  "default_mode": "string",
  "trust_thresholds": {
    "high_trust": 0.8,
    "medium_trust": 0.5,
    "low_trust": 0.2
  },
  "mode_mapping": {
    "high_trust": "autonomous",
    "medium_trust": "supervised",
    "low_trust": "manual"
  },
  "confidence_levels": {
    "high": 0.9,
    "medium": 0.7,
    "low": 0.4
  },
  "regulatory_constraints": {
    "require_human_review": ["task_id"],
    "audit_trail_required": true
  }
}
```

#### `mesh_topology` (optional)
- Defines the agent mesh topology for the workflow
- Structure:

```json
{
  "topology_type": "string",
  "edge_execution": {
    "enabled": true,
    "fallback_policy": "string"
  },
  "routing_constraints": {
    "task_id": {
      "preferred_agents": ["agent_id"],
      "excluded_agents": ["agent_id"],
      "location_constraints": ["edge", "cloud"]
    }
  }
}
```

#### `debug_trace_config` (optional)
- Configures the Capsule Debug Trace system for the workflow
- Structure:

```json
{
  "default_trace_level": "minimal|standard|verbose|forensic",
  "capture_inputs": true,
  "capture_outputs": true,
  "capture_parameters": true,
  "capture_agent_reasoning": true,
  "retention_period_days": 30,
  "forensics_enabled": true
}
```

#### `escalation_protocol` (optional)
- Defines the AI-driven escalation logic for the workflow
- Structure:

```json
{
  "default_escalation_policy": "string",
  "escalation_levels": [
    {
      "level": 1,
      "conditions": ["expression"],
      "actions": ["action"],
      "timeout_seconds": 300
    }
  ],
  "bid_system": {
    "enabled": true,
    "bid_timeout_seconds": 30,
    "selection_criteria": "lowest_bid|highest_capability|balanced"
  }
}
```

#### `dtsl_embedding` (optional)
- Configuration for embedding the workflow in DTSL twin definitions
- Structure:

```json
{
  "enabled": true,
  "twin_id": "string",
  "activation_triggers": ["trigger"],
  "twin_property_mappings": {
    "workflow_input": "twin_property",
    "workflow_output": "twin_property"
  },
  "edge_execution_config": {
    "enabled": true,
    "resource_constraints": {}
  }
}
```

#### `cross_layer_integration` (optional)
- Defines integration points with other Industriverse layers
- Structure:

```json
{
  "protocol_layer": {
    "mcp_integration": {
      "enabled": true,
      "channels": ["channel"]
    },
    "a2a_integration": {
      "enabled": true,
      "agent_discovery": true
    }
  },
  "data_layer": {
    "data_sources": ["source"],
    "data_sinks": ["sink"]
  },
  "core_ai_layer": {
    "model_endpoints": ["endpoint"]
  },
  "generative_layer": {
    "template_ids": ["template_id"]
  },
  "application_layer": {
    "app_ids": ["app_id"]
  }
}
```

## Validation Rules

1. **Workflow ID Uniqueness**: Each workflow must have a unique `workflow_id`
2. **Task ID Uniqueness**: Each task within a workflow must have a unique `task_id`
3. **Execution Graph Integrity**: 
   - All referenced `task_id` values must exist in the `tasks` array
   - The execution graph must not contain cycles
   - There must be at least one entry point (node with no incoming edges)
   - There must be at least one exit point (node with no outgoing edges)
4. **Required Fields**: All required fields must be present and non-empty
5. **Semantic Versioning**: The `version` field must follow semantic versioning format
6. **Execution Mode Validity**: All referenced execution modes must be defined
7. **Agent Existence**: All referenced `agent_id` values must correspond to existing agents
8. **DTSL Twin Existence**: If `dtsl_embedding` is enabled, the referenced `twin_id` must exist

## Best Practices

1. **Descriptive Naming**: Use clear, descriptive names for workflows and tasks
2. **Appropriate Granularity**: Design tasks with appropriate granularity (not too fine or coarse)
3. **Error Handling**: Define comprehensive error handling for critical tasks
4. **Timeouts**: Set appropriate timeouts for all tasks, especially those involving external systems
5. **Documentation**: Use description fields to document the purpose and behavior of workflows and tasks
6. **Versioning**: Increment the version number appropriately when making changes
7. **Tagging**: Use tags for categorization and to aid in discovery
8. **Trust-Aware Design**: Configure execution modes based on trust requirements
9. **Debug Tracing**: Enable appropriate debug trace levels based on workflow criticality
10. **Cross-Layer Integration**: Define integration points with other layers for seamless operation

## Example Workflow Manifest

```json
{
  "workflow_id": "predictive-maintenance-workflow-001",
  "name": "Manufacturing Equipment Predictive Maintenance",
  "version": "1.0.0",
  "description": "Monitors equipment sensors, predicts maintenance needs, and schedules service appointments",
  "industry_context": "manufacturing",
  "tags": ["predictive-maintenance", "iot", "manufacturing"],
  "tasks": [
    {
      "task_id": "sensor-data-collection",
      "name": "Collect Sensor Data",
      "description": "Collect real-time sensor data from manufacturing equipment",
      "agent_id": "data-collection-agent",
      "task_type": "data_collection",
      "parameters": {
        "data_sources": ["equipment-sensors"],
        "collection_interval_seconds": 60
      },
      "outputs": [
        {
          "name": "sensor_data",
          "schema": "sensor_data_schema"
        }
      ]
    },
    {
      "task_id": "anomaly-detection",
      "name": "Detect Anomalies",
      "description": "Analyze sensor data to detect anomalies indicating potential equipment issues",
      "agent_id": "anomaly-detection-agent",
      "task_type": "analysis",
      "parameters": {
        "detection_algorithm": "isolation_forest",
        "sensitivity": 0.8
      },
      "inputs": [
        {
          "name": "sensor_data",
          "source_task_id": "sensor-data-collection",
          "source_output": "sensor_data"
        }
      ],
      "outputs": [
        {
          "name": "anomalies",
          "schema": "anomaly_schema"
        }
      ]
    }
  ],
  "execution_graph": {
    "start": {
      "task_id": "sensor-data-collection",
      "next": ["anomaly-detection-node"]
    },
    "anomaly-detection-node": {
      "task_id": "anomaly-detection",
      "next": []
    }
  },
  "task_timeouts": {
    "sensor-data-collection": 120,
    "anomaly-detection": 300
  },
  "retry_strategies": {
    "sensor-data-collection": {
      "max_retries": 3,
      "initial_delay": 5,
      "backoff_factor": 2,
      "max_delay": 60
    }
  },
  "execution_modes": {
    "default_mode": "autonomous",
    "trust_thresholds": {
      "high_trust": 0.8,
      "medium_trust": 0.5,
      "low_trust": 0.2
    },
    "mode_mapping": {
      "high_trust": "autonomous",
      "medium_trust": "supervised",
      "low_trust": "manual"
    }
  },
  "debug_trace_config": {
    "default_trace_level": "standard",
    "capture_inputs": true,
    "capture_outputs": true,
    "forensics_enabled": true
  }
}
```

## Compatibility with Other Specifications

The Workflow Manifest Specification is designed to work seamlessly with other Industriverse specifications:

1. **DTSL (Digital Twin Swarm Language)**: Workflows can be embedded in DTSL twin definitions
2. **Unified Message Envelope**: Workflow tasks communicate using the Unified Message Envelope format
3. **Cross-Mesh Federation**: Workflows can span multiple mesh instances through federation
4. **Agent Reflex Timers**: Tasks can leverage reflex timers for time-sensitive operations
5. **Protocol Kernel Intelligence**: Workflows integrate with the PKI for intent-aware routing

## Version History

- **1.0.0** (2025-05-22): Initial specification
