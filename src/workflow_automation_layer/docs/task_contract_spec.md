# Task Contract Specification

## Overview

The Task Contract is a formal agreement between workflow components that defines the expectations, requirements, and guarantees for task execution within the Industriverse Workflow Automation Layer. It provides a structured way to ensure reliable task execution across distributed agents and systems.

This specification defines the schema, validation rules, and best practices for creating task contracts that enable robust, trust-aware workflow execution.

## Schema Definition

A task contract is a JSON or YAML document with the following top-level structure:

```json
{
  "contract_id": "string",
  "version": "string",
  "task_id": "string",
  "workflow_id": "string",
  "agent_id": "string",
  "contract_type": "string",
  "execution_requirements": {},
  "input_requirements": {},
  "output_guarantees": {},
  "performance_slas": {},
  "error_handling": {},
  "trust_requirements": {},
  "verification_methods": {},
  "compensation_actions": {},
  "audit_requirements": {},
  "zk_attestation": {}
}
```

### Core Properties

#### `contract_id` (required)
- Unique identifier for the task contract
- Format: UUID v4 or custom string (must be unique within the system)
- Example: `"contract-123e4567-e89b-12d3-a456-426614174000"`

#### `version` (required)
- Semantic version of the contract
- Format: `major.minor.patch`
- Example: `"1.0.0"`

#### `task_id` (required)
- Identifier of the task this contract applies to
- Example: `"data-processing-task"`

#### `workflow_id` (required)
- Identifier of the workflow this task belongs to
- Example: `"predictive-maintenance-workflow"`

#### `agent_id` (required)
- Identifier of the agent responsible for executing the task
- Example: `"data-processing-agent"`

#### `contract_type` (required)
- Type of contract defining the execution model
- Valid values: `"standard"`, `"strict"`, `"flexible"`, `"adaptive"`
- Example: `"standard"`

### Execution Requirements

#### `execution_requirements` (required)
- Defines the requirements for task execution
- Structure:

```json
{
  "execution_mode": "string",
  "timeout_seconds": 300,
  "max_retries": 3,
  "priority": 1,
  "resource_requirements": {
    "cpu": "0.5",
    "memory": "512Mi",
    "gpu": "0"
  },
  "execution_environment": {
    "location": "string",
    "isolation_level": "string"
  },
  "dependencies": [
    {
      "task_id": "string",
      "relationship": "string"
    }
  ]
}
```

- **execution_mode**: Mode of execution (autonomous, supervised, manual)
- **timeout_seconds**: Maximum execution time in seconds
- **max_retries**: Maximum number of retry attempts
- **priority**: Task priority (higher values indicate higher priority)
- **resource_requirements**: Computational resources required
- **execution_environment**: Environment requirements
- **dependencies**: Task dependencies

### Input and Output Specifications

#### `input_requirements` (required)
- Defines the required inputs for the task
- Structure:

```json
{
  "schema": {},
  "validation_rules": [],
  "required_fields": [],
  "default_values": {},
  "sensitive_fields": []
}
```

#### `output_guarantees` (required)
- Defines the guaranteed outputs from the task
- Structure:

```json
{
  "schema": {},
  "guaranteed_fields": [],
  "quality_metrics": {},
  "format": "string"
}
```

### Performance and Reliability

#### `performance_slas` (optional)
- Service Level Agreements for task performance
- Structure:

```json
{
  "response_time_ms": 1000,
  "throughput_per_second": 10,
  "availability_percent": 99.9,
  "error_rate_threshold": 0.01
}
```

#### `error_handling` (optional)
- Defines how errors should be handled
- Structure:

```json
{
  "error_types": [
    {
      "type": "string",
      "action": "string",
      "max_retries": 3,
      "backoff_strategy": "string"
    }
  ],
  "fallback_action": "string",
  "error_reporting": {
    "level": "string",
    "destinations": []
  }
}
```

### Trust and Verification

#### `trust_requirements` (optional)
- Defines trust-related requirements for execution
- Structure:

```json
{
  "minimum_trust_score": 0.7,
  "trust_context": "string",
  "verification_required": true,
  "human_oversight_level": "string",
  "explainability_level": "string"
}
```

#### `verification_methods` (optional)
- Methods to verify task execution and results
- Structure:

```json
{
  "methods": [
    {
      "type": "string",
      "parameters": {}
    }
  ],
  "verification_timeout_seconds": 60,
  "verification_agent_id": "string"
}
```

### Advanced Features

#### `compensation_actions` (optional)
- Actions to take if the task needs to be compensated (rolled back)
- Structure:

```json
{
  "compensation_task_id": "string",
  "compensation_strategy": "string",
  "timeout_seconds": 300,
  "idempotent": true
}
```

#### `audit_requirements` (optional)
- Requirements for auditing task execution
- Structure:

```json
{
  "audit_level": "string",
  "retention_period_days": 90,
  "required_metadata": [],
  "compliance_frameworks": []
}
```

#### `zk_attestation` (optional)
- Zero-Knowledge attestation configuration
- Structure:

```json
{
  "enabled": true,
  "proof_type": "string",
  "verification_key": "string",
  "attestation_parameters": {}
}
```

## Contract Versioning

Task contracts support versioning to allow for evolution over time:

1. **Major Version**: Incremented for backward-incompatible changes
2. **Minor Version**: Incremented for backward-compatible feature additions
3. **Patch Version**: Incremented for backward-compatible bug fixes

The Task Contract Versioning Agent manages contract versions and ensures compatibility between interacting components.

## Contract Negotiation

Contracts can be negotiated between workflow components:

1. **Proposal**: Initial contract proposed by the workflow runtime
2. **Counterproposal**: Agent may propose modifications
3. **Agreement**: Final contract agreed upon by all parties
4. **Enforcement**: Contract terms enforced during execution

The Workflow Negotiator Agent facilitates this negotiation process.

## Trust-Aware Execution

Task contracts integrate with the trust-aware execution system:

1. **Trust Scores**: Minimum trust scores required for execution
2. **Execution Modes**: Different execution modes based on trust levels
3. **Verification**: Verification requirements based on trust context
4. **Human Oversight**: Required level of human oversight

## ZK-Based Task Attestation

For high-security workflows, Zero-Knowledge proofs can be used to attest task execution:

1. **Proof Generation**: Agent generates ZK proof of correct execution
2. **Verification**: Proof verified without revealing sensitive data
3. **Attestation**: Successful verification recorded in the workflow telemetry

## Example Task Contract

```json
{
  "contract_id": "contract-123e4567-e89b-12d3-a456-426614174000",
  "version": "1.0.0",
  "task_id": "anomaly-detection",
  "workflow_id": "predictive-maintenance-workflow",
  "agent_id": "anomaly-detection-agent",
  "contract_type": "standard",
  "execution_requirements": {
    "execution_mode": "autonomous",
    "timeout_seconds": 300,
    "max_retries": 3,
    "priority": 2,
    "resource_requirements": {
      "cpu": "1.0",
      "memory": "1Gi",
      "gpu": "0"
    },
    "execution_environment": {
      "location": "cloud",
      "isolation_level": "container"
    },
    "dependencies": [
      {
        "task_id": "sensor-data-collection",
        "relationship": "requires_completion"
      }
    ]
  },
  "input_requirements": {
    "schema": {
      "type": "object",
      "properties": {
        "sensor_data": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "timestamp": { "type": "string", "format": "date-time" },
              "sensor_id": { "type": "string" },
              "value": { "type": "number" }
            },
            "required": ["timestamp", "sensor_id", "value"]
          }
        }
      },
      "required": ["sensor_data"]
    },
    "validation_rules": [
      "sensor_data.length > 0",
      "sensor_data[*].value >= 0"
    ],
    "required_fields": ["sensor_data"]
  },
  "output_guarantees": {
    "schema": {
      "type": "object",
      "properties": {
        "anomalies": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "timestamp": { "type": "string", "format": "date-time" },
              "sensor_id": { "type": "string" },
              "anomaly_score": { "type": "number" },
              "confidence": { "type": "number" }
            },
            "required": ["timestamp", "sensor_id", "anomaly_score", "confidence"]
          }
        }
      },
      "required": ["anomalies"]
    },
    "guaranteed_fields": ["anomalies"],
    "quality_metrics": {
      "min_confidence": 0.7,
      "max_false_positive_rate": 0.05
    }
  },
  "performance_slas": {
    "response_time_ms": 2000,
    "availability_percent": 99.5,
    "error_rate_threshold": 0.02
  },
  "error_handling": {
    "error_types": [
      {
        "type": "data_format_error",
        "action": "retry",
        "max_retries": 2,
        "backoff_strategy": "exponential"
      },
      {
        "type": "timeout_error",
        "action": "escalate",
        "max_retries": 1,
        "backoff_strategy": "fixed"
      }
    ],
    "fallback_action": "skip",
    "error_reporting": {
      "level": "warning",
      "destinations": ["workflow_telemetry", "system_log"]
    }
  },
  "trust_requirements": {
    "minimum_trust_score": 0.7,
    "trust_context": "anomaly_detection",
    "verification_required": true,
    "human_oversight_level": "review_results",
    "explainability_level": "feature_importance"
  },
  "verification_methods": {
    "methods": [
      {
        "type": "statistical_validation",
        "parameters": {
          "confidence_threshold": 0.9,
          "sample_size": 100
        }
      }
    ],
    "verification_timeout_seconds": 60,
    "verification_agent_id": "verification-agent"
  },
  "audit_requirements": {
    "audit_level": "detailed",
    "retention_period_days": 90,
    "required_metadata": ["execution_time", "agent_version", "input_hash"],
    "compliance_frameworks": ["ISO27001"]
  }
}
```

## Best Practices

1. **Explicit Requirements**: Clearly define all requirements and guarantees
2. **Appropriate Constraints**: Set realistic constraints that balance reliability and performance
3. **Error Handling**: Define comprehensive error handling for all anticipated error types
4. **Trust Awareness**: Configure trust requirements based on task criticality
5. **Verification**: Include appropriate verification methods for critical tasks
6. **Auditability**: Define audit requirements based on compliance needs
7. **Versioning**: Use semantic versioning to manage contract evolution
8. **Negotiation**: Allow for contract negotiation when appropriate
9. **Documentation**: Document the purpose and constraints of each contract
10. **Testing**: Test contracts with different scenarios to ensure robustness

## Compatibility with Other Specifications

The Task Contract Specification is designed to work seamlessly with other Industriverse specifications:

1. **Workflow Manifest**: Task contracts are referenced in workflow manifests
2. **Unified Message Envelope**: Contract terms are enforced during message exchange
3. **Agent Reflex Timers**: Contracts can specify timing constraints for reflex operations
4. **Capsule Debug Trace**: Contract verification can leverage debug traces
5. **Trust-Aware Execution Modes**: Contracts define trust requirements for execution modes

## Version History

- **1.0.0** (2025-05-22): Initial specification
