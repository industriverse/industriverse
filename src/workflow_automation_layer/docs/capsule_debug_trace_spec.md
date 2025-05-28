# Capsule Debug Trace Specification

## Overview

The Capsule Debug Trace system provides comprehensive debugging, monitoring, and forensic analysis capabilities for workflows in the Industriverse Workflow Automation Layer. It enables step-by-step tracing of workflow execution, agent decision-making, and data transformations, supporting both real-time debugging and post-execution analysis.

This specification defines the schema, configuration options, and best practices for implementing and using the Capsule Debug Trace system.

## Architecture

The Capsule Debug Trace system consists of the following components:

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│                 Workflow Automation Layer               │
│                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │             │    │             │    │             │  │
│  │  Workflow   │    │    Task     │    │   Agent     │  │
│  │  Runtime    │    │  Execution  │    │  Framework  │  │
│  │             │    │             │    │             │  │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘  │
│         │                  │                  │         │
│         └──────────┬───────┴──────────┬───────┘         │
│                    │                  │                 │
│          ┌─────────▼──────────────────▼─────────┐       │
│          │                                      │       │
│          │       Capsule Debug Trace System     │       │
│          │                                      │       │
│          └─────────┬──────────────────┬─────────┘       │
│                    │                  │                 │
│          ┌─────────▼──────────┐ ┌─────▼─────────────┐   │
│          │                    │ │                   │   │
│          │   Trace Storage    │ │ Forensics Engine │   │
│          │                    │ │                   │   │
│          └─────────┬──────────┘ └─────────┬─────────┘   │
│                    │                      │             │
└────────────────────┼──────────────────────┼─────────────┘
                     │                      │
        ┌────────────▼──────────┐ ┌─────────▼─────────────┐
        │                       │ │                       │
        │   Visualization UI    │ │   Pattern Analysis    │
        │                       │ │                       │
        └───────────────────────┘ └───────────────────────┘
```

## Trace Schema

A debug trace is a structured record of workflow execution with the following schema:

```json
{
  "trace_id": "string",
  "workflow_id": "string",
  "workflow_instance_id": "string",
  "start_time": "string",
  "end_time": "string",
  "status": "string",
  "trace_level": "string",
  "spans": [],
  "metrics": {},
  "annotations": [],
  "context": {}
}
```

### Core Properties

#### `trace_id` (required)
- Unique identifier for the trace
- Format: UUID v4
- Example: `"trace-123e4567-e89b-12d3-a456-426614174000"`

#### `workflow_id` (required)
- Identifier of the workflow being traced
- Example: `"predictive-maintenance-workflow"`

#### `workflow_instance_id` (required)
- Identifier of the specific workflow instance
- Example: `"instance-123e4567-e89b-12d3-a456-426614174000"`

#### `start_time` (required)
- Start time of the trace
- Format: ISO 8601 datetime
- Example: `"2025-05-22T14:32:17.123Z"`

#### `end_time` (optional)
- End time of the trace
- Format: ISO 8601 datetime
- Example: `"2025-05-22T14:35:42.987Z"`

#### `status` (required)
- Status of the traced workflow
- Valid values: `"running"`, `"completed"`, `"failed"`, `"aborted"`
- Example: `"completed"`

#### `trace_level` (required)
- Level of detail in the trace
- Valid values: `"minimal"`, `"standard"`, `"verbose"`, `"forensic"`
- Example: `"standard"`

### Spans

Spans represent individual operations within the workflow:

```json
{
  "span_id": "string",
  "parent_span_id": "string",
  "name": "string",
  "type": "string",
  "start_time": "string",
  "end_time": "string",
  "status": "string",
  "task_id": "string",
  "agent_id": "string",
  "inputs": {},
  "outputs": {},
  "events": [],
  "logs": [],
  "agent_reasoning": {},
  "error": {}
}
```

- **span_id**: Unique identifier for the span
- **parent_span_id**: Identifier of the parent span (for nested operations)
- **name**: Human-readable name for the span
- **type**: Type of operation (task, agent_decision, data_transformation, etc.)
- **start_time**: Start time of the span
- **end_time**: End time of the span
- **status**: Status of the span (running, completed, failed, aborted)
- **task_id**: Identifier of the associated task (if applicable)
- **agent_id**: Identifier of the associated agent (if applicable)
- **inputs**: Input data for the operation
- **outputs**: Output data from the operation
- **events**: Significant events during the span
- **logs**: Log entries related to the span
- **agent_reasoning**: Agent reasoning process (for agent operations)
- **error**: Error details (if the span failed)

### Metrics

Metrics provide quantitative measurements of workflow execution:

```json
{
  "execution_time_ms": 3500,
  "cpu_usage_percent": 45.2,
  "memory_usage_mb": 128.5,
  "task_count": 12,
  "error_count": 0,
  "retry_count": 2,
  "custom_metrics": {}
}
```

### Annotations

Annotations provide additional context and metadata:

```json
{
  "annotation_id": "string",
  "timestamp": "string",
  "type": "string",
  "source": "string",
  "message": "string",
  "data": {}
}
```

### Context

Context provides additional information about the execution environment:

```json
{
  "environment": "string",
  "user_id": "string",
  "session_id": "string",
  "trust_context": {},
  "execution_mode": "string",
  "custom_context": {}
}
```

## Trace Levels

The Capsule Debug Trace system supports multiple trace levels:

### 1. Minimal
- Basic workflow execution information
- Task start/end times and status
- Error information for failed tasks
- Minimal memory and storage footprint

### 2. Standard
- All minimal level information
- Task inputs and outputs (sanitized)
- Agent decisions with basic reasoning
- Performance metrics
- Suitable for production monitoring

### 3. Verbose
- All standard level information
- Detailed agent reasoning
- Intermediate data transformations
- Detailed performance metrics
- Event logs and annotations
- Suitable for development and testing

### 4. Forensic
- All verbose level information
- Complete agent reasoning with alternatives
- Raw data captures at all stages
- System-level metrics
- Full context capture
- Suitable for incident investigation and compliance

## Configuration

The Capsule Debug Trace system is configured at multiple levels:

### 1. System Level

```yaml
capsule_debug_trace:
  enabled: true
  default_trace_level: "standard"
  storage:
    type: "database"
    retention_days: 30
    encryption_enabled: true
  forensics_engine:
    enabled: true
    pattern_analysis_enabled: true
    anomaly_detection_enabled: true
  visualization:
    enabled: true
    real_time_updates: true
```

### 2. Workflow Level

In the workflow manifest:

```yaml
debug_trace_config:
  trace_level: "verbose"
  capture_inputs: true
  capture_outputs: true
  capture_agent_reasoning: true
  retention_period_days: 90
  forensics_enabled: true
```

### 3. Task Level

In the task definition:

```yaml
debug_trace_config:
  trace_level: "forensic"
  capture_inputs: true
  capture_outputs: true
  capture_agent_reasoning: true
```

## Forensics Engine

The AI Workflow Forensics Engine provides advanced analysis capabilities:

### 1. Pattern Analysis
- Identifies common patterns in workflow execution
- Detects anomalies and deviations from normal patterns
- Suggests optimizations based on execution patterns

### 2. Root Cause Analysis
- Analyzes trace data to identify root causes of failures
- Correlates errors across multiple workflow instances
- Provides actionable insights for resolution

### 3. Performance Analysis
- Identifies performance bottlenecks
- Analyzes resource utilization patterns
- Suggests performance optimizations

### 4. Compliance Verification
- Verifies workflow execution against compliance requirements
- Generates compliance reports with supporting evidence
- Identifies potential compliance violations

## Visualization and Analysis

The Capsule Debug Trace system provides multiple visualization and analysis interfaces:

### 1. Trace Explorer
- Interactive visualization of workflow execution
- Timeline view of spans and events
- Filtering and search capabilities
- Drill-down into specific tasks and operations

### 2. Agent Reasoning Viewer
- Visualization of agent decision-making processes
- Comparison of alternatives considered
- Explanation of decision factors and weights

### 3. Performance Dashboard
- Real-time and historical performance metrics
- Resource utilization visualization
- Bottleneck identification

### 4. Forensics Workbench
- Advanced analysis tools for incident investigation
- Pattern matching and anomaly detection
- Correlation analysis across multiple traces

## Integration with Dynamic Agent Capsules

The Capsule Debug Trace system integrates with Dynamic Agent Capsules:

1. **Live Trace Visualization**: Debug traces can be visualized in real-time within agent capsules
2. **Trace Navigation**: Users can navigate through trace data directly in the capsule UI
3. **Reasoning Exploration**: Agent reasoning can be explored and explained within capsules
4. **Trace Comparison**: Multiple traces can be compared side-by-side in the capsule UI

## Security and Privacy

The Capsule Debug Trace system includes several security and privacy features:

1. **Data Sanitization**: Sensitive data can be automatically sanitized in traces
2. **Access Control**: Fine-grained access control for trace data
3. **Encryption**: Encryption of trace data at rest and in transit
4. **Retention Policies**: Configurable retention policies for trace data
5. **Audit Logging**: Audit logs for all access to trace data

## Example: Configuring Trace for a Workflow

```yaml
# In workflow manifest
debug_trace_config:
  trace_level: "verbose"
  capture_inputs: true
  capture_outputs: true
  capture_agent_reasoning: true
  retention_period_days: 90
  forensics_enabled: true
  sanitization_rules:
    - field_pattern: "*.password"
      action: "redact"
    - field_pattern: "*.personal_data"
      action: "hash"
  span_filters:
    include_types: ["task", "agent_decision", "data_transformation"]
    exclude_tasks: ["routine-logging-task"]
```

## Example: Accessing Trace Data

```python
# Python example
from workflow_automation.debug_trace import TraceClient

# Initialize client
trace_client = TraceClient()

# Get trace by ID
trace = trace_client.get_trace("trace-123e4567-e89b-12d3-a456-426614174000")

# Get traces for a workflow
workflow_traces = trace_client.get_traces_by_workflow("predictive-maintenance-workflow")

# Get traces with errors
error_traces = trace_client.get_traces(status="failed")

# Analyze trace with forensics engine
analysis = trace_client.analyze_trace("trace-123e4567-e89b-12d3-a456-426614174000")
```

## Best Practices

1. **Appropriate Trace Levels**: Use appropriate trace levels based on the environment and use case
2. **Data Privacy**: Configure sanitization rules to protect sensitive data
3. **Storage Management**: Implement appropriate retention policies to manage storage
4. **Performance Impact**: Be aware of the performance impact of higher trace levels
5. **Structured Logging**: Use structured logging within spans for better analysis
6. **Contextual Information**: Include relevant context in annotations
7. **Correlation IDs**: Use correlation IDs to link related traces
8. **Regular Analysis**: Regularly analyze traces to identify patterns and issues
9. **Documentation**: Document custom metrics and annotations
10. **Integration Testing**: Include trace verification in integration tests

## Compatibility with Other Specifications

The Capsule Debug Trace Specification is designed to work seamlessly with other Industriverse specifications:

1. **Workflow Manifest**: Debug trace configuration is defined in workflow manifests
2. **Task Contract**: Debug trace requirements can be specified in task contracts
3. **Trust-Aware Execution**: Debug trace levels can be adjusted based on trust context
4. **Agent Mesh Topology**: Traces span across the agent mesh topology
5. **DTSL Embedding**: Debug traces can be embedded in DTSL twin definitions

## Version History

- **1.0.0** (2025-05-22): Initial specification
